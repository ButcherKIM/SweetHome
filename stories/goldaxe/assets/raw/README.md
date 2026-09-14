# 생성 원본을 여기에

안티그라비티(또는 다른 도구)가 저장한 **손대지 않은 원본**을 이 폴더에 넣습니다.
배경을 지우거나 자르지 마세요 — `tools/cutout.py` 가 합니다.

```bash
python3 tools/cutout.py            # raw/ → ../char, ../bg, ../prop, ../icon
python3 tools/cutout.py --only prop_axe_gold
```

## 파일명 (이 이름 그대로)

| 파일 | 배경 |
|---|---|
| `char_woodcutter_idle.png` `char_woodcutter_sad.png` `char_woodcutter_happy.png` | 마젠타 |
| `char_woodcutter_surprise.png` | 마젠타 |
| `char_spirit_calm.png` `char_spirit_smile.png` | 마젠타 |
| `bg_forest_day.png` `bg_pond_day.png` `bg_pond_glow.png` `bg_home_night.png` | 그대로 |
| `prop_axe_iron.png` `prop_axe_gold.png` `prop_axe_silver.png` | 마젠타 |
| `prop_light_rays.png` | **검정** |
| `choice_wade.png` `choice_wait.png` `choice_home.png` | 마젠타 |
| `choice_point_iron.png` `choice_take_gold.png` `choice_shrug.png` | 마젠타 |

`bg_` 로 시작하면 배경이라 키잉하지 않고, 이름에 `light`/`glow`/`ray` 가 있으면
발광체라 검은 배경째로 둡니다. 나머지는 분홍 배경을 걷어냅니다.

한 파일에 여러 개가 들어 있으면 왼쪽부터 `_1` `_2` `_3` 으로 나뉘어 나옵니다.

## 밑그림

`style/refs/woodcutter_sheet.png`, `style/refs/spirit_sheet.png` —
여기 말고 `style/refs/` 에 넣습니다. 앱에 안 들어가는 재료입니다.
