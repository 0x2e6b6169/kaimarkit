// @vitest-environment jsdom

/**
 * Die Warteschlange als Liste — Reihenfolge, Ansage, Weiterreichen.
 *
 * Die Ansage im `aria-live`-Bereich ist der Teil, den man auf dem Bildschirm
 * nicht sieht und deshalb ohne Test verliert.
 */

import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import FileDropZone from './FileDropZone.vue'
import FileQueue from './FileQueue.vue'
import { createConversionQueue, type ConvertFn, type QueueEntry } from '../composables/useConversion'
import type { ConversionEntry } from '../types'

function entry(id: number, filename: string, overrides: Partial<QueueEntry> = {}): QueueEntry {
  return {
    id,
    filename,
    status: 'queued',
    markdown: null,
    engine: null,
    warnings: [],
    error: null,
    durationMs: null,
    ...overrides,
  }
}

/** Fuenf Dateien, wie sie unmittelbar nach dem Ablegen aussehen. */
function fresh(): QueueEntry[] {
  return ['a.pdf', 'b.pdf', 'c.pdf', 'd.pdf', 'e.pdf'].map((name, index) =>
    entry(index + 1, name, { status: index < 2 ? 'running' : 'queued' }),
  )
}

const live = '[aria-live="polite"]'

describe('FileQueue', () => {
  it('sagt, dass noch nichts da ist', () => {
    const wrapper = mount(FileQueue, { props: { entries: [] } })

    expect(wrapper.text()).toContain('Noch keine Dateien')
    expect(wrapper.find('ul').exists()).toBe(false)
  })

  it('zeigt jede Datei sofort als Zeile, in der Reihenfolge des Hinzufuegens', () => {
    const wrapper = mount(FileQueue, { props: { entries: fresh() } })

    const rows = wrapper.findAll('li')
    expect(rows).toHaveLength(5)
    const expected = ['a.pdf', 'b.pdf', 'c.pdf', 'd.pdf', 'e.pdf']
    rows.forEach((row, index) => expect(row.text()).toContain(expected[index]!))
    // Zwei laufen, drei warten — beides steht als Wort an der Zeile.
    expect(wrapper.text().match(/läuft/g)).toHaveLength(2)
    expect(wrapper.text().match(/wartet/g)).toHaveLength(3)
  })

  it('haelt einen leeren Ansagebereich bereit, bevor es etwas anzusagen gibt', () => {
    const wrapper = mount(FileQueue, { props: { entries: fresh() } })

    expect(wrapper.get(live).text()).toBe('')
  })

  it('sagt an, wenn eine Datei fertig ist', async () => {
    const entries = fresh()
    const wrapper = mount(FileQueue, { props: { entries } })

    await wrapper.setProps({
      entries: entries.map((item) =>
        item.id === 1
          ? { ...item, status: 'ok' as const, markdown: '# a', engine: 'markitdown', durationMs: 12 }
          : item,
      ),
    })

    expect(wrapper.get(live).text()).toBe('a.pdf ist fertig.')
  })

  it('nennt in der Ansage die Zahl der Warnungen', async () => {
    const entries = fresh()
    const wrapper = mount(FileQueue, { props: { entries } })

    await wrapper.setProps({
      entries: entries.map((item) =>
        item.id === 2
          ? { ...item, status: 'ok' as const, markdown: '# b', warnings: ['Bild ersetzt.'] }
          : item,
      ),
    })

    expect(wrapper.get(live).text()).toBe('b.pdf ist fertig, mit 1 Warnung.')
  })

  it('sagt einen Fehlschlag samt Meldung an', async () => {
    const entries = fresh()
    const wrapper = mount(FileQueue, { props: { entries } })

    await wrapper.setProps({
      entries: entries.map((item) =>
        item.id === 1
          ? { ...item, status: 'failed' as const, error: 'Die Engine scheiterte an dieser Datei.' }
          : item,
      ),
    })

    expect(wrapper.get(live).text()).toBe(
      'a.pdf ist fehlgeschlagen: Die Engine scheiterte an dieser Datei.',
    )
    expect(wrapper.text()).toContain('Die Engine scheiterte an dieser Datei.')
  })

  it('sagt an, wenn eine wartende Datei startet', async () => {
    const entries = fresh()
    const wrapper = mount(FileQueue, { props: { entries } })

    await wrapper.setProps({
      entries: entries.map((item) =>
        item.id === 3 ? { ...item, status: 'running' as const } : item,
      ),
    })

    expect(wrapper.get(live).text()).toBe('c.pdf wird konvertiert.')
  })

  it('klappt eine Zeile auf und wieder zu', async () => {
    const wrapper = mount(FileQueue, {
      props: { entries: [entry(1, 'a.pdf', { status: 'ok', markdown: '# a' })] },
    })

    const toggle = wrapper.get('[aria-expanded]')
    expect(toggle.attributes('aria-expanded')).toBe('false')

    await toggle.trigger('click')
    expect(wrapper.get('[aria-expanded]').attributes('aria-expanded')).toBe('true')
    expect(wrapper.text()).toContain('Vorschau folgt mit FE-4')

    await wrapper.get('[aria-expanded]').trigger('click')
    expect(wrapper.get('[aria-expanded]').attributes('aria-expanded')).toBe('false')
  })

  it('reicht den Wunsch weiter, eine Zeile zu entfernen', async () => {
    const wrapper = mount(FileQueue, { props: { entries: [entry(9, 'a.pdf')] } })

    const buttons = wrapper.findAll('button')
    await buttons[buttons.length - 1]!.trigger('click')

    expect(wrapper.emitted('remove')).toEqual([[9]])
  })
})

