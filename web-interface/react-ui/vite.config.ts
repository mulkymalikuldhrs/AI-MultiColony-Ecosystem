import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 12000,
    strictPort: true,
    cors: true,
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      'work-1-bqyopsolghmiebxx.prod-runtime.all-hands.dev',
      'work-2-bqyopsolghmiebxx.prod-runtime.all-hands.dev',
      '.all-hands.dev'
    ],
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
      },
      '/socket.io': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
        ws: true,
      },
    },
  },
})