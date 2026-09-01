---
id: 85
title: IN-15 · Eine vorhandene Authelia-Middleware laesst sich nicht verwenden
status: in-progress
priority: medium
created: 2026-09-01T17:38:37.523949913+02:00
updated: 2026-09-01T17:41:03.265084308+02:00
assignee: akar
tags:
    - infra
    - docs
claimed_by: akar-28
claimed_at: 2026-09-01T17:41:03.265084308+02:00
class: standard
---

## Befund (01.09.2026, vom Nutzer aus seinem eigenen Aufbau gemeldet)

Der Nutzer betreibt Authelia bereits und schaltet sie so vor einen Dienst:

    traefik.http.routers.whoami-secure.middlewares: "authelia@docker"

Das ist der übliche Weg: Die Authelia-Instanz definiert ihre ForwardAuth-Middleware
an sich selbst, und jeder geschützte Dienst verweist nur darauf.

**Unsere Schicht kann das nicht nutzen.** `docker-compose.authelia.yml` definiert eine
**eigene** Middleware `kaimarkit-auth` über `${AUTHELIA_VERIFY_URL}` und schreibt sie
in Zeile 41 fest an den Router:

    traefik.http.routers.kaimarkit.middlewares: kaimarkit-auth@docker

Wer eine funktionierende `authelia@docker` hat, muss also trotzdem
`AUTHELIA_VERIFY_URL` und `AUTHELIA_RESPONSE_HEADERS` ein zweites Mal richtig
setzen — mitsamt dem `rd=`-Parameter, an dem sich leicht etwas verdreht. Oder er
ändert die Compose-Datei, was sie zu seiner Datei macht.

Bezeichnend: Für den `/api`-Router **ist** die Middlewareliste konfigurierbar
(`KAIMARKIT_API_MIDDLEWARES`). Für den Hauptrouter nicht. Der Schalter existiert
bereits, nur an der falschen Hälfte.

## Ziel

Wer Authelia schon betreibt, verweist auf seine vorhandene Middleware und setzt
nichts doppelt.

## Eigene Dateien

- `docker/docker-compose.authelia.yml`
- `docker/.env.example`
- `docs/betrieb/authelia.md`

Konvention 6 gilt: `.env.example` und `docs/betrieb/konfiguration.md` sind ein Paar —
kommt dort eine Variable hinzu, gehört sie in beide.

## Vorgaben

Die Middlewareliste des Hauptrouters wird eine Variable, in derselben Form wie
`KAIMARKIT_API_MIDDLEWARES`. Voreinstellung bleibt `kaimarkit-auth@docker`, damit
sich für bestehende Aufbauten nichts ändert.

Wer `authelia@docker` einträgt, braucht `AUTHELIA_VERIFY_URL` und
`AUTHELIA_RESPONSE_HEADERS` dann nicht mehr. **Das gehört in der Dokumentation
zusammen erklärt** — als zwei Wege mit ihren Bedingungen, nicht als Schalter ohne
Zusammenhang:

- **eigene Middleware** (Voreinstellung): funktioniert unabhängig davon, wie die
  vorhandene Authelia beschriftet ist; verlangt die zwei Variablen.
- **vorhandene Middleware**: nichts doppelt zu setzen; verlangt, dass sie wirklich
  `@docker` heißt und nicht `@file`, und dass sie dieselben Response-Header
  durchreicht.

Die Definition der eigenen Middleware bleibt stehen — sie wird nur nicht mehr
zwingend benutzt.

## Prüfung

- Mit der Voreinstellung verhält sich alles wie bisher; die Prüfung aus IN-4 (#25)
  läuft unverändert durch.
- Mit `authelia@docker` als Wert erscheint der Router in Traefik mit genau dieser
  Middleware — an der Traefik-API abgelesen, nicht aus der Datei geschlossen.
- Gegenprobe: Ein leerer Wert lässt den Router **ohne** Schutz laufen; das ist in
  `docs/betrieb/authelia.md` bereits für `/api` beschrieben und gilt hier genauso —
  der Hinweis gehört an beide Stellen.
- `docs/betrieb/konfiguration.md` nennt die neue Variable.
