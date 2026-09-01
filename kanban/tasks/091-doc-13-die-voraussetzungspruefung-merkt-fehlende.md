---
id: 91
title: DOC-13 · Die Voraussetzungspruefung merkt fehlende Docker-Rechte nicht
status: backlog
priority: medium
created: 2026-09-01T18:40:51.760156559+02:00
updated: 2026-09-01T18:40:51.760156559+02:00
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
