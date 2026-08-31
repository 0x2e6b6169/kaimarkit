---
id: 24
title: 'IN-3 · Traefik-Ergaenzung: Labels in Map-Form, externes Netz, ports reset'
status: todo
priority: medium
created: 2026-08-31T10:21:39.54608892+02:00
updated: 2026-08-31T10:30:46.281977744+02:00
assignee: akar
tags:
    - infra
depends_on:
    - 22
class: standard
---

## Ziel

Betrieb hinter dem Traefik-Proxy, ergaenzend zur Basisdatei.

## Eigene Dateien

- `docker/docker-compose.traefik.yml`

## Vorgaben

- **Labels in Map-Form, nicht als Liste.** Compose fuehrt Listen additiv zusammen;
  die Authelia-Schicht koennte das `middlewares`-Label sonst nicht setzen.
- `ports: !reset []` nimmt die Veroeffentlichung aus der Basisdatei zurueck. Das
  verlangt Compose 2.24 oder neuer - die Anforderung gehoert in
  `docs/betrieb/traefik.md`. Falls sie im Zielsystem fehlt, veroeffentlicht
  stattdessen eine `docker-compose.local.yml` den Port und die Basisdatei keinen.
- Jeder Wert aus `.env`, auch der Netzname:
  `networks.proxy.name: ${TRAEFIK_NETWORK}` mit `external: true`.
- Router-, Domain-, Entrypoint- und Certresolver-Namen ebenfalls aus Variablen.
- `traefik.docker.network` setzen - ohne das waehlt Traefik bei mehreren Netzen
  unter Umstaenden das falsche.

## Pruefung

`docker compose -f docker/docker-compose.yml -f docker/docker-compose.traefik.yml
config` zeigt keine veroeffentlichten Ports, das externe Netz mit dem Namen aus
`.env` und alle Labels aufgeloest.
