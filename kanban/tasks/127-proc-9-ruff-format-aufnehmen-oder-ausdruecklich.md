---
id: 127
title: 'PROC-9 · ruff format: aufnehmen oder ausdruecklich weglassen'
status: backlog
priority: low
created: 2026-09-07T09:47:57.591135982+02:00
updated: 2026-09-07T09:48:11.824743535+02:00
assignee: akar
tags:
    - process
class: standard
---

## Befund (2026-09-07, gemeldet von sophie-43 beim Abschluss von BE-39)

`ruff format --check` würde im Backend acht Dateien umformatieren (alte Stellen,
Zeilenlänge). Das Projekt fährt bislang nur `ruff check` — weder im Makefile noch in
CLAUDE.md steht `ruff format`. Solange das nicht entschieden ist, findet das jeder
nächste Subagent wieder und fragt erneut.

## Entscheidung, keine Umsetzung

Eine Produktentscheidung des PO, keine Ticketarbeit im engeren Sinn:

- entweder `ruff format` aufnehmen (Makefile-Ziel, CLAUDE.md-Vorgabe) und einmal über
  den bestehenden Stand laufen lassen, oder
- ausdrücklich in CLAUDE.md festhalten, dass nur `ruff check` gilt und `ruff format`
  bewusst nicht Teil des Workflows ist.

## Prüfung

Keine — dieses Ticket klärt eine Entscheidung, kein Verhalten. Nach der Entscheidung ggf.
neues Ticket für die Umsetzung.
