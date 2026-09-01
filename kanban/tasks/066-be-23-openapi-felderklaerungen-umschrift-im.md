---
id: 66
title: 'BE-23 · OpenAPI-Felderklaerungen: Umschrift im Schnittstellen-Dreiklang'
status: todo
priority: low
created: 2026-09-01T12:19:21.276601172+02:00
updated: 2026-09-01T12:27:38.884146294+02:00
started: 2026-09-01T12:27:38.899745151+02:00
assignee: sophie
tags:
    - backend
    - docs
class: standard
---

## Befund (01.09.2026, von sophie gemeldet)

`backend/app/models.py` beschreibt die Felder der API in ASCII-Umschrift. Diese Texte
stehen in der erzeugten OpenAPI-Fassung und damit unter `/docs` — sie sind
nutzersichtbar wie jede Fehlermeldung, nur an anderer Stelle.

## Warum eigens geschnitten

`models.py` gehoert zum **Schnittstellen-Dreiklang** (Konvention 1): Wer die Datei
anfasst, fasst `contracts/api.md` und `frontend/src/types.ts` im selben Commit an.
Das ist ein anderer Zuschnitt als "Meldungen in einer Datei berichtigen" und wuerde
BE-22 (#65) ueber zwei Lanes ziehen.

## Eigene Dateien

- `backend/app/models.py`
- `contracts/api.md`
- `frontend/src/types.ts`

Kollidiert nicht mit FE-10 (#63) — das besitzt die `.vue`-Dateien, nicht `types.ts`.
Wenn beide gleichzeitig offen sind, trotzdem nacheinander fahren.

## Vorgaben

Nur die Beschreibungstexte. Keine Feldnamen, keine Typen, keine Struktur — sonst ist
es kein Umschrift-Ticket mehr, sondern eine Schnittstellenaenderung.

Die drei Dateien bleiben inhaltlich deckungsgleich: Was in `models.py` als
Beschreibung steht, steht so auch im Vertrag.

## Pruefung

- `/docs` im laufenden Container zeigt die Beschreibungen mit Umlauten.
- Feldnamen und Typen sind unveraendert: `git diff` zeigt nur Beschreibungstexte.
- `pytest -q` und `npm run typecheck` bleiben gruen.
