/**
 * Die Warteschlange: eine Zeile je Datei, von `queued` bis `ok` oder `failed`.
 *
 * Es laufen hoechstens zwei Konvertierungen gleichzeitig, die uebrigen warten.
 * Das Backend bremst zwar selbst, aber ohne Begrenzung im Frontend saehe der
 * Nutzer zwanzig laufende Zeilen, von denen sich nichts bewegt.
 *
 * Eine Zeile kommt aus einer Datei **oder** aus einer Webadresse. Von da an
 * unterscheiden sie sich in zweierlei: welcher Endpunkt gerufen wird und woher
 * der Name kommt. Eine Datei bringt ihren Namen mit; eine Adresse steht so
 * lange als Name in der Zeile, bis die Antwort einen `filename` aus dem
 * Seitentitel mitbringt. Alles Uebrige — Grenze, Optionen, Abbruch, Archiv —
 * gilt fuer beide gleich.
 *
 * Ein Fehlschlag betrifft nur seine eigene Zeile. Die uebrigen laufen weiter,
 * und die Meldung steht am Eintrag, nicht in der Konsole.
 *
 * ## Die Grenze
 *
 * `limits.max_files` aus `/api/capabilities` begrenzt die Warteschlange als
 * Ganzes — Dateien und Adressen zusammen, nicht je Quelle. Was darueber
 * hinausgeht, kommt gar nicht erst herein und wird in `rejected` gezaehlt; die
 * Oberflaeche sagt es. Der Dienst lehnt einen zu grossen Stapel ohnehin ab, und
 * es ist besser, das vorher zu sagen, als zwanzig Anfragen loszuschicken, von
 * denen die Haelfte scheitert.
 *
 * Kennt niemand eine Grenze — die Faehigkeiten kamen nicht durch —, gilt keine.
 * Eine erfundene Voreinstellung waere schlimmer als keine: Sie wiese Dateien ab,
 * die der Dienst angenommen haette.
 *
 * Wer nicht laenger warten will, bricht eine laufende Zeile ab. Jede laufende
 * Datei hat dafuer ihren eigenen `AbortController`; die Warteschlange ruft
 * `/api/convert` je Datei auf, ein Abbruch beendet also genau eine Anfrage.
 * Danach steht die Zeile auf `aborted` und nicht auf `failed`: Der Nutzer hat
 * entschieden, gescheitert ist nichts.
 *
 * Was der Abbruch beendet, ist allein das Warten des Browsers. Der Dienst
 * wandelt weiter: BE-30 hat gemessen, dass uvicorn die ASGI-Aufgabe beim
 * Verbindungsabbruch nicht abbricht und der Handler erst an der Zeitgrenze
 * endet. Deshalb verspricht die Oberflaeche nicht mehr als „nicht mehr warten".
 *
 * ## Die gemerkte Engine
 *
 * Die zuletzt gewaehlte Engine bleibt im Browser, ueber Sitzungen hinweg
 * (GitHub #3). Der Dienst hat keinen Sitzungszustand und liest kein Cookie;
 * deshalb `localStorage`, ein Schluessel, und nur hier: Wer den Speicher
 * anfasst, tut es ueber `rememberEngine`, und die Warteschlange liest ihn beim
 * Anlegen. Gemerkt wird nur die Engine, nicht der OCR-Schalter. Ohne Eintrag —
 * oder ohne Speicher, etwa im privaten Fenster — gilt `markitdown`.
 */

import { computed, ref, type ComputedRef, type Ref } from 'vue'
import { convertFile, convertUrl, messageFromError } from '../api'
import { useCapabilities } from './useCapabilities'
import type { ConversionEntry, ConvertOptions } from '../types'

/** Hoechstens so viele Dateien laufen gleichzeitig. */
const MAX_PARALLEL = 2

/** Der Schluessel im `localStorage`, unter dem die gewaehlte Engine steht. */
const ENGINE_KEY = 'kaimarkit.engine'

/** Die Engine, wenn nichts gemerkt ist. */
const DEFAULT_ENGINE = 'markitdown'

/**
 * Liest die gemerkte Engine. `localStorage` kann werfen — privates Fenster,
 * blockierte Site-Daten —, und dann gilt die Vorgabe.
 */
function storedEngine(): string {
  try {
    return localStorage.getItem(ENGINE_KEY) || DEFAULT_ENGINE
  } catch {
    return DEFAULT_ENGINE
  }
}

