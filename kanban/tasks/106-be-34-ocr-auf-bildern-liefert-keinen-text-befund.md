---
id: 106
title: 'BE-34 · OCR auf Bildern liefert keinen Text: Befund im Abbild (GitHub #2)'
status: done
priority: high
created: 2026-09-03T11:20:26.183542324+02:00
updated: 2026-09-03T14:35:35.037092741+02:00
started: 2026-09-03T14:35:34.305954375+02:00
completed: 2026-09-03T14:35:34.305954375+02:00
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


## Umsetzung (sophie-37, 2026-09-03)

**Ursache.** Der eine leere Fall der Messung liegt an der EXIF-Orientation, nicht an OCR. Doclings `ImageDocumentBackend` öffnet ein Bild mit `img.convert("RGB")` und wertet den Tag `Orientation` nicht aus (docling 2.124). Ein Handyfoto legt die Pixel quer ab und notiert die Drehung nur dort; EasyOCR sieht den Text um 90° gedreht und findet nichts.

**Änderung.** `backend/app/converters/docling.py` bekommt `_upright_image(path)`. Die Funktion liest bei den vier Bildendungen den Tag, richtet das Bild mit `PIL.ImageOps.exif_transpose` auf und gibt es als PNG im Speicher zurück; `run()` reicht es über `DocumentStream` an Docling. Ohne Tag, bei Orientation 1 und bei mehrseitigen TIFFs bleibt der Weg wie bisher — dieselbe Datei, derselbe Pfad. Das `convert("RGB")` vor dem Schreiben ist dasselbe, was Doclings Backend gleich danach tut; es steht dort, weil PNG nicht jeden Modus speichern kann. Konvention 3 bleibt gewahrt: Alles, was PIL oder Docling werfen, landet in `convert()` und wird zu `EngineFailed`.

**Neuer Fixture.** `build_fixtures.py` baut `foto_exif6.jpg` — denselben Satz wie `scan.png`, nur um 90° gegen den Uhrzeigersinn gespeichert und mit Orientation 6 versehen. Beide Vorlagen unterscheiden sich in nichts als der Drehung; `exif_transpose` bildet die eine auf die andere ab (mittlere Abweichung 0,14 von 255, gegen 14,96 bei 180° verdreht).

**Rot vor grün.** Mit dem alten Adapter, sonst allem Neuen: `tests/test_docling_ocr.py` im Abbild `1 failed, 1 passed, 2 deselected` — der aufrechte Scan bestand, das Foto fiel. Nach der Änderung bestehen beide.

**Zahlen.**

- `make test-slow-image`: 154 gesammelt, 9 ausgewählt, **9 bestanden**, 145 abgewählt, 178 s.
- `pytest -q -rs` im Backend: 154 gesammelt, 145 ausgewählt, **145 bestanden**, 9 abgewählt, 15 s. Die slow-Tests erscheinen dort nicht als übersprungen, sondern als abgewählt — `addopts = ["-m", "not slow"]` in `backend/pyproject.toml` nimmt sie über die Marke heraus, nicht über `skipif`. Die Zahl stieg von 7 auf 9; verschluckt wird nichts.
- `ruff check .`: sauber.

**Nachweis am Container.** Abbild neu gebaut (`make build`), eigener Container auf 127.0.0.1:18034, nach `"docling":"ready"`. `curl -F file=@foto_exif6.jpg -F ocr=true` liefert `## Dieser Satz stammt aus einem Scan.`, `warnings: []`, 6862 ms; ohne `ocr` und mit `engine=docling` dasselbe in 6106 ms. `scan.png` unverändert grün. Container entfernt.

**Was aus den beiden anderen Erklärungen folgt.**

1. *Warming-Rückfall auf MarkItDown.* Bleibt, wie er ist, und ist kein Fehler: In den ersten Minuten nach dem Start nimmt `engine=auto` für `.png`/`.jpg` MarkItDown, das Ergebnis ist leer, und die Antwort sagt es in `warnings`. `docs/grenzen.md` beschreibt das schon. Wer sicher OCR will, nennt Docling ausdrücklich. Ob das Frontend diesen Zustand deutlich genug zeigt — „1 Warnung" an der Datei —, ist eine Frage an benny, nicht an diese Lane.
2. *Der OCR-Schalter im Frontend* ist keine Ursache. Nicht angeklickt schickt er `ocr` nicht mit; dann gilt `KAIMARKIT_OCR_ENABLED`, Vorgabe `true`. Gemessen: dieselben Ergebnisse mit und ohne `ocr`.

**`docs/grenzen.md` bleibt unverändert.** Der Abschnitt „Gescannte Seiten ohne OCR bleiben leer" sagt nichts, was durch diese Änderung falsch wird: Er handelt von Vorlagen ohne Textebene und vom Warming-Rückfall, beides gilt weiter.

Zweig `task/106-ocr-images`, Commit `86b5c0f`, Merge `b772ca2`.
