---
id: 15
title: FE-3 · Dropzone und Warteschlange mit Status je Datei
status: done
priority: medium
created: 2026-08-31T10:20:20.286425335+02:00
updated: 2026-08-31T11:14:56.741059998+02:00
started: 2026-08-31T11:14:51.72859834+02:00
completed: 2026-08-31T11:14:51.72859834+02:00
assignee: benny
tags:
    - frontend
depends_on:
    - 14
class: standard
---

## Ziel

Dateien hinzufuegen und ihren Fortschritt sehen.

## Eigene Dateien

- `frontend/src/components/FileDropZone.vue`
- `frontend/src/components/FileQueue.vue`
- `frontend/src/components/FileRow.vue`

## Vorgaben

- Drag & Drop und Dateiauswahl. Die Dropzone ist per Tastatur erreichbar
  (fokussierbar, Leertaste oeffnet den Dialog).
- Jede Datei erscheint sofort als Zeile mit Status, bevor die Konvertierung
  beginnt.
- Statusaenderungen laufen ueber `aria-live`, damit sie ohne Blick auf den
  Bildschirm wahrnehmbar sind.
- Status wird nicht allein durch Farbe unterschieden, sondern zusaetzlich durch
  Symbol und Text.
- Warnungen stehen sichtbar an der Zeile - genau dort entscheidet sich, ob das
  Ergebnis taugt.
- Eine Zeile laesst sich aufklappen; der Inhalt kommt aus `MarkdownPreview` (FE-4),
  bis dahin genuegt ein Platzhalter.

## Pruefung

Im Browser mit Mock: fuenf Dateien ablegen, Reihenfolge und Status stimmen, eine
fehlgeschlagene Datei zeigt ihre Meldung, Bedienung allein per Tastatur moeglich.


## Ergebnis (benny-03, Branch task/15-dropzone-queue, merged 267ff24)

Drei Komponenten, je eine Testdatei daneben. Keine Komponente greift selbst auf
`useConversion()` zu: Alles kommt ueber Props herein und geht ueber Events
hinaus, damit FE-7 verdrahten kann und der Test ohne `App.vue` auskommt.

**FileDropZone** — Props `extensions?: string[]` (Endungen samt Punkt, fuer
`accept`), `disabled?: boolean`. Event `files: [File[]]`. Der Ablagebereich ist
ein echter `<button>`: fokussierbar von Haus aus, Leertaste und Eingabetaste
oeffnen den Dialog, Screenreader kuendigen ihn als Schaltflaeche an. Der
Dateidialog haengt an einer ausgeblendeten Eingabe mit `tabindex="-1"`, damit
dieselbe Handlung nicht zweimal in der Tabreihenfolge steht.

**FileQueue** — Prop `entries: QueueEntry[]`. Event `remove: [number]`. Zeigt
eine Zeile je Datei in der Reihenfolge des Hinzufuegens und haelt selbst, welche
Zeilen aufgeklappt sind. Jede Statusaenderung geht in einen `role="log"`-Bereich
mit `aria-live="polite"`. Die Ansagen sammeln sich dort, statt einander zu
ersetzen: Ein Fehlschlag und der Start der naechsten Datei liegen oft nur einen
Durchlauf auseinander, und ein Bereich mit einer einzigen Zeile ueberschreibt die
erste Ansage, bevor sie jemand gehoert hat. Die letzten zehn bleiben stehen.

**FileRow** — Props `entry: QueueEntry`, `expanded?: boolean`. Events
`toggle: [number]`, `remove: [number]`. Der Zustand steht als Symbol, Wort und
Farbe zugleich da (wartet · laeuft · fertig · fehlgeschlagen), nie in der Farbe
allein. Warnungen und die Fehlermeldung stehen an der Zeile selbst. Aufklappen
gibt es nur, wenn Markdown vorliegt; der aufgeklappte Bereich ist der Slot
`preview` mit einem Platzhalter als Rueckfall.

### Was FE-7 zum Verdrahten braucht

```vue
const { entries, enqueue, remove } = useConversion()
const { extensions } = useCapabilities()

<FileDropZone :extensions="extensions" @files="enqueue" />
<FileQueue :entries="entries" @remove="remove" />
```

Die Refs oben einzeln herausnehmen, nicht `queue.entries` im Template lassen —
nur Bindungen der obersten Ebene entpackt Vue selbsttaetig.

### Uebergabe an FE-4

`MarkdownPreview` gehoert in den Slot `preview` von `FileRow`. `FileQueue`
reicht den Slot **nicht** durch; wer die Vorschau einhaengt, ersetzt den
Platzhalter in `FileRow.vue` (eine Stelle, `<slot name="preview" :entry="entry">`).
Das ist der einzige Handgriff, den FE-3 offen laesst.

### Pruefung

Die Pruefung im Ticket verlangt den Browser. Hier gibt es keinen; nachgestellt
ist sie als Test, der Dropzone und Warteschlange an dieselbe
`createConversionQueue` haengt: fuenf Dateien ablegen, fuenf Zeilen in der
richtigen Reihenfolge, zwei laufen und drei warten, die erste scheitert und
zeigt ihre Meldung an der Zeile, die uebrigen vier werden fertig. Die
Tastaturbedienung ist ueber die Bauart geprueft (`<button>`), nicht ueber ein
nachgestelltes Tastenereignis — das pruefte jsdom, nicht die Komponente.

Auf dem zusammengefuehrten Stand, einschliesslich FE-4 und FE-5:

```
npm run test       Test Files  6 passed (6)   Tests  43 passed (43)
npm run typecheck  vue-tsc --build, ohne Ausgabe
npm run build      dist/assets/index-CtaPYQjO.js  64.01 kB, built in 1.26s
```

### Luecke in der Dokumentation (fuer akar, DOC-2)

`docs/entwicklung.md` fehlt noch. Was dort hingehoert und niemand sonst notiert:

- Komponententests laufen unter `vitest` mit `@vue/test-utils`. Die
  Testumgebung steht als `// @vitest-environment jsdom` in der ersten Zeile
  jeder Testdatei, weil `vite.config.ts` keinen `test`-Abschnitt hat.
- Die Testdateien liegen neben der Komponente (`FileQueue.test.ts`). FE-5 hat
  seinen Test nach `__tests__/` gelegt. Zwei Orte fuer dieselbe Sache — das
  gehoert einmal entschieden und aufgeschrieben.
