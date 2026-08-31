---
id: 11
title: BE-8 · Endpunkt /api/convert/batch und ZIP-Bau
status: todo
priority: medium
created: 2026-08-31T10:20:17.832410936+02:00
updated: 2026-08-31T10:30:45.065941956+02:00
assignee: sophie
tags:
    - backend
depends_on:
    - 10
class: standard
---

## Ziel

Mehrere Dateien in einem Aufruf, Ergebnis als ZIP.

## Eigene Dateien

- `backend/app/packaging.py`
- `backend/app/api/convert.py` (Stapel-Teil)
- `backend/tests/test_packaging.py`

## Vorgaben

- `POST /api/convert/batch` nimmt mehrere `file`-Felder, hoechstens
  `KAIMARKIT_MAX_FILES`.
- Ein Fehler bei einer Datei bricht den Stapel nicht ab. Im JSON steht je Eintrag
  `status`; im ZIP liegt neben den `.md`-Dateien eine `_errors.txt`, wenn etwas
  fehlschlug.
- `packaging.py` saeubert Dateinamen und loest Namenskollisionen auf
  (`bericht.md`, `bericht-2.md`). Kein Pfadanteil im Archiv.
- Das ZIP entsteht im Speicher und wird gestreamt, nicht auf Platte geschrieben.
- Hinweis: Das Frontend nutzt diesen Endpunkt nicht - es ruft `/api/convert` je
  Datei auf und packt selbst. Dieser Endpunkt ist fuer die API-Nutzung da.

## Pruefung

`pytest backend/tests/test_packaging.py -q` gruen: gleiche Dateinamen kollidieren
nicht, `../` verschwindet, eine fehlgeschlagene Datei erzeugt `_errors.txt`.
Ein curl-Aufruf mit drei Dateien liefert ein entpackbares ZIP.
