<script setup lang="ts">
/**
 * Die Seite. Sie haelt die Bausteine zusammen und entscheidet nichts selbst:
 * Die Warteschlange gehoert `useConversion`, die Faehigkeiten `useCapabilities`,
 * die Darstellung den Komponenten.
 *
 * Was hier zusammenlaeuft:
 *
 * - Die Dropzone meldet Dateien, die Warteschlange nimmt sie an.
 * - Die Optionen gelten fuer den naechsten Start; die Dateinamen schraenken die
 *   Enginewahl ein.
 * - Jede Zeile bekommt ihre Vorschau ueber den Slot `preview` der
 *   Warteschlange.
 * - „Alles herunterladen" packt die fertigen Ergebnisse zu einem Archiv. Der
 *   Einzeldownload sitzt in der Zeile, weil er nur deren Eintrag braucht; das
 *   Archiv steht hier, weil es alle Zeilen sieht.
 *
 * **Die Warteschlange bleibt immer eingehaengt**, auch ohne Dateien. `FileQueue`
 * merkt sich beim Einhaengen den Zustand jeder Zeile, um nur Aenderungen
 * anzusagen. Wuerde sie erst mit der ersten Datei erscheinen, saehe sie deren
 * Start als Ausgangszustand und sagte ihn nie an.
 */
import { computed, onMounted, ref, watch } from 'vue'
import FileDropZone from './components/FileDropZone.vue'
import FileQueue from './components/FileQueue.vue'
import MarkdownPreview from './components/MarkdownPreview.vue'
import OptionsPanel from './components/OptionsPanel.vue'
import { useCapabilities } from './composables/useCapabilities'
import { useConversion } from './composables/useConversion'
import { messageFromError } from './api'
import { ARCHIVE_FILENAME, downloadArchive, hasResult } from './download'

const { entries, options, busy, enqueue, abort, remove } = useConversion()
const { extensions, error: capabilitiesError, load, reload } = useCapabilities()

onMounted(() => void load())

/** Die Dateinamen schraenken die Enginewahl ein — siehe `OptionsPanel`. */
const filenames = computed(() => entries.value.map((entry) => entry.filename))

const formats = computed(() => extensions.value.join(' · '))

const succeeded = computed(() => entries.value.filter((entry) => entry.status === 'ok').length)
const failed = computed(() => entries.value.filter((entry) => entry.status === 'failed').length)

/**
 * Die Ansage am Ende eines Laufs. `FileQueue` meldet jede einzelne Zeile; was
 * dort fehlt, ist der Augenblick, in dem nichts mehr laeuft — genau dann kann
 * der Nutzer weiterarbeiten. Die Ansagen sammeln sich, damit zwei Laeufe kurz
 * hintereinander nicht einander ueberschreiben.
 */
const announcements = ref<{ id: number; text: string }[]>([])
let nextAnnouncement = 1

function announce(text: string): void {
  announcements.value.push({ id: nextAnnouncement++, text })
  if (announcements.value.length > 5) announcements.value.shift()
}

watch(busy, (running, before) => {
  if (running || !before || !entries.value.length) return
  const parts = [`${succeeded.value} gelungen`]
  if (failed.value) parts.push(`${failed.value} fehlgeschlagen`)
  announce(`Alle Dateien sind fertig: ${parts.join(', ')}.`)
})

/**
 * Das Archiv. Es entsteht im Browser aus den Ergebnissen, die ohnehin schon da
 * sind — siehe `download.ts`.
 *
 * Das Packen dauert und zeigt von sich aus nichts an. Deshalb sagt der Knopf,
 * dass er arbeitet, und der Ausgang wird angesagt: Wer nicht auf den Bildschirm
 * sieht, erfaehrt sonst nie, dass die Datei bereitsteht.
 */
const results = computed(() => entries.value.filter((entry) => hasResult(entry)))
const packing = ref(false)
const archiveError = ref<string | null>(null)

async function downloadAll(): Promise<void> {
  packing.value = true
  archiveError.value = null
  try {
    await downloadArchive(entries.value)
    announce(`${ARCHIVE_FILENAME} steht bereit.`)
  } catch (cause) {
    archiveError.value = messageFromError(cause)
  } finally {
    packing.value = false
  }
}
</script>

<template>
  <div class="min-h-dvh">
    <main class="mx-auto flex w-full max-w-3xl flex-col gap-8 px-4 py-8 sm:px-6">
      <header class="flex flex-col gap-2">
        <h1 class="text-2xl font-semibold sm:text-3xl">kaimarkit</h1>
        <p class="text-slate-600">
          kaimarkit wandelt Dokumente nach Markdown, damit man den Kontext liest, den man
          einem Sprachmodell gibt.<template v-if="formats">
            Angenommen werden {{ formats }}.</template>
        </p>
      </header>

      <!--
        Der Ausfall der Faehigkeiten trifft die ganze Seite: Ohne sie kennt die
        Dropzone keine Endungen und die Auswahl keine Engine. Deshalb `alert` und
        nicht die stille Ansage weiter unten.
      -->
      <p
        v-if="capabilitiesError"
        role="alert"
        class="flex flex-wrap items-center gap-x-3 gap-y-2 rounded border border-red-300 bg-red-50 p-3 text-red-900"
        data-test="capabilities-error"
      >
        <span class="flex-1">
          Der Dienst antwortet nicht: {{ capabilitiesError }} Ohne ihn steht keine Engine
          zur Wahl.
        </span>
        <button
          type="button"
          class="rounded border border-red-300 px-3 py-1 text-sm font-medium"
          @click="void reload()"
        >
          Erneut versuchen
        </button>
      </p>

      <OptionsPanel v-model="options" :filenames="filenames" />

      <FileDropZone :extensions="extensions" @files="enqueue" />

      <section aria-labelledby="queue-heading" class="flex flex-col gap-3">
        <div class="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
          <h2 id="queue-heading" class="text-lg font-medium">Warteschlange</h2>
          <p v-if="entries.length" class="text-sm text-slate-500" data-test="progress">
            {{ succeeded }} von {{ entries.length }} fertig<span v-if="failed">
              · {{ failed }} fehlgeschlagen</span
            >
          </p>
        </div>

        <div v-if="entries.length" class="flex flex-wrap items-center gap-x-3 gap-y-2">
          <button
            type="button"
            class="rounded border border-slate-400 px-3 py-1 text-sm font-medium hover:bg-slate-100 disabled:opacity-50"
            data-test="download-all"
            :disabled="busy || packing || !results.length"
            @click="void downloadAll()"
          >
            {{ packing ? 'Archiv wird gepackt …' : 'Alles herunterladen' }}
          </button>
          <span v-if="busy" class="text-sm text-slate-600">
            Das Archiv steht bereit, sobald nichts mehr läuft.
          </span>
        </div>

        <p
          v-if="archiveError"
          role="alert"
          class="rounded border border-red-300 bg-red-50 p-3 text-red-900"
          data-test="archive-error"
        >
          Das Archiv ließ sich nicht bauen: {{ archiveError }}
        </p>

        <FileQueue :entries="entries" @abort="abort" @remove="remove">
          <template #preview="{ entry }">
            <MarkdownPreview :markdown="entry.markdown" :open="true" />
          </template>
        </FileQueue>
      </section>
    </main>

    <div class="sr-only" role="log" aria-live="polite" data-test="app-log">
      <p v-for="item in announcements" :key="item.id">{{ item.text }}</p>
    </div>
  </div>
</template>
