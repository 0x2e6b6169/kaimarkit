---
id: 88
title: IN-17 · Drei Kommentare in den Compose-Dateien sagen Falsches
status: todo
priority: medium
created: 2026-09-01T18:16:39.541396522+02:00
updated: 2026-09-01T18:16:39.541396522+02:00
assignee: akar
tags:
    - infra
    - docs
class: standard
---

## Befund (01.09.2026, drei Meldungen aus IN-16)

Drei Stellen in den Compose-Dateien sagen etwas Falsches oder verschweigen etwas, das man beim nächsten Anfassen wissen muss. Alle drei kommen aus dem, was IN-16 (#87) nachgemessen hat.

### 1. Eine Begründung, die widerlegt ist

`docker/docker-compose.yml`, Zeilen 25–27, begründet die Map-Form für `environment` so: „Compose führt Listen additiv zusammen, Maps ersetzen einzelne Schlüssel."

Für `labels` **stimmt das nicht** — IN-16 hat gemessen, dass Compose eine Label-Liste beim Laden zur Map normalisiert und über die Schlüssel zusammenführt. Dieselbe Aussage steht auch auf den Traefik-Seiten und hat dort seit IN-3 (#24) den Verzicht auf die Listenform begründet.

**Die Map-Form für `environment` bleibt trotzdem richtig** — lesbarer, und eine Ergänzungsdatei überschreibt einen einzelnen Schlüssel sichtbar. Nur die Begründung ist es nicht.

**Erst messen, dann schreiben:** Ob Compose auch `environment`-Listen zur Map normalisiert, ist ungeprüft. Die neue Begründung muss zu dem passen, was gemessen wurde, nicht zu dem, was plausibel klingt.

### 2. Zwei Formen nebeneinander, beide richtig

Seit IN-16 stehen in der Traefik-Schicht zwei Zeilen mit verschiedener Ersetzungsform:

    ${KAIMARKIT_TRAEFIK_NAME:-kaimarkit}    mit Doppelpunkt
    ${KAIMARKIT_MIDDLEWARES}                ohne

Der Unterschied ist beabsichtigt: Ein leerer Namensraum ergäbe `traefik.http.routers..rule` — unbrauchbar, deshalb greift die Voreinstellung auch bei leerem Wert. Ein leeres `KAIMARKIT_MIDDLEWARES` ist dagegen eine **gültige Angabe**: „keine Middleware", der dokumentierte Weg für ein `curl` ohne Browsersitzung.

Ohne einen Satz dazu sieht es nach Unachtsamkeit aus, und jemand vereinheitlicht es — und nimmt damit den einen Weg weg, den `docs/betrieb/authelia.md` ausdrücklich beschreibt.

### 3. Eine Falle beim Umsortieren

Verkettung in der `.env` funktioniert **nur vorwärts**: Steht die referenzierte Variable weiter unten, setzt Compose still eine leere Zeichenkette ein und warnt bloß. In `docker/.env.example` stimmt die Reihenfolge heute. Wer die Datei umsortiert, merkt den Bruch nicht.

## Eigene Dateien

- `docker/docker-compose.yml` (Kommentar bei `environment`)
- `docker/docker-compose.traefik.yml` (Kommentar bei den beiden Ersetzungsformen)
- `docker/.env.example` (Hinweis zur Reihenfolge)
- `docs/betrieb/traefik.md`, falls die widerlegte Aussage dort ebenfalls steht

## Vorgaben

Kein Verhalten ändern. Es geht ausschließlich um Kommentare und Dokumentation.

Zu 1: Die widerlegte Aussage kommt weg. Was an ihre Stelle tritt, richtet sich nach der Messung — steht die Begründung für `environment` nach der Prüfung ohne Stütze da, ist „Map-Form, weil lesbarer und weil eine Ergänzung sichtbar einen Schlüssel ersetzt" ehrlicher als eine neue technische Behauptung.

Zu 2: Ein Satz, der beide Formen nebeneinander erklärt und sagt, warum sie verschieden bleiben müssen.

Zu 3: Ein Satz am Kopf von `.env.example`.

## Prüfung

- Keine Datei behauptet mehr, Compose führe Label-Listen additiv zusammen.
- Der Satz zu den zwei Ersetzungsformen nennt beide Gründe und macht klar, dass das Vereinheitlichen einen dokumentierten Weg zerstört.
- `docker compose -f … config` liefert vor und nach dem Ticket dieselbe Ausgabe — es hat sich nichts als Kommentare geändert. Das ist die Prüfung, dass kein Verhalten mitgegangen ist.
- `mkdocs build --strict` läuft durch.
