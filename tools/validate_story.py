#!/usr/bin/env python3
"""story.json 검증 V1~V12 (Pipeline.md §S7).

런타임에 깨지면 아이가 본다. 여기서 전부 잡는다.
외부 의존성 없이 동작하며, jsonschema 가 설치돼 있으면 V1 을 정밀 검사한다.

사용: python3 tools/validate_story.py stories/goldaxe/story.json [--strict]
"""
import json, re, sys, pathlib

CAMERA = {"still","pushIn","pullOut","panLeft","panRight","tiltUp"}
ANIM   = {"none","breathe","sway","bob","driftIn"}
ENTER  = {"none","fadeIn","popIn","slideIn"}
TRANS  = {"crossfade","pageTurn","wipe","cut"}
FX     = {"none","petals","snow","fireflies","sparkle","rain","dust"}

SUBTITLE_TOP = 0.80   # Spec §6.3 — 자막이 차지하는 하단 영역 경계


class Report:
    def __init__(self): self.errors, self.warns = [], []
    def err(self, code, msg):  self.errors.append(f"{code}  {msg}")
    def warn(self, code, msg): self.warns.append(f"{code}  {msg}")


def iter_beats(story):
    for nid, node in story["nodes"].items():
        for b in node.get("beats", []):
            yield nid, b


def v1_schema(story, root, r):
    try:
        import jsonschema
    except ImportError:
        r.warn("V1", "jsonschema 미설치 — 구조 정밀 검사를 건너뛴다 (pip install jsonschema)")
        return
    schema = json.loads((root / "schema/story.schema.json").read_text(encoding="utf-8"))
    v = jsonschema.Draft202012Validator(schema)
    for e in sorted(v.iter_errors(story), key=lambda e: list(e.path))[:20]:
        r.err("V1", f"{'/'.join(map(str, e.path)) or '(root)'}: {e.message}")


def v2_refs(story, r):
    """참조 무결성 — 선언되지 않은 에셋을 가리키면 검은 화면이 된다."""
    a = story["assets"]
    for nid, b in iter_beats(story):
        sc = b["scene"]
        if sc["background"] not in a["backgrounds"]:
            r.err("V2", f"{b['id']}: 배경 '{sc['background']}' 미선언")
        for act in sc.get("actors", []):
            kind, _, name = act["asset"].partition("/")
            pool = a.get(kind, {})
            if name not in pool:
                r.err("V2", f"{b['id']}: 에셋 '{act['asset']}' 미선언")
            elif kind == "characters":
                pose = act.get("pose")
                if pose not in pool[name]["poses"]:
                    r.err("V2", f"{b['id']}: '{name}' 에 포즈 '{pose}' 없음")


def v3_files(story, root, r, strict):
    """파일 실재 — 더미 단계에서는 경고, --strict 에서는 오류."""
    base = root / "stories" / story["storyId"] / "assets"
    missing = []
    for kind, group in story["assets"].items():
        for name, spec in group.items():
            srcs = [spec["src"]] if "src" in spec else list(spec["poses"].values())
            missing += [s for s in srcs if not (base / s).exists()]
    if missing:
        (r.err if strict else r.warn)("V3", f"에셋 파일 {len(missing)}개 없음 (예: {missing[0]})")


def v4_tree(story, r):
    """트리 무결성 — 13노드가 되면 사람 눈으로 못 잡는다."""
    nodes = story["nodes"]
    if story["rootNode"] not in nodes:
        r.err("V4", f"rootNode '{story['rootNode']}' 가 존재하지 않는다"); return

    edges = {nid: [o["next"] for o in n.get("choice", {}).get("options", [])]
             for nid, n in nodes.items()}
    for nid, outs in edges.items():
        for nxt in outs:
            if nxt not in nodes:
                r.err("V4", f"{nid}: 선택지가 없는 노드 '{nxt}' 를 가리킨다")

    seen, stack = set(), [story["rootNode"]]
    while stack:
        cur = stack.pop()
        if cur in seen: continue
        seen.add(cur)
        stack += [n for n in edges.get(cur, []) if n in nodes]
    for nid in nodes.keys() - seen:
        r.err("V4", f"{nid}: 도달할 수 없는 노드")

    color = {}
    def cyclic(n):
        color[n] = 1
        for nx in edges.get(n, []):
            if color.get(nx) == 1: return True
            if color.get(nx) is None and cyclic(nx): return True
        color[n] = 2
        return False
    if cyclic(story["rootNode"]):
        r.err("V4", "트리에 순환이 있다")

    for nid, node in nodes.items():
        if node["type"] == "narrative" and "choice" not in node:
            r.err("V4", f"{nid}: narrative 인데 choice 가 없다 (막다른 길)")
        if node["type"] == "ending" and "choice" in node:
            r.err("V4", f"{nid}: ending 인데 choice 가 있다")


def v5_endings(story, r):
    ends = {nid: n for nid, n in story["nodes"].items() if n["type"] == "ending"}
    if len(ends) not in (3, 9):
        r.err("V5", f"결말 {len(ends)}개 — v0 데모는 3개, v1 전편은 9개여야 한다")
    canon = [nid for nid, n in ends.items() if n.get("isCanonical")]
    if len(canon) != 1:
        r.err("V5", f"isCanonical 이 {len(canon)}개 — 정확히 1개(원작 결말)여야 한다")
    elif story.get("canonicalEnding") != canon[0]:
        r.err("V5", f"canonicalEnding='{story.get('canonicalEnding')}' 인데 실제는 '{canon[0]}'")
    for nid, n in ends.items():
        if not n.get("lesson"):
            r.err("V5", f"{nid}: lesson 이 없다 (Spec §3.4 — 모든 결말은 교훈 1문장)")


