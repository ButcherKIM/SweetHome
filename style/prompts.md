# Flow 이미지 프롬프트 — 금도끼 은도끼

> **복붙용.** 유료 API를 쓰지 않으므로 이 파일이 사실상의 생성 도구다.
> 스타일: [style-bible.md](./style-bible.md) `D15 한지 수채 확정`
> 관련: [Pipeline §S4](../Pipeline.md) · [Spec §5](../StoryTellingSpec.md)

**남은 에셋 12개.** 완료: `bg_pond_glow`, `char_woodcutter_surprise`, 나무꾼 시트.

---

## 0. Flow에서 쓸 때

Flow는 영상 도구다. 정지 이미지로 쓰려면:

- 모든 프롬프트에 **`completely static image, single still frame, no camera movement, no motion, no animation`** 이 들어가 있다 (아래 토큰에 포함)
- 결과가 영상이면 **첫 프레임을 캡처**해서 쓴다
- **21:9를 못 고르면 16:9로** 받는다. 그 배경을 쓰는 비트는 `camera` 를 `still` 이나 `pushIn` 으로 두면 가장자리가 안 드러난다
- 레퍼런스 이미지는 Flow의 **Ingredients** 로 넣는다

**받은 이미지는 플레이어의 해당 슬롯에 끌어다 놓으면 끝이다.** 배경 제거는 브라우저가 한다.

---

## 1. 스타일 토큰 `모든 프롬프트 맨 앞에`

요약하지 말고 통째로 붙인다. 일부만 쓰면 그림체가 흔들린다.

```
Korean folk tale picture-book illustration, hanji paper watercolor with visible paper grain,
soft brush ink outlines, muted earth palette of sage green, clay ochre and warm grey,
flat even daylight with no harsh shadows, characters 2.5 heads tall with rounded
simplified forms and small gentle features, hand-painted children's book art,
completely static image, single still frame, no camera movement, no motion, no animation,
no text, no lettering, no watermark, no signature
```

아래에서 `[토큰]` 이라고 쓴 자리에 이 블록이 들어간다.

---

## 2. 산신령 시트 — **가장 먼저**

시트 없이 포즈를 뽑으면 컷마다 다른 사람이 된다. 뽑아서 `style/refs/spirit_sheet.png` 로 저장하고,
④⑤를 뽑을 때 Ingredients로 넣는다.

```
[토큰]

Character reference sheet of a gentle Korean mountain spirit (sanshin): an elderly sage
with a long flowing white beard and long white eyebrows, wearing loose pale robes
with soft golden trim, holding a simple wooden staff, a faint warm glow around him,
kind smiling eyes. He floats slightly rather than standing on the ground.
Show the SAME character three times side by side in one image:
full-body front view, full-body three-quarter view, and a head close-up.
Plain flat magenta #FF00FF background.
No shadow, no ground, no cast shadow, no floor line.
```

---

## 3. 캐릭터 5개 `Ingredients에 시트 첨부`

각 프롬프트 끝에 항상:
`Keep this exact character design, same face, same clothes, same colors.`

> **방향 규칙** — 나무꾼은 **오른쪽**, 산신령은 **왼쪽**을 본다.
> 무대 안쪽(상대역 쪽)을 봐야 어색하지 않다. 반대로 나오면 다시 뽑지 말고
> `story.json` 에 `"flip": true` 를 붙이면 된다.

### ① `char_woodcutter_idle` — 나무꾼 시트 첨부

```
[토큰]

Full body single character, standing calmly holding an axe over his shoulder,
faint friendly smile.
Facing slightly to the RIGHT, three-quarter view turned toward the right side of the frame.
Isolated on a plain flat magenta #FF00FF background.
No shadow, no ground, no cast shadow, no floor line, no other objects.
Keep this exact character design, same face, same clothes, same colors.
```

### ② `char_woodcutter_sad` — 나무꾼 시트 첨부

```
[토큰]

Full body single character, shoulders drooped, both hands empty and open,
looking down, worried face.
Facing slightly to the RIGHT, three-quarter view turned toward the right side of the frame.
Isolated on a plain flat magenta #FF00FF background.
No shadow, no ground, no cast shadow, no floor line, no other objects.
Keep this exact character design, same face, same clothes, same colors.
```

