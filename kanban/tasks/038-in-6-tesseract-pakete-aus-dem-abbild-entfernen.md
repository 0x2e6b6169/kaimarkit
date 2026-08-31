---
id: 38
title: IN-6 · tesseract-Pakete aus dem Abbild entfernen, EasyOCR-Gewichte sicherstellen
status: in-progress
priority: medium
created: 2026-08-31T12:04:18.074654123+02:00
updated: 2026-08-31T12:17:11.155603394+02:00
started: 2026-08-31T12:04:52.815073313+02:00
assignee: akar
tags:
    - infra
depends_on:
    - 37
claimed_by: akar-15
claimed_at: 2026-08-31T12:17:11.155603394+02:00
class: standard
---

## Ziel

Nach BE-12 (#37) waehlt der Adapter EasyOCR ausdruecklich. Damit werden
`tesseract-ocr`, `tesseract-ocr-deu` und `tesseract-ocr-eng` in
`docker/Dockerfile:127-129` nie mehr benutzt — sie waren es schon vorher nicht,
weil `OcrAutoModel` Tesseract gar nicht in seiner Auswahl fuehrt.

## Eigene Dateien

- `docker/Dockerfile`

## Vorgaben

- Die drei `tesseract-*`-Pakete aus der Laufzeitstufe entfernen.
- Vorher pruefen, ob eine andere Stelle im Abbild `tesseract` aufruft. Nur was
  nachweislich niemand benutzt, faellt weg.
- Die Modellgewichte von EasyOCR muessen im Abbild liegen, damit der Warmlauf
  mit `HF_HUB_OFFLINE=1` gelingt. Falls die Vorback-Stufe sie heute nicht holt,
  ist das hier zu ergaenzen — sonst tauscht dieses Ticket totes Gewicht gegen
  einen kaputten Offlinebetrieb.

## Pruefung

`docker build` gelingt, das Abbild ist kleiner als vorher (Zahl in die Notiz).
Eine Wandlung mit OCR gelingt im Container ohne Netzzugriff.
