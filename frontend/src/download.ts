/**
 * Das Ergebnis herausbekommen: eine Datei als `.md`, der ganze Satz als ZIP.
 *
 * Das Archiv entsteht im Browser. Die Ergebnisse liegen dort bereits — sie fuer
 * das Paket erneut an `/api/convert/batch` zu schicken hiesse, jede Datei ein
 * zweites Mal zu konvertieren.
 *
 * Zwei Regeln kommen aus `backend/app/packaging.py`, damit ein hier gebautes
 * Archiv aussieht wie eines vom Dienst: Der Name im Archiv hat keinen Pfadanteil,
 * und zwei Dateien gleichen Namens ueberschreiben einander nicht — die zweite
 * heisst `bericht-2.md`, die dritte `bericht-3.md`. Gescheiterte Dateien liegen
 * nicht im Archiv, sondern als je eine Zeile in `_errors.txt` darin.
 *
 * Was noch wartet oder laeuft, kommt weder ins Archiv noch in `_errors.txt`:
 * Eine Datei, die noch konvertiert wird, ist nicht gescheitert. Die Oberflaeche
 * sperrt „Alles herunterladen“, solange die Warteschlange arbeitet.
 */

import JSZip from 'jszip'

/**
 * Was dieses Modul von einem Eintrag braucht.
 *
 * Sowohl `QueueEntry` aus `composables/useConversion` als auch `ConversionEntry`
 * aus `types.ts` erfuellen diese Form. Deshalb steht sie hier und wird nicht aus
 * einer der beiden Dateien geliehen.
 */
export interface DownloadEntry {
  filename: string
  status: 'queued' | 'running' | 'ok' | 'failed'
  markdown: string | null
  error: string | null
}

/** Liegt im Archiv, sobald eine Datei gescheitert ist. */
export const ERROR_FILENAME = '_errors.txt'

/** Steht in `_errors.txt`, wenn ein Eintrag keinen Grund nennt. */
export const UNKNOWN_ERROR = 'Unbekannter Fehler'

/** Der Name, unter dem das Archiv im Download landet. */
export const ARCHIVE_FILENAME = 'kaimarkit.zip'

/** Bleibt vom Dateinamen nichts uebrig, heisst er so — wie im Backend. */
const FALLBACK_NAME = 'upload'

/** Steuerzeichen haben in einem Dateinamen nichts zu suchen. */
const CONTROL_CHARS = /[\u0000-\u001f\u007f]/g

/** Laengste Dateinamen der gaengigen Dateisysteme. */
const MAX_NAME_LENGTH = 255

/** Legt einen Puffer als Datei ab. Der Test setzt hier eine Attrappe ein. */
export type SaveFn = (blob: Blob, filename: string) => void

/**
 * Behaelt vom Dateinamen nur den Namensteil.
 *
 * Der Name kommt aus einer Datei, die der Nutzer ausgewaehlt hat, und wandert in
 * ein Archiv. Ein entpacktes `../../etc/passwd` waere ein Einbruch, also bleibt
 * uebrig, was hinter dem letzten Trennzeichen steht.
 */
export function sanitizeFilename(name: string | null | undefined): string {
  if (!name) return FALLBACK_NAME
  const bare = name.replace(/\\/g, '/').split('/').pop() ?? ''
  const cleaned = bare.replace(CONTROL_CHARS, '').trim()
  if (!cleaned || cleaned === '.' || cleaned === '..') return FALLBACK_NAME
  // Von vorn kuerzen, damit die Endung erhalten bleibt.
  return cleaned.slice(-MAX_NAME_LENGTH)
}

/** Der blanke Name mit der Endung `.md`: aus `bericht.pdf` wird `bericht.md`. */
export function markdownFilename(filename: string | null | undefined): string {
  const name = sanitizeFilename(filename)
  const dot = name.lastIndexOf('.')
  const stem = dot > 0 ? name.slice(0, dot) : name
  return `${stem}.md`
}

/** Haengt `-2`, `-3` an, bis der Name im Archiv noch frei ist. */
function unique(name: string, taken: Set<string>): string {
  let candidate = name
  if (taken.has(candidate)) {
    const dot = name.lastIndexOf('.')
    const stem = dot > 0 ? name.slice(0, dot) : name
    const suffix = dot > 0 ? name.slice(dot) : ''
    let counter = 2
    while (taken.has(`${stem}-${counter}${suffix}`)) counter += 1
    candidate = `${stem}-${counter}${suffix}`
  }
  taken.add(candidate)
  return candidate
}

/** Wahr, wenn der Eintrag ein Ergebnis hat, das sich herunterladen laesst. */
export function hasResult(entry: DownloadEntry): boolean {
  return entry.status === 'ok' && entry.markdown !== null
}

/**
 * Packt die gelungenen Ergebnisse und schreibt die gescheiterten in eine Liste.
 *
 * Zurueck kommt das fertige Archiv. Es wird auch dann gebaut, wenn jede Datei
 * scheiterte — dann enthaelt es allein `_errors.txt`.
 */
export async function buildArchive(entries: readonly DownloadEntry[]): Promise<Blob> {
  const zip = new JSZip()
  const taken = new Set<string>()
  const errors: string[] = []

  for (const entry of entries) {
    if (hasResult(entry)) {
      zip.file(unique(markdownFilename(entry.filename), taken), entry.markdown ?? '')
    } else if (entry.status === 'failed') {
      errors.push(`${sanitizeFilename(entry.filename)}: ${entry.error || UNKNOWN_ERROR}`)
    }
  }
  if (errors.length > 0) zip.file(ERROR_FILENAME, `${errors.join('\n')}\n`)

  // Ueber `arraybuffer` statt direkt nach `blob`: So haengt das Paket nicht an
  // JSZips Erkennung der Blob-Unterstuetzung und laesst sich auch im Test lesen,
  // der ohne Browser laeuft.
  const bytes = await zip.generateAsync({ type: 'arraybuffer', compression: 'DEFLATE' })
  return new Blob([bytes], { type: 'application/zip' })
}

/**
 * Legt einen Puffer als Datei im Browser ab.
 *
 * Der Anker haengt kurz im Dokument, weil Firefox einen Klick auf ein Element
 * ausserhalb des Baums ignoriert. Die Objekt-URL wird danach wieder freigegeben,
 * sonst behaelt der Browser das Ergebnis bis zum Neuladen im Speicher.
 */
export function saveBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob)
  try {
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = filename
    anchor.rel = 'noopener'
    document.body.appendChild(anchor)
    anchor.click()
    anchor.remove()
  } finally {
    URL.revokeObjectURL(url)
  }
}

/** Ein einzelnes Ergebnis als `.md`. */
export function downloadMarkdown(entry: DownloadEntry, save: SaveFn = saveBlob): void {
  if (!hasResult(entry)) {
    throw new Error(`Fuer ${sanitizeFilename(entry.filename)} gibt es kein Ergebnis.`)
  }
  const blob = new Blob([entry.markdown ?? ''], { type: 'text/markdown;charset=utf-8' })
  save(blob, markdownFilename(entry.filename))
}

/** Alles herunterladen: ein ZIP aus allen fertigen Eintraegen. */
export async function downloadArchive(
  entries: readonly DownloadEntry[],
  filename: string = ARCHIVE_FILENAME,
  save: SaveFn = saveBlob,
): Promise<void> {
  save(await buildArchive(entries), filename)
}
