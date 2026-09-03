<script setup lang="ts">
/**
 * Die Enginewahl als Schaltergruppe: genau eine ist gewaehlt, neben jedem Namen
 * steht ein Halbsatz, und ein Info-Zeichen dahinter oeffnet die laengere
 * Erklaerung (GitHub #3).
 *
 * Die Komponente entscheidet nichts. Welche Engines es gibt, steht in `states`
 * (aus `/api/capabilities`); welche davon gerade in Frage kommen, bestimmt das
 * `OptionsPanel` aus den Dateien in der Warteschlange und uebergibt sie als
 * `engines`. Hier wird nur dargestellt und gemeldet.
 *
 * Eine Engine, die nicht in Frage kommt, bleibt als Schaltflaeche stehen und
 * ist deaktiviert, mit dem Grund im `title`. Sonst aenderte die Gruppe ihre
 * Form mit jeder Datei, die in die Warteschlange faellt. `warming` bleibt
 * waehlbar und wird gekennzeichnet: Das Modell laedt noch, die erste Anfrage
 * wartet eben.
 *
 * ## Warum echte Radioschalter
 *
 * `<input type="radio">` in einem `<fieldset>` bringen Pfeiltasten und die
 * Semantik fuer Screenreader mit. Wer stattdessen `<button role="radio">`
 * baut, baut die Tastaturbedienung nach.
 *
 * ## Warum die Erklaerung auch ohne Maus zu erreichen ist
 *
 * Zwischen den Engines liegen mehrere Zehnerpotenzen: dasselbe PDF braucht bei
 * docling Sekunden bis Minuten, bei markitdown den Bruchteil einer Sekunde —
 * und das schnelle Ergebnis ist nicht durchweg das schlechtere. Wer das erst
 * an der Zeitgrenze merkt, hat die Wahl nie gehabt. Der Halbsatz steht deshalb
 * offen neben dem Namen. Die Erklaerung dahinter erscheint bei Hover **und**
 * bei Tastaturfokus auf dem Info-Zeichen, schliesst mit Escape und haengt per
 * `aria-describedby` am Zeichen, so dass ein Screenreader sie beim Anspringen
 * mitliest — ob sie gerade sichtbar ist oder nicht.
 *
 * ## Die Texte
 *
 * Nur die Tabelle `TEXTS` kennt Enginenamen. Angeboten wird, was `states`
 * nennt; ein Name ohne Eintrag bekommt keinen Text und keinen Fehler. Die
 * Aussagen stammen aus `docs/formate.md`, Abschnitte „Docling", „MarkItDown"
 * und „Pandoc"; wer dort etwas aendert, aendert es hier mit.
 */

import { computed, ref, useId } from 'vue'
import type { EngineState } from '../types'

const props = defineProps<{
  /** Der gewaehlte Enginename oder `auto`. */
  modelValue: string
  /** Die Engines, die gerade in Frage kommen. */
  engines: string[]
  /** Der Zustand je Engine aus `/api/capabilities`. Nennt alle, die es gibt, und gibt die Reihenfolge vor. */
  states: Record<string, EngineState>
}>()

const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

interface Texts {
  /** Ein Halbsatz neben dem Namen. */
  short: string
  /** Drei bis fuenf Saetze hinter dem Info-Zeichen. */
  long: string
}

const TEXTS: Record<string, Texts> = {
  auto: {
    short: 'wählt je Dateiendung die erste Engine, die der Dienst dafür nennt',
    long:
      'Der Dienst wählt nach der Dateiendung die erste Engine seiner Präferenzliste, ' +
      'die gerade bereit ist. Scheitert sie, nimmt er die nächste; der Grund steht ' +
      'danach in den Warnungen. Solange Docling noch seine Modelle lädt, bekommt ' +
      'ein PDF deshalb MarkItDown.',
  },
  markitdown: {
    short: 'schnell, ohne Modelle, breite Formatliste',
    long:
      'MarkItDown kommt ohne Modelle und ohne OCR aus und ist nach Sekundenbruchteilen ' +
      'fertig. Aus einem PDF liest es nur die Textebene: Bilder hinterlassen dort keine ' +
      'Spur, und ein gescanntes PDF ergibt ein leeres Ergebnis mit einer Warnung. ' +
      'In .docx, .html und .epub steht von einem Bild nur der Alt-Text.',
  },
  docling: {
    short: 'gründlich, mit Layout, Tabellen und OCR, oft Minuten je Dokument',
    long:
      'Docling liest mit Layout- und Tabellenmodellen und braucht dafür oft Minuten je ' +
      'Dokument. Bei gescannten Seiten ohne Textebene führt kein Weg daran vorbei: Nur ' +
      'Docling schickt sie durch die Texterkennung. Bilder übernimmt es nicht, sondern ' +
      'setzt einen Platzhalter an ihre Stelle und nennt die Zahl in den Warnungen. ' +
      'Lädt es noch, wartet der Aufruf, bis die Modelle da sind.',
  },
  pandoc: {
    short: 'für .odt, .rtf, .tex, .rst, .org und ePub; liest kein PDF',
    long:
      'Pandoc bedient die Formate, die sonst niemand liest: .odt, .rtf, .tex, .rst und ' +
      '.org. Für ePub ist es die erste Wahl. PDF liest es nicht. Jeder Aufruf läuft in ' +
      'einer Sandbox, die nur die übergebene Datei sieht.',
  },
}

