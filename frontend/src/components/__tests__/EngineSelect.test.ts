// @vitest-environment jsdom

/**
 * Die Enginewahl und der Hinweis daneben.
 *
 * Geprueft wird, was die Auswahl ueber sich selbst sagt: Zu docling und zu
 * markitdown steht je ein Satz da, der Dauer und Vollstaendigkeit
 * gegeneinanderstellt, und `aria-describedby` haengt diese Saetze an das Feld.
 */

import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import EngineSelect from '../EngineSelect.vue'
import type { EngineState } from '../../types'

const states: Record<string, EngineState> = {
  markitdown: 'ready',
  docling: 'ready',
  pandoc: 'ready',
}

function render(engines: string[] = ['markitdown', 'docling', 'pandoc']) {
  return mount(EngineSelect, {
    props: { modelValue: 'auto', engines, states, id: 'engine' },
  })
}

describe('EngineSelect', () => {
  it('nennt zu docling Dauer und Vollstaendigkeit', () => {
    const note = render().get('[data-test="engine-note-docling"]').text()
    expect(note).toMatch(/Minuten/)
    expect(note).toMatch(/gescannt/i)
  })

  it('nennt zu markitdown Tempo und den Preis dafuer', () => {
    const note = render().get('[data-test="engine-note-markitdown"]').text()
    expect(note).toMatch(/Sekundenbruchteil/)
    expect(note).toMatch(/Tabelle|Layout/)
  })

  it('haengt die Hinweise per aria-describedby an das Auswahlfeld', () => {
    const wrapper = render()
    const describedBy = wrapper.get('[data-test="engine-select"]').attributes('aria-describedby')
    expect(describedBy).toBeTruthy()
    expect(wrapper.get('[data-test="engine-notes"]').attributes('id')).toBe(describedBy)
  })

  it('erfindet keinen Hinweis fuer eine Engine, ueber die nichts zu sagen ist', () => {
    const wrapper = render()
    expect(wrapper.find('[data-test="engine-note-pandoc"]').exists()).toBe(false)
    expect(wrapper.findAll('[data-test="engine-notes"] li')).toHaveLength(2)
  })

  it('laesst Hinweis und Verweis weg, wenn keine der beiden Engines angeboten wird', () => {
    const wrapper = render(['pandoc'])
    expect(wrapper.find('[data-test="engine-notes"]').exists()).toBe(false)
    expect(
      wrapper.get('[data-test="engine-select"]').attributes('aria-describedby'),
    ).toBeUndefined()
  })

  it('meldet die Wahl weiterhin nach aussen', async () => {
    const wrapper = render()
    await wrapper.get('[data-test="engine-select"]').setValue('docling')
    expect(wrapper.emitted('update:modelValue')![0]![0]).toBe('docling')
  })
})
