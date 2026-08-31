<script setup lang="ts">
/**
 * Die Vorschau auf ein Ergebnis: gerendertes Markdown oder Rohtext.
 *
 * **Die Filterung ist der Zweck dieser Komponente, keine Beigabe.** Das Markdown
 * kommt aus fremden Dokumenten, und `markdown-it` laeuft hier mit `html: true` —
 * eine aus PDF oder docx gerettete Tabelle steht sonst als Quelltext auf der
 * Seite statt als Tabelle. Damit reicht jedes Dokument beliebiges HTML bis an
 * die Oberflaeche. Genau eine Stelle haelt es auf: `DOMPurify.sanitize()` in
 * `rendered`. Wer `v-html` in dieser Datei ohne diesen Aufruf fuellt, oeffnet
 * jedem hochgeladenen Dokument die Seite.
 *
 * Gerendert wird erst beim Aufklappen. `rendered` ist ein `computed` und steht
 * nur unter `v-if`, deshalb kostet ein zugeklapptes Ergebnis von zwei Megabyte
 * nichts.
 *
 * Die Komponente steht fuer sich: Sie kennt weder die Warteschlange noch die
 * Schnittstelle, sie bekommt fertiges Markdown gereicht.
 *
 *   <MarkdownPreview :markdown="entry.markdown" :filename="entry.filename"
 *                    v-model:open="offen" @copied="melden" />
 */

import { computed, onBeforeUnmount, ref } from 'vue'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

const props = withDefaults(
  defineProps<{
    /** Das Ergebnis. `null` oder leer heisst: es gibt noch nichts zu zeigen. */
    markdown: string | null
    /** Name der Eingabedatei, nur fuer die Beschriftung. */
    filename?: string
  }>(),
  { filename: '' },
)

/** Wird nach erfolgreichem Kopieren gemeldet, damit die Seite es ansagen kann. */
const emit = defineEmits<{ copied: [] }>()

/** Auf- und zugeklappt. Ohne `v-model:open` regelt die Komponente das selbst. */
const open = defineModel<boolean>('open', { default: false })

type Tab = 'rendered' | 'raw'
const tab = ref<Tab>('rendered')

const markdownIt = new MarkdownIt({ html: true, linkify: true, breaks: false })

const source = computed(() => props.markdown ?? '')
const hasResult = computed(() => source.value.length > 0)

/** Der einzige Weg, auf dem HTML in die Seite gelangt — und er fuehrt durch DOMPurify. */
const rendered = computed(() => DOMPurify.sanitize(markdownIt.render(source.value)))

type CopyState = 'idle' | 'done' | 'failed'
const copyState = ref<CopyState>('idle')
let copyTimer: ReturnType<typeof setTimeout> | undefined

function flash(state: CopyState): void {
  copyState.value = state
  clearTimeout(copyTimer)
  copyTimer = setTimeout(() => {
    copyState.value = 'idle'
  }, 2000)
}

async function copy(): Promise<void> {
  if (!hasResult.value) return
  try {
    // Ohne sicheren Kontext gibt es keine Zwischenablage. Dann meldet die
    // Schaltflaeche den Fehlschlag, statt still nichts zu tun.
    await navigator.clipboard.writeText(source.value)
    flash('done')
    emit('copied')
  } catch {
    flash('failed')
  }
}

onBeforeUnmount(() => clearTimeout(copyTimer))

const copyLabel = computed(() =>
  copyState.value === 'done'
    ? 'Kopiert'
    : copyState.value === 'failed'
      ? 'Kopieren ging nicht'
      : 'Kopieren',
)
</script>

<template>
  <section class="rounded-lg border border-slate-300 dark:border-slate-700">
    <header class="flex items-center gap-2 px-3 py-2">
      <button
        type="button"
        class="flex-1 truncate text-left font-medium"
        :aria-expanded="open"
        @click="open = !open"
      >
        <span aria-hidden="true" class="inline-block w-4">{{ open ? '▾' : '▸' }}</span>
        {{ filename || 'Ergebnis' }}
      </button>

      <button
        type="button"
        class="rounded border border-slate-300 px-2 py-1 text-sm disabled:opacity-50 dark:border-slate-700"
        :disabled="!hasResult"
        @click="copy"
      >
        {{ copyLabel }}
      </button>
      <span role="status" class="sr-only">
        {{ copyState === 'done' ? 'In die Zwischenablage kopiert.' : '' }}
        {{ copyState === 'failed' ? 'Kopieren in die Zwischenablage ging nicht.' : '' }}
      </span>
    </header>

    <div v-if="open" class="border-t border-slate-300 dark:border-slate-700">
      <div v-if="!hasResult" class="px-3 py-4 text-sm text-slate-500">
        Noch kein Ergebnis.
      </div>

      <template v-else>
        <!--
          Beide Reiter stehen in der Tabreihenfolge. Der ARIA-Entwurf laesst
          dafuer zwei Wege: wandernder Fokus mit Pfeiltasten, oder jeder Reiter
          einzeln per Tabulator erreichbar. Der erste Weg stand hier ohne die
          Pfeiltasten, die er braucht — „Rohtext" trug `tabindex="-1"` und war
          damit fuer die Tastatur nicht erreichbar. Bei zwei Reitern ist der
          zweite Weg der kuerzere.
        -->
        <div role="tablist" aria-label="Darstellung" class="flex gap-1 px-3 pt-2">
          <button
            id="tab-rendered"
            type="button"
            role="tab"
            aria-controls="panel-rendered"
            :aria-selected="tab === 'rendered'"
            class="rounded-t px-3 py-1 text-sm"
            :class="tab === 'rendered' ? 'bg-slate-200 dark:bg-slate-800' : ''"
            @click="tab = 'rendered'"
          >
            Vorschau
          </button>
          <button
            id="tab-raw"
            type="button"
            role="tab"
            aria-controls="panel-raw"
            :aria-selected="tab === 'raw'"
            class="rounded-t px-3 py-1 text-sm"
            :class="tab === 'raw' ? 'bg-slate-200 dark:bg-slate-800' : ''"
            @click="tab = 'raw'"
          >
            Rohtext
          </button>
        </div>

        <!-- eslint-disable-next-line vue/no-v-html -- gefiltert in `rendered`, siehe Kopf -->
        <div
          v-if="tab === 'rendered'"
          id="panel-rendered"
          role="tabpanel"
          aria-labelledby="tab-rendered"
          tabindex="0"
          class="markdown-body px-3 py-2"
          data-test="rendered"
          v-html="rendered"
        />

        <pre
          v-else
          id="panel-raw"
          role="tabpanel"
          aria-labelledby="tab-raw"
          tabindex="0"
          class="raw px-3 py-2"
          data-test="raw"
          >{{ source }}</pre
        >
      </template>
    </div>
  </section>
</template>

<style scoped>
/*
 * Breites Ergebnis scrollt in seinem eigenen Bereich. Ohne das schiebt eine
 * Tabelle aus einem quer gesetzten PDF die ganze Seite waagerecht.
 */
.markdown-body,
.raw {
  max-width: 100%;
  overflow-x: auto;
}

.raw {
  white-space: pre;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.85rem;
}

.markdown-body :deep(table) {
  display: block;
  max-width: 100%;
  overflow-x: auto;
  border-collapse: collapse;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  border: 1px solid currentColor;
  padding: 0.25rem 0.5rem;
}

.markdown-body :deep(pre) {
  max-width: 100%;
  overflow-x: auto;
  padding: 0.5rem;
  font-size: 0.85rem;
}

.markdown-body :deep(img) {
  max-width: 100%;
  height: auto;
}
</style>
