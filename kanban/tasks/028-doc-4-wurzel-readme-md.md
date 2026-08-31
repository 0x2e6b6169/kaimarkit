---
id: 28
title: DOC-4 · Wurzel-README.md
status: done
priority: low
created: 2026-08-31T10:21:42.814918987+02:00
updated: 2026-08-31T11:32:13.101098867+02:00
started: 2026-08-31T11:32:01.138537865+02:00
completed: 2026-08-31T11:32:01.138537865+02:00
assignee: akar
tags:
    - docs
depends_on:
    - 21
class: standard
---

## Ziel

Die Einstiegsseite im Repo. Kurz.

## Eigene Dateien

- `README.md`

## Vorgaben

- Was das Werkzeug tut, in drei Saetzen.
- Der kuerzeste Startbefehl.
- Verweis auf `/docs` fuer alles Weitere.
- **Keine Betriebsanleitung hier.** Die steht in `docs/betrieb/`, und zwei Quellen
  fuer dieselbe Sache pflegt niemand.

## Pruefung

Wer die Datei liest, weiss nach einer Minute, was das Werkzeug tut und wie er es
startet.


## Ergebnis (akar-09)

`README.md` in der Wurzel angelegt, 46 Zeilen. Aufbau: was das Werkzeug tut (drei
Saetze), die drei Engines in zwei Saetzen, ein Startblock (`cp docker/.env.example
docker/.env`, `make up`, ein curl-Aufruf), ein ehrlicher Hinweis auf den
Geruestzustand der Oberflaeche (INT-1 offen), und die Verweisliste in `docs/`.
Keine Betriebsanleitung, keine Variablentabelle — Konvention 6 gewahrt.

Pruefung bestanden. Belege:
- Alle acht internen Links geprueft, jedes Ziel existiert (docs/index, schnellstart,
  formate, api, betrieb/konfiguration, entwicklung, grenzen, contracts/api.md).
- Jeder genannte Make-Befehl steht in `make help`: up, help, docs-serve.
- Port 8080 belegt durch `KAIMARKIT_HOST_PORT=8080` und das Mapping in
  docker-compose.yml; Port 8001 durch das docs-serve-Ziel; `/docs` durch den Mount
  in backend/app/main.py.
- `cp docker/.env.example docker/.env` deckt sich woertlich mit dem Hinweis des
  check-env-Ziels.
- SPRACHE.md gegengelesen, grep nach tragen-Formen ohne Treffer.

Merge b477728 auf main, Branch task/28-readme geloescht.
