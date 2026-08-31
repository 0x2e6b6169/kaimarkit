<script setup lang="ts">
/**
 * Eine Zeile der Warteschlange: Name, Zustand, Warnungen, Meldung.
 *
 * Der Zustand steht nie allein in einer Farbe. Jede Zeile nennt ihn zusaetzlich
 * als Symbol und als Wort — wer Farben nicht unterscheiden kann, liest denselben
 * Befund.
 *
 * Warnungen stehen an der Zeile und nicht erst in der Vorschau. Genau dort
 * entscheidet sich, ob das Ergebnis taugt.
 *
 * Aufgeklappt zeigt die Zeile den Slot `preview`. FE-4 haengt dort
 * `MarkdownPreview` ein; ohne Fuellung steht ein Platzhalter.
 */
import { computed } from 'vue'
import type { QueueEntry, QueueStatus } from '../composables/useConversion'

const props = defineProps<{
  entry: QueueEntry
  expanded?: boolean
}>()

const emit = defineEmits<{
  /** Aufklappen oder zuklappen; die Warteschlange fuehrt darueber Buch. */
  toggle: [number]
  remove: [number]
}>()

interface Badge {
  symbol: string
  label: string
  class: string
}

const BADGES: Record<QueueStatus, Badge> = {
  queued: { symbol: '◦', label: 'wartet', class: 'text-slate-600' },
  running: { symbol: '◐', label: 'laeuft', class: 'text-sky-700' },
  ok: { symbol: '✓', label: 'fertig', class: 'text-emerald-700' },
  failed: { symbol: '✗', label: 'fehlgeschlagen', class: 'text-red-700' },
}

const badge = computed(() => BADGES[props.entry.status])

/** Engine und Dauer, sobald sie feststehen. */
const meta = computed(() => {
  const parts: string[] = []
  if (props.entry.engine) parts.push(props.entry.engine)
  if (props.entry.durationMs !== null) parts.push(`${props.entry.durationMs} ms`)
  return parts.join(' · ')
})

const canExpand = computed(() => props.entry.markdown !== null)

const previewId = computed(() => `file-row-${props.entry.id}-preview`)
</script>

<template>
  <li class="rounded border border-slate-300 bg-white p-3">
    <div class="flex flex-wrap items-center gap-x-3 gap-y-1">
      <span aria-hidden="true" :class="badge.class" class="text-lg leading-none">
        {{ badge.symbol }}
      </span>
      <span class="min-w-0 flex-1 truncate font-medium">{{ entry.filename }}</span>
      <span :class="badge.class" class="text-sm">{{ badge.label }}</span>
      <span v-if="meta" class="text-sm text-slate-600">{{ meta }}</span>

      <button
        v-if="canExpand"
        type="button"
        class="rounded border border-slate-400 px-2 py-1 text-sm hover:bg-slate-100"
        :aria-expanded="expanded === true"
        :aria-controls="previewId"
        @click="emit('toggle', entry.id)"
      >
        {{ expanded ? 'Zuklappen' : 'Aufklappen' }}
      </button>

      <button
        type="button"
        class="rounded border border-slate-400 px-2 py-1 text-sm hover:bg-slate-100"
        @click="emit('remove', entry.id)"
      >
        Entfernen<span class="sr-only"> — {{ entry.filename }}</span>
      </button>
    </div>

    <p v-if="entry.error" class="mt-2 rounded border border-red-300 bg-red-50 p-2 text-sm text-red-900">
      {{ entry.error }}
    </p>

    <div
      v-if="entry.warnings.length"
      class="mt-2 rounded border border-amber-300 bg-amber-50 p-2 text-sm text-amber-900"
    >
      <p class="font-medium">
        {{ entry.warnings.length === 1 ? 'Warnung' : 'Warnungen' }}
      </p>
      <ul class="list-disc pl-5">
        <li v-for="warning in entry.warnings" :key="warning">{{ warning }}</li>
      </ul>
    </div>

    <div v-if="canExpand && expanded" :id="previewId" class="mt-2">
      <slot name="preview" :entry="entry">
        <p class="rounded bg-slate-100 p-2 text-sm text-slate-600">
          Die Vorschau folgt mit FE-4. Bis dahin steht hier nur, dass
          {{ entry.markdown?.length ?? 0 }} Zeichen Markdown vorliegen.
        </p>
      </slot>
    </div>
  </li>
</template>
