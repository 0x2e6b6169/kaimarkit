---
id: 11
title: BE-8 · Endpunkt /api/convert/batch und ZIP-Bau
status: done
priority: medium
created: 2026-08-31T10:20:17.832410936+02:00
updated: 2026-08-31T11:14:10.928769793+02:00
started: 2026-08-31T11:13:56.04457332+02:00
completed: 2026-08-31T11:13:56.04457332+02:00
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


## Ergebnis (sophie-08)

`POST /api/convert/batch` haengt an demselben Router wie BE-7; der
Einzeldatei-Endpunkt blieb unberuehrt. Je Datei ein `ConversionEntry`: Ein
`ConversionError` wird zum Eintrag mit `status: failed`, der Stapel laeuft weiter.
Nur mehr als `KAIMARKIT_MAX_FILES` Dateien beenden die Anfrage — 413,
`too_many_files`. Uploads laufen ueber `stored_upload` und `run_conversion`, jede
Datei raeumt ihre Tempdatei im `finally` weg.

`packaging.py` baut das ZIP in einer `BytesIO` und gibt sie an eine
`StreamingResponse` — nichts landet auf Platte. Namen kommen durch
`sanitize_filename`, verlieren also jeden Pfadanteil, und Kollisionen werden
durchnummeriert (`bericht.md`, `bericht-2.md`). `_errors.txt` liegt nur dann im
Archiv, wenn wirklich etwas scheiterte.

Auslegung des Vertrags: „Nur 413 und 415 gelten fuer den Stapel als Ganzes" ist als
Aufzaehlung der Fehler der Anfrage gelesen. Ein `UnsupportedFormat` einer einzelnen
Datei bleibt ein gescheiterter Eintrag, sonst widerspraeche es „Ein Fehler bei einer
Datei bricht den Stapel nicht ab".

Geprueft: `pytest tests/test_packaging.py -q` 10 gruen (Kollision, `../`,
Backslash-Pfad, `_errors.txt` nur im Fehlerfall, Umlaut im Archiv, ZIP-Antwort,
JSON-Antwort, 413). Volle Suite auf `main` nach dem Merge: 74 passed, 1 skipped;
`ruff check .` sauber. Curl mit drei Dateien gegen ein laufendes uvicorn: ZIP
entpackbar, `bericht.md` + `bericht-2.md` + `_errors.txt`.

Dreiklang **nicht** angefasst — `BatchResponse` und `ConversionEntry` standen in
`models.py` bereits vertragsgleich. Keine neue `KAIMARKIT_*`-Variable:
`KAIMARKIT_MAX_FILES` steht schon in `docker/.env.example` und `docs/grenzen.md`.
Doku: `docs/api.md` um den Stapelabschnitt ergaenzt.

Fuer BE-9: eine Fixture mit **zwei gleichnamigen Dateien aus verschiedenen Ordnern**
und einer absichtlich kaputten Datei deckt den Stapel am besten ab; ohne Engines
reicht `.md` (passthrough).
