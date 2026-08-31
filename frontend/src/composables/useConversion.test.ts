/**
 * Die Warteschlange gegen einen Attrappen-Client.
 *
 * Zwei Zusagen werden geprueft, und beide fallen ohne Test erst im Betrieb auf:
 * die Grenze von zwei gleichzeitigen Laeufen und dass ein Fehlschlag die
 * uebrigen Dateien nicht mitnimmt.
 */

import { describe, expect, it } from 'vitest'
import { ApiError } from '../api'
import { createConversionQueue, type ConvertFn } from './useConversion'
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
}

/**
 * Ein Client, der nichts von allein beantwortet. Der Test entscheidet, wann eine
 * Konvertierung endet — nur so laesst sich messen, wie viele gleichzeitig laufen.
 */
function stubClient() {
  const pending: Pending[] = []
  let active = 0
  let peak = 0

  const convert: ConvertFn = (file) =>
    new Promise<ConversionEntry>((resolve, reject) => {
      active += 1
      peak = Math.max(peak, active)
      pending.push({ filename: file.name, resolve, reject })
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
})
