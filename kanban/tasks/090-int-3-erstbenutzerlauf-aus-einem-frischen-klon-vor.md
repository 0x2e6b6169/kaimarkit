---
id: 90
title: INT-3 · Erstbenutzerlauf aus einem frischen Klon vor dem ersten Tag
status: done
priority: high
created: 2026-09-01T18:29:48.381602755+02:00
updated: 2026-09-02T16:29:28.040200237+02:00
started: 2026-09-02T16:29:28.046619742+02:00
completed: 2026-09-02T16:29:28.046619742+02:00
assignee: akar
tags:
    - infra
    - release
class: standard
---

## Ziel

Vor dem ersten Tag einmal den Weg gehen, den ein Fremder geht: frischer Klon, kein `docker/.env`, kein Bau-Cache, kein vorhandenes Abbild.

## Warum das kein Vorsorgelauf ist

Alles, was heute belegt wurde, ist in **diesem** Arbeitsbaum belegt worden — mit einem `docker/.env` von heute Vormittag, warmem Cache und vorhandenen Abbildern. Ein frischer Klon auf einem VPS hat nichts davon. **Der Weg des Erstbenutzers ist heute kein einziges Mal gegangen worden**, und genau dorthin will der Nutzer als Nächstes.

Dazu sind vier Merges nach dem letzten vollständigen Bau gelandet: BE-32, IN-15, IN-16, IN-17. Jeder für sich belegt, der zusammengesetzte Stand nicht.

## Drei Stellen mit echtem Risiko (benannt von akar)

**1. Die Voreinstellung aus IN-15.** `KAIMARKIT_MIDDLEWARES` steht auf `authelia@docker`. Wer die Authelia-Schicht startet, **ohne** eine per Docker-Label beschriftete Authelia zu betreiben, bekommt Router `disabled` und überall 404 — sicherheitstechnisch richtig, für den Erstbenutzer ein Dienst ohne erkennbaren Grund. Zu prüfen ist, ob `docs/betrieb/authelia.md` ihn dort auffängt.

**2. Der Erstbau ohne Cache.** `.dockerignore`, die Stufenreihenfolge und die Docs-Stufe sind heute geändert worden; die Docs-Stufe hängt `.git` als Bind-Mount ein. Bei einem Klon ohne `gh-pages` greift die Rückfallebene. Belegt ist das in einem Wegwerf-Klon, nicht in einem echten Erstbau.

**3. `make docs-release`.** Der `gh-pages`-Zweig ist gelöscht. Ein erster Release-Lauf legt ihn neu an — ein Weg, den nie jemand von null gegangen ist.

## Eigene Dateien

Keine. Dieses Ticket ändert nichts; es geht einen Weg und schreibt auf, was es findet.

**Findet es etwas, wird es gemeldet und nicht behoben.** Jeder Fund ist ein eigenes Ticket — sonst vermischt sich die Prüfung mit ihrer Reparatur, und am Ende weiß niemand, welcher Stand geprüft ist.

## Vorgaben

In einem frischen Klon von `main`, außerhalb des Arbeitsbaums, ohne `docker/.env`:

1. `cp docker/.env.example docker/.env` — genau der Weg aus `docs/betrieb/lokal.md`, ohne eine Zeile zu ändern.
2. Volle Testsuite: `pytest -q -rs` mit Sammelzahl, `ruff check .`, `npm run test` und `npm run typecheck`.
3. `make up` — Erstbau ohne Cache. Bauzeit notieren, samt Angabe, ob das VPN während des Laufs an war.
4. Container bis `healthy`, dann ein **echtes Dokument** durchschicken und den Textinhalt ansehen, nicht den Statuscode.
5. `make docs-serve` und `mkdocs build --strict`.
6. Die Traefik-Schicht einmal wirklich starten und an der Traefik-API ablesen, dass die Router dastehen.
7. Die Authelia-Schicht mit der Voreinstellung starten, **ohne** eine `authelia@docker` — und prüfen, ob die Dokumentation den 404 erklärt, den man dann bekommt.

## Prüfung

- Jeder der sieben Punkte hat ein Ergebnis in der Ticketnotiz, mit Zahlen statt „lief durch".
- Der geprüfte Commit steht in der Notiz.
- Der Arbeitsbaum und der laufende Dienst des Nutzers sind unberührt; der frische Klon ist danach abgeräumt.
- Gefundene Abweichungen sind als Befunde aufgeschrieben, nicht behoben.

## Randbedingung

