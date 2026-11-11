# SweetHome — 분기형 동화 앱

전래동화를 원작으로, 이야기 도중 아이가 고르면 결말이 달라지는 **읽어주는 그림책**.
대상 4~7세. 원작은 **금도끼 은도끼**. 분기 2회 × 선택 3개 = 결말 9개(1개는 원작).

**게임이 아니라 그림책이다.** 아이의 역할은 보고 듣는 것이고 개입은 분기점 2회뿐이다.
**그리고 한글 읽기 학습 앱이다.** 나레이션과 동시에 그 어절이 하이라이트된다 —
부가 기능이 아니라 학부모가 이 앱을 고르는 이유다.

---

## 0. 먼저 읽을 것 — 이 규칙이 제일 중요하다

> **제품 결정은 사용자만 확정한다.**
> 기획서를 고치려면 **허락을 받는다.** 혼자 바꾸지 않는다.
> `제안` 항목은 승인 전까지 구현 근거가 되지 못한다.
> 기술적 귀결(예: 무료 제약 → 무료 도구)만 자동으로 따라간다.

작업판·문서를 "더 좋게" 다시 짜는 것도 여기 해당한다. 사용자가 "이대로 하겠다"고
한 것을 묻지 않고 재구성하지 않는다.

**비용 0원.** 유료 API 를 쓰지 않는다. 이미지는 웹 UI 수작업, TTS 는 edge-tts.

---

## 1. 문서 — 이 셋이 기준이다

| 파일 | 무엇 |
|---|---|
| [StoryTellingSpec.md](./StoryTellingSpec.md) | **단일 기준점.** 제품 정의 · 스키마 · 아트 · 오디오 · 프론트엔드 · 결정 현황(D1~D20) |
| [Pipeline.md](./Pipeline.md) | 제작 파이프라인 S0~S8, 사람이 서는 게이트 3곳 |
| [GOAL.md](./GOAL.md) | **골 = 기획한 것을 다 구현했는가.** 구현 항목 60개 대조표 |

**변경 이력은 [CHANGELOG.md](./CHANGELOG.md)** 에 쌓는다 (v0.1.0 부터). 의미 있는 작업을 커밋할
때마다 버전 · 날짜 · 무엇이 왜 바뀌었는지를 같이 적는다. 앱 버전(`player/package.json`)과 맞춘다.

막혔으면 Spec 의 해당 절을 먼저 본다. 거의 다 적혀 있고, 왜 그렇게 정했는지도 있다.

---

## 2. 저장소

```
CLAUDE.md  StoryTellingSpec.md  Pipeline.md  GOAL.md  requirements.txt
schema/story.schema.json     스키마 0.5 — 콘텐츠의 계약
stories/goldaxe/
  story.json                 13노드 / 17비트 / 38줄 / 9결말 / 큐 57개
  audio/*.mp3                54개 (줄 38 + 선택지 질문 4 + 선택지 12)
  assets/raw/                ← 생성 원본을 여기에 넣는다 (지금 비어 있음)
  asset_manifest.json        S3 산출물
style/
  style-bible.md             한지 수채 — 팔레트 · 등신 · 방향 규칙
  prompts-antigravity.md     ★ 안티그라비티용. 메시지 5개로 22장
  prompts.md                 한 장씩 뽑던 Flow 시절 원본
  refs/                      밑그림 2장 (②①의 첫 장)
player/                      React + Vite 앱 — 아래 §3
  prototype.html             한 파일짜리 옛 프로토타입 (참고용, 앱 아님)
tools/                       build_sample · validate_story · tts_gen · cutout
                             · extract_assets · build_asset_board
tests/                       pytest — CI 가 돌린다
```

---

## 3. player/ — 엔진과 렌더러는 갈라져 있다

