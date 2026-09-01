---
id: 77
title: IN-13 · Die Docs-Stufe laeuft nach jedem Commit neu
status: backlog
priority: low
created: 2026-09-01T13:50:30.694332269+02:00
updated: 2026-09-01T14:10:45.24020749+02:00
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

[[2026-09-01]] Tue 14:10
## Mitzunehmen: zwei Messungen für #56 (Auflage des PO, 01.09.2026)

Dieses Ticket baut und startet den Dienst neu. Das **ist** der kontrollierte Neustart, den zwei offene Zahlen aus BE-17 (#56) brauchen — sie im selben Zug zu nehmen spart einen zweiten und, wichtiger, liefert beide aus demselben Lauf.

Vorschlag von akar, Bedingungen von ihm und hier eingelöst: Es steht im Rumpf und nicht nur in einer Nachricht, und der Subagent **misst und trägt ein, er entscheidet nichts.**

### Was zu messen ist

Am frischen Container, unmittelbar nacheinander:

1. **Zeit bis `healthy`** — vom Start bis zum ersten gelungenen Healthcheck. **Gleich beim Start abgreifen**, nicht nachträglich: `docker inspect` hält nur die letzten Einträge, und bei einem Container, der eine Stunde läuft, ist der erste herausgerollt. Die Auskunft ist einmal da und danach weg.
2. **Speicher im Ruhezustand** — `docker stats --no-stream`, bevor irgendetwas umgewandelt wird.
3. **Speicher während einer Umwandlung** — dieselbe Messung, während ein Dokument durch `docling` läuft, am **selben** Container, unmittelbar danach.

### Was ausdrücklich nicht zu tun ist

**Kein Vergleich mit und ohne Vorladen.** Dafür bräuchte es ein zweites Abbild ohne `_warmup`, und das ist den Aufwand nicht wert. Die Entscheidung in #56 hängt an absoluten Werten, nicht an einem Verhältnis: Die Zeit bis `healthy` muss deutlich unter `KAIMARKIT_HEALTH_START_PERIOD` (180 s) liegen, der Speicher deutlich unter `KAIMARKIT_MEM_LIMIT` (6 GB).

Fällt eines von beidem knapp aus, ist das ein Befund und geht als Notiz zurück — hier wird nichts umgebaut.

### Wohin die Zahlen gehören

Als Notiz an **#56**, mit dem Abbildstand. Die Folgerung daraus zieht sophies Lane, nicht dieses Ticket. Ein Satz in der Notiz dieses Tickets genügt als Verweis.

### Warum das keine Vermischung ist

Es ändert nichts am Gegenstand von #77 und besitzt keine zusätzliche Datei. Es nutzt nur einen Neustart, der ohnehin stattfindet. Ein eigenes Ticket dafür bräuchte denselben Neustart und könnte deshalb nie neben diesem laufen.
