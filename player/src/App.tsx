import { useEffect, useMemo, useState } from 'react'
import { beatOf, lineOf, nodeOf, type Story } from './engine'
import { AudioBus } from './audio/AudioBus'
import { measureLatency, unlockAudio, type Latency } from './audio/latency'
import { ChoiceOverlay } from './renderer/ChoiceOverlay'
import { EndingOverlay } from './renderer/EndingOverlay'
import { FxCanvas } from './renderer/FxCanvas'
import { Loading } from './renderer/Loading'
import { SceneView } from './renderer/SceneView'
import { SettingsGate } from './renderer/SettingsGate'
import { SubtitleBar } from './renderer/SubtitleBar'
import { TitleScreen } from './renderer/TitleScreen'
import { usePlayback } from './renderer/usePlayback'
import { useApp } from './store'

const STORY_URL = import.meta.env.BASE_URL + 'stories/goldaxe/story.json'
const AUDIO_BASE = import.meta.env.BASE_URL + 'stories/goldaxe'

export default function App() {
  const bus = useMemo(() => new AudioBus(AUDIO_BASE), [])
  const screen = useApp((s) => s.screen)
  const boot = useApp((s) => s.boot)
  const fail = useApp((s) => s.fail)
  const begin = useApp((s) => s.begin)
  const setSyncOffset = useApp((s) => s.setSyncOffset)
  const [latency, setLatency] = useState<Latency>({ ms: 0, source: 'default' })

  useEffect(() => {
    let alive = true
    fetch(STORY_URL)
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`story.json ${r.status}`))))
      .then((s: Story) => { if (alive) boot(s) })
      .catch((e: Error) => { if (alive) fail(e.message) })
    return () => { alive = false }
  }, [boot, fail])

  /** 탭 게이트 (§6.6) 에서 오디오를 깨우고, 그 자리에서 출력 지연을 잰다 (§6.5). */
  const start = async () => {
    await unlockAudio()
    const l = measureLatency()
    setLatency(l)
    if (useApp.getState().syncOffsetMs === 0) setSyncOffset(l.ms)
    begin()
  }

  if (screen === 'loading') return <Frame><Loading /></Frame>
  if (screen === 'error')
    return <Frame><Loading label={`이야기를 못 불러왔어요 — ${useApp.getState().error}`} /></Frame>
  return <Frame><Play bus={bus} latency={latency} onStart={start} /></Frame>
}

function Frame({ children }: { children: React.ReactNode }) {
  return <div className="app"><div className="stage" id="stage">{children}</div></div>
}

function Play({ bus, latency, onStart }: { bus: AudioBus; latency: Latency; onStart: () => void }) {
  const story = useApp((s) => s.story)!
  const play = useApp((s) => s.play)
  const screen = useApp((s) => s.screen)
  const advance = useApp((s) => s.advance)
  const subtitlesOn = useApp((s) => s.subtitlesOn)
  const word = usePlayback(bus)

  if (screen === 'title' || !play) return <TitleScreen story={story} onStart={onStart} />

  const node = nodeOf(story, play)
  const beat = beatOf(story, play)
  const line = lineOf(story, play)

  return (
    <>
      {beat ? <SceneView story={story} scene={beat.scene} beatId={beat.id} /> : null}
      {beat ? <FxCanvas fx={beat.scene.fx ?? 'none'} /> : null}

      {/* 화면 어디든 탭 = 다음 비트 (선택 화면 제외) — Spec §8.3 */}
      {play.phase === 'beat' ? (
        <button className="tap" onClick={advance} aria-label="다음" />
      ) : null}

      {play.phase === 'beat' && line ? (
        <SubtitleBar story={story} line={line} word={word} on={subtitlesOn} />
      ) : null}

      {play.phase === 'choice' && node.choice ? (
        <ChoiceOverlay choice={node.choice} bus={bus} />
      ) : null}

      {play.phase === 'ending' ? <EndingOverlay story={story} node={node} /> : null}

      <SettingsGate latency={latency} />
    </>
  )
}
