---
id: 50
title: 'IN-9 · Abnahmefassung: laufender Dienst, im Browser des Hosts pruefbar'
status: in-progress
priority: high
created: 2026-09-01T08:52:15.226215349+02:00
updated: 2026-09-01T08:55:14.66329185+02:00
assignee: akar
tags:
    - infra
    - release
claimed_by: akar-21
claimed_at: 2026-09-01T08:55:14.66329185+02:00
class: standard
---

## Ziel

Der Nutzer soll kaimarkit auf seinem Rechner starten und im Browser des
Windows-Hosts bedienen koennen. Heute ist der Dienst nur aus WSL heraus geprueft.

## Ausgangslage

INT-2 (#30) hat den Container Ende zu Ende geprueft — mit `curl` aus WSL. Das
belegt den Container, nicht den Weg dorthin. Zwei Annahmen stehen dazwischen und
sind nie geprueft worden:

- `KAIMARKIT_BIND_ADDR` steht auf `127.0.0.1`. Ob Docker Desktop einen so
  gebundenen Port an Windows weiterreicht, hat hier noch niemand nachgesehen.
- Die Oberfläche kommt aus derselben Herkunft wie die API. Ein Browser prueft
  Dinge, die `curl` nicht prueft.

## Eigene Dateien

- `docs/betrieb/lokal.md` (Abschnitt "Docker Desktop unter Windows", neu)

Sonst nichts. `docker/Dockerfile` gehoert IN-8 (#45): Wer beim Bauen auf einen
Fehler stoesst, meldet ihn, statt ihn hier zu beheben.

## Vorgaben

Aus dem **Haupt-Checkout** auf dem Stand von `main` bauen und starten
(`cp docker/.env.example docker/.env`, `make up`), bis
`docker inspect -f '{{.State.Health.Status}}' kaimarkit` `healthy` meldet.

Am Gegenstand pruefen, nicht am Werkzeug: den Textinhalt der Antworten ansehen,
nicht den Statuscode.

Was der Weg ueber Docker Desktop zusaetzlich verlangt, gehoert als eigener
Abschnitt nach `docs/betrieb/lokal.md` — Bindeadresse, Port, unter welcher Adresse
die Oberfläche im Browser des Hosts erscheint. Verlangt er nichts weiter, sagt der
Abschnitt genau das in zwei Saetzen.

Die letzte Meile geht der Nutzer: Ein Subagent in WSL kann keinen Browser unter
Windows bedienen. Deshalb endet dieses Ticket auf `review`, nicht auf `done`, und
die Ticketnotiz enthaelt eine kurze Abnahmeliste — die Adresse und drei Handgriffe,
die der Nutzer nacheinander macht.

Was dabei auffaellt, wird gemeldet und nicht behoben. Daraus schneidet der PO
Tickets.

## Pruefung

- Der Container meldet `healthy`.
- `curl -sf localhost:8080/` liefert das HTML der Oberfläche, nicht nur einen
  Statuscode; `curl -sf localhost:8080/api/capabilities` nennt alle drei Engines.
- Eine Umwandlung von der Kommandozeile liefert sichtbaren Text: das Ergebnis
  enthaelt Woerter aus der Vorlage, nicht nur eine leere Antwort.
- `docs/betrieb/lokal.md` hat den neuen Abschnitt.
- Das Ticket steht auf `review`, der Container laeuft weiter, und die Notiz nennt
  die Adresse und die Abnahmeliste fuer den Nutzer.
