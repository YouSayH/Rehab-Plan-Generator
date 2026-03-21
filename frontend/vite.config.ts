/**
 * File: frontend/vite.config.ts
 *
 * Summary:
 * フロントエンドのビルドツール「Vite」の設定ファイル。
 * 開発サーバーにおけるバックエンドAPIへのリクエスト転送（プロキシ設定）を行っています。さらに、スプレッドシート機能を提供する巨大なライブラリ `@univerjs` の読み込みエラーを防ぐために事前バンドルから除外（`optimizeDeps.exclude`）し、本番ビルド時にはファイルサイズを最適化するためのチャンク分割（`manualChunks`）を設定するなど、パフォーマンスと動作安定化のための重要なチューニングが行われています。
 *
 * Tags: Frontend, Vite, Build Configuration, Proxy, Optimization, Univer
 */

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    watch: {
      usePolling: true,
    },
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
      }
    }
  },
  // 1. 開発サーバー (npm run dev) の設定
  optimizeDeps: {
    include: ['exceljs'],
    // 【修正】includeではなくexcludeを使用します
    // UniverJSを事前バンドルから「除外」し、直接ESMとして読み込むことで
    // 二重読み込みやサービスの競合エラー（Identifier already exists）を防ぎます。
    exclude: [
      '@univerjs/core',
      '@univerjs/design',
      '@univerjs/engine-render',
      '@univerjs/engine-formula',
      '@univerjs/ui',
      '@univerjs/docs',
      '@univerjs/docs-ui',
      '@univerjs/sheets',
      '@univerjs/sheets-ui',
      '@univerjs/sheets-formula',
      '@univerjs/presets',
      '@univerjs/preset-sheets-core'
    ],
  },
  // 2. 本番ビルド (npm run build) の最適化
  build: {
    rollupOptions: {
      output: {
        // ライブラリごとにファイルを分割して、メインの読み込みを軽くする
        manualChunks: {
          'vendor-react': ['react', 'react-dom', 'react-resizable-panels'],
          'vendor-univer': [
            '@univerjs/core',
            '@univerjs/design',
            '@univerjs/engine-render',
            '@univerjs/engine-formula',
            '@univerjs/ui',
            '@univerjs/docs',
            '@univerjs/docs-ui',
            '@univerjs/sheets',
            '@univerjs/sheets-ui',
            '@univerjs/sheets-formula'
          ],
        },
      },
    },
    // Univerなどの新しいライブラリに合わせてターゲットを調整
    target: 'es2020', 
  },
})