---
id: 117
title: 'BE-38 · OCR bei Bildern in Dokumenten: erst messen, dann entscheiden (GitHub #2)'
status: todo
priority: high
created: 2026-09-03T14:55:02.223095162+02:00
updated: 2026-09-03T14:55:02.223095162+02:00
assignee: sophie
tags:
    - backend
    - gh-2
class: standard
---

## Ziel

Die Antwort des Nutzers auf GitHub-Issue #2 ist da, und sie schließt beide bisherigen
Erklärungen aus. Auf die Frage, was er hochgeladen hat, sagt er: **ein Dokument mit
einem Bild darin.** Auf die Frage nach einem Warnhinweis: **ja, eine Warnung stand da.**

Es waren also keine Handyfotos (BE-34, EXIF-Drehung) und keine Bilddateien, die den
`warming`-Rückfall getroffen hätten. Sophies Verdacht aus der BE-34-Messung passt genau:
Ein Dokument mit Textebene — docx oder PDF — wird als Text erkannt, die Textebene
gelesen, und die eingebetteten Bilder laufen nicht durch OCR. Wer ein Word-Dokument mit
einem abfotografierten Absatz hochlädt, bekommt alles außer diesem Absatz. Genau das
heißt „bei noch keinem Test mit Bildern ein Ergebnis von OCR gesehen".

Der Verdacht ist nicht gemessen. **Dieses Ticket misst zuerst und entscheidet danach.**

## Eigene Dateien

- `backend/app/converters/docling.py`
- `backend/tests/test_docling_ocr.py`
- `backend/tests/fixtures/build_fixtures.py` und ein neues Fixture: ein Dokument mit
  Textebene, in dem ein Bild mit einem bekannten deutschen Satz steckt. Name und Format
  wählt die Umsetzung; `scan.png`, `foto.jpg` und `foto_exif6.jpg` bleiben, was sie sind.

Nicht hier: `converters/markitdown.py` und `converters/registry.py`. Falls die Ursache
dort liegt, melden und übergeben — die Registry gehört BE-2.

Nicht hier: `docs/formate.md` und `docs/grenzen.md`. Was die Messung ergibt, geht als
Befund an den PO und wird ein eigenes Doku-Ticket. Ein Satz über OCR, der auf einer
ungemessenen Annahme steht, ist schlimmer als kein Satz.

## Vorgaben

Die Messung beantwortet drei Fragen, jede mit dem tatsächlichen Markdown als Beleg:

1. Ein **docx** mit Textebene und einem eingebetteten Bild, `engine=docling`, `ocr=true`
   im Abbild: Steht der Satz aus dem Bild im Ergebnis?
2. Dasselbe für ein **PDF mit Textebene** und eingebettetem Bild.
3. Dieselben zwei Dateien mit `engine=markitdown`: Was kommt zurück, und **welche
   Warnung** setzt die Engine? Der Wortlaut gehört in die Notiz — der Nutzer hat eine
   Warnung gesehen und ist daraus nicht klüger geworden.

Führt Docling einen Schalter, der eingebettete Bilder durch OCR schickt, gehört er
angeschaltet, sofern `ocr` gesetzt ist — dann ist es ein Fehler und wird behoben.
Führt Docling keinen, ist es eine Grenze der Engine und **wird nicht nachgebaut**: Bilder
selbst aus einem Dokument zu schneiden und einzeln durch OCR zu schicken, ist ein eigenes
Vorhaben und nicht Gegenstand dieses Tickets. Dann endet das Ticket mit der Messung, und
die Grenze wird dokumentiert statt umgangen.

## Prüfung

- Die drei Messungen stehen mit Markdown-Ausschnitt und Warnungstext in der Ticketnotiz.
  Ohne Abbild ist das nicht messbar: `make test-slow-image`, nicht die pyenv-Umgebung.
- Fall „Fehler": Rot vor grün im Abbild belegt — der neue Test fällt mit dem alten
  Adapter durch und besteht mit dem neuen.
- Fall „Grenze der Engine": Ein Test hält den gemessenen Ist-Zustand fest, damit eine
  spätere Docling-Version es meldet, wenn sich das ändert. Das Ticket geht dann mit
  `done` und einem ausdrücklichen Befund an den PO, nicht mit einem Handoff.
- `pytest -q -rs` und `ruff check .` sauber, Sammelzahl und Abgewählte gemeldet.
