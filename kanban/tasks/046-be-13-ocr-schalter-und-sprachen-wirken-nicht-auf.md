---
id: 46
title: BE-13 · OCR-Schalter und Sprachen wirken nicht auf Bilder
status: backlog
priority: high
created: 2026-08-31T17:07:58.407903761+02:00
updated: 2026-08-31T17:07:58.407903761+02:00
assignee: sophie
tags:
    - backend
    - bug
class: standard
---

## Ziel

`ocr` und `KAIMARKIT_OCR_LANGS` sollen fuer alles gelten, was Docling durch die
Texterkennung schickt. Heute gelten sie nur fuer PDF.

## Befund (belegt in INT-2, 31.08.2026, im laufenden Container)

Dieselbe Seite, einmal als PDF und einmal als PNG, beide ohne Textebene:

```
gescannt.pdf  engine=docling ocr=true   -> 143 Zeichen
gescannt.pdf  engine=docling ocr=false  ->   0 Zeichen
scan.png      engine=docling ocr=true   -> Text erkannt
scan.png      engine=docling ocr=false  -> derselbe Text erkannt
```

Beim Bild aendert der Schalter nichts. Die Texterkennung laeuft in jedem Fall.

## Ursache

`backend/app/converters/docling.py`, `_build_pipeline` (Zeilen 64 bis 82): Die
`PdfPipelineOptions` mit `do_ocr`, `artifacts_path` und `EasyOcrOptions(lang=...)`
gehen ausschliesslich an `InputFormat.PDF`:

```python
converter = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)}
)
```

Fuer `InputFormat.IMAGE` legt Docling seine eigene Voreinstellung an. Damit faellt
dreierlei weg: `do_ocr`, die Sprachen aus `KAIMARKIT_OCR_LANGS` und die
ausdrueckliche Wahl von EasyOCR aus BE-12 (#37).

Dass eine andere Maschine laeuft, zeigt der Lauf der langsamen Tests im Container:
`test_docling_liest_ein_bild_ohne_zu_scheitern` erzeugt eine Warnung aus
`docling/models/stages/ocr/rapid_ocr_model.py` — RapidOCR, nicht EasyOCR.

## Warum das mehr ist als eine Feinheit

IN-6 (#38) hat die tesseract-Pakete aus dem Abbild genommen, weil der Adapter
EasyOCR ausdruecklich waehlt, und backt nur dessen Gewichte ein. Fuer Bilder trifft
diese Begruendung nicht zu.

Drei Stellen der Dokumentation sagen ausdruecklich das Gegenteil des Verhaltens:

- `docs/betrieb/konfiguration.md:49` — "Docling schickt gescannte Seiten und Bilder
  durch die Texterkennung", gesteuert von `KAIMARKIT_OCR_ENABLED`
- `docs/formate.md:59` — derselbe Satz
- `docs/formate.md:63` und `docs/grenzen.md:57` — die Sprachen kommen aus
  `KAIMARKIT_OCR_LANGS`

Sie beschreiben das Gewollte. Der Quelltext gehoert dorthin gebracht, nicht die
Dokumentation zurueckgenommen.

## Eigene Dateien

- `backend/app/converters/docling.py`
- `backend/tests/test_docling.py`

## Vorgaben

Die Bildformate bekommen dieselben Optionen wie PDF. In der Sprache von Docling
heisst das ein zweiter Eintrag in `format_options` fuer `InputFormat.IMAGE`.
`.png`, `.jpg`, `.jpeg` und `.tiff` stehen in `EXTENSIONS` und in
`/api/capabilities`, alle vier mit docling an erster Stelle.

## Pruefung

- Ein Test faehrt dasselbe Bild mit `ocr=true` und `ocr=false` durch den Adapter.
  Mit `false` kommt kein erkannter Text zurueck, mit `true` schon. Ohne die
  Korrektur schlaegt genau dieser Test fehl — das ist die Gegenprobe.
- Der Lauf mit `-m slow` erzeugt keine Warnung mehr aus `rapid_ocr_model.py`.
- `pytest -q` und `pytest -q -m slow` bleiben gruen.
