/**
 * Die Warteschlange: eine Zeile je Datei, von `queued` bis `ok` oder `failed`.
 *
 * Es laufen hoechstens zwei Konvertierungen gleichzeitig, die uebrigen warten.
 * Das Backend bremst zwar selbst, aber ohne Begrenzung im Frontend saehe der
 * Nutzer zwanzig laufende Zeilen, von denen sich nichts bewegt.
 *
 * Ein Fehlschlag betrifft nur seine eigene Zeile. Die uebrigen laufen weiter,
 * und die Meldung steht am Eintrag, nicht in der Konsole.
 */

import { computed, ref, type ComputedRef, type Ref } from 'vue'
import { convertFile, messageFromError } from '../api'
import type { ConversionEntry, ConvertOptions } from '../types'

/** Hoechstens so viele Dateien laufen gleichzeitig. */
const MAX_PARALLEL = 2

/**
 * Der Lebenslauf einer Zeile. `queued` und `running` gibt es nur im Frontend;
 * `ok` und `failed` sind der `status` aus `contracts/api.md`.
 */
export type QueueStatus = 'queued' | 'running' | 'ok' | 'failed'

/** Eine Zeile der Warteschlange. */
export interface QueueEntry {
  /** Stabil ueber die Lebensdauer der Zeile, auch wenn zwei Dateien gleich heissen. */
  id: number
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
export type ConvertFn = (file: File, options: ConvertOptions) => Promise<ConversionEntry>

export interface ConversionQueue {
  entries: Ref<QueueEntry[]>
  /** Engine und OCR fuer den naechsten Start. FE-5 bindet die Optionen daran. */
  options: Ref<ConvertOptions>
  /** Wahr, solange etwas wartet oder laeuft. */
  busy: ComputedRef<boolean>
  enqueue: (files: Iterable<File>) => void
  remove: (id: number) => void
  clear: () => void
}

/**
 * Baut eine eigene Warteschlange. Die Anwendung nimmt die gemeinsame aus
 * `useConversion()`; eine eigene braucht nur der Test, der einen anderen
 * Client und eine andere Grenze einsetzt.
 */
export function createConversionQueue(
  deps: { convert?: ConvertFn; maxParallel?: number } = {},
): ConversionQueue {
  const convert = deps.convert ?? convertFile
  const maxParallel = deps.maxParallel ?? MAX_PARALLEL

  const entries = ref<QueueEntry[]>([])
  const options = ref<ConvertOptions>({ engine: 'auto', ocr: null })

  /**
   * Die Dateien liegen ausserhalb der Reaktivitaet. Ein `File` in einem
   * reaktiven Objekt kaeme als Proxy zurueck, und `FormData.append` will das
   * echte Objekt.
   */
  const files = new Map<number, File>()
  let nextId = 1
  let running = 0

  function enqueue(incoming: Iterable<File>): void {
    for (const file of incoming) {
      const id = nextId++
      files.set(id, file)
      entries.value.push({
        id,
        filename: file.name,
        status: 'queued',
        markdown: null,
        engine: null,
        warnings: [],
        error: null,
        durationMs: null,
      })
    }
    pump()
  }

  function remove(id: number): void {
    files.delete(id)
    const index = entries.value.findIndex((entry) => entry.id === id)
    if (index >= 0) entries.value.splice(index, 1)
  }

  function clear(): void {
    // Was schon laeuft, laeuft zu Ende; sein Ergebnis findet keine Zeile mehr
    // und verfaellt.
    files.clear()
    entries.value = []
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
    const file = files.get(entry.id)
    if (!file) return
    try {
      const result = await convert(file, { ...options.value })
      entry.status = result.status
      entry.markdown = result.markdown
      entry.engine = result.engine
      entry.warnings = result.warnings
      entry.durationMs = result.duration_ms
      entry.error = result.error
    } catch (cause) {
      entry.status = 'failed'
      entry.error = messageFromError(cause)
    }
  }

  const busy = computed(() =>
    entries.value.some((entry) => entry.status === 'queued' || entry.status === 'running'),
  )

  return { entries, options, busy, enqueue, remove, clear }
}

/**
 * Die Warteschlange der Anwendung. Alle Komponenten teilen sie sich, deshalb
 * liegt sie im Modul und nicht in einem Aufruf — ohne Pinia und ohne Provide.
 */
const shared = createConversionQueue()

export function useConversion(): ConversionQueue {
  return shared
}
