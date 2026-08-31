/**
 * Mock-Server fuer `/api`, als Middleware im Vite-Dev-Server.
 *
 * Er ist der Grund, warum der Frontend-Strang keinen Backend-Commit abwarten
 * muss. Eingeschaltet wird er ueber die Umgebungsvariable
 * `VITE_KAIMARKIT_MOCK=1`; ohne sie geht `/api` per Proxy an localhost:8000.
 *
 *     VITE_KAIMARKIT_MOCK=1 npm run dev
 *
 * Die Middleware sitzt vor dem Proxy, nicht im Browser. Damit antwortet der Mock
 * auch auf `curl` — eine Attrappe fuer `fetch` koennte das nicht.
 *
 * Drei Faelle, ausgeloest ueber den Dateinamen:
 *
 *   bericht.pdf          -> 200, Markdown, keine Warnungen
 *   bericht-warnung.pdf  -> 200, Markdown mit zwei Warnungen
 *   bericht-fehler.pdf   -> 500, `conversion_failed`
 *
 * Ohne den dritten Fall bliebe die Fehlerdarstellung im Frontend ungeprueft.
 */

import type { IncomingMessage, ServerResponse } from 'node:http'
import busboy from 'busboy'
import type { Connect, Plugin } from 'vite'
import type { ErrorCode, ErrorResponse, HealthResponse } from '../types.ts'
import {
  capabilities,
  caseForFilename,
  entryFor,
  errorStatus,
  failureDetail,
  version,
} from './fixtures.ts'

/** Name der Umgebungsvariable, die den Mock einschaltet. */
export const MOCK_ENV_VAR = 'VITE_KAIMARKIT_MOCK'

/** Kuenstliche Verzoegerung je Konvertierung, damit Warteschlange und
 *  Fortschrittsanzeige im Frontend ueberhaupt sichtbar werden. */
const MIN_DELAY_MS = 400
const MAX_DELAY_MS = 1600

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

interface UploadedFile {
  filename: string
  bytes: number
}

interface ParsedUpload {
  files: UploadedFile[]
  fields: Record<string, string>
}

function sendJson(res: ServerResponse, status: number, body: unknown): void {
  const payload = JSON.stringify(body)
  res.statusCode = status
  res.setHeader('Content-Type', 'application/json; charset=utf-8')
  res.end(payload)
}

function sendError(res: ServerResponse, code: ErrorCode, detail: string): void {
  const body: ErrorResponse = { detail, code }
  sendJson(res, errorStatus[code], body)
}

/**
 * Liest den Multipart-Rumpf. Der Inhalt der Datei interessiert den Mock nicht,
 * nur Name und Groesse — die Bytes werden gezaehlt und verworfen.
 */
function parseUpload(req: IncomingMessage): Promise<ParsedUpload> {
  return new Promise((resolve, reject) => {
    const parser = busboy({ headers: req.headers })
    const files: UploadedFile[] = []
    const fields: Record<string, string> = {}

    parser.on('field', (name, value) => {
      fields[name] = value
    })
    parser.on('file', (_name, stream, info) => {
      let bytes = 0
      stream.on('data', (chunk: Buffer) => {
        bytes += chunk.length
      })
      stream.on('end', () => {
        files.push({ filename: info.filename, bytes })
      })
      stream.resume()
    })
    parser.on('error', reject)
    parser.on('close', () => resolve({ files, fields }))

    req.pipe(parser)
  })
}

function extensionOf(filename: string): string {
  const dot = filename.lastIndexOf('.')
  return dot < 0 ? '' : filename.slice(dot).toLowerCase()
}

/** Der Dateiname ohne Pfadanteil — das Backend saeubert ihn ebenso. */
function sanitize(filename: string): string {
  return filename.split(/[\\/]/).pop() ?? filename
}

/**
 * Waehlt die Engine wie das Backend: `auto` folgt der Praeferenzliste, eine
 * ausdruecklich genannte Engine wird nie durch eine andere ersetzt.
 */
