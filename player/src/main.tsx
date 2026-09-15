import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import { attachStorage } from './store'
import { webStorage } from './platform/webStorage'
import './app.css'

attachStorage(webStorage())
createRoot(document.getElementById('root')!).render(
  <StrictMode><App /></StrictMode>,
)
