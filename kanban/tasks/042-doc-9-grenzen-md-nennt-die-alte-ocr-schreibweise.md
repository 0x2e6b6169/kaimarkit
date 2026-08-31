---
id: 42
title: DOC-9 · grenzen.md nennt die alte OCR-Schreibweise deu,eng
status: done
priority: medium
created: 2026-08-31T13:41:32.599836039+02:00
updated: 2026-08-31T13:44:46.083847846+02:00
started: 2026-08-31T13:44:29.104148502+02:00
completed: 2026-08-31T13:44:29.104148502+02:00
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


## Ergebnis (akar-17)

Geaendert wurde genau ein Satz in `docs/grenzen.md`, Zeile 58:

- vorher: „... `KAIMARKIT_OCR_LANGS` steht auf `deu,eng`, ein franzoesisches
  Dokument braucht dort seinen eigenen Eintrag."
- nachher: „... `KAIMARKIT_OCR_LANGS` steht auf `de,en`, ein franzoesisches
  Dokument braucht dort seinen eigenen Eintrag, `fr`."

Der Zusatz „`fr`" ist bewusst: Der Satz forderte einen eigenen Eintrag, ohne
dessen Form zu nennen — genau die Luecke, aus der `fra` entstanden waere. Er
steht in derselben eigenen Datei und in demselben Satz.

Anker im Code geprueft, nicht uebernommen:

- `backend/app/config.py:36` — `ocr_langs: str = "de,en"`, Kommentar Zeile 34
  nennt ISO 639-1 und EasyOCR
- `backend/app/converters/docling.py:76-78` — `EasyOcrOptions(lang=langs)`,
  Kommentar: „EasyOCR erwartet ISO 639-1"

Der uebrige Absatz haelt nach dem EasyOCR-Wechsel unveraendert: OCR nur ueber
Docling, `KAIMARKIT_OCR_ENABLED` als Standard, `ocr` je Anfrage, Laufzeitkosten,
`engine=auto` faellt auf die naechste Engine zurueck. Kein weiterer Satz falsch.

### Pruefung

`grep -n "deu,eng" docs/grenzen.md` — kein Treffer (exit 1).

`grep -rn "deu,eng"` ohne `kanban/`, `.git/`, `.worktrees/` — die drei
Abgrenzungen stehen unveraendert:

```
backend/app/config.py:35:    # Kuerzel. Tesseracts ``deu,eng`` erkennt sie nicht.
docs/betrieb/konfiguration.md:67:`deu,eng` gehoert hier nicht hin.
docker/.env.example:68:# zweibuchstabige Form: "de,en", nicht Tesseracts "deu,eng".
```

`mkdocs build --strict` (pyenv `claude-code`) — Exit 0, keine Warnung von
MkDocs selbst; die rote Meldung im Protokoll ist der Hinweis des
Material-Themes auf MkDocs 2.0, kein Buildfehler.

Branch `task/42-grenzen-ocr`, Commit `6a68761`, Merge `b65f059` (--no-ff).
Worktree entfernt, Branch geloescht. Keine Datei ausserhalb `docs/grenzen.md`
angefasst; `docker/Dockerfile` (IN-6, parallel) nicht beruehrt.