### ③ `char_woodcutter_happy` — 나무꾼 시트 첨부

```
[토큰]

Full body single character, both arms raised in delight, big open smile, standing upright.
Facing slightly to the RIGHT, three-quarter view turned toward the right side of the frame.
Isolated on a plain flat magenta #FF00FF background.
No shadow, no ground, no cast shadow, no floor line, no other objects.
Keep this exact character design, same face, same clothes, same colors.
```

### ④ `char_spirit_calm` — 산신령 시트 첨부

```
[토큰]

Full body single character, floating upright, one hand holding a golden axe
out toward the viewer, serene expression.
Facing slightly to the LEFT, three-quarter view turned toward the left side of the frame.
Isolated on a plain flat magenta #FF00FF background.
No shadow, no ground, no cast shadow, no floor line, no other objects.
Keep this exact character design, same face, same clothes, same colors.
```

### ⑤ `char_spirit_smile` — 산신령 시트 첨부

```
[토큰]

Full body single character, floating upright, both arms open in a giving gesture,
warm smile.
Facing slightly to the LEFT, three-quarter view turned toward the left side of the frame.
Isolated on a plain flat magenta #FF00FF background.
No shadow, no ground, no cast shadow, no floor line, no other objects.
Keep this exact character design, same face, same clothes, same colors.
```

---

## 4. 배경 2개

### ⑥ `bg_forest_day` — 숲길

```
[토큰]

A wide establishing shot of a quiet Korean mountain forest path in soft morning light,
tall pine trees, mossy rocks, ferns along the path, a distant ridge.

IMPORTANT STYLE RULES:
Bright and airy with light high-key values. Do NOT make it dark, moody or atmospheric.
Very simple and flat: only three depth layers, large simple shapes, minimal detail.
Use the SAME thick soft ink outline weight as a children's picture book character.
The background must stay quiet and recede so a character placed in front of it stands out.
Leave the lower middle area open and uncluttered.
Horizon in the lower third, shallow flat perspective like a picture book page.

ABSOLUTELY NO people, NO characters, NO animals, NO human figures anywhere.
Very wide panoramic composition, aspect ratio 21:9.
```

### ⑦ `bg_pond_day` — 평범한 연못 `bg_pond_glow 를 Ingredients로 첨부`

⚠️ **구도가 같아야 대조가 산다.** 구도까지 바뀌면 "빛이 쏟아졌다" 가 아니라
"장소가 바뀌었다" 로 읽힌다.

```
[토큰]

The SAME pond scene as the attached image — identical composition, identical camera angle,
identical placement of every pine tree, rock and water edge. Do not move or redesign anything.

Change ONLY the light. This is the ordinary moment BEFORE anything magical happens:
plain flat overcast daylight, quiet and unremarkable. No golden glow, no light rays,
no rising mist, no sparkle on the water. The pond surface is dull and still.
Slightly cooler and duller colors overall.

ABSOLUTELY NO people, NO characters, NO animals, NO human figures anywhere.
Very wide panoramic composition, aspect ratio 21:9.
```

