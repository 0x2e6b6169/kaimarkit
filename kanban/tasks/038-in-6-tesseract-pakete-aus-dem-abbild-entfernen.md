---
id: 38
title: IN-6 · tesseract-Pakete aus dem Abbild entfernen, EasyOCR-Gewichte sicherstellen
status: done
priority: medium
created: 2026-08-31T12:04:18.074654123+02:00
updated: 2026-08-31T13:55:09.293206714+02:00
started: 2026-08-31T12:04:52.815073313+02:00
completed: 2026-08-31T13:55:08.557050474+02:00
assignee: akar
tags:
    - infra
depends_on:
    - 37
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

## Ergebnis (akar-15)

Beide drei `tesseract-*`-Pakete sind aus der Laufzeitstufe raus. Vorher geprueft:
ausser dem Kommentar im Dockerfile ruft nichts im Abbild `tesseract` auf — weder
der Code (`grep -ri tesseract backend/` findet nur den Kommentar in `config.py`)
noch die Abhaengigkeiten (`docling[easyocr]`, kein `pytesseract`).

**Der Ausbau allein waere ein Rueckschritt gewesen.** Der Nachweis am unveraenderten
Abbild (`kaimarkit:in6-before`, aus dem heutigen `main`) scheiterte:

    HTTP 500 — "Docling ist an scanned.pdf gescheitert: Missing
    /opt/docling-models/EasyOcr/craft_mlt_25k.pth and downloads disabled"

`docling-tools models download` ohne Argumente holt seinen vorgegebenen Satz, und
darin steckt EasyOCR seit docling 2.56 nicht mehr — nur RapidOcr, Layout,
TableFormer, CodeFormula und der Bildklassifikator. Der Warmlauf meldete trotzdem
`ready`, weil Docling die Gewichte erst bei der ersten Wandlung anfasst. Die
Vorback-Stufe holt EasyOCR jetzt ausdruecklich nach:

    RUN docling-tools models download --output-dir /opt/docling-models \
        && docling-tools models download --output-dir /opt/docling-models easyocr \
            --easyocr-lang de --easyocr-lang en

Die Sprachen entsprechen der Voreinstellung von `KAIMARKIT_OCR_LANGS` (`de,en`).
Wer eine andere Sprache einstellt, braucht beim ersten Lauf Netz — oder das Ticket,
das die Sprachliste zur Bauzeit aus einem ARG zieht.

### Nachweis, positiv

Scan-PDF ohne Textebene (PIL, Text als Bild, 200 dpi), im Container abgelegt,
Container mit `--network none` gestartet, `HF_HUB_OFFLINE=1` aus dem Abbild.

- `GET /api/capabilities` → `engines.docling` von `warming` auf `ready`, keine
  Haengepartie.
- `POST /api/convert`, `engine=docling`, `ocr=true` → HTTP 200, `engine: docling`,
  `duration_ms: 26124`, und im Markdown steht tatsaechlich:

      KAIMARKIT OFFLINE OCR Beweis fuer die Texterkennung ohne Netzzugriff im Container

  Alle sieben erwarteten Woerter gefunden — kein leeres Ergebnis, kein stiller
  Rueckfall.
- Im Abbild: `command -v tesseract` leer, `dpkg -l | grep -c tesseract` = 0,
  `/opt/docling-models/EasyOcr` mit `craft_mlt_25k.pth` (83 MB), `latin_g2.pth`
  und `english_g2.pth`, zusammen 109 MB.

### Groesse: das Abbild waechst, statt zu schrumpfen

| | vorher | nachher |
|---|---|---|
| apt-Schicht (Laufzeit) | 459 MB | 370 MB |
| Modellschicht | 1,44 GB | 1,55 GB |
| **Abbild gesamt** | **4.077.054.323 B** | **4.101.376.619 B** |

Die drei Pakete bringen 89 MB, die fehlenden EasyOCR-Gewichte 109 MB. Unterm
Strich +24 MB (+0,6 %). Die Pruefung erwartete ein kleineres Abbild; das war unter
der Annahme geschrieben, die Gewichte laegen schon drin. Zwischen 24 MB und einem
funktionierenden Offlinebetrieb ist die Wahl eindeutig.

### Fuer den PO, nicht in diesem Ticket

Der vorgegebene Modellsatz enthaelt **RapidOcr** — die einzige OCR-Maschine, die
ohne Zusatzschritt im Abbild liegt. Wer die 109 MB sparen will, muesste BE-12
umdrehen und RapidOcr statt EasyOCR waehlen. Das ist eine Produktentscheidung,
keine Infrastrukturfrage.

Anker: `f79fa90` (Commit), `87ed9d9` (Merge nach main).
