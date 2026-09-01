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
 * Aufgeklappt zeigt die Zeile den Slot `preview`; die Anwendung haengt dort
 * `MarkdownPreview` ein. Fuellt ihn niemand, nennt die Zeile den Umfang des
 * Markdown — sonst stuende die aufgeklappte Zeile leer da.
 *
 * Der Knopf „Herunterladen" steht erst da, wenn ein Ergebnis vorliegt. Er legt
 * die Datei unmittelbar ab, statt den Wunsch nach oben zu melden: Was
 * heruntergeladen wird, steht vollstaendig im Eintrag dieser Zeile.
 *
 * Eine laufende Zeile laesst sich abbrechen. Der Knopf heisst „Nicht mehr
 * warten", und mehr sagt er auch nicht zu: Er beendet die Anfrage des Browsers.
 *
 * **Die schwache Beschriftung ist gemessen, nicht zaghaft.** BE-30 hat den
 * Abbruch nachgestellt: uvicorn bricht die ASGI-Aufgabe beim Verbindungsabbruch
 * nicht ab, der Handler laeuft bis zur Zeitgrenze weiter. Der Platz auf dem
 * Server blieb acht Sekunden laenger belegt, als der Aufruf fuer den Nutzer
 * ueberhaupt bestand. „Umwandlung stoppen" oder ein blankes „Abbrechen" waere
 * also nachweislich falsch: Der Nutzer bekommt seine Wartezeit zurueck, der
 * Dienst behaelt die Last. Wer den Text spaeter „schoener" macht, macht ihn
 * unwahr.
 *
 * Eine laufende Zeile zaehlt mit, wie lange sie schon laeuft. Docling braucht
 * Minuten je Dokument; ohne die Zahl haelt man den Dienst nach einer Minute fuer
 * haengengeblieben. Einen Fortschritt behauptet die Zeile nicht — das Backend
 * meldet nur Anfang und Ende, und ein Balken ohne Ende waere gelogen.
 */
import { computed, onUnmounted, ref, watch } from 'vue'
import { downloadMarkdown, hasResult } from '../download'
import type { QueueEntry, QueueStatus } from '../composables/useConversion'

const props = defineProps<{
  entry: QueueEntry
  expanded?: boolean
}>()

const emit = defineEmits<{
  /** Aufklappen oder zuklappen; die Warteschlange fuehrt darueber Buch. */
  toggle: [number]
  /** Nicht laenger auf diese Zeile warten. */
  abort: [number]
  remove: [number]
}>()

interface Badge {
  symbol: string
  label: string
  class: string
}

const BADGES: Record<QueueStatus, Badge> = {
  queued: { symbol: '◦', label: 'wartet', class: 'text-slate-600' },
  running: { symbol: '◐', label: 'läuft', class: 'text-sky-700' },
  ok: { symbol: '✓', label: 'fertig', class: 'text-emerald-700' },
  failed: { symbol: '✗', label: 'fehlgeschlagen', class: 'text-red-700' },
  aborted: { symbol: '⊘', label: 'abgebrochen', class: 'text-slate-600' },
}

const badge = computed(() => BADGES[props.entry.status])

/**
 * Den Startzeitpunkt haelt die Zeile selbst. Der Eintrag kennt ihn nicht: Seine
 * `durationMs` kommt aus der Antwort und steht erst am Ende fest.
 */
const startedAt = ref<number | null>(null)
const now = ref(0)
let ticker: ReturnType<typeof setInterval> | undefined

function stopTicker(): void {
  if (ticker === undefined) return
  clearInterval(ticker)
  ticker = undefined
}

watch(
  () => props.entry.status,
  (status) => {
    stopTicker()
    if (status !== 'running') {
      startedAt.value = null
      return
    }
    startedAt.value = Date.now()
    now.value = startedAt.value
    ticker = setInterval(() => {
      now.value = Date.now()
    }, 1000)
  },
  { immediate: true },
)

// Sonst tickt der Zaehler weiter, nachdem niemand mehr hinsieht.
onUnmounted(stopTicker)

