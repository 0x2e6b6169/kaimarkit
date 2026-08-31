// @vitest-environment jsdom

/**
 * Die Dropzone auf ihren beiden Wegen: Ablegen und Dateidialog.
 *
 * Die Tastaturbedienung wird hier ueber die Bauart geprueft, nicht ueber ein
 * nachgestelltes Tastenereignis. Der Ablagebereich ist ein `<button>`; dass
 * Leertaste und Eingabetaste eine Schaltflaeche ausloesen, macht der Browser.
 * Ein Test, der `keydown` schickt und `click` erwartet, pruefte jsdom, nicht
 * diese Komponente.
 */

import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import FileDropZone from './FileDropZone.vue'

function fileNamed(name: string): File {
  return new File(['Beispielinhalt'], name)
}

describe('FileDropZone', () => {
  it('ist eine Schaltflaeche und damit per Tastatur erreichbar', () => {
    const wrapper = mount(FileDropZone)
    const zone = wrapper.get('button')

    expect(zone.element.tagName).toBe('BUTTON')
    expect(zone.attributes('type')).toBe('button')
    expect(zone.attributes('tabindex')).toBeUndefined()
  })

  it('oeffnet den Dateidialog, wenn die Flaeche ausgeloest wird', async () => {
    const wrapper = mount(FileDropZone)
    const input = wrapper.get('input[type="file"]').element as HTMLInputElement
    const opened = vi.spyOn(input, 'click').mockImplementation(() => {})

    await wrapper.get('button').trigger('click')

    expect(opened).toHaveBeenCalledOnce()
  })

  it('meldet die im Dialog gewaehlten Dateien in ihrer Reihenfolge', async () => {
    const wrapper = mount(FileDropZone)
    const input = wrapper.get('input[type="file"]')
    Object.defineProperty(input.element, 'files', {
      value: [fileNamed('a.pdf'), fileNamed('b.docx')],
      configurable: true,
    })

    await input.trigger('change')

    const emitted = wrapper.emitted('files')
    expect(emitted).toHaveLength(1)
    expect(emitted![0]![0]).toHaveLength(2)
    expect((emitted![0]![0] as File[]).map((file) => file.name)).toEqual(['a.pdf', 'b.docx'])
  })

  it('meldet abgelegte Dateien', async () => {
    const wrapper = mount(FileDropZone)

    await wrapper.get('button').trigger('drop', {
      dataTransfer: { files: [fileNamed('a.pdf')] },
    })

    const emitted = wrapper.emitted('files')
    expect(emitted).toHaveLength(1)
    expect((emitted![0]![0] as File[]).map((file) => file.name)).toEqual(['a.pdf'])
  })

  it('nimmt nichts an, solange sie gesperrt ist', async () => {
    const wrapper = mount(FileDropZone, { props: { disabled: true } })

    await wrapper.get('button').trigger('drop', {
      dataTransfer: { files: [fileNamed('a.pdf')] },
    })

    expect(wrapper.emitted('files')).toBeUndefined()
    expect(wrapper.get('button').attributes('disabled')).toBeDefined()
  })

  it('reicht die bekannten Endungen an den Dateidialog weiter', () => {
    const wrapper = mount(FileDropZone, { props: { extensions: ['.pdf', '.epub'] } })

    expect(wrapper.get('input[type="file"]').attributes('accept')).toBe('.pdf,.epub')
    expect(wrapper.text()).toContain('.pdf')
  })

  it('hebt die Flaeche hervor, solange etwas darueber schwebt', async () => {
    const wrapper = mount(FileDropZone)
    const zone = wrapper.get('button')

    await zone.trigger('dragenter')
    expect(zone.text()).toContain('loslassen')

    await zone.trigger('dragleave')
    expect(zone.text()).not.toContain('loslassen')
  })
})
