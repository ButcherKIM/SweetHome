# 이미지 생성 프롬프트 모음

> Gemini 웹 UI에 **복붙**하는 용도. 유료 API를 쓰지 않으므로 이 파일이 사실상의 생성 도구다.
> 관련: [Pipeline.md §S1 §S4](../Pipeline.md) · [StoryTellingSpec.md §5](../StoryTellingSpec.md)

**프롬프트는 영어로 쓴다.** 이미지 모델은 영어 스타일 지시를 훨씬 안정적으로 따른다.
아래 블록을 그대로 복사해 붙여 넣으면 된다.

---

## 0. 작업 순서 — 이 순서를 지켜야 한다

```
1. 캐릭터 시트 생성   → 저장 (style/refs/)      ※ 건너뛰면 이후 전부 다른 사람이 나온다
2. 시트를 첨부하고 포즈별 컷아웃 생성
3. 배경 생성 (캐릭터 없이, 21:9)
4. 소품 · 선택지 그림
```

**1번이 가장 중요하다.** 캐릭터 시트 없이 포즈를 하나씩 뽑으면 컷마다 다른 사람이 되고,
그것이 AI 동화 앱이 실패하는 1순위 원인이다 (Spec §5.2).

---

## 1. 공통 스타일 토큰

**모든 프롬프트 맨 앞에 붙인다.** 아트 스타일(D15)이 확정되면 이 블록만 고치면 된다.

```
Korean folk tale picture-book illustration, hanji paper watercolor with visible paper grain,
soft brush ink outlines, muted earth palette of sage green, clay ochre and warm grey,
flat even daylight with no harsh shadows, characters 2.5 heads tall with rounded
simplified forms and small gentle features, hand-painted children's book art,
no text, no lettering, no watermark, no signature
```

---

## 2. 캐릭터 시트 `style/refs/`

### 2.1 나무꾼 (woodcutter)

```
Korean folk tale picture-book illustration, hanji paper watercolor with visible paper grain,
soft brush ink outlines, muted earth palette of sage green, clay ochre and warm grey,
flat even daylight with no harsh shadows, characters 2.5 heads tall with rounded
simplified forms and small gentle features, hand-painted children's book art,
no text, no lettering, no watermark, no signature

Character reference sheet of a kind young Korean woodcutter in his early twenties.
He wears a simple undyed hemp jeogori jacket and baji trousers with a dark cloth waist sash,
straw shoes, and his hair tied in a small topknot with a plain headband.
Show the SAME character three times side by side in one image:
full-body front view, full-body side view, and a head close-up with a neutral expression.
Relaxed standing pose, arms at his sides.
Plain flat magenta #FF00FF background.
No shadow, no ground, no cast shadow, no floor line.
```

### 2.2 산신령 (spirit)

```
[공통 스타일 토큰]

Character reference sheet of a gentle Korean mountain spirit (sanshin), an elderly sage
with a long flowing white beard and long white eyebrows, wearing loose pale robes
with soft golden trim, holding a simple wooden staff, a faint warm glow around him,
kind smiling eyes. He floats slightly rather than standing.
Show the SAME character three times side by side in one image:
full-body front view, full-body three-quarter view, and a head close-up.
Plain flat magenta #FF00FF background.
No shadow, no ground, no cast shadow, no floor line.
```

---

## 3. 캐릭터 포즈 컷아웃 `assets/char/`

> **반드시 해당 캐릭터 시트를 레퍼런스 이미지로 첨부하고**, 프롬프트 끝에
> `Keep this exact character design, same face, same clothes, same colors.` 를 붙인다.

### ⚠️ 방향 규칙 — 전부 **오른쪽을 향해** 뽑는다

무대 연출의 기본은 **인물이 무대 안쪽(상대역 쪽)을 본다**는 것이다. 왼쪽에 선 인물이
왼쪽을 보면 화면 밖을 보는 꼴이 되어 어색하다.

에셋을 방향별로 두 벌 만들 필요는 없다. **전부 오른쪽을 향해 한 벌만** 만들고,
오른쪽에 배치할 때 `story.json` 에서 뒤집는다.

```jsonc
{ "asset": "characters/woodcutter", "pose": "surprise", "x": 0.28, "y": 0.80 }              // 왼쪽 — 그대로 (오른쪽을 본다)
{ "asset": "characters/spirit",     "pose": "calm",     "x": 0.70, "y": 0.74, "flip": true } // 오른쪽 — 뒤집어 왼쪽을 본다
```

프롬프트에 아래 문장을 넣는다.

```
Facing slightly to the RIGHT, three-quarter view turned toward the right side of the frame.
```

이미 왼쪽을 보는 에셋을 뽑았다면 다시 뽑을 것 없이 `"flip": true` 만 붙이면 된다.

| 파일명 | 포즈 설명 (아래 `{POSE}` 자리에 넣는다) |
|---|---|
| `char_woodcutter_idle.png` | standing calmly, holding an axe over his shoulder, faint friendly smile |
| `char_woodcutter_sad.png` | shoulders drooped, both hands empty and open, looking down, worried face |
| `char_woodcutter_surprise.png` | leaning back slightly, both hands raised near his chest, eyes wide, mouth open in surprise |
| `char_woodcutter_happy.png` | both arms raised in delight, big open smile, standing upright |
| `char_spirit_calm.png` | floating upright, one hand holding a golden axe out toward the viewer, serene expression |
| `char_spirit_smile.png` | floating upright, both arms open in a giving gesture, warm smile |

**템플릿**

