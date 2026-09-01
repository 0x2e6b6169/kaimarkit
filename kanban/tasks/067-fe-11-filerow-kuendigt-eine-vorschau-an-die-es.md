---
id: 67
title: FE-11 · FileRow kuendigt eine Vorschau an, die es laengst gibt
status: done
priority: low
created: 2026-09-01T12:20:15.250971723+02:00
updated: 2026-09-01T12:25:09.314271525+02:00
assignee: benny
tags:
    - frontend
class: standard
---

## Befund (01.09.2026, gemeldet von benny aus FE-10)

Der Slot-Rueckfall in `frontend/src/components/FileRow.vue` sagt: "Die Vorschau folgt
mit FE-4. Bis dahin steht hier nur, dass N Zeichen Markdown vorliegen."

FE-4 (#16) ist gebaut, `App.vue` haengt `MarkdownPreview` ein. Der Satz kuendigt an,
was laengst da ist, und nennt dabei eine Ticketnummer, die ausserhalb des Boards
niemandem etwas sagt.

Der Rueckfall greift nur, wenn kein Elternteil den Slot fuellt — im Normalbetrieb
also nie. Sichtbar wird er, sobald jemand `FileRow` einzeln verwendet. Zwei Tests
pruefen den Satz und ziehen mit.

benny-11 hat ihn gemeldet statt geaendert: FE-10 berichtigte die Schreibung, nicht
die Aussagen. Richtig so.

## Eigene Dateien

- `frontend/src/components/FileRow.vue`
- `frontend/src/components/FileRow.test.ts`

## Vorgaben

Der Rueckfall sagt, was er zeigt, ohne auf ein Ticket zu verweisen — etwa den Umfang
des Markdown. Oder er faellt weg, wenn er nichts beitraegt; das entscheidet die Lane
am Gegenstand.

Eine Ticketnummer gehoert nicht in einen Text, den ein Nutzer lesen kann.

## Pruefung

- Der Satz nennt weder FE-4 noch eine andere Ticketnummer.
- Die beiden Tests pruefen den neuen Wortlaut.
- `npm run test` und `npm run typecheck` bleiben gruen.

## Ergebnis (benny-12)

Der Rueckfall bleibt. `FileQueue` haelt ihn per `v-if="$slots.preview"` bewusst am
Leben, und eine aufgeklappte Zeile ohne Inhalt saehe kaputt aus. Er sagt jetzt, was er
zeigt: "Das Ergebnis umfasst N Zeichen Markdown." — ohne Ticketnummer. Der
Kopfkommentar von `FileRow` nennt FE-4 ebenfalls nicht mehr.

Mitgezogen: `FileQueue.test.ts` sicherte denselben Satz durch die Zeile hindurch zu.
Kein offenes Ticket besitzt die Datei; die eine Zusicherung folgt dem Text, den sie
prueft.

86 Tests gruen, `npm run typecheck` gruen. Merge 22abc43 auf task/67-vorschau-rueckfall.
