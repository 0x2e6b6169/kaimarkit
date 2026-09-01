// @vitest-environment jsdom

/**
 * Die Optionen gegen eine gesetzte Faehigkeitsmatrix.
 *
 * Geprueft wird der Leitsatz des Tickets: Angeboten wird nur, was gelingen kann.
 * Die Faelle haengen davon ab, welche Engines gerade installiert sind, und lassen
 * sich im Browser nicht der Reihe nach herstellen — deshalb setzt der Test die
 * Faehigkeitsmatrix hier direkt.
 */

import { beforeEach, describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import OptionsPanel from '../OptionsPanel.vue'
import { useCapabilities } from '../../composables/useCapabilities'
import type { CapabilitiesResponse, ConvertOptions } from '../../types'

const baseCapabilities: CapabilitiesResponse = {
  formats: {
    '.pdf': ['docling', 'markitdown'],
    '.docx': ['markitdown', 'docling', 'pandoc'],
    '.epub': ['pandoc', 'markitdown'],
  },
  engines: { markitdown: 'ready', docling: 'warming', pandoc: 'ready' },
  limits: { max_file_size_mb: 50, max_files: 20, conversion_timeout_s: 120 },
  ocr_available: true,
  default_engine: 'auto',
}

/** `useCapabilities` haelt einen geteilten Zustand; jeder Test setzt ihn neu. */
function given(patch: Partial<CapabilitiesResponse> = {}): void {
  useCapabilities().capabilities.value = { ...baseCapabilities, ...patch }
}

const defaultOptions: ConvertOptions = { engine: 'auto', ocr: null }

function render(filenames: string[] = [], options: ConvertOptions = defaultOptions) {
  return mount(OptionsPanel, { props: { modelValue: options, filenames } })
}

/** Die Werte der Auswahl, ohne den Eintrag `auto`. */
function offeredEngines(wrapper: ReturnType<typeof render>): string[] {
  return wrapper
    .findAll('[data-test="engine-select"] option')
    .map((option) => option.attributes('value') ?? '')
    .filter((value) => value !== 'auto')
}

describe('OptionsPanel', () => {
  beforeEach(() => {
    given()
  })

  it('steht auf automatisch und bietet ohne Dateien alle nutzbaren Engines', () => {
    const wrapper = render()
    const select = wrapper.get('[data-test="engine-select"]')
    expect((select.element as HTMLSelectElement).value).toBe('auto')
    expect(offeredEngines(wrapper)).toEqual(['markitdown', 'docling', 'pandoc'])
  })

  it('laesst bei einer .epub nur die Engines uebrig, die epub lesen koennen', () => {
    const wrapper = render(['buch.epub'])
    expect(offeredEngines(wrapper)).toEqual(['pandoc', 'markitdown'])
    expect(offeredEngines(wrapper)).not.toContain('docling')
  })

  it('bietet bei gemischten Formaten nur die Schnittmenge', () => {
    const wrapper = render(['buch.epub', 'bericht.pdf'])
    expect(offeredEngines(wrapper)).toEqual(['markitdown'])
  })

  it('kennzeichnet eine ladende Engine und laesst sie waehlbar', () => {
    const wrapper = render(['bericht.pdf'])
    const docling = wrapper
      .findAll('[data-test="engine-select"] option')
      .find((option) => option.attributes('value') === 'docling')
    expect(docling).toBeDefined()
    expect(docling!.text()).toContain('lädt noch')
    expect(docling!.attributes('disabled')).toBeUndefined()
  })

  it('bietet eine unavailable gemeldete Engine nicht an', () => {
    given({ engines: { markitdown: 'ready', docling: 'unavailable', pandoc: 'ready' } })
    const wrapper = render(['bericht.pdf'])
    expect(offeredEngines(wrapper)).toEqual(['markitdown'])
  })

  it('bietet nicht an, was in engines gar nicht steht', () => {
    // `.md` fuehrt `passthrough`, und `engines` nennt den Namen nicht: Markdown
    // wird durchgereicht, gewaehlt wird dort nichts. Ohne diese Pruefung stuende
    // `passthrough` in der Auswahl, obwohl der Dienst es nicht anbietet.
    given({ formats: { ...baseCapabilities.formats, '.md': ['passthrough'] } })
    const wrapper = render(['notizen.md'])
    expect(offeredEngines(wrapper)).toEqual([])
  })

  it('faellt auf automatisch zurueck, wenn die gewaehlte Engine das Format nicht kann', async () => {
    const wrapper = render(['bericht.pdf'], { engine: 'docling', ocr: null })
    expect(wrapper.emitted('update:modelValue')).toBeUndefined()

    await wrapper.setProps({ filenames: ['buch.epub'] })
    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toHaveLength(1)
    expect(emitted![0]![0]).toEqual({ engine: 'auto', ocr: null })
  })

  it('meldet die gewaehlte Engine nach aussen', async () => {
    const wrapper = render(['buch.epub'])
    await wrapper.get('[data-test="engine-select"]').setValue('pandoc')
    expect(wrapper.emitted('update:modelValue')![0]![0]).toEqual({
      engine: 'pandoc',
      ocr: null,
    })
  })

  it('zeigt den OCR-Schalter, wenn das Backend OCR meldet', async () => {
    const wrapper = render()
    const ocr = wrapper.get('[data-test="ocr-switch"]')
    expect((ocr.element as HTMLInputElement).checked).toBe(false)

    await ocr.setValue(true)
    expect(wrapper.emitted('update:modelValue')![0]![0]).toEqual({
      engine: 'auto',
      ocr: true,
    })
  })

  it('laesst den OCR-Schalter weg, wenn das Backend kein OCR meldet', () => {
    given({ ocr_available: false })
    const wrapper = render()
    expect(wrapper.find('[data-test="ocr-switch"]').exists()).toBe(false)
    expect(wrapper.find('[data-test="ocr-field"]').exists()).toBe(false)
  })

  it('bietet ohne geladene Faehigkeiten nur automatisch an', () => {
    useCapabilities().capabilities.value = null
    const wrapper = render(['bericht.pdf'])
    expect(offeredEngines(wrapper)).toEqual([])
  })

  it('sagt schon in der Voreinstellung, was docling und markitdown kosten', () => {
    // Der Nutzer soll die Dauer nicht erst an der Zeitgrenze erfahren: Die
    // Saetze stehen da, bevor jemand die Auswahl anfasst.
    const wrapper = render()
    expect(wrapper.get('[data-test="engine-note-docling"]').text()).toMatch(/Minuten/)
    expect(wrapper.get('[data-test="engine-note-markitdown"]').text()).toMatch(
      /Sekundenbruchteil/,
    )
  })
})
