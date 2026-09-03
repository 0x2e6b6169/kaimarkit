// @vitest-environment jsdom

/**
 * Die Optionen gegen eine gesetzte Faehigkeitsmatrix.
 *
 * Geprueft wird der Leitsatz des Tickets: Angeboten wird nur, was gelingen kann.
 * Die Faelle haengen davon ab, welche Engines gerade installiert sind, und lassen
 * sich im Browser nicht der Reihe nach herstellen — deshalb setzt der Test die
 * Faehigkeitsmatrix hier direkt.
 */

import { beforeEach, describe, expect, it, vi } from 'vitest'
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

/** Die waehlbaren Schaltflaechen der Gruppe, ohne den Eintrag `auto`. */
function offeredEngines(wrapper: ReturnType<typeof render>): string[] {
  return wrapper
    .findAll('[data-test="engine-select"] input[type="radio"]')
    .filter((radio) => radio.attributes('disabled') === undefined)
    .map((radio) => radio.attributes('value') ?? '')
    .filter((value) => value !== 'auto')
}

function radio(wrapper: ReturnType<typeof render>, engine: string) {
  return wrapper.get(`[data-test="engine-select"] input[type="radio"][value="${engine}"]`)
}

/** Die gestaltete Schaltflaeche um den Radioschalter; sie traegt den Grund im `title`. */
function chip(wrapper: ReturnType<typeof render>, engine: string) {
  return wrapper.get(`[data-test="engine-choice-${engine}"] label`)
}

describe('OptionsPanel', () => {
  beforeEach(() => {
    given()
    localStorage.clear()
    vi.restoreAllMocks()
  })

  it('zeigt die Wahl aus den Optionen und bietet ohne Dateien alle nutzbaren Engines', () => {
    const wrapper = render([], { engine: 'markitdown', ocr: null })
    expect((radio(wrapper, 'markitdown').element as HTMLInputElement).checked).toBe(true)
    expect(offeredEngines(wrapper)).toEqual(['markitdown', 'docling', 'pandoc'])
  })

  it('laesst bei einer .epub nur die Engines waehlbar, die epub lesen koennen', () => {
    // Die Reihenfolge ist die der Gruppe, nicht die Praeferenz je Endung: Die
    // Gruppe behaelt ihre Form, ganz gleich, was in der Warteschlange liegt.
    const wrapper = render(['buch.epub'])
    expect(offeredEngines(wrapper)).toEqual(['markitdown', 'pandoc'])
    expect(offeredEngines(wrapper)).not.toContain('docling')
  })

  it('zeigt eine Engine, die die Warteschlange ausschliesst, als deaktivierte Schaltflaeche', () => {
    // Nicht versteckt: Sonst aenderte die Gruppe ihre Form mit jeder Datei.
    const wrapper = render(['buch.epub'])
    const docling = radio(wrapper, 'docling')
    expect(docling.attributes('disabled')).toBeDefined()
    expect(chip(wrapper, 'docling').attributes('title')).toBe('liest diese Dateien nicht')
  })

  it('bietet bei gemischten Formaten nur die Schnittmenge', () => {
    const wrapper = render(['buch.epub', 'bericht.pdf'])
    expect(offeredEngines(wrapper)).toEqual(['markitdown'])
  })

  it('kennzeichnet eine ladende Engine und laesst sie waehlbar', () => {
    const wrapper = render(['bericht.pdf'])
    expect(radio(wrapper, 'docling').attributes('disabled')).toBeUndefined()
    expect(wrapper.get('[data-test="engine-choice-docling"]').text()).toContain('lädt noch')
  })

  it('zeigt eine unavailable gemeldete Engine deaktiviert als nicht installiert', () => {
    given({ engines: { markitdown: 'ready', docling: 'unavailable', pandoc: 'ready' } })
    const wrapper = render(['bericht.pdf'])
    expect(offeredEngines(wrapper)).toEqual(['markitdown'])
    expect(radio(wrapper, 'docling').attributes('disabled')).toBeDefined()
    expect(chip(wrapper, 'docling').attributes('title')).toBe('nicht installiert')
  })

  it('bietet nicht an, was in engines gar nicht steht', () => {
    // `.md` fuehrt `passthrough`, und `engines` nennt den Namen nicht: Markdown
    // wird durchgereicht, gewaehlt wird dort nichts. Ohne diese Pruefung stuende
    // `passthrough` in der Auswahl, obwohl der Dienst es nicht anbietet.
    given({ formats: { ...baseCapabilities.formats, '.md': ['passthrough'] } })
    const wrapper = render(['notizen.md'])
    expect(offeredEngines(wrapper)).toEqual([])
    expect(wrapper.find('input[type="radio"][value="passthrough"]').exists()).toBe(false)
  })

  it('faellt auf automatisch zurueck, wenn die gewaehlte Engine das Format nicht kann', async () => {
    const wrapper = render(['bericht.pdf'], { engine: 'docling', ocr: null })
    expect(wrapper.emitted('update:modelValue')).toBeUndefined()

    await wrapper.setProps({ filenames: ['buch.epub'] })
    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toHaveLength(1)
    expect(emitted![0]![0]).toEqual({ engine: 'auto', ocr: null })
  })

  it('laesst beim Ruecksprung auf automatisch den gemerkten Wert stehen', async () => {
    // Beim naechsten Besuch soll die Engine wieder da sein.
    localStorage.setItem('kaimarkit.engine', 'docling')
    const wrapper = render(['bericht.pdf'], { engine: 'docling', ocr: null })
    await wrapper.setProps({ filenames: ['buch.epub'] })
    expect(wrapper.emitted('update:modelValue')![0]![0]).toEqual({ engine: 'auto', ocr: null })
    expect(localStorage.getItem('kaimarkit.engine')).toBe('docling')
  })

  it('meldet die gewaehlte Engine nach aussen', async () => {
    const wrapper = render(['buch.epub'])
    await radio(wrapper, 'pandoc').setValue()
    expect(wrapper.emitted('update:modelValue')![0]![0]).toEqual({
      engine: 'pandoc',
      ocr: null,
    })
  })

  it('merkt die gewaehlte Engine unter kaimarkit.engine im Browser', async () => {
    const wrapper = render(['buch.epub'])
    await radio(wrapper, 'pandoc').setValue()
    expect(localStorage.getItem('kaimarkit.engine')).toBe('pandoc')
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

  it('sagt neben jedem Namen, wofuer die Engine gut ist', () => {
    // Der Nutzer soll die Dauer nicht erst an der Zeitgrenze erfahren: Die
    // Halbsaetze stehen da, bevor jemand die Auswahl anfasst.
    const wrapper = render()
    expect(wrapper.get('[data-test="engine-short-docling"]').text()).toMatch(/Minuten/)
    expect(wrapper.get('[data-test="engine-short-markitdown"]').text()).toMatch(/schnell/)
  })
})
