/**
 * story.json 타입 — schema/story.schema.json 0.5 와 1:1.
 *
 * 이 폴더(engine/)에는 DOM·CSS·브라우저 API 가 들어오지 않는다.
 * Spec §8.5 — 제품화(React Native) 때 다시 쓰는 것은 렌더러뿐이어야 한다.
 */

export type Camera = 'still' | 'pushIn' | 'pullOut' | 'panLeft' | 'panRight' | 'tiltUp'
export type Anim = 'none' | 'breathe' | 'sway' | 'bob' | 'driftIn' | 'pulse'
export type Enter = 'none' | 'fadeIn' | 'popIn' | 'slideIn'
export type Transition = 'crossfade' | 'pageTurn' | 'wipe' | 'cut'
export type Fx = 'none' | 'petals' | 'snow' | 'fireflies' | 'sparkle' | 'rain' | 'dust'
export type Blend = 'normal' | 'screen'

/** [문자시작, 문자끝, 시작ms, 끝ms] — 어절 단위 (D14) */
export type WordTiming = [number, number, number, number]

export interface BgTreatment {
  blurPx?: number
  brightness?: number
  saturate?: number
}

export interface Actor {
  asset: string
  pose?: string
  x: number
  y: number
  scale?: number
  z?: number
  flip?: boolean
  anim?: Anim
  enter?: Enter
  blend?: Blend
}

export interface Scene {
  background: string
  camera?: Camera
  transitionIn?: Transition
  fx?: Fx
  actors?: Actor[]
  bgTreatment?: BgTreatment
}

export interface Line {
  id: string
  text: string
  audio?: string
  durationMs: number
  wordTimings: WordTiming[]
}

export interface Beat {
  id: string
  scene: Scene
  lines: Line[]
}

export interface ChoiceOption {
  id: string
  label: string
  image?: string
  tint?: string
  next: string
  /** 선택지를 순서대로 읽어준다 (Spec §3.5). 없으면 조용히 건너뛴다. */
  audio?: string
  wordTimings?: WordTiming[]
}

export interface Choice {
  promptText: string
  promptAudio?: string
  promptWordTimings?: WordTiming[]
  options: ChoiceOption[]
}

export interface StoryNode {
  type: 'narrative' | 'ending'
  beats: Beat[]
  choice?: Choice
  isCanonical?: boolean
  endingTitle?: string
  lesson?: string
}

export interface AssetRef { src: string; tint?: string; blend?: Blend }
export interface CharacterAsset {
  displayName?: string
  tint?: string
  poses: Record<string, string>
}

export interface Story {
  schemaVersion: string
  storyId: string
  title: string
  source?: string
  locale?: string
  targetAge?: [number, number]
  styleId?: string
  stage: { width: number; height: number; safeArea: number; bgTreatment?: BgTreatment }
  rootNode: string
  canonicalEnding?: string
  subtitle?: {
    defaultOn?: boolean
    highlightUnit?: string
    minFontPx?: number
    wordSpacingEm?: number
    maxLines?: number
  }
  assets: {
    backgrounds: Record<string, AssetRef>
    characters: Record<string, CharacterAsset>
    props?: Record<string, AssetRef>
    icons?: Record<string, AssetRef>
  }
  nodes: Record<string, StoryNode>
}
