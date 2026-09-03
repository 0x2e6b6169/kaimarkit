---
id: 124
title: DOC-19 · Der Schnellstart prüft die Docker-Voraussetzung falsch
status: done
priority: medium
created: 2026-09-03T15:13:05.981344814+02:00
updated: 2026-09-03T15:18:44.424118823+02:00
started: 2026-09-03T15:18:36.986161738+02:00
completed: 2026-09-03T15:18:36.986161738+02:00
assignee: akar
tags:
    - docs
class: standard
---

## Ziel

Befund von akar beim Abschluss von DOC-13 (#91): `docs/schnellstart.md:9` führt dieselbe
untaugliche Voraussetzungsprüfung, die DOC-13 in `docs/betrieb/lokal.md` beseitigt hat.

`docker compose version` fragt nur das Plugin und braucht den Daemon nicht. Auf einem
Rechner, dessen Nutzer nicht in der Gruppe `docker` ist, gibt der Befehl 0 zurück,
während `docker version` und `docker info` mit „permission denied … docker API"
scheitern. Eine Voraussetzungsprüfung, die besteht, obwohl die Voraussetzung fehlt.

Der Fehler war schon vor DOC-13 da, deshalb hat akar ihn gemeldet statt mitgeändert.

## Eigene Dateien

- `docs/schnellstart.md`

Nicht hier: `docs/betrieb/lokal.md` und `Makefile` — beide hat DOC-13 bereits berichtigt.

## Vorgaben

- Dieselbe Prüfung wie in `docs/betrieb/lokal.md`: `docker version`. DOC-13 hat sie
  gegen `docker info` abgewogen und sich begründet dafür entschieden (0,13 s gegen
  1,80 s, gleicher Fehlerfall, nennt zusätzlich die Server-Version). Nicht neu abwägen
  — abschreiben, damit beide Seiten dasselbe sagen.
- Ob die Abhilfe samt ihrem Preis hier wiederholt wird oder ein Verweis auf
  `docs/betrieb/lokal.md` genügt, entscheidet die Lane. Der Schnellstart soll kurz
  bleiben; ein Verweis ist kein Mangel.
- `make check-docker` gibt es seit DOC-13. Falls der Schnellstart eine Handprüfung nennt,
  wo inzwischen ein Ziel steht, gehört das mit richtiggestellt.

## Prüfung

- Rot vor grün, ohne Test: Vor der Arbeit `grep -n "compose version" docs/schnellstart.md`
  mit Fundstelle in die Notiz, danach ohne Fund.
- `grep -rn "compose version" docs/` findet nach der Arbeit keine Stelle mehr, die den
  Befehl als Voraussetzungsprüfung ausgibt.
- `mkdocs build --strict` ohne Warnung.


## Notiz akar-42 (DOC-19, 2026-09-03)

Rot vor grün: vorher `docs/schnellstart.md:9` — „Eine Docker Engine mit dem
Compose-Plugin — `docker compose version` muss antworten —". Nachher findet
`grep -n "compose version" docs/schnellstart.md` nichts (Rückgabewert 1).

Der Abschnitt „Was vorher da sein muss" nennt die Voraussetzung jetzt ohne Befehl
und stellt `docker version` als eigene Prüfung daneben, im Wortlaut von
`docs/betrieb/lokal.md`. Die Abwägung von DOC-13 (#91) ist übernommen, nicht neu
geführt: 0,13 s gegen 1,80 s bei `docker info`, gleicher Fehlerfall, nennt
zusätzlich die Server-Version.

**Entscheidung: Verweis statt Wiederholung — mit dem Preis in einem Satz.** Der
Schnellstart soll kurz bleiben und verweist schon in der Einleitung auf Lokaler
Betrieb; die Abhilfe (`sudo usermod -aG docker $USER`, danach neu anmelden) samt
Abwägung dort zu wiederholen hätte den kürzesten Weg zum laufenden Dienst um einen
halben Bildschirm verlängert. Eines darf der Leser aber nicht erst nach einem Klick
erfahren: den Preis. Ein Satz nennt deshalb die fehlende Gruppe `docker` und dass
sie auf diesem Rechner effektiv Root bedeutet; der Link auf
`betrieb/lokal.md#was-vorher-da-sein-muss` liefert Befehl und Abwägung.

`make check-docker` gibt es seit DOC-13, doch der Schnellstart nannte weder Ziel
noch Handprüfung dafür — er ruft `make up`. Dort steht jetzt derselbe Satz wie in
lokal.md: `make up` stellt die Frage vor dem Bau von selbst und bricht ab, bevor die
erste Stufe anläuft. Das Ziel selbst bleibt ungenannt; es hängt als Vorbedingung an
`up`, `down`, `logs` und `build`.

`grep -rn "compose version" docs/` findet noch zwei Stellen, beide in anderer Rolle
und deshalb nicht angefasst: `docs/betrieb/lokal.md:42` führt den Befehl ausdrücklich
als Gegenbeispiel („beantwortet diese Frage **nicht**"), `docs/betrieb/traefik.md:151`
liest damit die Compose-Version für die Anforderung „2.24 oder neuer" — genau die
Frage, die der Befehl beantworten kann.

`mkdocs build --strict`: Rückgabewert 0, keine WARNING- oder ERROR-Zeile. Die rote
Ausgabe ist der Material-Hinweis auf MkDocs 2.0, keine Buildmeldung.

Commit `66964b2`, Merge `7abc7f5`. Worktree entfernt, Zweig gelöscht.
