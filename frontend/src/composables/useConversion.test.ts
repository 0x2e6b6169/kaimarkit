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
import JSZip from 'jszip'
import { ApiError } from '../api'
import { buildArchive, markdownFilename } from '../download'
import {
  createConversionQueue,
  rememberEngine,
  type ConvertFn,
  type ConvertUrlFn,
} from './useConversion'
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

/**
 * Eintraege aus Webadressen. Sie durchlaufen dieselbe Warteschlange wie
 * Dateien; verschieden ist nur, woher sie kommen und woher ihr Name stammt.
 */
describe('useConversion mit Webadressen', () => {
  /** Ein Client fuer `/api/convert/url`, der von Hand beantwortet wird. */
  function stubUrlClient() {
    const pending: { url: string; resolve: (e: ConversionEntry) => void; reject: (c: unknown) => void }[] = []

    const convertUrl: ConvertUrlFn = (url, _options, signal) =>
      new Promise<ConversionEntry>((resolve, reject) => {
        const item = { url, resolve, reject }
        pending.push(item)
        signal.addEventListener('abort', () => {
          const index = pending.indexOf(item)
          if (index >= 0) pending.splice(index, 1)
          reject(new DOMException('Abgebrochen', 'AbortError'))
        })
      })

    return {
      convertUrl,
      seen: () => pending.map((item) => item.url),
      answerNext(entry: ConversionEntry): void {
        pending.shift()?.resolve(entry)
      },
      failNext(cause: unknown): void {
        pending.shift()?.reject(cause)
      },
    }
  }

  it('zeigt die Adresse als Namen und ersetzt sie durch den filename der Antwort', async () => {
    const client = stubUrlClient()
    const queue = createConversionQueue({ convertUrl: client.convertUrl })

    queue.enqueueUrls(['https://example.com/'])
    await tick()

    // Solange keine Antwort da ist, steht die Adresse in der Zeile.
    expect(queue.entries.value[0]!.filename).toBe('https://example.com/')
    expect(queue.entries.value[0]!.source).toBe('url')
    expect(client.seen()).toEqual(['https://example.com/'])

    client.answerNext({ ...okEntry('example-domain.html'), markdown: '# Example Domain' })
    await tick()

    expect(queue.entries.value[0]!.filename).toBe('example-domain.html')
    expect(queue.entries.value[0]!.status).toBe('ok')
    // Und der Download heisst danach so, wie das Ticket es verlangt.
    expect(markdownFilename(queue.entries.value[0]!.filename)).toBe('example-domain.md')
  })

  it('packt zwei Adressen mit gleichem Titel als -2 ins Archiv', async () => {
    const client = stubUrlClient()
    const queue = createConversionQueue({ convertUrl: client.convertUrl })

    queue.enqueueUrls(['https://example.com/', 'https://example.org/'])
    await tick()
    client.answerNext(okEntry('example-domain.html'))
    client.answerNext(okEntry('example-domain.html'))
    await tick()

    const zip = await JSZip.loadAsync(await buildArchive(queue.entries.value))
    expect(Object.keys(zip.files).sort()).toEqual([
      'example-domain-2.md',
      'example-domain.md',
    ])
  })

  it('haelt eine Fehlerantwort als failed mit ihrer Meldung fest', async () => {
    const client = stubUrlClient()
    const queue = createConversionQueue({ convertUrl: client.convertUrl })

    queue.enqueueUrls(['https://example.com/'])
    await tick()
    client.failNext(new ApiError('Die Adresse zeigt nicht ins offene Netz.', 400, 'invalid_url'))
    await tick()

    expect(queue.entries.value[0]!.status).toBe('failed')
    expect(queue.entries.value[0]!.error).toBe('Die Adresse zeigt nicht ins offene Netz.')
    // Ohne Antwort bleibt die Adresse stehen; sonst wuesste niemand, welche Zeile es war.
    expect(queue.entries.value[0]!.filename).toBe('https://example.com/')
  })

  it('bricht eine laufende Adresse ab, ohne sie als Fehlschlag zu zaehlen', async () => {
    const client = stubUrlClient()
    const queue = createConversionQueue({ convertUrl: client.convertUrl })

    queue.enqueueUrls(['https://example.com/'])
    await tick()
    queue.abort(queue.entries.value[0]!.id)
    await tick()

    expect(queue.entries.value[0]!.status).toBe('aborted')
    expect(queue.entries.value[0]!.error).toBeNull()
  })

  it('teilt sich die Grenze und die Optionen mit den Dateien', async () => {
    const files = stubClient()
    const seen: { engine: string; ocr: boolean | null }[] = []
    const convertUrl: ConvertUrlFn = (_url, options) => {
      seen.push({ ...options })
      return new Promise<ConversionEntry>(() => {})
    }
    const queue = createConversionQueue({ convert: files.convert, convertUrl })

    queue.options.value = { engine: 'docling', ocr: true }
    queue.enqueue([fileNamed('a.pdf')])
    queue.enqueueUrls(['https://example.com/', 'https://example.org/'])
    await tick()

    // Zwei gleichzeitig, egal woher sie kommen: die Datei und die erste Adresse.
    expect(files.count()).toBe(1)
    expect(seen).toEqual([{ engine: 'docling', ocr: true }])
    expect(queue.entries.value[2]!.status).toBe('queued')
  })

  it('nimmt eine Adresse aus der Warteschlange und bricht sie dabei ab', async () => {
    const client = stubUrlClient()
    const queue = createConversionQueue({ convertUrl: client.convertUrl })

    queue.enqueueUrls(['https://example.com/'])
    await tick()
    queue.remove(queue.entries.value[0]!.id)
    await tick()

    expect(queue.entries.value).toEqual([])
    expect(client.seen()).toEqual([])
  })
})

