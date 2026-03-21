/**
 * File: frontend/src/main.tsx
 *
 * Summary:
 * Reactアプリケーションのエントリーポイントファイル。
 * `createRoot` を使用して、HTML側のルート要素（id="root"）にメインコンポーネントである `<App />` をレンダリングし、Reactの仮想DOMをマウントする役割を担っています。
 *
 * Tags: Frontend, React, Entry Point
 */

import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <App />
)