def v6_enums(story, r):
    for nid, b in iter_beats(story):
        sc = b["scene"]
        for key, allowed in (("camera", CAMERA), ("transitionIn", TRANS), ("fx", FX)):
            if key in sc and sc[key] not in allowed:
                r.err("V6", f"{b['id']}: {key}='{sc[key]}' 는 허용값이 아니다 ({sorted(allowed)})")
        for act in sc.get("actors", []):
            if act.get("anim", "none") not in ANIM:
                r.err("V6", f"{b['id']}: anim='{act['anim']}' 허용값 아님")
            if act.get("enter", "none") not in ENTER:
                r.err("V6", f"{b['id']}: enter='{act['enter']}' 허용값 아님")


def v7_duration(story, r):
    for nid, b in iter_beats(story):
        d = b["durationMs"]
        if not 6000 <= d <= 15000:
            r.err("V7", f"{b['id']}: {d/1000:.1f}초 — 4~7세 기준 6~12초(최대 15초)")
        elif d > 12000:
            r.warn("V7", f"{b['id']}: {d/1000:.1f}초 — 12초 초과, 비트 분할 검토")


def v8_timings(story, r):
    for nid, b in iter_beats(story):
        wt, text, dur = b["wordTimings"], b["text"], b["durationMs"]
        prev_end = 0
        for a, z, t0, t1 in wt:
            if not 0 <= a < z <= len(text):
                r.err("V8", f"{b['id']}: 문자 인덱스 [{a},{z}] 가 본문 길이 {len(text)} 를 벗어난다")
            if t0 < prev_end:
                r.err("V8", f"{b['id']}: 어절 시각이 역행한다 ({t0} < {prev_end})")
            prev_end = t1
        if wt[-1][3] > dur:
            r.err("V8", f"{b['id']}: 마지막 어절 종료 {wt[-1][3]}ms > durationMs {dur}ms")


def v9_text(story, r):
    for nid, node in story["nodes"].items():
        for o in node.get("choice", {}).get("options", []):
            if len(o["label"]) > 12:
                r.err("V9", f"{nid}/{o['id']}: 선택지 {len(o['label'])}자 — 12자 이내")
        les = node.get("lesson", "")
        if les and len(re.findall(r"[.!?。]", les)) > 1:
            r.err("V9", f"{nid}: lesson 이 2문장 이상 — 1문장이어야 한다")


def v10_coords(story, r):
    for nid, b in iter_beats(story):
        zs = {}
        for act in b["scene"].get("actors", []):
            if not (0 <= act["x"] <= 1 and 0 <= act["y"] <= 1):
                r.err("V10", f"{b['id']}: {act['asset']} 좌표 ({act['x']},{act['y']}) 가 화면 밖")
            z = act.get("z", 0)
            if z in zs:
                r.err("V10", f"{b['id']}: z={z} 중복 ({zs[z]} / {act['asset']}) — 겹침 순서가 불확정")
            zs[z] = act["asset"]


def v11_wordtimings(story, r):
    """한글 학습이 핵심 기능이므로 타임스탬프 없는 비트는 통과시키지 않는다."""
    for nid, b in iter_beats(story):
        if not b.get("wordTimings"):
            r.err("V11", f"{b['id']}: wordTimings 없음 — 어절 하이라이트 불가")
    for nid, node in story["nodes"].items():
        ch = node.get("choice")
        if ch and not ch.get("promptWordTimings"):
            r.warn("V11", f"{nid}: 선택지 질문에 promptWordTimings 없음")


def v13_bg_treatment(story, r):
    """배경 후처리 값이 범위를 벗어나면 배경이 뭉개지거나 캐릭터를 덮는다."""
    LIM = {"blurPx": (0, 6), "brightness": (40, 140), "saturate": (0, 150)}

    def check(t, where):
        for k, v in (t or {}).items():
            if k not in LIM:
                r.err("V13", f"{where}: bgTreatment 에 알 수 없는 항목 '{k}'")
            elif not LIM[k][0] <= v <= LIM[k][1]:
                r.err("V13", f"{where}: bgTreatment.{k}={v} 가 범위 {LIM[k]} 밖")

    check(story["stage"].get("bgTreatment"), "stage")
    for nid, b in iter_beats(story):
        check(b["scene"].get("bgTreatment"), b["id"])


def v12_subtitle_area(story, r):
    """자막이 그림을 가리지 않도록 하단 영역을 비워 둔다 (Spec §6.3)."""
    for nid, b in iter_beats(story):
        for act in b["scene"].get("actors", []):
            if act["y"] > SUBTITLE_TOP:
                r.err("V12", f"{b['id']}: {act['asset']} y={act['y']} > {SUBTITLE_TOP} — 자막 영역 침범")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    strict = "--strict" in sys.argv
    path = pathlib.Path(args[0] if args else "stories/goldaxe/story.json")
    root = pathlib.Path(__file__).resolve().parent.parent
    story = json.loads(path.read_text(encoding="utf-8"))

    r = Report()
    v1_schema(story, root, r)
    v2_refs(story, r)
    v3_files(story, root, r, strict)
    v4_tree(story, r)
    v5_endings(story, r)
    v6_enums(story, r)
    v7_duration(story, r)
    v8_timings(story, r)
    v9_text(story, r)
    v10_coords(story, r)
    v11_wordtimings(story, r)
    v12_subtitle_area(story, r)
    v13_bg_treatment(story, r)

    print(f"검증 대상: {path}")
    for w in r.warns:  print(f"  ⚠  {w}")
    for e in r.errors: print(f"  ✗  {e}")
    if r.errors:
        print(f"\n실패 — 오류 {len(r.errors)}건, 경고 {len(r.warns)}건")
        return 1
    print(f"\n통과 — V1~V13 이상 없음 (경고 {len(r.warns)}건)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
