---
id: 6
title: BE-3 · MarkItDown-Adapter
status: todo
priority: medium
created: 2026-08-31T10:20:14.617302932+02:00
updated: 2026-08-31T10:30:45.060773362+02:00
assignee: sophie
tags:
    - backend
depends_on:
    - 5
class: standard
---

## Ziel

MarkItDown hinter dem Converter-Protokoll.

## Eigene Dateien

- `backend/app/converters/markitdown.py`

## Vorgaben

- `MarkItDown(enable_plugins=False)`, einmal erzeugt und wiederverwendet.
- Kein LLM-Client. Bilder werden dadurch ohnehin nur als Alt-Text uebernommen, was
  der gewuenschten Platzhalter-Behandlung entspricht.
- Alle Ausnahmen von markitdown werden zu `EngineFailed` aus `errors.py`. Nichts
  Bibliotheksspezifisches dringt nach aussen.
- `available()` prueft den Import, ohne zu werfen.
- Leeres Ergebnis (nur Leerraum) ergibt eine Warnung im Ergebnis, keinen Fehler.

## Pruefung

Ein Skript konvertiert `tests/fixtures/sample.docx` und gibt Markdown mit
Ueberschriften aus. `python -c "from app.converters.markitdown import ...; print(c.available())"`
gibt True.
