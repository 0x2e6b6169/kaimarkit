---
id: 9
title: BE-6 · Upload-Strom mit Groessenlimit, Tempfiles, Semaphor, Zeitgrenze
status: todo
priority: medium
created: 2026-08-31T10:20:16.570035673+02:00
updated: 2026-08-31T10:30:45.064526591+02:00
assignee: sophie
tags:
    - backend
depends_on:
    - 4
class: standard
---

## Ziel

Hochgeladene Dateien sicher entgegennehmen und die Last begrenzen.

## Eigene Dateien

- `backend/app/uploads.py`

## Vorgaben

- Die Datei wird in Bloecken in eine `NamedTemporaryFile` geschrieben und beim
  Ueberschreiten von `KAIMARKIT_MAX_FILE_SIZE_MB` abgebrochen. Eine Pruefung nach
  dem vollstaendigen Einlesen kaeme zu spaet - dann liegt die Datei schon im
  Speicher.
- Aufraeumen im `finally`, auch im Fehlerfall. Der Dienst speichert nichts.
- Dateinamen werden gesaeubert: kein Pfadanteil, keine Traversierung.
- Ein `asyncio.Semaphore` aus `KAIMARKIT_MAX_CONCURRENT` begrenzt die
  gleichzeitigen Konvertierungen. Ohne diese Bremse legen drei parallele
  Docling-Laeufe den Container lahm.
- Der eigentliche Aufruf laeuft ueber `anyio.to_thread.run_sync`.
- Zeitgrenze je Datei aus `KAIMARKIT_CONVERSION_TIMEOUT` -> `ConversionTimeout`.
  Bekannte Einschraenkung: Der Thread laeuft weiter, bis er endet, und belegt das
  Semaphor. Das gehoert in `docs/grenzen.md`.

## Pruefung

`pytest -q -k upload` gruen: eine zu grosse Datei wird abgebrochen, bevor sie
vollstaendig gelesen ist; nach jedem Fall existiert keine Datei mehr in `/tmp`;
ein Dateiname mit `../` landet ohne Pfadanteil im Ergebnis.
