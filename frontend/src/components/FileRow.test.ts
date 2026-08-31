// @vitest-environment jsdom

/**
 * Was eine Zeile ueber ihren Eintrag verraet.
 *
 * Geprueft wird vor allem, was ohne Test still verschwindet: das Wort neben dem
 * Symbol, die Warnungen an der Zeile und die Meldung einer gescheiterten Datei.
 */

import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import FileRow from './FileRow.vue'
import type { QueueEntry } from '../composables/useConversion'

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
  it('nennt jeden Zustand als Wort, nicht nur als Farbe', () => {
    const cases: [QueueEntry['status'], string][] = [
      ['queued', 'wartet'],
      ['running', 'laeuft'],
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
    expect(wrapper.text()).toContain('412 ms')
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
    expect(wrapper.get('#file-row-1-preview').text()).toContain('Vorschau folgt mit FE-4')
  })

  it('ueberlaesst den aufgeklappten Inhalt dem Slot preview', async () => {
    const wrapper = mount(FileRow, {
      props: { entry: entry({ status: 'ok', markdown: '# Bericht' }), expanded: true },
      slots: { preview: '<p>Hier steht spaeter MarkdownPreview.</p>' },
    })

    expect(wrapper.get('#file-row-1-preview').text()).toBe('Hier steht spaeter MarkdownPreview.')
  })

  it('meldet den Wunsch, die Zeile zu entfernen', async () => {
    const wrapper = mount(FileRow, { props: { entry: entry({ id: 7 }) } })

    const buttons = wrapper.findAll('button')
    await buttons[buttons.length - 1]!.trigger('click')

    expect(wrapper.emitted('remove')).toEqual([[7]])
  })
})
