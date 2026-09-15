/** engine 의 Storage 를 브라우저에 붙인다. 사생활 보호 모드에서 던져도 앱은 돈다. */
import { memoryStorage, type Storage } from '../engine'

export function webStorage(): Storage {
  try {
    const probe = '__sweethome__'
    window.localStorage.setItem(probe, '1')
    window.localStorage.removeItem(probe)
    return {
      get: (k) => window.localStorage.getItem(k),
      set: (k, v) => window.localStorage.setItem(k, v),
    }
  } catch {
    return memoryStorage()
  }
}
