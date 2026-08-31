---
id: 37
title: 'BE-12 · OCR-Maschine ausdruecklich setzen: EasyOCR mit de,en'
status: todo
priority: high
created: 2026-08-31T12:03:54.39201469+02:00
updated: 2026-08-31T12:04:51.15275163+02:00
started: 2026-08-31T12:04:51.169484447+02:00
assignee: sophie
tags:
    - backend
    - bug
class: standard
---

## Ziel

`KAIMARKIT_OCR_LANGS` wirkt zurzeit gar nicht — nicht in der falschen
Schreibweise, sondern ohne jede Wirkung.

`docling.py:62-76` baut `PdfPipelineOptions()` ohne ausdrueckliche OCR-Maschine
und setzt danach `options.ocr_options.lang = langs`. Die Vorgabe von docling ist
`OcrAutoOptions`, deren `lang` absichtlich leer bleibt ("Language settings are
deferred to the chosen engine's defaults"). `OcrAutoModel` probiert die Maschinen
durch und baut die gewaehlte mit einem frischen Options-Objekt, aus dem nur
`mode` uebernommen wird. Das gesetzte `lang` faellt dabei weg.

Belegt von akar-11 auf Ankercommit `187705a`. Der Code-Teil ist gegengeprueft:
`PdfPipelineOptions()` steht dort ohne `ocr_options`. Die Aussage ueber die
Bibliotheksvorgabe stammt aus akar-11s Lektuere des docling-Quelltexts und liess
sich hier nicht nachvollziehen, weil docling in der Entwicklungsumgebung nicht
installiert ist. Sie aendert am Ergebnis nichts: Sich auf die Vorgabe einer nach
oben offenen Abhaengigkeit zu verlassen, ist der Fehler.

## Entscheidung des Nutzers (2026-08-31)

**EasyOCR, ausdruecklich gesetzt.** `EasyOcrOptions(lang=[...])` mit ISO 639-1,
also `de,en`. Begruendung: schlechtes OCR erzeugt falsches Markdown, und dann
prueft man den Kontext umsonst — Erkennungsqualitaet schlaegt hier Bildgroesse.
Das Abbild baeckt ohnehin Modelle vor (`HF_HUB_OFFLINE=1`,
`DOCLING_ARTIFACTS_PATH`), EasyOCR fuegt sich also ein.

Die drei `tesseract-*`-Pakete werden damit totes Gewicht. Ihr Ausbau ist IN-6
(akars Lane, eigene Datei) — hier nicht anfassen.

## Eigene Dateien

- `backend/app/converters/docling.py`
- `backend/app/config.py`
- `backend/pyproject.toml`

`docker/Dockerfile` gehoert IN-6, `docker/.env.example` und
`docs/betrieb/konfiguration.md` gehoeren DOC-6 (#34). Beide haengen an diesem
Ticket.

## Vorgaben

- Der Adapter setzt `ocr_options` ausdruecklich auf `EasyOcrOptions` und uebergibt
  die Sprachen aus `settings.ocr_langs`. Keine Abhaengigkeit mehr von der Vorgabe
  der Bibliothek.
- `config.py:34` setzt `ocr_langs = "de,en"`.
- `docling>=2.0` in `pyproject.toml:19` bekommt eine Untergrenze, unter der die
  benutzte Options-Klasse nachweislich existiert. Welche Fassung das ist, gehoert
  in die Ticketnotiz.
- Konvention 2 gilt: der Import bleibt im Adaptermodul.

## Pruefung

Ein Test zeigt, dass der gebaute Konverter `EasyOcrOptions` mit genau den
Sprachen aus `KAIMARKIT_OCR_LANGS` fuehrt — vor der Aenderung ist er rot, weil
die Sprachliste nicht ankommt. `pytest -q` und `ruff check .` bleiben gruen.
