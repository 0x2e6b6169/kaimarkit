/**
 * Feste Antworten des Mock-Servers, nach `contracts/api.md`.
 *
 * Die Werte sind erfunden, aber vollstaendig: Wer hier ein Feld weglaesst,
 * verschiebt den Fehler in das Frontend, das dann gegen eine Schnittstelle
 * entwickelt wird, die es so nie gibt.
 */

import type { CapabilitiesResponse, ConversionEntry, ErrorCode } from '../types.ts'

export const capabilities: CapabilitiesResponse = {
  formats: {
    '.pdf': ['docling', 'markitdown'],
    '.docx': ['markitdown', 'docling', 'pandoc'],
    '.epub': ['pandoc', 'markitdown'],
    '.pptx': ['markitdown'],
    '.html': ['markitdown', 'pandoc'],
  },
  engines: {
    markitdown: 'ready',
    docling: 'warming',
    pandoc: 'ready',
  },
  limits: {
    max_file_size_mb: 50,
    max_files: 20,
    conversion_timeout_s: 120,
  },
  ocr_available: true,
  default_engine: 'auto',
}

export const version = '0.1.0-mock'

/**
 * Welchen der drei Faelle eine Anfrage bekommt, entscheidet der Dateiname.
 * So laesst sich jeder Fall im Browser ausloesen, ohne den Mock umzustellen.
 */
export type MockCase = 'ok' | 'warnings' | 'failure'

export function caseForFilename(filename: string): MockCase {
  const name = filename.toLowerCase()
  if (name.includes('fehler')) return 'failure'
  if (name.includes('warnung')) return 'warnings'
  return 'ok'
}

const sampleMarkdown = (filename: string) => `# ${filename}

Dieser Text kommt aus dem Mock-Server, nicht aus einer Engine.

## Abschnitt

Ein Absatz mit **fetter** und *kursiver* Schrift, dazu eine Liste:

- erster Punkt
- zweiter Punkt
- dritter Punkt

| Spalte | Wert |
|---|---|
| Seiten | 12 |
| Sprache | de |
`

const mockWarnings = [
  'Seite 4 enthielt ein Bild, das durch einen Platzhalter ersetzt wurde.',
  'Zwei Tabellen wurden vereinfacht, weil sie verbundene Zellen enthielten.',
]

/**
 * Meldung des dritten Falls. `/api/convert` antwortet auf einen Fehlschlag der
 * Engine mit einem Fehlercode, nicht mit einem Eintrag `status: "failed"` —
 * den gibt es nur im Stapel. Siehe `contracts/api.md`.
 */
export const failureDetail =
  'Die Engine konnte die Datei nicht lesen (beschaedigtes Archiv).'

/** Eintrag fuer die beiden gelungenen Faelle: mit und ohne Warnungen. */
export function entryFor(
  filename: string,
  engine: string,
  durationMs: number,
): ConversionEntry {
  const kind = caseForFilename(filename)
  return {
    filename,
    status: 'ok',
    markdown: sampleMarkdown(filename),
    engine,
    warnings: kind === 'warnings' ? mockWarnings : [],
    duration_ms: durationMs,
    error: null,
  }
}

export const errorStatus: Record<ErrorCode, number> = {
  file_too_large: 413,
  too_many_files: 413,
  unsupported_format: 415,
  engine_unsuitable: 400,
  engine_unavailable: 400,
  conversion_failed: 500,
  conversion_timeout: 504,
}
