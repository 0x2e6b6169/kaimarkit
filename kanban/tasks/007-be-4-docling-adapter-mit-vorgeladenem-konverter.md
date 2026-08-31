---
id: 7
title: BE-4 · Docling-Adapter mit vorgeladenem Konverter und OCR-Schalter
status: todo
priority: medium
created: 2026-08-31T10:20:15.302387611+02:00
updated: 2026-08-31T10:30:45.06134009+02:00
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
