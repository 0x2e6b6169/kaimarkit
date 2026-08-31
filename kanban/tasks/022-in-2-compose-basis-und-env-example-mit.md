---
id: 22
title: IN-2 · Compose-Basis und .env.example mit Quellenverweis ueber Variablen
status: todo
priority: high
created: 2026-08-31T10:21:37.944434653+02:00
updated: 2026-08-31T10:30:46.279488804+02:00
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
