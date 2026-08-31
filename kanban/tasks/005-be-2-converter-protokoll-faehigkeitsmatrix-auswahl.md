---
id: 5
title: BE-2 · Converter-Protokoll, Faehigkeitsmatrix, Auswahl und Fallback
status: todo
priority: high
created: 2026-08-31T10:20:13.905482705+02:00
updated: 2026-08-31T10:30:45.060260552+02:00
assignee: sophie
tags:
    - backend
depends_on:
    - 3
class: standard
---

## Ziel

Die Abstraktion, hinter der die drei Engines verschwinden, samt der Entscheidung,
welche Engine eine Datei bekommt.

## Eigene Dateien

- `backend/app/converters/base.py`
- `backend/app/converters/registry.py`
- `backend/tests/test_registry.py`

## Vorgaben

- `base.py`: `ConversionResult` (markdown, engine, warnings, duration_ms),
  `ConvertOptions` (engine, ocr), `Converter` als `Protocol` mit `name`,
  `extensions`, `available()`, `convert(path, opts)`.
- `registry.py` haelt die Praeferenzliste je Endung. Sie steht im Code, nicht in der
  Konfiguration - sie beschreibt, was die Bibliotheken koennen.
- **Wichtig:** Diese Datei nennt alle drei Enginenamen und laedt die Module
  verzoegert (Import erst beim ersten Zugriff). Die Engine-Tickets BE-3 bis BE-5
  liefern nur ihr eigenes Modul und tragen sich hier nirgends ein - sonst
  kollidieren drei Tickets, die gleichzeitig laufen sollen.
- Matrix laut Plan. `.pdf` fuehrt docling vor markitdown, pandoc taucht bei `.pdf`
  nicht auf. `.md` wird durchgereicht.
- `engines_for(ext)`, `select(ext, requested)`, `convert_with_fallback(...)`.
  Eine ausdruecklich angeforderte Engine wird nie durch eine andere ersetzt.
  `KAIMARKIT_ENABLE_FALLBACK` schaltet den Rueckfall global ab,
  `KAIMARKIT_DEFAULT_ENGINE` ueberschreibt die Praeferenz.
- Eine fehlende Engine (Modul nicht installiert) fuehrt zu `EngineUnavailable`,
  nicht zu einem ImportError.

## Pruefung

`pytest backend/tests/test_registry.py -q` gruen. Abgedeckt: Praeferenzreihenfolge
je Endung, unbekannte Endung, angeforderte Engine ohne Eignung, Fallback an und aus.
Die Tests laufen mit Attrappen, ohne dass eine echte Engine installiert sein muss.
