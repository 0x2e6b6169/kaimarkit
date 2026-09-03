---
id: 106
title: 'BE-34 · OCR auf Bildern liefert keinen Text: Befund im Abbild (GitHub #2)'
status: in-progress
priority: high
created: 2026-09-03T11:20:26.183542324+02:00
updated: 2026-09-03T11:41:51.442530267+02:00
assignee: sophie
tags:
    - backend
    - gh-2
claimed_by: sophie-35
claimed_at: 2026-09-03T11:41:51.442954215+02:00
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


## Befund vor der Änderung (sophie-35, 2026-09-03)

Gemessen gegen `kaimarkit:local` (7f5ea938ee70, gebaut aus dem Zweig `task/106-ocr-images` ohne Änderung am Adapter; docling 2.124.0, easyocr 1.7.2) in einem eigenen Container auf 127.0.0.1:18034, nach `docling: ready` in `/api/capabilities`. `Accept: application/json`; „Satz“ ist `Dieser Satz stammt aus einem Scan`. `scan.pdf` ist eine Seite, nur Bild, ohne Textebene (im Scratchpad gebaut, kein Fixture).

| Datei | Aufruf | HTTP | engine | warnings | Länge | Satz enthalten | ms |
|---|---|---|---|---|---|---|---|
| scan.png | engine=docling ocr=true | 200 | docling | [] | 37 | ja | 10443 |
| scan.png | ohne engine, ocr=true | 200 | docling | [] | 37 | ja | 9892 |
| scan.png | ohne engine, ohne ocr | 200 | docling | [] | 37 | ja | 6118 |
| scan.png | engine=markitdown | 200 | markitdown | „MarkItDown hat in scan.png keinen Text gefunden.“ | 0 | nein | 45 |
| scan.pdf | engine=docling ocr=true | 200 | docling | [] | 34 | ja | 6708 |
| scan.pdf | ohne engine, ocr=true | 200 | docling | [] | 34 | ja | 4558 |
| scan.pdf | ohne engine, ohne ocr | 200 | docling | [] | 34 | ja | 12307 |
| scan.pdf | engine=markitdown | 200 | markitdown | „… keinen Text gefunden.“, „… übernimmt keine Bilder aus PDF …“ | 0 | nein | 62 |

Das Markdown lautet `## Dieser Satz stammt aus einem Scan.` (PNG) beziehungsweise `Dieser Satz stammt aus einem Scan.` (PDF). Weitere Varianten, je `engine=docling ocr=true` / `ohne engine, ohne ocr`:

| Datei | engine | Länge | Satz enthalten | ms |
|---|---|---|---|---|
| scan.jpg | docling | 36 / 36 | ja / ja | 6498 / 8267 |
| SCAN.JPG (Großschreibung) | docling | 36 / 36 | ja / ja | 17283 / 16623 |
| scan.tiff | docling | 37 / 37 | ja / ja | 19384 / 6997 |
| foto.jpg (3000×4000, farbig, drei Zeilen mit Umlauten) | docling | 109 / 109 | ja / ja | 29951 / 62451 |
| foto_exif6.jpg (dasselbe Foto, Pixel um 90° gedreht, EXIF-Orientation 6) | docling | 1 / 1 | nein / nein | 52101 / 113116 |

Dieselben Aufrufe gegen das Abbild, das auf :8080 läuft (b9904f91448f vom 01.09., Version 0.1.0): identisch — scan.png und scan.pdf liefern den Satz in allen drei Docling-Aufrufen, MarkItDown liefert leer mit Warnung, foto_exif6.jpg liefert `g`.

**Ergebnis:** Der Adapter, EasyOCR und die Modelle im Abbild funktionieren. PNG, JPG, TIFF und Bild-PDF kommen mit Text zurück, mit und ohne ausdrückliches `ocr`, weil `KAIMARKIT_OCR_ENABLED=true` gilt. Ein Fehler in `registry.py`, in der Pipeline-Wahl oder bei den Modellen liegt nicht vor; der vorhandene slow-Test `test_the_ocr_switch_works_on_images` bestand schon vorher.

**Was der Nutzer gesehen haben kann:**

1. **Ein Foto vom Handy.** Kameras speichern die Pixel quer und schreiben die Drehung als EXIF-Orientation. Doclings `ImageDocumentBackend` öffnet das Bild mit `img.convert("RGB")` und wertet den Tag nicht aus (`docling/backend/image_backend.py`, kein `exif_transpose`). EasyOCR sieht dann Text um 90° gedreht und findet nichts — Markdown `g`, keine Warnung. Das ist der eine Fall in der Messung, der leer bleibt, und er liegt im Backend: Der Adapter kann das Bild vor der Übergabe aufrichten. **Das wird hier behoben.**
2. **`engine=auto` in den ersten Minuten nach dem Start.** Solange Docling `warming` meldet, nimmt die Registry für `.png`/`.jpg` MarkItDown; das liefert leer, und die Antwort sagt es in `warnings` („MarkItDown hat in X keinen Text gefunden.“). Im Frontend steht dann „1 Warnung“ an der Datei. `/api/health` meldet in dieser Zeit `ok` — das ist so gebaut, der Zustand steht in `/api/capabilities`. `docs/grenzen.md` beschreibt das schon.
3. Der OCR-Schalter im Frontend ist keine Ursache: Nicht angeklickt schickt er `ocr` nicht mit, und dann gilt die Vorgabe `true`.
