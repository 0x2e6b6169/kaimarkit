---
id: 85
title: IN-15 · Eine vorhandene Authelia-Middleware laesst sich nicht verwenden
status: done
priority: medium
created: 2026-09-01T17:38:37.523949913+02:00
updated: 2026-09-01T17:55:39.069044442+02:00
started: 2026-09-01T17:55:32.574543233+02:00
completed: 2026-09-01T17:55:32.574543233+02:00
assignee: akar
tags:
    - infra
    - docs
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


---

## Umsetzung (akar-28, 01.09.2026)

Merge `7119c8f`, Commit `098e1f8`, Zweig `task/85-authelia-middleware`.

**Neue Variable: `KAIMARKIT_MIDDLEWARES`** — die Middlewareliste des Hauptrouters,
in derselben Form wie `KAIMARKIT_API_MIDDLEWARES`.

### Entscheidung des Nutzers vom 01.09.2026: die Voreinstellung ist umgedreht

Der Rumpf oben verlangte `kaimarkit-auth@docker` als Voreinstellung. Der Nutzer hat
das während der Umsetzung umgedreht, wörtlich: „Ich möchte meinen Weg gehen. Mit
`authelia@docker` als Standardwert, den ich überschreiben kann." Beide Router stehen
deshalb voreingestellt auf `authelia@docker`, auch `KAIMARKIT_API_MIDDLEWARES`. Die
eigene Middleware `kaimarkit-auth` bleibt definiert und ist der zweite Weg.

**Zweite Entscheidung, ebenfalls vom Nutzer und ebenfalls am 01.09.2026:**
„Rückwärtskompatibilität spielt keine Rolle und kann ignoriert werden." Ein zuvor
geschriebener Abschnitt „Umstieg von einer früheren Fassung" in
`docs/betrieb/authelia.md` ist daraufhin wieder entfernt worden. Dass sich der Wert
überschreiben lässt, steht weiterhin dort — aber als Wahl für den, dessen Authelia
nicht per Docker-Label beschriftet ist, nicht als Rückweg.

### Der Sicherheitsbefund: Traefik schließt bei Fehlkonfiguration

Die Abbruchbedingung war, ob ein Verweis auf eine nicht vorhandene Middleware den
Dienst ungeschützt ausliefert. Er tut es nicht. Gemessen mit Traefik 3.6.25, jedes
Mal an `/api/http/routers` abgelesen:

| Wert | Router | `/` |
| --- | --- | --- |
| `authelia@docker` | `enabled`, `["authelia@docker"]` | 401 |
| `kaimarkit-auth@docker` | `enabled`, `["kaimarkit-auth@docker"]` | 401 |
| `authelia@file` (fehlt) | `disabled`, `middleware "authelia@file" does not exist` | 404 |
| leer | `enabled`, keine Middleware | 200 |
| Variable fehlt ganz | `enabled`, `["authelia@docker"]` | 401 |

Die eigene Middleware mit leerer `AUTHELIA_VERIFY_URL` benutzt: 500, kein
Durchlassen. Auch das ist ein Schließen, kein Öffnen.

Die 401 stammt aus dem Messaufbau — an Authelias Stelle stand ein Dienst, der jede
Anfrage abweist. Eine echte Authelia antwortet dort mit 302.

### `${VAR-default}` statt `${VAR:-default}`

Der Vorgabewert steht in der Compose-Datei, nicht nur in `.env.example`. Ohne den
Bindestrich-Vorgabewert setzte Compose bei fehlender Variable still die leere
Zeichenkette ein — und leer heißt „keine Middleware". Der Doppelpunkt hätte auch den
ausdrücklich leeren Wert ersetzt und damit die Gegenprobe unmöglich gemacht.

### Auflage 2: `AUTHELIA_VERIFY_URL` darf leer bleiben

Nachgesehen, nicht vermutet. Die ungenutzte Definition mit leerer Adresse stand unter
`/api/http/middlewares` auf `enabled`, ohne Fehler und ohne Eintrag im Log. Die
Definition braucht deshalb keine Bedingung.

### Prüfaufbau

Wegwerf-Projekte `in15` und `in15proxy` im eigenen Netz `in15-web`, Traefik `v3.6`
(3.6.25) mit `--api.insecure`, an Authelias Stelle ein Container, der jede Anfrage
mit 401 beantwortet. Danach vollständig abgeräumt: Container, Netz, Volumes. Geholt
wurde kein Abbild — `traefik:v3.6` und `alpine:latest` lagen bereits vor. Der
Container `kaimarkit` des Nutzers lief durchgehend und meldete am Ende `healthy`.

`mkdocs build --strict` läuft durch.

### Befunde für den PO

- **Schnittfehler im Rumpf.** Unter „Eigene Dateien" standen drei Dateien;
  `docs/betrieb/konfiguration.md` fehlte, obwohl die Prüfung sie ausdrücklich
  verlangt und Konvention 6 sie ohnehin an `.env.example` bindet. Sie ist mit
  geändert worden.
- **`docs/betrieb/authelia.md` nennt weiter „Traefik 3.6.7"** an der Stelle, die aus
  IN-4 stammt (Abschnitt „Die API bleibt erreichbar"). Das ist eine fremde Messung
  und bleibt unangetastet; die Abweichung zur hier gemessenen 3.6.25 fällt aber auf,
  weil beide Zahlen auf einer Seite stehen. Das Abbild `traefik:v3.6` liefert heute
  3.6.25.
