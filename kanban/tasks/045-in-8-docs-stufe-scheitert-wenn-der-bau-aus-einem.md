---
id: 45
title: IN-8 · Docs-Stufe scheitert, wenn der Bau aus einem Worktree laeuft
status: done
priority: high
created: 2026-08-31T17:07:30.823818638+02:00
updated: 2026-09-01T12:04:33.784551809+02:00
started: 2026-09-01T12:04:27.719060659+02:00
completed: 2026-09-01T12:04:27.719060659+02:00
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

[[2026-09-01]] Tue 09:13
Die Begruendung dieses Tickets ist staerker, als beim Verteilen angenommen. Ich hatte #45 gegen #50 als Entwicklerbequemlichkeit eingeordnet; das war zu kurz gegriffen.

Befund von akar, waehrend #50 lief: **Ein Bau aus dem gemeinsamen Haupt-Checkout hat keinen festen Stand.** akar-21 fing um 08:53 auf `ed56300` an; waehrend der Bau lief, merzten sophies Subagenten `0cc458a` (BE-13) und `6f9cafc` (BE-14) in genau das Verzeichnis, aus dem gebaut wurde. Die Abnahmefassung haette dem Nutzer die beiden Fehler vorgelegt, die wir gerade behoben hatten. Aufgefallen ist es nur, weil der PO die Merges nebenher gesehen hat — nicht, weil irgendetwas es gemeldet haette.

Der Worktree ist die Antwort darauf: Er faehrt einen festgelegten Stand, den fremde Merges nicht bewegen. Solange dieses Ticket offen ist, kann kein Bau reproduzierbar sein.

Daraus eine zusaetzliche Vorgabe: Der Abschnitt in `docs/entwicklung.md` sagt nicht nur, dass der Bau aus einem Worktree geht, sondern **dass er von dort laufen soll** — und warum. Ein Bau aus dem Haupt-Checkout ist kein Notweg mehr, sondern eine Fehlerquelle mit Namen.

[[2026-09-01]] Tue 09:58
Gegenprobe belegt, die diesem Ticket bisher fehlte (01.09.2026, aus dem Neubau fuer IN-9): **Aus dem Haupt-Checkout laeuft die Docs-Stufe sauber durch** — `#21 [docs 5/5] ... DONE 151.9s`, also greift der `git config --global --add safe.directory /src` dort und die Kette faellt korrekt auf `gh-pages` oder `mkdocs build` zurueck.

Damit steht beides gemessen nebeneinander, und der Befund ist eingegrenzt: Haupt-Checkout gruen, Worktree bricht mit 128 ab. Nur der Worktree-Fall ist ungedeckt. Wer dieses Ticket umsetzt, muss den Normalfall nicht mehr selbst herstellen, sondern nur dafuer sorgen, dass er gruen bleibt — die zweite Zeile der Pruefung hat damit einen belegten Ausgangswert.

Gemeldet von akar.

Umgesetzt von akar-22, Merge 8e1e799 (Branch task/45-docs-stage-worktree, Commit 55a47c5).

**Die Aenderung.** In `docker/Dockerfile` (Stufe 4, jetzt Zeile 88-113) steht die
ganze Git-Kette hinter der Frage `[ -d .git ]`. Vorher lief `git config --global
--add safe.directory /src` als erste Anweisung ungeschuetzt; im Worktree ist `.git`
eine Datei mit `gitdir:`-Zeiger, der im Container ins Leere laeuft, und Git beendet
daraufhin jeden Aufruf im Baum mit 128 — auch den, der aus dem Repo nichts liest.
Ist `.git` kein Verzeichnis, bleibt `GH_PAGES` leer, und der bestehende Zweig faellt
auf `mkdocs build` zurueck. Der `gh-pages`-Weg ist unveraendert. `.dockerignore` ist
nicht angefasst: Der Kommentar dort (Zeile 3-5) bleibt richtig, `.git` bleibt drin.

