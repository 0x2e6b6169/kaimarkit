---
id: 95
title: 'ORG-1 · MIT-Lizenz: LICENSE, Paketangaben, README'
status: todo
priority: high
created: 2026-09-02T16:29:00.805615873+02:00
updated: 2026-09-02T16:29:00.805615873+02:00
assignee: akar
class: standard
---

## Ziel

Das Repository ist öffentlich. Ohne Lizenz darf niemand es benutzen, ändern oder
weitergeben — das voreingestellte Urheberrecht verbietet alles, was nicht
ausdrücklich erlaubt ist. Eine MIT-Lizenz erlaubt es.

## Eigene Dateien

- `LICENSE` — neu, Wurzel des Repositorys
- `README.md` — ein neuer Abschnitt am Ende
- `backend/pyproject.toml`
- `frontend/package.json`
- `docs/entwicklung.md` — ein Satz, siehe unten

`pyproject.toml` gehört laut CLAUDE.md allein `BE-1`. `BE-1` ist abgeschlossen und
kein offenes Ticket beansprucht die Datei; das Eigentum ist frei. Nach diesem
Ticket fällt es an `BE-1` zurück.

## Vorgaben

**Der Wortlaut ist der unveränderte MIT-Text**, wie ihn die OSI führt. Kein Satz
umformuliert, keine Zusatzbedingung, keine Übersetzung. Die Copyright-Zeile lautet
genau:

    Copyright (c) 2026 kaimarkit contributors

So vom Nutzer entschieden am 2026-09-02: kein Personenname, damit spätere
Beitragende ohne Änderung der Datei mitgemeint sind.

**`backend/pyproject.toml`:** `license = "MIT"` als SPDX-Ausdruck in `[project]`.
Das Backend ist `hatchling`; ob die vorhandene Fassung den Zeichenketten-Ausdruck
nach PEP 639 annimmt oder noch die Tabellenform erwartet, ist nicht geprüft. Wenn
der Bau ihn ablehnt, statt dessen den Klassifizierer
`License :: OSI Approved :: MIT License` setzen — und in der Ticketnotiz
festhalten, welche der beiden Formen es geworden ist und woran die andere
scheiterte. `license-files` bleibt weg: `LICENSE` liegt oberhalb von `backend/`
und ist von dort aus nicht erreichbar.

**`frontend/package.json`:** `"license": "MIT"` neben `"version"`.

**`README.md`:** ein Abschnitt `## Lizenz` am Ende, zwei Sätze. Er nennt MIT und
verweist auf `LICENSE`. Die vorhandenen Abschnitte bleiben unangetastet.

**`docs/entwicklung.md`:** ein Satz an passender Stelle, dass der Quelltext unter
MIT steht, mit Verweis auf die Datei im Repository. Kein eigener Abschnitt, kein
Eintrag in `mkdocs.yml`.

**Was dieses Ticket nicht tut.** Die Lizenzen der mitgelieferten Fremdbestandteile
— docling, markitdown, pandoc, Torch und die vorgebackenen Modelle im Abbild —
bleiben unberührt. Ob das Abbild eine NOTICE-Datei braucht, ist eine eigene Frage
und gehört nicht hierher. Wer beim Arbeiten darauf stößt, meldet es, statt es
mitzuerledigen.

## Prüfung

1. `LICENSE` beginnt mit `MIT License` und enthält die Copyright-Zeile wörtlich
   wie oben. Die Klausel `THE SOFTWARE IS PROVIDED "AS IS"` steht darin.
2. Vor der Arbeit: `test -f LICENSE` schlägt fehl. Einmal belegen — die Datei gibt
   es heute nicht.
3. `cd backend && python -m build --wheel` (oder `pip wheel . --no-deps`) läuft
   durch, und die erzeugte `METADATA` nennt MIT. Das ist die Prüfung, die zwischen
   den beiden Formen oben entscheidet.
4. `cd frontend && npm run build` läuft durch. `node -e "console.log(require('./package.json').license)"` gibt `MIT`.
5. `mkdocs build --strict` ohne Warnung.
6. `pytest -q -rs` im Backend unverändert grün — Sammelzahl mitnennen.
