/**
 * Typen der HTTP-Schnittstelle.
 *
 * Diese Datei, `contracts/api.md` und `backend/app/models.py` beschreiben dieselbe
 * Schnittstelle und werden gemeinsam geändert. Siehe CLAUDE.md, Konvention 1.
 */

export type ConversionStatus = 'ok' | 'failed'

export type EngineState = 'ready' | 'warming' | 'unavailable'

export type ErrorCode =
  | 'file_too_large'
  | 'too_many_files'
  | 'unsupported_format'
  | 'engine_unsuitable'
  | 'engine_unavailable'
  | 'conversion_failed'
  | 'conversion_timeout'
  | 'invalid_url'

export interface ErrorResponse {
  detail: string
  code: ErrorCode
}

/**
 * Rumpf von `POST /api/convert/url`. `engine` und `ocr` bedeuten dasselbe wie
 * die Formularfelder von `/api/convert`; fehlt `engine`, gilt `auto`.
 */
export interface UrlConvertRequest {
  url: string
  engine?: string
  ocr?: boolean | null
}

/**
 * Ergebnis für genau eine Datei.
 *
 * `markdown` und `error` sind immer vorhanden: bei `ok` ist `error` null,
 * bei `failed` `markdown`.
 *
 * In `engine` steht neben den drei wählbaren Engines auch `passthrough`:
 * Markdown wird durchgereicht, nicht gewandelt. In `CapabilitiesResponse.engines`
 * fehlt der Name dagegen — dort steht, wozwischen sich wählen lässt.
 */
export interface ConversionEntry {
  filename: string
  status: ConversionStatus
  markdown: string | null
  engine: string | null
  warnings: string[]
  duration_ms: number
  error: string | null
}

export interface BatchResponse {
  entries: ConversionEntry[]
  total: number
  succeeded: number
  failed: number
}

export interface Limits {
  max_file_size_mb: number
  max_files: number
  conversion_timeout_s: number
}

/**
 * In `formats` ist die Reihenfolge die Präferenz: Der erste Eintrag wird bei
 * `engine=auto` genommen. Engines im Zustand `unavailable` erscheinen hier nicht.
 *
 * `engines` nennt nur die wählbaren Engines. `formats` führt `.md` mit
 * `passthrough`, und dieser Name fehlt in `engines` — dort gibt es nichts zu
 * wählen. Die Auswahl bietet deshalb nur an, was in `engines` steht.
 */
export interface CapabilitiesResponse {
  formats: Record<string, string[]>
  engines: Record<string, EngineState>
  limits: Limits
  ocr_available: boolean
  default_engine: string
}

export interface HealthResponse {
  status: 'ok'
  version: string
}

/** Optionen für einen Konvertierungslauf. `engine: 'auto'` folgt der Präferenz. */
export interface ConvertOptions {
  engine: string
  ocr: boolean | null
}
