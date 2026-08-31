---
id: 24
title: 'IN-3 · Traefik-Ergaenzung: Labels in Map-Form, externes Netz, ports reset'
status: done
priority: medium
created: 2026-08-31T10:21:39.54608892+02:00
updated: 2026-08-31T10:53:58.429207137+02:00
started: 2026-08-31T10:53:57.710278675+02:00
completed: 2026-08-31T10:53:57.710278675+02:00
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

[[2026-08-31]] Mon 10:53
## Ergebnis

Umgesetzt in `docker/docker-compose.traefik.yml` (Merge 3b22fd9).

`ports: !reset []` nimmt die Veroeffentlichung der Basisdatei zurueck. Das Netz
`proxy` steht mit `external: true` und `name: ${TRAEFIK_NETWORK}` da,
`traefik.docker.network` ist gesetzt, die Labels stehen in Map-Form.

**Pruefung bestanden.** `docker compose -f docker/docker-compose.yml -f
docker/docker-compose.traefik.yml config` zeigt keinen einzigen Port, das externe
Netz `traefik-web` aus `.env` und alle Labels aufgeloest; `config -q` laeuft ohne
Fehler durch. Compose im Testsystem: v5.1.4.

**Keine neue Variable noetig.** IN-2 hatte den Traefik-Block in
`docker/.env.example` bereits vollstaendig angelegt: `TRAEFIK_NETWORK`,
`TRAEFIK_ENTRYPOINT`, `TRAEFIK_CERTRESOLVER`, `KAIMARKIT_DOMAIN`,
`KAIMARKIT_ROUTER`. Die Datei blieb unveraendert.

### Befund fuer IN-4 (#25), DOC-3 (#27) und IN-2 (#22)

`KAIMARKIT_ROUTER` laesst sich nicht einsetzen. Compose ersetzt Variablen nur in
Werten, nicht in Schluesseln. Ein Minimaltest belegt es: aus `prefix.${R}.suffix`
wird `prefix.$${R}.suffix`, waehrend der Wert derselben Zeile aufloest. Router-
und Servicename stehen deshalb woertlich als `kaimarkit` in den Labels; Domain,
Entrypoint, Certresolver und Netzname kommen weiter aus der Umgebung.

Die Listenform haette das geloest, bricht aber die Vorgabe der Map-Form, auf der
IN-4 aufsetzt. **IN-4 haengt sein Middleware-Label folglich an den Schluessel
`traefik.http.routers.kaimarkit.middlewares`.**

Ob `KAIMARKIT_ROUTER` in `.env.example` bleibt — dann mit dem Hinweis, dass eine
Umbenennung beide Compose-Schichten anfasst — oder entfaellt, entscheiden IN-2 und
DOC-3; ihnen gehoert die Datei.

Fuer `docs/betrieb/traefik.md` (DOC-3): `!reset` verlangt Compose 2.24 oder neuer.
Fehlt das im Zielsystem, nimmt man den Port aus der Basisdatei und veroeffentlicht
ihn in einer eigenen `docker-compose.local.yml`. Ein Hinweis darauf steht als
Kommentar in der Traefik-Datei.
