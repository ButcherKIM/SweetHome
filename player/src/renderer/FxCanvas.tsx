/** 파티클 오버레이 — Spec §4.5 fx (7종). 캔버스 한 장. */
import { useEffect, useRef } from 'react'
import type { Fx } from '../engine'

interface Spec {
  n: number; c: string; r: [number, number]; vy: [number, number]
  sway: number; fade: number; a?: number; line?: number
}

const FX: Record<Exclude<Fx, 'none'>, Spec> = {
  petals:    { n: 26, c: '#E8B4C8', r: [3, 7],     vy: [0.18, 0.5],   sway: 1.3,  fade: 0 },
  snow:      { n: 46, c: '#FFFFFF', r: [1.4, 3.4], vy: [0.2, 0.55],   sway: 0.7,  fade: 0 },
  rain:      { n: 60, c: '#BFD4E0', r: [0.8, 1.4], vy: [2.4, 4],      sway: 0.1,  fade: 0, line: 12 },
  dust:      { n: 26, c: '#E6DCC4', r: [1, 2.2],   vy: [-0.08, 0.1],  sway: 0.35, fade: 0.5, a: 0.34 },
  fireflies: { n: 20, c: '#FFE08A', r: [1.8, 3.4], vy: [-0.14, 0.1],  sway: 0.5,  fade: 1 },
  sparkle:   { n: 30, c: '#FFF1B8', r: [1.4, 3.2], vy: [-0.3, -0.05], sway: 0.4,  fade: 1 },
}

export function FxCanvas({ fx }: { fx: Fx }) {
  const ref = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const cv = ref.current
    if (!cv) return
    const cx = cv.getContext('2d')
    if (!cx) return

    const dpr = window.devicePixelRatio || 1
    const resize = () => {
      const r = cv.getBoundingClientRect()
      cv.width = Math.max(1, r.width * dpr)
      cv.height = Math.max(1, r.height * dpr)
    }
    resize()
    window.addEventListener('resize', resize)

    const spec = fx !== 'none' ? FX[fx] : null
    const quiet = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const parts = spec && !quiet
      ? Array.from({ length: spec.n }, () => ({
          x: Math.random() * cv.width, y: Math.random() * cv.height,
          r: (spec.r[0] + Math.random() * (spec.r[1] - spec.r[0])) * dpr,
          vy: (spec.vy[0] + Math.random() * (spec.vy[1] - spec.vy[0])) * dpr,
          ph: Math.random() * 6.28, sp: 0.4 + Math.random() * 0.8,
        }))
      : []

    let raf = 0
    const tick = () => {
      raf = requestAnimationFrame(tick)
      const { width: W, height: H } = cv
      cx.clearRect(0, 0, W, H)
      if (!spec || !parts.length) return
      cx.fillStyle = spec.c
      cx.strokeStyle = spec.c
      for (const o of parts) {
        o.y += o.vy
        o.ph += 0.02 * o.sp
        o.x += Math.sin(o.ph) * spec.sway * dpr
        if (o.y > H + 20) { o.y = -20; o.x = Math.random() * W }
        if (o.y < -20) { o.y = H + 20; o.x = Math.random() * W }
        if (o.x < -20) o.x = W + 20
        if (o.x > W + 20) o.x = -20
        const base = spec.a ?? 0.8
        cx.globalAlpha = base * (spec.fade
          ? (0.35 + 0.65 * Math.abs(Math.sin(o.ph * 0.7))) * spec.fade + (1 - spec.fade)
          : 1)
        if (spec.line) {
          cx.lineWidth = o.r
          cx.beginPath()
          cx.moveTo(o.x, o.y)
          cx.lineTo(o.x, o.y + spec.line * dpr)
          cx.stroke()
        } else {
          cx.beginPath()
          cx.arc(o.x, o.y, o.r, 0, 6.2832)
          cx.fill()
        }
      }
      cx.globalAlpha = 1
    }
    raf = requestAnimationFrame(tick)
    return () => { cancelAnimationFrame(raf); window.removeEventListener('resize', resize) }
  }, [fx])

  return <canvas ref={ref} className="fx" aria-hidden="true" />
}
