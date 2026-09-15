"""에셋 경로가 기획서 부록 B 를 지키는지 — 어긋나면 그림이 조용히 안 뜬다.

cutout.py 는 raw 파일명을 그대로 유지한다(`char_woodcutter_idle.png`).
story.json 이 `char/woodcutter_idle.png` 을 가리키고 있으면 그림 22장을
다 뽑아 놓고도 화면이 빈 채로 돈다. 사람이 눈치채기 어려운 종류라 여기서 막는다.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORY = json.loads((ROOT / "stories" / "goldaxe" / "story.json").read_text(encoding="utf-8"))

# 부록 B — 폴더별 파일명 접두사
RULES = [("bg/", "bg_"), ("char/", "char_"), ("prop/", "prop_"), ("icon/", "choice_")]


def srcs():
    a = STORY["assets"]
    for v in a["backgrounds"].values():
        yield v["src"]
    for c in a["characters"].values():
        yield from c["poses"].values()
    for p in (a.get("props") or {}).values():
        yield p["src"]
    for node in STORY["nodes"].values():
        for opt in (node.get("choice") or {}).get("options", []):
            if opt.get("image"):
                yield opt["image"]


def test_asset_naming_follows_appendix_b():
    bad = []
    for src in srcs():
        folder, _, name = src.partition("/")
        prefix = dict((f.rstrip("/"), p) for f, p in RULES).get(folder)
        if prefix is None:
            bad.append(f"{src} — 모르는 폴더")
        elif not name.startswith(prefix):
            bad.append(f"{src} — {folder}/ 는 {prefix} 로 시작해야 한다")
    assert not bad, "부록 B 위반: " + ", ".join(bad)


def test_extract_assets_reports_no_mismatch():
    """story.json 이 쓰는 에셋과 프롬프트 문서가 만들 파일이 일치하는가."""
    r = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "extract_assets.py")],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stdout + r.stderr
