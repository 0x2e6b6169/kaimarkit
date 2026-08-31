---
id: 8
title: BE-5 · Pandoc-Adapter mit --sandbox und Zeitgrenze
status: todo
priority: medium
created: 2026-08-31T10:20:15.927246151+02:00
updated: 2026-08-31T10:30:45.063841207+02:00
assignee: sophie
tags:
    - backend
depends_on:
    - 5
class: standard
---

## Ziel

Pandoc hinter dem Converter-Protokoll, sicher aufgerufen.

## Eigene Dateien

- `backend/app/converters/pandoc.py`

## Vorgaben

- `subprocess.run` mit Argumentliste, **niemals** `shell=True`.
- Feste Argumente: `--sandbox` (Pandoc greift auf keine Datei ausser der Eingabe zu),
  `--to=gfm-raw_html`, `--wrap=none`.
- Zeitgrenze aus `KAIMARKIT_PANDOC_TIMEOUT`; `TimeoutExpired` wird zu
  `ConversionTimeout`.
- Rueckgabewert ungleich null: die ersten Zeilen von stderr wandern in die Meldung
  von `EngineFailed`.
- `available()` prueft, ob die Binaerdatei im PATH liegt.
- **Kein PDF.** Die Endungsmenge enthaelt `.pdf` nicht - Pandoc kann PDF nicht lesen.

## Pruefung

Ein Skript konvertiert `tests/fixtures/sample.epub` und liefert Markdown.
Ein Aufruf mit `.pdf` wird von der Registry gar nicht erst an diesen Adapter
gereicht; ein direkter Aufruf wirft `UnsupportedFormat`.
