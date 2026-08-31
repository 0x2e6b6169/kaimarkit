// @vitest-environment jsdom

/**
 * Die Vorschau gegen ein feindliches Ergebnis.
 *
 * Geprueft wird der Fall aus dem Ticket: ein Markdown mit Tabelle, Codeblock und
 * einem `<script>`-Versuch. Tabelle und Code stehen da, das Skript nicht — und
 * das faellt ohne Test erst auf, wenn es zu spaet ist.
 */

import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import MarkdownPreview from './MarkdownPreview.vue'

/** So sieht ein Ergebnis aus, das aus einem fremden Dokument stammt. */
const HOSTILE = [
  '# Bericht',
  '',
  '| Spalte A | Spalte B |',
  '| --- | --- |',
  '| eins | zwei |',
  '',
  '```python',
  'print("hallo")',
  '```',
  '',
  '<script>window.__pwned = true</script>',
  '',
  '<img src="x" onerror="window.__pwned = true">',
  '',
  '[Verweis](javascript:window.__pwned = true)',
].join('\n')

function open(markdown: string | null) {
  return mount(MarkdownPreview, {
    props: { markdown, filename: 'bericht.pdf', open: true },
  })
}

describe('MarkdownPreview', () => {
  beforeEach(() => {
    delete (window as unknown as Record<string, unknown>).__pwned
  })

  it('stellt Tabelle und Codeblock dar', () => {
    const html = open(HOSTILE).get('[data-test="rendered"]').html()
    expect(html).toContain('<table>')
    expect(html).toContain('Spalte A')
    expect(html).toContain('<code class="language-python">')
    expect(html).toContain('print(')
  })

  it('filtert das Skript heraus, es steht nicht im Ergebnis und laeuft nicht', () => {
    const wrapper = open(HOSTILE)
    const panel = wrapper.get('[data-test="rendered"]')

    expect(panel.html()).not.toContain('<script')
    expect(panel.find('script').exists()).toBe(false)
    expect(panel.html()).not.toContain('onerror')
    expect(panel.html()).not.toContain(String.raw`href="javascript:`)
    expect((window as unknown as Record<string, unknown>).__pwned).toBeUndefined()
  })

  it('zeigt im Reiter Rohtext den Quelltext unveraendert', async () => {
    const wrapper = open(HOSTILE)
    await wrapper.get('#tab-raw').trigger('click')

    const raw = wrapper.get('[data-test="raw"]')
    expect(raw.text()).toBe(HOSTILE)
    // Der Rohtext ist Text, kein Markup: `<script>` steht als Zeichenfolge da.
    expect(raw.find('script').exists()).toBe(false)
    expect(wrapper.find('[data-test="rendered"]').exists()).toBe(false)
  })

  it('rendert erst beim Aufklappen', async () => {
    const wrapper = mount(MarkdownPreview, {
      props: { markdown: HOSTILE, filename: 'bericht.pdf' },
    })
    expect(wrapper.find('[data-test="rendered"]').exists()).toBe(false)

    await wrapper.get('button[aria-expanded]').trigger('click')
    expect(wrapper.get('[data-test="rendered"]').html()).toContain('<table>')
  })

  it('kopiert den Rohtext und meldet es sichtbar', async () => {
    const writeText = vi.fn().mockResolvedValue(undefined)
    Object.defineProperty(navigator, 'clipboard', { value: { writeText }, configurable: true })

    const wrapper = open(HOSTILE)
    const button = wrapper.findAll('button').find((b) => b.text() === 'Kopieren')!
    await button.trigger('click')
    await Promise.resolve()
    await wrapper.vm.$nextTick()

    expect(writeText).toHaveBeenCalledWith(HOSTILE)
    expect(button.text()).toBe('Kopiert')
    expect(wrapper.emitted('copied')).toHaveLength(1)
  })

  it('bleibt ohne Ergebnis stumm', () => {
    const wrapper = open(null)
    expect(wrapper.text()).toContain('Noch kein Ergebnis.')
    expect(wrapper.find('[data-test="rendered"]').exists()).toBe(false)
  })
})