**Doku.** `docs/entwicklung.md`, neuer Abschnitt „Das Abbild wird aus dem Worktree
gebaut" hinter „Jedes Ticket bekommt einen eigenen Worktree". Er sagt, dass `make up`
und `make build` aus dem Worktree laufen sollen, und nennt den Grund: Der
Haupt-Checkout hat keinen festen Stand, fremde Merges landen waehrend des Laufs in
dem Verzeichnis, aus dem Docker liest, und nichts meldet das — ein falscher Bau
sieht aus wie ein richtiger. Dazu das Anlegen von `docker/.env` im Worktree, der
Hinweis auf denselben Containernamen und Port in jedem Checkout, und der bleibende
Unterschied: Aus dem Worktree entsteht die aktuelle Fassung, die veroeffentlichten
Versionen nur aus dem Haupt-Checkout.

**Pruefung, Punkt fuer Punkt.**

1. *Gegenprobe zuerst.* `docker build -f docker/Dockerfile --target docs .` aus
   `.worktrees/task-45` mit unveraendertem Dockerfile:
   `#13 0.543 fatal: not a git repository:
   /home/kai/claude-sandbox/projects/kaimarkit/.git/worktrees/task-45`,
   `exit code: 128`, Dockerfile:96. Genau der Befund des Tickets, nur mit dem
   eigenen Worktree-Pfad.
2. *Dieselbe Stufe mit der Aenderung:* `EXIT=0`, `Documentation built in 0.48
   seconds`. Im Abbild liegt der gebaute Stand ohne `versions.json` — die
   Rueckfallebene, wie vorgesehen.
3. *`make up` aus dem Worktree:* `EXIT=0`, `#19 [docs 5/5] ... DONE 28.8s`,
   `Container kaimarkit Started`, `docker inspect` meldet `healthy`,
   `/api/health` liefert `{"status":"ok","version":"0.1.0"}`, `/docs/` 200. Der neue
   Abschnitt steht im Abbild (`grep -c` in `/opt/kaimarkit/docs/entwicklung/index.html`
   findet ihn dreimal).
4. *`make up` aus dem Haupt-Checkout:* `EXIT=0`, `#17 [docs 5/5] ... DONE 23.6s`,
   `Container kaimarkit Recreated/Started`, `healthy`. Dieser Lauf steht; der Dienst
   laeuft auf `127.0.0.1:8080` (`/` 200, `/docs/` 200, `/api/health` ok).

**Abweichung von Pruefpunkt 2, und warum die Pruefung gemeint ist, nicht die
Arbeit.** Der Punkt verlangt, dass der Haupt-Checkout „weiter die Fassung aus
`gh-pages`" liefert und `/docs/versions.json` alle Versionen nennt. Dieses Repo hat
gar keinen Zweig `gh-pages` (`git rev-parse --verify gh-pages` -> `fatal: Needed a
single revision`, `git branch -a --list '*gh-pages*'` leer). Auch vor dieser
Aenderung nahm der Haupt-Checkout also die Rueckfallebene — die 151.9s aus dem
Nachtrag vom 09:58 sind pip-install plus `mkdocs build`, nicht `git archive`.
`/docs/versions.json` antwortet folgerichtig mit 404, vorher wie nachher.

Belegt habe ich den `gh-pages`-Weg deshalb an der Sache statt am Werkzeug: in einem
Wegwerf-Klon des Branches unter dem Scratchpad einen Zweig `gh-pages` mit
`versions.json` und `index.html` angelegt und die Docs-Stufe mit dem **geaenderten**
Dockerfile gebaut. Ergebnis: `DONE 0.4s` (also `git archive`, kein pip),
`/docs-site` enthaelt `index.html` und `versions.json`, Inhalt
`[{"version": "0.1", "title": "0.1", "aliases": ["latest"]}]`. Der Zweig wird
weiterhin gefunden und ausgepackt. Klon und Pruefabbilder sind wieder entfernt.

**Nebenbefund, nicht repariert.** Der Lauf aus dem Worktree hat die Stufen 2 und 3
neu gebaut (`#18 DONE 300.4s` pip, `#21 DONE 379.3s` Modelle), obwohl unter
`backend/` nichts geaendert war — der Cache des Laufs aus #50 hat nicht gegriffen.
Der anschliessende Lauf aus dem Haupt-Checkout traf ihn dann (nur die Docs-Stufe
lief neu, 23.6s). Das passt zu #55 (IN-10) und gehoert dorthin; hier nur vermerkt.
