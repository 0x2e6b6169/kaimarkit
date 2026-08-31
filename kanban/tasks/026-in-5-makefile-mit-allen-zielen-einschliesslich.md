---
id: 26
title: IN-5 · Makefile mit allen Zielen einschliesslich docs-serve und docs-release
status: done
priority: medium
created: 2026-08-31T10:21:41.179562066+02:00
updated: 2026-08-31T10:59:03.63292938+02:00
started: 2026-08-31T10:59:02.922125778+02:00
completed: 2026-08-31T10:59:02.922125778+02:00
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


## Ergebnis (akar-04)

Makefile in der Wurzel. `COMPOSE` haelt die Dateikette; `up-traefik` und
`up-authelia` haengen die Ergaenzungsdateien an. Authelia setzt Traefik voraus,
weil die ForwardAuth-Middleware am Traefik-Router haengt.

Ziele: `help` (Standardziel, aus den Zielkommentaren erzeugt und deshalb immer
vollstaendig), `up`, `up-traefik`, `up-authelia`, `down`, `logs`, `build`,
`dev`, `test`, `test-slow`, `lint`, `docs-serve`, `docs-release VERSION=x.y`.

Die Python-Ziele rufen die Programme direkt aus
`$PYENV_ROOT/versions/claude-code/bin` auf — kein globales Python, kein
aktiviertes Shell-Profil noetig. Fehlt die Umgebung, bricht `check-venv` mit
einem Hinweis ab; fehlt `docker/.env`, bricht `check-env` ab, denn sonst setzt
Compose still leere Werte ein.

**Pruefung bestanden.** `make help` listet jedes Ziel mit einer Zeile Erklaerung.
`make up` hat gebaut, gestartet und `/api/health` beantwortet, `make logs` las
mit, `make down` hat Container und Netz wieder entfernt. Da `docker/Dockerfile`
aus IN-1 noch fehlt, lief der Rauchtest gegen eine wegwerfbare
`docker/Dockerfile.smoke` mit eigenem Projekt- und Containernamen auf Port 18099;
Datei, `.env` und Abbild sind geloescht, committet wurde allein das `Makefile`.
`make docs-serve` lieferte 200 auf `127.0.0.1:8001/docs/` — mkdocs leitet `/`
dorthin um, weil `site_url` auf `/docs/` endet. `make lint` laeuft sauber durch.

Keine neuen `KAIMARKIT_*`-Variablen, DOC-3 muss nichts nachziehen.

Zwei Randnotizen fuer andere Lanes: `make test` endet derzeit mit pytest-Code 5,
weil BE-9 die Tests noch nicht geliefert hat. `make dev` braucht die
`frontend/package.json` aus FE-1.
