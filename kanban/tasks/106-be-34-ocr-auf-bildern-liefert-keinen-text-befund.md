---
id: 106
title: 'BE-34 · OCR auf Bildern liefert keinen Text: Befund im Abbild (GitHub #2)'
status: todo
priority: high
created: 2026-09-03T11:20:26.183542324+02:00
updated: 2026-09-03T11:20:26.183542324+02:00
assignee: sophie
tags:
    - backend
    - gh-2
class: standard
---

## Ziel

GitHub-Issue #2, vom Nutzer präzisiert: „Ich habe bei noch keinem Test mit Bildern ein Ergebnis von OCR gesehen." Ein hochgeladenes Bild mit Text (PNG, JPG) kommt ohne den Text zurück. Das Ticket klärt im Abbild, wo der Text verloren geht, und behebt es, wenn die Ursache im Backend liegt.

Was der Quelltext behauptet, und was deshalb zu prüfen ist:

- `registry.py` nennt für `.png`, `.jpg`, `.jpeg`, `.tiff` zuerst `docling`, dann `markitdown`. MarkItDown kennt kein OCR; läuft das Bild dort, kommt nichts.
- `docling.py` setzt `ImageFormatOption(pipeline_options=options)` mit `do_ocr` und EasyOCR (`KAIMARKIT_OCR_LANGS`).
- Das Frontend schickt ohne Klick `ocr` gar nicht mit (`null`); dann gilt `KAIMARKIT_OCR_ENABLED`, Vorgabe `true`.

Jede dieser Stellen kann die Ursache sein, oder keine: fehlende EasyOCR-Modelle im Abbild, ein `warming`-Zustand, der still auf MarkItDown zurückfällt, ein Bild, das Docling als leer ansieht.

## Eigene Dateien

- `backend/app/converters/docling.py`
- `backend/tests/test_docling_ocr.py`
- `backend/tests/fixtures/build_fixtures.py` und ein neues Fixture `backend/tests/fixtures/scan.png` (gerendertes Bild mit einem bekannten deutschen Satz, aus `build_fixtures.py` erzeugt; `bild.png` bleibt, was es ist)
- `docs/grenzen.md` (Abschnitt „Gescannte Seiten ohne OCR bleiben leer"), nur falls der Befund dort etwas Unwahres hinterlässt

Liegt die Ursache im Frontend (Schalter, Enginewahl) oder im Abbild (Modelle, Dockerfile): melden und übergeben, nicht selbst ändern.

## Vorgaben

- **Erst messen.** Abbild bauen (`make build`), Container starten, dann mit `curl` gegen `/api/convert`: `-F file=@scan.png -F engine=docling -F ocr=true`, dann ohne `engine`, dann ohne `ocr`, dann `engine=markitdown`. Je Lauf: `engine` und `warnings` aus der Antwort, Länge des Markdown, ob der Satz darin steht. Diese Tabelle steht in der Ticketnotiz, **bevor** etwas geändert wird.
- Dasselbe mit einem gescannten PDF (eine Seite, nur Bild). Ob PDF und Bild sich gleich verhalten, grenzt die Ursache ein.
- Abbild und Maschine sind ein Betriebsmittel: Während der Messung baut und misst niemand sonst. Läuft ein anderer Bau, warten.
- Ein slow-Test, der `scan.png` durch den Docling-Adapter mit `ocr=True` schickt und den Satz im Ergebnis erwartet, gehört in `test_docling_ocr.py` (Markierung `slow`, läuft mit `make test-slow-image`). Er belegt den Zustand, gleich ob rot oder grün: Läuft er vorher grün, liegt der Fehler nicht im Adapter, und das ist ein Befund.
- Konvention 3: Was EasyOCR oder Docling werfen, bleibt `ConversionError`.

## Prüfung

1. Die Messtabelle steht in der Notiz: vier Aufrufe für PNG, dieselben für das Scan-PDF.
2. `make test-slow-image` grün, einschließlich des neuen Tests; Sammelzahl und ausgewählte Zahl nennen.
3. `pytest -q -rs` im Backend grün; der neue Test wird dort als übersprungen **genannt**, nicht verschluckt.
4. Nach dem Merge liefert `curl -F file=@scan.png -F ocr=true` gegen den Container Markdown, das den Satz enthält. Widerspricht das Ergebnis dem Nutzerbefund (OCR ging schon immer), sagt die Notiz, was der Nutzer stattdessen gesehen haben kann und an welche Lane der Rest geht.
