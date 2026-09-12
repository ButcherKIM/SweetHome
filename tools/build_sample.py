#!/usr/bin/env python3
"""금도끼 은도끼 뼈대 story.json 생성.

스키마의 모든 구조를 한 번씩 통과시키는 최소 표본이다 (3노드 구조 / 6비트).
이야기를 완성하는 것이 목적이 아니라 그릇이 쓸 만한지 보는 것이 목적이다.

구조: 비트(그림 한 장) > 줄(자막 한 문장 + 오디오 하나)
    그림책은 한 페이지에 2~3줄이 들어간다. 한 줄마다 화면이 바뀌면 애니메이션이지
    그림책이 아니다. 카메라는 비트 전체에 걸쳐 천천히 움직인다.

wordTimings 는 여기서 어절 길이에 비례해 추정한다.
실제 값은 S6(edge-tts)의 WordBoundary 로 대체된다.
"""
import json, pathlib

# 나레이션 속도. 프로토타입에서 4~7세 기준으로 실제 귀로 맞춰본 값이다.
# 글자당 290ms ≈ 초당 3.45음절. 앞뒤 여백 1.5초(그림이 자리잡고 나서 말이 시작된다).
# 이 값은 S6(edge-tts)이 합성 결과를 실측하면 그것으로 대체된다.
LEAD_MS, MS_PER_CHAR, MIN_MS = 1500, 290, 6000


def timings(text, duration_ms):
    """어절별 [문자시작, 문자끝(제외), 시작ms, 끝ms]. 공백 제외 글자수에 비례 배분."""
    spans, i = [], 0
    for token in text.split(" "):
        if token:
            spans.append((i, i + len(token)))
        i += len(token) + 1

    weights = [sum(1 for c in text[a:b] if c.isalnum()) or 1 for a, b in spans]
    total = sum(weights)
    out, t = [], 0
    for (a, b), w in zip(spans, weights):
        end = t + round(duration_ms * w / total)
        out.append([a, b, t, end])
        t = end
    out[-1][3] = duration_ms          # 반올림 오차를 마지막 어절이 흡수
    return out


def line(lid, text):
    dur = max(MIN_MS, LEAD_MS + sum(1 for c in text if not c.isspace()) * MS_PER_CHAR)
    return {"id": lid, "text": text, "audio": f"audio/{lid}.opus",
            "durationMs": dur, "wordTimings": timings(text, dur)}


def beat(bid, scene, texts):
    """그림 한 장 + 줄 2~3개. 비트의 길이는 줄의 합이다."""
    return {"id": bid, "scene": scene,
            "lines": [line(f"{bid}_{i+1}", t) for i, t in enumerate(texts)]}


WOODCUTTER = {"asset": "characters/woodcutter", "x": 0.32, "y": 0.80,
              "scale": 1.0, "z": 30, "anim": "breathe"}


def woodcutter(pose, **kw):
    return {**WOODCUTTER, "pose": pose, **kw}


