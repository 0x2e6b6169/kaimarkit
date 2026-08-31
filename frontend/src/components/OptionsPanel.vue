<script setup lang="ts">
/**
 * Die Optionen fuer den naechsten Lauf: welche Engine, und ob mit OCR.
 *
 * Der Leitsatz: Angeboten wird nur, was gelingen kann. Welche Engines es
 * ueberhaupt gibt und ob OCR zur Verfuegung steht, meldet `/api/capabilities`
 * ueber `useCapabilities()`. Diese Komponente kennt keinen Enginenamen; sie
 * liest die Faehigkeitsmatrix und leitet daraus die Auswahl ab. Kommt eine
 * vierte Engine hinzu, aendert sich hier nichts.
 *
 * Zwei Filter greifen nacheinander:
 *
 * 1. **Das Format.** Liegen Dateien in der Warteschlange, bleiben nur die
 *    Engines uebrig, die *jede* dieser Endungen lesen koennen. Bei einer
 *    einzelnen `.epub` faellt docling deshalb heraus.
 * 2. **Der Zustand.** `warming` bleibt waehlbar und wird gekennzeichnet — das
 *    Modell laedt noch, die erste Anfrage wartet. `unavailable` erscheint nicht.
 *
 * Faellt die gewaehlte Engine durch einen dieser Filter, springt die Auswahl auf
 * `automatisch` zurueck. Sonst stuende dort ein Name, den der Dienst mit 400
 * zurueckwiese.
 *
 * Die Optionen gelten fuer den naechsten Start, nicht rueckwirkend: Was bereits
 * konvertiert ist, bleibt, wie es ist.
 */

import { computed, onMounted, watch } from 'vue'
import EngineSelect from './EngineSelect.vue'
import { useCapabilities } from '../composables/useCapabilities'
import type { ConvertOptions } from '../types'

const props = withDefaults(
  defineProps<{
    /** Engine und OCR fuer den naechsten Lauf — die Optionen aus `useConversion()`. */
    modelValue: ConvertOptions
    /** Die Dateien in der Warteschlange. Sie schraenken die Enginewahl ein. */
    filenames?: string[]
  }>(),
  { filenames: () => [] },
)

const emit = defineEmits<{ 'update:modelValue': [value: ConvertOptions] }>()

const { engines, ocrAvailable, enginesFor, supports, loading, error, load } = useCapabilities()

onMounted(() => void load())

/**
 * Die waehlbaren Engines. Ohne Dateien sind es alle nutzbaren; mit Dateien nur
 * die, die alle Endungen lesen koennen. Dateien in einem Format, das der Dienst
 * gar nicht kennt, bleiben ausser Betracht — sie scheitern ohnehin, und ihre
 * leere Liste wuerde sonst jede Engine wegschneiden.
 */
const offered = computed<string[]>(() => {
  const usable = (name: string) => engines.value[name] !== 'unavailable'
  const known = props.filenames.filter((filename) => supports(filename))

  if (known.length === 0) return Object.keys(engines.value).filter(usable)

  const lists = known.map((filename) => enginesFor(filename))
  const [first, ...rest] = lists
  return (first ?? []).filter(
    (engine) => usable(engine) && rest.every((list) => list.includes(engine)),
  )
})

const engine = computed(() => props.modelValue.engine)

function update(patch: Partial<ConvertOptions>): void {
  emit('update:modelValue', { ...props.modelValue, ...patch })
}

// Eine Engine, die aus der Auswahl gefallen ist, darf nicht gewaehlt bleiben.
watch(offered, (list) => {
  if (engine.value !== 'auto' && !list.includes(engine.value)) update({ engine: 'auto' })
})

function onOcrChange(event: Event): void {
  update({ ocr: (event.target as HTMLInputElement).checked })
}
</script>

<template>
  <section class="space-y-3" aria-labelledby="options-heading" data-test="options-panel">
    <h2 id="options-heading" class="text-lg font-medium">Optionen</h2>

    <p v-if="error" class="text-sm text-red-700" data-test="options-error">{{ error }}</p>
    <p v-else-if="loading" class="text-sm text-slate-500">Faehigkeiten werden geladen …</p>

    <div class="flex flex-wrap items-center gap-x-6 gap-y-3">
      <div class="flex items-center gap-2">
        <label for="options-engine" class="text-sm">Engine</label>
        <EngineSelect
          id="options-engine"
          :model-value="engine"
          :engines="offered"
          :states="engines"
          @update:model-value="update({ engine: $event })"
        />
      </div>

      <!-- Der OCR-Schalter steht nur da, wenn das Backend OCR meldet. -->
      <div v-if="ocrAvailable" class="flex items-center gap-2" data-test="ocr-field">
        <input
          id="options-ocr"
          type="checkbox"
          class="size-4"
          data-test="ocr-switch"
          :checked="modelValue.ocr === true"
          @change="onOcrChange"
        />
        <label for="options-ocr" class="text-sm">Text in Bildern erkennen (OCR)</label>
        <span v-if="modelValue.ocr === null" class="text-xs text-slate-500">
          folgt der Voreinstellung des Dienstes
        </span>
      </div>
    </div>

    <p class="text-xs text-slate-500">
      Die Optionen gelten fuer den naechsten Lauf. Bereits konvertierte Dateien bleiben,
      wie sie sind.
    </p>
  </section>
</template>
