# 프로덕션 파이프라인

> 상태: **Draft v0.1** / 2026-09-12
> [StoryTellingSpec.md](./StoryTellingSpec.md) 의 §5 §7 을 실행 가능한 수준으로 전개한 문서.
> 제작 강도 **T1 (팝업북)** 기준.

---

## 0. 한 장 요약

```
 ┌─ S0 기획 ────────────────────────────────────────────── 사람
 │   원작 → 13노드 트리 · 분기점 설계
 │   ⇣ outline.md
 ├─ S1 스타일 바이블 ───────────────────────────── 사람 + Gemini
 │   팔레트 · 질감 · 등신 · 캐릭터 시트
 │   ⇣ style-bible.md, refs/*.png                         ★ 게이트 1
 ├─ S2 스크립트 생성 ────────────────────────────────── Gemini
 │   노드 → 비트 분할 · 나레이션 · 씬 지시 · 이미지 프롬프트
 │   ⇣ script.json                                        ★ 게이트 2
 ├─ S3 에셋 명세 추출 ─────────────────────────────────── 자동
 │   씬 지시에서 참조된 에셋 유니크 목록 산출
 │   ⇣ asset_manifest.json
 │
 ├───────────────┬─────────────────────────────┐
 │               │                             │
 │  S4 이미지 생성 (Gemini Image API)          │  S8 TTS (GCP)
 │   ⇣ raw/*.png                               │   ⇣ audio/, timings/
 │  S5 컷아웃 (rembg)                          │
 │   ⇣ cut/*.png                               │        │
 │  S6 검수 — 후보 N개 중 택1     ★ 게이트 3   │        │
 │  S7 정규화 (트림·정렬·리사이즈)              │        │
 │   ⇣ assets/, assets.json                    │        │
 └───────────────┬─────────────────────────────┴────────┘
                 ↓
 ┌─ S9 빌드 & 검증 ────────────────────────────────────── 자동
 │   script + assets + timings → story.json  (+ 10종 검증)
 │   ⇣ story.json
 ├─ S10 번들 ──────────────────────────────────────────── 자동
 │   WebP 1x/2x · Opus · manifest
 │   ⇣ dist/{storyId}/
 └─ ▶ 플레이어
```

**병목은 기계가 아니라 사람 게이트 3개다.** (§7 시간 추정 참조)

---

## 1. 설계 원칙

| 원칙 | 의미 |
|---|---|
| **멱등성** | 모든 스크립트는 재실행 안전. 이미 존재하는 산출물은 건너뛴다 |
| **콘텐츠 해시 캐시** | 에셋 ID + 프롬프트 해시가 같으면 재생성하지 않는다 (S4가 가장 비싸다) |
| **부분 실행** | `--only <id>` 로 에셋/비트 하나만 다시 돌린다 |
| **게이트는 명시적** | 사람 승인 없이 다음 단계로 흐르지 않는다 |
| **검증은 빌드 타임** | 런타임에 깨지면 아이가 본다. S9에서 전부 잡는다 |
| **되먹임은 2개뿐** | 에셋 리젝(S6→S4), 오디오 길이(S8→S2). 그 외 단방향 |

---

## 2. 디렉터리 & 데이터 흐름

```
stories/heungbu/
├── outline.md              S0   사람이 쓴다
├── script.json             S2   Gemini 생성 → 사람 검수
├── asset_manifest.json     S3   자동 추출
├── raw/                    S4   생성 원본 (에셋당 후보 N개)
│   └── char_heungbu_happy_{0..3}.png
├── cut/                    S5   컷아웃 (캐릭터·소품만)
│   └── char_heungbu_happy_{0..3}.png
├── assets/                 S6·S7 확정 + 정규화 ← 여기부터가 "진짜" 에셋
│   ├── bg/  char/  prop/  icon/
│   └── assets.json         S7   자동 생성
├── audio/                  S8   b_intro_03.opus
├── timings/                S8   b_intro_03.json
└── story.json              S9   ★ 최종 산출물

dist/heungbu/               S10  배포 번들
style/
├── style-bible.md          S1
└── refs/                   S1   캐릭터 시트 (전 생성의 레퍼런스)
```

