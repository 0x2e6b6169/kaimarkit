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

## Zweiter Fall, gemeldet von sophie

Derselbe Schnittfehler ist schon einmal aufgetreten, und zwar andersherum.
`docs/formate.md` gehoert DOC-2 (#21), wurde aber von BE-2 bis BE-9 laufend
ergaenzt — jede Engine trug ihre Formate nach. BE-3 musste dort einen
Merge-Konflikt mit BE-4 von Hand aufloesen.

Das ist nicht der Fall aus dem Abschnitt oben. Dort haben zwei Tickets dieselbe
Codedatei angefasst, weil die Regel eine Luecke hat. Hier hat der Schnitt eine
Datei einem Eigentuemer zugewiesen, die jedes andere Ticket zwangslaeufig
anfassen muss: Wer eine Engine baut, weiss als Einziger, welche Formate sie
kann. Die Doku-Lane kann es erst hinterher abschreiben.

## Was der zweite Fall an der Frage aendert

Beide Wege oben passen darauf nicht. Ein Uebergabeweg macht aus jedem
Engine-Ticket eine Wartezeit auf die Doku-Lane; die Ausnahme "eigener Abschnitt
am Ende" erzeugt genau die Konflikte, die BE-3 von Hand aufgeloest hat.

Ein dritter Weg liegt naeher: Eine Seite, die mit jedem Ticket waechst, gehoert
keinem einzelnen Ticket. Entweder besitzt jedes Engine-Ticket sein eigenes
Bruchstueck und die Seite wird daraus gebaut, oder die Seite entsteht erst, wenn
alle Engines stehen — als eigenes Ticket am Ende der Welle, nicht mittendrin.

Welcher der drei Wege in CLAUDE.md landet, entscheidet der Nutzer. Dieses Ticket
sammelt die Faelle, bis er entschieden hat.
