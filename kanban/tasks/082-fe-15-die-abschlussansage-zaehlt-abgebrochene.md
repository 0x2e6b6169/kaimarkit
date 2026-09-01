---
id: 82
title: FE-15 · Die Abschlussansage zaehlt abgebrochene Dateien nicht mit
status: todo
priority: low
created: 2026-09-01T16:31:20.232261206+02:00
updated: 2026-09-01T16:31:20.232261206+02:00
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
