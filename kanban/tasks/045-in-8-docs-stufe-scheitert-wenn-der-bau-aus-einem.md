---
id: 45
title: IN-8 · Docs-Stufe scheitert, wenn der Bau aus einem Worktree laeuft
status: todo
priority: high
created: 2026-08-31T17:07:30.823818638+02:00
updated: 2026-09-01T08:56:11.989913031+02:00
assignee: akar
tags:
    - infra
    - bug
depends_on:
    - 50
class: standard
---

## Ziel

Das Abbild laesst sich aus einem Git-Worktree bauen. Heute geht das nicht, und
genau so arbeitet dieses Projekt.

## Befund (belegt in INT-2, 31.08.2026)

`make up` aus `.worktrees/task-30` bricht in Stufe 4 ab:

```
#19 0.470 fatal: not a git repository: /home/kai/.../.git/worktrees/task-30
#19 ERROR: process "/bin/sh -c git config --global --add safe.directory /src ..."
           did not complete successfully: exit code: 128
```

Die Ursache liegt in der ersten Anweisung der Kette, nicht in der Abfrage nach
`gh-pages`. In einem Worktree ist `.git` keine Verzeichnis, sondern eine Datei mit
einem `gitdir:`-Zeiger auf einen Pfad des Haupt-Checkouts. Im Container gibt es den
nicht. Git behandelt einen ins Leere zeigenden `gitdir` als harten Fehler und
beendet **jeden** Aufruf im Baum mit 128 — auch `git config --global`, das gar
nichts aus dem Repo liest.

Gegenprobe, beide Male dasselbe Kommando:

```
Worktree als /src:        config exit=128   (fatal: not a git repository)
Haupt-Checkout als /src:  config exit=0
```

Die Abfrage nach `gh-pages` ist gegen einen fehlenden Zweig abgesichert
(`>/dev/null 2>&1`) und faellt sauber auf `mkdocs build` zurueck. Nur der
Worktree-Fall ist ungedeckt.

## Wirkung

Jeder Subagent arbeitet laut CLAUDE.md in einem Worktree. Keiner von ihnen kann
das Abbild aus seinem eigenen Verzeichnis bauen. INT-2 ist ausgewichen und hat
`KAIMARKIT_BUILD_CONTEXT` auf den Haupt-Checkout gesetzt — moeglich, aber es baut
dann fremden Stand, nicht den eigenen.

## Eigene Dateien

- `docker/Dockerfile` (Stufe 4, docs)
- `.dockerignore`, falls die Loesung dort ansetzt
- `docs/entwicklung.md`, falls der Weg dort erklaert gehoert

## Vorgaben

Die Stufe muss den Fall erkennen und wie bei fehlendem `gh-pages` auf
`mkdocs build` zurueckfallen, statt abzubrechen. Naheliegend ist, den ersten
Git-Aufruf ebenso abzusichern wie den zweiten, oder vorher zu pruefen, ob `.git`
ein Verzeichnis ist. Wer stattdessen `.git` in `.dockerignore` aufnimmt, verliert
die veroeffentlichte Dokumentation aus `gh-pages` — der Kommentar dort nennt den
Grund, warum sie drinbleibt.

## Pruefung

- `make up` aus einem frischen Worktree laeuft durch.
- `make up` aus dem Haupt-Checkout liefert weiter die Fassung aus `gh-pages`:
  `/docs/versions.json` nennt alle veroeffentlichten Versionen.
- Gegenprobe, dass die Pruefung anschlaegt: ohne die Aenderung bricht der Bau aus
  dem Worktree weiterhin mit 128 ab.

[[2026-09-01]] Tue 08:53
Nach todo gezogen, aber hinter #50 (IN-9). Grund ist kein Dateikonflikt, sondern ein Betriebsmittel: Beide Tickets bauen und starten den Dienst, beide benutzen denselben Containernamen `kaimarkit` und denselben Port 8080. Gleichzeitig laufen sie sich gegenseitig um. IN-9 zuerst, weil der Nutzer die Fassung heute testen will; IN-8 danach, mit dem Bau aus dem Worktree.
