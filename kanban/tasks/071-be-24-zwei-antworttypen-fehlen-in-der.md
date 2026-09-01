---
id: 71
title: BE-24 · Zwei Antworttypen fehlen in der veroeffentlichten OpenAPI-Fassung
status: in-progress
priority: high
created: 2026-09-01T12:39:21.848759324+02:00
updated: 2026-09-01T12:42:55.983314288+02:00
assignee: sophie
tags:
    - backend
    - api
claimed_by: sophie-19
claimed_at: 2026-09-01T12:42:55.983314288+02:00
class: standard
---

## Befund (01.09.2026, gemeldet von sophie beim Abschluss von BE-23)

`ConversionEntry` und `BatchResponse` tauchen in der erzeugten OpenAPI-Fassung **gar
nicht auf**. Den Endpunkten fehlt ein `response_model`.

Der Schnittstellen-Dreiklang ist damit an dieser Stelle nur auf dem Papier
geschlossen: `contracts/api.md`, `models.py` und `types.ts` stimmen überein — aber die
Schnittstelle, die der Dienst tatsächlich veröffentlicht, kennt zwei der Typen nicht.
Wer unter `/api/docs` nachsieht, findet sie nicht.

Gefunden über einen Lauf durch den Syntaxbaum, nicht über `grep`.

## Warum das mehr wert ist als der Anlass

Ein `response_model` an den Endpunkten macht die Typen nicht nur sichtbar. FastAPI
prüft die Antwort damit zugleich gegen das Modell — eine Abweichung fällt dann beim
Antworten auf und nicht erst im Frontend.

## Eigene Dateien

- `backend/app/api/convert.py`
- die zugehörigen Tests

`models.py` nur, falls ein Modell dafür fehlt. Ändert sich dabei ein Feld oder ein
Name, ist das der Schnittstellen-Dreiklang — dann kommen `contracts/api.md` und
`frontend/src/types.ts` in denselben Commit.

## Vorgaben

Erst nachsehen, was die Endpunkte heute wirklich zurückgeben, dann das Modell
danebenlegen. Weicht die tatsächliche Antwort vom Vertrag ab, ist das ein Befund und
kein Anlass, das Modell passend zu machen — melden und übergeben.

## Prüfung

- `/api/openapi.json` nennt `ConversionEntry` und `BatchResponse` unter `components`.
- Ein Test ruft beide Endpunkte auf und prüft die Antwort gegen das Modell.
- Gegenprobe: Ohne `response_model` fällt dieser Test durch.
- `pytest -q` bleibt grün.
