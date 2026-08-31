---
id: 21
title: 'DOC-2 · Inhalte: Schnellstart, Formate, API, Entwicklung, Grenzen'
status: todo
priority: medium
created: 2026-08-31T10:20:24.247774672+02:00
updated: 2026-08-31T10:30:46.278942761+02:00
assignee: akar
tags:
    - docs
depends_on:
    - 20
    - 11
class: standard
---

## Ziel

Die Dokumentation, aus der jemand das Werkzeug bedienen kann, ohne den Code zu
lesen.

## Eigene Dateien

- `docs/index.md`, `docs/schnellstart.md`, `docs/formate.md`, `docs/api.md`,
  `docs/entwicklung.md`, `docs/grenzen.md`

## Vorgaben

- Deutsch nach den Prosa-Regeln aus `~/.claude/rules/SPRACHE.md`. Bezeichner,
  Codebeispiele und Variablennamen bleiben englisch.
- `formate.md`: die Matrix aus dem Plan, dazu je Engine ein Satz, wofuer sie taugt
  und wofuer nicht. Ausdruecklich: Pandoc kann PDF nicht lesen.
- `api.md`: jeder Endpunkt mit einem curl-Beispiel, das sich kopieren und
  ausfuehren laesst. Quelle ist `contracts/api.md`.
- `grenzen.md`: was das Werkzeug nicht kann. Mindestens: gescannte PDFs ohne OCR
  liefern wenig; die Zeitgrenze beendet den Wartevorgang, nicht den Thread;
  mehrere Worker halten je eigene Docling-Modelle im Speicher.
- `entwicklung.md`: Aufbau, wie man eine vierte Engine ergaenzt, wie das Board
  benutzt wird.

## Pruefung

`mkdocs build --strict` ohne Warnung. Jeder curl-Aufruf aus `api.md` laeuft gegen
den laufenden Dienst und liefert, was dort steht.
