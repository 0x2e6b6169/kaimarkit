---
id: 70
title: FE-13 · Die fertige Zeile zeigt rohe Millisekunden
status: done
priority: medium
created: 2026-09-01T12:36:53.106709459+02:00
updated: 2026-09-01T12:44:54.779526099+02:00
assignee: benny
tags:
    - frontend
    - ux
class: standard
---

## Befund (01.09.2026, gemeldet von benny aus FE-12)

Die fertige Zeile schreibt die Gesamtdauer als rohe Millisekunden. Auf dem
Bildschirmfoto des Nutzers steht wörtlich:

    docling · 326062 ms

Das sind 5 Minuten 26 Sekunden — eine Zahl, die er im Kopf umrechnen muss, um sie zu
verstehen. Seit FE-12 (#68) steht in derselben Zeile während des Laufs „läuft · 0:47".
Dieselbe Zeitspanne erscheint also in zwei Schreibweisen, je nachdem ob die Datei
gerade läuft oder fertig ist.

Der Befund ist älter als FE-12 und fällt erst durch FE-12 auf. benny-13 hat ihn nicht
mitgeändert, weil das Ticket die laufende Zeile betraf und nicht die fertige. Richtig
so — der Umbau wäre über den Ticketrand hinausgegangen.

## Ziel

Eine Dauer sieht in derselben Zeile gleich aus, ob sie läuft oder fertig ist.

## Eigene Dateien

- `frontend/src/components/FileRow.vue`
- `frontend/src/components/FileRow.test.ts`

Erst seit dem Merge von FE-12 frei — dieselbe Datei.

## Vorgaben

Dieselbe Form wie die laufende Zeile: `5:26` statt `326062 ms`. Für kurze Läufe
entscheidet die Lane, was sich besser liest — `0:04` oder `4 s`; wichtig ist, dass
eine Sekundenangabe nicht als `0:00` verschwindet.

Nur die Anzeige. Die Zahl, die das Backend liefert, bleibt wie sie ist; das Feld im
Schnittstellen-Dreiklang wird nicht angefasst.

## Prüfung

- Eine fertige Zeile mit 326 062 ms zeigt `5:26`, eine mit 103 500 ms `1:43`.
- Ein Lauf unter einer Sekunde zeigt nicht `0:00`.
- Laufende und fertige Zeile benutzen dieselbe Formatierung — eine Funktion, nicht
  zwei.
- `npm run test` und `npm run typecheck` bleiben grün; ohne die Änderung fällt der
  neue Test durch.

[[2026-09-01]] Tue 12:44
## Ergebnis (benny-14)

Eine Funktion `formatDuration()` für beide Zustände. Ab einer Sekunde `m:ss`
(326 062 ms → `5:26`, 103 500 ms → `1:43`), darunter die Sekunde selbst:
35 ms → `0,04 s`, 300 ms → `0,3 s`, 0 ms → `0 s`. Damit verschwindet der
häufige markitdown-Fall nicht mehr als `0:00`.

Der laufende Zähler benutzt dieselbe Funktion und beginnt deshalb bei
`läuft · 0 s` statt `läuft · 0:00`. Die Zusicherung darauf stammt aus FE-12 und
steht in derselben Datei, ist also mitgezogen. Ausserhalb von
`FileRow.test.ts` steht keine Zusicherung auf `ms` — geprüft über alle Tests.

92 Tests grün, `npm run typecheck` grün. Gegenprobe ohne die Änderung an
`FileRow.vue`: 5 Tests rot. In `docs/` wird durch die Änderung kein Satz falsch
(`schnellstart.md` nennt „Engine und Dauer", ohne eine Schreibweise zu nennen;
`api.md` beschreibt `duration_ms` im Backend, das unangetastet bleibt).
