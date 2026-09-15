/**
 * 자막 — Spec §6.3. 제품의 절반이다.
 * 기본 ON · 64px@1080p · 어절 간격 0.3em · 하이라이트 시 1.08배.
 */
import type { Line, Story } from '../engine'

export function SubtitleBar({ story, line, word, on }: {
  story: Story; line: Line; word: number; on: boolean
}) {
  if (!on) return null
  const spacing = story.subtitle?.wordSpacingEm ?? 0.3
  const words = line.wordTimings.map(([a, b]) => line.text.slice(a, b))

  return (
    <div className="subs">
      <p className="box" style={{ ['--gap' as string]: `${spacing}em` }}>
        {words.map((w, i) => (
          <span key={i} className={i === word ? 'w on' : 'w'}>{w}</span>
        ))}
      </p>
    </div>
  )
}
