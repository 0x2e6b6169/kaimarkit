---
id: 113
title: BE-36 · test_openapi.py prüft die Fehlerantworten von /api/convert/url nicht
status: todo
priority: low
created: 2026-09-03T11:42:54.518942358+02:00
updated: 2026-09-03T11:42:54.518942358+02:00
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