```
[공통 스타일 토큰]

Full body single character, {POSE}.
Facing slightly to the RIGHT, three-quarter view turned toward the right side of the frame.
Isolated on a plain flat magenta #FF00FF background.
No shadow, no ground, no cast shadow, no floor line, no other objects.
Keep this exact character design, same face, same clothes, same colors.
```

---

## 4. 배경 `assets/bg/`

> **21:9로 뽑는다.** 화면은 16:9인데 카메라가 좌우로 움직이므로 여유분이 필요하다.
> 좁게 뽑으면 팬 할 때 가장자리가 비어 보인다.
> **인물이 들어가면 안 된다.** 배경 속 사람과 컷아웃 캐릭터가 겹쳐 나온다.

| 파일명 | 장면 설명 (`{SCENE}`) |
|---|---|
| `bg_forest_day.png` | a quiet Korean mountain forest path in soft morning light, tall pine trees, mossy rocks, ferns, a distant ridge |
| `bg_pond_day.png` | a small still forest pond in a Korean mountain valley, pine trees and mossy rocks around the water, calm reflective surface, overcast soft daylight |
| `bg_pond_glow.png` | the same small forest pond at dusk, warm golden light rising from the water surface and glowing through thin mist, pine trees silhouetted, magical but gentle |

**템플릿**

```
[공통 스타일 토큰]

A wide establishing shot of {SCENE}.
Horizon in the lower third, shallow flat perspective like a picture book page.
ABSOLUTELY NO people, NO characters, NO animals, NO human figures anywhere in the image.
Very wide panoramic composition, aspect ratio 21:9.
```

---

## 5. 소품 `assets/prop/`

| 파일명 | 설명 (`{PROP}`) |
|---|---|
| `prop_axe_iron.png` | a plain old iron axe with a worn wooden handle |
| `prop_axe_gold.png` | a shining golden axe with an ornate handle, soft warm glow |
| `prop_axe_silver.png` | a shining silver axe with a pale handle, soft cool glow |

```
[공통 스타일 토큰]

{PROP}, single object, centered, seen from the side.
Isolated on a plain flat magenta #FF00FF background.
No shadow, no ground, no cast shadow, no hands, no other objects.
```

---

## 6. 선택지 그림 `assets/icon/`

> 4~7세는 선택지를 **그림으로 이해한다** (Spec §3.5). 글자 없이도 뭘 고르는지 보여야 한다.

| 파일명 | 설명 (`{ACTION}`) |
|---|---|
| `choice_point_iron.png` | a hand pointing at a plain old iron axe |
| `choice_take_gold.png` | a hand reaching out to grab a shining golden axe |
| `choice_shrug.png` | two open empty hands raised in a "I don't know" gesture |

```
[공통 스타일 토큰]

{ACTION}. Simple clear composition, single focus, large and easy to read at a glance.
Isolated on a plain flat magenta #FF00FF background. No shadow, no ground, no text.
```

---

## 7. 생성할 때 확인할 것

받은 이미지를 저장하기 전에 매번 본다.

- [ ] **캐릭터 시트와 같은 사람인가** ← 가장 중요. 아니면 다시
- [ ] **오른쪽을 향하고 있는가** (§3 방향 규칙)
- [ ] 배경이 고른 마젠타인가 (얼룩·그라데이션 없이)
- [ ] **발밑에 그림자나 바닥선이 없는가** ← 있으면 컷아웃 후 회색 얼룩이 남는다
- [ ] 손발이 잘리지 않았는가
- [ ] 배경 이미지: 사람이 안 들어갔는가, 충분히 가로로 넓은가
- [ ] 글자·서명·워터마크가 없는가

## 8. 잘 안 될 때

| 증상 | 대처 |
|---|---|
| 발밑에 그림자가 생긴다 | `no shadow, no ground, no cast shadow, no floor line` 를 **맨 뒤에 한 번 더** 반복 |
| 배경에 사람이 나온다 | `ABSOLUTELY NO people` 을 대문자로 강조하고 문장 맨 앞으로 옮긴다 |
| 마젠타가 아니라 흰 배경이 나온다 | `on a solid bright magenta background (hot pink #FF00FF)` 로 풀어 쓴다 |
| 캐릭터가 매번 달라진다 | 시트를 첨부했는지 확인. 첨부해도 안 되면 시트를 다시 만든다 |
| 21:9가 안 나온다 | `extremely wide panoramic banner composition, much wider than tall` 을 덧붙인다 |
| 그림체가 매번 다르다 | 공통 스타일 토큰을 **통째로** 앞에 붙였는지 확인 (요약하면 안 된다) |
| 인물이 화면 밖을 본다 | 다시 뽑지 말고 `story.json` 에 `"flip": true` 추가 (§3 방향 규칙) |
| 구석에 반짝이·장식이 붙는다 | **프롬프트로는 막을 수 없다.** 플레이어가 마젠타를 걷어낼 때 가장 큰 덩어리만 남겨 자동 제거한다 |

## 9. 파일 저장

```
캐릭터 시트   style/refs/woodcutter_sheet.png
캐릭터        stories/goldaxe/assets/char/char_woodcutter_surprise.png
배경          stories/goldaxe/assets/bg/bg_pond_glow.png
소품          stories/goldaxe/assets/prop/prop_axe_gold.png
선택지        stories/goldaxe/assets/icon/choice_point_iron.png
```

**마젠타 배경을 지우지 않아도 된다.** 플레이어가 불러올 때 브라우저에서 자동으로 걷어낸다.
