---
id: 5
title: BE-2 · Converter-Protokoll, Faehigkeitsmatrix, Auswahl und Fallback
status: done
priority: high
created: 2026-08-31T10:20:13.905482705+02:00
updated: 2026-08-31T10:57:11.385596348+02:00
started: 2026-08-31T10:57:10.621720659+02:00
completed: 2026-08-31T10:57:10.621720659+02:00
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


## Ergebnis (sophie-02)

Gebaut auf `task/05-converter-registry`, `--no-ff` nach main gemergt.

**Schnittstelle für BE-3 bis BE-5.** Jedes Enginemodul (`converters/markitdown.py`,
`docling.py`, `pandoc.py`) stellt genau eine Funktion bereit:
`get_converter() -> Converter`. Die Registry ruft sie beim ersten Zugriff auf und
merkt sich das Ergebnis; kein Enginemodul trägt sich irgendwo ein. Der Konverter
braucht `name: str`, `extensions: tuple[str, ...]`, `available() -> bool` und
`convert(path: Path, opts: ConvertOptions) -> ConversionResult`. `duration_ms` setzt
die Registry (Gesamtdauer einschließlich gescheiterter Versuche), eine Engine darf
das Feld auf 0 lassen. Jede Bibliotheksausnahme wird zu `ConversionError`.

**Registry-API:** `PREFERENCES`, `ENGINE_NAMES`, `PASSTHROUGH`, `get_converter(name)`,
`preferences_for(ext)`, `engines_for(ext)`, `select(ext, requested)`,
`convert_with_fallback(path, opts)`. Für `/api/capabilities` (BE-7): über
`PREFERENCES.keys()` laufen und `engines_for(ext)` nehmen — das filtert bereits alles
heraus, was nicht lädt oder nicht bereit ist.

`.md` und `.markdown` bedient ein eingebauter Konverter namens `passthrough`; er liest
die Datei und gibt sie unverändert zurück. Er steht in `engines_for(".md")`. BE-7
entscheidet, ob er auch im `engines`-Wörterbuch von `/api/capabilities` auftaucht.

**Geprüft:** `pytest backend/tests/test_registry.py -q` — 14 Tests grün, ohne
installierte Engine (Attrappen im Cache `_INSTANCES`). Abgedeckt: Präferenz je Endung,
pandoc fehlt bei `.pdf`, unbekannte Endung (415), angeforderte Engine ohne Eignung
(400), unbekannter Enginename und fehlendes Modul (beides `EngineUnavailable`, kein
ImportError), Fallback an und aus, `KAIMARKIT_DEFAULT_ENGINE`, Durchreichen von `.md`.
`ruff check .` sauber.

**Zwei Randnotizen für PO/SM:**
1. `backend/tests/conftest.py` neu angelegt (drei Zeilen, legt `backend/` auf
   `sys.path`) — ohne sie findet kein Test `app`, weil das Paket nicht installiert
   ist. Die Datei gehört keinem Ticket; BE-9 braucht sie ebenfalls.
2. `docs/formate.md` enthält jetzt die Fähigkeitsmatrix samt Auswahl und Rückfall.
   Die Seite gehört laut Schnitt DOC-2 — dort also übernehmen statt neu schreiben.

Der Schnittstellen-Dreiklang blieb unangetastet.
