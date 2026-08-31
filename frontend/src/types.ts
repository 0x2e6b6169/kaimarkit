/**
 * Typen der HTTP-Schnittstelle.
 *
 * Diese Datei, `contracts/api.md` und `backend/app/models.py` beschreiben dieselbe
 * Schnittstelle und werden gemeinsam geaendert. Siehe CLAUDE.md, Konvention 1.
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

export interface ErrorResponse {
  detail: string
  code: ErrorCode
}

/**
 * Ergebnis fuer genau eine Datei.
 *
 * `markdown` und `error` sind immer vorhanden: bei `ok` ist `error` null,
 * bei `failed` `markdown`.
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
 * In `formats` ist die Reihenfolge die Praeferenz: Der erste Eintrag wird bei
 * `engine=auto` genommen. Engines im Zustand `unavailable` erscheinen hier nicht.
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

/** Optionen fuer einen Konvertierungslauf. `engine: 'auto'` folgt der Praeferenz. */
export interface ConvertOptions {
  engine: string
  ocr: boolean | null
}