/**
 * Merkt eine Engine fuer den naechsten Besuch. Nur eine Wahl des Nutzers
 * gehoert hierher — der Ruecksprung auf `auto`, wenn eine Engine aus dem
 * Angebot faellt, ueberschreibt den gemerkten Wert nicht.
 */
export function rememberEngine(engine: string): void {
  try {
    localStorage.setItem(ENGINE_KEY, engine)
  } catch {
    // Ohne Speicher gibt es nichts zu merken; die Wahl gilt fuer diese Sitzung.
  }
}

/**
 * Der Lebenslauf einer Zeile. `queued`, `running` und `aborted` gibt es nur im
 * Frontend; `ok` und `failed` sind der `status` aus `contracts/api.md`.
 */
export type QueueStatus = 'queued' | 'running' | 'ok' | 'failed' | 'aborted'

/** Woher eine Zeile kommt. Ausserhalb der Reaktivitaet, siehe `sources`. */
export type QueueSource = { kind: 'file'; file: File } | { kind: 'url'; url: string }

/** Eine Zeile der Warteschlange. */
export interface QueueEntry {
  /** Stabil ueber die Lebensdauer der Zeile, auch wenn zwei Dateien gleich heissen. */
  id: number
  /** Datei oder Webadresse. Nur eine Adresse taugt nicht als Dateiname. */
  source: QueueSource['kind']
  filename: string
  status: QueueStatus
  markdown: string | null
  engine: string | null
  warnings: string[]
  /** Lesbare Meldung bei `failed`, sonst null. */
  error: string | null
  durationMs: number | null
}

/** Die Attrappe im Test setzt hier an. */
export type ConvertFn = (
  file: File,
  options: ConvertOptions,
  signal: AbortSignal,
) => Promise<ConversionEntry>

/** Dasselbe fuer `/api/convert/url`. */
export type ConvertUrlFn = (
  url: string,
  options: ConvertOptions,
  signal: AbortSignal,
) => Promise<ConversionEntry>

export interface ConversionQueue {
  entries: Ref<QueueEntry[]>
  /** Engine und OCR fuer den naechsten Start. FE-5 bindet die Optionen daran. */
  options: Ref<ConvertOptions>
  /** Wahr, solange etwas wartet oder laeuft. */
  busy: ComputedRef<boolean>
  /** Wie viele Eintraege die Warteschlange fasst; null, solange keine Grenze bekannt ist. */
  maxEntries: ComputedRef<number | null>
  /** Wie viele beim letzten Hinzufuegen nicht mehr hineinpassten. */
  rejected: Ref<number>
  enqueue: (files: Iterable<File>) => void
  /** Je Adresse eine Zeile. Leere Zeilen und Schemapruefung macht `UrlInput`. */
  enqueueUrls: (urls: Iterable<string>) => void
  /** Beendet das Warten auf eine laufende Zeile. Wartende und fertige bleiben. */
  abort: (id: number) => void
  remove: (id: number) => void
  clear: () => void
}

/**
 * Baut eine eigene Warteschlange. Die Anwendung nimmt die gemeinsame aus
 * `useConversion()`; eine eigene braucht nur der Test, der einen anderen
 * Client und eine andere Grenze einsetzt.
 */
