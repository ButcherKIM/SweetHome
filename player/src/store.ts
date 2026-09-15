import { create } from 'zustand'
import {
  back, choose, endingNodes, loadProgress, next, nodeOf, restart, saveProgress, start,
  type PlayState, type Progress, type Story, type Storage,
} from './engine'

export type Screen = 'loading' | 'title' | 'play' | 'error'

interface AppState extends Progress {
  story: Story | null
  play: PlayState | null
  screen: Screen
  error: string | null
  settingsOpen: boolean
  /** 선택 확정 연출 중인 선택지. 있으면 입력을 막는다. */
  picking: string | null

  boot: (story: Story) => void
  fail: (msg: string) => void
  begin: () => void
  advance: () => void
  goBack: () => void
  pick: (optionId: string) => void
  commitPick: () => void
  again: () => void
  toggleSubtitles: () => void
  setSyncOffset: (ms: number) => void
  setSettings: (open: boolean) => void
}

let storage: Storage
export function attachStorage(s: Storage) { storage = s }

const persist = (s: AppState) =>
  saveProgress(storage, {
    seenEndings: s.seenEndings,
    subtitlesOn: s.subtitlesOn,
    syncOffsetMs: s.syncOffsetMs,
  })

export const useApp = create<AppState>((set, get) => ({
  story: null,
  play: null,
  screen: 'loading',
  error: null,
  settingsOpen: false,
  picking: null,
  seenEndings: [],
  subtitlesOn: true,
  syncOffsetMs: 0,

  boot: (story) => {
    const p = loadProgress(storage)
    set({
      story,
      screen: 'title',
      seenEndings: p.seenEndings,
      subtitlesOn: story.subtitle?.defaultOn === false ? p.subtitlesOn : p.subtitlesOn,
      syncOffsetMs: p.syncOffsetMs,
    })
  },

  fail: (msg) => set({ screen: 'error', error: msg }),

  begin: () => {
    const { story } = get()
    if (story) set({ play: start(story), screen: 'play' })
  },

  advance: () => {
    const { story, play, picking } = get()
    if (!story || !play || picking) return
    const after = next(story, play)
    if (after.phase === 'ending' && play.phase !== 'ending') {
      const seen = get().seenEndings.includes(after.nodeId)
        ? get().seenEndings
        : [...get().seenEndings, after.nodeId]
      set({ play: after, seenEndings: seen })
      persist(get())
      return
    }
    set({ play: after })
  },

  goBack: () => {
    const { story, play } = get()
    if (story && play) set({ play: back(story, play), settingsOpen: false })
  },

  pick: (optionId) => set({ picking: optionId }),

  commitPick: () => {
    const { story, play, picking } = get()
    if (!story || !play || !picking) return
    set({ play: choose(story, play, picking), picking: null })
  },

  again: () => {
    const { story } = get()
    if (story) set({ play: restart(story), screen: 'play', settingsOpen: false, picking: null })
  },

  toggleSubtitles: () => {
    set({ subtitlesOn: !get().subtitlesOn })
    persist(get())
  },

  setSyncOffset: (ms) => {
    set({ syncOffsetMs: ms })
    persist(get())
  },

  setSettings: (open) => set({ settingsOpen: open }),
}))

/** 표지에 쓸 "본 엔딩 n / 전체 m". */
export function endingProgress(story: Story, seen: string[]) {
  const all = endingNodes(story)
  return { seen: all.filter((id) => seen.includes(id)).length, total: all.length }
}

export { nodeOf }
