/**
 * 자막 싱크 자동 보정 — Spec §6.5.
 *
 * `HTMLMediaElement.currentTime` 은 디코더 위치다. 스피커에 닿는 소리는 출력 버퍼만큼
 * 늦으므로, 타임스탬프에 정확히 맞춘 하이라이트는 귀보다 앞선다.
 *
 * Spec §6.5 의 예시는 `createMediaElementSource` 로 엘리먼트를 오디오 그래프에 물린다.
 * 여기서는 물리지 않는다 — `outputLatency` 는 출력 장치의 속성이라 빈 컨텍스트에서도
 * 읽히고, 물리다 실패하면 §6.5 가 경고한 대로 **소리가 아예 안 나기** 때문이다.
 */

export interface Latency {
  ms: number
  /** 어디서 나온 값인지 — 설정 화면에 보여준다. */
  source: 'outputLatency' | 'baseLatency' | 'default'
}

const FALLBACK_MS = 150 // 모바일 브라우저 실측 대역 (§6.5)

let ctx: AudioContext | null = null

function context(): AudioContext | null {
  if (ctx) return ctx
  try {
    const Ctor = window.AudioContext ?? (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext
    if (!Ctor) return null
    ctx = new Ctor()
    return ctx
  } catch {
    return null
  }
}

/** 사용자 제스처 뒤에 불러야 한다 (Spec §6.6). */
export async function unlockAudio(): Promise<void> {
  const c = context()
  if (c && c.state === 'suspended') {
    try {
      await c.resume()
    } catch {
      /* 잠금 해제 실패해도 <audio> 재생은 시도한다 */
    }
  }
}

export function measureLatency(): Latency {
  const c = context()
  if (c) {
    if (typeof c.outputLatency === 'number' && c.outputLatency > 0)
      return { ms: Math.round(c.outputLatency * 1000), source: 'outputLatency' }
    if (typeof c.baseLatency === 'number' && c.baseLatency > 0)
      return { ms: Math.round(c.baseLatency * 1000), source: 'baseLatency' }
  }
  return { ms: FALLBACK_MS, source: 'default' }
}
