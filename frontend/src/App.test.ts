// @vitest-environment jsdom
/**
 * Die Seite als Ganzes. Geprueft wird nicht, wie die Bausteine aussehen — das
 * tun ihre eigenen Tests —, sondern dass sie zusammenpassen: dass die Dropzone
 * die Warteschlange fuellt, dass die Vorschau durch die Warteschlange bis in die
 * Zeile durchkommt und dass das Ende eines Laufs angesagt wird.
 *
 * Die Schnittstelle ist attrappiert, die Composables sind echt. Sie liegen als
 * Modulzustand vor und ueberdauern deshalb den einzelnen Test; jeder Test setzt
 * sie zu Beginn zurueck.
 */
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import App from './App.vue'
import FileDropZone from './components/FileDropZone.vue'
import { useCapabilities } from './composables/useCapabilities'
import { useConversion } from './composables/useConversion'
import type { CapabilitiesResponse, ConversionEntry } from './types'

const api = vi.hoisted(() => ({
  fetchCapabilities: vi.fn(),
  convertFile: vi.fn(),
}))

vi.mock('./api', () => ({
  fetchCapabilities: api.fetchCapabilities,
  convertFile: api.convertFile,
  messageFromError: (cause: unknown) =>
    cause instanceof Error && cause.message ? cause.message : String(cause),
}))

const CAPABILITIES: CapabilitiesResponse = {
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

function result(filename: string, markdown: string): ConversionEntry {
  return {
    filename,
    status: 'ok',
    markdown,
    engine: 'markitdown',
    warnings: [],
    duration_ms: 12,
    error: null,
  }
}

/** Faehigkeiten neu laden, damit der Modulzustand des vorigen Tests weg ist. */
async function resetCapabilities(): Promise<void> {
  await useCapabilities().reload()
}

beforeEach(() => {
  vi.clearAllMocks()
  useConversion().clear()
  useConversion().options.value = { engine: 'auto', ocr: null }
})

describe('App', () => {
  it('nennt im leeren Zustand Zweck und Formate und zeigt die leere Warteschlange', async () => {
    api.fetchCapabilities.mockResolvedValue(CAPABILITIES)
    await resetCapabilities()

    const wrapper = mount(App)
    await flushPromises()

    const text = wrapper.text()
    expect(text).toContain('kaimarkit wandelt Dokumente nach Markdown')
    // Die Endungen kommen aus /api/capabilities, alphabetisch sortiert.
    expect(text).toContain('Angenommen werden .docx · .epub · .pdf.')
    expect(text).toContain('Noch keine Dateien ausgewaehlt.')

    // Die Warteschlange bleibt eingehaengt, auch ohne Dateien: Sonst saehe sie
    // den Start der ersten Datei als Ausgangszustand und sagte ihn nie an.
    expect(wrapper.find('[role="log"][aria-live="polite"]').exists()).toBe(true)
  })

  it('nimmt Dateien aus der Dropzone an und reicht die Vorschau bis in die Zeile durch', async () => {
    api.fetchCapabilities.mockResolvedValue(CAPABILITIES)
    api.convertFile.mockImplementation(async (file: File) =>
      result(file.name, '# Bericht\n\nEin Absatz.'),
    )
    await resetCapabilities()

    const wrapper = mount(App)
    await flushPromises()

    wrapper
      .findComponent(FileDropZone)
      .vm.$emit('files', [new File(['x'], 'bericht.pdf'), new File(['y'], 'notiz.docx')])
    await nextTick()
    await flushPromises()

    expect(wrapper.text()).toContain('bericht.pdf')
    expect(wrapper.text()).toContain('notiz.docx')
    expect(wrapper.find('[data-test="progress"]').text()).toContain('2 von 2 fertig')

    // Vor dem Aufklappen ist keine Vorschau da; sie kostet dann auch nichts.
    expect(wrapper.find('[data-test="rendered"]').exists()).toBe(false)

    const expand = wrapper.findAll('button').find((button) => button.text() === 'Aufklappen')
    expect(expand).toBeDefined()
    await expand!.trigger('click')

    // Der Slot `preview` geht durch FileQueue hindurch bis in FileRow. Ohne die
    // Durchreichung staende hier der Platzhalter aus FE-3.
    const rendered = wrapper.find('[data-test="rendered"]')
    expect(rendered.exists()).toBe(true)
    expect(rendered.html()).toContain('<h1>Bericht</h1>')

    // Keine Schaltflaeche faellt aus der Tabreihenfolge. Der Reiter „Rohtext"
    // tat das einmal und war damit nur mit der Maus zu erreichen.
    expect(wrapper.findAll('button[tabindex="-1"], [role="tab"][tabindex="-1"]')).toHaveLength(0)
  })

  it('sagt das Ende eines Laufs mit Zaehlung an', async () => {
    api.fetchCapabilities.mockResolvedValue(CAPABILITIES)
    api.convertFile.mockImplementation(async (file: File) => {
      if (file.name.includes('fehler')) throw new Error('Die Engine scheiterte.')
      return result(file.name, '# Titel')
    })
    await resetCapabilities()

    const wrapper = mount(App)
    await flushPromises()

    wrapper
      .findComponent(FileDropZone)
      .vm.$emit('files', [new File(['x'], 'gut.pdf'), new File(['y'], 'fehler.pdf')])
    await nextTick()
    await flushPromises()
    await nextTick()

    expect(wrapper.find('[data-test="app-log"]').text()).toContain(
      'Alle Dateien sind fertig: 1 gelungen, 1 fehlgeschlagen.',
    )
  })

  it('meldet den Ausfall der Faehigkeiten als alert und laesst es erneut versuchen', async () => {
    api.fetchCapabilities.mockRejectedValue(new Error('Der Dienst ist nicht erreichbar.'))
    await resetCapabilities()

    const wrapper = mount(App)
    await flushPromises()

    const alert = wrapper.find('[data-test="capabilities-error"]')
    expect(alert.exists()).toBe(true)
    expect(alert.attributes('role')).toBe('alert')
    expect(alert.text()).toContain('Der Dienst ist nicht erreichbar.')

    api.fetchCapabilities.mockResolvedValue(CAPABILITIES)
    const retry = alert.findAll('button').find((button) => button.text() === 'Erneut versuchen')
    expect(retry).toBeDefined()
    await retry!.trigger('click')
    await flushPromises()

    expect(wrapper.find('[data-test="capabilities-error"]').exists()).toBe(false)
    expect(wrapper.text()).toContain('Angenommen werden .docx · .epub · .pdf.')
  })
})
