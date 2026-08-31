---
id: 37
title: 'BE-12 · OCR-Maschine ausdruecklich setzen: EasyOCR mit de,en'
status: done
priority: high
created: 2026-08-31T12:03:54.39201469+02:00
updated: 2026-08-31T14:03:42.654950744+02:00
started: 2026-08-31T12:04:51.169484447+02:00
completed: 2026-08-31T12:15:24.848130815+02:00
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


## Ergebnis (sophie-11, Branch task/37-easyocr-explizit, merge 1266f4a)

Der Adapter setzt `options.ocr_options = EasyOcrOptions(lang=langs)` — kein
nachtraegliches `lang` mehr auf dem Vorgabeobjekt. `config.py` steht auf
`ocr_langs = "de,en"` (ISO 639-1). Suite auf `main`: 107 passed / 3 deselected,
`ruff check .` sauber.

### Untergrenze fuer docling: `docling[easyocr]>=2.56.0`, mit Beleg

Belegt aus den Paketmetadaten und den Radern von PyPI, nicht geraten:

- `EasyOcrOptions` mit dem Feld `lang: List[str]` steht seit **2.0.0** in
  `docling/datamodel/pipeline_options.py` (aus dem Rad 2.0.0 gelesen). Die Klasse
  allein rechtfertigt also keine neue Untergrenze.
- Die Untergrenze kommt vom Paketschnitt: Ab **2.56.0** ist `easyocr` ein Extra.
  Vorher stand `easyocr>=1.7,<2.0` als feste Abhaengigkeit in den Metadaten
  (nachgelesen in `docling-2.0.0.dist-info/METADATA`), ab 2.56.0 steht dort
  `Provides-Extra: easyocr`. Ermittelt per binaerer Suche ueber die
  PEP-658-Metadaten aller 164 Fassungen der Reihe 2.x: 2.55.1 ohne Extra,
  2.56.0 mit. Ein blosses `docling>=…` liefert die Maschine seit 2.56.0 also
  nicht mehr mit — deshalb `docling[easyocr]`.
- Gegenprobe oben: In der neuesten Fassung **2.123.1** existiert
  `EasyOcrOptions` unveraendert (mit `lang`, ISO 639-1 in der Feldbeschreibung).
  Das Rad `docling` ist dort nur noch eine Huelle um `docling-slim[standard]`;
  der Quelltext steckt in `docling-slim`, gelesen aus dessen Rad.
- Ebenfalls in 2.123.1 gegengeprueft und damit der Befund des Tickets bestaetigt:
  `PdfPipelineOptions.ocr_options` steht auf `OcrAutoOptions()`, dessen `lang`
  ausdruecklich leer bleibt ("The `lang` field is intentionally defaulted to an
  empty list. To control language selection, specify an explicit OCR engine
  option class instead.").

### Rot vor Gruen

`backend/tests/test_docling_ocr.py` haengt Attrappen der Docling-Module in
`sys.modules` und ruft `_build_pipeline(True)` auf. Beide Tests liefen gegen den
unveraenderten Stand und waren rot:
`assert isinstance(FakeOcrAutoOptions(lang=['de','en']), FakeEasyOcrOptions)` —
die Sprachen landeten auf dem Vorgabeobjekt, die Maschine wurde nie gewaehlt.
Nach der Aenderung gruen.

### Was ungeprueft blieb

Docling ist in der Umgebung `claude-code` nicht installiert und wurde bewusst
nicht nachinstalliert (Torch samt Modellen in einer geteilten Umgebung). Der Test
prueft deshalb nur, welche Options-Klasse der Adapter baut und welche Sprachen er
hineinreicht — nicht, ob EasyOCR mit `de,en` tatsaechlich erkennt und ob die
Gewichte im Abbild liegen. Das entscheidet sich in INT-2 (#30) im Container.

### Nachzuziehen in anderen Lanes

- **DOC-6 (#34):** `docker/.env.example:65` und `docs/betrieb/konfiguration.md:50`
  fuehren beide `deu,eng`. Richtig ist jetzt `de,en` (ISO 639-1, EasyOCR).
- **DOC-2 (#21)** besitzt zwei weitere Seiten, die dadurch falsch werden — von
  sophie-11 nicht angefasst, weil sie einem offenen Ticket gehoeren:
  `docs/grenzen.md:57-58` ("`KAIMARKIT_OCR_LANGS` steht auf `deu,eng`") und
  `docs/formate.md:63` (Kuerzel muessen zur Maschine passen — die Maschine steht
  jetzt fest und heisst EasyOCR).
- **IN-6 (#38):** neben den drei toten `tesseract-*`-Paketen ist im Dockerfile zu
  pruefen, dass `pip install /src/backend` das Extra `easyocr` mitnimmt (es steht
  jetzt in `pyproject.toml`) und dass `docling-tools models download` die
  EasyOCR-Gewichte fuer `de` und `en` mitbringt.
- Der Schnittstellen-Dreiklang ist nicht beruehrt.

[[2026-08-31]] Mon 14:03
Nachtrag zur Entscheidung, nach IN-6 (#38, merge 87ed9d9). Die Annahme, die Gewichte laegen schon im Modellsatz, war falsch: `docling-tools models download` liefert EasyOCR seit docling 2.56 nicht mehr mit, das Abbild konnte offline gar kein OCR (500, fehlende craft_mlt_25k.pth). IN-6 holt sie jetzt ausdruecklich. Damit waechst das Abbild netto um 24 MB, statt zu schrumpfen: apt -89 MB, Modellstufe +109 MB. Dem Nutzer am 31.08.2026 erneut vorgelegt, weil sich die Ausgangslage geaendert hatte. **Entscheidung: es bleibt bei EasyOCR.** Die Begruendung stand nie auf der Bildgroesse, sondern auf der Erkennungsqualitaet, und 109 MB sind 2,7 Prozent eines 4,1-GB-Abbilds. RapidOcr laege als einzige Maschine ohne Zusatzschritt im Standardsatz — festgehalten, falls die Bildgroesse spaeter einmal zaehlt. Gemeldet von akar.
