---
id: 26
title: IN-5 · Makefile mit allen Zielen einschliesslich docs-serve und docs-release
status: todo
priority: medium
created: 2026-08-31T10:21:41.179562066+02:00
updated: 2026-08-31T10:30:46.28355638+02:00
assignee: akar
tags:
    - infra
depends_on:
    - 22
    - 20
class: standard
---

## Ziel

Die Aufrufe an einer Stelle, damit sich niemand Dateiketten merken muss.

## Eigene Dateien

- `Makefile`

## Vorgaben

- Eine Variable `COMPOSE` haelt die Dateikette, die Ziele bauen darauf auf:
  `up`, `up-traefik`, `up-authelia`, `down`, `logs`, `build`.
- Entwicklung: `dev` (Backend und Frontend), `test`, `lint`.
- Dokumentation: `docs-serve` (mkdocs serve auf Port 8001),
  `docs-release VERSION=x.y` -> `mike deploy --update-aliases x.y latest` gefolgt
  von `mike set-default latest`.
- Alle Aufrufe funktionieren aus dem Wurzelverzeichnis.
- `make help` als Standardziel listet die Ziele mit je einer Zeile Erklaerung.
- Python-Ziele setzen die pyenv-Umgebung `claude-code` voraus und sagen es, wenn
  sie fehlt.

## Pruefung

`make help` listet jedes Ziel. `make up` startet den Dienst, `make down` beendet
ihn. `make docs-serve` zeigt die Dokumentation auf 8001.
