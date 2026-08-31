---
id: 34
title: DOC-6 · OCR-Sprachen und DOCLING_ARTIFACTS_PATH in .env.example und Konfigurationsseite
status: todo
priority: medium
created: 2026-08-31T11:45:54.471902201+02:00
updated: 2026-08-31T12:05:26.115243161+02:00
started: 2026-08-31T11:46:25.433276163+02:00
assignee: akar
tags:
    - docs
    - bug
depends_on:
    - 37
blocked: true
block_reason: 'Wartet auf BE-12 (#37): der Adapter setzt EasyOCR ausdruecklich, erst danach steht die Schreibweise (ISO 639-1, de/en) fest. Vorher waere jeder Wert in .env.example fiktiv.'
class: standard
---

## Ziel

Zwei Luecken in der Betriebsdokumentation von Docling, beide gemeldet von sophie.

1. `docker/.env.example` setzt `KAIMARKIT_OCR_LANGS=deu,eng`. Das ist die
   Schreibweise von Tesseract. Doclings Voreinstellung ist EasyOCR, und die
   erwartet `de,en`. Wer die Beispieldatei uebernimmt und OCR einschaltet,
   bekommt keine Fehlermeldung, sondern schlechtere Erkennung.
2. `DOCLING_ARTIFACTS_PATH` fehlt in `docs/betrieb/konfiguration.md`. Die
   Variable steht im Dockerfile (IN-1, #23) und der Adapter liest sie (BE-4,
   #7) — beschrieben ist sie nirgends. Ohne sie laedt Docling zur Laufzeit
   Modelle nach, was mit `HF_HUB_OFFLINE=1` fehlschlaegt.

## Eigene Dateien

- `docker/.env.example`
- `docs/betrieb/konfiguration.md`

Beide gehoeren zusammen — Konvention 6 sagt, dass sie gemeinsam geaendert
werden. Genau deshalb ist das ein Ticket und nicht zwei.

## Vorgaben

- Klaeren, welche OCR-Maschine der Docling-Adapter tatsaechlich benutzt, und die
  Beispielwerte danach richten. Wenn beide Schreibweisen vorkommen koennen,
  gehoert das in die Dokumentation, nicht in einen stillen Standardwert.
- `DOCLING_ARTIFACTS_PATH` in `docs/betrieb/konfiguration.md` aufnehmen: was sie
  bedeutet, welchen Wert das Image setzt, und was ohne sie passiert.
- Beim Durchsehen pruefen, ob weitere `KAIMARKIT_*`- oder Docling-Variablen in
  einer der beiden Dateien fehlen. Dieselbe Luecke steht selten allein.

## Pruefung

Jede Variable aus `docker/.env.example` kommt in `docs/betrieb/konfiguration.md`
vor und umgekehrt — einmal gegeneinander abgeglichen, das Ergebnis in der
Ticketnotiz. Die OCR-Sprachen im Beispiel passen zu der Maschine, die der
Adapter aufruft, mit Nachweis aus dem Code.

Erfasst via /findings (Test-Pass 2026-08-31)

[[2026-08-31]] Mon 11:57
**Teilweise geliefert, OCR-Haelfte an die Backend-Lane uebergeben (akar-11).**

Befundstand: main-Commit `ebb783c` (Worktree-HEAD), `docling>=2.0` aus
`backend/pyproject.toml:19` — PyPI liefert derzeit 2.123.1.

## Geliefert (Merge 187705a, Branch task/34-ocr-doku)

- `docs/betrieb/konfiguration.md`: neuer Abschnitt „Was das Abbild fest setzt"
  mit `DOCLING_ARTIFACTS_PATH=/opt/docling-models`, `HF_HOME=/opt/docling-models`
  und `HF_HUB_OFFLINE=1`. Werte abgelesen aus `docker/Dockerfile:113-115`, nicht
  geraten. Dazu, was ohne den Pfad passiert: Docling laedt nach, `HF_HUB_OFFLINE=1`
  verbietet das, die Engine meldet sich als nicht verfuegbar, `engine=auto` nimmt
  die naechste (belegt in `backend/app/converters/registry.py:131-173`).
- `docker/.env.example`: Hinweiskommentar auf dieselben drei Variablen. Sie sind
  keine Compose-Variablen — `docker/docker-compose.yml` reicht sie nicht durch.
  Beide Dateien im selben Commit, Konvention 6.
- Der Gleichlauf-Satz auf der Seite nimmt den neuen Abschnitt ausdruecklich aus.

## Pruefung Teil 1 — bestanden

Mechanischer Abgleich (`grep` + `comm`, nicht nach Augenmass):
**32 Variablen** in `docker/.env.example`, **32** auf der Konfigurationsseite
ausserhalb des Abbild-Abschnitts, beide Differenzmengen leer. Zusaetzlich alle
`${...}` aus `docker/docker-compose*.yml` gegen `.env.example` geprueft: 32 zu 32,
Differenz in beiden Richtungen leer. Keine weitere Luecke gefunden.

## Pruefung Teil 2 — nicht bestanden, und nicht durch Doku zu beheben

Die Ticketpraemisse stimmt nicht mehr. Der Adapter waehlt gar keine OCR-Maschine:

- `backend/app/converters/docling.py:64` — `options = PdfPipelineOptions()`,
  `ocr_options` wird nirgends gesetzt.
- `backend/app/converters/docling.py:73-76` — `options.ocr_options.lang = langs`.

In docling 2.123.1 ist die Vorgabe `PdfPipelineOptions.ocr_options = OcrAutoOptions()`
(`docling/datamodel/pipeline_options.py:2006`). `OcrAutoOptions.lang` ist absichtlich
leer, und die Klasse sagt selbst (ebd. 264-287): „Language settings are deferred to
the chosen engine's defaults." `OcrAutoModel`
(`docling/models/stages/ocr/auto_ocr_model.py:30-141`) probiert unter Linux der Reihe
nach nemotron, rapidocr/onnxruntime, easyocr, rapidocr/torch und baut die gewaehlte
Engine mit einem **frischen** Options-Objekt, aus dem nur `mode` uebernommen wird.
Tesseract steht in dieser Liste nicht.

Zwei Folgen:

1. `KAIMARKIT_OCR_LANGS` wirkt zurzeit ueberhaupt nicht — gleich, ob `deu,eng` oder
   `de,en` darin steht. Deshalb wurde der Wert **nicht** geaendert: jede Schreibweise
   waere gleich fiktiv. `de,en` einzutragen haette den Fehler nur verschoben.
2. `tesseract-ocr`, `tesseract-ocr-deu` und `tesseract-ocr-eng` im Laufzeit-Abbild
   (`docker/Dockerfile:129-131`) werden auf diesem Weg nie benutzt.

## Fuer die Backend-Lane (BE-11 / #33) — ohne Rueckfrage uebernehmbar

- **Datei/Zeilen:** `backend/app/converters/docling.py:62-76`.
- **Beobachtet:** `PdfPipelineOptions()` liefert `OcrAutoOptions`; das dort gesetzte
  `lang` verwirft die automatische Auswahl. `KAIMARKIT_OCR_LANGS` bleibt wirkungslos.
- **Erwartet:** Der Adapter setzt die Engine ausdruecklich, etwa
  `options.ocr_options = EasyOcrOptions(lang=langs)` (Kuerzel dann ISO 639-1:
  `de`, `en`) oder `TesseractOcrOptions(lang=langs)` (ISO 639-2: `deu`, `eng` —
  passt zu den Paketen, die schon im Abbild liegen). Erst danach steht fest, welche
  Schreibweise gilt.
- **Nebenbefund:** `backend/app/config.py:34` haelt denselben Standard
  `ocr_langs = "deu,eng"` und muss zur gewaehlten Engine passen.
- **Nebenbefund:** `docling>=2.0` in `backend/pyproject.toml:19` ist offen nach oben.
  Welche Vorgabe gilt, haengt am Buildzeitpunkt; eine Untergrenze waere sinnvoll.

## Rest dieses Tickets

Sobald die Engine feststeht: Schreibweise der Sprachkuerzel in
`docs/betrieb/konfiguration.md` (Zeile `KAIMARKIT_OCR_LANGS`) und den Wert in
`docker/.env.example` nachziehen. Beides gehoert weiter dieser Doku-Lane.

## Nachtrag (PO, 2026-08-31)

akar-11 hat die Doku-Haelfte geliefert und gemergt (`187705a`), den Wert von
`KAIMARKIT_OCR_LANGS` aber bewusst nicht angefasst — zu Recht: solange der
Adapter gar keine Maschine setzt, waere jede Schreibweise gleich fiktiv.

Die Entscheidung steht jetzt: **EasyOCR mit ISO 639-1**, umgesetzt in BE-12
(#37). Dieses Ticket haengt daran und zieht danach nach:

- `docker/.env.example`: `KAIMARKIT_OCR_LANGS=de,en`.
- `docs/betrieb/konfiguration.md`: die Schreibweise als ISO 639-1 benennen und
  sagen, welche Maschine sie liest.
- **`docs/betrieb/konfiguration.md:83`** sagt weiterhin, Docling lade die Modelle
  „beim ersten Aufruf". Seit BE-11 (#33) ist das der Warmlauf beim Start, nicht
  die erste Nutzeranfrage. Gefunden von akar-12 beim wiederholten Grep in DOC-7
  (#36) und dort liegen gelassen, weil die Datei diesem Ticket gehoert. Kein
  eigenes Ticket — zwei Tickets auf derselben Datei waeren der Schnittfehler aus
  PROC-1 (#35).
