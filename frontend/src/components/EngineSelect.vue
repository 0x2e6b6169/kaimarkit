<script setup lang="ts">
/**
 * Die Enginewahl als Auswahlfeld, mit einem Satz zu jeder Engine daneben.
 *
 * Die Komponente entscheidet nichts. Welche Engines hier stehen, bestimmt das
 * `OptionsPanel` aus `/api/capabilities` und aus den Dateien, die in der
 * Warteschlange liegen. Hier wird nur dargestellt und gemeldet.
 *
 * Der Zustand einer Engine steht am Eintrag: `warming` heisst, das Modell laedt
 * noch — waehlbar ist die Engine trotzdem, die erste Anfrage wartet eben.
 * `unavailable` erscheint gar nicht erst; solche Engines siebt das Panel aus.
 *
 * ## Warum unter der Auswahl ein Hinweis steht
 *
 * Die Namen allein sagen nichts darueber, worauf man sich einlaesst. Zwischen
 * den Engines liegen mehrere Zehnerpotenzen: dasselbe PDF braucht bei docling
 * Sekunden bis Minuten, bei markitdown den Bruchteil einer Sekunde — und das
 * schnelle Ergebnis ist nicht durchweg das schlechtere. Wer das erst an der
 * Zeitgrenze merkt, hat die Wahl nie gehabt.
 *
 * Der Hinweis steht deshalb offen unter der Auswahl, nicht in einem Tooltip:
 * Er ist ohne Maus zu lesen, und `aria-describedby` haengt ihn an das Feld, so
 * dass ein Screenreader ihn beim Anspringen mitliest. Die Voreinstellung
 * bleibt `automatisch`; gewaehlt wird hier nach wie vor von Hand.
 */

import { computed, useId } from 'vue'
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

/**
 * Je Engine ein Satz, der Dauer und Vollstaendigkeit gegeneinanderstellt.
 *
 * Nur fuer die beiden Engines, bei denen die Wahl etwas kostet. pandoc steht
 * nicht darin: Es liest Formate, die sonst niemand liest, und stellt damit
 * keine Wahl zwischen schnell und gruendlich.
 */
const NOTES: Record<string, string> = {
  docling:
    'docling liest gründlich und braucht dafür oft Minuten je Dokument. ' +
    'Bei gescannten Seiten ohne Textebene führt kein Weg daran vorbei.',
  markitdown:
    'markitdown ist nach Sekundenbruchteilen fertig, verliert dabei aber ' +
    'gelegentlich eine Tabelle oder das Layout.',
}

/** Eine eigene Kennung, damit `aria-describedby` auch ohne `id`-Prop greift. */
const notesId = `engine-notes-${useId()}`

const notes = computed(() =>
  props.engines
    .filter((engine) => engine in NOTES)
    .map((engine) => ({ engine, text: NOTES[engine] as string })),
)

/** Der Zusatz hinter dem Namen. Nur `warming` bekommt einen. */
function hint(engine: string): string {
  return props.states[engine] === 'warming' ? ' (lädt noch)' : ''
}

function onChange(event: Event): void {
  emit('update:modelValue', (event.target as HTMLSelectElement).value)
}
</script>

<template>
  <div class="flex flex-col gap-1">
    <select
      :id="id"
      class="self-start rounded border border-slate-400 bg-white px-2 py-1.5 text-sm"
      :value="modelValue"
      :aria-describedby="notes.length > 0 ? notesId : undefined"
      data-test="engine-select"
      @change="onChange"
    >
      <option value="auto">automatisch</option>
      <option v-for="engine in engines" :key="engine" :value="engine">
        {{ engine }}{{ hint(engine) }}
      </option>
    </select>

    <ul
      v-if="notes.length > 0"
      :id="notesId"
      class="max-w-prose space-y-0.5 text-xs text-slate-500"
      data-test="engine-notes"
    >
      <li v-for="note in notes" :key="note.engine" :data-test="'engine-note-' + note.engine">
        {{ note.text }}
      </li>
    </ul>
  </div>
</template>
