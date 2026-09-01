---
id: 71
title: BE-24 · Zwei Antworttypen fehlen in der veroeffentlichten OpenAPI-Fassung
status: done
priority: high
created: 2026-09-01T12:39:21.848759324+02:00
updated: 2026-09-01T12:51:20.4142963+02:00
started: 2026-09-01T12:51:13.817985029+02:00
completed: 2026-09-01T12:51:13.817985029+02:00
assignee: sophie
tags:
    - backend
    - api
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


## Umsetzung (sophie-19, 01.09.2026)

`/api/convert` trägt jetzt `response_model=ConversionEntry`, `/api/convert/batch`
trägt `response_model=BatchResponse`; beide Endpunkte geben das Modell selbst zurück
statt einer von Hand gebauten `JSONResponse`. Damit stehen beide Typen in
`/api/openapi.json` unter `components.schemas` — `ConversionStatus` kam als
Nebenwirkung mit —, und FastAPI prüft die Antwort beim Antworten gegen das Modell.

**Reihenfolge eingehalten, keine Abweichung gefunden.** Erst nachgesehen, was die
Endpunkte liefern, dann den Vertrag danebengelegt: Beides deckt sich Feld für Feld.
`markdown`, `engine`, `warnings` und `error` sind in beiden Zweigen immer vorhanden.
Kein Modell wurde angepasst, `models.py` blieb unangetastet, der Dreiklang brauchte
keinen gemeinsamen Commit.

**Der Dateizweig bleibt ein rohes `Response`** — Markdown mit `Content-Disposition`,
im Stapel das ZIP. FastAPI reicht ein zurückgegebenes `Response` an `response_model`
vorbei, der Zweig ändert sich also nicht. Damit die veröffentlichte Fassung ihn nicht
verschweigt, nennen zwei `responses=`-Einträge die zweiten Medientypen:
`text/markdown; charset=utf-8` und `application/zip` stehen jetzt neben
`application/json` in derselben 200-Antwort. Vorher sagte sie bei beiden Endpunkten
nur `application/json` mit leerem Schema.

### Tests

Neu in `backend/tests/test_openapi.py`, vier Stück:

- `test_openapi_names_both_answer_types` — beide Typen unter `components`, und die
  200 jedes Endpunkts verweist auf den richtigen.
- `test_openapi_keeps_the_second_branch` — Markdown- und ZIP-Medientyp stehen weiter drin.
- `test_convert_answers_exactly_a_conversion_entry` und
  `test_batch_answers_exactly_a_batch_response` — die Antwort wird gegen das Modell
  gelesen und zurückgeschrieben; identisch, also kein Feld zu viel und keins zu wenig.

**Gegenprobe ausgeführt**, nicht behauptet: `response_model` auf `None` zurückgesetzt,
Tests gelaufen, danach wiederhergestellt. Ergebnis `1 failed, 3 passed`,
`test_openapi_names_both_answer_types` fällt mit
`AssertionError: assert 'ConversionEntry' in {...}` durch. Die drei übrigen bleiben
grün: Sie prüfen, ob Handler und Modell übereinstimmen, beziehungsweise das
`responses=` — nicht das `response_model`.

`pytest -q`: 103 passed, 8 skipped, 4 deselected. `ruff check .` sauber. Kein
Container gebaut, alles über `TestClient`.

### Befund nebenbei, nicht geändert

`ErrorResponse` fehlt in der erzeugten OpenAPI-Fassung genauso. Jeder Fehlercode
kommt aus einem Exception-Handler, und kein Endpunkt deklariert seine 4xx- und
5xx-Antworten. Wer unter `/api/docs` nachsieht, findet die Codetabelle aus
`contracts/api.md` dort nicht wieder. Dieselbe Klasse von Problem, war schon vorher
da — gehört in ein eigenes Ticket.
