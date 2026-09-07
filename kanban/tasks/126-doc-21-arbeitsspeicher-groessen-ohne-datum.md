---
id: 126
title: DOC-21 · Arbeitsspeicher-Groessen ohne Datum
status: backlog
priority: low
created: 2026-09-07T09:44:37.470382744+02:00
updated: 2026-09-07T09:44:47.182070031+02:00
assignee: akar
tags:
    - docs
class: standard
---

## Befund (2026-09-07, gemeldet von akar-42 beim Abschluss von DOC-12)

`docs/betrieb/lokal.md:8` ("etwa 6 GB freier Arbeitsspeicher") und
`docs/betrieb/konfiguration.md:99` ("rund 2 GB" je Worker) sind gemessene Größen
ohne Datum. Sie wachsen mit dem Abbild, ohne dass jemand die Seite anfasst — dieselbe
Klasse wie DOC-12 (#86).

## Eigene Dateien

- `docs/betrieb/lokal.md`
- `docs/betrieb/konfiguration.md`

## Vorgaben

Wie in DOC-12 gelöst: ein datierter Messwert statt einer nackten Größe.

## Prüfung

- Keine undatierte Speicher-/Größenangabe mehr im Fließtext der genannten Stellen,
  geprüft über den geflachten Text.
- `mkdocs build --strict` läuft durch.
