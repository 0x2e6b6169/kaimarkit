<script setup lang="ts">
/**
 * Webseiten wandeln: ein mehrzeiliges Feld, eine Adresse je Zeile.
 *
 * Die Komponente entscheidet nichts über eine Adresse außer dem Offensichtlichen.
 * Sie wirft Leerzeilen und Leerraum weg und hält zurück, was weder mit `http://`
 * noch mit `https://` beginnt — dafür braucht es keinen Aufruf. Alles Weitere
 * prüft der Dienst: ob der Name auflöst, ob er ins offene Netz zeigt, ob dort
 * ein Dokument liegt. Seine Meldung landet als `failed` an der Zeile in der
 * Warteschlange, nicht hier.
 *
 * Was liegen blieb, bleibt stehen. Das gilt für beide Fälle, aus demselben
 * Grund: Wäre die Zeile weg, ließe sie sich weder berichtigen noch wiederholen.
 * Eine Zeile ohne Schema bleibt sofort stehen und wird zusätzlich benannt.
 * Eine gültige geht hinaus und kommt zurück, wenn die Warteschlange keinen Platz
 * mehr hat — über ihre Grenze `limits.max_files` entscheidet sie selbst. Dass es
 * an der Grenze lag, sagt die Seite; welche Adressen es traf, zeigt das Feld.
 *
 * Nur was wirklich in der Warteschlange steht, verschwindet daraus. Die Seite
 * gibt dafür `keep` zurück, sobald sie die Adressen weitergereicht hat.
 */
import { computed, ref } from 'vue'

const emit = defineEmits<{
  /** Die abgeschickten Adressen, in der Reihenfolge der Zeilen. */
  urls: [string[]]
}>()

withDefaults(defineProps<{ disabled?: boolean }>(), { disabled: false })

const text = ref('')
const rejected = ref<string[]>([])

/** Die zuletzt abgeschickten Zeilen — `keep` stellt daraus ihre Reihenfolge her. */
let submitted: string[] = []

/** Die Zeilen ohne Leerraum und ohne die leeren. */
const lines = computed(() =>
  text.value
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.length > 0),
)

function hasScheme(line: string): boolean {
  return /^https?:\/\//i.test(line)
}

function submit(): void {
  submitted = lines.value
  const accepted = submitted.filter(hasScheme)
  rejected.value = submitted.filter((line) => !hasScheme(line))
  text.value = rejected.value.join('\n')
  if (accepted.length) emit('urls', accepted)
}

/**
 * Legt die Adressen zurück ins Feld, die keinen Platz mehr fanden.
 *
 * Die Warteschlange nimmt der Reihe nach auf, liegen bleibt also das Ende des
 * Stapels. Zusammen mit den Zeilen ohne Schema steht danach wieder da, was
 * nicht durchkam — in der eingegebenen Reihenfolge.
 */
function keep(unplaced: readonly string[]): void {
  if (!unplaced.length) return
  const placed = submitted.filter(hasScheme).length - unplaced.length
  let seen = 0
  text.value = submitted
    .filter((line) => {
      if (!hasScheme(line)) return true
      seen += 1
      return seen > placed
    })
    .join('\n')
}

defineExpose({ keep })
</script>

<template>
  <section class="flex flex-col gap-2" aria-labelledby="url-input-label">
    <label id="url-input-label" for="url-input" class="text-sm font-medium">
      Webseiten, eine Adresse je Zeile
    </label>

    <!--
      Den sichtbaren Fokusrahmen bringt die Regel `*:focus-visible` aus
      `style.css` mit; hier ist nichts nachzubauen.
    -->
    <textarea
      id="url-input"
      v-model="text"
      rows="3"
      spellcheck="false"
      class="w-full rounded border border-slate-400 bg-white px-3 py-2 font-mono text-sm text-slate-800 disabled:opacity-50"
      :disabled="disabled"
      :aria-invalid="rejected.length ? 'true' : undefined"
      :aria-describedby="rejected.length ? 'url-input-rejected' : undefined"
      placeholder="https://example.com/"
    ></textarea>

    <div class="flex flex-wrap items-center gap-x-3 gap-y-2">
      <button
        type="button"
        class="rounded border border-slate-400 px-3 py-1 text-sm font-medium hover:bg-slate-100 disabled:opacity-50"
        data-test="url-submit"
        :disabled="disabled || !lines.length"
        @click="submit"
      >
        Webseiten wandeln
      </button>
    </div>

    <p
      v-if="rejected.length"
      id="url-input-rejected"
      role="alert"
      class="rounded border border-amber-300 bg-amber-50 p-3 text-sm text-amber-900"
      data-test="url-rejected"
    >
      Nicht abgeschickt — eine Adresse beginnt mit <code>http://</code> oder
      <code>https://</code>:
      <span class="mt-1 block font-mono break-all">{{ rejected.join(' · ') }}</span>
    </p>
  </section>
</template>
