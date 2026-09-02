---
id: 96
title: ORG-2 · make docs-release von null, ohne gh-pages-Zweig
status: backlog
priority: low
created: 2026-09-02T16:29:46.681664448+02:00
updated: 2026-09-02T16:29:46.681664448+02:00
assignee: akar
class: standard
---

## Ziel

`make docs-release` einmal von null gehen. Dieses Repository hat keinen
`gh-pages`-Zweig; der erste Lauf legt ihn an. Diesen Weg ist niemand gegangen.

## Herkunft

Rest aus INT-3 (#90). Punkt 1 und 2 jenes Tickets sind durch die echte
VPS-Installation vom 2026-09-01 belegt, Punkt 3 nicht — der Nutzer hat den
Dienst installiert, nicht die Dokumentation veröffentlicht.

## Eigene Dateien

Voraussichtlich keine. Ein Lauf, kein Umbau. Ergibt der Lauf einen Befund an
`Makefile`, `mkdocs.yml` oder `docs/entwicklung.md`, gehört die Berichtigung
in denselben Merge — dann besitzt dieses Ticket die betroffene Datei.

## Vorgaben

**Nicht auf dem Zweig `main` des gemeinsamen Checkouts.** `mike` schreibt in
einen Zweig und wechselt dabei den Arbeitsbaum; das würde die Lanes unter den
Füßen wegziehen. Der Lauf gehört in einen eigenen Worktree oder einen
Wegwerf-Klon.

**Ein Fernziel wird nicht angefasst, solange nichts entschieden ist.** `mike
deploy` schiebt voreingestellt nicht, aber `--push` und eine falsch geerbte
Konfiguration tun es. Vor dem ersten Lauf prüfen, wohin das Ziel zeigt, und
das Ergebnis in der Notiz nennen. Ein versehentlich veröffentlichter
`gh-pages`-Zweig im öffentlichen Repository ist nicht zurückzunehmen.

## Prüfung

1. Vor dem Lauf: `git branch -a | grep gh-pages` ist leer. Belegen.
2. `make docs-release VERSION=0.1` läuft ohne Fehler durch.
3. Danach existiert `gh-pages` lokal und enthält eine Verzeichnisebene `0.1`
   sowie die von `mike` gepflegte Weiche (`versions.json`).
4. `main` ist unverändert: `git status` im Board-Home meldet nichts Neues.
5. In der Notiz steht, ob geschoben wurde und wohin.
