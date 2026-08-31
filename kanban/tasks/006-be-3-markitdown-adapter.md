---
id: 6
title: BE-3 · MarkItDown-Adapter
status: done
priority: medium
created: 2026-08-31T10:20:14.617302932+02:00
updated: 2026-08-31T11:05:17.338242524+02:00
started: 2026-08-31T11:05:10.130693536+02:00
completed: 2026-08-31T11:05:10.130693536+02:00
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

## Ergebnis (sophie-05)

`backend/app/converters/markitdown.py` haelt `MarkItDownConverter` und
`get_converter()`. Die Bibliothek wird verzoegert geladen, `MarkItDown(enable_plugins=False)`
einmal gebaut und wiederverwendet. Kein LLM-Client — Bilder bleiben Alt-Text.
`available()` wirft nie; fehlt die Bibliothek, endet der Zugriff in `EngineUnavailable`,
jede Ausnahme der Bibliothek in `EngineFailed`. Ein Ergebnis aus reinem Leerraum
ergibt eine Warnung, keinen Fehler. `opts` bleibt ungenutzt: MarkItDown kennt kein OCR.

Geprueft: Skript wandelt eine erzeugte `tests/fixtures/sample.docx` und gibt
`# Erste Ueberschrift` / `## Zweite Ueberschrift` aus; `available()` gibt True.
`pytest -q` 43 passed, `ruff check .` sauber (auf main nach dem Merge).

Fuer BE-9: Die Fixture wurde nur zur Pruefung erzeugt und **nicht** eingecheckt —
`backend/tests/fixtures/*` gehoert BE-9. `backend/tests/test_markitdown.py` baut sein
docx selbst (zipfile, drei Teile: Content_Types, _rels/.rels, word/document.xml;
Ueberschriften ueber `w:pStyle w:val="Heading1"`), der Helfer `_write_docx` laesst sich
wiederverwenden. Der Test steht unter `pytest.importorskip("markitdown")`.

MarkItDown war in der pyenv-Umgebung `claude-code` nicht installiert; ich habe
`markitdown[docx]` nachinstalliert. `pyproject.toml` nennt `markitdown[all]` — im
Container passt das, lokal fehlen die uebrigen Extras.

Doku: `docs/formate.md` um den Abschnitt "MarkItDown" ergaenzt (Merge-Konflikt mit
dem Docling-Abschnitt aus BE-4 haendisch aufgeloest, beide Abschnitte stehen drin).
Keine neue `KAIMARKIT_*`-Variable, kein Eingriff in den Schnittstellen-Dreiklang.
