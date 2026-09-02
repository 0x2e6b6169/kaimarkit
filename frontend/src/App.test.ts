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
  fetchHealth: vi.fn(),
  convertFile: vi.fn(),
}))

vi.mock('./api', () => ({
  fetchCapabilities: api.fetchCapabilities,
  fetchHealth: api.fetchHealth,
  convertFile: api.convertFile,
  messageFromError: (cause: unknown) =>
    cause instanceof Error && cause.message ? cause.message : String(cause),
}))

// Das Packen selbst ist in `download.spec.ts` geprueft. Hier zaehlt nur, ob der
// Knopf im richtigen Augenblick greifbar ist und was er uebergibt.
const downloads = vi.hoisted(() => ({ downloadArchive: vi.fn() }))
vi.mock('./download', async (importOriginal) => ({
  ...(await importOriginal<typeof import('./download')>()),
  downloadArchive: downloads.downloadArchive,
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
    expect(text).toContain('Noch keine Dateien ausgewählt.')

    // Die Warteschlange bleibt eingehaengt, auch ohne Dateien: Sonst saehe sie
    // den Start der ersten Datei als Ausgangszustand und sagte ihn nie an.
    expect(wrapper.find('[role="log"][aria-live="polite"]').exists()).toBe(true)
  })

  it('verweist im Kopf auf das Repository', async () => {
    api.fetchCapabilities.mockResolvedValue(CAPABILITIES)
    await resetCapabilities()

    const wrapper = mount(App)
    await flushPromises()

    // Gesucht wird ueber den zugaenglichen Namen, nicht ueber eine Klasse oder
    // ein `data-test`: Genau diesen Namen bekommt zu hoeren, wer den Verweis
    // nicht sieht. Das Zeichen selbst ist versteckt und traegt keinen Text.
    const link = wrapper.get('header a[aria-label="kaimarkit auf GitHub"]')
    expect(link.attributes('href')).toBe('https://github.com/0x2e6b6169/kaimarkit')
    expect(link.attributes('target')).toBe('_blank')
    expect(link.attributes('rel')).toBe('noopener noreferrer')
    expect(link.get('svg').attributes('aria-hidden')).toBe('true')
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

  it('zaehlt abgebrochene Dateien mit, ohne sie zu den Fehlern zu schlagen', async () => {
    api.fetchCapabilities.mockResolvedValue(CAPABILITIES)
    // Wer abgebrochen wird, antwortet nie von allein — wie `fetch` endet der
    // Aufruf erst mit dem Abbruch, und zwar als `AbortError`.
    api.convertFile.mockImplementation(
      (file: File, _options: unknown, signal: AbortSignal) =>
        new Promise<ConversionEntry>((resolve, reject) => {
          if (!file.name.startsWith('warte')) {
            resolve(result(file.name, '# Titel'))
            return
          }
          signal.addEventListener('abort', () =>
            reject(new DOMException('Abgebrochen', 'AbortError')),
          )
        }),
    )
    await resetCapabilities()

    const wrapper = mount(App)
    await flushPromises()

    // Die beiden abzubrechenden stehen vorn, damit sie auch wirklich laufen:
    // Eine wartende Zeile hat keinen Signalgeber, den ein Abbruch erreichen
    // koennte.
    const names = ['warte-1.pdf', 'warte-2.pdf', 'a.pdf', 'b.pdf', 'c.pdf']
    wrapper
      .findComponent(FileDropZone)
      .vm.$emit(
        'files',
        names.map((name) => new File(['x'], name)),
      )
    await nextTick()
    await flushPromises()

    const queue = useConversion()
    for (const entry of queue.entries.value.filter((item) => item.filename.startsWith('warte'))) {
      queue.abort(entry.id)
    }
    await flushPromises()
    await nextTick()
    await flushPromises()
    await nextTick()

    const log = wrapper.find('[data-test="app-log"]').text()
    expect(log).toContain('Der Lauf ist zu Ende: 3 gelungen, 2 abgebrochen.')
    // Die abgebrochenen tauchen nirgends als Fehlschlag auf.
    expect(log).not.toContain('fehlgeschlagen')
  })

  it('gibt das Archiv erst frei, wenn ein Ergebnis vorliegt, und sagt es an', async () => {
    api.fetchCapabilities.mockResolvedValue(CAPABILITIES)
    downloads.downloadArchive.mockResolvedValue(undefined)
    let finish: (entry: ConversionEntry) => void = () => {}
    api.convertFile.mockImplementation(
      (file: File) =>
        new Promise<ConversionEntry>((resolve) => {
          finish = () => resolve(result(file.name, '# Titel'))
        }),
    )
    await resetCapabilities()

    const wrapper = mount(App)
    await flushPromises()

    // Ohne Dateien steht der Knopf gar nicht da.
    expect(wrapper.find('[data-test="download-all"]').exists()).toBe(false)

    wrapper.findComponent(FileDropZone).vm.$emit('files', [new File(['x'], 'bericht.pdf')])
    await nextTick()
    await flushPromises()

    // Solange etwas laeuft, waere das Archiv unvollstaendig.
    const button = wrapper.get('[data-test="download-all"]')
    expect(button.attributes('disabled')).toBeDefined()

    finish(result('bericht.pdf', '# Titel'))
    await flushPromises()
    await nextTick()

    expect(button.attributes('disabled')).toBeUndefined()
    await button.trigger('click')
    await flushPromises()
    await nextTick()

    expect(downloads.downloadArchive).toHaveBeenCalledTimes(1)
    expect(downloads.downloadArchive.mock.calls[0]![0]).toHaveLength(1)
    expect(wrapper.find('[data-test="app-log"]').text()).toContain('kaimarkit.zip steht bereit.')
  })

  it('meldet einen gescheiterten Archivbau als alert', async () => {
    api.fetchCapabilities.mockResolvedValue(CAPABILITIES)
    api.convertFile.mockImplementation(async (file: File) => result(file.name, '# Titel'))
    downloads.downloadArchive.mockRejectedValue(new Error('Der Speicher reichte nicht.'))
    await resetCapabilities()

    const wrapper = mount(App)
    await flushPromises()

    wrapper.findComponent(FileDropZone).vm.$emit('files', [new File(['x'], 'bericht.pdf')])
    await nextTick()
    await flushPromises()

    await wrapper.get('[data-test="download-all"]').trigger('click')
    await flushPromises()
    await nextTick()

    const alert = wrapper.get('[data-test="archive-error"]')
    expect(alert.attributes('role')).toBe('alert')
    expect(alert.text()).toContain('Der Speicher reichte nicht.')
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

  it('zeigt die Version des Dienstes unverändert an', async () => {
    api.fetchCapabilities.mockResolvedValue(CAPABILITIES)
    // So sieht der Wert aus, sobald er aus dem Git-Tag stammt. Er ist eine
    // undurchsichtige Zeichenkette: Was kommt, steht da — ungekürzt.
    api.fetchHealth.mockResolvedValue({ status: 'ok', version: 'v0.1.0-12-ga22a6c5' })
    await resetCapabilities()

    const wrapper = mount(App)
    await flushPromises()

    expect(wrapper.text()).toContain('v0.1.0-12-ga22a6c5')
  })

  it('schweigt, wenn die Version nicht zu haben ist', async () => {
    api.fetchCapabilities.mockResolvedValue(CAPABILITIES)
    api.fetchHealth.mockRejectedValue(new Error('Der Dienst ist nicht erreichbar.'))
    await resetCapabilities()

    const wrapper = mount(App)
    await flushPromises()

    // Kein Banner, kein Platzhalter, keine Zeile: An der Version hängt nichts,
    // wer sie nicht kennt, kann trotzdem umwandeln.
    expect(wrapper.find('[data-test="version"]').exists()).toBe(false)
    expect(wrapper.text()).not.toContain('Version')
    expect(wrapper.findAll('[role="alert"]')).toHaveLength(0)

    // Und die Seite steht wie zuvor.
    expect(wrapper.text()).toContain('Angenommen werden .docx · .epub · .pdf.')
    expect(wrapper.text()).toContain('Noch keine Dateien ausgewählt.')
  })
})