export function createConversionQueue(
  deps: {
    convert?: ConvertFn
    convertUrl?: ConvertUrlFn
    maxParallel?: number
    /** Die Grenze der Warteschlange. Ohne sie zaehlt `limits.max_files`. */
    maxEntries?: () => number | null
  } = {},
): ConversionQueue {
  const convert = deps.convert ?? convertFile
  const fetchUrl = deps.convertUrl ?? convertUrl
  const maxParallel = deps.maxParallel ?? MAX_PARALLEL
  const limitOf = deps.maxEntries ?? (() => useCapabilities().limits.value?.max_files ?? null)

  const entries = ref<QueueEntry[]>([])
  const options = ref<ConvertOptions>({ engine: storedEngine(), ocr: null })
  const maxEntries = computed(limitOf)
  const rejected = ref(0)

  /**
   * Die Quellen liegen ausserhalb der Reaktivitaet. Ein `File` in einem
   * reaktiven Objekt kaeme als Proxy zurueck, und `FormData.append` will das
   * echte Objekt.
   */
  const sources = new Map<number, QueueSource>()

  /** Einer je laufender Zeile, angelegt beim Start und am Ende wieder entfernt. */
  const controllers = new Map<number, AbortController>()

  let nextId = 1
  let running = 0

  /** Legt eine Zeile an. Den Namen bringt der Aufrufer mit, die Quelle auch. */
  function push(source: QueueSource, filename: string): void {
    const id = nextId++
    sources.set(id, source)
    entries.value.push({
      id,
      source: source.kind,
      filename,
      status: 'queued',
      markdown: null,
      engine: null,
      warnings: [],
      error: null,
      durationMs: null,
    })
  }

  /**
   * Laesst durch, wofuer noch Platz ist, und zaehlt den Rest.
   *
   * Der Platz bemisst sich an der ganzen Warteschlange, nicht am Stapel: Wer
   * fuenfzehn Dateien liegen hat, bringt keine acht Adressen mehr unter.
   */
  function admit<T>(incoming: Iterable<T>): T[] {
    const items = Array.from(incoming)
    const limit = maxEntries.value
    if (limit === null) {
      rejected.value = 0
      return items
    }
    const room = Math.max(0, limit - entries.value.length)
    rejected.value = Math.max(0, items.length - room)
    return items.slice(0, room)
  }

  function enqueue(incoming: Iterable<File>): void {
    for (const file of admit(incoming)) push({ kind: 'file', file }, file.name)
    pump()
  }

  function enqueueUrls(incoming: Iterable<string>): void {
    // Bis eine Antwort da ist, ist die Adresse alles, was die Zeile benennt.
    for (const url of admit(incoming)) push({ kind: 'url', url }, url)
    pump()
  }

  /**
   * Bricht das Warten auf eine laufende Zeile ab.
   *
   * Den Zustand setzt nicht diese Funktion, sondern `run`: Der Aufruf endet erst
   * mit dem naechsten Durchlauf, und bis dahin laeuft die Zeile noch.
   */
  function abort(id: number): void {
    controllers.get(id)?.abort()
  }

  function remove(id: number): void {
    // Sonst laeuft die Anfrage weiter, obwohl niemand mehr auf sie wartet.
    abort(id)
    sources.delete(id)
    const index = entries.value.findIndex((entry) => entry.id === id)
    if (index >= 0) entries.value.splice(index, 1)
  }

  function clear(): void {
    for (const controller of controllers.values()) controller.abort()
    sources.clear()
    entries.value = []
    // Die Meldung ueber Abgewiesenes gilt der geleerten Warteschlange und
    // stimmt fuer die leere nicht mehr.
    rejected.value = 0
  }

  /** Startet so viele wartende Zeilen, wie die Grenze noch zulaesst. */
  function pump(): void {
    while (running < maxParallel) {
      const entry = entries.value.find((candidate) => candidate.status === 'queued')
      if (!entry) return
      entry.status = 'running'
      running += 1
      void run(entry).finally(() => {
        running -= 1
        pump()
      })
    }
  }

  async function run(entry: QueueEntry): Promise<void> {
    const source = sources.get(entry.id)
    if (!source) return
    const controller = new AbortController()
    controllers.set(entry.id, controller)
    try {
      const request = { ...options.value }
      const result =
        source.kind === 'file'
          ? await convert(source.file, request, controller.signal)
          : await fetchUrl(source.url, request, controller.signal)
      // Ein Ergebnis, das nach dem Abbruch noch eintrifft, aendert nichts mehr:
      // Der Nutzer hat schon aufgehoert zu warten.
      if (controller.signal.aborted) {
        entry.status = 'aborted'
        return
      }
      // Erst jetzt hat eine Adresse einen Namen: Der Dienst leitet ihn aus dem
      // Seitentitel ab. Eine Datei behaelt den ihren.
      if (source.kind === 'url' && result.filename) entry.filename = result.filename
      entry.status = result.status
      entry.markdown = result.markdown
      entry.engine = result.engine
      entry.warnings = result.warnings
      entry.durationMs = result.duration_ms
      entry.error = result.error
    } catch (cause) {
      if (controller.signal.aborted) {
        // Kein Fehlschlag und deshalb auch keine Meldung.
        entry.status = 'aborted'
        entry.error = null
      } else {
        entry.status = 'failed'
        entry.error = messageFromError(cause)
      }
    } finally {
      controllers.delete(entry.id)
    }
  }

  const busy = computed(() =>
    entries.value.some((entry) => entry.status === 'queued' || entry.status === 'running'),
  )

  return {
    entries,
    options,
    busy,
    maxEntries,
    rejected,
    enqueue,
    enqueueUrls,
    abort,
    remove,
    clear,
  }
}

/**
 * Die Warteschlange der Anwendung. Alle Komponenten teilen sie sich, deshalb
 * liegt sie im Modul und nicht in einem Aufruf — ohne Pinia und ohne Provide.
 */
const shared = createConversionQueue()

export function useConversion(): ConversionQueue {
  return shared
}
