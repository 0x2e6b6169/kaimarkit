---
id: 77
title: IN-13 · Die Docs-Stufe laeuft nach jedem Commit neu
status: backlog
priority: low
created: 2026-09-01T13:50:30.694332269+02:00
updated: 2026-09-01T13:50:30.694332269+02:00
assignee: akar
tags:
    - infra
    - performance
class: standard
---

## Befund (01.09.2026, gemessen von akar beim Abschluss von IN-10)

Die Docs-Stufe kopiert mit `COPY . .` (Zeile 107) den gesamten Bau-Kontext samt
`.git`. Weil `.git` sich bei jedem Commit ändert, läuft die Stufe nach **jedem**
Commit neu — gemessen 20 bis 23 Sekunden.

Seit IN-10 (#55) den Bau von 485 s auf 86 s gebracht hat, sind das rund ein Viertel
der verbleibenden Zeit. Vorher ging es im Rauschen unter.

## Die Vorgeschichte, damit niemand denselben Weg zweimal geht

Bei der Suche nach der Cache-Ursache in #55 stand `COPY . .` als Verdächtiger im
Raum. Der PO hat sie ausgeschlossen — richtig: Sie gehört zur Docs-Stufe mit eigenem
`FROM` und kann die Installationsschicht der Builder-Stufe nicht verwerfen. Die
eigentliche Ursache lag in den `.dockerignore`-Mustern.

**Ihre eigene Schicht verwirft sie aber sehr wohl.** Der Verdächtige war unschuldig
für die große Tat und schuldig für eine kleinere.

## Warum `.git` nicht einfach hinausfliegt

`.dockerignore` nennt den Grund im Kopf: Die Docs-Stufe holt die veröffentlichte
Dokumentation mit `git archive gh-pages` aus dem Repo. Ohne `.git` fällt sie auf
`mkdocs build` zurück und liefert nur die aktuelle Fassung. Wer `.git` ausschließt,
löst dieses Ticket und bricht das, wofür IN-8 (#45) gebaut wurde.

## Eigene Dateien

- `docker/Dockerfile` (Stufe `docs`)
- `.dockerignore`, falls die Lösung dort ansetzt

## Vorgaben

Die Stufe kopiert, was sie braucht, statt alles. Sie braucht `.git` und die
mkdocs-Eingaben — nicht `backend/`, nicht `frontend/`, nicht `docker/`.

Ob das über gezielte `COPY`-Anweisungen geht oder über einen anderen Weg an die
veröffentlichte Fassung, entscheidet die Lane am Gegenstand.

## Prüfung

- Ein Commit, der weder `docs/` noch `mkdocs.yml` anfasst, lässt die Docs-Stufe
  `CACHED` melden.
- Gegenprobe: Eine Änderung an `docs/` lässt sie zu Recht neu laufen.
- Der Rückfall bleibt heil: Aus einem Checkout mit `gh-pages` landet die
  veröffentlichte Fassung weiterhin im Abbild, aus einem ohne greift `mkdocs build`.
- Die gemessene Bauzeit vorher und nachher steht in der Ticketnotiz.
