// @vitest-environment jsdom

/**
 * Die Warteschlange gegen einen Attrappen-Client.
 *
 * Drei Zusagen werden geprueft, und jede faellt ohne Test erst im Betrieb auf:
 * die Grenze von zwei gleichzeitigen Laeufen, dass ein Fehlschlag die uebrigen
 * Dateien nicht mitnimmt, und dass ein Abbruch den Signalgeber der Zeile
 * tatsaechlich erreicht.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { ApiError } from '../api'
import { createConversionQueue, rememberEngine, type ConvertFn } from './useConversion'
import type { ConversionEntry } from '../types'

/** Laesst alle offenen Microtasks durchlaufen. */
const tick = () => new Promise((resolve) => setTimeout(resolve, 0))

function fileNamed(name: string): File {
  return new File(['Beispielinhalt'], name)
}

function okEntry(filename: string): ConversionEntry {
  return {
    filename,
    status: 'ok',
    markdown: `# ${filename}`,
    engine: 'markitdown',
    warnings: [],
    duration_ms: 12,
    error: null,
  }
}

interface Pending {
  filename: string
  resolve: (entry: ConversionEntry) => void
  reject: (cause: unknown) => void
  signal: AbortSignal
}

/**
 * Ein Client, der nichts von allein beantwortet. Der Test entscheidet, wann eine
 * Konvertierung endet — nur so laesst sich messen, wie viele gleichzeitig laufen.
 */
function stubClient() {
  const pending: Pending[] = []
  let active = 0
  let peak = 0

  const convert: ConvertFn = (file, _options, signal) =>
    new Promise<ConversionEntry>((resolve, reject) => {
      active += 1
      peak = Math.max(peak, active)
      const item: Pending = { filename: file.name, resolve, reject, signal }
      pending.push(item)
      // Wie `fetch`: Ein Abbruch beendet den Aufruf mit einem `AbortError`.
      signal.addEventListener('abort', () => {
        const index = pending.indexOf(item)
        if (index >= 0) {
          pending.splice(index, 1)
          active -= 1
        }
        reject(new DOMException('Abgebrochen', 'AbortError'))
      })
    })

  function next(): Pending {
    const item = pending.shift()
    if (!item) throw new Error('Es laeuft nichts, was beantwortet werden koennte.')
    active -= 1
    return item
  }

  return {
    convert,
    /** Wie viele Laeufe gerade auf ihre Antwort warten. */
    count: () => pending.length,
    /** Die groesste Zahl gleichzeitiger Laeufe seit Beginn. */
    peak: () => peak,
    /** Der Signalgeber, den die Zeile dieser Datei mitbekommen hat. */
    signalFor(filename: string): AbortSignal {
      const item = pending.find((candidate) => candidate.filename === filename)
      if (!item) throw new Error(`${filename} laeuft nicht.`)
      return item.signal
    },
    succeedNext(): string {
      const item = next()
      item.resolve(okEntry(item.filename))
      return item.filename
    },
    failNext(detail: string): string {
      const item = next()
      item.reject(new ApiError(detail, 500, 'conversion_failed'))
      return item.filename
    },
  }
}

