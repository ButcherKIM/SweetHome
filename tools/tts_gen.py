#!/usr/bin/env python3
"""나레이션 합성 + 어절 타임스탬프 (Pipeline.md §S6).

edge-tts 로 mp3 를 만들고, WordBoundary 로 어절 경계를 받아
story.json 의 durationMs 와 wordTimings 를 **실측값으로 덮어쓴다**.
대본 단계의 추정치는 여기서 폐기된다 (Spec §6.4).

사용: python3 tools/tts_gen.py [--story goldaxe] [--rate -28%] [--only b_intro_01_1]

⚠ edge-tts 는 Microsoft 의 비공식 엔드포인트다. 상용 배포 전 교체해야 하며,
  그래서 이 단계를 독립 스크립트로 격리해 두었다. 교체해도 story.json 포맷은 그대로다.
"""
import argparse, asyncio, json, os, pathlib, sys

import edge_tts
import edge_tts.communicate as ec

# 사내 프록시가 TLS 를 재종료하는 환경에서는 그 CA 도 신뢰해야 한다.
# 검증을 끄는 것이 아니라 신뢰 목록에 더하는 것이다.
for _ca in (os.environ.get("SSL_CERT_FILE"), os.environ.get("REQUESTS_CA_BUNDLE")):
    if _ca and os.path.exists(_ca):
        ec._SSL_CTX.load_verify_locations(_ca)
        break

VOICE   = "ko-KR-SunHiNeural"   # 해설자 1인 (Spec §6.2)
TAIL_MS = 1200                  # 말이 끝나고 그림을 한 박자 더 보여준다
MIN_MS  = 6000                  # Spec §3.3 — 4~7세는 한 화면을 최소 이만큼 본다


def spans(text, words):
    """WordBoundary 의 어절 텍스트를 원문 문자 위치로 되돌린다.

    edge-tts 는 문장부호를 떼고 준다('살았어요.' → '살았어요').
    어절 단위 하이라이트이므로 다음 공백까지 늘려 부호를 포함시킨다.
    """
    out, cur = [], 0
    for w in words:
        i = text.find(w, cur)
        if i < 0:                      # 못 찾으면 그 어절은 건너뛴다
            out.append(None)
            continue
        j = i + len(w)
        while j < len(text) and not text[j].isspace():
            j += 1
        out.append((i, j))
        cur = j
    return out


async def synth(text, out_path, rate):
    c = edge_tts.Communicate(text, VOICE, rate=rate, boundary="WordBoundary")
    audio, marks = bytearray(), []
    async for ch in c.stream():
        if ch["type"] == "audio":
            audio += ch["data"]
        elif ch["type"] == "WordBoundary":
            marks.append((ch["text"], ch["offset"] / 10_000, (ch["offset"] + ch["duration"]) / 10_000))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(audio)

    speech_end = max((m[2] for m in marks), default=0)
    duration = max(MIN_MS, round(speech_end + TAIL_MS))

    timings = []
    for (a, b), (_, t0, t1) in zip(spans(text, [m[0] for m in marks]), marks):
        if (a, b) != (None, None) and a is not None:
            timings.append([a, b, round(t0), round(t1)])
    return duration, timings, len(audio), speech_end


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--story", default="goldaxe")
    ap.add_argument("--rate", default="-28%")
    ap.add_argument("--only")
    args = ap.parse_args()

    root = pathlib.Path(__file__).resolve().parent.parent
    sp = root / "stories" / args.story / "story.json"
    story = json.loads(sp.read_text(encoding="utf-8"))
    adir = sp.parent / "audio"

    # 합성 대상: 모든 줄 + 선택지 질문
    jobs = []
    for node in story["nodes"].values():
        for b in node["beats"]:
            for ln in b["lines"]:
                jobs.append((ln["id"], ln["text"], ln, "line"))
        ch = node.get("choice")
        if ch:
            jobs.append((f"{node['beats'][0]['id']}_choice", ch["promptText"], ch, "choice"))

    if args.only:
        jobs = [j for j in jobs if j[0] == args.only]

    print(f"음성 {VOICE}  ·  속도 {args.rate}  ·  대상 {len(jobs)}개\n")
    total_ms = total_bytes = 0
    for lid, text, holder, kind in jobs:
        dur, tim, nbytes, speech = await synth(text, adir / f"{lid}.mp3", args.rate)
        chars = sum(1 for c in text if not c.isspace())
        if kind == "line":
            holder["audio"] = f"audio/{lid}.mp3"
            holder["durationMs"] = dur
            holder["wordTimings"] = tim
        else:
            holder["promptAudio"] = f"audio/{lid}.mp3"
            holder["promptWordTimings"] = tim
        total_ms += dur
        total_bytes += nbytes
        print(f"  {lid:<18} 말 {speech/1000:>5.1f}s → 비트 {dur/1000:>5.1f}s "
              f"· {speech/chars:>5.0f}ms/자 · 어절 {len(tim):>2}개 · {nbytes/1024:>5.1f}KB")

    sp.write_text(json.dumps(story, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n{sp} 갱신 — 전체 {total_ms/1000:.1f}초 / 오디오 {total_bytes/1024/1024:.2f}MB")
    print("durationMs 와 wordTimings 를 실측값으로 덮어썼다 (Spec §6.4)")


if __name__ == "__main__":
    asyncio.run(main())
