"""engine/ 에 브라우저가 들어오지 않았는지 — Spec §8.5.

제품화(React Native) 때 다시 쓰는 것은 렌더러뿐이어야 한다. 그 전제는
"엔진 코드에 DOM·CSS·브라우저 API 를 섞지 않는다" 하나다. 규칙은 지켜지지
않으면 규칙이 아니므로 여기서 확인한다.
"""
import re
from pathlib import Path

ENGINE = Path(__file__).resolve().parent.parent / "player" / "src" / "engine"

# 엔진에 있으면 안 되는 것들
BROWSER = [
    r"\bdocument\b", r"\bwindow\b", r"\blocalStorage\b", r"\bsessionStorage\b",
    r"\bnavigator\b", r"\bfetch\b", r"\bHTML[A-Za-z]*Element\b", r"\bAudio\b",
    r"\brequestAnimationFrame\b", r"\bperformance\b", r"from ['\"]react",
]


def engine_files():
    return sorted(ENGINE.glob("*.ts"))


def test_engine_exists():
    assert engine_files(), f"엔진 파일이 없다: {ENGINE}"


def test_no_browser_api_in_engine():
    bad = []
    for f in engine_files():
        src = f.read_text(encoding="utf-8")
        # 주석은 설명이라 봐준다 — 코드만 본다
        code = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
        code = re.sub(r"^\s*(//|\*).*$", "", code, flags=re.M)
        for pat in BROWSER:
            if re.search(pat, code):
                bad.append(f"{f.name}: {pat}")
    assert not bad, "엔진에 브라우저가 들어왔다 (Spec §8.5): " + ", ".join(bad)


def test_engine_has_no_css():
    assert not list(ENGINE.glob("*.css")), "엔진에 CSS 가 있으면 안 된다"
