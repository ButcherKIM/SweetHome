# 안티그라비티 프롬프트 — 5개 메시지로 22장

> Flow는 다중 이미지 생성이 안 됐고, 안티그라비티는 됐다.
> 아래 5개를 순서대로 보내면 끝난다. 저장 경로가 프롬프트에 들어 있으므로
> 그대로 저장되면 `python3 tools/cutout.py` 한 번으로 처리된다.
>
> 스타일 기준: [style-bible.md](./style-bible.md) `한지 수채`

## 순서

| # | 메시지 | 장수 | 참조 |
|---|---|---|---|
| 1 | 산신령 밑그림 + 포즈 2 | 3 | 1장을 먼저 만들고 2·3이 그걸 읽는다 |
| 2 | 나무꾼 밑그림 + 포즈 4 | 5 | 1장을 먼저 만들고 2~5가 그걸 읽는다 |
| 3 | 소품 | 4 | — |
| 4 | 배경 | 4 | 2장을 먼저 만들고 3이 그걸 읽는다 |
| 5 | 선택지 | 6 | — |

**첨부도 없고 미리 올릴 파일도 없다.** 모든 참조는 같은 메시지 안에서
먼저 만들어 저장한 파일을 경로로 가리킨다. 22장 전부 여기서 나온다.

> ①과 ②는 첫 장(밑그림)이 나머지의 기준이다. **밑그림을 눈으로 확인하고 넘어간다.**
> 밑그림이 틀리면 뒤따라 나온 것이 전부 틀린다.

---

## ① 산신령 — 밑그림 + 포즈 2

```
Please generate 3 SEPARATE images. Do NOT merge them into one picture.
Generate IMAGE 1 first and save it. Then read that saved file back and use it as the
visual reference for IMAGE 2 and IMAGE 3 — all three must show the exact same character.

=== SHARED STYLE — apply to every image ===
Korean folk tale picture-book illustration, hanji paper watercolor with visible paper grain,
soft brush ink outlines, muted earth palette of sage green, clay ochre and warm grey,
flat even lighting with no harsh shadows, characters 2.5 heads tall with rounded
simplified forms and small gentle features, hand-painted children's book art,
completely static image, single still frame, no camera movement, no motion, no animation,
no text, no lettering, no watermark, no signature

=== THE CHARACTER ===
A gentle Korean mountain spirit (sanshin): an elderly sage with a long flowing white beard
and long white eyebrows, loose pale robes with soft golden trim, a simple wooden staff,
a faint warm glow around him, kind smiling eyes. He floats slightly above the ground
rather than standing on it.

=== [IMAGE 1] reference sheet ===
Save as: style/refs/spirit_sheet.png
Show the SAME character three times side by side in one image:
full-body front view, full-body three-quarter view, and a head close-up.
Background: plain flat MAGENTA #FF00FF, completely even.
No shadow, no ground, no cast shadow, no floor line.

=== [IMAGE 2] ===
Save as: stories/goldaxe/assets/raw/char_spirit_calm.png
Full body, floating upright, one hand holding a golden axe out toward the viewer,
serene expression.
Facing slightly to the LEFT, three-quarter view turned toward the left side of the frame.
Background: plain flat MAGENTA #FF00FF, completely even.
No shadow, no ground, no cast shadow, no floor line, no other objects.
Same face, same robes, same colours as style/refs/spirit_sheet.png.

=== [IMAGE 3] ===
Save as: stories/goldaxe/assets/raw/char_spirit_smile.png
Full body, floating upright, both arms open in a giving gesture, warm smile.
Facing slightly to the LEFT, three-quarter view turned toward the left side of the frame.
Background: plain flat MAGENTA #FF00FF, completely even.
No shadow, no ground, no cast shadow, no floor line, no other objects.
Same face, same robes, same colours as style/refs/spirit_sheet.png.
```

---

## ② 나무꾼 — 밑그림 + 포즈 4

