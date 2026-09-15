/**
 * 저장 어댑터. engine 은 localStorage 를 모른다 —
 * 웹은 localStorage, React Native 는 AsyncStorage 를 넣어주면 된다 (Spec §8.5).
 */
export interface Storage {
  get(key: string): string | null
  set(key: string, value: string): void
}

/** 저장소가 없거나 막힌 환경(사생활 보호 모드 등)에서도 앱은 돌아야 한다. */
export const memoryStorage = (): Storage => {
  const m = new Map<string, string>()
  return { get: (k) => m.get(k) ?? null, set: (k, v) => void m.set(k, v) }
}

export interface Progress {
  seenEndings: string[]
  subtitlesOn: boolean
  syncOffsetMs: number
}

const KEY = 'sweethome.progress'
const DEFAULTS: Progress = { seenEndings: [], subtitlesOn: true, syncOffsetMs: 0 }

export function loadProgress(storage: Storage): Progress {
  try {
    const raw = storage.get(KEY)
    if (!raw) return { ...DEFAULTS }
    return { ...DEFAULTS, ...(JSON.parse(raw) as Partial<Progress>) }
  } catch {
    return { ...DEFAULTS }
  }
}

export function saveProgress(storage: Storage, p: Progress): void {
  try {
    storage.set(KEY, JSON.stringify(p))
  } catch {
    /* 저장 실패는 진행을 막지 않는다 */
  }
}
