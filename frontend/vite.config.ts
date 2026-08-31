import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

/**
 * Der Dev-Server reicht `/api` an das Backend auf localhost:8000 weiter.
 *
 * Damit spricht das Frontend in der Entwicklung dieselbe Herkunft an wie im
 * Container, wo `main.py` die gebaute Anwendung selbst ausliefert. Der API-Client
 * kennt deshalb nur den Pfad `/api` und nie einen Host.
 */
export default defineConfig({
  plugins: [vue(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
