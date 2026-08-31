---
id: 25
title: 'IN-4 · Authelia-Ergaenzung: ForwardAuth-Middleware und API-Router'
status: done
priority: medium
created: 2026-08-31T10:21:40.305443953+02:00
updated: 2026-08-31T11:04:10.397001718+02:00
started: 2026-08-31T11:03:26.582344229+02:00
completed: 2026-08-31T11:03:26.582344229+02:00
assignee: akar
tags:
    - infra
depends_on:
    - 24
class: standard
---

## Ziel

Zugriffsschutz ueber Authelia, ohne die API unbenutzbar zu machen.

## Eigene Dateien

- `docker/docker-compose.authelia.yml`

## Vorgaben

- Die Datei definiert die ForwardAuth-Middleware am eigenen Service, damit sie fuer
  sich steht: `forwardauth.address`, `trustForwardHeader: true`,
  `authResponseHeaders` - alles aus `.env`.
- **Der Punkt, um den es hier geht:** Hinter Authelia ist auch `/api` geschuetzt,
  und ein `curl` ohne Browser-Sitzung bekommt eine Weiterleitung zum Login. Deshalb
  ein zweiter Router fuer `PathPrefix('/api')` mit hoeherer Prioritaet, dessen
  Middleware-Liste aus `${KAIMARKIT_API_MIDDLEWARES}` kommt.
- **Offene Frage, die dieses Ticket klaert:** Akzeptiert Traefik einen leeren Wert
  in `middlewares=` als "keine Middleware"? Falls ja, genuegt eine leere Variable,
  um die API freizugeben. Falls nein, kommt der Block auskommentiert samt
  Erklaerung in die Datei. Das Ergebnis gehoert nach `docs/betrieb/authelia.md`
  (Ticket DOC-3).

## Pruefung

Mit allen drei Dateien: `docker compose ... config` loest beide Router auf. Gegen
eine laufende Authelia-Instanz: Der Browser wird zum Login geleitet; mit
freigegebener API antwortet `curl -F file=@a.pdf .../api/convert` ohne Anmeldung.

## Ergebnis (akar-06)

Gebaut: `docker/docker-compose.authelia.yml` als dritte Schicht. Merge 6c017fd.

**Die offene Frage ist beantwortet: ja.** Traefik nimmt einen leeren
`middlewares=`-Wert als "keine Middleware" an. Der Router bleibt auf
`enabled`, die Middlewareliste ist leer, es gibt keinen Fehler. Eine leere
Variable genuegt also, um die API freizugeben; der auskommentierte Block
entfaellt. Geprueft mit Traefik 3.6.7 gegen eine laufende Instanz. Fuer
DOC-3 (#27), `docs/betrieb/authelia.md`.

### Pruefung, tatsaechliches Ergebnis

1. `docker compose -f docker-compose.yml -f docker-compose.traefik.yml -f docker-compose.authelia.yml config`
   loest beide Router auf: `kaimarkit` (Host-Regel, Middleware
   `kaimarkit-auth@docker`) und `kaimarkit-api` (`Host() && PathPrefix('/api')`,
   Prioritaet 100, Dienst `kaimarkit`). Die Map-Form der Labels merged wie
   erwartet — die Traefik-Schicht bleibt unveraendert, meine Schluessel kommen
   dazu.
2. Laufzeitprobe mit den drei echten Dateien gegen ein lokales Traefik 3.6.7,
   Anwendungsimage per Wegwerf-Override durch `traefik/whoami` ersetzt,
   `AUTHELIA_VERIFY_URL` auf einen nicht erreichbaren Host gesetzt:
   - Vorgabe (`KAIMARKIT_API_MIDDLEWARES=kaimarkit-auth@docker`):
     `/` und `/api/health` beide 500 — die ForwardAuth greift auf beiden Routern.
   - Leere Variable: `/` weiterhin 500, `/api/health` 200,
     `curl -F file=@a.txt .../api/convert` 200. Genau der Fall aus der Pruefung.

**Nicht ausgefuehrt:** die Login-Weiterleitung im Browser gegen ein echtes
Authelia. Kein Authelia-Image vorhanden und kein Netz zum Nachladen. Die
unerreichbare ForwardAuth-Adresse belegt, dass die Middleware haengt und laeuft;
die Anmeldemaske selbst gehoert nach INT-2 (#30).

### Keine neuen Variablen

`.env.example` blieb unangetastet. IN-2 hatte den Authelia-Block bereits
angelegt; die Datei verbraucht daraus `AUTHELIA_VERIFY_URL`,
`AUTHELIA_RESPONSE_HEADERS` und `KAIMARKIT_API_MIDDLEWARES`.

**Fuer DOC-3:** `AUTH_MIDDLEWARE=kaimarkit-auth` wird von nichts mehr gelesen —
dasselbe Schicksal wie `KAIMARKIT_ROUTER`. Grund ist der Befund aus IN-3:
Compose setzt Variablen nur in Label-*Werte* ein, nie in Label-*Schluessel*. Der
Middlewarename steht im Schluessel
(`traefik.http.middlewares.kaimarkit-auth.forwardauth.address`) und muss deshalb
woertlich dastehen, genau wie der Routername in der Traefik-Schicht. Ich habe die
Variable nicht geloescht.

### Kein Eingriff in den Schnittstellen-Dreiklang

"API-Router" im Titel meint den Traefik-Router fuer `PathPrefix('/api')`, nicht
den FastAPI-Router. `contracts/api.md`, `backend/app/models.py` und
`frontend/src/types.ts` bleiben unberuehrt.

### Nebenbefund

Traefik verwirft beide Router stillschweigend, wenn ein zweiter Container auf
demselben Host Router gleichen Namens mit anderer Konfiguration meldet
("Router defined multiple times"). Der Routername muss hostweit eindeutig sein —
das steht so schon in der Traefik-Schicht und gilt fuer `kaimarkit-api` genauso.