/**
 * Eine Zeitspanne, wie die Zeile sie zeigt: „5:26" ab einer Sekunde, darunter
 * die Sekunde selbst — „0,04 s".
 *
 * Laufende und fertige Zeile teilen sich diese Funktion. Dieselbe Zeitspanne in
 * zwei Schreibweisen, je nachdem ob die Datei laeuft oder fertig ist, war der
 * Befund, aus dem dieses Format entstanden ist.
 *
 * Der kurze Fall ist bei diesem Dienst der haeufige: markitdown wandelt eine
 * Datei in 0,035 s um. „0:00" waere darueber keine Auskunft.
 */
function formatDuration(ms: number): string {
  const seconds = Math.max(0, ms) / 1000
  const rounded = Math.round(seconds * 100) / 100
  if (rounded < 1) return `${rounded.toString().replace('.', ',')} s`
  // Was auf eine Sekunde aufrundet, heisst 0:01 und nicht 0:00.
  const whole = Math.max(1, Math.floor(seconds))
  return `${Math.floor(whole / 60)}:${String(whole % 60).padStart(2, '0')}`
}

/** „0:47" — mitgezaehlt, solange die Zeile laeuft, sonst nichts. */
const elapsed = computed(() => {
  if (startedAt.value === null) return null
  return formatDuration(now.value - startedAt.value)
})

/** „läuft · 0:47"; fertige und gescheiterte Zeilen nennen nur ihren Zustand. */
const statusLabel = computed(() =>
  elapsed.value === null ? badge.value.label : `${badge.value.label} · ${elapsed.value}`,
)

/** Engine und Dauer, sobald sie feststehen. */
const meta = computed(() => {
  const parts: string[] = []
  if (props.entry.engine) parts.push(props.entry.engine)
  if (props.entry.durationMs !== null) parts.push(formatDuration(props.entry.durationMs))
  return parts.join(' · ')
})

const canAbort = computed(() => props.entry.status === 'running')

const canExpand = computed(() => props.entry.markdown !== null)

/** Nur ein gelungener Eintrag laesst sich herunterladen. */
const canDownload = computed(() => hasResult(props.entry))

const previewId = computed(() => `file-row-${props.entry.id}-preview`)
</script>

<template>
  <li class="rounded border border-slate-300 bg-white p-3">
    <div class="flex flex-wrap items-center gap-x-3 gap-y-1">
      <span aria-hidden="true" :class="badge.class" class="text-lg leading-none">
        {{ badge.symbol }}
      </span>
      <span class="min-w-0 flex-1 truncate font-medium">{{ entry.filename }}</span>
      <span :class="badge.class" class="text-sm">{{ statusLabel }}</span>
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
        v-if="canAbort"
        type="button"
        class="rounded border border-slate-400 px-2 py-1 text-sm hover:bg-slate-100"
        data-test="abort-row"
        @click="emit('abort', entry.id)"
      >
        Nicht mehr warten<span class="sr-only"> — {{ entry.filename }}</span>
      </button>

      <button
        v-if="canDownload"
        type="button"
        class="rounded border border-slate-400 px-2 py-1 text-sm hover:bg-slate-100"
        data-test="download-row"
        @click="downloadMarkdown(entry)"
      >
        Herunterladen<span class="sr-only"> — {{ entry.filename }}</span>
      </button>

      <button
        type="button"
        class="rounded border border-slate-400 px-2 py-1 text-sm hover:bg-slate-100"
        @click="emit('remove', entry.id)"
      >
        Entfernen<span class="sr-only"> — {{ entry.filename }}</span>
      </button>
    </div>

    <p
      v-if="entry.status === 'aborted'"
      class="mt-2 rounded bg-slate-100 p-2 text-sm text-slate-700"
      data-test="abort-note"
    >
      Der Browser wartet nicht mehr auf diese Datei. Der Dienst wandelt sie im
      Hintergrund zu Ende — abgebrochen ist das Warten, nicht die Umwandlung.
    </p>

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
          Das Ergebnis umfasst {{ entry.markdown?.length ?? 0 }} Zeichen Markdown.
        </p>
      </slot>
    </div>
  </li>
</template>
