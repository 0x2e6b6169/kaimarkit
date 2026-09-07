---
id: 128
title: FE-26 · OCR-Reichweite im Options-Panel sichtbar
status: done
priority: medium
created: 2026-09-07T09:55:45.859306412+02:00
updated: 2026-09-07T10:03:29.950087517+02:00
started: 2026-09-07T10:03:29.277987043+02:00
completed: 2026-09-07T10:03:29.277987043+02:00
assignee: benny
tags:
    - frontend
    - gh-2
class: standard
---

## Ziel

Der OCR-Schalter im Options-Panel sagt nicht, wo er wirkt. Ein Nutzer schaltet ihn bei
einem docx mit fotografiertem Absatz ein, bekommt trotzdem nichts — und weiss nicht,
ob das ein Fehler ist oder eine Grenze. Die Grenze ist seit DOC-18 (#123) belegt und in
`docs/grenzen.md` beschrieben; sie gehört jetzt auch ins UI, an die Stelle, wo die
Wahl getroffen wird.

## Eigene Dateien

- `frontend/src/components/OptionsPanel.vue` und der Test dazu

## Vorgaben

- Direkt beim OCR-Feld ein kurzer Satz, sichtbar ohne Interaktion, z. B. "Wirkt nur bei
  PDF und Bilddateien." Genauer Wortlaut nach Ermessen der Lane, in richtiger Schreibung.
- Daneben ein i-Icon mit ausfuehrlicherer Erlaeuterung bei Hover **und** bei
  Tastaturfokus (nicht nur `:hover` — sonst unerreichbar ohne Maus). Der Screenreader
  bekommt denselben Text, nicht nur das Icon.
- Inhaltlich identisch mit der belegten Aussage aus `docs/grenzen.md`
  ("OCR greift nur in PDF und Bilddateien"): Texterkennung liest Bildtext nur in PDF
  und den Formaten .png/.jpg/.jpeg/.tiff; bei .docx/.pptx/.xlsx/.html/.epub bleibt sie
  aus, unabhaengig vom Schalter. Umweg: das Dokument als PDF speichern und mit OCR
  erneut hochladen.
- Der Hinweis gilt statisch, unabhaengig von der aktuellen Dateiauswahl in der
  Warteschlange — keine dynamische Herleitung je Datei noetig.
- Erscheint nur, wenn der OCR-Schalter selbst erscheint (`ocrAvailable`), sonst nichts
  zu erklaeren.

## Prüfung

- Rot vor grün: ein Test prüft, dass der Kurzhinweis und das i-Icon mit dem
  Tooltiptext im Options-Panel vorhanden sind — schlägt vor der Arbeit fehl.
- Der ausführliche Text ist per Tastaturfokus erreichbar, nicht nur per Hover; ein Test
  belegt das (z. B. Tab auf das Icon, Text sichtbar/erreichbar für AT).
- `npm run test`, `npm run typecheck` sauber.


---

## Ergebnis benny-30

Umgesetzt in `frontend/src/components/OptionsPanel.vue`, Tests in
`frontend/src/components/__tests__/OptionsPanel.test.ts`. Branch
`task/128-ocr-scope`, Merge `1dae416`.

**Der Wortlaut.** Offen neben dem Schalter steht „wirkt nur in PDF und
Bilddateien". Hinter dem Info-Zeichen: „Die Texterkennung liest Bildtext nur in
PDF und in den Bildformaten .png, .jpg, .jpeg und .tiff. In .docx, .pptx, .xlsx,
.html und .epub bleibt sie aus — auch dann, wenn dieser Schalter an ist. Der
Umweg führt über PDF: das Dokument als PDF speichern und erneut hochladen."
Inhaltlich aus `docs/grenzen.md`, Abschnitt „OCR greift nur in PDF und
Bilddateien"; die Seite selbst blieb unangetastet.

**Ohne Maus erreichbar.** Das Info-Zeichen ist ein `<button type="button">` und
damit von sich aus im Tabulatorlauf. Es öffnet den Text bei `@focus` und
`@mouseenter`, schließt bei `@blur`, `@mouseleave` und `@keydown.escape`, führt
`aria-expanded` mit und hängt den Absatz per `aria-describedby` an — ein
Screenreader liest den vollen Wortlaut beim Anspringen, unabhängig davon, ob der
Absatz gerade sichtbar ist. Der Absatz trägt `role="tooltip"`, das `aria-label`
des Zeichens lautet „Erklärung zur Reichweite der Texterkennung". Der Fokusring
kommt aus `*:focus-visible` in `style.css`, nichts neu gebaut. Das ist dasselbe
Muster wie in `EngineSelect.vue`; die Lane hat es dort schon einmal belegt.

**Kein Zustand über das Nötige hinaus.** Ein `ref` für „offen", eine `useId`-
Kennung gegen Kollisionen, sonst nichts. Der Hinweis steht innerhalb des
`v-if="ocrAvailable"`-Blocks und hängt an keiner Datei in der Warteschlange.

**Rot vor grün.** Vier neue Tests, vor der Änderung drei davon rot:
„Tests 3 failed | 16 passed (19)", jeweils „Unable to get
[data-test=\"ocr-short\"] / [data-test=\"ocr-info\"]". Der vierte Test (der
Hinweis fehlt ohne `ocrAvailable`) war vorher trivial grün und sichert seitdem
das `v-if`.

**Danach.** `npm run test`: Test Files 10 passed (10), Tests 144 passed (144) —
die 140 des Ausgangsstands plus vier. `npm run typecheck` und `npm run build`
ohne Befund.

**Gemeldet statt geändert:** nichts. Am Rand nur eine Anmerkung zum Schnitt:
Weil die Aussage aus `docs/grenzen.md` jetzt an zwei Stellen steht, zieht eine
spätere Änderung dort diese Komponente mit. Der Docblock sagt das; ein Ticket,
das `docs/grenzen.md` anfasst, sollte `OptionsPanel.vue` mit besitzen.
