---
id: 83
title: IN-14 · Jeder Frontend-Worktree installiert node_modules neu
status: backlog
priority: low
created: 2026-09-01T16:31:20.780989763+02:00
updated: 2026-09-01T16:31:20.780989763+02:00
assignee: akar
tags:
    - infra
class: standard
---

## Befund (01.09.2026, gemeldet von benny aus FE-14)

`frontend/node_modules` fehlt in einem frischen Worktree. Jeder Frontend-Subagent
fährt deshalb zuerst `npm ci`, bevor überhaupt ein Test läuft. Benny hatte heute
sieben Tickets — die Minuten summieren sich.

## Was zu klären ist, bevor etwas gebaut wird

**Möglicherweise ist die Antwort „nichts tun".** npm hält einen eigenen Cache; ein
zweites `npm ci` auf derselben Maschine ist deutlich billiger als das erste. Wenn die
gemessene Dauer im frischen Worktree ohnehin klein ist, ist dieses Ticket erledigt,
ohne dass eine Zeile fällt.

Erst messen: Wie lange dauert `npm ci` in einem frischen Worktree, wenn der npm-Cache
warm ist? Die Zahl gehört in die Notiz.

## Denkbare Wege, falls es sich lohnt

- `npm ci --prefer-offline` als dokumentierter Befehl.
- `node_modules` aus dem Haupt-Checkout verlinken — **riskant**: Zweige können
  verschiedene Abhängigkeiten haben, und ein geteiltes Verzeichnis macht aus zwei
  Läufen einen. Nur, wenn die Messung es rechtfertigt und die Gefahr benannt ist.

## Eigene Dateien

- `docs/entwicklung.md` (Abschnitt zur Frontend-Entwicklung)
- `.claude/skills/work-lane/SKILL.md`, falls ein Befehl in die Arbeitsschleife gehört

Kein `package.json`, keine Änderung an den Abhängigkeiten.

## Prüfung

- Die gemessene Dauer steht in der Notiz, mit warmem und kaltem Cache.
- Wird ein Weg gewählt, ist er dokumentiert und einmal gefahren.
- Wird keiner gewählt, steht der Grund in der Notiz und das Ticket schließt trotzdem.
