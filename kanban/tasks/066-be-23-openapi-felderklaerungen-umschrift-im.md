---
id: 66
title: 'BE-23 · OpenAPI-Felderklaerungen: Umschrift im Schnittstellen-Dreiklang'
status: done
priority: low
created: 2026-09-01T12:19:21.276601172+02:00
updated: 2026-09-01T12:36:14.960175204+02:00
started: 2026-09-01T12:27:38.899745151+02:00
completed: 2026-09-01T12:35:59.198883197+02:00
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


---

## Ergebnis (sophie-18, 01.09.2026)

Umschrift in den OpenAPI-Beschreibungen beseitigt. Commit `3764ce7`, Branch
`task/66-openapi-umschrift`, `--no-ff` nach `main` gemerged.

**Befund zum Schnitt:** `models.py` hat gar keine `Field(description=...)`-Argumente.
Die nutzersichtbaren Beschreibungen sind die **Klassen-Docstrings** — Pydantic stellt
sie als `schema.description` in die OpenAPI-Fassung. Ein AST-Lauf hat Docstrings,
`Field`-Schlüsselwörter, die übrigen String-Konstanten und die Kommentare getrennt
aufgezählt; getroffen wurden Modul-Docstring, `ConversionEntry` und
`CapabilitiesResponse` (fuer, pruefen, waehlbaren, waehlen, laesst, Praeferenz,
fuehrt, geaendert). Die Enum-Werte (`ok`, `failed`, `file_too_large` …) sind
Bezeichner, keine Beschreibungen, und blieben unberührt.

**Dreiklang (Konvention 1) — für die Frontend-Lane:** `models.py`, `contracts/api.md`
und `frontend/src/types.ts` sind in einem Commit angefasst. In `types.ts` sind
ausschließlich die vier JSDoc-Blöcke geändert (Modul, `ConversionEntry`,
`CapabilitiesResponse`, `ConvertOptions`), kein Typ und kein Bezeichner.
`contracts/api.md` schrieb diese Passagen schon vorher richtig und bleibt inhaltlich
deckungsgleich, also ohne Änderung.

**Prüfung:** `/api/openapi.json` über `TestClient` zeigt die
`CapabilitiesResponse`-Beschreibung mit Umlauten. `pytest -q`: 114 passed,
4 deselected. `ruff check .` sauber. `git diff` gegen Feldnamen und Typen geprüft —
nur Beschreibungstexte. **Offen:** `npm run typecheck`. `node_modules` ist weder im
Worktree noch im Board-Home installiert, und installiert habe ich nichts; die
Änderung an `types.ts` betrifft nur Kommentartext, keinen Typ.

## Drei Befunde für den PO (nicht geändert)

1. `ConversionEntry` und `BatchResponse` tauchen in der erzeugten OpenAPI-Fassung gar
   nicht auf — kein Endpunkt deklariert sie als `response_model`. Unter `/api/docs`
   stehen damit nur `CapabilitiesResponse`, `HealthResponse` und `Limits`. Die
   Docstrings der beiden sind berichtigt, sichtbar sind sie dort trotzdem nicht.
2. `contracts/api.md` nennt als Beispiel `"Datei ist groesser als 50 MB."` und
   `"pandoc: konnte die Datei nicht lesen (beschaedigtes Archiv)"`. Beides sind
   JSON-Beispielrümpfe, keine Beschreibungen — deshalb ausgelassen. Der erste weicht
   ausserdem vom echten Wortlaut ab: `uploads.py:91` wirft
   `"{filename} überschreitet {N} MB"`.
3. Umschrift in Docstrings ausserhalb meiner Dateien: `errors.py:60` und
   `uploads.py:73` (»ueberschreitet«), dazu Testfixtures in `backend/tests/` und
   `frontend/src/__tests__/` (»beschaedigt«).
