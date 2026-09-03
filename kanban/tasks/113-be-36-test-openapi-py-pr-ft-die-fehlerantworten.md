---
id: 113
title: BE-36 · test_openapi.py prüft die Fehlerantworten von /api/convert/url nicht
status: done
priority: low
created: 2026-09-03T11:42:54.518942358+02:00
updated: 2026-09-03T14:22:48.209309813+02:00
started: 2026-09-03T14:22:46.928540844+02:00
completed: 2026-09-03T14:22:46.928540844+02:00
assignee: sophie
tags:
    - backend
class: standard
---

## Ziel

Befund aus BE-35 (#107): `backend/tests/test_openapi.py` führt in `ERROR_CODES` nur `/api/convert` und `/api/convert/batch`. Die Fehlerantworten des neuen Endpunkts `/api/convert/url` (400, 413, 415, 500, 504) stehen damit in keiner OpenAPI-Prüfung, und `test_openapi_binds_each_endpoint_to_its_model` kennt ihn ebenfalls nicht.

## Eigene Dateien

- `backend/tests/test_openapi.py`

Fehlt im OpenAPI-Dokument ein Code, den `contracts/api.md` für den Endpunkt nennt, ist das ein Befund für `api/convert.py`: melden, nicht hier flicken.

## Vorgaben

- `/api/convert/url` in `ERROR_CODES` mit den Codes aus `contracts/api.md` aufnehmen und in der Modellbindung an `ConversionEntry` prüfen.

## Prüfung

1. Vorher rot: Die Codes für `/api/convert/url` eintragen und nur diesen Test laufen lassen; er muss zuerst zeigen, was fehlt, oder grün durchlaufen. Läuft er sofort grün, steht das als Beleg in der Notiz, dass der Endpunkt alle Codes schon dokumentiert.
2. `pytest -q -rs` grün; Sammelzahl, ausgewählte Zahl und Übersprungenes nennen.



## Ergebnis (sophie-39)

`/api/convert/url` steht jetzt in `ERROR_CODES` mit 400, 413, 415, 500 und 504 — die Codes von `/api/convert` plus `invalid_url` (400), wie `contracts/api.md` es dem Endpunkt zuschreibt ("Deshalb gelten dieselben Fehler wie bei /api/convert, dazu invalid_url"). Dazu prüft `test_openapi_binds_each_endpoint_to_its_model` die 200-Antwort gegen `ConversionEntry`.

**Der Test lief sofort grün.** BE-35 (#107) hat den Endpunkt vollständig ausgezeichnet: `/api/openapi.json` nennt für `POST /api/convert/url` die Antworten 200, 400, 413, 415, 422, 500 und 504, jede Fehlerantwort mit `$ref` auf `ErrorResponse`, und die 200-Antwort verweist auf `ConversionEntry`. Damit ist kein Befund für `api/convert.py` offen; die Lücke lag allein im Test, der den Endpunkt nicht kannte.

Berichtigt wurde außerdem der Docstring von `test_openapi_names_the_error_codes_of_each_endpoint`: Er sprach von "beiden Endpunkten", was mit dem dritten falsch geworden wäre.

Zahlen: `pytest -q -rs` im Backend — 204 gesammelt, 197 ausgewählt, 197 bestanden, 7 abgewählt (Marker `slow`, laufen nur im Abbild), nichts übersprungen. `ruff check .` sauber. Nur `backend/tests/test_openapi.py` angefasst.

Zweig `task/113-openapi-url`, Merge `b0c7e0c`.
