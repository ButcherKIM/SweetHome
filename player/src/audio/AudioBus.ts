/**
 * 나레이션 + BGM 덕킹 + SFX — Spec §6.2, §8.2.
 *
 * BGM·SFX 음원(CC0)은 아직 없다. 인터페이스만 세워두고 파일이 없으면 조용히 넘어간다 —
 * 음원이 들어오면 `setBgmSources` / `setSfxSources` 로 붙이면 된다.
 */

const DUCK_DB = -18
const dbToGain = (db: number) => Math.pow(10, db / 20)

export type BgmKind = 'calm' | 'tense' | 'warm'

export class AudioBus {
  private narration = new Audio()
  private bgm = new Audio()
  private cache = new Map<string, HTMLAudioElement>()
  private bgmSources: Partial<Record<BgmKind, string>> = {}
  private sfxSources: Record<string, string> = {}
  private bgmVolume = 0.5

  constructor(private base: string) {
    this.narration.preload = 'auto'
    this.bgm.loop = true
    this.bgm.volume = 0
  }

  private url(path: string): string {
    return `${this.base}/${path}`
  }

  setBgmSources(s: Partial<Record<BgmKind, string>>) { this.bgmSources = s }
  setSfxSources(s: Record<string, string>) { this.sfxSources = s }

  /** 받아둘 파일. 실패는 무시한다 — 없는 에셋이 진행을 막으면 안 된다. */
  preload(paths: string[]) {
    for (const p of paths) {
      if (!p.endsWith('.mp3') && !p.endsWith('.opus')) continue
      if (this.cache.has(p)) continue
      const el = new Audio(this.url(p))
      el.preload = 'auto'
      this.cache.set(p, el)
    }
  }

  /**
   * 한 줄을 읽는다. 오디오가 없거나 실패하면 즉시 resolve 해서
   * 무음으로도 진행되게 한다 (Spec §8.3).
   */
  playLine(path: string | undefined, onEnded: () => void): HTMLAudioElement | null {
    this.stopLine()
    if (!path) { onEnded(); return null }

    const el = this.narration
    el.src = this.url(path)
    el.currentTime = 0
    el.onended = onEnded
    el.onerror = onEnded
    this.duck(true)
    void el.play().catch(onEnded)
    return el
  }

  stopLine() {
    this.narration.onended = null
    this.narration.onerror = null
    this.narration.pause()
    this.duck(false)
  }

  /** 지금 소리가 나고 있는 위치(ms). 자막 하이라이트가 이걸 따라간다. */
  get positionMs(): number {
    return this.narration.currentTime * 1000
  }

  get rate(): number { return this.narration.playbackRate }
  set rate(v: number) { this.narration.playbackRate = v; this.bgm.playbackRate = 1 }

  playBgm(kind: BgmKind) {
    const src = this.bgmSources[kind]
    if (!src) { this.bgm.pause(); return } // 음원 없음 — 조용히 넘어간다
    if (this.bgm.src !== this.url(src)) {
      this.bgm.src = this.url(src)
      void this.bgm.play().catch(() => {})
    }
    this.duck(!this.narration.paused)
  }

  stopBgm() { this.bgm.pause() }

  sfx(name: string) {
    const src = this.sfxSources[name]
    if (!src) return
    const el = new Audio(this.url(src))
    el.volume = 0.6
    void el.play().catch(() => {})
  }

  /** 나레이션 중 BGM -18dB (Spec §6.2). */
  private duck(on: boolean) {
    this.bgm.volume = this.bgmVolume * (on ? dbToGain(DUCK_DB) : 1)
  }
}
