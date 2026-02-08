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
  // 1. 開発サーバー (npm run dev) の高速化
  optimizeDeps: {
    // 【重要】exclude を削除し、逆に include に加えるか、Viteの自動検出に任せます。
    // これにより、巨大なUniverライブラリが1つのファイルに事前バンドルされ、
    // ブラウザのリクエスト数が激減して起動が爆速になります。
    include: [
      'react', 
      'react-dom',
      'react-resizable-panels', 
      'lucide-react',
      'luckyexcel',
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