> **더 싼 길이 먼저다.** 밝기·채도 차이만으로 충분하면 새로 뽑지 말고
> `scene.bgTreatment` 로 직전 비트를 눌러두면 된다 ([Spec §5.7](../StoryTellingSpec.md#57-배경-후처리--배경을-한-발-물린다)).
> 지금 표본은 이미 그렇게 해뒀다 — ⑦ 없이도 대조는 난다.

---

## 5. 소품 3개

```
[토큰]

{소품}, single object, centered, seen from the side.
Isolated on a plain flat magenta #FF00FF background.
No shadow, no ground, no cast shadow, no hands, no other objects.
```

| # | 파일 | `{소품}` |
|---|---|---|
| ⑧ | `prop_axe_iron` | `a plain old iron axe with a worn wooden handle` |
| ⑨ | `prop_axe_gold` | `a shining golden axe with an ornate handle and a soft warm glow` |
| ⑩ | `prop_axe_silver` | `a shining silver axe with a pale handle and a soft cool glow` |

---

## 6. 빛줄기 1개 — ⚠️ **검정 배경**

마젠타가 아니다. 빛은 반투명이라 오려낼 수 없어서, 검정에 뽑아 더하기 합성한다.

### ⑪ `prop_light_rays`

```
Hand-painted watercolor soft golden light rays fanning upward and outward from a point
near the bottom, with gentle glowing haze, fading out smoothly toward the edges.
Warm golden tone.

Pure solid BLACK background (#000000). Absolutely nothing else in the image —
no scenery, no objects, no characters, no ground, no border, no text.
Only the glow itself on pure black.
Completely static image, single still frame, no motion.
Aspect ratio 16:9.
```

> **재사용률이 가장 높은 에셋이다.** 산신령 등장, 엔딩, 다음 동화까지 이 한 장으로 간다.
> 한 장 잘 뽑아두면 계속 쓴다.
>
> 결과가 뿌옇게 들뜨면 검정이 회색빛인 것이다 —
> `pure #000000 black, absolute black, no grey` 를 덧붙인다.

---

## 7. 선택지 그림 3개

4~7세는 선택지를 **그림으로 이해한다.** 글자 없이도 뭘 고르는지 보여야 한다.

```
[토큰]

{행동}. Simple clear composition, single focus, large and easy to read at a glance.
Isolated on a plain flat magenta #FF00FF background.
No shadow, no ground, no text.
```

| # | 파일 | `{행동}` | 뜻 |
|---|---|---|---|
| ⑫ | `choice_point_iron` | `a hand pointing at a plain old iron axe` | 쇠도끼를 가리킨다 |
| ⑬ | `choice_take_gold` | `a hand reaching out to grab a shining golden axe` | 금도끼를 받는다 |
| ⑭ | `choice_shrug` | `two open empty hands raised in an "I don't know" gesture` | 모르겠다고 한다 |

---

## 8. 뽑을 때마다 확인

- [ ] **시트와 같은 사람인가** ← 아니면 다시. 제일 중요
- [ ] **오른쪽(산신령은 왼쪽)을 향하는가**
- [ ] **발밑에 그림자나 바닥선이 없는가** ← 있으면 오려낸 뒤 회색 얼룩이 남는다
- [ ] 마젠타가 얼룩 없이 고른가 (빛줄기는 검정이 순수한가)
- [ ] 손발이 잘리지 않았는가
- [ ] 배경: 사람이 없는가, 충분히 가로로 긴가, 하단 중앙이 비었는가
- [ ] 글자·서명·워터마크가 없는가

## 9. 잘 안 될 때

| 증상 | 대처 |
|---|---|
| 영상이 나온다 | 첫 프레임 캡처. 토큰의 `single still frame` 이 들어갔는지 확인 |
| 발밑에 그림자 | `no shadow, no ground, no cast shadow` 를 **맨 뒤에 한 번 더** |
| 배경에 사람이 나온다 | `ABSOLUTELY NO people` 을 **문장 맨 앞**으로 옮긴다 |
| 마젠타 대신 흰 배경 | `on a solid bright magenta background (hot pink #FF00FF)` 로 풀어 쓴다 |
| 빛이 뿌옇게 들뜬다 | 검정이 순수하지 않다. `pure #000000 black, absolute black, no grey` |
| 21:9가 안 나온다 | 16:9로 받고 그 비트의 `camera` 를 `still`/`pushIn` 으로 |
| 캐릭터가 매번 다르다 | 시트를 Ingredients에 넣었는지 확인. 넣어도 안 되면 시트를 다시 만든다 |
| 그림체가 매번 다르다 | 스타일 토큰을 **통째로** 붙였는지 확인 (요약하면 안 된다) |
| 인물이 화면 밖을 본다 | 다시 뽑지 말고 `story.json` 에 `"flip": true` |
| 구석에 반짝이·장식 | **프롬프트로는 못 막는다.** 플레이어가 가장 큰 덩어리만 남겨 자동 제거 |

## 10. 저장 위치

```
style/refs/spirit_sheet.png                        산신령 시트
stories/goldaxe/assets/char/char_woodcutter_idle.png
stories/goldaxe/assets/bg/bg_forest_day.png
stories/goldaxe/assets/prop/prop_axe_gold.png
stories/goldaxe/assets/icon/choice_point_iron.png
```

파일로 정리해두면 나중에 좋지만, **플레이어 슬롯에 바로 끌어다 놓아도 된다** —
아티팩트에 업로드되어 기기 간에 공유된다.
