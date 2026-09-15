/**
 * 재생 루프 — Spec §6.4 "한 시계".
 * 넘기는 주체는 여기 하나다. 오디오 종료와 durationMs 중 늦은 쪽에서 넘어간다.
 */
import { useEffect, useRef, useState } from 'react'
import { lineOf, preloadPaths, shouldAdvance, wordIndexAt } from '../engine'
import type { AudioBus } from '../audio/AudioBus'
import { useApp } from '../store'

export function usePlayback(bus: AudioBus) {
  const story = useApp((s) => s.story)
  const play = useApp((s) => s.play)
  const advance = useApp((s) => s.advance)
  const syncOffsetMs = useApp((s) => s.syncOffsetMs)
  const [word, setWord] = useState(-1)

  const audioEnded = useRef(false)
  const startedAt = useRef(0)

  const key = play ? `${play.nodeId}:${play.beat}:${play.line}:${play.phase}` : ''

  useEffect(() => {
    if (!story || !play || play.phase !== 'beat') return
    const line = lineOf(story, play)
    if (!line) return

    setWord(-1)
    audioEnded.current = false
    startedAt.current = performance.now()

    bus.preload(preloadPaths(story, play))
    bus.playLine(line.audio, () => { audioEnded.current = true })

    let raf = 0
    const tick = () => {
      raf = requestAnimationFrame(tick)
      const elapsed = performance.now() - startedAt.current
      // 자막은 실제로 나는 소리를 따라간다. 오디오가 없으면 경과 시간으로 대신한다.
      const heard = (bus.positionMs || elapsed) - syncOffsetMs
      setWord(wordIndexAt(line.wordTimings, heard))
      if (shouldAdvance(elapsed, line, audioEnded.current)) {
        cancelAnimationFrame(raf)
        advance()
      }
    }
    raf = requestAnimationFrame(tick)

    return () => {
      cancelAnimationFrame(raf)
      bus.stopLine()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key])

  return word
}
