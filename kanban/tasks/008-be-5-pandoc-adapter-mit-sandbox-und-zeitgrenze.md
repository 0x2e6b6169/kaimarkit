---
id: 8
title: BE-5 · Pandoc-Adapter mit --sandbox und Zeitgrenze
status: done
priority: medium
created: 2026-08-31T10:20:15.927246151+02:00
updated: 2026-08-31T11:12:59.010552283+02:00
started: 2026-08-31T11:12:31.850262139+02:00
completed: 2026-08-31T11:12:31.850262139+02:00
assignee: sophie
tags:
    - backend
depends_on:
    - 5
class: standard
---

## Ziel

Pandoc hinter dem Converter-Protokoll, sicher aufgerufen.

## Eigene Dateien

- `backend/app/converters/pandoc.py`

## Vorgaben

- `subprocess.run` mit Argumentliste, **niemals** `shell=True`.
- Feste Argumente: `--sandbox` (Pandoc greift auf keine Datei ausser der Eingabe zu),
  `--to=gfm-raw_html`, `--wrap=none`.
- Zeitgrenze aus `KAIMARKIT_PANDOC_TIMEOUT`; `TimeoutExpired` wird zu
  `ConversionTimeout`.
- Rueckgabewert ungleich null: die ersten Zeilen von stderr wandern in die Meldung
  von `EngineFailed`.
- `available()` prueft, ob die Binaerdatei im PATH liegt.
- **Kein PDF.** Die Endungsmenge enthaelt `.pdf` nicht - Pandoc kann PDF nicht lesen.

## Pruefung

Ein Skript konvertiert `tests/fixtures/sample.epub` und liefert Markdown.
Ein Aufruf mit `.pdf` wird von der Registry gar nicht erst an diesen Adapter
gereicht; ein direkter Aufruf wirft `UnsupportedFormat`.


## Ergebnis (sophie-07)

`backend/app/converters/pandoc.py` gebaut, gemergt als `merge: BE-5 pandoc adapter`.

- Aufruf ueber Argumentliste, nie `shell=True`. Feste Argumente in jedem Aufruf:
  `--sandbox`, `--to=gfm-raw_html`, `--wrap=none`.
- Zeitgrenze aus `KAIMARKIT_PANDOC_TIMEOUT` am Unterprozess selbst; `subprocess.run`
  toetet den Prozess, bevor `ConversionTimeout` den Adapter verlaesst.
- Rueckgabewert != 0: die ersten fuenf Zeilen von stderr stehen in `EngineFailed`.
  stderr bei Erfolg wird zu einer Warnung.
- `available()` prueft `shutil.which("pandoc")`. Zusaetzlich wirft schon
  `get_converter()` `EngineUnavailable`, wenn das Programm fehlt — sonst meldete
  `/api/capabilities` die Engine als `warming` statt `unavailable`, weil `meta.py`
  `available() is False` auf `warming` abbildet. Ein eigenes `state()` wie bei
  Docling ist damit unnoetig: `meta.py` ruft es ohnehin nicht.
- Kein `.pdf` in der Endungsmenge; ein direkter Aufruf wirft `UnsupportedFormat`.

**Pruefung bestanden.** `pandoc 3.1.3` liegt auf dieser Maschine unter `/usr/bin/pandoc`.
Ein ePub durch `registry.convert_with_fallback` liefert `engine: pandoc` und
`# Erstes Kapitel …`; der direkte PDF-Aufruf endet in `UnsupportedFormat`.
`pytest -q`: 58 passed, 2 skipped. `ruff check .`: sauber. Die Tests in
`backend/tests/test_pandoc.py` bauen ihr ePub selbst und ueberspringen sich sauber,
wenn `pandoc` fehlt (`skipif` statt Marke `slow` — die Marke ist in `pyproject.toml`
fuer die Docling-Modelle beschrieben, und der Pandoc-Test dauert Millisekunden).

**Fremde Datei angefasst — bitte lesen.** `backend/tests/test_registry.py` hat sich
darauf verlassen, dass es das Pandoc-Modul noch nicht gibt
(`test_engines_for_skips_unready_and_missing`, Kommentar „pandoc bleibt ungeladen"),
und wurde durch BE-5 rot. Eine dritte Attrappe `DummyEngine("pandoc", ready=False)`
im `install()`-Aufruf macht den Test wieder gruen und ausserdem unabhaengig davon, ob
`pandoc` auf der Maschine liegt. Das war die kleinstmoegliche Aenderung; ohne sie
waere `main` rot geblieben.

**Fuer BE-9:** gebraucht wird `backend/tests/fixtures/sample.epub` (ePub 3, ein
Kapitel mit `<h1>` und einem Absatz) — der Bauplan steht in `_write_epub` in
`backend/tests/test_pandoc.py` und laesst sich von dort uebernehmen. Ein zweites
Fixture fuer `.odt` oder `.rtf` waere fuer den Smoketest sinnvoll, weil Pandoc dort
die einzige Engine ist.

**Doku:** `docs/formate.md` um einen Abschnitt „Pandoc" ergaenzt (Sandbox, kein PDF,
Zeitgrenze), `docs/grenzen.md` um einen Satz: Pandoc ist die Ausnahme, dort beendet
die Zeitgrenze den Prozess wirklich. `KAIMARKIT_PANDOC_TIMEOUT` steht bereits in
`docker/.env.example`; `docs/betrieb/konfiguration.md` ist noch ein Rumpf und gehoert
DOC-3 (laeuft parallel) — die Variable muss dort noch beschrieben werden.
