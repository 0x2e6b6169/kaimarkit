---
id: 36
title: DOC-7 · Ladezeitpunkt von Docling in der Doku nachziehen
status: todo
priority: medium
created: 2026-08-31T11:56:15.436625961+02:00
updated: 2026-08-31T11:56:17.078901783+02:00
started: 2026-08-31T11:56:17.087408335+02:00
assignee: akar
tags:
    - docs
    - bug
class: standard
---

## Ziel

Die Dokumentation behauptet an mehreren Stellen, Docling lade sein Modell erst
beim ersten Zugriff. Seit BE-11 (#33) stimmt das nicht mehr: `main.py` stoesst
das Vorladen beim Hochfahren an.

`docs/grenzen.md` hat sophie-10 im Zuge von BE-11 schon korrigiert. Ein Grep
ueber `docs/` und `contracts/` zeigt eine zweite Stelle, die dieselbe Aussage
weiterfuehrt:

- `docs/entwicklung.md`

Gemeldet von sophie als Nebenbefund aus BE-11.

## Eigene Dateien

- `docs/entwicklung.md`

Kein offenes Ticket besitzt diese Datei. DOC-6 (#34) besitzt
`docker/.env.example` und `docs/betrieb/konfiguration.md` — kein Ueberschnitt.

## Vorgaben

- Die Aussage zum Ladezeitpunkt auf den Stand nach BE-11 bringen: das Vorladen
  beginnt mit dem Hochfahren des Dienstes, `/api/health` wartet trotzdem nie,
  und waehrend des Aufbaus meldet `state()` weiterhin `warming`.
- Den Grep wiederholen, bevor das Ticket schliesst — die Suche oben lief auf dem
  Stand von `main` zum Zeitpunkt der Erfassung, INT-1 (#29) kann bis dahin
  weitere Seiten angefasst haben.
- Nur diese Aussage anfassen. Was sonst in der Datei steht, gehoert anderen
  Tickets.

## Pruefung

Ein Grep nach dem alten Wortlaut ueber `docs/` und `contracts/` findet keine
Stelle mehr, die das Laden beim ersten Zugriff behauptet. `mkdocs build
--strict` endet mit 0.

Erfasst via /findings (Test-Pass 2026-08-31)
