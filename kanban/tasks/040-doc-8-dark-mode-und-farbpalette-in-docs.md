---
id: 40
title: DOC-8 · Dark Mode und Farbpalette in docs/entwicklung.md
status: in-progress
priority: low
created: 2026-08-31T12:04:20.646170298+02:00
updated: 2026-08-31T12:06:04.431435001+02:00
started: 2026-08-31T12:04:55.134823565+02:00
assignee: akar
tags:
    - docs
claimed_by: akar-14
claimed_at: 2026-08-31T12:06:04.431435001+02:00
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
