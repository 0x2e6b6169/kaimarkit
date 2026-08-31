---
id: 42
title: DOC-9 · grenzen.md nennt die alte OCR-Schreibweise deu,eng
status: todo
priority: medium
created: 2026-08-31T13:41:32.599836039+02:00
updated: 2026-08-31T13:41:32.599836039+02:00
assignee: akar
tags:
    - docs
    - bug
class: standard
---

## Ziel

`docs/grenzen.md` nennt `deu,eng` als geltende Einstellung fuer
`KAIMARKIT_OCR_LANGS`. Der Dienst erwartet seit BE-12 (#37) die zweibuchstabige
Form. Wer den Satz liest und den Wert uebernimmt, schaltet die Texterkennung ab.

## Eigene Dateien

- `docs/grenzen.md`

## Vorgaben

Zeile 58 lautet heute: „... steht auf `deu,eng`, ein franzoesisches Dokument
braucht dort seinen eigenen Eintrag." Richtig ist `de,en`.

**Nicht suchen und ersetzen.** Im Repo stehen ausserhalb von `kanban/` vier
Treffer auf `deu,eng`, und drei davon sind richtig, weil sie Tesseracts Form
ausdruecklich abgrenzen:

- `backend/app/config.py:35` — „Tesseracts ``deu,eng`` erkennt sie nicht"
- `docker/.env.example:68` — „nicht Tesseracts \"deu,eng\""
- `docs/betrieb/konfiguration.md:67` — „gehoert hier nicht hin"

Nur die Stelle in `grenzen.md` behauptet den Wert. Sie allein wird geaendert.

Belegt ist die Schreibweise in `backend/app/converters/docling.py` und
`backend/app/config.py` (Standard `ocr_langs = "de,en"`), Ankercommit 7079d3e.

## Pruefung

- `grep -n "deu,eng" docs/grenzen.md` findet nichts mehr
- die drei Abgrenzungen oben stehen unveraendert
- `mkdocs build --strict` laeuft sauber durch

## Herkunft

Nebenbefund aus DOC-6 (#34), gemeldet von akar. `grenzen.md` gehoerte DOC-2
(#21), das geschlossen ist — deshalb ein eigenes Ticket statt einer Ergaenzung.
