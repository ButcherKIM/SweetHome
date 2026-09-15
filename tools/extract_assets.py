#!/usr/bin/env python3
"""에셋 명세 추출 (Pipeline.md §S3).

story.json 이 **실제로 참조하는** 에셋을 모아 목록을 만든다.
수작업 환경에서는 에셋 하나가 곧 사람 시간이므로, 뽑기 전에 이 세 가지를 안다:

  1. 뭘 뽑아야 하는가        — 참조되는데 파일이 없는 것
  2. 안 뽑아도 되는가        — 선언만 되고 아무 비트도 안 쓰는 것
  3. 몇 번 쓰이는가          — 1번만 쓰이는 에셋은 기존 것으로 대체를 검토한다

프롬프트 문서와 대조해 빠진 것/남는 것도 짚는다.

사용: python3 tools/extract_assets.py [--story goldaxe] [--write]
"""
import argparse
import collections
import json
import pathlib
import re
import sys

KINDS = {"background": "bg", "character": "char", "prop": "prop", "icon": "icon"}


def collect(story):
    """참조 횟수를 센다. key = (kind, 에셋id, 파일경로)"""
    used = collections.Counter()
    missing_decl = []

    for node in story["nodes"].values():
        for beat in node["beats"]:
            sc = beat["scene"]
            bg = story["assets"]["backgrounds"].get(sc["background"])
            if bg:
                used[("background", sc["background"], bg["src"])] += 1
            else:
                missing_decl.append(f"{beat['id']}: 배경 '{sc['background']}' 선언 없음")

            for a in sc.get("actors", []):
                kind, name = a["asset"].split("/", 1)
                if kind == "characters":
                    c = story["assets"]["characters"].get(name)
                    pose = a.get("pose")
                    src = (c or {}).get("poses", {}).get(pose) if c else None
                    if src:
                        used[("character", f"{name}:{pose}", src)] += 1
                    else:
                        missing_decl.append(f"{beat['id']}: 캐릭터 '{name}/{pose}' 선언 없음")
                elif kind == "props":
                    p = (story["assets"].get("props") or {}).get(name)
                    if p:
                        used[("prop", name, p["src"])] += 1
                    else:
                        missing_decl.append(f"{beat['id']}: 소품 '{name}' 선언 없음")

        for opt in (node.get("choice") or {}).get("options", []):
            if opt.get("image"):
                used[("icon", opt["id"] + ":" + opt["label"], opt["image"])] += 1

    return used, missing_decl


def declared(story):
    """선언된 것 전부 — 안 쓰이는 게 있는지 보려고."""
    out = {}
    for k, v in story["assets"]["backgrounds"].items():
        out[v["src"]] = ("background", k)
    for name, c in story["assets"]["characters"].items():
        for pose, src in c["poses"].items():
            out[src] = ("character", f"{name}:{pose}")
    for name, p in (story["assets"].get("props") or {}).items():
        out[p["src"]] = ("prop", name)
    return out


def prompt_files(root):
    """프롬프트 문서가 만들기로 한 파일들 (Save as: 줄)."""
    md = root / "style" / "prompts-antigravity.md"
    if not md.exists():
        return set()
    return {
        line.split("/")[-1]
        for line in re.findall(r"^Save as:\s*(\S+)", md.read_text(encoding="utf-8"), re.M)
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--story", default="goldaxe")
    ap.add_argument("--write", action="store_true", help="asset_manifest.json 으로 저장")
    args = ap.parse_args()

    root = pathlib.Path(__file__).resolve().parent.parent
    sdir = root / "stories" / args.story
    story = json.loads((sdir / "story.json").read_text(encoding="utf-8"))
    adir = sdir / "assets"

    used, missing_decl = collect(story)
    decl = declared(story)
    wanted = prompt_files(root)

    rows = []
    for (kind, aid, src), n in sorted(used.items(), key=lambda kv: (-kv[1], kv[0][0], kv[0][1])):
        rows.append({
            "id": aid, "kind": kind, "src": src,
            "uses": n,
            "status": "done" if (adir / src).exists() else "todo",
            "inPrompts": src.split("/")[-1] in wanted if wanted else None,
        })

    todo = [r for r in rows if r["status"] == "todo"]
    once = [r for r in rows if r["uses"] == 1]
    unused = [(k, v) for src, (k, v) in decl.items() if not any(r["src"] == src for r in rows)]
    used_names = {r["src"].split("/")[-1] for r in rows}
    extra = sorted(wanted - used_names - {"spirit_sheet.png", "woodcutter_sheet.png"})
    absent = sorted(n for n in used_names if wanted and n not in wanted)

    w = max((len(r["id"]) for r in rows), default=10)
    print(f"에셋 {len(rows)}종 · 참조 {sum(r['uses'] for r in rows)}회 "
          f"· 있음 {len(rows)-len(todo)} · 없음 {len(todo)}\n")
    for r in rows:
        mark = "✓" if r["status"] == "done" else " "
        flag = "" if r["inPrompts"] in (True, None) else "  ← 프롬프트에 없음"
        print(f"  {mark} {r['kind']:<10} {r['id']:<{w}}  {r['uses']:>2}회  {r['src']}{flag}")

    if missing_decl:
        print("\n⚠ 선언 없는 참조 — 빌드가 아니라 여기서 잡는다")
        for m in missing_decl:
            print("   ", m)

    if unused:
        print(f"\n· 선언만 되고 안 쓰이는 것 {len(unused)}개 — 안 뽑아도 된다")
        for k, v in unused:
            print(f"    {k} {v}")

    if absent:
        print(f"\n⚠ 쓰이는데 프롬프트 문서에 없는 파일 {len(absent)}개")
        for n in absent:
            print("   ", n)

    if extra:
        print(f"\n· 프롬프트에는 있는데 아무 비트도 안 쓰는 파일 {len(extra)}개")
        for n in extra:
            print("   ", n)

    if once:
        print(f"\n· 한 번만 쓰이는 에셋 {len(once)}개 — 기존 것으로 대체를 검토한다")
        for r in once:
            print(f"    {r['kind']} {r['id']}")

    if args.write:
        out = sdir / "asset_manifest.json"
        out.write_text(json.dumps({
            "summary": {
                "total": len(rows), "done": len(rows) - len(todo), "todo": len(todo),
                "byKind": dict(collections.Counter(r["kind"] for r in rows)),
                "reuse": {r["id"]: r["uses"] for r in rows if r["uses"] > 1},
            },
            "assets": rows,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"\n{out} 저장")

    return 1 if missing_decl or absent else 0


if __name__ == "__main__":
    sys.exit(main())
