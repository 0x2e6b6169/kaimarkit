<script setup lang="ts">
/**
 * Geruestseite. Sie zeigt, dass Vue, Tailwind und die Schnittstelle
 * zusammenspielen, und loest die drei Faelle des Mocks aus. FE-3 bis FE-7
 * ersetzen sie durch Dropzone, Warteschlange, Optionen und Vorschau.
 */
import { onMounted, ref } from 'vue'
import type { CapabilitiesResponse, ConversionEntry, ErrorResponse } from './types'

const capabilities = ref<CapabilitiesResponse | null>(null)
const capabilitiesError = ref<string | null>(null)

const running = ref(false)
const entry = ref<ConversionEntry | null>(null)
const failure = ref<ErrorResponse | null>(null)

const cases: { label: string; filename: string }[] = [
  { label: 'Erfolg', filename: 'bericht.pdf' },
  { label: 'Erfolg mit Warnungen', filename: 'bericht-warnung.pdf' },
  { label: 'Fehlschlag', filename: 'bericht-fehler.pdf' },
]

onMounted(async () => {
  try {
    const response = await fetch('/api/capabilities', {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    capabilities.value = (await response.json()) as CapabilitiesResponse
  } catch (cause) {
    capabilitiesError.value = cause instanceof Error ? cause.message : String(cause)
  }
})

async function convert(filename: string): Promise<void> {
  running.value = true
  entry.value = null
  failure.value = null
  try {
    const body = new FormData()
    body.append('file', new File(['Beispielinhalt'], filename), filename)
    body.append('engine', 'auto')
    const response = await fetch('/api/convert', {
      method: 'POST',
      headers: { Accept: 'application/json' },
      body,
    })
    const payload: unknown = await response.json()
    if (response.ok) {
      entry.value = payload as ConversionEntry
    } else {
      failure.value = payload as ErrorResponse
    }
  } catch (cause) {
    failure.value = {
      detail: cause instanceof Error ? cause.message : String(cause),
      code: 'conversion_failed',
    }
  } finally {
    running.value = false
  }
}
</script>

<template>
  <main class="mx-auto max-w-3xl space-y-8 p-8 font-sans">
    <header>
      <h1 class="text-3xl font-semibold">kaimarkit</h1>
      <p class="text-slate-600">
        Dokumente nach Markdown wandeln, um den Kontext zu sehen, den man einem LLM gibt.
      </p>
    </header>

    <section class="space-y-2">
      <h2 class="text-xl font-medium">Faehigkeiten</h2>
      <p v-if="capabilitiesError" class="text-red-700">
        /api/capabilities nicht erreichbar: {{ capabilitiesError }}
      </p>
      <ul v-else-if="capabilities" class="space-y-1">
        <li v-for="(state, name) in capabilities.engines" :key="name">
          <span class="font-mono">{{ name }}</span> — {{ state }}
        </li>
      </ul>
      <p v-else class="text-slate-500">wird geladen …</p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xl font-medium">Die drei Faelle des Mocks</h2>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="item in cases"
          :key="item.filename"
          type="button"
          class="rounded border border-slate-400 px-3 py-1.5 hover:bg-slate-100 disabled:opacity-50"
          :disabled="running"
          @click="convert(item.filename)"
        >
          {{ item.label }}
        </button>
      </div>

      <p v-if="running" class="text-slate-500">konvertiert …</p>

      <div v-if="failure" class="rounded border border-red-300 bg-red-50 p-3">
        <p class="font-mono text-sm">{{ failure.code }}</p>
        <p>{{ failure.detail }}</p>
      </div>

      <div v-if="entry" class="space-y-2">
        <p class="text-sm text-slate-600">
          {{ entry.filename }} · {{ entry.engine }} · {{ entry.duration_ms }} ms
        </p>
        <ul v-if="entry.warnings.length" class="rounded border border-amber-300 bg-amber-50 p-3">
          <li v-for="warning in entry.warnings" :key="warning">{{ warning }}</li>
        </ul>
        <pre class="overflow-x-auto rounded bg-slate-100 p-3 text-sm">{{ entry.markdown }}</pre>
      </div>
    </section>
  </main>
</template>
