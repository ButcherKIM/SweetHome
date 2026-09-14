"""story.json 이 스펙을 지키는지 — 푸시할 때마다 확인한다.

검사의 본체는 tools/validate_story.py (V1~V13) 이고 첫 테스트가 그것을 실제
스토리에 돌린다. 나머지는 스펙의 대표 조항이라 눈에 보이게 따로 둔다.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORY = ROOT / "stories" / "goldaxe" / "story.json"


def load():
    return json.loads(STORY.read_text(encoding="utf-8"))


def beats():
    for node_id, node in load()["nodes"].items():
        for b in node["beats"]:
            yield node_id, b


def test_validator_passes():
    """V1~V13 전부. 에셋 파일이 아직 없는 것은 경고라 통과한다 (--strict 아님)."""
    r = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "validate_story.py"), str(STORY)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stdout + r.stderr


def test_nine_endings_one_canonical():
    """Spec §3 — 분기 2회 × 선택 3개 = 결말 9개, 그중 원작이 정확히 하나."""
    story = load()
    endings = {k: v for k, v in story["nodes"].items() if v["type"] == "ending"}
    assert len(endings) == 9
    canonical = [k for k, v in endings.items() if v.get("isCanonical")]
    assert canonical == [story["canonicalEnding"]]


def test_every_choice_has_three_options():
    for node_id, node in load()["nodes"].items():
        if "choice" in node:
            assert len(node["choice"]["options"]) == 3, node_id


def test_every_line_has_word_timings():
    """Spec §6.3 — 어절 하이라이트가 제품 목표라 wordTimings 는 필수다."""
    for node_id, b in beats():
        for ln in b["lines"]:
            assert ln.get("wordTimings"), ln["id"]
            assert len(ln["wordTimings"]) == len(ln["text"].split()), ln["id"]


def test_beat_holds_two_or_three_lines():
    """Spec §2 — 그림 한 장이 자막 2~3줄을 덮는다. 한 줄이면 동화책이 아니다."""
    for node_id, b in beats():
        assert 2 <= len(b["lines"]) <= 3, b["id"]


def test_every_beat_has_a_background():
    """배경 없는 비트는 검은 화면이 된다."""
    for node_id, b in beats():
        assert b["scene"].get("background"), b["id"]
