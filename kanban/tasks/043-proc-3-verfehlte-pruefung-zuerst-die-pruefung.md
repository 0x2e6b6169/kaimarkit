---
id: 43
title: 'PROC-3 · Verfehlte Pruefung: zuerst die Pruefung verdaechtigen'
status: backlog
priority: low
created: 2026-08-31T14:05:10.07801012+02:00
updated: 2026-08-31T14:05:10.07801012+02:00
assignee: akar
tags:
    - process
class: standard
---

## Ziel

Dreimal an einem Tag war die **Pruefung** eines Tickets unter genau der Annahme
geschrieben, die sie haette pruefen sollen. Dreimal war die Annahme der Fehler,
nicht die Umsetzung.

- **DOC-5** — `mkdocs build --strict` sollte das fehlende `def_list` fangen. Es
  ist fuer diese Fehlerklasse blind.
- **DOC-6** — die Pruefung fragte nach der richtigen Schreibweise der
  OCR-Sprachen und setzte damit voraus, dass ueberhaupt eine wirkt.
  `KAIMARKIT_OCR_LANGS` wirkte gar nicht (BE-12, #37).
- **IN-6** — die Pruefung erwartete ein kleineres Abbild und setzte voraus, dass
  die EasyOCR-Gewichte darin liegen. Sie lagen nicht drin; das Abbild konnte
  offline kein OCR und warf 500 (merge 87ed9d9).

Alle drei sind nur aufgefallen, weil der Subagent die Abweichung **gemeldet**
hat, statt sie zu schliessen. Die naheliegende Reaktion auf eine verfehlte
Vorgabe ist, die eigene Arbeit zu verdaechtigen und nachzubessern, bis die Zahl
stimmt. Genau dann verschwindet der Befund.

Beobachtet und zusammengestellt von akar.

## Die Frage

Soll die Arbeitsweise ausdruecklich festhalten, wie ein Subagent mit einer
verfehlten Pruefung umgeht? Der Vorschlag in zwei Saetzen:

> **Weicht eine Pruefung ab, ist zuerst die Pruefung verdaechtig, nicht die
> Arbeit.** Der Subagent meldet die Abweichung, statt sie zu schliessen.

Der erste Satz ist die Lehre, der zweite die Bedingung, unter der sie ueberhaupt
jemanden erreicht. Ohne den zweiten bessert ein Agent still nach.

Zu entscheiden ist, wie streng das gilt:

1. **Als Regel in CLAUDE.md**, im Abschnitt "Der Ticketschnitt" neben den vier
   Rumpfabschnitten. Gilt dann fuer jedes Ticket.
2. **Als Auflage im Auftrag**, die die Eltern-Sitzung beim Verteilen mitgibt.
   Beweglicher, aber jede Sitzung muss daran denken.
3. **So lassen.** Dreimal hat es ohne Regel funktioniert, weil die Subagenten
   von sich aus gemeldet haben.

## Reichweite

Beruehrt CLAUDE.md ("Der Ticketschnitt") und den Skill `/work-lane`, der die
Definition of done beschreibt. Faellt die Entscheidung fuer Form 1 oder 2, gehoert
sie ausserdem in den Skill `/agent-orchestration` in dot-claude — er gibt den
Ticketrumpf und die Rolle der Pruefung an neue Projekte weiter. Sonst gilt die
Lehre hier und nirgends sonst.

Die Aenderung liegt beim Nutzer, nicht bei einer Lane — wie bei PROC-1 (#35) und
PROC-2 (#41).

## Pruefung

Der Nutzer hat sich fuer eine Form entschieden, und die Stelle, die den
Ticketrumpf beschreibt, sagt danach ausdruecklich, was bei einer verfehlten
Pruefung zu tun ist.
