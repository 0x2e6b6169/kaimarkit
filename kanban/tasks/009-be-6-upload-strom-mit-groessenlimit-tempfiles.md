---
id: 9
title: BE-6 · Upload-Strom mit Groessenlimit, Tempfiles, Semaphor, Zeitgrenze
status: done
priority: medium
created: 2026-08-31T10:20:16.570035673+02:00
updated: 2026-08-31T10:58:13.175858274+02:00
started: 2026-08-31T10:57:52.359806366+02:00
completed: 2026-08-31T10:57:52.359806366+02:00
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


## Ergebnis (sophie-03)

Gebaut in `backend/app/uploads.py`, gemergt als `merge: BE-6 upload streaming with limits`:

- `sanitize_filename(name)` — behaelt nur den Namensteil. `../../etc/passwd` wird zu
  `passwd`, `..`, `.` und ein leerer Name werden zu `upload`, Steuerzeichen fallen
  weg, die Laenge wird von vorn auf 255 gekuerzt, damit die Endung bleibt.
- `stored_upload(upload)` — asynchroner Kontextmanager. Schreibt den Upload in
  1-MiB-Bloecken in eine `NamedTemporaryFile` und bricht mit `FileTooLarge` ab,
  sobald `KAIMARKIT_MAX_FILE_SIZE_MB` ueberschritten ist; der Rest wird nicht mehr
  gelesen. Liefert `StoredUpload(path, filename)` und loescht die Datei im
  `finally`, auch im Fehlerfall.
- `run_conversion(func)` — fuehrt den blockierenden Aufruf ueber
  `anyio.to_thread.run_sync(..., abandon_on_cancel=True)` aus, hinter einem
  `asyncio.Semaphore` aus `KAIMARKIT_MAX_CONCURRENT` und `anyio.fail_after`
  (`KAIMARKIT_CONVERSION_TIMEOUT`) -> `ConversionTimeout`.

**Was BE-7 und BE-8 davon benutzen:** `async with stored_upload(file) as stored:` und
darin `await run_conversion(partial(engine.convert, stored.path, ...))`. Das
Antwortfeld `filename` kommt aus `stored.filename`.

**Prueflauf:** `pytest -q -k upload` -> 14 gruen. Geprueft: eine 3-MiB-Datei bei
1-MiB-Limit bricht ab, bevor sie vollstaendig gelesen ist (der Test misst die
gelesenen Bytes am Quellstrom); nach Erfolg, nach `FileTooLarge` und nach einem
Fehler im Rumpf ist das Spool-Verzeichnis leer; `../../etc/bericht.pdf` kommt als
`bericht.pdf` an; die Zeitgrenze liefert `ConversionTimeout`; bei
`KAIMARKIT_MAX_CONCURRENT=1` laeuft nie mehr als ein Thread. `ruff check .` sauber.

**Zwei Randnotizen:**

- Neu ist `backend/conftest.py` (drei Zeilen): Ohne den `sys.path`-Eintrag findet
  pytest ein fremdes Paket namens `app` aus einem anderen Projekt der Umgebung.
  BE-9 legt seine Fixtures besser nach `backend/tests/conftest.py`, nicht dorthin.
- `docs/grenzen.md` ist um die vier Grenzwerte und die bekannte Einschraenkung der
  Zeitgrenze ergaenzt (Vorgabe aus diesem Ticketrumpf). Die Datei gehoert sonst
  DOC-2 — die Ergaenzung steht am Ende und soll dort erhalten bleiben.
  `docker/.env.example` beschreibt die Variablen bereits vollstaendig, deshalb war
  dort nichts zu aendern; `docs/betrieb/konfiguration.md` ist noch ein Stumpf und
  gehoert DOC-3. Der Schnittstellen-Dreiklang blieb unangetastet.
