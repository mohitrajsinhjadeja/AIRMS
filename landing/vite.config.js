import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  define: {
    'process.env.VITE_API_URL': JSON.stringify('https://airms-backend-1013218741719.us-central1.run.app')
  },
  server: {
    port: 5173,
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})