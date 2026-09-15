import { defineConfig, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'
import { createReadStream, existsSync, statSync } from 'node:fs'
import { cp } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))

const MIME: Record<string, string> = {
  '.json': 'application/json', '.png': 'image/png', '.webp': 'image/webp',
  '.mp3': 'audio/mpeg', '.opus': 'audio/ogg', '.svg': 'image/svg+xml',
}

/** stories/ 는 앱 밖에 산다 (파이프라인 산출물). dev 에서 서빙하고 build 에서 복사한다. */
function stories(): Plugin {
  const dir = resolve(HERE, '../stories')
  return {
    name: 'sweethome-stories',
    configureServer(server) {
      server.middlewares.use('/stories', (req, res, next) => {
        const rel = decodeURIComponent(((req as { url?: string }).url ?? '/').split('?')[0])
        const file = resolve(dir, '.' + rel)
        if (!file.startsWith(dir) || !existsSync(file) || statSync(file).isDirectory()) return next()
        const ext = file.slice(file.lastIndexOf('.'))
        res.setHeader('Content-Type', MIME[ext] ?? 'application/octet-stream')
        createReadStream(file).pipe(res)
      })
    },
    async closeBundle() {
      await cp(dir, resolve(HERE, 'dist/stories'), { recursive: true })
    },
  }
}

export default defineConfig({
  base: './',
  plugins: [react(), stories()],
  build: { target: 'es2022' },
})
