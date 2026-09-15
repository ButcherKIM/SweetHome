/**
 * 에셋 경로 해석과 선행 로드 목록 — Pipeline §S8.
 * 문자열 계산뿐이므로 엔진에 둔다.
 */
import type { PlayState } from './play'
import { nodeOf } from './play'
import type { Actor, Story } from './types'

/** `characters/woodcutter` + pose, `props/axe_gold`, `icon/...` 를 파일 경로로. */
export function actorSrc(story: Story, actor: Actor): string | null {
  const [kind, name] = actor.asset.split('/')
  if (kind === 'characters') {
    const c = story.assets.characters[name]
    if (!c) return null
    const pose = actor.pose ?? Object.keys(c.poses)[0]
    return c.poses[pose] ?? null
  }
  if (kind === 'props') return story.assets.props?.[name]?.src ?? null
  return null
}

export function actorTint(story: Story, actor: Actor): string {
  const [kind, name] = actor.asset.split('/')
  if (kind === 'characters') return story.assets.characters[name]?.tint ?? '#8A8F98'
  if (kind === 'props') return story.assets.props?.[name]?.tint ?? '#8A8F98'
  return '#8A8F98'
}

export function backgroundSrc(story: Story, id: string): string | null {
  return story.assets.backgrounds[id]?.src ?? null
}

export function backgroundTint(story: Story, id: string): string {
  return story.assets.backgrounds[id]?.tint ?? '#6E7F74'
}

/**
 * 지금 받아둬야 할 파일들 — 현재 비트 + 다음 비트 + 선택지 갈래의 첫 비트.
 * Spec §8.4 "비트 전환 끊김 없음".
 */
export function preloadPaths(story: Story, s: PlayState): string[] {
  const out = new Set<string>()
  const node = nodeOf(story, s)

  const collect = (beatIndex: number, n = node) => {
    const beat = n.beats[beatIndex]
    if (!beat) return
    const bg = backgroundSrc(story, beat.scene.background)
    if (bg) out.add(bg)
    for (const a of beat.scene.actors ?? []) {
      const src = actorSrc(story, a)
      if (src) out.add(src)
    }
    for (const l of beat.lines) if (l.audio) out.add(l.audio)
  }

  collect(s.beat)
  collect(s.beat + 1)

  // 마지막 비트에 서 있으면 곧 선택지다 — 세 갈래의 첫 비트를 미리 받는다.
  if (s.beat + 1 >= node.beats.length && node.choice) {
    for (const o of node.choice.options) {
      if (o.image) out.add(o.image)
      const nextNode = story.nodes[o.next]
      if (nextNode) collect(0, nextNode)
    }
  }
  return [...out]
}
