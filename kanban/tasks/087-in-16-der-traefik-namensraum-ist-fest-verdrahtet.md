---
id: 87
title: IN-16 · Der Traefik-Namensraum ist fest verdrahtet
status: done
priority: medium
created: 2026-09-01T17:59:55.186651513+02:00
updated: 2026-09-01T18:14:58.004013382+02:00
started: 2026-09-01T18:14:48.887496365+02:00
completed: 2026-09-01T18:14:48.887496365+02:00
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


---

## Erledigt (akar-29, 01.09.2026) — Merge aa6b7a8, Zweig task/87-traefik-namespace

### Die Machbarkeitsfrage: beide fruehere Aussagen stimmten, nur nicht zusammen

Compose setzt Variablen **nicht** in Label-Schluessel ein — der Vermerk aus dem
frueheren Lauf haelt stand. Gemessen mit Compose v5.1.4:

    labels:
      traefik.http.routers.${X}.rule: "..."     # Map-Form
    -> traefik.http.routers.$${X}.rule           # woertlich stehengeblieben

In der **Listenform** ist das ganze Label ein Wert, und dort greift die Ersetzung:

    labels:
      - "traefik.http.routers.${X}.rule=..."
    -> traefik.http.routers.zzznamespace.rule    # eingesetzt

Damit war die Frage, ob die Listenform den Grund fuer die Map-Form zerstoert. Der
stand woertlich in beiden Dateien: "Compose fuehrt Listen additiv zusammen — die
Authelia-Schicht koennte einen einzelnen Schluessel dann nicht mehr ersetzen."
**Fuer `labels` gilt das nicht.** Zwei Dateien, beide Listenform, ein Schluessel in
beiden:

    a.yml: - "traefik.http.routers.${X}.rule=Host(`a.test`)"
    b.yml: - "traefik.http.routers.${X}.rule=Host(`OVERRIDDEN`)"
    -> traefik.http.routers.ns.rule: Host(`OVERRIDDEN`)    # einmal, ersetzt

Compose macht aus der Liste beim Laden eine Map und fuehrt sie danach ueber die
Schluessel zusammen. Deshalb Listenform, kein zweiter Entwurf und keine zweite
Datei. Die alte Begruendung steht in beiden Compose-Dateien und in
`docs/betrieb/traefik.md` berichtigt, mit der Messung dazu.

### Umgesetzt

`KAIMARKIT_TRAEFIK_NAME`, Voreinstellung `kaimarkit`. Daraus: Router `${NAME}`,
API-Router `${NAME}-api`, Traefik-Dienst `${NAME}`, eigene Middleware
`${NAME}-auth`. Der Dienstschluessel `kaimarkit:` in der YAML blieb unangetastet,
`docker/docker-compose.yml` ebenso.

Im Label steht `${KAIMARKIT_TRAEFIK_NAME:-kaimarkit}`, mit Doppelpunkt — anders als
bei `KAIMARKIT_MIDDLEWARES` daneben. Dort heisst ein ausdruecklich leerer Wert
"keine Middleware" und muss leer bleiben; hier ergaebe er `traefik.http.routers..rule`.
Der Doppelpunkt faengt beide Faelle ab, die fehlende und die leere Variable. Damit
laeuft ein `docker/.env` aus der Zeit vor dieser Variablen unveraendert weiter —
nachgewiesen: Die erste Messung unten lief gegen eine `.env`, die die neue Variable
noch gar nicht enthielt.

### Die Stolperstelle KAIMARKIT_MIDDLEWARES — am Gegenstand geprueft

Verkettung in der `.env` funktioniert, aber nur vorwaerts:

    X=probe                    MW=${X}-auth@docker
    MW=${X}-auth@docker        X=probe
    -> probe-auth@docker       -> -auth@docker  (nur eine Warnung, kein Abbruch)

In `.env.example` steht die Traefik-Gruppe vor der Authelia-Gruppe, die Reihenfolge
stimmt also von selbst. Beides steht als Verweis **und** als Satz in
`.env.example` und in `docs/betrieb/authelia.md`, samt der Bedingung.

