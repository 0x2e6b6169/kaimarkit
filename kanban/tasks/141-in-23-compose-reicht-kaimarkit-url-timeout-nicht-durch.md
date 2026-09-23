---
id: 141
title: IN-23 · Compose reicht KAIMARKIT_URL_TIMEOUT nicht in den Container
status: backlog
priority: medium
created: 2026-09-23T11:30:00+02:00
updated: 2026-09-23T11:30:00+02:00
assignee: akar
tags:
    - infra
class: standard
---

## Befund (2026-09-23, beim Abschluss von BE-42)

`docker/.env.example` führt `KAIMARKIT_URL_TIMEOUT=30`, und
`docs/admin/konfiguration.md` beschreibt die Variable. `docker/docker-compose.yml`
zählt unter `environment` aber jede Variable einzeln auf, und dort fehlt sie. Ein
Wert in `docker/.env` erreicht den Container deshalb nie; es gilt immer die
Vorgabe 30 aus `config.py`.

## Eigene Dateien

- `docker/docker-compose.yml`, Schlüssel `environment`

## Vorgaben

Eine Zeile `KAIMARKIT_URL_TIMEOUT: ${KAIMARKIT_URL_TIMEOUT}` neben den übrigen.
Dabei die ganze Liste gegen die `KAIMARKIT_*`-Einträge in `docker/.env.example`
abgleichen, die die Anwendung liest (`config.py`), damit keine weitere fehlt.

## Prüfung

- Rot vor grün: `KAIMARKIT_URL_TIMEOUT=7` in `docker/.env`, dann
  `docker compose -f docker/docker-compose.yml config | grep URL_TIMEOUT` —
  vorher keine Zeile, danach `KAIMARKIT_URL_TIMEOUT: "7"`.
