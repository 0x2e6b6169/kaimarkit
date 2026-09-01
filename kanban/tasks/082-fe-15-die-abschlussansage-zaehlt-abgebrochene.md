---
id: 82
title: FE-15 · Die Abschlussansage zaehlt abgebrochene Dateien nicht mit
status: done
priority: low
created: 2026-09-01T16:31:20.232261206+02:00
updated: 2026-09-01T16:35:49.741897269+02:00
started: 2026-09-01T16:35:44.223634478+02:00
completed: 2026-09-01T16:35:44.223634478+02:00
assignee: benny
tags:
    - frontend
    - ux
class: standard
---

## Befund (01.09.2026, gemeldet von benny aus FE-14)

Die Abschlussansage in `frontend/src/App.vue` sagt „Alle Dateien sind fertig: N
gelungen" und erwähnt abgebrochene Dateien nicht. Wer zwei von fünf abbricht, hört
eine Zahl, die seine eigene Entscheidung nicht abbildet.

Nicht falsch, aber unvollständig — und der Befund entsteht erst durch FE-14 (#79), war
im Rumpf also nicht vorherzusehen.

## Eigene Dateien

- `frontend/src/App.vue`
- der zugehörige Test

## Vorgaben

Die Ansage nennt die abgebrochenen Dateien neben den gelungenen und den
fehlgeschlagenen. Der Wortlaut soll den Unterschied halten, den FE-14 eingeführt hat:
Ein Abbruch ist kein Fehler, sondern eine Entscheidung des Nutzers.

Die Ansage geht an `aria-live` — sie wird vorgelesen. Kurz halten.

## Prüfung

- Zwei abgebrochene von fünf: Die Ansage nennt beide Zahlen, und die abgebrochenen
  erscheinen nicht als Fehler.
- Gegenprobe: Ohne Abbruch bleibt die Ansage wie bisher.
- Testdateien und Tests je mit Sammelzahl, `npm run typecheck` grün.


## Ergebnis (benny-16)

Die Ansage nennt die abgebrochenen Dateien getrennt: „Der Lauf ist zu Ende: 3
gelungen, 2 abgebrochen." Der Einleitungssatz wechselt nur bei einem Abbruch —
„Alle Dateien sind fertig" stimmt dann nicht, weil der Dienst im Hintergrund
weiterwandelt. Ohne Abbruch bleibt die Ansage wortgleich: „Alle Dateien sind
fertig: 1 gelungen, 1 fehlgeschlagen." Zahlen mit Null bleiben ungenannt, außer
den gelungenen; das war schon vorher so.

Kein Test außerhalb von `App.test.ts` sichert diesen Wortlaut zu, und
`docs/schnellstart.md` bleibt richtig — dort steht nur, dass die Warteschlange
den Abbruch nicht als Fehlschlag zählt.

Test Files 9 passed (9), Tests 101 passed (101), `npm run typecheck` grün.