**`raw/` → `cut/` → `assets/` 3단 분리 이유:** 검수에서 리젝했을 때
어느 단계로 되돌아갈지가 명확해진다. 프롬프트 문제면 S4, 컷아웃 실패면 S5.

---

## 3. 스테이지 상세

### S0 — 기획 `사람`

| | |
|---|---|
| 입력 | 원작 텍스트 (public domain) |
| 출력 | `outline.md` |
| 도구 | 사람 + Claude/Gemini 대화 |

**산출 내용**
- 13개 노드의 1~2문장 요약
- 분기점 2개의 위치와 3지선다 내용
- 9개 결말 각각의 제목 + 교훈 + 원작 여부
- 등장인물 목록, 장소 목록 (에셋 물량의 1차 추정치)

**체크**: 결말 9개가 전부 [Spec §3.4 톤 정책](./StoryTellingSpec.md#34-결말-정책)을 통과하는가.
여기서 걸러야 S2 재작업이 없다.

---

### S1 — 스타일 바이블 `사람 + Gemini` ★게이트 1

| | |
|---|---|
| 입력 | `outline.md` |
| 출력 | `style/style-bible.md`, `style/refs/char_{name}_sheet.png` |

**style-bible.md 에 고정할 것**

```markdown
## 스타일 토큰 (모든 이미지 프롬프트에 주입)
traditional Korean hanji watercolor illustration, soft ink outlines,
muted mid-saturation palette, children's picture book, flat lighting

## 팔레트
주조: #E8D5B7 #C4956A #8B5A3C #6B8E6B #4A6741
보조: ...
강조: #D96C4F #F2C14E

## 캐릭터 규격
2.5~3등신 / 눈 크게 / 손발 단순화 / 외곽선 3px 상당

## 배경 규격
원근 얕게, 지평선 화면 하단 1/3, 인물 없음
```

**캐릭터 시트**는 인물당 1장. 정면/측면 + 기본 표정. **이후 모든 생성의 레퍼런스로 물린다.**

> ⚠️ **이 게이트를 통과하기 전에 S4를 돌리지 마라.** 스타일이 바뀌면 에셋 전량 재생성이다.

---

### S2 — 스크립트 생성 `Gemini` ★게이트 2

```bash
python -m pipeline.script_gen --story heungbu
```

| | |
|---|---|
| 입력 | `outline.md`, `style-bible.md`, `schema/story.schema.json` |
| 출력 | `script.json` |
| 모델 | Gemini (구조화 출력 / JSON 모드) |

**노드 단위로 호출한다** (13회). 한 번에 전체를 요청하면 후반 노드 품질이 떨어진다.

**프롬프트에 반드시 포함**
1. 스키마 발췌 — 특히 [§4.5 움직임 어휘 enum](./StoryTellingSpec.md#45-움직임-어휘--폐쇄형-집합-6544)
   → **자유 서술이 아니라 enum에서 고르게 한다.** 출력 안정성의 핵심
2. 톤 정책 (배드엔딩 금지, 교훈 1문장)
3. 비트 길이 규칙 (8~15초 ≈ 한국어 35~70자)
4. 이미 확정된 에셋 ID 목록 → **재사용 유도**
   ("가능하면 아래 배경 중에서 고르고, 꼭 필요할 때만 새로 요청")

**노드당 출력**
```jsonc
{
  "nodeId": "n_intro",
  "beats": [
    { "id": "b_intro_03",
      "text": "흥부는 다친 제비를 조심조심 안아 들었어요.",
      "scene": { "background": "bg_village_day", "camera": "pushIn",
                 "actors": [...], "fx": "petals", "transitionIn": "pageTurn" },
      "newAssets": [                       // 기존에 없는 것만
        { "id": "char_heungbu_happy", "kind": "character",
          "prompt": "웃으며 두 손으로 작은 새를 감싸 안은 자세" }
      ]}
  ],
  "choice": { ... }
}
```

**게이트 2 — 사람 검수 항목**
- [ ] 톤 정책 위반 없음
- [ ] 선택지 3개의 도덕적 우열이 드러나지 않음
- [ ] 선택지 label 12자 이내, 구체적 동사
- [ ] 비트 텍스트가 5~8세 어휘
- [ ] 신규 에셋 요청이 과하지 않음 (재사용률 확인)

---

### S3 — 에셋 명세 추출 `자동`

```bash
python -m pipeline.extract_assets --story heungbu
```

| | |
|---|---|
| 입력 | `script.json` |
| 출력 | `asset_manifest.json` |

씬 지시가 참조하는 모든 에셋 ID를 **유니크하게** 모으고, `newAssets`의 프롬프트를 결합한다.

```jsonc
{
  "summary": { "total": 23, "backgrounds": 6, "characters": 9, "props": 6, "icons": 3,
               "referencedBy": { "char_heungbu_idle": 11 } },   // 재사용 횟수
  "assets": [
    { "id": "char_heungbu_happy", "kind": "character",
      "ref": "style/refs/char_heungbu_sheet.png",
      "prompt": "웃으며 두 손으로 작은 새를 감싸 안은 자세",
      "promptHash": "a3f9…" }
  ]
}
```

**이 단계가 있는 이유**
- 에셋 누락이 빌드 타임이 아니라 **여기서** 잡힌다
- 재사용 횟수가 보인다 → 1회만 쓰이는 에셋은 기존 것으로 대체 검토
- `promptHash` 가 S4의 캐시 키가 된다

---

### S4 — 이미지 생성 `Gemini Image API`

```bash
python -m pipeline.image_gen --story heungbu [--only char_heungbu_happy] [--candidates 4]
```

| | |
|---|---|
| 입력 | `asset_manifest.json`, `style-bible.md`, `refs/*.png` |
| 출력 | `raw/{assetId}_{0..N-1}.png` |
| 기본 후보 수 | 4 |

**프롬프트 조립**

```
[스타일 토큰]  ← style-bible.md 에서 그대로
[피사체 프롬프트]  ← manifest
[종류별 규칙]      ← 아래
```

| 종류 | 종류별 규칙 (실무 함정) |
|---|---|
| **캐릭터** | `full body, standing on nothing, isolated on flat magenta #FF00FF background,` **`no shadow, no ground, no cast shadow`** |
| **소품** | 동일 + `single object, centered` |
| **배경** | `wide establishing shot,` **`no people, no characters, no animals`** `, aspect 21:9` |
| **아이콘** | `simple flat icon, single subject, magenta background` |

> ⚠️ **`no shadow, no ground` 를 빠뜨리면** 컷아웃 후 캐릭터 발밑에 회색 얼룩이 남는다.
> ⚠️ **배경에 `no people` 을 빠뜨리면** 배경에 그려진 사람과 컷아웃 캐릭터가 겹쳐 나온다.
> ⚠️ **배경은 21:9로 생성**한다 (16:9의 1.3배). 카메라 팬 여유분.

**레퍼런스 이미지**: 캐릭터/소품은 해당 캐릭터 시트를 물린다. 배경은 이전에 확정된
같은 장소 배경이 있으면 그것을 물린다 (시간대 변형의 일관성).

**구현 요구**
- 레이트 리밋 백오프 (2s→4s→8s→16s)
- `promptHash` 캐시 — 이미 있으면 건너뜀
- 실패 로그를 `raw/_failed.json` 에 남기고 계속 진행 (중단하지 않음)

---

### S5 — 컷아웃 `rembg / BiRefNet`

```bash
python -m pipeline.cutout --story heungbu
```

| | |
|---|---|
| 입력 | `raw/` 중 **캐릭터·소품·아이콘만** |
| 출력 | `cut/{assetId}_{n}.png` (RGBA) |
| 배경 | **스킵** — 통짜로 쓴다 |

**처리**
1. 마젠타 키 1차 제거 (색상 거리 임계) — 깔끔한 경우 이것만으로 끝
2. rembg/BiRefNet 2차 — 1차가 불완전한 경우
3. 알파 가장자리 1px 디스페클 (마젠타 프린지 제거)

> 마젠타를 쓰는 이유: 살색·초록·하늘색과 색상 거리가 가장 먼 색이라 오탐이 적다.

---

### S6 — 검수 `사람` ★게이트 3

```bash
python -m pipeline.review --story heungbu     # 로컬 웹 UI (localhost:5174)
```

에셋별로 후보 N개를 격자로 띄우고 클릭 한 번으로 확정. 확정본이 `assets/` 로 복사된다.

| 판정 | 처리 |
|---|---|
| 채택 | `assets/{kind}/{assetId}.png` |
| 프롬프트 문제 | 프롬프트 수정 → S4 `--only` 재실행 |
| 컷아웃 실패 | S5만 재실행 |
| 전부 부적합 | `--candidates 8` 로 S4 재실행 |

**검수 기준**
- [ ] 캐릭터 시트와 **같은 인물로 보이는가** ← 가장 중요
- [ ] 스타일 바이블 준수 (팔레트, 선, 등신)
- [ ] 알파 가장자리 깨끗한가 (프린지·잘린 손발 없음)
- [ ] 배경: 인물이 들어가 있지 않은가, 21:9인가

---

### S7 — 정규화 `자동`

```bash
python -m pipeline.normalize --story heungbu
```

| | |
|---|---|
| 입력 | `assets/` 확정본 |
| 출력 | 정규화된 `assets/` + `assets.json` |

1. **트림** — 투명 여백 제거
2. **기준점 정렬** — 캐릭터/소품은 **하단 중앙**이 원점 (`story.json` 의 `y` 가 발 닿는 지점)
3. **리사이즈** — 마스터 2x (캐릭터 전신 높이 ≈ 1400px @2x)
4. **배경 검증** — 종횡비 21:9 ±2% 확인, 아니면 경고
5. `assets.json` 자동 생성 ([Spec §4.2](./StoryTellingSpec.md#42-에셋-선언) 형식)

---

### S8 — TTS `GCP Cloud TTS`

```bash
python -m pipeline.tts_gen --story heungbu [--only b_intro_03]
```

| | |
|---|---|
| 입력 | `script.json` 의 `text`, `choice.promptText` |
| 출력 | `audio/{beatId}.opus`, `timings/{beatId}.json` |

**처리**
1. 텍스트를 SSML로 변환, 어절마다 `<mark name="w{i}"/>` 삽입
2. `enableTimePointing: SSML_MARK` 으로 합성 → 타임포인트 수신
3. 타임포인트 → `wordTimings: [[문자시작, 문자끝, 시작ms, 끝ms], ...]`
4. 실제 `durationMs` 측정
5. Opus 인코딩 (LINEAR16 → libopus 48kbps mono)

**되먹임 — 길이 규칙 위반 리포트**

```
⚠ b_intro_03: 21.4s (상한 20s 초과) → 비트 분할 필요
⚠ b_end5_02:   4.1s (하한 8s 미만) → 앞 비트와 병합 검토
```

이 리포트를 들고 S2로 돌아가 해당 비트만 다시 쓴다. **파이프라인의 두 되먹임 루프 중 하나.**

**Gemini TTS를 쓰는 경우**: 타임스탬프가 없으므로 `whisperx` 강제정렬 단계를 S8.5로 추가.
GPU 없이 CPU로도 가능하지만 느리고 한국어 어절 경계 정확도가 떨어진다. GCP 권장 이유.

---

### S9 — 빌드 & 검증 `자동`

```bash
python -m pipeline.build_story --story heungbu
```

| | |
|---|---|
| 입력 | `script.json` + `assets.json` + `timings/` |
| 출력 | `story.json` |

**검증 10종 — 하나라도 실패하면 빌드 실패**

| # | 검증 | 잡는 사고 |
|---|---|---|
| V1 | JSON Schema 준수 | 구조 오류 |
| V2 | 참조 무결성 — 모든 `background`/`actors.asset` 이 `assets` 에 존재 | 검은 화면 |
| V3 | 파일 실재 — 선언된 경로에 파일이 있는가 | 404 |
| V4 | 트리 무결성 — 모든 `next` 가 유효, 도달 불가 노드 없음, 순환 없음 | 막다른 길 |
| V5 | 결말 수 — `type:"ending"` 이 정확히 9개(v0는 3개), `isCanonical` 정확히 1개 | 원작 엔딩 누락 |
| V6 | enum 유효성 — `camera`/`anim`/`enter`/`transitionIn`/`fx` 가 어휘 집합 내 | 렌더러 무반응 |
| V7 | 길이 규칙 — `durationMs` 8000~20000 (경고), 오디오 실측과 ±100ms 일치 | 자막 밀림 |
| V8 | 타임스탬프 정합 — `wordTimings` 끝 ≤ `durationMs`, 인덱스가 `text` 범위 내 | 하이라이트 깨짐 |
| V9 | 텍스트 규칙 — 선택지 `label` ≤ 12자, `lesson` 1문장 | UI 넘침 |
| V10 | 좌표 범위 — `x`,`y` ∈ [0,1], `z` 충돌 없음 | 화면 밖 캐릭터 |

> V4·V5 는 분기형 콘텐츠의 고유 위험이다. 트리가 13노드로 커지면 사람 눈으로 못 잡는다.

**CI**: `stories/**/story.json` 변경 시 V1~V10 자동 실행.

---

### S10 — 번들 `자동`

```bash
python -m pipeline.build_bundle --story heungbu
```

| 자산 | 처리 | 목표 |
|---|---|---|
| 이미지 | WebP q82, 1x/2x 2벌 | |
| 오디오 | Opus 48kbps mono | |
| story.json | minify | |
| **합계** | | **30MB 이하 / 편** |

`dist/heungbu/manifest.json` 에 선행 로드 순서를 기록한다
(현재 비트 + 다음 비트 + 선택지 3갈래의 첫 비트).

---

## 4. 오케스트레이션

```bash
# 전체 (게이트에서 멈춤)
python -m pipeline.run --story heungbu

# 구간 실행
python -m pipeline.run --story heungbu --from S4 --to S7

# 에셋 하나만 되돌리기
python -m pipeline.image_gen --story heungbu --only char_heungbu_happy --candidates 8
python -m pipeline.cutout    --story heungbu --only char_heungbu_happy
python -m pipeline.review    --story heungbu --only char_heungbu_happy
python -m pipeline.run       --story heungbu --from S7
```

게이트 도달 시 동작:
```
★ 게이트 3 (에셋 검수) — 23개 중 18개 확정, 5개 미검수
  → python -m pipeline.review --story heungbu
중단.
```

---

## 5. 되먹임 루프 (2개만 존재)

```
 ┌─── L1: 에셋 리젝 ────────────────────┐
 │  S6 검수 → 프롬프트 수정 → S4 재생성   │   가장 자주 도는 루프
 └───────────────────────────────────────┘

 ┌─── L2: 오디오 길이 ──────────────────┐
 │  S8 길이 리포트 → S2 비트 재작성       │   1~2회면 수렴
 └───────────────────────────────────────┘
```

**그 외는 전부 단방향이다.** 루프가 3개 이상 생기면 파이프라인이 아니라 늪이 된다.
스타일 바이블(게이트 1)이 되먹임 루프가 되지 않도록 **S1에서 확실히 끝내는 것**이 핵심.

---

## 6. 실패 모드 대응표

| 증상 | 원인 | 대응 |
|---|---|---|
| 컷아웃 발밑에 회색 얼룩 | 프롬프트에 `no shadow` 누락 | S4 프롬프트 수정 |
| 캐릭터 외곽에 마젠타 테두리 | 디스페클 미적용 | S5 후처리 강화 |
| 배경에 사람이 그려져 있음 | `no people` 누락 | S4 재생성 |
| 같은 캐릭터가 달라 보임 | 레퍼런스 미주입 / 시트 품질 | S1 시트 재작업 → S4 전량 |
| 배경 팬 시 가장자리 노출 | 21:9 미준수 | S7 V-check → S4 재생성 |
| 자막이 음성보다 빠름/느림 | 타임스탬프 스케일 오류 | V8 확인, S8 재실행 |
| 특정 결말에 도달 불가 | `choice.next` 오타 | V4가 빌드에서 차단 |
| 비트가 20초 초과 | 스크립트 과다 | L2 루프 |
| 이미지 생성 429 | 레이트 리밋 | 백오프 후 자동 재개 |

---

## 7. 시간 · 비용 추정 (데모 = 에셋 23개 / 비트 15개)

| 스테이지 | 기계 시간 | 사람 시간 | 비용 |
|---|---|---|---|
| S0 기획 | — | **3~5h** | — |
| S1 스타일 바이블 | 20m | **4~8h** | 생성 ~50회 |
| S2 스크립트 | 10m | **1~2h** (검수) | 텍스트 토큰, 무시 가능 |
| S3 명세 추출 | 즉시 | — | — |
| S4 이미지 생성 | 15~30m | — | 23×4 = **92회** + 재시도 |
| S5 컷아웃 | 5m | — | — |
| S6 검수 | — | **1~2h** | — |
| S7 정규화 | 2m | — | — |
| S8 TTS | 5m | — | ~2,000자 |
| S9 빌드 | 즉시 | — | — |
| S10 번들 | 2m | — | — |
| **합계** | **~1h** | **9~17h** | 생성 150~250회 |

**결론: 기계는 1시간, 사람은 이틀.**
비용 최적화는 의미가 없고, **게이트 1(스타일 바이블)에 집중하는 것**이 유일한 레버다.
여기가 흔들리면 S4~S7 전체가 반복된다.

**v1 전체(에셋 45개 / 비트 70개) 확장 시**
- S1 은 **재실행하지 않는다** (0h) ← 분리 생성의 가장 큰 보상
- S4 는 추가분 22개만 = 88회
- S2·S8 은 비트 수에 비례 (약 4.7배)
- 사람 시간 증가분은 주로 S2 검수와 S6 검수

---

## 8. 구현 순서

파이프라인 전체를 한 번에 짜지 않는다. **S9(빌드·검증)와 플레이어를 먼저** 만든다.
그래야 만든 에셋을 눈으로 확인할 수 있다.

| 순서 | 대상 | 이유 |
|---|---|---|
| 1 | `schema/story.schema.json` + 손으로 쓴 `story.json` 1개 | 모든 것의 계약 |
| 2 | 플레이어 (더미 도형 에셋) | 움직임 어휘 확정 |
| 3 | S9 `build_story.py` + V1~V10 | 검증 없이 만든 콘텐츠는 못 믿는다 |
| 4 | S4·S5·S7 (캐릭터 **1명**만 관통) | [Spec §9.3 질문 #3](./StoryTellingSpec.md#93-데모가-답해야-할-질문) 검증 |
| 5 | S6 검수 UI | 4번에서 손으로 하다가 지치면 |
| 6 | S8 TTS | |
| 7 | S2·S3 | 마지막. 그때쯤 스키마가 안정돼 있다 |
| 8 | S10 번들 | 배포 직전 |

> **S2(스크립트 생성 자동화)를 마지막에 두는 이유:** 데모 1편 분량(15비트)은 손으로 써도
> 된다. 스키마가 흔들리는 동안 생성 프롬프트를 다듬는 것은 낭비다.
