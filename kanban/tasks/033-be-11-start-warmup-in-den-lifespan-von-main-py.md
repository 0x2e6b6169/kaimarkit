---
id: 33
title: BE-11 · start_warmup() in den Lifespan von main.py einhaengen
status: todo
priority: medium
created: 2026-08-31T11:45:36.537469938+02:00
updated: 2026-08-31T11:46:24.737683487+02:00
started: 2026-08-31T11:46:24.741541958+02:00
assignee: sophie
tags:
    - backend
    - bug
class: standard
---

## Ziel

`docling.start_warmup()` wird nirgends beim Start der Anwendung aufgerufen. Das
Vorladen beginnt deshalb erst, wenn `get_converter()` zum ersten Mal zugreift —
also mitten in der ersten echten Wandlung. `/api/health` blockiert nie, aber wer
als Erster ein PDF hochlaedt, wartet auf das Modell.

BE-4 (#7) hat den Einhaenger gebaut und in seiner Ergebnisnotiz beschrieben:
"`start_warmup()` startet einen Daemon-Thread, `get_converter()` ruft ihn beim
ersten Zugriff selbst." Der zweite Halbsatz ist der Notnagel, nicht der Weg.
Gerufen wird er nirgends.

Gemeldet von sophie aus der Backend-Welle.

## Eigene Dateien

- `backend/app/main.py`
- `backend/app/converters/docling.py`

Kein offenes Ticket besitzt diese Dateien: BE-1 (#4), BE-3 (#6) und BE-4 (#7)
sind geschlossen. BE-10 (#32) besitzt `meta.py` und die Vertragsdateien, nicht
diese hier.

## Vorgaben

- `start_warmup()` haengt im Lifespan von `main.py`, damit das Vorladen beginnt,
  sobald der Dienst hochfaehrt.
- Der Aufruf darf den Start nicht aufhalten: der Daemon-Thread laeuft weiter,
  `/api/health` antwortet sofort.
- Fehlt Docling, faellt der Aufruf still aus — kein `ImportError`, kein
  Startabbruch, `state()` meldet weiterhin `unavailable`.
- Konvention 2 gilt: `main.py` importiert nichts aus `docling` selbst, der Weg
  fuehrt ueber das Adaptermodul.

## Pruefung

Ein Test zeigt, dass `start_warmup()` beim Hochfahren gerufen wird — vorher
schlaegt er fehl. Ein zweiter zeigt, dass der Start ohne installiertes Docling
gelingt. `pytest -q` und `ruff check .` bleiben gruen.

Erfasst via /findings (Test-Pass 2026-08-31)
