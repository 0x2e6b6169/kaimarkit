---
id: 41
title: PROC-2 · Sperrbegruendungen pruefbar machen
status: backlog
priority: low
created: 2026-08-31T12:07:49.698579853+02:00
updated: 2026-08-31T12:07:49.698579853+02:00
assignee: akar
tags:
    - process
class: standard
---

## Ziel

Ein Freitext-Grund an einer Sperre laesst sich nicht gegenpruefen. Genau daran
ist heute beinahe etwas vorbeigelaufen.

`--block` an DOC-6 (#34) nannte als Grund BE-11 (#33) — ein Ticket, das laengst
gemergt war. Die Sperre klang plausibel und war stale. Ein `/work-lane`-Durchlauf
prueft `depends_on` gegen den Status der Vorgaenger und findet solche Faelle; bei
einem Freitext kann er es nicht, weil dort kein Bezug steht, den man aufloesen
koennte. Gemeldet von akar.

## Die Frage

Soll eine Sperrbegruendung verpflichtend nennen, worauf sie wartet — als
Ticketnummer, nicht als Prosa? Dann laesst sich jede Sperre maschinell gegen den
Status ihres Bezugs pruefen, so wie `depends_on` heute.

Drei Formen sind denkbar:

1. **Jede `--block`-Begruendung nennt ein Ticket.** Wartet eine Sperre auf etwas
   ohne Ticket, wird das Ticket vorher angelegt. Streng, aber jede Sperre wird
   pruefbar.
2. **`depends_on` statt `--block`, wo immer es geht.** `--block` bleibt den
   Faellen vorbehalten, die kein Ticket haben — eine fehlende Entscheidung, ein
   Zugang, eine Person. Diese wenigen bekommen ein Datum und einen Eigentuemer.
3. **So lassen, Sperren im PO-Durchlauf gegenlesen.** Kostet nichts an Regeln
   und haengt daran, dass jemand regelmaessig hinsieht.

Beruehrt CLAUDE.md ("Rollen und Lanes") und den Skill `/work-lane`, der die
Pruefung heute beschreibt. Die Aenderung liegt beim Nutzer, nicht bei einer Lane —
wie bei PROC-1 (#35).

## Pruefung

Der Nutzer hat sich fuer eine Form entschieden, und die Stelle, die die Pruefung
von Sperren beschreibt, sagt danach ausdruecklich, woran eine Sperre erkennbar
bleibt.
