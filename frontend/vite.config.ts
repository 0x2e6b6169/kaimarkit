import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { mockApi, MOCK_ENV_VAR } from './src/mocks/index.ts'

/**
 * Zwei Betriebsarten in der Entwicklung, und sie schliessen einander aus:
 *
 *   npm run dev                      -> /api geht per Proxy an localhost:8000
 *   VITE_KAIMARKIT_MOCK=1 npm run dev -> /api beantwortet der Mock im Dev-Server
 *
 * Der Mock haengt sich als Middleware vor den Proxy. Deshalb wird der Proxy in
 * dieser Betriebsart gar nicht erst eingerichtet: Sonst liefe jede Anfrage, die
 * der Mock nicht kennt, still in ein Backend, das keiner gestartet hat.
 */
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const useMock = env[MOCK_ENV_VAR] === '1' || env[MOCK_ENV_VAR] === 'true'

  return {
    plugins: [vue(), tailwindcss(), ...(useMock ? [mockApi()] : [])],
    server: {
      port: 5173,
      proxy: useMock
        ? undefined
        : {
            '/api': {
              target: 'http://localhost:8000',
              changeOrigin: true,
            },
          },
    },
  }
})
