---
id: 87
title: IN-16 · Der Traefik-Namensraum ist fest verdrahtet
status: todo
priority: medium
created: 2026-09-01T17:59:55.186651513+02:00
updated: 2026-09-01T17:59:55.186651513+02:00
assignee: akar
tags:
    - infra
class: standard
---

## Ziel

Zwei kaimarkit-Instanzen hinter derselben Traefik kollidieren nicht mehr in ihren Router-, Dienst- und Middlewarenamen.

## Befund (01.09.2026, vom Nutzer gemeldet)

Die Traefik-Namen stehen wörtlich in den Label-Schlüsseln:

    traefik.http.routers.kaimarkit.rule
    traefik.http.routers.kaimarkit-api.middlewares
    traefik.http.services.kaimarkit.loadbalancer.server.port
    traefik.http.middlewares.kaimarkit-auth.forwardauth.address

Diese Namen sind **global innerhalb einer Traefik-Instanz**. Wer zwei kaimarkit dahinter hängt — Produktion und Test, zwei Mandanten —, erzeugt zwei Definitionen desselben Routers. Traefik hat dann zwei Wahrheiten über einen Namen, und die Fehlersuche führt zuerst zu Traefik statt zu uns.

Nach außen ist bereits alles variabel: `KAIMARKIT_IMAGE`, `KAIMARKIT_CONTAINER_NAME`, `KAIMARKIT_PROJECT_NAME`, `KAIMARKIT_TAG`. Nur der Traefik-Namensraum fehlt.

## Entscheidung des Nutzers

Wörtlich: „Ja, genau so." — auf den Vorschlag: **eine Variable für den Traefik-Namensraum, Voreinstellung `kaimarkit`, aus der sich Router-, Dienst- und Middlewarename ableiten. Der Dienstschlüssel bleibt fest.**

**Der Dienstschlüssel `kaimarkit:` in der YAML wird ausdrücklich nicht angefasst.** Er ist der Bezeichner, unter dem die drei Compose-Dateien zusammengeführt werden, und der Name in jedem dokumentierten Befehl (`docker compose logs kaimarkit`, Makefile-Ziele, `docs/betrieb/`). Ihn variabel zu machen zöge alle diese Befehle mit und brächte nichts, was `KAIMARKIT_CONTAINER_NAME` nicht schon liefert.

## Zuerst prüfen, ob es überhaupt geht

**Compose muss in Label-*Schlüsseln* ersetzen, nicht nur in Werten.** Das ist die Annahme, auf der das ganze Ticket ruht, und sie ist ungeprüft. Erster Schritt: ein Minimalbeispiel mit `traefik.http.routers.${X}.rule` und `docker compose config` — steht dort der eingesetzte Name?

**Trifft die Annahme nicht zu, ist das Ticket hier zu Ende: melden und übergeben, nicht ausweichen.** Ein Ausweg über eine zweite Datei oder eine Erzeugung zur Laufzeit wäre ein anderer Entwurf und keine Umsetzung dieses Tickets.

## Eigene Dateien

- `docker/docker-compose.traefik.yml`
- `docker/docker-compose.authelia.yml`
- `docker/.env.example`
- `docs/betrieb/konfiguration.md` — Konvention 6: `.env.example` und diese Seite sind ein Paar, eine neue Variable gehört in beide
- `docs/betrieb/traefik.md`
- `docs/betrieb/authelia.md`

`docker/docker-compose.yml` bleibt unberührt; dort steht kein Traefik-Label.

## Vorgaben

Eine Variable, etwa `KAIMARKIT_TRAEFIK_NAME`, Voreinstellung `kaimarkit`. Daraus leiten sich ab:

- der Router: `${NAME}`
- der API-Router: `${NAME}-api`
- der Traefik-Dienst: `${NAME}`
- die eigene Middleware: `${NAME}-auth`

**Eine Stolperstelle, die benannt gehört:** `KAIMARKIT_MIDDLEWARES` steht seit IN-15 (#85) auf `authelia@docker` und ist davon unberührt. Wer aber auf die eigene Middleware umstellt, muss `${NAME}-auth@docker` eintragen — der Name folgt dann dem Namensraum. Ob sich das in `.env.example` als Verweis schreiben lässt oder nur als Satz erklären, ist am Gegenstand zu entscheiden; Verkettung von Variablen in einer `.env` ist nicht überall zuverlässig, also **prüfen statt annehmen**.

Die Dateien sind bewusst erklärend geschrieben. Wo ein Label durch die Variable schlechter lesbar wird, gehört ein Satz dazu, warum der Name variabel ist — sonst sieht es nach Verkomplizierung aus.

## Prüfung

- `docker compose -f … config` zeigt mit der Voreinstellung genau die heutigen Labelnamen. Nichts ändert sich für einen bestehenden Aufbau.
- Mit einem abweichenden Wert erscheinen Router, Dienst und Middleware unter dem neuen Namen — **an der Traefik-API abgelesen**, nicht aus der Datei geschlossen, wie in IN-15.
- Gegenprobe: Zwei Aufbauten mit verschiedenen Werten laufen nebeneinander an derselben Traefik, beide erreichbar unter ihrer eigenen Domain. Das ist der Fall, für den das Ticket existiert — ohne diesen Beleg ist es nicht erledigt.
- `docs/betrieb/konfiguration.md` nennt die neue Variable.
- `mkdocs build --strict` läuft durch.

## Randbedingung

**Der Dienst des Nutzers bleibt stehen.** Er arbeitet auf `127.0.0.1:8080`. Geprüft wird gegen einen eigenen Aufbau mit eigenem Projektnamen und eigenen Ports; kein `make up`, kein `make down` auf dem laufenden Container.