function chooseEngine(
  extension: string,
  requested: string,
): { engine: string } | { code: ErrorCode; detail: string } {
  const candidates = capabilities.formats[extension]
  if (!candidates) {
    return {
      code: 'unsupported_format',
      detail: `Format ${extension || '(ohne Endung)'} wird nicht unterstuetzt.`,
    }
  }
  if (requested === 'auto') {
    return { engine: candidates[0]! }
  }
  if (!(requested in capabilities.engines)) {
    return { code: 'engine_unavailable', detail: `Engine ${requested} ist nicht installiert.` }
  }
  if (!candidates.includes(requested)) {
    return {
      code: 'engine_unsuitable',
      detail: `Engine ${requested} kann ${extension} nicht lesen.`,
    }
  }
  return { engine: requested }
}

async function handleConvert(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const { files, fields } = await parseUpload(req)
  const file = files[0]
  if (!file) {
    sendError(res, 'unsupported_format', 'Es wurde keine Datei uebergeben.')
    return
  }

  const filename = sanitize(file.filename)
  const maxBytes = capabilities.limits.max_file_size_mb * 1024 * 1024
  if (file.bytes > maxBytes) {
    sendError(
      res,
      'file_too_large',
      `Datei ist groesser als ${capabilities.limits.max_file_size_mb} MB.`,
    )
    return
  }

  const chosen = chooseEngine(extensionOf(filename), fields.engine ?? 'auto')
  if ('code' in chosen) {
    sendError(res, chosen.code, chosen.detail)
    return
  }

  const durationMs = MIN_DELAY_MS + Math.round(Math.random() * (MAX_DELAY_MS - MIN_DELAY_MS))
  await sleep(durationMs)

  if (caseForFilename(filename) === 'failure') {
    sendError(res, 'conversion_failed', failureDetail)
    return
  }

  const entry = entryFor(filename, chosen.engine, durationMs)
  const accept = req.headers.accept ?? ''
  if (accept.includes('application/json')) {
    sendJson(res, 200, entry)
    return
  }

  const stem = filename.replace(/\.[^.]+$/, '')
  res.statusCode = 200
  res.setHeader('Content-Type', 'text/markdown; charset=utf-8')
  res.setHeader('Content-Disposition', `attachment; filename="${stem}.md"`)
  res.setHeader('X-Engine', entry.engine ?? '')
  res.setHeader('X-Warnings', String(entry.warnings.length))
  res.end(entry.markdown ?? '')
}

/** Vite-Plugin, das `/api` im Dev-Server selbst beantwortet. */
export function mockApi(): Plugin {
  return {
    name: 'kaimarkit-mock-api',
    apply: 'serve',
    configureServer(server) {
      server.middlewares.use('/api', (req, res, next) => {
        handle(req, res).catch(next)
      })
      server.config.logger.info(
        `  \x1b[32m➜\x1b[0m  Mock-API aktiv (${MOCK_ENV_VAR}), Backend-Proxy aus`,
      )
    },
  }
}

async function handle(req: Connect.IncomingMessage, res: ServerResponse): Promise<void> {
  // `server.middlewares.use('/api', ...)` schneidet das Praefix ab: aus
  // /api/capabilities wird hier /capabilities.
  const path = (req.url ?? '/').split('?')[0]!.replace(/\/$/, '')
  const method = req.method ?? 'GET'

  if (method === 'GET' && path === '/health') {
    const body: HealthResponse = { status: 'ok', version }
    sendJson(res, 200, body)
    return
  }
  if (method === 'GET' && path === '/capabilities') {
    await sleep(120)
    sendJson(res, 200, capabilities)
    return
  }
  if (method === 'POST' && path === '/convert') {
    await handleConvert(req, res)
    return
  }

  sendJson(res, 404, { detail: `Der Mock kennt ${method} /api${path} nicht.` })
}
