---
id: 123
title: DOC-18 · OCR greift in PDF und Bilddateien, sonst nirgends
status: todo
priority: high
created: 2026-09-03T15:13:04.835081493+02:00
updated: 2026-09-03T15:13:04.835081493+02:00
assignee: akar
tags:
    - docs
    - gh-2
class: standard
---

## Ziel

Die Messung aus BE-38 (#117) ist da, und sie beantwortet GitHub-Issue #2. Das Ergebnis
gehört in die Dokumentation, weil es eine **Grenze der Engine** ist und nicht behoben
wird: Bilder aus einem Dokument zu schneiden und einzeln durch OCR zu schicken wäre ein
eigenes Vorhaben, und niemand hat es beschlossen.

Gemessen im Abbild, docling 2.124.0:

- **PDF mit eingebettetem Bild, Docling, `ocr=true`: der Satz kommt.** Gegenprobe mit
  `ocr=false`: er fehlt. In PDF greift OCR also auch auf eingebettete Bilder.
- **docx: nicht.** DOCX geht bei Docling an die `SimplePipeline`, und deren Optionen
  (`ConvertPipelineOptions`) führen `do_ocr` überhaupt nicht; das OCR-Modell wird im
  ganzen `docling/pipeline/` nur in `standard_pdf_pipeline.py` gebaut. Es gibt keinen
  Schalter, den man anschalten könnte.

Für den Nutzer heißt das: OCR greift bei **Bilddateien** und bei **PDF**, sonst nirgends
— nicht in docx, pptx, xlsx, html, epub. Der Umweg ist, das Dokument als PDF abzugeben.

## Eigene Dateien

- `docs/formate.md`
- `docs/grenzen.md`

Beide waren in BE-38 ausdrücklich ausgeschlossen und sind seit DOC-17 (#118) frei. Kein
anderes offenes Ticket führt sie.

## Vorgaben

- Die Aussage steht dort, wo jemand nach OCR sucht, nicht in einer Fußnote. Wer wissen
  will, ob sein Word-Dokument mit dem abfotografierten Absatz durchgeht, soll es finden.
- Der Umweg gehört dazu und in denselben Absatz: als PDF abgeben.
- Die Zahlen und die Herkunft mitschreiben: gemessen am Abbild, docling 2.124.0. Eine
  spätere Docling-Version kann das ändern; ein Satz ohne Version wäre in einem Jahr eine
  Behauptung ohne Deckung.
- Keine Aussage darüber, was MarkItDown bei docx tut — das ändert sich gerade in BE-40 (#122) und wäre morgen falsch. Der Verweis auf die Engine-Grenze reicht.

## Prüfung

- Rot vor grün, ohne Test: Vor der Arbeit einmal belegen, dass beide Dateien zu OCR in
  Dokumenten nichts sagen (Suchbegriff und Fundstellenzahl in die Notiz), danach, dass
  sie es sagen.
- `mkdocs build --strict` ohne Warnung.
- Ein Leser, der nur `docs/formate.md` öffnet, erfährt die Grenze, ohne `grenzen.md`
  aufschlagen zu müssen — und umgekehrt genügt ein Verweis, keine Verdopplung.
