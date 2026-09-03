// @vitest-environment jsdom

/**
 * Das Feld fuer Webadressen. Geprueft wird, was es weitergibt und was es
 * zurueckhaelt: Leerzeilen und Leerraum verschwinden, eine Zeile ohne Schema
 * wird markiert und bleibt stehen, alles Uebrige geht hinaus und das Feld ist
 * danach leer. Und was die Warteschlange nicht mehr aufnahm, legt `keep`
 * zurueck — an seinen alten Platz zwischen den uebrigen Zeilen.
 */

import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import UrlInput from './UrlInput.vue'

/** Schreibt Text in das Feld, so wie der Nutzer es tut. */
async function type(wrapper: ReturnType<typeof mount>, text: string): Promise<void> {
  await wrapper.get('textarea').setValue(text)
}

describe('UrlInput', () => {
  it('beschriftet das Feld und laesst den Knopf erst zu, wenn etwas dasteht', async () => {
    const wrapper = mount(UrlInput)

    expect(wrapper.get('label').text()).toBe('Webseiten, eine Adresse je Zeile')
    expect(wrapper.get('label').attributes('for')).toBe(wrapper.get('textarea').attributes('id'))

    const button = wrapper.get('[data-test="url-submit"]')
    expect(button.text()).toBe('Webseiten wandeln')
    expect(button.attributes('disabled')).toBeDefined()

    await type(wrapper, 'https://example.com/')
    expect(button.attributes('disabled')).toBeUndefined()
  })

  it('schickt die gueltige Zeile ab, verwirft die leere und markiert die ohne Schema', async () => {
    const wrapper = mount(UrlInput)

    await type(wrapper, '\n   beispiel.de/seite  \nhttps://example.com/\n')
    await wrapper.get('[data-test="url-submit"]').trigger('click')

    expect(wrapper.emitted('urls')).toEqual([[['https://example.com/']]])

    const marked = wrapper.get('[data-test="url-rejected"]')
    expect(marked.attributes('role')).toBe('alert')
    expect(marked.text()).toContain('beispiel.de/seite')
    expect(wrapper.get('textarea').attributes('aria-invalid')).toBe('true')

    // Die abgeschickte Zeile lebt in der Warteschlange weiter, die markierte
    // bleibt im Feld — sonst liesse sie sich nicht berichtigen.
    expect((wrapper.get('textarea').element as HTMLTextAreaElement).value).toBe(
      'beispiel.de/seite',
    )
  })

  it('leert das Feld, wenn jede Zeile durchkam', async () => {
    const wrapper = mount(UrlInput)

    await type(wrapper, 'https://example.com/\nHTTP://example.org/a.pdf')
    await wrapper.get('[data-test="url-submit"]').trigger('click')

    expect(wrapper.emitted('urls')).toEqual([
      [['https://example.com/', 'HTTP://example.org/a.pdf']],
    ])
    expect((wrapper.get('textarea').element as HTMLTextAreaElement).value).toBe('')
    expect(wrapper.find('[data-test="url-rejected"]').exists()).toBe(false)
  })

  it('legt zurueck, was keinen Platz fand, in der eingegebenen Reihenfolge', async () => {
    const wrapper = mount(UrlInput)

    await type(wrapper, 'https://example.com/a\nbeispiel.de\nhttps://example.com/b')
    await wrapper.get('[data-test="url-submit"]').trigger('click')

    expect(wrapper.emitted('urls')).toEqual([[['https://example.com/a', 'https://example.com/b']]])

    // Die Warteschlange nahm nur die erste Adresse auf. Die zweite steht danach
    // wieder da, wo sie stand: hinter der Zeile ohne Schema.
    wrapper.vm.keep(['https://example.com/b'])
    await wrapper.vm.$nextTick()

    expect((wrapper.get('textarea').element as HTMLTextAreaElement).value).toBe(
      'beispiel.de\nhttps://example.com/b',
    )
  })

  it('schickt nichts ab, wenn keine Zeile ein Schema hat', async () => {
    const wrapper = mount(UrlInput)

    await type(wrapper, 'ftp://example.com/datei\nbeispiel.de')
    await wrapper.get('[data-test="url-submit"]').trigger('click')

    expect(wrapper.emitted('urls')).toBeUndefined()
    expect(wrapper.get('[data-test="url-rejected"]').text()).toContain('ftp://example.com/datei')
  })
})
