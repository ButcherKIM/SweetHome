/** 결말 — Spec §3.4. 원작 결말이면 배지를 띄운다. */
import { endingNodes, type Story, type StoryNode } from '../engine'
import { useApp } from '../store'

export function EndingOverlay({ story, node }: { story: Story; node: StoryNode }) {
  const again = useApp((s) => s.again)
  const seen = useApp((s) => s.seenEndings)
  const total = endingNodes(story).length

  return (
    <div className="overlay ending">
      {node.isCanonical ? <span className="badge">원작 엔딩을 찾았어요!</span> : null}
      <p className="t">{node.endingTitle}</p>
      <p className="l">{node.lesson}</p>
      <button className="btn" onClick={again}>다시 하기</button>
      <p className="count">{seen.length} / {total} 엔딩</p>
    </div>
  )
}
