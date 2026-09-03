---
id: 117
title: 'BE-38 · OCR bei Bildern in Dokumenten: erst messen, dann entscheiden (GitHub #2)'
status: done
priority: high
created: 2026-09-03T14:55:02.223095162+02:00
updated: 2026-09-03T15:10:41.650515463+02:00
started: 2026-09-03T15:10:35.151448473+02:00
completed: 2026-09-03T15:10:35.151448473+02:00
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


---

## Die Messung (sophie-40, im Abbild kaimarkit:local, docling 2.124.0)

Zwei neue Fixtures, beide gebaut aus `tests/fixtures/build_fixtures.py`: ein Dokument
mit Textebene, in dem ein Bild mit dem Satz „Dieser Satz steckt nur im Bild.“ steckt —
einmal als `bild_im_dokument.docx`, einmal als `bild_im_dokument.pdf`. Der Satz steht
nirgends in der Textebene. Wer ihn im Markdown findet, hat den Beleg, dass die
Texterkennung gelaufen ist.

| Datei | Engine | ocr | Satz aus dem Bild im Ergebnis? | Warnung |
|---|---|---|---|---|
| `bild_im_dokument.docx` | docling | true | **nein** | „Docling hat in bild_im_dokument.docx ein Bild durch einen Platzhalter ersetzt. Sein Inhalt fehlt im Markdown.“ |
| `bild_im_dokument.pdf` | docling | true | **ja** | keine |
| `bild_im_dokument.pdf` | docling | false | nein | keine |
| `bild_im_dokument.docx` | markitdown | — | nein | **keine** |
| `bild_im_dokument.pdf` | markitdown | — | nein | „MarkItDown übernimmt keine Bilder aus PDF. Enthielt bild_im_dokument.pdf Bilder, fehlt ihr Inhalt hier.“ |

Das Markdown im Einzelnen:

- docling/docx: `Kaimarkit Fixture` · `Ein Absatz aus dem Fixturebestand.` · `<!-- image -->`
- docling/pdf, ocr=true: `Kaimarkit Fixture` · `Ein Absatz aus dem Fixturebestand.` · `Dieser Satz steckt nur im Bild`
- docling/pdf, ocr=false: dieselben zwei Zeilen, die dritte fehlt
- markitdown/docx: `# Kaimarkit Fixture` · `Ein Absatz aus dem Fixturebestand.` · `![](data:image/png;base64...)`
- markitdown/pdf: dieselben zwei Zeilen

Die Zeile mit `ocr=false` ist die Gegenprobe: Im PDF kommt der Satz allein aus der
Texterkennung und nicht aus der Textebene.

## Die Entscheidung: Grenze der Engine, kein Fehler

Der Verdacht stimmt zur Hälfte. Bei **PDF** läuft die Texterkennung über eingebettete
Bilder und liefert den Satz; da ist nichts kaputt. Bei **docx** läuft sie nicht — und
Docling 2.124.0 führt keinen Schalter, der das änderte.

Der Beleg steht im Quelltext der installierten Fassung:

- `document_converter.py` gibt `InputFormat.DOCX` an `WordFormatOption` und damit an
  `pipeline_cls=SimplePipeline`; PDF geht an `StandardPdfPipeline`.
- `pipeline/simple_pipeline.py` enthält das Wort `ocr` nicht. Die Pipeline ruft nur
  `backend.convert()` des deklarativen Backends auf.
- `ocr_model` wird im ganzen Paket `docling/pipeline/` genau einmal gebaut, in
  `standard_pdf_pipeline.py:613`. Kein anderer Weg in die Texterkennung existiert.
- Was `SimplePipeline` an Anreicherung kennt, steht in `base_pipeline.py:212` —
  `DocumentPictureClassifier` und ein Bildbeschreibungsmodell (SmolVLM,
  „Describe this image in a few sentences“), dazu Diagrammauslesung. Das sind
  Bildbeschreibung und Klassifikation, nicht Texterkennung; ein Modell davon steckt
  auch nicht im Abbild.
- `SimplePipeline.get_default_options()` liefert `ConvertPipelineOptions`. Die Klasse
  führt `do_ocr` gar nicht; das Feld sitzt erst an `PdfPipelineOptions`. Ein
  `WordFormatOption(pipeline_options=…)` mit gesetztem `do_ocr` bliebe folgenlos.

Damit greift der zweite Ausgang aus dem Ticketrumpf: Bilder selbst aus einem
Word-Dokument zu schneiden und einzeln durch die Texterkennung zu schicken, wäre ein
Nachbau der Engine und ist ausdrücklich nicht Gegenstand. `docling.py` bleibt deshalb
unverändert.

Festgehalten ist der Ist-Zustand in zwei `slow`-Tests in `tests/test_docling_ocr.py`:
Der PDF-Test verlangt den Satz und hat eine Gegenprobe mit `ocr=False`, der docx-Test
verlangt sein Fehlen samt der Platzhalter-Warnung. Ändert eine spätere
Docling-Fassung das, fällt der docx-Test durch und meldet es.

## Befunde für den PO

1. **Die Doku braucht einen Satz dazu** (eigenes Ticket, `docs/formate.md` und
   `docs/grenzen.md`): Docling erkennt Text in Bildern nur dort, wo es die
   PDF-Pipeline fährt — also in PDF und in reinen Bilddateien. In docx, pptx, xlsx,
   html und epub liest es die Textebene und lässt Bilder als `<!-- image -->` stehen.
   Wer einen abfotografierten Absatz in Word einklebt, bekommt ihn nicht zurück. Der
   Umweg für den Nutzer: das Dokument als PDF abgeben.
2. **Die Warnung sagt nicht, was fehlt.** „Docling hat … ein Bild durch einen
   Platzhalter ersetzt“ nennt den Vorgang, nicht den Grund. Genau davor stand der
   Nutzer aus GitHub #2: Eine Warnung stand da, klüger ist er daraus nicht geworden.
   Ein Zusatz wie „In Word-Dokumenten liest Docling keine Bilder; als PDF abgegeben,
   erkennt es den Text darin.“ wäre eine Verhaltensänderung an `docling.py` und
   gehört in ein eigenes Ticket.
3. **MarkItDown warnt bei docx gar nicht.** Es setzt das Bild als
   `![](data:image/png;base64...)` ins Markdown — der Inhalt ist damit formal da,
   lesbar ist er nicht, und ein Kontextfenster füllt er ohne Nutzen. Für `engine=auto`
   ist markitdown bei `.docx` die erste Wahl (`registry.py`, `PREFERENCES`); der
   Regelfall für ein Word-Dokument liefert also den base64-Klotz und schweigt dazu.
   Eigenes Ticket, `markitdown.py` gehört nicht zu BE-38.
4. **Die Antwort an GitHub #2** kann jetzt konkret werden: PDF und Bilddateien
   erkennen Text, Word-Dokumente nicht.
