---
id: 25
title: 'IN-4 · Authelia-Ergaenzung: ForwardAuth-Middleware und API-Router'
status: todo
priority: medium
created: 2026-08-31T10:21:40.305443953+02:00
updated: 2026-08-31T10:30:46.282699558+02:00
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