story = {
    "schemaVersion": "0.5",
    "storyId": "goldaxe",
    "title": "금도끼 은도끼",
    "source": "한국 전래동화 (public domain)",
    "locale": "ko-KR",
    "targetAge": [4, 7],
    "styleId": "hanji-watercolor-v1",

    # bgTreatment: 프로토타입에서 눈으로 맞춘 값. 배경이 한 발 물러나 캐릭터가 앞으로 나온다.
    # 비트별로 scene.bgTreatment 로 덮어쓸 수 있다 (같은 배경으로 명암 대조를 만들 때).
    "stage": {"width": 1920, "height": 1080, "safeArea": 0.05,
              "bgTreatment": {"blurPx": 1.0, "brightness": 100, "saturate": 100}},

    "rootNode": "n_intro",
    "canonicalEnding": "n_end_honest",

    # Spec §6.3 — 한글 학습이 제품 목표이므로 기본 ON
    "subtitle": {"defaultOn": True, "highlightUnit": "eojeol",
                 "minFontPx": 64, "wordSpacingEm": 0.3, "maxLines": 2},

    # tint 는 더미 플레이어가 도형을 칠하는 색. 실제 에셋이 생기면 무시된다.
    "assets": {
        "backgrounds": {
            "bg_forest_day": {"src": "bg/bg_forest_day.png",  "tint": "#7C9A6B"},
            "bg_pond_day":   {"src": "bg/bg_pond_day.png",    "tint": "#6E8CA8"},
            "bg_pond_glow":  {"src": "bg/bg_pond_glow.png",   "tint": "#C9A24B"},
        },
        "characters": {
            "woodcutter": {
                "displayName": "나무꾼", "tint": "#4A7FB5",
                "poses": {
                    "idle":     "char/woodcutter_idle.png",
                    "sad":      "char/woodcutter_sad.png",
                    "surprise": "char/woodcutter_surprise.png",
                    "happy":    "char/woodcutter_happy.png",
                },
            },
            "spirit": {
                "displayName": "산신령", "tint": "#E8C86A",
                "poses": {"calm": "char/spirit_calm.png",
                          "smile": "char/spirit_smile.png"},
            },
        },
        "props": {
            "axe_iron":   {"src": "prop/axe_iron.png",   "tint": "#8A8F98"},
            "axe_gold":   {"src": "prop/axe_gold.png",   "tint": "#E3B341"},
            "axe_silver": {"src": "prop/axe_silver.png", "tint": "#C6CBD1"},
            # 발광체는 검은 배경에 생성해 screen 으로 더한다. 오려낼 수 없기 때문이다.
            # 빛줄기 한 장은 산신령 등장·엔딩·다른 동화에서 그대로 재사용된다.
            "light_rays": {"src": "prop/light_rays.png", "tint": "#FFE9A8",
                           "blend": "screen"},
        },
    },

    "nodes": {
        "n_intro": {
            "type": "narrative",
            "beats": [
                beat("b_intro_01", {
                    "background": "bg_forest_day", "camera": "pushIn",
                    "transitionIn": "crossfade", "fx": "dust",
                    "actors": [woodcutter("idle", enter="fadeIn")],
                }, [
                    "산속 깊은 곳에 마음씨 착한 나무꾼이 살았어요.",
                    "오늘도 지게를 지고 나무를 하러 올라갔어요.",
                ]),

                beat("b_intro_02", {
                    "background": "bg_pond_day", "camera": "panRight",
                    "transitionIn": "pageTurn", "fx": "none",
                    # 빛이 쏟아지기 직전. 여기를 눌러둬야 다음 비트가 밝아 보인다.
                    "bgTreatment": {"blurPx": 1.0, "brightness": 68, "saturate": 52},
                    "actors": [
                        woodcutter("sad", enter="none"),
                        {"asset": "props/axe_iron", "x": 0.62, "y": 0.72,
                         "scale": 0.5, "z": 25, "anim": "bob", "enter": "slideIn"},
                    ],
                }, [
                    "그런데 그만, 도끼가 손에서 미끄러졌어요.",
                    "도끼는 깊은 연못 속으로 풍덩 빠져버렸어요.",
                    "나무꾼은 그 자리에 주저앉고 말았어요.",
                ]),

                beat("b_intro_03", {
                    "background": "bg_pond_glow", "camera": "pushIn",
                    "transitionIn": "crossfade", "fx": "sparkle",
                    "actors": [
                        woodcutter("surprise", x=0.22, enter="none"),
                        {"asset": "characters/spirit", "pose": "calm",
                         "x": 0.70, "y": 0.74, "scale": 1.25, "z": 20,
                         "anim": "bob", "enter": "fadeIn"},
                        {"asset": "props/axe_gold", "x": 0.56, "y": 0.60,
                         "scale": 0.55, "z": 35, "anim": "sway", "enter": "popIn"},
                        # 빛이 "쏟아진다" — 밝기만 올리는 것보다 직접적이다
                        {"asset": "props/light_rays", "x": 0.62, "y": 0.50,
                         "scale": 1.0, "z": 15, "anim": "pulse", "enter": "fadeIn"},
                    ],
                }, [
                    "그때 연못에서 환한 빛이 쏟아졌어요.",
                    "산신령이 스르르 나타났어요.",
                    "산신령은 반짝이는 금도끼를 들어 보였어요.",
                ]),
            ],
            "choice": {
                "promptText": "이것이 네 도끼냐?",
                "promptAudio": "audio/n_intro_choice.opus",
                "promptWordTimings": timings("이것이 네 도끼냐?", 2600),
                "options": [
                    {"id": "a", "label": "쇠도끼를 가리킨다", "tint": "#8A8F98",
                     "image": "icon/choice_point_iron.png", "next": "n_end_honest"},
                    {"id": "b", "label": "금도끼를 받는다",   "tint": "#E3B341",
                     "image": "icon/choice_take_gold.png",  "next": "n_end_greedy"},
                    {"id": "c", "label": "모르겠다고 한다",   "tint": "#9B8FB5",
                     "image": "icon/choice_shrug.png",      "next": "n_end_unsure"},
                ],
            },
        },

        # 결말 3종 — Spec §3.4: 배드엔딩 없음. 셋 다 따뜻하게 착지한다.
        "n_end_honest": {
            "type": "ending", "isCanonical": True,
            "endingTitle": "정직한 나무꾼",
            "lesson": "정직한 마음은 반짝반짝 빛난단다.",
            "beats": [beat("b_honest_01", {
                "background": "bg_pond_glow", "camera": "pullOut",
                "transitionIn": "crossfade", "fx": "sparkle",
                "actors": [
                    woodcutter("happy", x=0.24, enter="none"),
                    {"asset": "characters/spirit", "pose": "smile",
                     "x": 0.70, "y": 0.74, "scale": 1.25, "z": 20,
                     "anim": "bob", "enter": "none"},
                    {"asset": "props/axe_silver", "x": 0.50, "y": 0.58,
                     "scale": 0.45, "z": 34, "anim": "sway", "enter": "popIn"},
                    {"asset": "props/light_rays", "x": 0.60, "y": 0.50,
                     "scale": 0.9, "z": 15, "anim": "pulse", "enter": "none"},
                ],
            }, [
                "나무꾼은 낡은 쇠도끼를 가리켰어요.",
                "산신령은 빙그레 웃으며 도끼 세 자루를 모두 주었어요.",
            ])],
        },
        "n_end_greedy": {
            "type": "ending",
            "endingTitle": "사라진 금빛",
            "lesson": "내 것을 아끼는 마음이 가장 반짝인단다.",
            "beats": [beat("b_greedy_01", {
                "background": "bg_pond_day", "camera": "pullOut",
                "transitionIn": "wipe", "fx": "none",
                "actors": [
                    woodcutter("happy", x=0.34, enter="none"),
                    {"asset": "props/axe_iron", "x": 0.58, "y": 0.66,
                     "scale": 0.5, "z": 35, "anim": "sway", "enter": "popIn"},
                ],
            }, [
                "금도끼로 손을 뻗자 환한 빛이 스르르 사라졌어요.",
                "그래도 나무꾼의 쇠도끼는 그대로 남아 있었어요.",
            ])],
        },
        "n_end_unsure": {
            "type": "ending",
            "endingTitle": "함께 찾은 도끼",
            "lesson": "모를 땐 같이 찾아보면 된단다.",
            "beats": [beat("b_unsure_01", {
                "background": "bg_pond_glow", "camera": "tiltUp",
                "transitionIn": "crossfade", "fx": "fireflies",
                "actors": [
                    woodcutter("idle", x=0.28, enter="none"),
                    {"asset": "characters/spirit", "pose": "smile",
                     "x": 0.64, "y": 0.78, "scale": 1.1, "z": 20,
                     "anim": "bob", "enter": "none"},
                ],
            }, [
                "나무꾼은 잘 모르겠다고 솔직하게 말했어요.",
                "산신령은 함께 연못을 들여다봐 주었어요.",
            ])],
        },
    },
}

out = pathlib.Path("stories/goldaxe/story.json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(story, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

beats = [b for n in story["nodes"].values() for b in n["beats"]]
lines = [l for b in beats for l in b["lines"]]
secs = sum(l["durationMs"] for l in lines) / 1000
print(f"{out}  노드 {len(story['nodes'])} / 비트 {len(beats)} / 줄 {len(lines)} / 전체 {secs:.1f}초")
for b in beats:
    d = sum(l["durationMs"] for l in b["lines"]) / 1000
    print(f"  {b['id']:<14} {d:>5.1f}s  줄 {len(b['lines'])}개")
