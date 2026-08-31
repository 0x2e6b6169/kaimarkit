/**
 * Was der Dienst kann — einmal geladen, von allen Komponenten geteilt.
 *
 * Die Antwort entscheidet, welche Endungen die Dropzone annimmt und welche
 * Engines zur Wahl stehen. Angeboten wird nur, was auch gelingen kann: Engines
 * im Zustand `unavailable` nennt `/api/capabilities` gar nicht erst.
 */

import { computed, ref, type ComputedRef, type Ref } from 'vue'
import { fetchCapabilities, messageFromError } from '../api'
import type { CapabilitiesResponse, EngineState, Limits } from '../types'

const capabilities = ref<CapabilitiesResponse | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

/** Der laufende Abruf. Zehn Komponenten duerfen `load()` rufen, es geht eine Anfrage hinaus. */
let inflight: Promise<void> | null = null

function load(): Promise<void> {
  if (capabilities.value) return Promise.resolve()
  if (inflight) return inflight

  loading.value = true
  error.value = null
  inflight = fetchCapabilities()
    .then((result) => {
      capabilities.value = result
    })
    .catch((cause: unknown) => {
      error.value = messageFromError(cause)
    })
    .finally(() => {
      loading.value = false
      inflight = null
    })
  return inflight
}

/** Nach einem Fehlschlag erneut versuchen. */
function reload(): Promise<void> {
  capabilities.value = null
  return load()
}

/** Die Endung samt Punkt, klein geschrieben — der Schluessel in `formats`. */
function extensionOf(filename: string): string {
  const dot = filename.lastIndexOf('.')
  return dot < 0 ? '' : filename.slice(dot).toLowerCase()
}

export interface Capabilities {
  capabilities: Ref<CapabilitiesResponse | null>
  loading: Ref<boolean>
  /** Lesbare Meldung, wenn der Abruf scheiterte. */
  error: Ref<string | null>
  /** Alle bekannten Endungen, fuer das `accept` der Dropzone. */
  extensions: ComputedRef<string[]>
  engines: ComputedRef<Record<string, EngineState>>
  limits: ComputedRef<Limits | null>
  ocrAvailable: ComputedRef<boolean>
  /** Die Engines fuer diese Datei, in der Reihenfolge der Praeferenz. Leer, wenn das Format fehlt. */
  enginesFor: (filename: string) => string[]
  supports: (filename: string) => boolean
  load: () => Promise<void>
  reload: () => Promise<void>
}

export function useCapabilities(): Capabilities {
  return {
    capabilities,
    loading,
    error,
    extensions: computed(() => Object.keys(capabilities.value?.formats ?? {}).sort()),
    engines: computed(() => capabilities.value?.engines ?? {}),
    limits: computed(() => capabilities.value?.limits ?? null),
    ocrAvailable: computed(() => capabilities.value?.ocr_available ?? false),
    enginesFor: (filename: string) =>
      capabilities.value?.formats[extensionOf(filename)] ?? [],
    supports: (filename: string) => extensionOf(filename) in (capabilities.value?.formats ?? {}),
    load,
    reload,
  }
}
