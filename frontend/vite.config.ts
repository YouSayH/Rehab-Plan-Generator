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
  optimizeDeps: {
    // 1. これらはバンドルする
    include: ['react-resizable-panels', 'lucide-react'],
    
    // 2. Univer系はバンドル「しない」（ここが最重要！）
    // これにより、Viteがソースコードをそのまま扱うようになり、2重読み込みを防ぎます
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
      '@univerjs/sheets-formula'
    ]
  }
})