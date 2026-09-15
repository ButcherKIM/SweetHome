# player — 금도끼 은도끼 플레이어

`story.json` 을 재생하는 앱. 이야기·그림·소리는 여기 없다 —
`stories/` 에 있고 파이프라인이 만든다 ([Pipeline.md](../Pipeline.md)).

```bash
cd player
npm install
npm run dev        # http://localhost:5173
npm run build      # dist/ — stories/ 를 함께 복사한다
```

## 왜 이렇게 갈라 놨나

`D16` 은 **데모까지 웹, 제품화에서 React Native** 다 ([Spec §8.5](../StoryTellingSpec.md#85-플랫폼-2단-경로--d16-확정)).
그때 다시 쓰는 것이 렌더러뿐이려면 경계가 실제 파일 경계여야 한다.

```
src/
  engine/     순수 TS. DOM·CSS·브라우저 API 금지 — RN 으로 그대로 간다
    types     story.json 타입 (schema 0.5 와 1:1)
    play      트리 진행 · 선택 · 되돌리기
    timeline  한 시계 (§6.4) · 어절 위치
    assets    경로 해석 · 선행 로드 목록
    storage   저장 어댑터 (localStorage 를 모른다)
  renderer/   웹 전용. RN 에서 다시 쓴다
  audio/      나레이션 · 덕킹 · 출력 지연 보정 (§6.5)
  platform/   engine 을 브라우저에 붙이는 얇은 층
```

**이 규칙은 CI 가 지킨다** — `tests/test_engine_is_pure.py` 가 `engine/` 에
브라우저가 들어왔는지 본다. 규칙은 지켜지지 않으면 규칙이 아니다.

## 아직 없는 것

- **그림** — `stories/goldaxe/assets/` 가 비어 있다. 지금은 `tint` 색면으로 자리만 잡는다
- **BGM · SFX** — CC0 음원이 없다. `AudioBus` 에 자리와 덕킹은 있고 파일만 비었다
