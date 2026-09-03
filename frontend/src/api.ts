/**
 * Der einzige Ort, an dem das Frontend mit dem Backend spricht.
 *
 * Alles, was hier hinausgeht, folgt `contracts/api.md`. Die Typen stammen
 * ausschliesslich aus `src/types.ts`. Wer ein Feld braucht, das dort fehlt,
 * aendert `contracts/api.md`, `backend/app/models.py` und `src/types.ts`
 * gemeinsam — siehe CLAUDE.md, Konvention 1.
 *
 * Zwei Zusagen an die Aufrufer:
 *
 * 1. Jeder Fehlschlag kommt als `ApiError` mit einer lesbaren Meldung. Netz- und
 *    HTTP-Fehler sehen von aussen gleich aus; keine Komponente muss `response.ok`
 *    pruefen oder einen Fehlerrumpf auspacken.
 * 2. Die Antworten kommen als JSON. `Accept: application/json` steht deshalb an
 *    jeder Anfrage: Ohne den Kopf liefert `/api/convert` Markdown als Download,
 *    was das Frontend nicht gebrauchen kann.
 *
 * Der Download einer einzelnen Datei und das ZIP baut das Frontend selbst (FE-6),
 * nicht ueber `/api/convert/batch`. Der Stapelendpunkt ist fuer Skripte gedacht;
 * die Warteschlange ruft `/api/convert` je Datei auf, weil sie Fortschritt und
 * Vorschau einzeln zeigt.
 */

import type {
  CapabilitiesResponse,
  ConversionEntry,
  ConvertOptions,
  ErrorCode,
  ErrorResponse,
  HealthResponse,
} from './types'

const API_BASE = '/api'

/** Ein Fehlschlag der Schnittstelle, uebersetzt in eine Meldung fuer die Oberflaeche. */
export class ApiError extends Error {
  /** Der Fehlercode aus dem Rumpf, oder null bei Netzfehlern und leerem Rumpf. */
  readonly code: ErrorCode | null
  /** Der HTTP-Status, oder 0, wenn die Anfrage den Dienst nie erreicht hat. */
  readonly status: number

  constructor(message: string, status: number, code: ErrorCode | null, cause?: unknown) {
    super(message, { cause })
    this.name = 'ApiError'
    this.status = status
    this.code = code
  }
}

/** Die Meldung, die einem Eintrag angeheftet wird — nie ein Stacktrace. */
export function messageFromError(cause: unknown): string {
  if (cause instanceof Error && cause.message) return cause.message
  return String(cause)
}

async function errorFromResponse(response: Response): Promise<ApiError> {
  let detail = `Der Dienst antwortete mit HTTP ${response.status}.`
  let code: ErrorCode | null = null
  try {
    const body = (await response.json()) as Partial<ErrorResponse>
    if (typeof body.detail === 'string' && body.detail) detail = body.detail
    if (typeof body.code === 'string') code = body.code as ErrorCode
  } catch {
    // Kein JSON im Rumpf. Dann bleibt es bei der Meldung aus dem Statuscode.
  }
  return new ApiError(detail, response.status, code)
}

async function request(path: string, init: RequestInit): Promise<Response> {
  let response: Response
  try {
    response = await fetch(`${API_BASE}${path}`, init)
  } catch (cause) {
    // Ein Abbruch ist kein Ausfall des Dienstes. Er kommt vom Nutzer und geht
    // unveraendert an den Aufrufer zurueck, damit die Warteschlange ihn von
    // einem echten Fehlschlag unterscheiden kann.
    if (init.signal?.aborted) throw cause
    throw new ApiError('Der Dienst ist nicht erreichbar.', 0, null, cause)
  }
  if (!response.ok) throw await errorFromResponse(response)
  return response
}

/** Was dieser Dienst kann. Das Frontend bietet nichts an, was ohnehin scheitern wuerde. */
export async function fetchCapabilities(): Promise<CapabilitiesResponse> {
  const response = await request('/capabilities', {
    headers: { Accept: 'application/json' },
  })
  return (await response.json()) as CapabilitiesResponse
}

/**
 * Der Stand des laufenden Dienstes. Die Oberfläche zeigt daraus nur die Version.
 *
 * `version` ist eine undurchsichtige Zeichenkette: aus dem Git-Tag gebaut etwas
 * wie `v0.1.0-12-ga22a6c5`, ohne Git-Verlauf die nackte Nummer aus
 * `backend/app/__init__.py`. Wer sie anzeigt, gibt sie unverändert weiter.
 */
export async function fetchHealth(): Promise<HealthResponse> {
  const response = await request('/health', {
    headers: { Accept: 'application/json' },
  })
  return (await response.json()) as HealthResponse
}

/**
 * Eine Datei nach Markdown.
 *
 * `ocr: null` heisst „nichts mitschicken": Dann gilt die Einstellung des Dienstes
 * aus `KAIMARKIT_OCR_ENABLED`.
 *
 * Ueber `signal` bricht der Aufrufer das Warten ab. Der Aufruf endet dann mit dem
 * `AbortError` des Browsers, nicht mit einem `ApiError` — abgebrochen ist nicht
 * gescheitert.
 */
export async function convertFile(
  file: File,
  options: ConvertOptions,
  signal?: AbortSignal,
): Promise<ConversionEntry> {
  const body = new FormData()
  body.append('file', file, file.name)
  body.append('engine', options.engine)
  if (options.ocr !== null) body.append('ocr', String(options.ocr))

  const response = await request('/convert', {
    method: 'POST',
    headers: { Accept: 'application/json' },
    body,
    signal,
  })
  return (await response.json()) as ConversionEntry
}
