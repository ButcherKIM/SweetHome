/**
 * 3지선다 — Spec §3.5, §8.3.
 * 그림 320px 이상 · 터치 120px 이상 · 화면 하단 1/2 · 선택지를 순서대로 읽어주고
 * 탭하면 다시 읽는다 · 고른 그림이 커지며 확정된다.
 */
import { useEffect, useRef, useState } from 'react'
import type { Choice } from '../engine'
import type { AudioBus } from '../audio/AudioBus'
import { useApp } from '../store'

const ICONS = import.meta.env.BASE_URL + 'stories/goldaxe/assets'
const COMMIT_MS = 700

export function ChoiceOverlay({ choice, bus }: { choice: Choice; bus: AudioBus }) {
  const pick = useApp((s) => s.pick)
  const commitPick = useApp((s) => s.commitPick)
  const picking = useApp((s) => s.picking)
  const [reading, setReading] = useState(-1) // -1 = 질문, 0.. = 선택지
  const timer = useRef<number>(0)

  /** 질문 → 선택지 1 → 2 → 3 순서대로 읽는다. */
  useEffect(() => {
    let alive = true
    const queue: (string | undefined)[] = [choice.promptAudio, ...choice.options.map((o) => o.audio)]
    let i = 0
    const step = () => {
      if (!alive || i >= queue.length) { setReading(-2); return }
      setReading(i - 1)
      const src = queue[i]
      i += 1
      if (!src) { timer.current = window.setTimeout(step, 900); return }
      bus.playLine(src, step)
    }
    step()
    return () => { alive = false; window.clearTimeout(timer.current); bus.stopLine() }
  }, [choice, bus])

  /**
   * 탭하면 바로 고른다. 읽어주는 도중이어도 마찬가지다 —
   * 아이가 누른 것이 안 먹히면 앱이 고장난 걸로 받아들인다.
   * 고른 그림이 커지는 동안 그 선택지를 한 번 더 들려준다 (§3.5 "탭하면 다시 읽음").
   */
  const tap = (id: string, audio?: string) => {
    if (picking) return
    window.clearTimeout(timer.current)
    setReading(-2)
    pick(id)
    bus.sfx('pick')

    const tappedAt = performance.now()
    let fired = false
    const go = () => {
      if (fired) return
      fired = true
      const left = Math.max(0, COMMIT_MS - (performance.now() - tappedAt))
      timer.current = window.setTimeout(commitPick, left)
    }
    bus.playLine(audio, go)
  }

  return (
    <div className="overlay choice">
      <p className="ask">{choice.promptText}</p>
      <div className="opts">
        {choice.options.map((o, i) => {
          const state = picking === o.id ? ' taken' : picking ? ' faded' : ''
          return (
            <button
              key={o.id}
              className={`opt${state}${reading === i ? ' reading' : ''}`}
              onClick={() => tap(o.id, o.audio)}
              aria-label={o.label}
            >
              <span
                className="thumb"
                style={{
                  backgroundColor: o.tint ?? '#7A8A84',
                  backgroundImage: o.image ? `url(${ICONS}/${o.image})` : undefined,
                }}
              />
              <b>{o.label}</b>
            </button>
          )
        })}
      </div>
      <p className="hint">{picking ? '\u00a0' : '골라 보세요'}</p>
    </div>
  )
}
