---
id: 40
title: DOC-8 · Dark Mode und Farbpalette in docs/entwicklung.md
status: done
priority: low
created: 2026-08-31T12:04:20.646170298+02:00
updated: 2026-08-31T12:09:39.160498257+02:00
started: 2026-08-31T12:04:55.134823565+02:00
completed: 2026-08-31T12:09:15.766940685+02:00
assignee: akar
tags:
    - docs
class: standard
---

## Ziel

Zwei Absaetze, die FE-7 (#19) gemeldet und INT-1 (#29) erneut uebergeben hat und
die bis heute fehlen. Beide gehoeren nach `docs/entwicklung.md`.

## Eigene Dateien

- `docs/entwicklung.md`

Die Datei ist frei: DOC-7 (#36) ist gemergt und geschlossen.

## Vorgaben

- **Dark Mode**: wie er umgesetzt ist und was jemand beachten muss, der eine
  Ansicht ergaenzt.
- **Bedingung an die Farbpalette**: Wer eine Farbklasse ergaenzt, liest vorher
  `frontend/src/style.css`. Jede Stufe dient dort nur einer Sache, `slate-800`
  ist die einzige Ausnahme. Diese Bedingung gehoert ausgeschrieben, nicht als
  Hinweis.

## Pruefung

Beide Absaetze stehen in `docs/entwicklung.md`, und die Aussage zur Palette laesst
sich an `frontend/src/style.css` nachpruefen. `mkdocs build --strict` endet mit 0.


## Ergebnis (akar-14)

Neuer Abschnitt "Dark Mode und die Farbpalette" in `docs/entwicklung.md`, zwischen
"Eine vierte Engine ergaenzen" und "Das Board". Drei Absaetze: (1) wie der dunkle
Modus umgesetzt ist und was jemand beachten muss, der eine Ansicht ergaenzt,
(2) die Bedingung an die Palette, ausgeschrieben mit allen Stufen und ihrer
Aufgabe, (3) `slate-800` als die eine Ausnahme samt Sonderregel am Ende von
`style.css`.

**Anker im Code.** Gelesen bei Commit `7f5a6e7`:
`frontend/src/style.css` Zeilen 1-132 (Kopfkommentar 3-29, Umbelegung 40-79,
Sonderregel 128-132), `frontend/src/components/MarkdownPreview.vue` Zeilen 92, 106,
118, 140, 152, `frontend/src/components/FileDropZone.vue` Zeile 87. Aendert sich das
Frontend, macht dieser Anker die Abweichung sichtbar.

**Die Praemisse haelt.** Nachgezaehlt ueber alle Farbklassen in `frontend/src` und
`frontend/index.html`: Flaeche `white`, `slate-50`, `slate-100`, `slate-200`,
`sky-50`, `red-50`, `amber-50`; Linie `slate-300`, `slate-400`, `slate-700`,
`sky-500`, `red-300`, `amber-300`; Schrift `slate-500`, `slate-600`, `sky-700`,
`sky-900`, `red-700`, `red-900`, `amber-900`, `emerald-700`. Genau eine Stufe dient
zwei Sachen: `slate-800` (`text-slate-800` in FileDropZone.vue, `dark:bg-slate-800`
in MarkdownPreview.vue). Die Aussage des Tickets stimmt unveraendert.

Nebenbefund fuer die Frontend-Lane: `dark:`-Klassen stehen im Produktivcode nur in
`MarkdownPreview.vue` (`dark:border-slate-700` 3x, `dark:bg-slate-800` 2x). Kein
Umschalter, keine Tailwind-Konfigurationsdatei -- Tailwind 4 wird ueber
`@import "tailwindcss"` geladen, der dunkle Modus folgt allein
`prefers-color-scheme`.

**Pruefung.** Beide geforderten Absaetze stehen in `docs/entwicklung.md`. Die
Palettenaussage laesst sich an `frontend/src/style.css` nachpruefen (siehe oben).
`mkdocs build --strict` endet mit 0, ohne MkDocs-Warnung; die rote Meldung im
Ausgabekopf ist der Hinweis des Material-Teams zu MkDocs 2.0, kein Buildfehler.
`grep -inE "tr(ä|a|u)g"` findet auf der Seite nur das vorbestehende "eintragen".

Merge: `f8e51cc` (`--no-ff` aus `task/40-dark-mode-doku`, Commit `fb353f1`).
Worktree entfernt, Branch geloescht.
