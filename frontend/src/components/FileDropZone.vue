<script setup lang="ts">
/**
 * Die Dropzone: Dateien hineinziehen oder ueber den Dateidialog auswaehlen.
 *
 * Der Ablagebereich ist ein echter `<button>`. Er ist damit von Haus aus
 * fokussierbar, Leertaste und Eingabetaste oeffnen den Dialog, und Screenreader
 * kuendigen ihn als Schaltflaeche an. Ein `<div role="button">` muesste all das
 * nachbauen und waere an jeder einzelnen Stelle ein Stueck schlechter.
 *
 * Die Komponente entscheidet nichts ueber die Dateien. Sie meldet, was
 * hereinkam; was davon konvertiert wird, bestimmt die Warteschlange.
 */
import { computed, ref } from 'vue'

const props = withDefaults(
  defineProps<{
    /** Endungen samt Punkt fuer den Dateidialog, etwa `['.pdf', '.docx']`. */
    extensions?: string[]
    disabled?: boolean
  }>(),
  { extensions: () => [], disabled: false },
)

const emit = defineEmits<{
  /** Die hereingekommenen Dateien, in der Reihenfolge der Auswahl. */
  files: [File[]]
}>()

const input = ref<HTMLInputElement | null>(null)

/**
 * Ein Zaehler, kein Schalter: `dragleave` feuert auch beim Wechsel von der
 * Flaeche auf ein Kindelement. Ein Schalter liesse die Hervorhebung dabei
 * flackern.
 */
const depth = ref(0)
const dragging = computed(() => depth.value > 0)

const accept = computed(() =>
  props.extensions.length ? props.extensions.join(',') : undefined,
)

const hint = computed(() =>
  props.extensions.length ? props.extensions.join(' · ') : 'alle unterstützten Formate',
)

function openDialog(): void {
  input.value?.click()
}

function onChange(event: Event): void {
  const target = event.target as HTMLInputElement
  emitFiles(target.files)
  // Zuruecksetzen, damit dieselbe Datei ein zweites Mal gewaehlt werden kann.
  target.value = ''
}

function onDragEnter(): void {
  if (props.disabled) return
  depth.value += 1
}

function onDragLeave(): void {
  depth.value = Math.max(0, depth.value - 1)
}

function onDrop(event: DragEvent): void {
  depth.value = 0
  if (props.disabled) return
  emitFiles(event.dataTransfer?.files ?? null)
}

function emitFiles(list: FileList | File[] | null): void {
  const files = list ? Array.from(list) : []
  if (files.length) emit('files', files)
}
</script>

<template>
  <div>
    <button
      type="button"
      class="flex w-full flex-col items-center gap-2 rounded-lg border-2 border-dashed px-6 py-10 text-center transition-colors disabled:cursor-not-allowed disabled:opacity-50"
      :class="
        dragging
          ? 'border-sky-500 bg-sky-50 text-sky-900'
          : 'border-slate-400 bg-white text-slate-800 hover:bg-slate-50'
      "
      :disabled="disabled"
      @click="openDialog"
      @dragenter.prevent="onDragEnter"
      @dragover.prevent
      @dragleave.prevent="onDragLeave"
      @drop.prevent="onDrop"
    >
      <span aria-hidden="true" class="text-3xl leading-none">⤓</span>
      <span class="text-lg font-medium">
        {{ dragging ? 'Zum Hinzufügen loslassen' : 'Dateien hierher ziehen oder auswählen' }}
      </span>
      <span class="text-sm text-slate-600">{{ hint }}</span>
    </button>

    <!--
      Der Dialog haengt an dieser Eingabe. Sie ist ausgeblendet und aus der
      Tabreihenfolge genommen: Die Schaltflaeche darueber oeffnet sie, ein
      zweiter Halt fuer dieselbe Handlung waere nur im Weg.
    -->
    <input
      ref="input"
      type="file"
      multiple
      class="hidden"
      tabindex="-1"
      aria-hidden="true"
      :accept="accept"
      @change="onChange"
    />
  </div>
</template>
