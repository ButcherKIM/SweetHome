#!/usr/bin/env python3
"""생성 원본 → 투명 PNG (Pipeline.md §S5).

`assets/raw/` 의 원본을 읽어 배경을 걷어내고 `assets/{char,prop,icon}/` 에 넣는다.
플레이어가 브라우저에서 하던 일과 같은 알고리즘이다 — 결과가 달라지면 안 된다.

  · 배경색은 모서리에서 직접 읽는다. 분홍의 진하기는 상관없다
  · 분홍 정도를 K = (R+B)/2 - G 로 재면 배경과 피사체가 잘 갈린다
    (연분홍 58 · 자주 77 인 반면 볼 홍조 15 · 살구 피부 1 · 미색 의복 -3)
  · 한 파일은 한 에셋이다. 떨어져 있는 부분(두 손, 지팡이 등)은 모두 살려 합친다
  · 부스러기(반짝이 등)만 버린다 — 가장 큰 덩어리의 12% 미만

  · bg_*   배경이므로 키잉하지 않는다
  · *light*, *glow*  발광체는 검은 배경에 screen 으로 얹으므로 키잉하지 않는다

사용: python3 tools/cutout.py [--story goldaxe] [--only prop_axe_iron]
"""
import argparse, pathlib, sys

import numpy as np
from PIL import Image

KEY_MIN   = 22     # 배경의 K 가 이보다 낮으면 분홍 배경이 아니라고 본다
HI, LO    = .82, .45
MIN_BLOB  = .12    # 가장 큰 덩어리 대비
MASTER_PX = 1400   # 컷아웃 긴 변
BG_PX     = 1800   # 배경 긴 변


def kind_of(name):
    n = name.lower()
    if n.startswith("bg_"):                      return "bg"
    if "light" in n or "glow" in n or "ray" in n: return "glow"
    if n.startswith("char_"):                    return "char"
    if n.startswith("choice") or n.startswith("icon_"): return "icon"
    return "prop"


def blobs_of(alpha):
    """4-이웃 연결 성분. 반환: (라벨 배열, 라벨별 픽셀수)."""
    h, w = alpha.shape
    ok = alpha >= 40
    label = np.full(h * w, -1, np.int32)
    flat = ok.reshape(-1)
    stack = np.empty(h * w, np.int32)
    sizes, cur = [], 0
    for start in range(h * w):
        if not flat[start] or label[start] >= 0:
            continue
        sp = 0; stack[sp] = start; sp += 1; label[start] = cur; size = 0
        while sp:
            sp -= 1; p = stack[sp]; size += 1
            x, y = p % w, p // w
            for q, okq in ((p-1, x > 0), (p+1, x < w-1), (p-w, y > 0), (p+w, y < h-1)):
                if okq and flat[q] and label[q] < 0:
                    label[q] = cur; stack[sp] = q; sp += 1
        sizes.append(size); cur += 1
    return label.reshape(h, w), sizes


def cut(img):
    """배경을 걷어내고 RGBA 이미지 하나를 돌려준다.

    떨어져 있는 덩어리도 같은 그림의 부분이므로 합친다 — "모르겠다" 아이콘의
    두 손처럼 서로 안 닿는 경우가 있다. 부스러기만 크기로 걸러낸다.
    """
    a = np.asarray(img.convert("RGBA")).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    k = (r + b) / 2 - g

    patch = max(2, round(min(a.shape[:2]) * .02))
    h, w = a.shape[:2]
    corners = [k[:patch, :patch], k[:patch, -patch:], k[-patch:, :patch], k[-patch:, -patch:],
               k[:patch, (w-patch)//2:(w+patch)//2], k[-patch:, (w-patch)//2:(w+patch)//2]]
    k_bg = float(np.median(np.concatenate([c.ravel() for c in corners])))
    if k_bg < KEY_MIN:
        return [], k_bg

    hi, lo = k_bg * HI, k_bg * LO
    alpha = a[..., 3].astype(np.float64)
    alpha = np.where(k >= hi, 0.0,
             np.where(k > lo, np.minimum(alpha, 255 * (1 - (k - lo) / (hi - lo))), alpha))
    a[..., 3] = alpha.astype(np.int16)

    # 가장자리 분홍 잔상 억제
    edge = (a[..., 3] < 250) & (k > 0)
    f = np.clip(k / (k_bg * .6), 0, 1)[edge] * .7
    a[..., 0][edge] = r[edge] - (r[edge] - g[edge]) * f
    a[..., 2][edge] = b[edge] - (b[edge] - g[edge]) * f

    label, sizes = blobs_of(a[..., 3])
    if not sizes:
        return None, k_bg, 0
    biggest = max(sizes)
    keep = {i for i, s in enumerate(sizes) if s >= max(400, biggest * MIN_BLOB)}
    dropped = sum(s for i, s in enumerate(sizes) if i not in keep)

    alive = np.isin(label, list(keep))
    a[..., 3] = np.where(alive, a[..., 3], 0)
    ys, xs = np.where(alive)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    sub = a[y0:y1+1, x0:x1+1]
    return Image.fromarray(sub.clip(0, 255).astype(np.uint8), "RGBA"), k_bg, dropped


def fit(img, px):
    s = min(1.0, px / max(img.size))
    return img if s == 1.0 else img.resize(
        (max(1, round(img.width * s)), max(1, round(img.height * s))), Image.LANCZOS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--story", default="goldaxe")
    ap.add_argument("--only")
    args = ap.parse_args()

    root = pathlib.Path(__file__).resolve().parent.parent
    base = root / "stories" / args.story / "assets"
    raw = base / "raw"
    if not raw.is_dir():
        sys.exit(f"원본 폴더가 없습니다: {raw}")

    files = sorted(p for p in raw.iterdir()
                   if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"))
    if args.only:
        files = [p for p in files if p.stem == args.only]
    if not files:
        sys.exit("처리할 파일이 없습니다")

    made = 0
    for p in files:
        kind = kind_of(p.stem)
        img = Image.open(p)
        if kind in ("bg", "glow"):                    # 키잉하지 않는다
            dst = base / ("bg" if kind == "bg" else "prop") / f"{p.stem}.png"
            dst.parent.mkdir(parents=True, exist_ok=True)
            fit(img.convert("RGB"), BG_PX).save(dst)
            print(f"  {p.name:<28} {kind:<5} 그대로            → {dst.relative_to(base)}")
            made += 1
            continue

        cutout, k_bg, dropped = cut(img)
        folder = {"char": "char", "icon": "icon"}.get(kind, "prop")
        dst = base / folder / f"{p.stem}.png"
        dst.parent.mkdir(parents=True, exist_ok=True)
        if cutout is None:
            fit(img.convert("RGBA"), MASTER_PX).save(dst)
            print(f"  {p.name:<28} ⚠ 분홍 배경을 못 찾음 (K={k_bg:.0f}) → 원본 그대로")
        else:
            fit(cutout, MASTER_PX).save(dst)
            note = f"  부스러기 {dropped}px 제거" if dropped > 200 else ""
            print(f"  {p.name:<28} {kind:<5} K={k_bg:>3.0f} "
                  f"{cutout.width}x{cutout.height:<5} → {dst.relative_to(base)}{note}")
        made += 1

    print(f"\n원본 {len(files)}개 → 에셋 {made}개  ({base})")


if __name__ == "__main__":
    main()
