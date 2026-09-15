/** 배경 + 컷아웃 배치 — Spec §8.2 BackgroundView · ActorView, §4.5 움직임 어휘. */
import {
  actorSrc, actorTint, backgroundSrc, backgroundTint, cueKind, hiddenAtStart,
  type Beat, type ResolvedCue, type Scene, type Story,
} from '../engine'

const STORIES_BASE = import.meta.env.BASE_URL + 'stories/goldaxe/assets'

function treat(scene: Scene, story: Story) {
  const t = { blurPx: 0, brightness: 100, saturate: 100, ...story.stage.bgTreatment, ...scene.bgTreatment }
  return `blur(${t.blurPx}px) brightness(${t.brightness}%) saturate(${t.saturate}%)`
}

export function SceneView({ story, beat, line, cues, shown }: {
  story: Story
  beat: Beat
  /** 지금 몇 번째 줄인가 — 앞선 줄에서 이미 나타난 배우는 계속 보여야 한다 */
  line: number
  cues: ResolvedCue[]
  shown: Map<string, 'shown' | 'hidden'>
}) {
  const scene = beat.scene
  const bg = backgroundSrc(story, scene.background)
  const camera = scene.camera ?? 'still'
  const transition = scene.transitionIn ?? 'pageTurn'
  const hidden = hiddenAtStart(beat, line)

  const camCue = cues.find((c) => c.target === 'camera' && cueKind(c.do) === 'camera')
  const stageCue = cues.find((c) => c.target === 'stage' && cueKind(c.do) === 'stage')
  const cueFor = (id?: string) =>
    id ? cues.find((c) => c.target === id && cueKind(c.do) === 'actor') : undefined

  return (
    <div key={beat.id} className={`scene t-${transition}`}>
      <div className={camCue ? `camwrap q-${camCue.do}` : 'camwrap'}>
        <div
          className={`bg cam-${camera}`}
          style={{
            backgroundColor: backgroundTint(story, scene.background),
            backgroundImage: bg ? `url(${STORIES_BASE}/${bg})` : undefined,
            filter: treat(scene, story),
          }}
        />
      </div>
      {stageCue ? <div className={`stagefx q-${stageCue.do}`} aria-hidden="true" /> : null}
      {(scene.actors ?? []).map((a, i) => {
        const src = actorSrc(story, a)
        const anim = a.anim ?? 'none'
        const enter = a.enter ?? 'none'
        const screen = a.blend === 'screen'
        const q = cueFor(a.id)
        // 큐가 등장시키기로 한 배우는 그 순간까지 숨어 있고, vanish 한 뒤엔 계속 없다
        const state = a.id ? shown.get(a.id) : undefined
        const off = state === 'hidden' || (a.id !== undefined && hidden.has(a.id) && state !== 'shown')
        return (
          <div
            key={`${a.asset}-${i}`}
            className={`actor${screen ? ' screen' : ''}${off ? ' off' : ''}`}
            style={{
              left: `${a.x * 100}%`,
              top: `${a.y * 100}%`,
              zIndex: a.z ?? 10,
              ['--scale' as string]: String(a.scale ?? 1),
            }}
          >
            <div className={`ent e-${enter}`}>
              <div className="flp" style={{ transform: a.flip ? 'scaleX(-1)' : undefined }}>
                <div className={q ? `cue q-${q.do}` : 'cue'}>
                <div
                  className={`art a-${anim}`}
                  style={
                    src
                      ? { backgroundImage: `url(${STORIES_BASE}/${src})` }
                      : { backgroundColor: actorTint(story, a), borderRadius: '14% 14% 6% 6%' }
                  }
                />
                </div>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
