"""컷아웃이 후광 번짐을 분홍 테두리로 남기지 않는지 — 산신령 첫 장에서 실제로 당했다.

"faint warm glow" 로 그린 후광은 마젠타 배경과 섞여 연분홍 띠가 된다. 예전 키잉은
K 가 배경의 45% 아래면 불투명으로 남겨서, 그 띠가 통째로 캐릭터에 붙어 나왔다.
배경에 이어진 번짐은 반투명 + 분홍 제거, 배경에 안 닿는 분홍(볼 홍조)은 그대로여야 한다.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import cutout  # noqa: E402

MAGENTA = np.array([255, 0, 255], np.float64)
GLOW = np.array([255, 245, 225], np.float64)     # 따뜻한 흰 빛
ROBE = (215, 220, 200)                           # 미색 옷, K -5
CHEEK = (235, 175, 165)                          # 볼 홍조, K 25 — 배경에 안 닿는다


def sample():
    """마젠타 배경 · 가운데 옷 원판 · 그 둘레 후광 · 원판 안의 볼 홍조."""
    n = 200
    y, x = np.mgrid[:n, :n]
    d = np.hypot(x - n / 2, y - n / 2)
    t = np.clip((80 - d) / 30, 0, 1)[..., None]   # 후광: 반지름 50→80 에서 빛 → 배경
    img = t * GLOW + (1 - t) * MAGENTA
    img[d < 50] = ROBE
    img[np.hypot(x - 90, y - 90) < 8] = CHEEK
    return Image.fromarray(img.round().astype(np.uint8), "RGB")


def run():
    out, k_bg, _ = cutout.cut(sample())
    return np.asarray(out).astype(int), k_bg


def test_background_is_keyed():
    a, k_bg = run()
    assert k_bg > 200
    assert a[0, 0, 3] == 0 and a[-1, -1, 3] == 0


def test_glow_becomes_translucent_not_pink():
    a, _ = run()
    seen = a[..., 3] > 0
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    pink = seen & (r - g > 30) & (b - g > 30)
    assert not pink.any(), f"분홍 테두리 {pink.sum()}px"
    ring = seen & (a[..., 3] < 250)
    assert ring.sum() > 2000, "후광이 반투명으로 남지 않고 잘려 나갔다"


def test_enclosed_pink_is_untouched():
    a, _ = run()
    # 크롭 오프셋: 후광 바깥 끝(반지름 ~80)부터 남는다 → 볼은 원판 안쪽 그대로
    h, w = a.shape[:2]
    cy, cx = h // 2 - 10, w // 2 - 10
    assert a[cy, cx, 3] == 255
    assert tuple(a[cy, cx, :3]) == CHEEK