/**
 * Die Pruefung aus dem Ticket, soweit sie sich ohne Browser nachstellen laesst:
 * fuenf Dateien ablegen, Reihenfolge und Status stimmen, die gescheiterte Datei
 * zeigt ihre Meldung.
 *
 * Hier haengen Dropzone und Warteschlange an derselben `useConversion`-Instanz,
 * nur der Client ist eine Attrappe. Was `App.vue` mit FE-7 verdrahtet, ist genau
 * diese Verbindung.
 */
describe('Dropzone und Warteschlange zusammen', () => {
  const tick = () => new Promise((resolve) => setTimeout(resolve, 0))

  function fileNamed(name: string): File {
    return new File(['Beispielinhalt'], name)
  }

  it('nimmt fuenf abgelegte Dateien auf und zeigt jeden Ausgang an seiner Zeile', async () => {
    const pending: {
      filename: string
      resolve: (entry: ConversionEntry) => void
      reject: (cause: unknown) => void
    }[] = []
    const convert: ConvertFn = (file) =>
      new Promise((resolve, reject) => pending.push({ filename: file.name, resolve, reject }))

    const queue = createConversionQueue({ convert })
    const dropzone = mount(FileDropZone, { props: { onFiles: queue.enqueue } })
    const list = mount(FileQueue, { props: { entries: queue.entries.value } })

    await dropzone.get('button').trigger('drop', {
      dataTransfer: { files: ['a.pdf', 'b.pdf', 'c.pdf', 'd.pdf', 'e.pdf'].map(fileNamed) },
    })
    await list.vm.$nextTick()

    const names = ['a.pdf', 'b.pdf', 'c.pdf', 'd.pdf', 'e.pdf']
    expect(list.findAll('li')).toHaveLength(5)
    list.findAll('li').forEach((row, index) => expect(row.text()).toContain(names[index]!))
    // Nur die Liste zaehlen, nicht den Ansagebereich: Der wiederholt dieselben Woerter.
    expect(list.get('ul').text().match(/läuft/g)).toHaveLength(2)
    expect(list.get('ul').text().match(/wartet/g)).toHaveLength(3)

    // Die erste Datei scheitert, die uebrigen gelingen.
    pending.shift()!.reject(new Error('Die Engine scheiterte an dieser Datei.'))
    await tick()
    await list.vm.$nextTick()
    expect(list.get(live).text()).toContain(
      'a.pdf ist fehlgeschlagen: Die Engine scheiterte an dieser Datei.',
    )

    while (pending.length) {
      const item = pending.shift()!
      item.resolve({
        filename: item.filename,
        status: 'ok',
        markdown: `# ${item.filename}`,
        engine: 'markitdown',
        warnings: [],
        duration_ms: 12,
        error: null,
      })
      await tick()
    }
    await list.vm.$nextTick()

    list.findAll('li').forEach((row, index) => expect(row.text()).toContain(names[index]!))
    expect(list.get('ul').text().match(/fertig/g)).toHaveLength(4)
    expect(list.get('li').text()).toContain('fehlgeschlagen')
    expect(list.get('li').text()).toContain('Die Engine scheiterte an dieser Datei.')
    // Die Ansage des Fehlschlags steht noch da, obwohl vier Erfolge folgten.
    expect(list.get(live).text()).toContain('a.pdf ist fehlgeschlagen')
    expect(queue.busy.value).toBe(false)
  })
})
