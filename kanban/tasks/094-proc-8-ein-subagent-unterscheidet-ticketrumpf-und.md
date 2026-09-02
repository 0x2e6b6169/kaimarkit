---
id: 94
title: PROC-8 · Ein Subagent unterscheidet Ticketrumpf und Auftrag nicht
status: backlog
priority: low
created: 2026-09-02T15:44:25.642858211+02:00
updated: 2026-09-02T15:45:17.298785437+02:00
assignee: katche
class: standard
---

## Beobachtung

Ein Subagent meldete einen Befund über „den Ticketrumpf": Der dort genannte
SVG-Pfad sei veraltet. Der Rumpf nannte gar keinen Pfad — er stand im Auftrag,
den die Lane an den Subagenten geschrieben hatte, ausdrücklich als Rückfall ohne
Netz. Der Subagent sieht Ticketrumpf und Auftrag nebeneinander und unterscheidet
beim Berichten nicht zuverlässig, woher ein Satz stammt.

Kosten: Der PO greppte das Board nach etwas, das dort nie stand. Der Fehler war
nach zwei Minuten erkannt, aber nur, weil jemand nachgesehen hat.

Bisher **ein** Vorkommen (FE-16, #93, 2026-09-02). Deshalb Backlog und keine Regel.
Kommt es ein zweites Mal, gehört die Konsequenz nach CLAUDE.md oder in
`/work-lane`.

## Kandidat für die Regel

Wer einen Befund weitergibt, der sich auf ein Ticket beruft, sieht vorher im
Ticket nach. Ein Subagent kann seine eigene Auftragslage nicht vom Board
trennen; die Lane kann es.

## Entscheidung des PO

Offen. Vor der Freigabe ist zu klären, ob die Regel bei der Lane ansetzt
(nachsehen vor dem Weitergeben) oder beim Auftrag (nichts in den Auftrag
schreiben, was wie eine Ticketvorgabe aussieht — Rückfälle und Hilfsangaben
kenntlich machen).

[[2026-09-02]] Wed 15:45
benny führt den zweiten Ansatzpunkt ab sofort in der eigenen Lane, ohne Freigabe
und zu Recht: Wie eine Lane ihre Aufträge gliedert, entscheidet sie selbst.

Die Form: Alles, was von der Lane stammt und nicht aus dem Ticket, steht unter
einer eigenen Überschrift „Hinweise von der Lane (nicht aus dem Ticket)", und
jede Hilfsangabe darin nennt ihre Herkunft. Verbindlich bleibt der Rumpf.
Bisher stand das als Satz im Auftrag; ein Satz lässt sich beim Berichten
übersehen, eine Überschrift schlechter.

Damit ist das Ticket kein Entwurf mehr, sondern eine Messung: Läuft in bennys
Lane seit 2026-09-02. Vor einer Verallgemeinerung nach CLAUDE.md oder
`/work-lane` wartet der PO ab, ob ein Subagent unter dieser Gliederung noch
einmal eine Lane-Angabe dem Ticket zuschreibt. Bleibt das aus, beschreibt die
Regel etwas Erprobtes statt etwas Ausgedachtes.
