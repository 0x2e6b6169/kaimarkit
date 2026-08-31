---
id: 19
title: FE-7 · Gestaltung, Dark Mode, Tastaturbedienung, aria-live
status: done
priority: medium
created: 2026-08-31T10:20:22.896316174+02:00
updated: 2026-08-31T11:33:48.70390736+02:00
started: 2026-08-31T11:33:41.818486585+02:00
completed: 2026-08-31T11:33:41.818486585+02:00
assignee: benny
tags:
    - frontend
depends_on:
    - 15
    - 16
    - 17
class: standard
---

## Ziel

Aus den Bausteinen eine Seite machen, die sich gut bedienen laesst.

## Eigene Dateien

- `frontend/src/App.vue`
- `frontend/src/style.css`

## Vorgaben

- Ruhiges, flaechiges Layout, ein Akzentton. Kein Farbfeuerwerk - das Werkzeug
  zeigt Text, und der soll lesbar sein.
- Dark Mode ueber `prefers-color-scheme`, keine eigene Umschaltung.
- Sichtbarer Fokusrahmen auf allen bedienbaren Elementen.
- Die Seite funktioniert ab 360 px Breite; breite Inhalte scrollen in ihrem eigenen
  Bereich.
- Leerer Zustand erklaert in einem Satz, was das Werkzeug tut und welche Formate
  es nimmt.

## Pruefung

Bedienung allein per Tastatur von der Dropzone bis zum Download. Im hellen und im
dunklen Modus ist jeder Text lesbar. Bei 360 px Breite scrollt die Seite nicht
waagerecht.

[[2026-08-31]] Mon 11:33
## Ergebnis FE-7 (benny-07, Branch task/19-layout-a11y, gemergt 7cd21b9)

Aus den Bausteinen ist eine Seite geworden: Kopf mit einem Satz zum Zweck und den
Formaten aus `/api/capabilities`, Optionen, Dropzone, Warteschlange mit Vorschau je
Zeile. Eigene Dateien: `App.vue`, `style.css`, dazu `App.test.ts` (vier Faelle).

**Die Warteschlange bleibt immer eingehaengt, auch ohne Dateien.** `FileQueue` merkt
sich beim Einhaengen den Zustand jeder Zeile, um nur Aenderungen anzusagen. Erschiene
sie erst mit der ersten Datei, saehe sie deren Start als Ausgangszustand und sagte ihn
nie an. Ein `v-if` auf die Warteschlange bricht also die Barrierefreiheit — das steht
als Kommentar in `App.vue` und als Zusicherung im Test.

**Dark Mode ohne Eingriff in die Komponenten.** Tailwind 4 uebersetzt jede Farbklasse
in eine Variable: `bg-white` wird zu `background-color: var(--color-white)`. `style.css`
belegt diese Variablen unter `prefers-color-scheme: dark` neu und kippt damit jede
Flaeche und jede Schrift der Anwendung. Der Block steht ausserhalb jeder `@layer` und
schlaegt deshalb `@layer theme`. Bedingung: Jede Stufe der Skala darf nur einer Sache
dienen, Flaeche oder Schrift. `slate-800` tut beides (`text-slate-800` in der Dropzone,
`dark:bg-slate-800` am gewaehlten Reiter) und steht als einzige Ausnahme mit einer
eigenen Regel da. **Wer eine neue Farbklasse einfuehrt, prueft, ob ihre Stufe in
`style.css` schon anders belegt ist.**

Dazu in `style.css`: Fokusrahmen (3 px, Akzentton) auf allem, was `:focus-visible`
trifft; `overflow-wrap: anywhere` gegen Dateinamen ohne Leerzeichen; und ab 26 rem
abwaerts eine eigene Zeile fuer den Dateinamen — `flex-1` gibt ihm die Ausgangsbreite
null, bei 360 px blieb von `bericht.pdf` ein „b." uebrig, waehrend Engine und Dauer
vollstaendig dastanden.

## Zwei Eingriffe in fremde Dateien, beide dort unvermeidlich

1. **`frontend/src/components/FileQueue.vue`** reicht den Slot `preview` jetzt an
   `FileRow` durch (`<template v-if="$slots.preview" #preview>`). FE-3 hatte den Slot in
   `FileRow` angelegt, aber `FileQueue` reichte ihn nicht weiter — von `App.vue` aus war
   keine Vorschau erreichbar. Das `v-if` haelt den Rueckfall aus `FileRow` am Leben,
   deshalb bleiben die Tests von FE-3 unveraendert gruen.