`D16`: **데모까지 웹, 제품화에서 React Native** ([Spec §8.5](./StoryTellingSpec.md#85-플랫폼-2단-경로--d16-확정)).
그때 다시 쓰는 것이 렌더러뿐이려면 경계가 실제 파일 경계여야 한다.

```
src/engine/    순수 TS. DOM·CSS·브라우저 API 금지 — RN 으로 그대로 간다
src/renderer/  웹 전용. RN 에서 다시 쓴다
src/audio/     나레이션 · 덕킹 · 출력 지연 보정
src/platform/  engine 을 브라우저에 붙이는 얇은 층
```

**이 규칙은 `tests/test_engine_is_pure.py` 가 CI 에서 강제한다.**
`engine/` 에 `document`·`window`·`fetch`·`react` 등이 들어오면 빨개진다.

---

## 4. 돌리는 법

**새 환경에서 처음이면 이것부터.** 안 하면 도구들이 바로 막힌다.

```bash
python3 -m pip install -r requirements.txt   # edge-tts · Pillow · numpy · jsonschema · pytest
cd player && npm install
```

```bash
# 앱
cd player && npm run dev                     # http://localhost:5173
npm run build                                # dist/ — stories/ 를 함께 복사한다

# 검증 — 고치고 나면 이 둘은 꼭
python3 tools/validate_story.py stories/goldaxe/story.json
python3 -m pytest tests/ -q

# 에셋
python3 tools/extract_assets.py              # 뭐가 쓰이고 뭐가 없는지
python3 tools/cutout.py                      # raw/ → char, bg, prop, icon
python3 tools/build_asset_board.py           # 프롬프트 md → 작업판 html

# 음성 (다시 뽑을 때만. story.json 의 durationMs·wordTimings 를 덮어쓴다)
python3 tools/tts_gen.py
```

CI: `.github/workflows/python-app.yml` — flake8 + pytest. **pytest 가 0건을 모으면
exit 5 로 실패한다.** 테스트를 지우지 말 것.

---

## 5. 지금 상태

**이야기·소리·앱은 서 있고, 그림이 0장이다.** 상세는 [GOAL.md](./GOAL.md).

| | |
|---|---|
| 이야기 | ✅ 13노드 · 17비트 · 38줄 · 9결말 · 연출 큐 57개 |
| 소리 | ✅ mp3 54개, 어절 타임스탬프 실측 |
| 앱 | ✅ 표지→비트→선택→결말까지 돈다. 번들 1.8MB |
| **그림** | ❌ **0 / 22** ← 여기서 막혀 있다 |
| BGM·SFX | ❌ CC0 음원이 없다 (`AudioBus` 에 자리와 덕킹은 있음) |

### 다음에 할 일

1. **그림 22장** — 안티그라비티에 [prompts-antigravity.md](./style/prompts-antigravity.md)
   의 메시지 5개를 순서대로. 저장 경로가 프롬프트 안에 들어 있다
2. `python3 tools/cutout.py` → 앱에서 확인
3. 아이에게 테스트 — [Spec §9.3](./StoryTellingSpec.md#93-데모가-답해야-할-질문) 질문 #1~#7
4. 그다음이 React Native (M6). **R18 선검증부터** — `blend: screen` 과 `blurPx` 가
   RN 에서 되는가. 안 되면 에셋 물량이 는다

### 열려 있는 질문 (사용자 답 대기)

- `D17` 화면 방향 · `D18` 오프라인 · `D19` 엔딩 보상 — 전부 v1 로 미뤄도 된다

정직 결말의 쇠도끼는 사용자 확정으로 넣었다 (v0.1.1) — [CHANGELOG.md](./CHANGELOG.md).

---

## 6. 조심할 것 — 전부 실제로 당한 것들

**조용히 실패하는 것들.** 화면에 아무 일도 안 일어나고 오류도 안 난다.

- **에셋 파일명은 [Spec 부록 B](./StoryTellingSpec.md) 다.** `char/char_woodcutter_idle.png`
  — 폴더에 들어가도 접두사는 남는다. `cutout.py` 가 raw 파일명을 그대로 두기 때문이다.
  `story.json` 이 `char/woodcutter_idle.png` 를 가리키면 그림이 다 있어도 화면이 빈다.
  → `tools/extract_assets.py` 와 `tests/test_assets.py` 가 막는다
- **큐의 `at` 은 어절 글자다** (번호 아님). 그 줄에 없는 어절이면 큐가 안 터진다.
  → 검증 V14
- **edge-tts 의 `boundary` 기본값은 `SentenceBoundary` 다.** `WordBoundary` 로 지정하지
  않으면 어절 타임스탬프가 안 나오고, 그러면 제품의 절반(한글 학습)이 사라진다

**그 밖에**

- **비트를 넘기는 주체는 하나여야 한다** ([Spec §6.4](./StoryTellingSpec.md#64-비트-길이와-오디오는-한-시계를-쓴다)).
  무음이면 타이머, 음성이면 `onend` 로 둘이 넘기게 하면 반드시 어긋난다
- **등장·퇴장은 비트 단위로 누적된다.** 줄 단위로 세면 첫 줄에 나타난 배우가 둘째 줄에서
  사라진다
- **제미나이가 넣는 구석 반짝이는 프롬프트로 못 막는다.** `cutout.py` 가 크기로 거른다
- **후광(glow)은 마젠타와 섞여 분홍 띠가 된다.** `cutout.py` 가 배경에 이어진 분홍빛을
  반투명 + 분홍 제거로 푼다. 컷아웃 결과는 어두운 바탕과 밝은 바탕 **양쪽에** 얹어 보고 판단한다
  → `tests/test_cutout.py`
- **떨어져 있는 부분도 한 에셋이다.** 두 손처럼 안 닿는 blob 을 나누면 `choice_shrug` 가
  쪼개진다. 합친다
- **배경과 캐릭터가 따로 노는 것은 결함이 아니다.** 동화극의 정체성이다. 없애야 할 것은
  배경이 캐릭터보다 정보량이 많아 "캐릭터를 덜 그렸네"로 읽히는 쪽이고,
  그건 `bgTreatment` 로 누른다 ([Spec §5.7](./StoryTellingSpec.md#57-배경-후처리--배경을-한-발-물린다))
- **프록시 환경에서 edge-tts 가 TLS 로 막히면** CA 를 신뢰 목록에 **더한다**
  (`ec._SSL_CTX.load_verify_locations`). 검증을 끄지 않는다 — `tools/tts_gen.py` 참고

---

## 7. 안티그라비티(AGY)로 작업할 때

[style/prompts-antigravity.md](./style/prompts-antigravity.md) 의 **5개 메시지를 순서대로**
보낸다. 첨부하지 않는다 — 참조는 전부 같은 메시지 안에서 먼저 만들어 저장한 파일을
경로로 가리킨다.

①과 ②는 **첫 장(밑그림)이 나머지의 기준**이다. 눈으로 확인하고 넘어간다.
밑그림이 틀리면 뒤따라 나온 것이 전부 틀린다.

저장 경로는 프롬프트의 `Save as:` 에 있다. 그대로 저장되면
`python3 tools/cutout.py` 한 번으로 처리된다.

**로컬 세션에서는 Claude 가 직접 보낸다.** Antigravity 에 `SweetHome` 프로젝트
(이 폴더)가 등록돼 있고, 전역 하네스의 래퍼로 CLI 에 넘긴다 — 메시지 하나(이미지 3장)에 5분쯤.

```powershell
& "$env:USERPROFILE\.gemini\scripts\ag.ps1" -Project SweetHome -PromptFile <메시지.txt> -Json -Timeout 1500s
```

메시지 끝에 "경로는 워크스페이스 기준, 그 경로에 PNG 로 저장, 저장한 경로·크기 보고, 다른 파일은
건드리지 말 것" 을 붙인다. 끝나면 `git status` 로 확인하고 이미지를 직접 본다.
자세한 것(권한 자동 거부, 쿼터 429)은 `~/.gemini/docs/antigravity.md`.
