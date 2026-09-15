/**
 * 연출 큐 — 대사의 그 순간에 그 일이 일어난다 (Spec §4.6).
 *
 * §4.5 의 움직임 어휘는 비트 내내 도는 앰비언트다. 큐는 일회성 사건이고,
 * 어절 타임스탬프에 물려 있다 — "빛이 쏟아졌어요" 의 `쏟아졌어요` 가
 * 소리로 나는 그 순간에 빛이 퍼진다.
 *
 * 순수 함수. 언제 무엇을 할지만 계산하고, 실제로 움직이는 것은 렌더러다.
 */
import type { Beat, Cue, CueDo } from './types'

/** 배우 대상 — 어휘는 닫혀 있다. 자유 서술이 아니라 여기서 고른다. */
export const ACTOR_CUES = ['appear', 'vanish', 'lift', 'drop', 'startle', 'shimmer'] as const
/** 화면 전체 */
export const STAGE_CUES = ['brighten', 'darken'] as const
/** 카메라 — §4.5 의 이동을 그 순간 한 번, 그리고 흔들림 */
export const CAMERA_CUES = ['pushIn', 'pullOut', 'panLeft', 'panRight', 'tiltUp', 'shake'] as const

/** 큐마다 길이는 고정이다. 작성자가 정하면 비트마다 톤이 달라진다. */
export const CUE_MS: Record<CueDo, number> = {
  appear: 900, vanish: 900, lift: 800, drop: 700, startle: 600, shimmer: 900,
  brighten: 1100, darken: 1100,
  pushIn: 1400, pullOut: 1400, panLeft: 1400, panRight: 1400, tiltUp: 1400, shake: 500,
}

export function cueKind(d: CueDo): 'actor' | 'stage' | 'camera' {
  if ((ACTOR_CUES as readonly string[]).includes(d)) return 'actor'
  if ((STAGE_CUES as readonly string[]).includes(d)) return 'stage'
  return 'camera'
}

export interface ResolvedCue extends Cue {
  /** 그 줄 안에서 큐가 터지는 시각(ms) */
  startMs: number
  endMs: number
}

/** `at` 이 가리키는 어절의 시작 시각. 못 찾으면 null. */
export function resolveCue(beat: Beat, cue: Cue): ResolvedCue | null {
  const line = beat.lines[cue.line]
  if (!line) return null

  let seen = 0
  const want = cue.nth ?? 1
  for (const [a, b, startMs] of line.wordTimings) {
    if (line.text.slice(a, b).trim().replace(/[.,!?…]+$/u, '') !== cue.at) continue
    seen += 1
    if (seen !== want) continue
    const start = Math.max(0, startMs + (cue.offsetMs ?? 0))
    return { ...cue, startMs: start, endMs: start + CUE_MS[cue.do] }
  }
  return null
}

/** 이 줄의 큐들을, 시간순으로. */
export function cuesForLine(beat: Beat, lineIndex: number): ResolvedCue[] {
  return (beat.cues ?? [])
    .filter((c) => c.line === lineIndex)
    .map((c) => resolveCue(beat, c))
    .filter((c): c is ResolvedCue => c !== null)
    .sort((a, b) => a.startMs - b.startMs)
}

/** 지금 터져 있어야 할 큐들. 렌더러가 매 프레임 묻는다. */
export function activeCues(cues: ResolvedCue[], tMs: number): ResolvedCue[] {
  return cues.filter((c) => tMs >= c.startMs && tMs < c.endMs)
}

/**
 * 지금 누가 보이고 누가 안 보이는가 — **비트 전체**를 기준으로 센다.
 *
 * 줄 단위로 세면 첫 줄에 나타난 배우가 둘째 줄에서 사라진다. 그림책의 한 페이지
 * 안에서 등장과 퇴장은 누적되는 사건이지, 줄마다 초기화되는 것이 아니다.
 *
 * `lineIndex` 이전 줄의 큐는 전부 끝난 것으로 보고, 현재 줄은 `tMs` 까지만 센다.
 */
export function beatState(
  beat: Beat, lineIndex: number, tMs: number,
): Map<string, 'shown' | 'hidden'> {
  const state = new Map<string, 'shown' | 'hidden'>()
  const apply = (c: Cue) => {
    if (c.do === 'appear') state.set(c.target, 'shown')
    if (c.do === 'vanish') state.set(c.target, 'hidden')
  }
  for (const c of beat.cues ?? []) {
    if (c.line < lineIndex) { apply(c); continue }
    if (c.line > lineIndex) continue
    const r = resolveCue(beat, c)
    if (r && tMs >= r.startMs) apply(c)
  }
  return state
}

/**
 * 큐가 등장시키기로 한 배우는 그 순간까지 숨어 있어야 한다.
 * 단, 그 배우가 **이 줄보다 앞선 줄**에서 이미 나타났으면 해당 없다.
 */
export function hiddenAtStart(beat: Beat, lineIndex = 0): Set<string> {
  const out = new Set<string>()
  for (const c of beat.cues ?? []) {
    if (c.do === 'appear' && c.line >= lineIndex) out.add(c.target)
  }
  return out
}
