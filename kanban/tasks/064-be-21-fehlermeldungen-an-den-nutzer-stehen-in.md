---
id: 64
title: BE-21 · Fehlermeldungen an den Nutzer stehen in ASCII-Umschrift
status: todo
priority: medium
created: 2026-09-01T12:12:55.183359933+02:00
updated: 2026-09-01T12:12:55.183359933+02:00
assignee: sophie
tags:
    - backend
    - ux
class: standard
---

## Befund (01.09.2026, aus dem Befund von benny zu FE-10 weitergesucht)

Dasselbe wie im Frontend, nur schwerer zu sehen, weil es erst im Fehlerfall auftaucht.
Der Nutzer hat es waehrend der Abnahme gelesen:

    Die Umwandlung hat die Zeitgrenze von 120 s ueberschritten

Erzeugt in `backend/app/uploads.py:121-122`. Weitere Stellen:

- `backend/app/uploads.py:91` — "{filename} ueberschreitet {n} MB"
- `backend/app/errors.py:60` — "Die Datei ueberschreitet ..."
- `backend/app/errors.py:67` — "Der Stapel ueberschreitet ..."
- `backend/app/errors.py:74` — "Die Zeitgrenze ... ist abgelaufen."

## Abgrenzung

Nur Zeichenketten, die als Meldung beim Nutzer landen. **Nicht** Docstrings,
Kommentare und Bezeichner — die bleiben, wie sie sind. Das haelt den Diff klein und
die Pruefung eindeutig.

## Eigene Dateien

- `backend/app/errors.py`
- `backend/app/uploads.py`
- die zugehoerigen Tests

Beruehrt sich nicht mit #60 (markitdown-Adapter und Doku).

## Vorgaben

Von Hand pruefen, nicht ersetzen lassen. Wo eine Meldung ohnehin angefasst wird,
gilt `SPRACHE.md` auch fuer den Rest des Satzes.

## Pruefung

- `grep -rnP "ueber|fuer|naech|waeh|groess" backend/app/errors.py backend/app/uploads.py`
  findet keine Treffer mehr in Zeichenketten, die zum Nutzer gehen.
- `pytest -q` bleibt gruen. Prueft ein Test auf den alten Wortlaut, wird er
  mitgezogen — er gehoert zu denselben Dateien.
- Gegenprobe: Eine Umwandlung, die in die Zeitgrenze laeuft, meldet "überschritten".
