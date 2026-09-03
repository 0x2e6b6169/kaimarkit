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
import { fetchHealth, messageFromError } from './api'
import { ARCHIVE_FILENAME, downloadArchive, hasResult } from './download'

const { entries, options, busy, enqueue, abort, remove } = useConversion()
const { extensions, error: capabilitiesError, load, reload } = useCapabilities()

/**
 * Welchen Stand der Dienst fährt. Der Wert kommt aus `/api/health`, einmal beim
 * Laden und danach nicht wieder.
 *
 * Zwei Dinge unterscheiden ihn von den Fähigkeiten. Er hält nichts auf: Die
 * Dropzone nimmt Dateien an, lange bevor die Antwort da ist. Und sein Ausfall
 * bleibt stumm — an der Version hängt kein Bedienschritt, wer sie nicht kennt,
 * wandelt trotzdem um. Ein Fehlerbanner für eine Fußnote wäre aus dem
 * Verhältnis.
 *
 * Die Zeichenkette geht unverändert auf den Bildschirm. Heute steht dort
 * `0.1.0`, später etwas wie `v0.1.0-12-ga22a6c5`; welche Form sie hat,
 * entscheidet der Dienst.
 */
const version = ref<string | null>(null)

async function loadVersion(): Promise<void> {
  try {
    const health = await fetchHealth()
    if (typeof health?.version === 'string' && health.version) version.value = health.version
  } catch {
    // Stillschweigen, siehe oben.
  }
}

onMounted(() => {
  void load()
  void loadVersion()
})

/** Die Dateinamen schraenken die Enginewahl ein — siehe `OptionsPanel`. */
const filenames = computed(() => entries.value.map((entry) => entry.filename))

const succeeded = computed(() => entries.value.filter((entry) => entry.status === 'ok').length)
const failed = computed(() => entries.value.filter((entry) => entry.status === 'failed').length)
const aborted = computed(() => entries.value.filter((entry) => entry.status === 'aborted').length)

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
  if (aborted.value) parts.push(`${aborted.value} abgebrochen`)
  // Wer abgebrochen hat, hoert nicht „alle sind fertig": Der Dienst wandelt eine
  // abgebrochene Datei im Hintergrund zu Ende, fertig ist nur das Warten. Und
  // „abgebrochen" steht neben „fehlgeschlagen", nicht darin — ein Abbruch ist
  // die Entscheidung des Nutzers und kein Fehler. Ohne Abbruch bleibt der Satz,
  // wie er war.
  const lead = aborted.value ? 'Der Lauf ist zu Ende' : 'Alle Dateien sind fertig'
  announce(`${lead}: ${parts.join(', ')}.`)
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
        <div class="flex items-center justify-between gap-4">
          <h1 class="text-2xl font-semibold sm:text-3xl">kaimarkit</h1>
          <!--
            Der Verweis auf das Repository. Den zugaenglichen Namen traegt das
            `a`, weil das Zeichen versteckt ist und keinen Text hat. Den
            sichtbaren Fokusrahmen bringt die Regel `*:focus-visible` aus
            `style.css` mit; hier ist nichts nachzubauen.

            Das Zeichen ist Octicons `mark-github` (24x24, MIT). Es steht als
            SVG in der Vorlage, damit es ueber `currentColor` die Schriftfarbe
            des Kopfes erbt und im dunklen Modus ohne Zutun stimmt.
          -->
          <a
            href="https://github.com/0x2e6b6169/kaimarkit"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="kaimarkit auf GitHub"
            class="shrink-0 text-slate-600 hover:text-slate-800"
          >
            <svg
              viewBox="0 0 24 24"
              fill="currentColor"
              aria-hidden="true"
              class="h-6 w-6 sm:h-7 sm:w-7"
            >
              <path
                d="M10.226 17.284c-2.965-.36-5.054-2.493-5.054-5.256 0-1.123.404-2.336 1.078-3.144-.292-.741-.247-2.314.09-2.965.898-.112 2.111.36 2.83 1.01.853-.269 1.752-.404 2.853-.404 1.1 0 1.999.135 2.807.382.696-.629 1.932-1.1 2.83-.988.315.606.36 2.179.067 2.942.72.854 1.101 2 1.101 3.167 0 2.763-2.089 4.852-5.098 5.234.763.494 1.28 1.572 1.28 2.807v2.336c0 .674.561 1.056 1.235.786 4.066-1.55 7.255-5.615 7.255-10.646C23.5 6.188 18.334 1 11.978 1 5.62 1 .5 6.188.5 12.545c0 4.986 3.167 9.12 7.435 10.669.606.225 1.19-.18 1.19-.786V20.63a2.9 2.9 0 0 1-1.078.224c-1.483 0-2.359-.808-2.987-2.313-.247-.607-.517-.966-1.034-1.033-.27-.023-.359-.135-.359-.27 0-.27.45-.471.898-.471.652 0 1.213.404 1.797 1.235.45.651.921.943 1.483.943.561 0 .92-.202 1.437-.719.382-.381.674-.718.944-.943"
              />
            </svg>
          </a>
        </div>
        <p class="text-slate-600">
          kaimarkit wandelt Dokumente nach Markdown, damit man den Kontext liest, den man
          einem Sprachmodell gibt.
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

    <!--
      Die Version. Sie steht unten, klein und gedämpft: Wer sie sucht, sucht
      sie gezielt, und wer umwandeln will, braucht sie nicht. Bleibt
      `/api/health` die Antwort schuldig, fehlt die Zeile ganz.
    -->
    <footer v-if="version" class="mx-auto w-full max-w-3xl px-4 pb-8 sm:px-6">
      <p class="text-xs text-slate-500" data-test="version">Version {{ version }}</p>
    </footer>

    <div class="sr-only" role="log" aria-live="polite" data-test="app-log">
      <p v-for="item in announcements" :key="item.id">{{ item.text }}</p>
    </div>
  </div>
</template>
