---
id: 132
title: FE-28 · MarkdownPreview bekommt keinen Dateinamen
status: backlog
priority: medium
created: 2026-09-07T11:19:46.212022153+02:00
updated: 2026-09-07T11:19:46.212022153+02:00
assignee: benny
tags:
    - frontend
class: standard
---

## Befund (2026-09-07, gemeldet von akar-43 beim Abschluss von DOC-23)

`App.vue` reicht `MarkdownPreview` kein `:filename` durch, obwohl der
Komponentenkopf es ausdrücklich vorsieht. In der aufgeklappten Zeile steht deshalb
"Ergebnis" statt des Dateinamens. Bei mehreren Dateien in der Warteschlange lässt
sich so nicht erkennen, welche Vorschau man gerade vor sich hat.

## Eigene Dateien

- `frontend/src/App.vue`
- `frontend/src/components/MarkdownPreview.vue`, falls die Weitergabe dort etwas
  ändert (erst nachsehen, nicht raten)

## Vorgaben

`:filename` von der Warteschlangenzeile bis zur Vorschau durchreichen.

## Prüfung

- Rot vor grün: ein Test, der bei mehreren Dateien in der Warteschlange den
  Dateinamen in der aufgeklappten Vorschau erwartet, fällt vor der Arbeit durch.
- `npm run test`, `npm run typecheck` sauber.
