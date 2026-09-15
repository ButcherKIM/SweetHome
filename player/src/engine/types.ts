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

/** 연출 큐가 가리킬 수 있는 동작 — 닫힌 집합 (Spec §4.6) */
export type CueDo =
  | 'appear' | 'vanish' | 'lift' | 'drop' | 'startle' | 'shimmer'   // 배우
  | 'brighten' | 'darken'                                           // 화면
  | 'pushIn' | 'pullOut' | 'panLeft' | 'panRight' | 'tiltUp' | 'shake' // 카메라

export interface Cue {
  /** 이 비트의 몇 번째 줄인가 */
  line: number
  /** 그 줄의 이 **어절**이 소리로 나기 시작할 때 터진다 */
  at: string
  /** 같은 어절이 한 줄에 여러 번 나오면 몇 번째인가 (기본 1) */
  nth?: number
  /** 미세 조정 (-1000~1000ms) */
  offsetMs?: number
  /** 배우 `id`, 또는 `camera` · `stage` */
  target: string
  do: CueDo
}

export interface Actor {
  /** 큐가 가리키는 이름. 큐를 쓰는 배우에게는 필수. */
  id?: string
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
  /** 연출 큐 (Spec §4.6). 없으면 §4.5 앰비언트만 돈다. */
  cues?: Cue[]
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
