---
id: 35
title: 'PROC-1 · Ticketschnitt: gehoeren Doku-Seiten einer Lane?'
status: backlog
priority: low
created: 2026-08-31T11:46:15.810335482+02:00
updated: 2026-08-31T11:46:15.810335482+02:00
assignee: akar
tags:
    - process
class: standard
---

## Ziel

BE-9 (Commit `cdd5509`, sophies Lane) hat die Abschnitte "Tests" und
"Beispieldateien" an `docs/entwicklung.md` angehaengt — eine Datei, die der
Ticketschnitt DOC-2 (#21) zuweist. Beim Merge gab es einen Konflikt; akar hat
ihn verlustfrei aufgeloest, beide Haelften stehen in der Datei.

Kein Schaden also, aber genau die Kollision, die das Dateieigentum ausschliessen
soll. Zweimal hat es gehalten, weil jemand von Hand aufgeraeumt hat.

Gemeldet von akar.

## Die offene Frage

Der Ticketschnitt in CLAUDE.md sagt: "Jedes Ticket nennt in seinem Rumpf die
Dateien, die es besitzt." Er sagt nicht ausdruecklich, dass Doku-Seiten ebenso
besessene Dateien sind wie Code. Ein Backend-Ticket, das seine Tests
beschreibt, greift deshalb naheliegend zu `docs/entwicklung.md`, ohne die Regel
verletzen zu wollen.

Zwei Wege stehen offen:

1. **Die Regel schaerfen.** In CLAUDE.md festhalten, dass `docs/`-Seiten Dateien
   mit Eigentuemer sind. Wer aus einer fremden Lane etwas beizutragen hat,
   uebergibt es per Ticketnotiz an den Eigentuemer, statt selbst zu schreiben.
   Kostet einen Umweg, macht die Konflikte aber unmoeglich.
2. **Die Ausnahme benennen.** Anhaengen an eine fremde Doku-Seite bleibt erlaubt,
   solange es ein eigener Abschnitt am Ende ist. Das ist der Zustand von heute —
   er hat funktioniert, aber nur, weil `.gitattributes` und ein wacher Mensch
   den Merge gerettet haben.

Ein dritter Weg waere, `docs/` wie `kanban/activity.jsonl` per `.gitattributes`
union-zu-mergen. Das loest den Konflikt technisch und erzeugt dafuer stumme
Dopplungen — deshalb hier nur der Vollstaendigkeit halber.

## Eigene Dateien

- `CLAUDE.md` (Abschnitt "Der Ticketschnitt")

Die Aenderung an CLAUDE.md liegt beim Nutzer, nicht bei einer Lane. Dieses
Ticket haelt den Fall fest, bis er entschieden ist.

## Pruefung

Der Nutzer hat sich fuer einen der Wege entschieden, und CLAUDE.md sagt
danach ausdruecklich, wie ein Ticket mit einer Doku-Seite umgeht, die einer
anderen Lane gehoert.

Erfasst via /findings (Test-Pass 2026-08-31)
