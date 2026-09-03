---
id: 124
title: DOC-19 · Der Schnellstart prüft die Docker-Voraussetzung falsch
status: todo
priority: medium
created: 2026-09-03T15:13:05.981344814+02:00
updated: 2026-09-03T15:13:23.603501916+02:00
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
