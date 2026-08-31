<script setup lang="ts">
/**
 * Die Warteschlange als Liste: eine Zeile je Datei, in der Reihenfolge des
 * Hinzufuegens.
 *
 * Jede Zeile erscheint sofort, noch bevor die Konvertierung beginnt. Wer fuenf
 * Dateien ablegt, sieht fuenf Zeilen — auch dann, wenn nur zwei davon laufen.
 *
 * Jede Statusaenderung wird zusaetzlich in einem `aria-live`-Bereich angesagt.
 * Ohne ihn erfaehrt niemand, der nicht auf den Bildschirm sieht, dass eine
 * Datei fertig ist.
 *
 * Die Komponente haelt nur, welche Zeilen aufgeklappt sind. Die Eintraege
 * selbst gehoeren `useConversion`; entfernt wird dort, nicht hier.
 */
import { ref, watch } from 'vue'
import FileRow from './FileRow.vue'
import type { QueueEntry, QueueStatus } from '../composables/useConversion'

const props = defineProps<{ entries: QueueEntry[] }>()

const emit = defineEmits<{ remove: [number] }>()

const expanded = ref<number[]>([])

function toggle(id: number): void {
  const index = expanded.value.indexOf(id)
  if (index >= 0) expanded.value.splice(index, 1)
  else expanded.value.push(id)
}

/**
 * Die Ansagen sammeln sich, statt einander zu ersetzen. Zwei Aenderungen liegen
 * oft nur einen Durchlauf auseinander — eine Datei scheitert, die naechste
 * startet —, und ein Bereich mit nur einer Zeile ueberschreibt die erste Ansage,
 * bevor sie jemand gehoert hat. Ein `role="log"` liest neu hinzugekommene
 * Absaetze der Reihe nach vor.
 */
const announcements = ref<{ id: number; text: string }[]>([])
let nextAnnouncement = 1

function sentence(entry: QueueEntry): string {
  switch (entry.status) {
    case 'running':
      return `${entry.filename} wird konvertiert.`
    case 'ok':
      return entry.warnings.length
        ? `${entry.filename} ist fertig, mit ${entry.warnings.length} ${
            entry.warnings.length === 1 ? 'Warnung' : 'Warnungen'
          }.`
        : `${entry.filename} ist fertig.`
    case 'failed':
      return `${entry.filename} ist fehlgeschlagen: ${entry.error ?? 'ohne Meldung'}`
    default:
      return `${entry.filename} wartet.`
  }
}

/**
 * Der zuletzt angesagte Zustand je Zeile. Eine neue Zeile gilt als `queued`,
 * auch wenn sie schon laufend hereinkommt: Die Warteschlange startet die ersten
 * beiden Dateien noch im selben Durchlauf, und ohne diese Annahme bliebe genau
 * deren Start unangesagt.
 */
const announced = new Map<number, QueueStatus>()
for (const entry of props.entries) announced.set(entry.id, entry.status)

watch(
  () => props.entries.map((entry) => [entry.id, entry.status] as const),
  () => {
    const messages: string[] = []
    const present = new Set<number>()
    for (const entry of props.entries) {
      present.add(entry.id)
      if ((announced.get(entry.id) ?? 'queued') !== entry.status) messages.push(sentence(entry))
      announced.set(entry.id, entry.status)
    }
    for (const id of [...announced.keys()]) if (!present.has(id)) announced.delete(id)
    for (const text of messages) announcements.value.push({ id: nextAnnouncement++, text })
    // Aeltere Ansagen sind laengst vorgelesen und muessen nicht stehen bleiben.
    const surplus = announcements.value.length - 10
    if (surplus > 0) announcements.value.splice(0, surplus)
  },
)
</script>

<template>
  <div>
    <div class="sr-only" role="log" aria-live="polite">
      <p v-for="item in announcements" :key="item.id">{{ item.text }}</p>
    </div>

    <p v-if="!entries.length" class="text-slate-600">Noch keine Dateien ausgewaehlt.</p>

    <ul v-else aria-label="Warteschlange" class="space-y-2">
      <FileRow
        v-for="entry in entries"
        :key="entry.id"
        :entry="entry"
        :expanded="expanded.includes(entry.id)"
        @toggle="toggle"
        @remove="emit('remove', $event)"
      >
        <!--
          Durchgereicht, nicht gefuellt: Die Warteschlange kennt keine Vorschau.
          `v-if` haelt den Rueckfall aus `FileRow` am Leben — ein Slot, den
          niemand fuellt, wuerde ihn sonst durch nichts ersetzen.
        -->
        <template v-if="$slots.preview" #preview="slotProps">
          <slot name="preview" v-bind="slotProps" />
        </template>
      </FileRow>
    </ul>
  </div>
</template>
