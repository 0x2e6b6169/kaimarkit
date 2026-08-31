---
id: 39
title: FE-8 · Favicon fuer frontend/index.html
status: todo
priority: low
created: 2026-08-31T12:04:19.217951051+02:00
updated: 2026-08-31T12:04:54.087648974+02:00
started: 2026-08-31T12:04:54.100728418+02:00
assignee: benny
tags:
    - frontend
class: standard
---

## Ziel

`frontend/index.html` nennt kein Favicon. Der Browser fragt bei jedem Aufruf
`/favicon.ico` und bekommt 404. Kosmetisch, keine Abweichung vom Vertrag —
gemeldet von INT-1 (#29).

## Eigene Dateien

- `frontend/index.html`
- die neue Symboldatei unter `frontend/public/`

## Vorgaben

- Ein schlichtes Symbol, das ohne Netz auskommt und im Abbild mitgeliefert wird.
- Kein zusaetzliches Paket dafuer.

## Pruefung

Ein Aufruf der Seite erzeugt keine 404 auf `/favicon.ico` mehr. `npm run build`
nimmt die Datei mit.
