import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/segments': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/forecast': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/reports': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/recommendations': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/churn': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/anomalies': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
