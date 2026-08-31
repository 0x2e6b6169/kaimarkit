# Lokaler Betrieb

Der kürzeste Weg zum laufenden Dienst: ein Container, ein veröffentlichter Port,
kein Reverse Proxy davor. Für einen Rechner unter dem Schreibtisch reicht das.

## Was vorher da sein muss

Docker Engine mit dem Compose-Plugin (`docker compose version` muss antworten) und
etwa 6 GB freier Arbeitsspeicher — so viel gibt `KAIMARKIT_MEM_LIMIT` dem Container.
Der erste Bau backt die Docling-Modelle in das Abbild und dauert entsprechend lange;
es braucht mehrere Gigabyte Platz. Dafür holt der Dienst zur Laufzeit nichts mehr
aus dem Netz.

## Drei Schritte

Alle Aufrufe laufen aus dem Wurzelverzeichnis des Projekts.

```bash
cp docker/.env.example docker/.env
make up
```

`make up` baut das Abbild und startet den Container. Ohne `make` geht es genauso:

```bash
docker compose -f docker/docker-compose.yml up -d --build
```

Compose leitet sein Projektverzeichnis aus der ersten `-f`-Datei ab und liest
`docker/.env` deshalb von selbst.

!!! warning "Ohne `docker/.env` startet der Dienst falsch"
    Fehlt die Datei, setzt Compose für jede Variable eine leere Zeichenkette ein
    und sagt nichts dazu. Der Aufruf scheitert dann an einer ganz anderen Stelle —
    am leeren Abbildnamen, am leeren Port — und die Meldung nennt nicht den Grund.
    `make up` prüft die Datei vorher und bricht mit einem Hinweis ab; der nackte
    `docker compose`-Aufruf tut das nicht.

Der dritte Schritt ist warten. Docling lädt beim Start seine Modelle, und solange
das läuft, gilt der Container als `starting`:

```bash
docker inspect -f '{{.State.Health.Status}}' kaimarkit
```

Sobald dort `healthy` steht, antwortet die Oberfläche unter
<http://127.0.0.1:8080>. Die API steht schon vorher bereit — `GET /api/health`
antwortet sofort, und `GET /api/capabilities` meldet Docling so lange als `warming`.

## Prüfen, ob der Dienst antwortet

```bash
curl -sf localhost:8080/api/health
curl -sf localhost:8080/api/capabilities | jq .
```

Die erste Umwandlung von der Kommandozeile aus:

```bash
curl -sf -F file=@bericht.pdf localhost:8080/api/convert -o bericht.md
```

Weitere Aufrufe stehen unter [API](../api.md).

## Mitlesen, beenden, aufräumen

```bash
make logs      # docker compose -f docker/docker-compose.yml logs -f
make down      # docker compose -f docker/docker-compose.yml down
```

`make help` listet alle Ziele.

## Was sich anzupassen lohnt

Die Standardwerte passen für einen Einzelplatz. Drei Stellen fallen im Alltag
zuerst auf, alle drei in `docker/.env`:

- `KAIMARKIT_BIND_ADDR` steht auf `127.0.0.1`. Der Dienst ist damit nur auf dem
  eigenen Rechner erreichbar. Für Zugriff aus dem Netz gehört eine
  TLS-Terminierung davor, siehe [Traefik](traefik.md). Ein `0.0.0.0` an dieser
  Stelle ersetzt sie nicht.
- `KAIMARKIT_HOST_PORT` steht auf `8080`. Ist der Port belegt, wird hier ein
  anderer eingetragen; im Container hört der Dienst unverändert auf 8000.
- `KAIMARKIT_MEM_LIMIT` steht auf `6g`. Wird der Container beim Umwandeln großer
  PDFs vom Kernel abgeschossen (`docker inspect` zeigt `OOMKilled`), fehlt
  Speicher.

Alle Variablen stehen unter [Konfiguration](konfiguration.md).

## Für die Entwicklung

Wer am Code arbeitet, braucht den Container nicht. `make dev` startet das Backend
auf `:8000` und das Frontend auf `:5173`, beide mit Reload. Die Einzelheiten stehen
unter [Entwicklung](../entwicklung.md).
