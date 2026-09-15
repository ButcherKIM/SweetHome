/**
 * 되돌리기·설정·자막 토글 — Spec §8.3 "길게 누르기 게이트 뒤에".
 * 아이가 눌러서 열리면 안 되므로 0.8초 눌러야 열린다.
 */
import { useRef, useState } from 'react'
import { useApp } from '../store'
import type { Latency } from '../audio/latency'

const HOLD_MS = 800

export function SettingsGate({ latency }: { latency: Latency }) {
  const open = useApp((s) => s.settingsOpen)
  const setOpen = useApp((s) => s.setSettings)
  const subtitlesOn = useApp((s) => s.subtitlesOn)
  const toggleSubtitles = useApp((s) => s.toggleSubtitles)
  const sync = useApp((s) => s.syncOffsetMs)
  const setSync = useApp((s) => s.setSyncOffset)
  const goBack = useApp((s) => s.goBack)
  const again = useApp((s) => s.again)

  const timer = useRef<number>(0)
  const [holding, setHolding] = useState(false)

  const down = () => {
    setHolding(true)
    timer.current = window.setTimeout(() => { setHolding(false); setOpen(true) }, HOLD_MS)
  }
  const up = () => { setHolding(false); window.clearTimeout(timer.current) }

  return (
    <>
      <button
        className={`gate${holding ? ' holding' : ''}`}
        onPointerDown={down}
        onPointerUp={up}
        onPointerLeave={up}
        onPointerCancel={up}
        aria-label="설정 — 길게 누르세요"
      >
        <span />
      </button>

      {open ? (
        <div className="overlay settings" role="dialog" aria-label="설정">
          <h2>설정</h2>

          <label className="row">
            <span>자막</span>
            <input id="set-subs" type="checkbox" checked={subtitlesOn} onChange={toggleSubtitles} />
          </label>

          <label className="row">
            <span>자막 싱크 <small>{sync >= 0 ? '+' : ''}{sync}ms</small></span>
            <input
              id="set-sync" type="range" min={-400} max={400} step={10}
              value={sync} onChange={(e) => setSync(Number(e.target.value))}
            />
          </label>
          <p className="note">
            자동 보정 {latency.ms}ms 적용됨 ({latency.source}). 소리와 글자가 어긋나면 여기서 미세조정하세요.
          </p>

          <div className="row buttons">
            <button className="btn" onClick={goBack}>이전 장면</button>
            <button className="btn" onClick={again}>처음부터</button>
            <button className="btn pri" onClick={() => setOpen(false)}>닫기</button>
          </div>
        </div>
      ) : null}
    </>
  )
}