```
Please generate 5 SEPARATE images. Do NOT merge them into one picture.
Generate IMAGE 1 first and save it. Then read that saved file back and use it as the
visual reference for IMAGE 2, 3, 4 and 5 — all five must show the exact same person.

=== SHARED STYLE — apply to every image ===
Korean folk tale picture-book illustration, hanji paper watercolor with visible paper grain,
soft brush ink outlines, muted earth palette of sage green, clay ochre and warm grey,
flat even lighting with no harsh shadows, characters 2.5 heads tall with rounded
simplified forms and small gentle features, hand-painted children's book art,
completely static image, single still frame, no camera movement, no motion, no animation,
no text, no lettering, no watermark, no signature

=== THE CHARACTER ===
A young Korean woodcutter from an old folk tale: a kind round face with rosy cheeks
and small gentle eyes, black hair tied in a simple topknot with a plain cloth headband,
a loose pale beige hemp jacket (jeogori) with a dark sash, dark grey work trousers
gathered at the ankles, straw sandals. Humble, cheerful, a little clumsy looking.
He owns almost nothing.

=== [IMAGE 1] reference sheet ===
Save as: style/refs/woodcutter_sheet.png
Show the SAME character three times side by side in one image:
full-body front view, full-body three-quarter view, and a head close-up.
Background: plain flat MAGENTA #FF00FF, completely even.
No shadow, no ground, no cast shadow, no floor line.

=== SHARED RULES — images 2, 3, 4 and 5 ===
Full body, single character, no one else in frame.
Facing slightly to the RIGHT, three-quarter view turned toward the right side of the frame.
Background: plain flat MAGENTA #FF00FF, completely even.
No shadow, no ground, no cast shadow, no floor line, no other objects.
Same face, same clothes, same colours as style/refs/woodcutter_sheet.png.
Same size and same framing in all four.

=== [IMAGE 2] ===
Save as: stories/goldaxe/assets/raw/char_woodcutter_idle.png
Standing calmly, holding an axe over his shoulder, faint friendly smile.

=== [IMAGE 3] ===
Save as: stories/goldaxe/assets/raw/char_woodcutter_sad.png
Shoulders drooped, both hands empty and open, looking down, worried face.

=== [IMAGE 4] ===
Save as: stories/goldaxe/assets/raw/char_woodcutter_happy.png
Both arms raised in delight, big open smile, standing upright.

=== [IMAGE 5] ===
Save as: stories/goldaxe/assets/raw/char_woodcutter_surprise.png
Eyes wide open and mouth open in surprise, both hands raised near his chest,
leaning back slightly. Startled but not frightened.
```

---

## ③ 소품 4

```
Please generate 4 SEPARATE images. Do NOT merge them into one picture.

=== SHARED STYLE — apply to every image ===
Korean folk tale picture-book illustration, hanji paper watercolor with visible paper grain,
soft brush ink outlines, muted earth palette of sage green, clay ochre and warm grey,
flat even lighting with no harsh shadows, hand-painted children's book art,
completely static image, single still frame, no camera movement, no motion, no animation,
no text, no lettering, no watermark, no signature

=== CONSISTENCY — images 1, 2 and 3 are a matched set ===
They are the same axe in three materials, so they MUST share:
- The SAME orientation: wooden handle at the BOTTOM-RIGHT, axe head at the TOP-LEFT,
  cutting edge facing LEFT, tilted roughly 30 degrees from vertical.
- The SAME size, the SAME position in frame, the SAME framing and margins.
- The SAME handle shape and the SAME head shape — only the material differs.
Side by side they should look identical except for the metal.

=== [IMAGE 1] ===
Save as: stories/goldaxe/assets/raw/prop_axe_iron.png
A plain old axe: dull grey worn iron head, plain worn wooden handle.
Background: plain flat MAGENTA #FF00FF, completely even.
No shadow, no ground, no cast shadow, no hands, no other objects.

=== [IMAGE 2] ===
Save as: stories/goldaxe/assets/raw/prop_axe_gold.png
The SAME axe, but the head is shining gold with a soft warm glow and the handle is
a richer ornate wood.
Background: plain flat MAGENTA #FF00FF, completely even.
No shadow, no ground, no cast shadow, no hands, no other objects.

=== [IMAGE 3] ===
Save as: stories/goldaxe/assets/raw/prop_axe_silver.png
The SAME axe, but the head is shining silver with a soft cool glow and the handle is
a pale light wood.
Background: plain flat MAGENTA #FF00FF, completely even.
No shadow, no ground, no cast shadow, no hands, no other objects.

=== [IMAGE 4] === ⚠ DIFFERENT BACKGROUND — not part of the set above
Save as: stories/goldaxe/assets/raw/prop_light_rays.png
Soft golden light rays fanning upward and outward from a point near the bottom,
with gentle glowing haze, fading out smoothly toward the edges. Warm golden tone.
Background: PURE SOLID BLACK #000000 — NOT magenta. Absolute black, no grey.
Nothing else in the image: no scenery, no objects, no characters, no ground, no border.
Aspect ratio 16:9.
```

---

## ④ 배경 4

