#!/usr/bin/env python3
"""금도끼 은도끼 story.json 생성 — 전체 트리 (13노드 / 9결말).

구조: 노드 > 비트(그림 한 장) > 줄(자막 한 문장 + 오디오 하나)
    그림책은 한 페이지에 2~3줄이 들어간다. 한 줄마다 화면이 바뀌면 애니메이션이지
    그림책이 아니다. 카메라는 비트 전체에 걸쳐 천천히 움직인다.

트리:
    도입 ─◆분기1(도끼를 잃고 어떻게 할까)─┬─ 들어가 본다 ─┐
                                          ├─ 기다린다   ─┼─◆분기2("이것이 네 도끼냐")─ 결말 9
                                          └─ 집에 갔다 옴 ─┘

    분기2의 답(정직/욕심/모름)이 결말을 가르고, 분기1의 경로(용기/인내/끈기)가
    그 결말에 색을 입힌다. 9개가 서로 다른 이야기가 되게 하는 장치다.

    ★ 원작 결말은 "들어가 본다 + 쇠도끼를 가리킨다" 하나뿐이다 (Spec §3.4).
      나머지 8개도 전부 따뜻하게 착지한다 — 배드엔딩은 만들지 않는다.

wordTimings 와 durationMs 는 여기서 추정한다.
실제 값은 tools/tts_gen.py 가 합성 결과를 실측해 덮어쓴다 (Spec §6.4).
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


SPIRIT = {"asset": "characters/spirit", "x": 0.70, "y": 0.74,
          "scale": 1.25, "z": 20, "anim": "bob", "enter": "none"}
RAYS   = {"asset": "props/light_rays", "x": 0.60, "y": 0.50,
          "scale": 0.9, "z": 15, "anim": "pulse", "enter": "none"}

# 결말 화면 3종. 아홉 결말이 답변별로 같은 구성을 공유하므로 에셋이 늘지 않는다.
ENDING_SCENES = {
    # 세 도끼를 다 받는다 — 가장 밝게
    "GLAD": {
        "background": "bg_pond_glow", "camera": "pullOut",
        "transitionIn": "crossfade", "fx": "sparkle",
        "actors": [
            woodcutter("happy", x=0.24, enter="none"),
            {**SPIRIT, "pose": "smile"},
            {"asset": "props/axe_gold", "x": 0.46, "y": 0.58,
             "scale": 0.42, "z": 35, "anim": "sway", "enter": "popIn"},
            {"asset": "props/axe_silver", "x": 0.54, "y": 0.56,
             "scale": 0.42, "z": 34, "anim": "sway", "enter": "popIn"},
        ],
    },
    # 빛은 사라지고 제 쇠도끼만 남는다 — 담담하게, 그래도 따뜻하게
    "PLAIN": {
        "background": "bg_pond_day", "camera": "pullOut",
        "transitionIn": "wipe", "fx": "none",
        "actors": [
            woodcutter("happy", x=0.34, enter="none"),
            {"asset": "props/axe_iron", "x": 0.58, "y": 0.66,
             "scale": 0.5, "z": 35, "anim": "sway", "enter": "popIn"},
        ],
    },
    # 산신령이 함께 찾아 준다 — 둘이 나란히
    "WARM": {
        "background": "bg_pond_glow", "camera": "tiltUp",
        "transitionIn": "crossfade", "fx": "fireflies",
        "bgTreatment": {"blurPx": 1.0, "brightness": 94, "saturate": 84},
        "actors": [
            woodcutter("idle", x=0.28, enter="none"),
            {**SPIRIT, "pose": "smile", "x": 0.64, "y": 0.78, "scale": 1.1},
            {"asset": "props/axe_iron", "x": 0.46, "y": 0.64,
             "scale": 0.42, "z": 35, "anim": "bob", "enter": "popIn"},
            RAYS,
        ],
    },
}


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
    "canonicalEnding": "n_end_wade_honest",

    # Spec §6.3 — 한글 학습이 제품 목표이므로 기본 ON
    "subtitle": {"defaultOn": True, "highlightUnit": "eojeol",
                 "minFontPx": 64, "wordSpacingEm": 0.3, "maxLines": 2},

    # tint 는 더미 플레이어가 도형을 칠하는 색. 실제 에셋이 생기면 무시된다.
    "assets": {
        "backgrounds": {
            "bg_forest_day": {"src": "bg/bg_forest_day.png",  "tint": "#7C9A6B"},
            "bg_pond_day":   {"src": "bg/bg_pond_day.png",    "tint": "#6E8CA8"},
            "bg_pond_glow":  {"src": "bg/bg_pond_glow.png",   "tint": "#C9A24B"},
            "bg_home_night": {"src": "bg/bg_home_night.png",  "tint": "#4A5568"},
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
        # ── 도입 ────────────────────────────────────────────────
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
                    "bgTreatment": {"blurPx": 1.0, "brightness": 78, "saturate": 62},
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
            ],
            "choice": {
                "promptText": "나무꾼은 어떻게 할까요?",
                "options": [
                    {"id": "a", "label": "연못에 들어간다", "tint": "#7E94A4",
                     "image": "icon/choice_wade.png", "next": "n_mid_wade"},
                    {"id": "b", "label": "앉아서 기다린다", "tint": "#8C9C7A",
                     "image": "icon/choice_wait.png", "next": "n_mid_wait"},
                    {"id": "c", "label": "집으로 돌아간다", "tint": "#C4A06A",
                     "image": "icon/choice_home.png", "next": "n_mid_home"},
                ],
            },
        },

        # ── 중간 3갈래 ──────────────────────────────────────────
        # 세 갈래 모두 "산신령 등장 + 금도끼" 로 모인다. 배경은 같은 에셋을 쓰고
        # bgTreatment 로 시간대를 달리해 에셋을 늘리지 않는다 (Spec §5.7).
        **{
            nid: {
                "type": "narrative",
                "beats": [
                    beat(f"b_{key}_01", mid_scene, mid_lines),
                    beat(f"b_{key}_02", {
                        "background": "bg_pond_glow", "camera": "pushIn",
                        "transitionIn": "crossfade", "fx": "sparkle",
                        **({"bgTreatment": glow} if glow else {}),
                        "actors": [
                            woodcutter("surprise", x=0.22, enter="none"),
                            {"asset": "characters/spirit", "pose": "calm",
                             "x": 0.70, "y": 0.74, "scale": 1.25, "z": 20,
                             "anim": "bob", "enter": "fadeIn"},
                            {"asset": "props/axe_gold", "x": 0.56, "y": 0.60,
                             "scale": 0.55, "z": 35, "anim": "sway", "enter": "popIn"},
                            {"asset": "props/light_rays", "x": 0.62, "y": 0.50,
                             "scale": 1.0, "z": 15, "anim": "pulse", "enter": "fadeIn"},
                        ],
                    }, [
                        "산신령이 스르르 나타났어요.",
                        "산신령은 반짝이는 금도끼를 들어 보였어요.",
                    ]),
                ],
                "choice": {
                    "promptText": "이것이 네 도끼냐?",
                    "options": [
                        {"id": "a", "label": "쇠도끼를 가리킨다", "tint": "#8A8F98",
                         "image": "icon/choice_point_iron.png", "next": f"n_end_{key}_honest"},
                        {"id": "b", "label": "금도끼를 받는다", "tint": "#D9B455",
                         "image": "icon/choice_take_gold.png", "next": f"n_end_{key}_greedy"},
                        {"id": "c", "label": "모르겠다고 한다", "tint": "#9B8FB5",
                         "image": "icon/choice_shrug.png", "next": f"n_end_{key}_unsure"},
                    ],
                },
            }
            for nid, key, glow, mid_scene, mid_lines in [
                ("n_mid_wade", "wade", None, {
                    "background": "bg_pond_day", "camera": "pushIn",
                    "transitionIn": "pageTurn", "fx": "none",
                    "actors": [woodcutter("sad", x=0.40, enter="none")],
                }, [
                    "나무꾼은 바지를 걷고 연못에 들어갔어요.",
                    "물이 차갑고 깊어서 도끼가 보이지 않았어요.",
                    "그때 물속에서 환한 빛이 올라왔어요.",
                ]),
                ("n_mid_wait", "wait", {"blurPx": 1.0, "brightness": 88, "saturate": 70}, {
                    "background": "bg_pond_day", "camera": "pullOut",
                    "transitionIn": "pageTurn", "fx": "dust",
                    "bgTreatment": {"blurPx": 1.0, "brightness": 84, "saturate": 66},
                    "actors": [woodcutter("sad", x=0.30, enter="none")],
                }, [
                    "나무꾼은 연못가에 앉아 한참을 기다렸어요.",
                    "해가 기울고 물안개가 스르르 피어올랐어요.",
                    "그때 안개 속에서 환한 빛이 쏟아졌어요.",
                ]),
                ("n_mid_home", "home", {"blurPx": 1.0, "brightness": 92, "saturate": 78}, {
                    "background": "bg_home_night", "camera": "panLeft",
                    "transitionIn": "pageTurn", "fx": "fireflies",
                    "actors": [woodcutter("sad", x=0.36, enter="none")],
                }, [
                    "나무꾼은 터덜터덜 집으로 돌아갔어요.",
                    "밤새 뒤척이다 새벽에 다시 연못으로 갔어요.",
                    "연못에는 환한 빛이 기다리고 있었어요.",
                ]),
            ]
        },

        # ── 결말 9개 ────────────────────────────────────────────
        # 답(정직/욕심/모름)이 결과를 가르고, 경로(용기/인내/끈기)가 색을 입힌다.
        # 아홉 개 모두 따뜻하게 착지한다 (Spec §3.4).
        **{
            f"n_end_{key}_{ans}": {
                "type": "ending",
                **({"isCanonical": True} if (key, ans) == ("wade", "honest") else {}),
                "endingTitle": title,
                "lesson": lesson,
                "beats": [beat(f"b_end_{key}_{ans}", ENDING_SCENES[scene], lines)],
            }
            for key, ans, title, lesson, scene, lines in [
                # 정직 — 세 도끼를 다 받는다
                ("wade", "honest", "정직한 나무꾼", "정직한 마음은 반짝반짝 빛난단다.",
                 "GLAD", ["나무꾼은 낡은 쇠도끼를 가리켰어요.",
                          "산신령은 빙그레 웃으며 도끼 세 자루를 모두 주었어요."]),
                ("wait", "honest", "기다린 보람", "기다릴 줄 아는 마음도 참 고운 마음이란다.",
                 "GLAD", ["나무꾼은 낡은 쇠도끼를 가리켰어요.",
                          "오래 기다린 마음이 곱다며 세 자루를 모두 주었어요."]),
                ("home", "honest", "다시 온 아침", "포기하지 않는 마음은 언젠가 꼭 닿는단다.",
                 "GLAD", ["나무꾼은 낡은 쇠도끼를 가리켰어요.",
                          "다시 찾아온 마음이 기특하다며 세 자루를 주었어요."]),
                # 욕심 — 빛은 사라지지만 제 도끼는 남는다
                ("wade", "greedy", "물에 비친 금빛", "찾던 것은 늘 가까이에 있단다.",
                 "PLAIN", ["금도끼로 손을 뻗자 환한 빛이 스르르 사라졌어요.",
                           "대신 차가운 물속에서 쇠도끼가 반짝 떠올랐어요."]),
                ("wait", "greedy", "안개 속으로", "내 것을 아끼는 마음이 가장 반짝인단다.",
                 "PLAIN", ["금도끼로 손을 뻗자 빛이 안개 속으로 사라졌어요.",
                           "안개가 걷힌 자리에 나무꾼의 쇠도끼가 놓여 있었어요."]),
                ("home", "greedy", "새벽빛이 걷히고", "욕심을 내려놓으면 마음이 가벼워진단다.",
                 "PLAIN", ["금도끼로 손을 뻗자 새벽빛이 스르르 사라졌어요.",
                           "그래도 나무꾼의 쇠도끼는 그 자리에 있었어요."]),
                # 모름 — 산신령이 함께 찾아 준다
                ("wade", "unsure", "함께 더듬은 물속", "모를 땐 같이 찾아보면 된단다.",
                 "WARM", ["나무꾼은 잘 모르겠다고 솔직하게 말했어요.",
                          "산신령은 물속을 함께 더듬어 쇠도끼를 찾아 주었어요."]),
                ("wait", "unsure", "안개가 걷히고", "천천히 보면 보이는 것들이 있단다.",
                 "WARM", ["나무꾼은 잘 모르겠다고 솔직하게 말했어요.",
                          "산신령이 안개를 걷어 주자 쇠도끼가 보였어요."]),
                ("home", "unsure", "함께 맞은 아침", "혼자보다 둘이 더 잘 찾는단다.",
                 "WARM", ["나무꾼은 잘 모르겠다고 솔직하게 말했어요.",
                          "산신령은 해가 뜰 때까지 함께 찾아 주었어요."]),
            ]
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
