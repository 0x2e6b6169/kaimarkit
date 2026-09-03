---
id: 123
title: DOC-18 · OCR greift in PDF und Bilddateien, sonst nirgends
status: done
priority: high
created: 2026-09-03T15:13:04.835081493+02:00
updated: 2026-09-03T15:18:58.372440447+02:00
started: 2026-09-03T15:18:57.412656736+02:00
completed: 2026-09-03T15:18:57.412656736+02:00
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

[[2026-09-03]] Thu 15:18
## Ergebnis (akar-41)

Rot vor gruen, zeilenumbruchtolerant: Die Aussage laeuft im Fliesstext ueber zwei Zeilen, zeilenweises grep haette auch nachher 0 gemeldet. Suchbegriff deshalb ueber den geflachten Text (tr '\n' ' '): (OCR|Texterkennung)[^.]{0,300}(docx|pptx|xlsx|epub|Word) und die Umkehrung. Vorher (git show HEAD): docs/formate.md 0, docs/grenzen.md 0. Nachher: docs/formate.md 1, docs/grenzen.md 1. Zusatzbelege vorher: 'als PDF' 0 Fundstellen in beiden Dateien, '2.124' 0 Fundstellen in ganz docs/ — nachher 2 Fundstellen fuer 2.124.0. Die allgemeinen OCR-Treffer (formate.md 8, grenzen.md 5) standen schon vorher da und sagten nichts ueber die Reichweite.

Ausfuehrliche Fassung: docs/grenzen.md, neuer Abschnitt 'OCR greift nur in PDF und Bilddateien', zwischen 'Gescannte Seiten ohne OCR bleiben leer' und 'Bilder werden nicht beschrieben'. Begruendung: Die Seite hat genau diesen Gegenstand — was der Dienst nicht kann und warum es dabei bleibt; eine Reichweitengrenze ohne Schalter ist eine Grenze, keine Formatangabe. Der Abschnitt nennt die Reichweite (PDF und .png/.jpg/.jpeg/.tiff), die ausgeschlossenen Formate, den Grund (Docling baut das OCR-Modell nur in der PDF-Pipeline; die einfache Pipeline kennt do_ocr nicht — es gibt keinen Schalter, weder ocr noch KAIMARKIT_OCR_ENABLED wirkt), die Gegenprobe in eingebetteten PDF-Bildern (ocr=true bringt den Absatz, ocr=false nicht), die Herkunft (gemessen im Container-Abbild, docling 2.124.0, spaetere Version kann das aendern) und den Umweg: als PDF speichern und mit engine=docling und ocr=true abgeben.

docs/formate.md bekommt im vorhandenen Abschnitt 'Docling: Modelle und OCR' einen eigenen Absatz mit Reichweite, ausgeschlossenen Formaten, der Unwirksamkeit beider Schalter, der Version und dem Umweg, dazu einen Verweis auf grenzen.md#ocr-greift-nur-in-pdf-und-bilddateien fuer die Einzelheiten. Wer nur formate.md oeffnet, erfaehrt Grenze und Umweg vollstaendig; der Grund und die Messung stehen nur einmal.

Keine Aussage ueber MarkItDown bei docx (BE-40, #122) hinzugefuegt; die vorhandene MarkItDown-Passage in formate.md blieb unberuehrt.

Pruefung: mkdocs build --strict, exit 0, 0 Zeilen WARNING oder ERROR. Die rote Meldung des Material-Themes zu MkDocs 2.0 ist ein Herstellerhinweis, keine Build-Warnung.

Commit 7408890, Merge-Commit 2e923f5 (--no-ff, unter flock).
