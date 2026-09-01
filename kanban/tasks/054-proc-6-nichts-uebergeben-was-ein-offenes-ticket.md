---
id: 54
title: PROC-6 · Nichts uebergeben, was ein offenes Ticket noch besitzt
status: backlog
priority: low
created: 2026-09-01T09:47:23.708566938+02:00
updated: 2026-09-01T09:47:23.708566938+02:00
assignee: katche
tags:
    - process
class: standard
---

## Befund (01.09.2026, waehrend IN-9)

Der PO hat dem Nutzer die Adresse `http://localhost:8080` genannt, waehrend #50
(IN-9) noch auf `in-progress` stand. Der Nutzer hat ein PDF hochgeladen; in der
Zwischenzeit hatte der Subagent `make down` und `make up` gefahren, und die
Oberflaeche meldete "Der Dienst ist nicht erreichbar."

Nichts ging verloren, und die Oberflaeche hat sich richtig verhalten. Der Nutzer hat
trotzdem Zeit an einer Baustelle verbracht und einen Fehler gemeldet, den es nicht
gab.

## Die Lehre

**Waehrend ein Ticket offen ist, gehoert sein Gegenstand dem Subagenten, nicht dem
Nutzer.** Eine laufende Adresse ist keine Uebergabe. Wer zwischen zwei Pruefungen
abraeumt und neu startet, hat zwischendurch immer nichts stehen — der Ausfall ist
also kein Einzelfall beim Neubau, sondern die Regel waehrend der Arbeit.

Die Uebergabe haengt am Statuswechsel nach `review`, nicht daran, dass eine Adresse
gerade antwortet. Ein Zusatz "verlass dich noch nicht darauf" reicht nicht: Wer eine
Adresse bekommt, benutzt sie.

## Wo das hingehoert

`CLAUDE.md`, Abschnitt "Rollen und Lanes", bei den PO-Pflichten — neben Board-Sync,
Befunde auffangen und der Reihenfolge aus PROC-5 (#51). Dieselbe Sammlung, dieselbe
Vorlage in dot-claude.

## Pruefung

Die Stelle, die die PO-Pflichten beschreibt, sagt ausdruecklich, dass ein Ergebnis
erst nach dem Statuswechsel an den Nutzer geht.

## Zurueckgestellt

Vom Nutzer zurueckgestellt, bis die Abnahmefassung steht (01.09.2026). Verwandt mit
[[PROC-5]] (#51) — beide handeln davon, dass ein Board-Zustand sofort gilt.
