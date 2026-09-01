---
id: 51
title: PROC-5 · Abhaengigkeit vor der Freigabe setzen, nicht danach
status: backlog
priority: low
created: 2026-09-01T08:56:13.051115364+02:00
updated: 2026-09-01T08:56:13.051115364+02:00
assignee: katche
tags:
    - process
class: standard
---

## Befund (01.09.2026, beim Verteilen von IN-9)

Der PO hat #45 nach `todo` geschoben und die Abhaengigkeit auf #50 zwei Kommandos
spaeter gesetzt. In den zwei Minuten dazwischen hat akars Lane #45 gezogen und einen
Subagenten verteilt. akar musste ihn stoppen, Worktree und Branch entfernen und das
Ticket zuruecksetzen.

Der Fehler steckt in der Reihenfolge, nicht im Werkzeug: `--add-dep` hat sauber
gewirkt, nur zu spaet. Ein Board mit laufenden Lanes hat kein stilles Zeitfenster —
`todo` ist die Freigabe, und sie gilt sofort.

## Die Regel

Erst die Abhaengigkeit, dann `move ... todo`. Ein Ticket, das nicht als Erstes
laufen soll, kommt nie ohne sein `depends_on` in `todo`.

## Wo das hingehoert

`CLAUDE.md`, Abschnitt "Rollen und Lanes", bei den PO-Pflichten — dieselbe Stelle
wie Board-Sync und Befunde auffangen. Wenn es dort steht, gehoert es auch in die
Vorlage `assets/claude-md-abschnitte.md` in dot-claude.

## Pruefung

Die Stelle, die die PO-Pflichten beschreibt, nennt die Reihenfolge ausdruecklich.

## Zurueckgestellt

Vom Nutzer zurueckgestellt, bis die Abnahmefassung steht (01.09.2026).