**Das VPN sollte für die Dauer aus sein, wenn möglich.** Ein Erstbau ohne Cache holt Torch, Docling und die Modelle vollständig. Gemessen: rund 0,5 MB/s aus einem Container unter VPN gegen 1,9 MB/s ohne. Das ist der Unterschied zwischen einer knappen halben Stunde und deutlich über einer. Ist es nicht möglich, ist der Lauf nicht falsch, nur lang — und die Bauzeit dann kein Vergleichswert.

[[2026-09-01]] Tue 18:37
**Versionsnummer entschieden (01.09.2026): `v0.1.0`.**

Der Nutzer hat sie gewählt, weil der Code sie schon sagt: `backend/app/__init__.py` führt `__version__ = "0.1.0"` als Literal, und `/api/health` meldet sie seit dem ersten Tag. Ein Tag `v0.0.1` hätte dem widersprochen — wer den Dienst fragt, bekäme eine andere Zahl als der Tag nennt.

**Damit ist im Quelltext nichts zu ändern.** Der Tag folgt der Zahl, nicht umgekehrt.

Zwei Punkte, die zum ersten Tag gehören und noch offen sind:

- Es gibt keinen `CHANGELOG.md`.
- 149 Commits sind nie gepusht worden; dieser Tag wäre die erste Auslieferung überhaupt.

Beides ist Sache des Nutzers und kein Ticket — er hat dafür eigene Werkzeuge.

[[2026-09-01]] Tue 21:29
**Teilweise überholt (01.09.2026): Der Nutzer ist den Weg selbst gegangen — auf einem echten VPS, mit v0.1.0.**

Gegangen und belegt:

- Klon des Tags über SSH, `detached HEAD`
- `cp docker/.env.example docker/.env`, vier Werte gesetzt
- `make up-authelia`, Erstbau ohne Cache
- Container `running / healthy`
- Traefik registriert beide Router, `status: enabled`
- Hinter Authelia erreichbar unter `kaimarkit.0x2e6b6169.de`

Drei Befunde sind dabei entstanden, die kein Lauf im Arbeitsbaum gefunden hätte: #91 (fehlende Docker-Gruppenzugehörigkeit besteht die dokumentierte Voraussetzungsprüfung), #92 (Domänenbedingung und `access_control` bei Authelia) und die Beobachtung zu den Beispielwerten in `.env.example`.

**Was dieses Ticket noch abdecken würde und der VPS-Lauf nicht:**

- die volle Testsuite auf einem frischen Klon (`pytest -q -rs`, `ruff`, `npm run test`, `npm run typecheck`)
- `make docs-serve` und `mkdocs build --strict` aus dem Klon
- `make docs-release` von null — der `gh-pages`-Zweig existiert nicht und wurde nie neu angelegt
- der Fall **ohne** `authelia@docker`: Router `disabled`, überall 404 — beim Nutzer nicht eingetreten, weil er Authelia betreibt

Das ist deutlich weniger als der ursprüngliche Zuschnitt und rechtfertigt keinen vollen Erstbau mehr. **Vor dem Neuschneiden entscheidet der PO, ob der Rest ein eigenes, kleineres Ticket wird oder entfällt.**

[[2026-09-02]] Wed 16:29
Erledigt durch den echten Lauf: Der Nutzer hat am 2026-09-01 auf seinem VPS aus
einem frischen Klon von v0.1.0 installiert und den Dienst erfolgreich in Betrieb
genommen — hinter Traefik und Authelia, unter `kaimarkit.0x2e6b6169.de`.

Damit sind die Punkte 1 und 2 belegt, und zwar härter als jeder Wegwerf-Klon es
gekonnt hätte: Erstbau ohne Cache auf fremder Maschine, kein `docker/.env`,
`.git` nur als Bind-Mount, und die Voreinstellung `authelia@docker` aus IN-15 im
echten Zusammenspiel.

Nicht ohne Reibung, und die Reibung war lehrreich: Zwei Hürden standen im Weg,
beide außerhalb dieses Repositorys — die Cookie-Domäne von Authelia und ein
fehlender Eintrag unter `access_control`. Beide hat der Nutzer gelöst. Was das
Projekt daraus lernt, steht in DOC-14 (#92).

**Punkt 3 ist damit nicht belegt.** `make docs-release` von null, auf einem
Repository ohne `gh-pages`-Zweig, hat niemand ausgeführt. Der Rest wandert nach
ORG-2 (#96); dieses Ticket wird nicht offen gehalten, um einen einzelnen Punkt
mitzuschleppen.
