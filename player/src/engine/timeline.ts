/**
 * 비트 스케줄링 — Spec §6.4 "한 시계".
 *
 * 비트를 넘기는 주체는 하나여야 한다. 프로토타입에서 무음이면 타이머,
 * 음성이면 onend 로 둘이 넘기게 했더니 반드시 어긋났다.
 * 여기서는 `shouldAdvance` 하나만 판단한다.
 */
import type { Beat, Line, WordTiming } from './types'

/** 줄이 끝나야 하는 시각. 오디오가 예상보다 짧아도 자막이 잘리지 않게 durationMs 를 하한으로 둔다. */
export function lineEndMs(line: Line): number {
  const lastWord = line.wordTimings.at(-1)?.[3] ?? 0
  return Math.max(line.durationMs, lastWord)
}

/**
 * 다음 줄로 넘길 때인가.
 * `audioEnded` 는 오디오가 실제로 끝났는지. 오디오가 없거나 실패하면 항상 true 로 준다
 * (Spec §8.3 — 오디오 실패 시에도 진행 가능해야 한다).
 */
export function shouldAdvance(elapsedMs: number, line: Line, audioEnded: boolean): boolean {
  return elapsedMs >= lineEndMs(line) && audioEnded
}

/** 지금 읽고 있는 어절. 아직 시작 전이면 -1. */
export function wordIndexAt(timings: WordTiming[], tMs: number): number {
  let hit = -1
  for (let i = 0; i < timings.length; i++) {
    if (tMs >= timings[i][2]) hit = i
    else break
  }
  return hit
}

/** 그림 한 장의 체류 시간 — 줄들의 합 (Spec §3.3, 12~35초). */
export function beatDurationMs(beat: Beat): number {
  return beat.lines.reduce((sum, l) => sum + lineEndMs(l), 0)
}
