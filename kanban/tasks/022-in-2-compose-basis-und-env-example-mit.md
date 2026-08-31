---
id: 22
title: IN-2 · Compose-Basis und .env.example mit Quellenverweis ueber Variablen
status: done
priority: high
created: 2026-08-31T10:21:37.944434653+02:00
updated: 2026-08-31T10:48:41.980253903+02:00
started: 2026-08-31T10:48:36.0194943+02:00
completed: 2026-08-31T10:48:36.0194943+02:00
assignee: akar
tags:
    - infra
depends_on:
    - 3
class: standard
---

## Ziel

Der lokale Betrieb, vollstaendig ueber `.env` gesteuert.

## Eigene Dateien

- `docker/docker-compose.yml`

## Vorgaben

- Top-Level `name: ${KAIMARKIT_PROJECT_NAME}`. Ohne das hiesse das Projekt
  "docker", weil Compose das Projektverzeichnis aus der ersten `-f`-Datei ableitet.
- `build.context: ${KAIMARKIT_BUILD_CONTEXT}` (Standard `..`) und
  `build.dockerfile: ${KAIMARKIT_DOCKERFILE}` (Standard `docker/Dockerfile`). Wer
  aus einem zweiten Checkout baut, setzt beide auf absolute Pfade - die
  Compose-Dateien bleiben unveraendert.
- Alle uebrigen Werte ebenfalls aus Variablen: image, tag, container_name, restart,
  Bindeadresse, Port, Speichergrenze.
- Healthcheck auf `/api/health` mit grosszuegigem `start_period` - Docling laedt
  beim Start.
- Kommentar in `.env.example`: Ein absoluter `context` verlangt ein `dockerfile`
  relativ zu genau diesem Kontext, und `.dockerignore` wird im Wurzelverzeichnis
  des dortigen Baums gesucht.

## Pruefung

`docker compose -f docker/docker-compose.yml config` loest jede Variable auf -
kein uebrig gebliebenes `${...}`, kein leerer Wert.


---

## Ergebnis (akar-02)

`docker/docker-compose.yml` angelegt. Top-Level-`name`, `build.context`,
`build.dockerfile`, `image:tag`, `container_name`, `restart`, Bindeadresse, Port,
`mem_limit` und alle Anwendungsvariablen kommen aus `KAIMARKIT_*`. `environment`
und `healthcheck` stehen in Map-Form, damit die Traefik- und Authelia-Schichten
einzelne Schluessel ersetzen statt anzuhaengen. Der Healthcheck ruft
`/api/health` ueber `python3 -c urllib.request` auf — `curl` ist im
Runtime-Image (`python:3.12-slim`) nicht zugesichert.

**Pruefung bestanden.** `docker compose -f docker/docker-compose.yml config`
loest jede Variable auf; `grep -nE '(\$\{|: *""$)'` ueber die Ausgabe findet
nichts. Zusaetzlich geprueft: mit `KAIMARKIT_BUILD_CONTEXT=/tmp` und
`KAIMARKIT_DOCKERFILE=/tmp/Dockerfile` uebernimmt Compose beide absoluten Pfade
unveraendert.

**Neue Variable — fuer DOC-3 (#27):** `KAIMARKIT_HEALTH_START_PERIOD=180s`. Sie
steht mit Kommentar in `docker/.env.example`, fehlt aber noch in
`docs/betrieb/konfiguration.md`; `docs/` gehoert derzeit DOC-1 (#20), deshalb
hier vermerkt statt dort eingetragen. Sonst wurde keine Variable geaendert.

Der in den Vorgaben geforderte Kommentar zu absolutem `context`,
`dockerfile`-Pfad und `.dockerignore` stand bereits aus SETUP-1 in
`.env.example` und blieb unveraendert.
