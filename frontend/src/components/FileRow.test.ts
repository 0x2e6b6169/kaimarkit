// @vitest-environment jsdom

/**
 * Was eine Zeile ueber ihren Eintrag verraet.
 *
 * Geprueft wird vor allem, was ohne Test still verschwindet: das Wort neben dem
 * Symbol, die Warnungen an der Zeile und die Meldung einer gescheiterten Datei.
 */

import { mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'
import FileRow from './FileRow.vue'
import type { QueueEntry } from '../composables/useConversion'

// Nur das Ablegen der Datei ist attrappiert; `hasResult` bleibt echt, denn genau
// daran haengt, ob der Knopf ueberhaupt dasteht.
const downloads = vi.hoisted(() => ({ downloadMarkdown: vi.fn() }))
vi.mock('../download', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../download')>()),
  downloadMarkdown: downloads.downloadMarkdown,
}))

function entry(overrides: Partial<QueueEntry> = {}): QueueEntry {
  return {
    id: 1,
    filename: 'bericht.pdf',
    status: 'queued',
    markdown: null,
    engine: null,
    warnings: [],
    error: null,
    durationMs: null,
    ...overrides,
  }
}

describe('FileRow', () => {
  afterEach(() => {
    vi.useRealTimers()
  })

  it('nennt jeden Zustand als Wort, nicht nur als Farbe', () => {
    const cases: [QueueEntry['status'], string][] = [
      ['queued', 'wartet'],
      ['running', 'läuft'],
      ['ok', 'fertig'],
      ['failed', 'fehlgeschlagen'],
    ]

    for (const [status, label] of cases) {
      const wrapper = mount(FileRow, { props: { entry: entry({ status }) } })
      expect(wrapper.text()).toContain(label)
      // Das Symbol steht daneben und bleibt fuer Screenreader stumm.
      expect(wrapper.get('[aria-hidden="true"]').text()).not.toBe('')
    }
  })

  it('zeigt Name, Engine und Dauer', () => {
    const wrapper = mount(FileRow, {
      props: { entry: entry({ status: 'ok', markdown: '# a', engine: 'docling', durationMs: 412 }) },
    })

    expect(wrapper.text()).toContain('bericht.pdf')
    expect(wrapper.text()).toContain('docling')
    expect(wrapper.text()).toContain('0,41 s')
    // Rohe Millisekunden muss niemand im Kopf umrechnen.
    expect(wrapper.text()).not.toContain('412 ms')
  })

  it('schreibt die Gesamtdauer wie den laufenden Zaehler', () => {
    const cases: [number, string][] = [
      [326_062, '5:26'],
      [103_500, '1:43'],
      [1_000, '0:01'],
    ]

    for (const [durationMs, shown] of cases) {
      const wrapper = mount(FileRow, {
        props: { entry: entry({ status: 'ok', markdown: '# a', engine: 'docling', durationMs }) },
      })
      expect(wrapper.text()).toContain(`docling · ${shown}`)
      wrapper.unmount()
    }
  })

  it('laesst einen kurzen Lauf nicht als 0:00 verschwinden', () => {
    // markitdown wandelt eine Datei in Hundertstelsekunden um; das ist hier der
    // haeufige Fall, nicht der Sonderfall.
    const cases: [number, string][] = [
      [35, '0,04 s'],
      [300, '0,3 s'],
      [0, '0 s'],
    ]

    for (const [durationMs, shown] of cases) {
      const wrapper = mount(FileRow, {
        props: { entry: entry({ status: 'ok', markdown: '# a', engine: 'markitdown', durationMs }) },
      })
      expect(wrapper.text()).toContain(`markitdown · ${shown}`)
      expect(wrapper.text()).not.toContain('0:00')
      wrapper.unmount()
    }
  })

  it('stellt Warnungen an die Zeile', () => {
    const wrapper = mount(FileRow, {
      props: {
        entry: entry({
          status: 'ok',
          markdown: '# a',
          warnings: ['Seite 4 enthielt ein Bild, das durch einen Platzhalter ersetzt wurde.'],
        }),
      },
    })

    expect(wrapper.text()).toContain('Warnung')
    expect(wrapper.text()).toContain('Seite 4 enthielt ein Bild')
  })

  it('zeigt die Meldung einer gescheiterten Datei', () => {
    const wrapper = mount(FileRow, {
      props: {
        entry: entry({ status: 'failed', error: 'pandoc konnte die Datei nicht lesen.' }),
      },
    })

    expect(wrapper.text()).toContain('fehlgeschlagen')
    expect(wrapper.text()).toContain('pandoc konnte die Datei nicht lesen.')
    // Ohne Ergebnis gibt es nichts aufzuklappen.
    expect(wrapper.find('[aria-expanded]').exists()).toBe(false)
  })

  it('laesst sich aufklappen, sobald ein Ergebnis vorliegt', async () => {
    const wrapper = mount(FileRow, {
      props: { entry: entry({ status: 'ok', markdown: '# Bericht' }) },
    })

    const toggle = wrapper.get('[aria-expanded]')
    expect(toggle.attributes('aria-expanded')).toBe('false')
    expect(toggle.attributes('aria-controls')).toBe('file-row-1-preview')

    await toggle.trigger('click')
    expect(wrapper.emitted('toggle')).toEqual([[1]])

    // Aufgeklappt wird die Zeile von aussen; die Zeile selbst haelt den Zustand nicht.
    await wrapper.setProps({ expanded: true })
    expect(wrapper.get('[aria-expanded]').attributes('aria-expanded')).toBe('true')
    expect(wrapper.get('#file-row-1-preview').text()).toContain('Das Ergebnis umfasst 9 Zeichen Markdown.')
  })

  it('ueberlaesst den aufgeklappten Inhalt dem Slot preview', async () => {
    const wrapper = mount(FileRow, {
      props: { entry: entry({ status: 'ok', markdown: '# Bericht' }), expanded: true },
      slots: { preview: '<p>Vorschau aus dem Elternteil.</p>' },
    })

    // Der gefuellte Slot ersetzt den Rueckfall vollstaendig.
    expect(wrapper.get('#file-row-1-preview').text()).toBe('Vorschau aus dem Elternteil.')
    expect(wrapper.text()).not.toContain('Zeichen Markdown')
  })

  it('zaehlt an der laufenden Zeile mit, wie lange sie schon laeuft', async () => {
    vi.useFakeTimers()

    const wrapper = mount(FileRow, { props: { entry: entry({ status: 'running' }) } })
    expect(wrapper.text()).toContain('läuft · 0 s')

    vi.advanceTimersByTime(47_000)
    await nextTick()
    expect(wrapper.text()).toContain('läuft · 0:47')

    vi.advanceTimersByTime(60_000)
    await nextTick()
    expect(wrapper.text()).toContain('läuft · 1:47')

    // Nichts behauptet einen Fortschritt: Das Ende ist unbekannt.
    expect(wrapper.text()).not.toContain('%')
    expect(wrapper.find('progress').exists()).toBe(false)
  })

  it('haelt den Zaehler an, sobald die Datei fertig ist, und nennt die Gesamtdauer', async () => {
    vi.useFakeTimers()

    const wrapper = mount(FileRow, { props: { entry: entry({ status: 'running' }) } })
    vi.advanceTimersByTime(103_000)
    await nextTick()
    expect(wrapper.text()).toContain('1:43')

    await wrapper.setProps({
      entry: entry({ status: 'ok', markdown: '# a', engine: 'docling', durationMs: 103_500 }),
    })

    // Der Zaehler haengt nicht mehr am Zustand; die Gesamtdauer steht daneben.
    expect(wrapper.text()).not.toContain('fertig · ')
    expect(wrapper.text()).toContain('fertig')
    expect(wrapper.text()).toContain('docling · 1:43')
    expect(vi.getTimerCount()).toBe(0)
  })

  it('zaehlt weder vor dem Start noch nach einem Fehlschlag', () => {
    vi.useFakeTimers()

    for (const status of ['queued', 'failed'] as const) {
      const wrapper = mount(FileRow, { props: { entry: entry({ status }) } })
      expect(wrapper.text()).not.toMatch(/\d:\d\d/)
      expect(vi.getTimerCount()).toBe(0)
      wrapper.unmount()
    }
  })

  it('laesst den Zaehler nicht weiterticken, wenn die Zeile verschwindet', () => {
    vi.useFakeTimers()

    const wrapper = mount(FileRow, { props: { entry: entry({ status: 'running' }) } })
    expect(vi.getTimerCount()).toBe(1)

    wrapper.unmount()
    expect(vi.getTimerCount()).toBe(0)
  })

  it('meldet den Wunsch, die Zeile zu entfernen', async () => {
    const wrapper = mount(FileRow, { props: { entry: entry({ id: 7 }) } })

    const buttons = wrapper.findAll('button')
    await buttons[buttons.length - 1]!.trigger('click')

    expect(wrapper.emitted('remove')).toEqual([[7]])
  })

  it('bietet den Download erst an, wenn ein Ergebnis vorliegt', async () => {
    downloads.downloadMarkdown.mockClear()

    for (const status of ['queued', 'running', 'failed'] as const) {
      const wrapper = mount(FileRow, { props: { entry: entry({ status }) } })
      expect(wrapper.find('[data-test="download-row"]').exists()).toBe(false)
    }

    const done = entry({ status: 'ok', markdown: '# Bericht' })
    const wrapper = mount(FileRow, { props: { entry: done } })
    const button = wrapper.get('[data-test="download-row"]')
    expect(button.text()).toContain('Herunterladen')
    // Der Name steht fuer Screenreader am Knopf: Zehn Zeilen tragen sonst
    // zehnmal dieselbe Beschriftung.
    expect(button.text()).toContain('bericht.pdf')

    await button.trigger('click')

    expect(downloads.downloadMarkdown).toHaveBeenCalledWith(done)
  })
})
