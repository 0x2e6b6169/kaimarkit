# Lokaler Betrieb

Der kürzeste Weg zum laufenden Dienst: ein Container, ein veröffentlichter Port,
kein Reverse Proxy davor. Für einen Rechner unter dem Schreibtisch reicht das.

## Was vorher da sein muss

Docker Engine mit dem Compose-Plugin und etwa 6 GB freier Arbeitsspeicher — so viel
gibt `KAIMARKIT_MEM_LIMIT` dem Container. Der erste Bau backt die Docling-Modelle in
das Abbild und dauert entsprechend lange; es braucht mehrere Gigabyte Platz. Dafür
holt der Dienst zur Laufzeit nichts mehr aus dem Netz.

Ob die Engine wirklich erreichbar ist, beantwortet ein Befehl:

```bash
docker version
```

Er zeigt neben dem Client einen Abschnitt `Server` mit der Version der Engine und
kehrt mit 0 zurück. Steht dort stattdessen

```text
permission denied while trying to connect to the docker API
at unix:///var/run/docker.sock
```

dann läuft die Engine, aber das eigene Konto darf nicht an ihren Socket. Es fehlt die
Gruppe `docker`:

```bash
sudo usermod -aG docker $USER
```

Danach neu anmelden, sonst wirkt die neue Gruppe im laufenden Login nicht.

!!! warning "Was die Gruppe `docker` einschließt"
    Wer den Docker-Daemon ansprechen darf, wird auf diesem Rechner effektiv Root:
    Ein Container, der das Wurzelverzeichnis des Hosts einhängt, genügt dafür. Auf
    dem eigenen Server nimmt man das üblicherweise in Kauf; auf einer Maschine mit
    mehreren Konten ist es eine Entscheidung.

`docker compose version` beantwortet diese Frage **nicht**. Der Befehl fragt allein
das Plugin und antwortet auch dann, wenn der Daemon unerreichbar bleibt — eine
Prüfung also, die besteht, während der erste echte Aufruf scheitert.

`make up` stellt die Frage vor dem Bau von selbst und bricht ab, bevor die erste
Stufe anläuft. Ein Bau, der erst nach zwanzig Minuten am fehlenden Recht scheitert,
wäre die schlechtere Reihenfolge.

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

Der dritte Schritt ist warten, und zwar kürzer, als es aussieht:

```bash
docker inspect -f '{{.State.Health.Status}}' kaimarkit
```

Sobald dort `healthy` steht, antwortet die Oberfläche unter
<http://127.0.0.1:8080>. Der Healthcheck ruft `GET /api/health` auf, und diese
Antwort hängt nicht an den Modellen — `healthy` sagt also, dass der Dienst läuft,
nicht dass Docling geladen hat.

Docling lädt derweil im Hintergrund: rund achteinhalb Sekunden je Pipeline, und der
Dienst baut zwei davon — eine mit Texterkennung, eine ohne. Solange die erste nicht
steht, meldet `GET /api/capabilities` Docling als `warming`, danach als `ready`,
während die zweite entsteht. Wer in diesen Sekunden schon ein PDF schickt, bekommt
es trotzdem gewandelt: `engine=auto` nimmt so lange MarkItDown, und wer Docling
ausdrücklich verlangt, wartet auf den fertigen Konverter.

## Docker Desktop unter Windows

Wer den Dienst in einer WSL-Distribution startet und ihn im Browser unter Windows
bedienen will, muss nichts weiter einstellen. Docker Desktop veröffentlicht den Port
nicht in der Distribution, sondern auf Windows selbst: `com.docker.backend` hört dort
auf `127.0.0.1:8080` und reicht jede Verbindung an den Container weiter. Die
Oberfläche steht deshalb unter <http://127.0.0.1:8080> — unter derselben Adresse wie
auf einem Linux-Rechner.

`localhost` löst Windows auf zwei Adressen auf, `127.0.0.1` und `::1`. Veröffentlicht
ist nur die erste; eine Verbindung nach `[::1]:8080` weist Windows ab.
`http://localhost:8080` kommt also nur an, solange das aufrufende Programm die
abgewiesene Adresse überspringt. Wer die Zahlen tippt, lässt die Frage gar nicht erst
aufkommen.

`KAIMARKIT_BIND_ADDR=127.0.0.1` meint hier den Windows-Rechner, nicht die
Distribution: Über die IP-Adresse der Distribution ist der Dienst nicht erreichbar,
auch nicht von Windows aus. Für den Zugriff von anderen Rechnern gilt darum dasselbe
wie sonst, siehe [Traefik](traefik.md).

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