```
Please generate 4 SEPARATE images. Do NOT merge them into one picture.

=== SHARED STYLE — apply to every image ===
Korean folk tale picture-book illustration, hanji paper watercolor with visible paper grain,
soft brush ink outlines, muted earth palette of sage green, clay ochre and warm grey,
flat even lighting, hand-painted children's book art,
completely static image, single still frame, no camera movement, no motion, no animation,
no text, no lettering, no watermark, no signature

=== SHARED RULES — every image ===
A wide establishing shot. Very simple and flat: only three depth layers, large simple
shapes, minimal detail. Use the SAME thick soft ink outline weight as a children's
picture book character. The background must stay quiet and recede so a character placed
in front of it stands out. Leave the lower middle area open and uncluttered.
Horizon in the lower third, shallow flat perspective like a picture book page.
ABSOLUTELY NO people, NO characters, NO animals, NO human figures anywhere.
Very wide panoramic composition, aspect ratio 21:9.

=== [IMAGE 1] ===
Save as: stories/goldaxe/assets/raw/bg_forest_day.png
A quiet Korean mountain forest path in soft morning light, tall pine trees,
mossy rocks, ferns along the path, a distant ridge.
Bright and airy with light high-key values. Do NOT make it dark, moody or atmospheric.

=== [IMAGE 2] === generate this BEFORE image 3
Save as: stories/goldaxe/assets/raw/bg_pond_glow.png
A still forest pond ringed by pine trees and mossy rocks, at the magical moment:
warm golden light welling up out of the water, a soft glowing haze over the surface,
gentle mist. Radiant and wondrous, still gentle and calm.

=== [IMAGE 3] ===
Save as: stories/goldaxe/assets/raw/bg_pond_day.png
Read the file you just saved at stories/goldaxe/assets/raw/bg_pond_glow.png and keep
the SAME composition — the same camera angle and the same placement of every pine tree,
rock and water edge. It must read as the very same place.
Change ONLY the light: this is the ordinary moment BEFORE anything magical happens.
Plain quiet overcast daylight, unremarkable. No golden glow, no light rays, no mist,
no sparkle. Slightly cooler and duller. Bright and airy, NOT dark or moody.

=== [IMAGE 4] ===
Save as: stories/goldaxe/assets/raw/bg_home_night.png
A small humble Korean thatched-roof cottage at night, warm lamplight glowing softly
through the paper window, a low stone wall, a persimmon tree beside the gate,
a quiet night sky with a few stars.
Gentle and calm, NOT dark or scary. Soft blue-grey night tones with warm lamplight.
```

---

## ⑤ 선택지 6

```
Please generate 6 SEPARATE images. Do NOT merge them into one picture.

=== SHARED STYLE — apply to every image ===
Korean folk tale picture-book illustration, hanji paper watercolor with visible paper grain,
soft brush ink outlines, muted earth palette of sage green, clay ochre and warm grey,
flat even lighting with no harsh shadows, hand-painted children's book art,
completely static image, single still frame, no camera movement, no motion, no animation,
no text, no lettering, no watermark, no signature

=== SHARED RULES — every image ===
A simple icon-like illustration. Single focus, large and easy to read at a glance.
A four-year-old who cannot read must understand it from the picture alone.
Background: plain flat MAGENTA #FF00FF, completely even.
No shadow, no ground, no text.

=== CONSISTENCY ===
Images 1-3 are shown side by side to a child, so they must be the SAME size,
the SAME framing and clearly DIFFERENT from one another at a glance.
The same goes for images 4-6.

=== [IMAGE 1] ===
Save as: stories/goldaxe/assets/raw/choice_wade.png
A pair of bare feet stepping into shallow pond water, with ripples spreading.

=== [IMAGE 2] ===
Save as: stories/goldaxe/assets/raw/choice_wait.png
A person sitting cross-legged beside water, seen from behind, waiting quietly.

=== [IMAGE 3] ===
Save as: stories/goldaxe/assets/raw/choice_home.png
A small thatched-roof cottage with a warm glowing window, seen from a distance.

=== [IMAGE 4] ===
Save as: stories/goldaxe/assets/raw/choice_point_iron.png
A hand pointing at a plain old iron axe.

=== [IMAGE 5] ===
Save as: stories/goldaxe/assets/raw/choice_take_gold.png
A hand reaching out to grab a shining golden axe.

=== [IMAGE 6] ===
Save as: stories/goldaxe/assets/raw/choice_shrug.png
Two open empty hands raised in an "I don't know" gesture.
```

---

## 다 되면

푸시하면 끝. 나머지는 `python3 tools/cutout.py` 가 한다.
