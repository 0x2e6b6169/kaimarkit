---
id: 31
title: DOC-5 · def_list in mkdocs.yml nachtragen
status: todo
priority: low
created: 2026-08-31T11:16:04.308070874+02:00
updated: 2026-08-31T11:41:56.425326726+02:00
started: 2026-08-31T11:41:56.427926704+02:00
assignee: akar
tags:
    - docs
class: standard
---

## Ziel

`markdown_extensions` in `mkdocs.yml` kennt `def_list` nicht. Definitionslisten
rendern deshalb als Absaetze mit fuehrendem Doppelpunkt, und `mkdocs build --strict`
schlaegt dabei nicht an — der Fehler faellt erst beim Ansehen der Seite auf.

Gefunden in DOC-3 (#27) beim Beschreiben der Optionen von
`KAIMARKIT_API_MIDDLEWARES`. Dort ist die Stelle umformuliert, die Luecke bleibt.

## Eigene Dateien

- `mkdocs.yml`

## Vorgaben

`def_list` in `markdown_extensions` aufnehmen. Pruefen, ob weitere Erweiterungen
aus dem Material-Theme fehlen, die das Seitengeruest schon benutzt.

## Pruefung

Eine Testseite mit Definitionsliste rendert als `<dl>`, nicht als Absatz.
`mkdocs build --strict` endet mit 0 und ohne Warnung.
