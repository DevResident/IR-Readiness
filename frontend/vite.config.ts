import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// In development, /api calls are proxied to the FastAPI backend, so the browser
// only ever talks to one origin. In production, serve both behind the same host.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': process.env.VITE_API_TARGET ?? 'http://127.0.0.1:8000',
    },
  },
})
