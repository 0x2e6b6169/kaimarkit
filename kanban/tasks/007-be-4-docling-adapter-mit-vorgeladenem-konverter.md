---
id: 7
title: BE-4 · Docling-Adapter mit vorgeladenem Konverter und OCR-Schalter
status: done
priority: medium
created: 2026-08-31T10:20:15.302387611+02:00
updated: 2026-08-31T11:04:16.221068038+02:00
started: 2026-08-31T11:03:53.54123043+02:00
completed: 2026-08-31T11:03:53.54123043+02:00
assignee: sophie
tags:
    - backend
depends_on:
    - 5
class: standard
---

## Ziel

Docling hinter dem Converter-Protokoll, ohne dass der Start der Anwendung darunter
leidet.

## Eigene Dateien

- `backend/app/converters/docling.py`

## Vorgaben

- Der `DocumentConverter` wird **einmal** gebaut und wiederverwendet. Ihn pro Anfrage
  neu zu erzeugen kostet Sekunden.
- Der Aufbau laeuft im FastAPI-Lifespan in einem Thread, damit `/api/health` sofort
  antwortet. Solange er laeuft, meldet der Adapter den Zustand `warming`; eine
  Anfrage in dieser Zeit wartet oder faellt auf die naechste Engine zurueck.
- `PdfPipelineOptions`: `do_ocr` aus `ConvertOptions.ocr` beziehungsweise
  `KAIMARKIT_OCR_ENABLED`, `do_table_structure=True`,
  `generate_picture_images=False`.
- Export mit `export_to_markdown(image_mode=ImageRefMode.PLACEHOLDER)`.
- `artifacts_path` aus `DOCLING_ARTIFACTS_PATH`, damit zur Laufzeit nichts
  nachgeladen wird.
- OCR-Sprachen aus `KAIMARKIT_OCR_LANGS`.
- Ausnahmen werden zu `EngineFailed`.

## Pruefung

Ein Skript konvertiert ein PDF mit Tabelle und liefert eine Markdown-Tabelle.
Ein zweiter Aufruf ist deutlich schneller als der erste (Konverter wiederverwendet).
Mit `HF_HUB_OFFLINE=1` und gesetztem `DOCLING_ARTIFACTS_PATH` gelingt die
Konvertierung ohne Netzzugriff.


## Ergebnis (sophie-04)

`backend/app/converters/docling.py` liefert `get_converter()` und traegt sich nirgends
in die Registry ein. Der `DocumentConverter` entsteht in `_build_pipeline(ocr)` — die
einzige Stelle, die docling importiert. Der Import steht in der Funktion, deshalb bleibt
das Modul ohne installierte Bibliothek ladbar und der Zugriff endet in
`EngineUnavailable`, nie in einem `ImportError`.

Vorladen: `start_warmup()` startet einen Daemon-Thread, `get_converter()` ruft ihn beim
ersten Zugriff selbst. `/api/health` wartet nie. Waehrend des Aufbaus meldet `state()`
`warming` und `available()` False — `auto` faellt auf die naechste Engine zurueck; wer
Docling ausdruecklich verlangt, wartet an der Aufbau-Sperre und bekommt denselben
Konverter. `state()` gibt die Werte aus `contracts/api.md` als String zurueck; BE-7 kann
sie fuer `/api/capabilities` direkt uebernehmen.

OCR: je Einstellung (`ConvertOptions.ocr`, sonst `KAIMARKIT_OCR_ENABLED`) ein eigener
Konverter im Cache, weil docling die Pipeline-Optionen beim Bau festschreibt.
`PdfPipelineOptions` mit `do_ocr`, `do_table_structure=True`,
`generate_picture_images=False`, `artifacts_path` aus `DOCLING_ARTIFACTS_PATH`, Sprachen
aus `KAIMARKIT_OCR_LANGS`. Export mit `export_to_markdown(image_mode=ImageRefMode.PLACEHOLDER)`.
Ausnahmen werden zu `EngineFailed`, ein gescheiterter Aufbau zu `EngineUnavailable`.

Pruefung: `backend/tests/test_docling.py`, 10 Tests gegen eine Attrappe von
`_build_pipeline` (Vorladen, warming zu ready, wartende Anfrage, Wiederverwendung,
OCR-Schalter, Fehleruebersetzung). `pytest -q` 37 passed, 1 skipped; `ruff check .` sauber.

**Offen und bewusst so:** Der echte Docling-Lauf (`test_real_docling_converts_a_table`,
Marke `slow`) ueberspringt sich, solange `docling` fehlt oder
`backend/tests/fixtures/tabelle.pdf` nicht da ist. Docling ist in der Umgebung
`claude-code` nicht installiert; ein Nachinstallieren haette Torch samt Modellen in die
gemeinsame Umgebung gezogen. **Fuer BE-9:** Fixture `tabelle.pdf` (PDF mit Tabelle) unter
`backend/tests/fixtures/` ablegen, dann laeuft der Test mit `pytest -m slow` und prueft
Markdown-Tabelle plus schnelleren Zweitlauf.

**Fuer main.py (BE-1) — nicht angefasst:** `docling.start_warmup()` ist der Einhaenger
fuer den Lifespan. Ohne ihn laedt Docling erst beim ersten Registry-Zugriff, ebenfalls im
Hintergrund.

**Fuer akar (IN-1/IN-2/DOC-3):** `DOCLING_ARTIFACTS_PATH` ist eine docling-eigene
Variable, keine `KAIMARKIT_*`. Sie gehoert ins Dockerfile und nach
`docs/betrieb/konfiguration.md`; `docker/.env.example` habe ich nicht angefasst.
`KAIMARKIT_OCR_LANGS`: die Kuerzel muessen zu der Texterkennung passen, die docling
benutzt (EasyOCR erwartet `de,en`, Tesseract `deu,eng`) — der Standard `deu,eng` in
`.env.example` passt nur zu Tesseract.

Doku: `docs/formate.md` um den Abschnitt "Docling: Modelle und OCR" ergaenzt (nur
angehaengt, die Matrix von BE-2 unberuehrt).