describe('useConversion', () => {
  it('laesst hoechstens zwei Dateien gleichzeitig laufen', async () => {
    const client = stubClient()
    const queue = createConversionQueue({ convert: client.convert })

    queue.enqueue(['a.pdf', 'b.pdf', 'c.pdf', 'd.pdf', 'e.pdf'].map(fileNamed))

    expect(client.count()).toBe(2)
    expect(queue.entries.value.filter((entry) => entry.status === 'running')).toHaveLength(2)
    expect(queue.entries.value.filter((entry) => entry.status === 'queued')).toHaveLength(3)

    while (client.count() > 0) {
      client.succeedNext()
      await tick()
    }

    expect(client.peak()).toBe(2)
    expect(queue.entries.value.map((entry) => entry.status)).toEqual([
      'ok',
      'ok',
      'ok',
      'ok',
      'ok',
    ])
    expect(queue.busy.value).toBe(false)
  })

  it('haelt einen Fehlschlag an seiner Zeile fest und arbeitet die uebrigen ab', async () => {
    const client = stubClient()
    const queue = createConversionQueue({ convert: client.convert })

    queue.enqueue(['a.pdf', 'b.pdf', 'c.pdf', 'd.pdf', 'e.pdf'].map(fileNamed))

    client.failNext('Die Engine scheiterte an dieser Datei.')
    await tick()

    expect(queue.entries.value[0]!.status).toBe('failed')
    expect(queue.entries.value[0]!.error).toBe('Die Engine scheiterte an dieser Datei.')
    expect(queue.entries.value[0]!.markdown).toBeNull()
    // Es ist sofort nachgerueckt.
    expect(client.count()).toBe(2)

    while (client.count() > 0) {
      client.succeedNext()
      await tick()
    }

    expect(client.peak()).toBe(2)
    expect(queue.entries.value.filter((entry) => entry.status === 'ok')).toHaveLength(4)
    expect(queue.entries.value.filter((entry) => entry.status === 'failed')).toHaveLength(1)
    expect(queue.entries.value[1]!.markdown).toBe('# b.pdf')
  })

  it('bricht eine laufende Zeile ab, ohne sie als Fehlschlag zu zaehlen', async () => {
    const client = stubClient()
    const queue = createConversionQueue({ convert: client.convert })

    queue.enqueue(['a.pdf', 'b.pdf', 'c.pdf'].map(fileNamed))
    const signal = client.signalFor('a.pdf')
    expect(signal.aborted).toBe(false)

    queue.abort(queue.entries.value[0]!.id)
    await tick()

    // Der Abbruch erreicht den Signalgeber der Anfrage und nicht nur die Anzeige.
    expect(signal.aborted).toBe(true)
    expect(queue.entries.value[0]!.status).toBe('aborted')
    expect(queue.entries.value[0]!.error).toBeNull()
    // Ein Abbruch ist kein Fehlschlag.
    expect(queue.entries.value.filter((entry) => entry.status === 'failed')).toHaveLength(0)
    // Der Platz ist frei geworden, c.pdf ist nachgerueckt.
    expect(client.count()).toBe(2)

    while (client.count() > 0) {
      client.succeedNext()
      await tick()
    }

    expect(queue.entries.value.map((entry) => entry.status)).toEqual(['aborted', 'ok', 'ok'])
    expect(queue.busy.value).toBe(false)
  })

  it('bricht auch ab, wer eine laufende Zeile entfernt', async () => {
    const client = stubClient()
    const queue = createConversionQueue({ convert: client.convert })

    queue.enqueue(['a.pdf', 'b.pdf'].map(fileNamed))
    const signal = client.signalFor('a.pdf')

    queue.remove(queue.entries.value[0]!.id)
    await tick()

    expect(signal.aborted).toBe(true)
    expect(queue.entries.value.map((entry) => entry.filename)).toEqual(['b.pdf'])
  })

  it('laesst eine wartende Zeile unberuehrt', async () => {
    const client = stubClient()
    const queue = createConversionQueue({ convert: client.convert })

    queue.enqueue(['a.pdf', 'b.pdf', 'c.pdf'].map(fileNamed))
    // c.pdf wartet noch; ein Abbruch hat dort nichts zu beenden.
    queue.abort(queue.entries.value[2]!.id)
    await tick()

    expect(queue.entries.value[2]!.status).toBe('queued')
    expect(client.count()).toBe(2)
  })

  it('schickt Engine und OCR mit, aber ocr nur, wenn es gesetzt ist', async () => {
    const seen: { engine: string; ocr: boolean | null }[] = []
    const convert: ConvertFn = (file, options) => {
      seen.push({ ...options })
      return Promise.resolve(okEntry(file.name))
    }
    const queue = createConversionQueue({ convert })

    queue.options.value = { engine: 'docling', ocr: true }
    queue.enqueue([fileNamed('a.pdf')])
    await tick()

    expect(seen).toEqual([{ engine: 'docling', ocr: true }])
  })

  describe('die gemerkte Engine', () => {
    beforeEach(() => {
      localStorage.clear()
    })

    afterEach(() => {
      vi.restoreAllMocks()
    })

    it('waehlt markitdown, wenn nichts gemerkt ist', () => {
      const queue = createConversionQueue()
      expect(queue.options.value).toEqual({ engine: 'markitdown', ocr: null })
    })

    it('schreibt die Wahl unter kaimarkit.engine und liest sie in eine neue Warteschlange zurueck', async () => {
      rememberEngine('docling')
      expect(localStorage.getItem('kaimarkit.engine')).toBe('docling')
      expect(createConversionQueue().options.value.engine).toBe('docling')

      // Auch die geteilte Warteschlange der Anwendung liest den Wert beim Start.
      vi.resetModules()
      const fresh = await import('./useConversion')
      expect(fresh.useConversion().options.value.engine).toBe('docling')
    })

    it('bleibt bei markitdown und wirft nicht, wenn der Speicher wirft', () => {
      vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
        throw new Error('Site-Daten blockiert')
      })
      vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
        throw new Error('Site-Daten blockiert')
      })
      expect(createConversionQueue().options.value.engine).toBe('markitdown')
      expect(() => rememberEngine('docling')).not.toThrow()
    })
  })
})
