/**
 * 표지 — Spec §3.4 (본 엔딩 목록) · §6.6 (자동재생 탭 게이트).
 * 브라우저는 제스처 없이 소리를 막는다. 이 화면의 탭이 그 제스처다.
 */
import { endingNodes, type Story } from '../engine'
import { useApp } from '../store'

export function TitleScreen({ story, onStart }: { story: Story; onStart: () => void }) {
  const seen = useApp((s) => s.seenEndings)
  const endings = endingNodes(story)

  return (
    <div className="title">
      <p className="src">{story.source}</p>
      <h1>{story.title}</h1>
      <button className="start" onClick={onStart}>시작하기</button>

      <section className="collected" aria-label="본 엔딩">
        <h2>본 엔딩 {seen.length} / {endings.length}</h2>
        <ul>
          {endings.map((id) => {
            const n = story.nodes[id]
            const got = seen.includes(id)
            return (
              <li key={id} className={got ? 'got' : ''}>
                {got ? (n.endingTitle ?? '?') : '？'}
                {got && n.isCanonical ? <em>원작</em> : null}
              </li>
            )
          })}
        </ul>
      </section>
    </div>
  )
}