### Pruefung — alle fuenf Punkte

1. **Voreinstellung aendert nichts.** `docker compose config` ueber alle drei Dateien,
   die 19 Labelzeilen vor und nach der Aenderung diff-gleich. Zweimal gelaufen: gegen
   die alte `.env.example` (ohne die Variable) und gegen die neue.
2. **Abweichender Wert, an der Traefik-API abgelesen.** Wegwerf-Traefik 3.6.25
   (`in16-traefik`, eigenes Netz `in16-web`, API auf 127.0.0.1:18080, websecure auf
   127.0.0.1:18443), zwei Instanzen `in16-a` und `in16-b` aus den Repo-Dateien mit
   `--no-build` auf `kaimarkit:local`:

   - `/api/http/routers`: `in16-a@docker`, `in16-a-api@docker`, `in16-b@docker`,
     `in16-b-api@docker` — alle vier `enabled`, kein `error`.
   - `/api/http/services`: `in16-a@docker` -> `http://172.21.0.3:8000`,
     `in16-b@docker` -> `http://172.21.0.4:8000`.
   - `/api/http/middlewares`: `in16-a-auth@docker` und `in16-b-auth@docker`, beide
     `enabled`.
3. **Gegenprobe, zwei Aufbauten nebeneinander.** Beide unter ihrer eigenen Domain
   erreichbar, und jede Antwort kam aus dem eigenen Container — die Instanzen liefen
   mit `KAIMARKIT_MAX_FILE_SIZE_MB=11` und `=22`:

   | Aufruf | Antwort |
   |---|---|
   | `https://a.in16.test/api/capabilities` | `max_file_size_mb: 11` |
   | `https://b.in16.test/api/capabilities` | `max_file_size_mb: 22` |
   | `https://a.in16.test/` und `https://b.in16.test/` | je 200 |
   | `https://x.in16.test/` (unbekannt) | 404 |

   **Der Kollisionsfall gegengemessen:** Beide Aufbauten auf denselben
   `KAIMARKIT_TRAEFIK_NAME` gestellt, Domains verschieden gelassen. Danach fuehrte
   `/api/http/routers` keinen der Router mehr auf, **beide** Domains antworteten mit
   404, und im Traefik-Log stand `Router defined multiple times with different
   configurations` mit den Namen beider Container. Nach Rueckstellung auf
   verschiedene Werte liefen beide wieder mit 200. Das ist genau der Schaden, gegen
   den das Ticket geschrieben ist.
4. **`docs/betrieb/konfiguration.md` nennt die Variable** — neue Zeile in der
   Traefik-Tabelle, dazu der Hinweis, dass der Compose-Dienst `kaimarkit` bleibt.
5. **`mkdocs build --strict`** laeuft durch, ohne Warnung.

### Aufraeumen und Randbedingung

Beide Instanzen, der Wegwerf-Traefik und das Netz `in16-web` sind entfernt
(`docker compose down -v --remove-orphans`, `docker rm -f`, `docker network rm`).
`docker/.env` des Nutzers wurde nie angefasst; im Worktree lag eine eigene Kopie,
die Testlaeufe liefen ueber `--env-file` aus dem Scratchpad. Der Container
`kaimarkit` des Nutzers lief waehrend der ganzen Arbeit auf 127.0.0.1:8080 durch und
meldet `healthy`.

### Befund nebenbei, nicht geaendert

`docker/docker-compose.yml` (Zeilen 25-27, Kommentar ueber `environment:`) begruendet
die Map-Form dort mit derselben Aussage — "Compose fuehrt Listen additiv zusammen,
Maps ersetzen einzelne Schluessel". Fuer `environment` ist die Map-Form weiterhin
richtig, und die Datei gehoert diesem Ticket nicht. Wer sie das naechste Mal anfasst,
koennte den Satz praeziser fassen: Compose normalisiert auch `environment` beim Laden
zur Map. Die Wahl der Form aendert das nicht, die Begruendung schon.