interface Choice {
  name: string
  label: string
  texts: Texts | null
  /** Der Grund, warum die Engine gerade nicht waehlbar ist; null, wenn sie es ist. */
  reason: string | null
}

/** Der Zusatz hinter dem Namen. Nur `warming` bekommt einen. */
function hint(engine: string): string {
  return props.states[engine] === 'warming' ? ' (lädt noch)' : ''
}

function reasonFor(engine: string): string | null {
  if (props.engines.includes(engine)) return null
  if (props.states[engine] === 'unavailable') return 'nicht installiert'
  return 'liest diese Dateien nicht'
}

/** `automatisch` zuerst, danach alle Engines, die der Dienst nennt. */
const choices = computed<Choice[]>(() => [
  { name: 'auto', label: 'automatisch', texts: TEXTS.auto ?? null, reason: null },
  ...Object.keys(props.states).map((name) => ({
    name,
    label: name + hint(name),
    texts: TEXTS[name] ?? null,
    reason: reasonFor(name),
  })),
])

/** Eine eigene Kennung je Instanz, damit `name`, `id` und `aria-describedby` nicht kollidieren. */
const uid = useId()
const groupName = `engine-${uid}`
const radioId = (name: string) => `engine-${uid}-${name}`
const longId = (name: string) => `engine-${uid}-${name}-long`

/** Die Engine, deren Erklaerung gerade offen ist. */
const open = ref<string | null>(null)

function onChange(event: Event): void {
  emit('update:modelValue', (event.target as HTMLInputElement).value)
}
</script>

<template>
  <fieldset class="flex flex-col gap-1.5" data-test="engine-select">
    <legend class="mb-1 text-sm">Engine</legend>

    <div
      v-for="choice in choices"
      :key="choice.name"
      class="flex flex-wrap items-center gap-x-2 gap-y-0.5"
      :data-test="'engine-choice-' + choice.name"
    >
      <label
        class="inline-flex items-center gap-2 rounded border border-slate-300 px-2 py-1 text-sm has-checked:border-sky-500 has-checked:bg-sky-50 has-disabled:opacity-50"
        :title="choice.reason ?? undefined"
      >
        <input
          :id="radioId(choice.name)"
          type="radio"
          class="size-4"
          :name="groupName"
          :value="choice.name"
          :checked="modelValue === choice.name"
          :disabled="choice.reason !== null"
          @change="onChange"
        />
        {{ choice.label }}
      </label>

      <template v-if="choice.texts">
        <span class="text-xs text-slate-500" :data-test="'engine-short-' + choice.name">
          {{ choice.texts.short }}
        </span>

        <span class="relative">
          <button
            type="button"
            class="size-5 rounded-full border border-slate-400 text-xs leading-none text-slate-600"
            :aria-label="'Erklärung zu ' + choice.label"
            :aria-describedby="longId(choice.name)"
            :aria-expanded="open === choice.name"
            :data-test="'engine-info-' + choice.name"
            @mouseenter="open = choice.name"
            @mouseleave="open = null"
            @focus="open = choice.name"
            @blur="open = null"
            @keydown.escape="open = null"
          >
            i
          </button>
          <p
            :id="longId(choice.name)"
            role="tooltip"
            class="absolute left-0 top-full z-10 mt-1 w-72 max-w-[calc(100vw-2rem)] rounded border border-slate-300 bg-white p-2 text-xs text-slate-600 shadow"
            :hidden="open !== choice.name"
            :data-test="'engine-long-' + choice.name"
          >
            {{ choice.texts.long }}
          </p>
        </span>
      </template>
    </div>
  </fieldset>
</template>