2. **`frontend/src/components/MarkdownPreview.vue`** hat den wandernden `tabindex` an
   den beiden Reitern verloren. Der ARIA-Entwurf laesst dafuer zwei Wege: wandernder
   Fokus mit Pfeiltasten, oder jeder Reiter per Tabulator erreichbar. Der erste stand
   dort ohne die Pfeiltasten, die er braucht: „Rohtext" trug `tabindex="-1"`, und in
   Chrome war er mit der Tastatur nicht zu erreichen — nachgewiesen mit echten
   Tabulatordruecken ueber das DevTools-Protokoll. Bei zwei Reitern ist der zweite Weg
   der kuerzere. `App.test.ts` haelt fest, dass keine Schaltflaeche aus der
   Tabreihenfolge faellt.

## Fuer INT-1 (#29)

- **Der Download haengt noch nicht.** `frontend/src/download.ts` (FE-6) ist waehrend
  dieses Tickets nach `main` gekommen, aber niemandem gehoert die Stelle, an der er
  eingehaengt wird: Der Einzeldownload braucht eine Schaltflaeche in `FileRow.vue`
  (FE-3, abgeschlossen), „Alles herunterladen" gehoert nach `App.vue`. In `App.vue`
  steht ein Kommentar an der Stelle. Der Tastaturweg endet deshalb heute bei der
  Vorschau.
- **`@copied` aus `MarkdownPreview` ist absichtlich nicht gebunden.** Die Komponente
  bringt fuer das Kopieren einen eigenen `role="status"` mit. Eine zweite Ansage in der
  Seite hiesse, dass Screenreader den Vorgang doppelt vorlesen.
- Die Ansage in `App.vue` deckt nur das Ende eines Laufs ab („Alle Dateien sind fertig:
  3 gelungen, 1 fehlgeschlagen."). Jede einzelne Zeile sagt `FileQueue` an.
- `docs/entwicklung.md` ist waehrend dieses Tickets entstanden und gehoert DOC-2 (#21,
  noch offen). Deshalb steht dort nichts von hier. Was hineingehoert: der Absatz zum
  Dark Mode oben, samt der Bedingung an die Farbskala.

## Pruefung

Auf dem zusammengefuehrten Stand, einschliesslich FE-6 und DOC-2:

    npm run test       Test Files  8 passed (8)   Tests  75 passed (75)
    npm run typecheck  vue-tsc --build, ohne Ausgabe, Exit 0
    npm run build      dist/assets/index-CA9HL6HI.css 13.15 kB, built in 694ms

Die Pruefung im Ticket verlangt den Browser. Sie ist in echtem Chrome gelaufen, headless
ueber das DevTools-Protokoll, gegen `VITE_KAIMARKIT_MOCK=1 npm run dev` mit drei
abgelegten Dateien (Erfolg, Warnungen, Fehlschlag) und aufgeklappter Vorschau:

- **360 px, kein waagerechtes Scrollen.** Hell wie dunkel `scrollWidth == clientWidth
  == 345`, kein Element ragt ueber die Breite hinaus. Bei 900 px ebenso.
- **Beide Modi lesbar.** Hell `body #f1f5f9` auf Schrift `#1e293b`, dunkel `#020617` auf
  `#e2e8f0`. Im dunklen Modus liegt der schwaechste gemessene Kontrast bei 7,87:1. Die
  Messung im hellen Modus taugt nicht: Chrome gibt die Tailwind-Grundfarben als `oklch`
  zurueck, und der Rechner las sie als RGB. Der helle Modus ist deshalb am Bildschirmfoto
  geprueft, nicht gerechnet.
- **Tastaturweg, mit echten Tabulatordruecken:** Engine → OCR → Dropzone → Aufklappen →
  Entfernen → Ergebnis → Kopieren → Vorschau → Rohtext → Vorschaubereich. Jeder Halt
  bekommt `outline: 3px solid`, `:focus-visible` trifft. Der Download fehlt am Ende, weil
  ihn niemand eingehaengt hat (siehe oben).
