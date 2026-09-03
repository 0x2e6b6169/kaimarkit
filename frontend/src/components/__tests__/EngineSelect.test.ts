// @vitest-environment jsdom

/**
 * Die Enginewahl als Schaltergruppe.
 *
 * Geprueft wird, was die Gruppe ueber sich selbst sagt: Zu jeder angebotenen
 * Engine steht ein Halbsatz, hinter jedem Namen ein Info-Zeichen, dessen
 * Langtext ueber `aria-describedby` erreichbar ist und sich ohne Maus oeffnet.
 * Eine Engine, die gerade nicht in Frage kommt, bleibt als deaktivierte
 * Schaltflaeche stehen — mit dem Grund im `title`.
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

function render(
  engines: string[] = ['markitdown', 'docling', 'pandoc'],
  overrides: Record<string, EngineState> = {},
  modelValue = 'markitdown',
) {
  return mount(EngineSelect, {
    props: { modelValue, engines, states: { ...states, ...overrides } },
  })
}

function radio(wrapper: ReturnType<typeof render>, engine: string) {
  return wrapper.get(`input[type="radio"][value="${engine}"]`)
}

/** Die gestaltete Schaltflaeche um den Radioschalter; sie traegt den Grund im `title`. */
function chip(wrapper: ReturnType<typeof render>, engine: string) {
  return wrapper.get(`[data-test="engine-choice-${engine}"] label`)
}

describe('EngineSelect', () => {
  it('ist eine Gruppe echter Radioschalter, kein Auswahlfeld', () => {
    const wrapper = render()
    expect(wrapper.find('select').exists()).toBe(false)
    expect(wrapper.get('[data-test="engine-select"]').element.tagName).toBe('FIELDSET')
    expect(wrapper.findAll('input[type="radio"]').map((r) => r.attributes('value'))).toEqual([
      'auto',
      'markitdown',
      'docling',
      'pandoc',
    ])
  })

  it('zeigt die gewaehlte Engine als gewaehlt', () => {
    const wrapper = render()
    expect((radio(wrapper, 'markitdown').element as HTMLInputElement).checked).toBe(true)
    expect((radio(wrapper, 'auto').element as HTMLInputElement).checked).toBe(false)
  })

  it('gibt jeder angebotenen Engine einen Kurztext', () => {
    const wrapper = render()
    for (const engine of ['auto', 'markitdown', 'docling', 'pandoc']) {
      expect(wrapper.get(`[data-test="engine-short-${engine}"]`).text()).not.toBe('')
    }
  })

  it('haengt den Langtext per aria-describedby an das Info-Zeichen', () => {
    const wrapper = render()
    const info = wrapper.get('[data-test="engine-info-docling"]')
    expect(info.element.tagName).toBe('BUTTON')
    expect(info.attributes('type')).toBe('button')
    const describedBy = info.attributes('aria-describedby')
    expect(describedBy).toBeTruthy()
    const long = wrapper.get(`#${describedBy}`)
    expect(long.text()).toMatch(/Minuten/)
    expect(long.text()).toMatch(/gescannt/i)
  })

  it('oeffnet die Erklaerung bei Tastaturfokus und schliesst sie mit Escape', async () => {
    const wrapper = render()
    const info = wrapper.get('[data-test="engine-info-markitdown"]')
    const long = wrapper.get('[data-test="engine-long-markitdown"]')
    expect(long.attributes('hidden')).toBeDefined()

    await info.trigger('focus')
    expect(long.attributes('hidden')).toBeUndefined()

    await info.trigger('keydown', { key: 'Escape' })
    expect(long.attributes('hidden')).toBeDefined()

    await info.trigger('mouseenter')
    expect(long.attributes('hidden')).toBeUndefined()
    await info.trigger('mouseleave')
    expect(long.attributes('hidden')).toBeDefined()
  })

  it('kennt zu einer fremden Engine keinen Text und stolpert nicht darueber', () => {
    const wrapper = render(['markitdown', 'neu'], { neu: 'ready' })
    expect(wrapper.find('input[type="radio"][value="neu"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="engine-short-neu"]').exists()).toBe(false)
    expect(wrapper.find('[data-test="engine-info-neu"]').exists()).toBe(false)
  })

  it('zeigt eine Engine, die die Dateien nicht liest, deaktiviert mit Grund', () => {
    const wrapper = render(['markitdown', 'pandoc'])
    const docling = radio(wrapper, 'docling')
    expect(docling.attributes('disabled')).toBeDefined()
    expect(chip(wrapper, 'docling').attributes('title')).toBe('liest diese Dateien nicht')
    expect(radio(wrapper, 'markitdown').attributes('disabled')).toBeUndefined()
    expect(chip(wrapper, 'markitdown').attributes('title')).toBeUndefined()
  })

  it('zeigt eine nicht installierte Engine deaktiviert mit Grund', () => {
    const wrapper = render(['markitdown'], { docling: 'unavailable' })
    const docling = radio(wrapper, 'docling')
    expect(docling.attributes('disabled')).toBeDefined()
    expect(chip(wrapper, 'docling').attributes('title')).toBe('nicht installiert')
  })

  it('laesst eine ladende Engine waehlbar und kennzeichnet sie', () => {
    const wrapper = render(['markitdown', 'docling'], { docling: 'warming' })
    expect(radio(wrapper, 'docling').attributes('disabled')).toBeUndefined()
    expect(wrapper.get('[data-test="engine-choice-docling"]').text()).toContain('lädt noch')
  })

  it('meldet die Wahl nach aussen', async () => {
    const wrapper = render()
    await radio(wrapper, 'docling').setValue()
    expect(wrapper.emitted('update:modelValue')![0]![0]).toBe('docling')
  })
})
