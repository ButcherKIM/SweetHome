/** 배경 + 컷아웃 배치 — Spec §8.2 BackgroundView · ActorView, §4.5 움직임 어휘. */
import { actorSrc, actorTint, backgroundSrc, backgroundTint, type Scene, type Story } from '../engine'

const STORIES_BASE = import.meta.env.BASE_URL + 'stories/goldaxe/assets'

function treat(scene: Scene, story: Story) {
  const t = { blurPx: 0, brightness: 100, saturate: 100, ...story.stage.bgTreatment, ...scene.bgTreatment }
  return `blur(${t.blurPx}px) brightness(${t.brightness}%) saturate(${t.saturate}%)`
}

export function SceneView({ story, scene, beatId }: { story: Story; scene: Scene; beatId: string }) {
  const bg = backgroundSrc(story, scene.background)
  const camera = scene.camera ?? 'still'
  const transition = scene.transitionIn ?? 'pageTurn'

  return (
    <div key={beatId} className={`scene t-${transition}`}>
      <div
        className={`bg cam-${camera}`}
        style={{
          backgroundColor: backgroundTint(story, scene.background),
          backgroundImage: bg ? `url(${STORIES_BASE}/${bg})` : undefined,
          filter: treat(scene, story),
        }}
      />
      {(scene.actors ?? []).map((a, i) => {
        const src = actorSrc(story, a)
        const anim = a.anim ?? 'none'
        const enter = a.enter ?? 'none'
        const screen = a.blend === 'screen'
        return (
          <div
            key={`${a.asset}-${i}`}
            className={`actor${screen ? ' screen' : ''}`}
            style={{
              left: `${a.x * 100}%`,
              top: `${a.y * 100}%`,
              zIndex: a.z ?? 10,
              ['--scale' as string]: String(a.scale ?? 1),
            }}
          >
            <div className={`ent e-${enter}`}>
              <div className="flp" style={{ transform: a.flip ? 'scaleX(-1)' : undefined }}>
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
        )
      })}
    </div>
  )
}
