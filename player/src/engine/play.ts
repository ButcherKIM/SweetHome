/**
 * 트리 진행 — Spec §3.1, §8.2 StoryEngine.
 * 순수 함수. 상태를 받아 다음 상태를 돌려준다.
 */
import type { Beat, Line, Story, StoryNode } from './types'

export type Phase = 'beat' | 'choice' | 'ending'

export interface PlayState {
  nodeId: string
  beat: number
  line: number
  phase: Phase
  /** 지나온 노드. 되돌리기와 "어디까지 왔나"에 쓴다. */
  path: string[]
}

export function nodeOf(story: Story, s: PlayState): StoryNode {
  const n = story.nodes[s.nodeId]
  if (!n) throw new Error(`없는 노드: ${s.nodeId}`)
  return n
}

export function beatOf(story: Story, s: PlayState): Beat | null {
  return nodeOf(story, s).beats[s.beat] ?? null
}

export function lineOf(story: Story, s: PlayState): Line | null {
  return beatOf(story, s)?.lines[s.line] ?? null
}

/** 비트를 다 보고 나면 선택지(있으면) 또는 결말로 간다. */
function phaseAfterBeats(node: StoryNode): Phase {
  return node.choice ? 'choice' : 'ending'
}

export function start(story: Story): PlayState {
  return { nodeId: story.rootNode, beat: 0, line: 0, phase: 'beat', path: [story.rootNode] }
}

function enter(story: Story, nodeId: string, path: string[]): PlayState {
  const node = story.nodes[nodeId]
  if (!node) throw new Error(`없는 노드: ${nodeId}`)
  const hasBeats = node.beats.length > 0
  return {
    nodeId,
    beat: 0,
    line: 0,
    phase: hasBeats ? 'beat' : phaseAfterBeats(node),
    path,
  }
}

/** 한 줄 앞으로. 줄이 끝나면 다음 비트, 비트가 끝나면 선택지나 결말. */
export function next(story: Story, s: PlayState): PlayState {
  if (s.phase !== 'beat') return s
  const node = nodeOf(story, s)
  const beat = node.beats[s.beat]
  if (!beat) return { ...s, phase: phaseAfterBeats(node) }

  if (s.line + 1 < beat.lines.length) return { ...s, line: s.line + 1 }
  if (s.beat + 1 < node.beats.length) return { ...s, beat: s.beat + 1, line: 0 }
  return { ...s, phase: phaseAfterBeats(node) }
}

/** 되돌리기 — 이전 비트의 첫 줄로. 노드 경계를 넘으면 이전 노드의 마지막 비트로. */
export function back(story: Story, s: PlayState): PlayState {
  if (s.phase !== 'beat') {
    const node = nodeOf(story, s)
    return { ...s, phase: 'beat', beat: Math.max(0, node.beats.length - 1), line: 0 }
  }
  if (s.beat > 0) return { ...s, beat: s.beat - 1, line: 0 }

  const path = s.path.slice(0, -1)
  const prev = path.at(-1)
  if (!prev) return s
  const node = story.nodes[prev]
  return { nodeId: prev, beat: Math.max(0, node.beats.length - 1), line: 0, phase: 'beat', path }
}

export function choose(story: Story, s: PlayState, optionId: string): PlayState {
  const opt = nodeOf(story, s).choice?.options.find((o) => o.id === optionId)
  if (!opt) return s
  return enter(story, opt.next, [...s.path, opt.next])
}

export function restart(story: Story): PlayState {
  return start(story)
}

export function endingNodes(story: Story): string[] {
  return Object.keys(story.nodes).filter((id) => story.nodes[id].type === 'ending')
}
