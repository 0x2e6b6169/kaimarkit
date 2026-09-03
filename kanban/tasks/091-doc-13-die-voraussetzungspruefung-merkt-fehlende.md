---
id: 91
title: DOC-13 · Die Voraussetzungspruefung merkt fehlende Docker-Rechte nicht
status: done
priority: medium
created: 2026-09-01T18:40:51.760156559+02:00
updated: 2026-09-03T15:10:57.583530378+02:00
started: 2026-09-03T15:01:05.845475184+02:00
completed: 2026-09-03T15:10:49.160058249+02:00
assignee: akar
tags:
    - docs
    - infra
class: standard
---

## Befund (01.09.2026, beim Vorbereiten des VPS-Aufbaus)

`docs/betrieb/lokal.md` nennt als Voraussetzung: „Docker Engine mit dem Compose-Plugin (`docker compose version` muss antworten)". Auf einem frischen Server antwortet der Befehl — und `docker info` scheitert trotzdem:

    permission denied while trying to connect to the docker API
    at unix:///var/run/docker.sock

Der Nutzer ist nicht in der Gruppe `docker`. `docker compose version` fragt nur das Plugin und braucht den Daemon nicht; die dokumentierte Prüfung geht also durch, während der erste echte Aufruf scheitert. **Eine Voraussetzungsprüfung, die besteht, obwohl die Voraussetzung fehlt** — dieselbe Klasse wie die Prüfungen, die heute schon grün waren, ohne etwas zu belegen.

`make up` ruft `docker compose` ohne `sudo`. Es scheitert damit beim ersten Versuch, und die Meldung nennt den Grund zwar, aber nicht die Abhilfe.

## Eigene Dateien

- `docs/betrieb/lokal.md` (Abschnitt „Was vorher da sein muss")
- `Makefile`, falls die Prüfung dort ansetzt (`check-env` prüft heute nur `docker/.env`)

## Vorgaben

Die Voraussetzungsprüfung fragt den **Daemon**, nicht das Plugin — `docker info` oder `docker version` statt `docker compose version`. Beides scheitert bei fehlender Gruppenzugehörigkeit.

Dazu die Abhilfe in einem Satz: `sudo usermod -aG docker $USER`, danach neu anmelden. **Mit dem Hinweis, was das bedeutet:** Wer in der Gruppe `docker` ist, kann auf dem Rechner effektiv Root werden. Auf einem eigenen Server ist das der übliche Handel, aber er gehört benannt und nicht verschwiegen.

Ob `make` selbst vorab prüfen soll, entscheidet die Lane. Ein Ziel, das nach zwanzig Minuten Bau an einem Rechteproblem scheitert, wäre die schlechtere Reihenfolge.

## Prüfung

- Die genannte Voraussetzungsprüfung scheitert auf einem Rechner ohne Gruppenzugehörigkeit. Gegenprobe: Sie besteht mit Zugehörigkeit.
- Der Hinweis nennt die Abhilfe und ihre Folge für die Rechte.
- `mkdocs build --strict` läuft durch.


## Ergebnis (akar-40, 03.09.2026)

Umgesetzt in `docs/betrieb/lokal.md` (Abschnitt „Was vorher da sein muss") und im `Makefile`. Merge-Commit **f65aabb**, Branch-Commit 98f0586.

**Wahl: `docker version`, nicht `docker info`.** Beide scheitern bei fehlendem Recht mit demselben Wortlaut und Rückgabewert 1. `docker version` stellt eine einzelne API-Anfrage, `docker info` sammelt den ganzen Daemon-Zustand ein. Gemessen auf dieser Maschine: `docker version --format '{{.Server.Version}}'` 0,13 s gegen `docker info --format '{{.ServerVersion}}'` 1,80 s — rund vierzehnmal so lang. Für eine Prüfung, die vor jedem `up`, `down`, `logs`, `build` und `test-slow-image` läuft, entscheidet das. Dazu zeigt `docker version` die Server-Version, also genau das, was eine Voraussetzungsprüfung wissen will.

**Makefile: ja, neues Ziel `check-docker`.** Vorgeschaltet bei `up`, `up-traefik`, `up-authelia`, `down`, `logs`, `build`, `test-slow-image`; `check-env` bleibt unverändert daneben. Grund: Der Bau backt die Docling-Modelle ein und dauert; an einem Rechteproblem darf er nicht erst danach scheitern. Kosten der Vorschaltung: 0,38 s für den ganzen `make check-docker`-Lauf, gegen einen Bau in Minuten. Der Fehlerfall druckt die letzte Zeile von `docker version`, dann `sudo usermod -aG docker $USER` samt Verweis auf `docs/betrieb/lokal.md`.

### Beleg — ohne Systemänderung

`setpriv --clear-groups` und `--groups=1000` gehen als unprivilegierter Nutzer nicht: „setgroups failed: Operation not permitted", rc 127. `unshare -Ur` hilft ebenfalls nicht — die kgids bleiben erhalten, `docker info` läuft darin durch. Stattdessen ein Socketpfad, an den das eigene Konto nicht darf: eine Datei mit Modus 000 unter `/tmp/dsock91.sock`, per `DOCKER_HOST` vorgehalten. Das erzeugt denselben Fehler wie der Befund und ändert nichts am System — kein sudo, kein usermod, keine Gruppen- oder Socketrechte angefasst.

ROT, `DOCKER_HOST=unix:///tmp/dsock91.sock`:

    docker compose version  ->  "Docker Compose version v5.1.4"                     rc=0   <- der Befund
    docker info             ->  "permission denied while trying to connect to the
                                 docker API at unix:///tmp/dsock91.sock"            rc=1
    docker version          ->  derselbe Wortlaut                                   rc=1

GRÜN, Gegenprobe am echten Socket, Nutzer in Gruppe `docker` (gid 1001):

    docker compose version  rc=0
    docker info             rc=0
    docker version          rc=0

`make check-docker` rot: rc=2 mit dem vollen Hinweistext. Grün: rc=0. `make -n up` zeigt beide Prüfungen vor `docker compose up`.

`mkdocs build --strict`: rc=0, null Zeilen WARNING oder ERROR.

### Befund für den PO — gemeldet, nicht geändert

`docs/schnellstart.md:9` führt dieselbe untaugliche Prüfung: „Eine Docker Engine mit dem Compose-Plugin — `docker compose version` muss antworten". Die Seite gehört nicht diesem Ticket, und diese Änderung hat sie nicht falsch gemacht; sie war es schon. Gehört nachgezogen. `docs/betrieb/traefik.md:151` nennt `docker compose version` zu Recht — dort geht es wirklich um die Plugin-Version, ab 2.24 wegen `!reset`.

Nebenbei: `/tmp/dsock91.sock` ließ sich nach dem Beleg nicht löschen, `rm` auf `/tmp` verweigert die Sandbox. Leere Datei, Modus 000, ohne Wirkung.
