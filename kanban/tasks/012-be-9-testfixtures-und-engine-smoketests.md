---
id: 12
title: BE-9 · Testfixtures und Engine-Smoketests
status: todo
priority: medium
created: 2026-08-31T10:20:18.427682548+02:00
updated: 2026-08-31T10:30:45.066681558+02:00
assignee: sophie
tags:
    - backend
depends_on:
    - 6
    - 7
    - 8
class: standard
---

## Ziel

Belegen, dass jede Engine mit einer echten Datei arbeitet.

## Eigene Dateien

- `backend/tests/fixtures/*`
- `backend/tests/test_converters.py`
- `backend/tests/test_api.py`

## Vorgaben

- Je eine moeglichst kleine Beispieldatei pro Format: pdf, docx, epub, pptx, xlsx,
  html, csv, odt, png. Selbst erzeugt, keine fremden Inhalte.
- `test_converters.py` prueft je Engine: Ergebnis ist nicht leer, enthaelt einen
  erwarteten Textbaustein, `engine` stimmt.
- Docling-Tests mit `@pytest.mark.slow` versehen und in `pyproject.toml` aus dem
  Standardlauf ausschliessen - sie brauchen die Modelle und dauern.
- `test_api.py` deckt die Fehlerpfade ab: 413, 415, 400 bei ungeeigneter Engine.

## Pruefung

`pytest -q` laeuft ohne Docling-Modelle durch. `pytest -q -m slow` laeuft mit
Modellen durch.
