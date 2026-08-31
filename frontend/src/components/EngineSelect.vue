<script setup lang="ts">
/**
 * Die Enginewahl als Auswahlfeld.
 *
 * Die Komponente entscheidet nichts. Welche Engines hier stehen, bestimmt das
 * `OptionsPanel` aus `/api/capabilities` und aus den Dateien, die in der
 * Warteschlange liegen. Hier wird nur dargestellt und gemeldet.
 *
 * Der Zustand einer Engine steht am Eintrag: `warming` heisst, das Modell laedt
 * noch — waehlbar ist die Engine trotzdem, die erste Anfrage wartet eben.
 * `unavailable` erscheint gar nicht erst; solche Engines siebt das Panel aus.
 */

import type { EngineState } from '../types'

const props = defineProps<{
  /** Der gewaehlte Enginename oder `auto`. */
  modelValue: string
  /** Die waehlbaren Engines, in der Reihenfolge der Praeferenz. */
  engines: string[]
  /** Der Zustand je Engine aus `/api/capabilities`. */
  states: Record<string, EngineState>
  /** Verbindet das Feld mit einem Label ausserhalb der Komponente. */
  id?: string
}>()

const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

/** Der Zusatz hinter dem Namen. Nur `warming` bekommt einen. */
function hint(engine: string): string {
  return props.states[engine] === 'warming' ? ' (laedt noch)' : ''
}

function onChange(event: Event): void {
  emit('update:modelValue', (event.target as HTMLSelectElement).value)
}
</script>

<template>
  <select
    :id="id"
    class="rounded border border-slate-400 bg-white px-2 py-1.5 text-sm"
    :value="modelValue"
    data-test="engine-select"
    @change="onChange"
  >
    <option value="auto">automatisch</option>
    <option v-for="engine in engines" :key="engine" :value="engine">
      {{ engine }}{{ hint(engine) }}
    </option>
  </select>
</template>