/**
 * Die Grenze aus `limits.max_files`. Sie zaehlt die Warteschlange als Ganzes,
 * Dateien und Webadressen zusammen.
 *
 * Der Dienst lehnt einen zu grossen Stapel ohnehin ab. Die Oberflaeche sagt es
 * vorher, statt zwanzig Anfragen loszuschicken, von denen die Haelfte scheitert.
 */
describe('useConversion mit einer Grenze', () => {
  /** Ein Client fuer Adressen, der nie antwortet — hier zaehlt nur, was hineinkommt. */
  const silentUrls: ConvertUrlFn = () => new Promise<ConversionEntry>(() => {})

  function filesNamed(count: number): File[] {
    return Array.from({ length: count }, (_, index) => fileNamed(`datei-${index}.pdf`))
  }

  it('nimmt nur so viele Dateien auf, wie die Grenze zulaesst', () => {
    const client = stubClient()
    const queue = createConversionQueue({ convert: client.convert, maxEntries: () => 20 })

    queue.enqueue(filesNamed(21))

    expect(queue.entries.value).toHaveLength(20)
    expect(queue.rejected.value).toBe(1)
    // Abgewiesen wird das Ende, nicht der Anfang.
    expect(queue.entries.value.at(-1)!.filename).toBe('datei-19.pdf')
  })

  it('zaehlt Dateien und Adressen zusammen gegen dieselbe Grenze', () => {
    const client = stubClient()
    const queue = createConversionQueue({
      convert: client.convert,
      convertUrl: silentUrls,
      maxEntries: () => 20,
    })

    queue.enqueue(filesNamed(15))
    const unplaced = queue.enqueueUrls(
      Array.from({ length: 8 }, (_, index) => `https://example.com/${index}`),
    )

    expect(queue.entries.value).toHaveLength(20)
    expect(queue.entries.value.filter((entry) => entry.source === 'url')).toHaveLength(5)
    expect(queue.rejected.value).toBe(3)

    // Aufgenommen wird der Reihe nach; zurueck kommt darum das Ende des Stapels.
    expect(unplaced).toEqual([
      'https://example.com/5',
      'https://example.com/6',
      'https://example.com/7',
    ])
  })

  it('weist ohne bekannte Grenze nichts ab', () => {
    const client = stubClient()
    const queue = createConversionQueue({
      convert: client.convert,
      convertUrl: silentUrls,
      maxEntries: () => null,
    })

    queue.enqueue(filesNamed(50))
    expect(queue.enqueueUrls(['https://example.com/'])).toEqual([])

    expect(queue.entries.value).toHaveLength(51)
    expect(queue.rejected.value).toBe(0)
  })
})
