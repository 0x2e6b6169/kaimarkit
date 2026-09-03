# Konfiguration

Alles, was sich im Betrieb umstellen lässt, kommt aus der Umgebung. Die Vorlage steht
in `docker/.env.example`. Kopieren, anpassen, fertig:

```bash
cp docker/.env.example docker/.env
```

Compose leitet sein Projektverzeichnis aus der ersten `-f`-Datei ab und liest deshalb
`docker/.env` von selbst. Niemand muss die Datei angeben. Aus demselben Grund beziehen
sich alle relativen Pfade darin auf `docker/`.

!!! warning "Eine leere Variable bricht nichts ab"
    Für eine fehlende oder leer gelassene Variable setzt Compose still eine leere
    Zeichenkette ein. Der Aufruf läuft weiter und scheitert erst an ganz anderer
    Stelle. Deshalb hat in `docker/.env.example` jede Variable einen Wert.

Diese Seite und `docker/.env.example` beschreiben dieselben Variablen. Wer eine
ergänzt, umbenennt oder streicht, ändert beide zugleich. Ausgenommen ist der Abschnitt
[Was das Abbild fest setzt](#was-das-abbild-fest-setzt): Diese Variablen stehen im
Dockerfile und nicht in der Umgebungsdatei.

## Quellen und Build

| Variable | Standard | Wirkung |
| --- | --- | --- |
| `KAIMARKIT_BUILD_CONTEXT` | `..` | Verzeichnis, aus dem gebaut wird. Relativ zu `docker/`, also die Projektwurzel. |
| `KAIMARKIT_DOCKERFILE` | `docker/Dockerfile` | Das Dockerfile, relativ zum Build-Kontext. |
| `KAIMARKIT_PROJECT_NAME` | `kaimarkit` | Name des Compose-Projekts. Ohne ihn hieße es `docker`, nach dem Verzeichnis der Compose-Datei. |
| `PANDOC_VERSION` | `3.6.4` | Pandoc kommt als `.deb` von GitHub, die Version steht fest. |
| `KAIMARKIT_VERSION` | aus `git describe` | Der Stand, aus dem gebaut wird. Steht in `docker/.env.example` auskommentiert. |

Wer aus einem zweiten Checkout baut, setzt die beiden ersten Variablen auf absolute
Pfade; die Compose-Dateien bleiben dann unverändert. Zwei Feinheiten dabei:
`KAIMARKIT_DOCKERFILE` muss relativ zu genau diesem Kontext liegen, und Docker sucht
die `.dockerignore` in der Wurzel des dortigen Baums.

### Welchen Stand der Dienst meldet

`KAIMARKIT_VERSION` sagt, was wirklich läuft. Der Wert erscheint unter
[`/api/health`](../api.md) und in der Fußzeile der Oberfläche. Ermittelt wird er
einmal beim Bauen, auf der Maschine, die das `.git` hat:

```bash
git describe --tags --always --dirty
```

Auf dem Tag steht dort `v0.1.0`, zwölf Commits dahinter `v0.1.0-12-ga22a6c5`, und bei
Änderungen im Arbeitsbaum kommt `-dirty` hinzu. Das Makefile ruft den Befehl auf und
reicht das Ergebnis über `build.args` an den Bau weiter; das Abbild behält es als
`ENV`. Der Container fragt nie selbst nach Git — er hat kein `.git`.

Die Rückfallkette hat zwei Stufen:

1. `KAIMARKIT_VERSION` aus der Umgebung, wie der Bau sie gesetzt hat.
2. Ist die Variable leer oder fehlt sie, gilt `__version__` aus
   `backend/app/__init__.py`.

Die zweite Stufe greift in drei Fällen, und alle drei kommen vor: ein Bau aus einem
Tarball ohne `.git`, ein Klon ohne Tags (`--depth 1` ohne `--tags`) und eine Maschine
ohne `git`. Keiner davon bricht den Bau ab. Wer in einem dieser Fälle trotzdem einen
genauen Stand melden will, trägt ihn in `docker/.env` von Hand ein; das Makefile
überschreibt ihn nicht, weil es einen leeren Wert gar nicht erst weitergibt. Umgekehrt
gilt: Wo `git describe` etwas liefert, gewinnt es gegen den Eintrag in der Datei.

## Anwendung

| Variable | Standard | Wirkung |
| --- | --- | --- |
| `KAIMARKIT_MAX_FILE_SIZE_MB` | `50` | Größe einer einzelnen Datei. |
| `KAIMARKIT_MAX_FILES` | `20` | Dateien je Stapelaufruf. |
| `KAIMARKIT_MAX_CONCURRENT` | `2` | Gleichzeitige Umwandlungen. |
| `KAIMARKIT_CONVERSION_TIMEOUT` | `600` | Zeitgrenze je Datei in Sekunden. |
| `KAIMARKIT_PANDOC_TIMEOUT` | `60` | Zeitgrenze für den Pandoc-Unterprozess in Sekunden. |
| `KAIMARKIT_URL_TIMEOUT` | `30` | Zeitgrenze je Abruf für `/api/convert/url` in Sekunden, Weiterleitungen eingeschlossen. |
| `KAIMARKIT_DEFAULT_ENGINE` | `auto` | `auto` folgt der Präferenzliste im Code. Ein Enginename (`markitdown`, `docling`, `pandoc`) zieht diese Engine überall nach vorn. |
| `KAIMARKIT_ENABLE_FALLBACK` | `true` | Bei `auto` die nächste geeignete Engine nehmen, wenn die erste scheitert. |
| `KAIMARKIT_OCR_ENABLED` | `true` | Docling schickt gescannte Seiten und Bilder durch die Texterkennung. |
| `KAIMARKIT_OCR_LANGS` | `de,en` | Sprachen der Texterkennung, als ISO-639-1-Kürzel und durch Komma getrennt. |
| `KAIMARKIT_LOG_LEVEL` | `info` | Ausführlichkeit der Ausgabe. |
| `KAIMARKIT_WORKERS` | `1` | Zahl der Uvicorn-Worker. |
| `KAIMARKIT_STATIC_DIR` | `/opt/kaimarkit/static` | Das gebaute Frontend im Container. |
| `KAIMARKIT_DOCS_DIR` | `/opt/kaimarkit/docs` | Diese Dokumentation im Container. |

Die Größe prüft der Dienst schon während des Empfangs. Eine Prüfung danach käme zu
spät — dann läge die Datei bereits vollständig im Speicher. Was die Grenzen für Größe,
Anzahl, Gleichzeitigkeit und Dauer im Einzelnen bewirken, steht unter
[Grenzen](../grenzen.md).

`KAIMARKIT_ENABLE_FALLBACK` gilt nur für `engine=auto`. Eine im Aufruf ausdrücklich
genannte Engine ersetzt der Dienst nie durch eine andere. `KAIMARKIT_OCR_ENABLED`
setzt den Standard; eine einzelne Anfrage überschreibt ihn mit dem Feld `ocr`.

`KAIMARKIT_OCR_LANGS` erwartet ISO-639-1-Kürzel. Der Docling-Adapter ruft
ausdrücklich EasyOCR auf, und EasyOCR liest nur die zweibuchstabige Form. Tesseracts
`deu,eng` gehört hier nicht hin.

Jeder Worker hält eigene Docling-Modelle im Speicher, rund 2 GB. `KAIMARKIT_WORKERS`
erst erhöhen, wenn genug RAM da ist, und `KAIMARKIT_MEM_LIMIT` mit anheben.

Fehlt eines der beiden Verzeichnisse, hängt das Backend es nicht ein und läuft
trotzdem: ohne gebautes Frontend und ohne Dokumentation, aber mit vollständiger API.

### Woran man merkt, dass die Zeitgrenze zu knapp ist

Überschreitet eine Umwandlung `KAIMARKIT_CONVERSION_TIMEOUT`, antwortet der Dienst mit 504 und
`conversion_timeout`, und die Oberfläche zeigt an der Datei „Die Umwandlung hat die
Zeitgrenze von *n* s überschritten". Der Satz nennt den Grund, sieht aber aus wie ein
Fehler des Dienstes. Er ist keiner: Der Dienst hat abgebrochen, weil die Einstellung
es ihm sagt.

Zwei Anzeichen unterscheiden die zu knappe Grenze von einer echten Störung. Erstens
scheitert immer dieselbe Datei, und zwar nach immer derselben Zeit — auf die Sekunde
der eingestellte Wert. Zweitens steht im Containerprotokoll keine Ausnahme, sondern
Doclings eigene Zeile:

```
INFO:docling.document_converter:Finished converting document rechnung.pdf in 326.06 sec.
```

Sie kommt oft erst nach der Fehlermeldung, weil die Engine weiterrechnet, wenn der
Wartevorgang längst beendet ist ([Grenzen](../grenzen.md)). Diese Zahl ist die
gesuchte: Wer die Zeitgrenze über sie setzt, lässt das Dokument durch.

Die Zeit geht dabei fast vollständig in die Texterkennung gescannter Seiten. Ein PDF
mit Textschicht wandelt derselbe Dienst in wenigen Sekunden um; eine gescannte Seite
kostet auf einem Notebook mit zwei Kernen zwischen anderthalb und drei Minuten,
dasselbe Dokument von Lauf zu Lauf verschieden. Wer regelmäßig gescannte Dokumente
mit vielen Seiten durchschickt, rechnet mit rund zwei Minuten je Seite und setzt die
Grenze entsprechend.

## Was das Abbild fest setzt

Drei Variablen für Docling stehen nicht in `docker/.env`, sondern im `ENV`-Block des
Dockerfiles. Compose reicht sie nicht durch. Wer sie ändern will, baut das Abbild neu.

| Variable | Wert im Abbild | Wirkung |
| --- | --- | --- |
| `DOCLING_ARTIFACTS_PATH` | `/opt/docling-models` | Das Verzeichnis, in dem Docling seine Layout- und Tabellenmodelle sucht. Die Build-Stufe `models` legt sie dort ab. |
| `HF_HOME` | `/opt/docling-models` | Der Hugging-Face-Cache. Einen Teil der Gewichte holt Docling über ihn, deshalb liegt er neben den übrigen Modellen. |
| `HF_HUB_OFFLINE` | `1` | Verbietet zur Laufzeit jeden Zugriff auf den Hugging-Face-Hub. |

Die drei gehören zusammen. Ohne `DOCLING_ARTIFACTS_PATH` sucht Docling die Modelle im
Home-Verzeichnis des Benutzers, findet nichts und lädt sie nach. Das Nachladen
beginnt schon beim Hochfahren, nicht erst bei der ersten Anfrage.
`HF_HUB_OFFLINE=1` verhindert genau das: Der Download scheitert, Docling meldet sich
als nicht verfügbar, und `engine=auto` nimmt die nächste Engine. Der Dienst antwortet
weiter, aber ohne Doclings Tabellenerkennung.

Wer eigene Modelle einhängt, setzt `DOCLING_ARTIFACTS_PATH` auf das eingehängte
Verzeichnis und lässt `HF_HUB_OFFLINE=1` stehen. Dann kommt zur Laufzeit nichts aus
dem Netz.

## Container

| Variable | Standard | Wirkung |
| --- | --- | --- |
| `KAIMARKIT_IMAGE` | `kaimarkit` | Name des Abbilds. |
| `KAIMARKIT_TAG` | `local` | Version des Abbilds, der Docker-Tag. |
| `KAIMARKIT_CONTAINER_NAME` | `kaimarkit` | Name des Containers. |
| `KAIMARKIT_RESTART_POLICY` | `unless-stopped` | Wann Docker den Container neu startet. |
| `KAIMARKIT_BIND_ADDR` | `127.0.0.1` | Adresse, auf der der Host-Port liegt. |
| `KAIMARKIT_HOST_PORT` | `8080` | Host-Port. Im Container hört der Dienst immer auf 8000. |
| `KAIMARKIT_MEM_LIMIT` | `6g` | Speichergrenze des Containers. Unter `4g` wird es eng. |
| `KAIMARKIT_HEALTH_START_PERIOD` | `180s` | Anlaufzeit des Healthchecks. |

`KAIMARKIT_BIND_ADDR=127.0.0.1` hält den Dienst auf dem eigenen Rechner. Für Zugriff
aus dem Netz gibt es zwei Wege: `0.0.0.0` setzen, oder — besser — den
[Traefik-Aufbau](traefik.md) nehmen. Dort entfällt die Veröffentlichung auf dem Host
ganz.

Solange die Anlaufzeit läuft, zählt ein fehlgeschlagener Healthcheck nicht als
ungesund. Sie deckt den Start des Dienstes ab, nicht das Vorladen der Modelle: Der
Healthcheck ruft `GET /api/health`, und diese Antwort hängt nicht an Docling.
`healthy` sagt also, dass der Dienst antwortet — nicht, dass das Vorladen fertig ist.
Docling lädt daneben im Hintergrund weiter: rund achteinhalb Sekunden je Pipeline,
und der Warmlauf baut zwei davon, eine mit Texterkennung und eine ohne. Solange die
erste nicht steht, meldet `GET /api/capabilities` Docling als `warming`.

Auf langsamen Datenträgern `KAIMARKIT_HEALTH_START_PERIOD` hochsetzen, sonst gilt
der Container als ungesund, bevor er überhaupt fertig gestartet ist.

## Traefik

Diese fünf Variablen braucht nur, wer `docker-compose.traefik.yml` mitgibt.

| Variable | Standard | Wirkung |
| --- | --- | --- |
| `TRAEFIK_NETWORK` | `traefik-web` | Das Docker-Netz, in dem Traefik läuft. Es muss bereits existieren. |
| `TRAEFIK_ENTRYPOINT` | `websecure` | Der Traefik-Entrypoint, an dem der Router hängt. Beispielwert. |
| `TRAEFIK_CERTRESOLVER` | `myresolver` | Der Certresolver für das Zertifikat. Beispielwert. |
| `KAIMARKIT_DOMAIN` | `kaimarkit.example.com` | Der Hostname, unter dem der Dienst antwortet. Hinter Authelia muss er unter deren Cookie-Domäne liegen. |
| `KAIMARKIT_TRAEFIK_NAME` | `kaimarkit` | Namensraum der Traefik-Namen: Router, `…-api`, Dienst und die eigene Middleware `…-auth`. |

Der letzte Wert trennt zwei Instanzen hinter derselben Traefik. Diese Namen gelten je
Traefik-Instanz, nicht je Container; zwei Aufbauten mit demselben Wert legen einander
lahm. Was daraus im Einzelnen wird und wie sich das nachprüfen lässt, steht unter
[Traefik](traefik.md#der-namensraum-der-traefik-namen).

`TRAEFIK_ENTRYPOINT` und `TRAEFIK_CERTRESOLVER` sind Beispielwerte und keine
Voreinstellungen: Beide Namen stammen aus der statischen Konfiguration der
vorhandenen Traefik und müssen dort genauso lauten.

Der Compose-Dienst heißt unabhängig davon weiterhin `kaimarkit`. `docker compose logs
kaimarkit` und die Makefile-Ziele bleiben also, wie sie sind.

## Authelia

Diese vier Variablen braucht nur, wer zusätzlich `docker-compose.authelia.yml`
mitgibt.

| Variable | Standard | Wirkung |
| --- | --- | --- |
| `KAIMARKIT_MIDDLEWARES` | `authelia@docker` | Die Middlewares des Hauptrouters. Leer lassen gibt die Oberfläche frei. |
| `KAIMARKIT_API_MIDDLEWARES` | `authelia@docker` | Die Middlewares des `/api`-Routers. Leer lassen gibt die API frei. |
| `AUTHELIA_VERIFY_URL` | `http://authelia:9091/api/verify?rd=https://auth.example.com` | Die Adresse, an der die eigene ForwardAuth-Middleware jede Anfrage prüfen lässt. |
| `AUTHELIA_RESPONSE_HEADERS` | `Remote-User,Remote-Groups,Remote-Name,Remote-Email` | Kopfzeilen, die Traefik von Authelia an die Anwendung durchreicht. |

Die ersten beiden entscheiden, welche Middleware die Router benutzen, und damit auch,
ob die letzten beiden überhaupt gelesen werden. Voreingestellt verweisen sie auf
`authelia@docker`: die Middleware, die eine per Docker-Label beschriftete Authelia an
sich selbst definiert. Dann bleiben `AUTHELIA_VERIFY_URL` und
`AUTHELIA_RESPONSE_HEADERS` ungenutzt.

Wer stattdessen `kaimarkit-auth@docker` einträgt, benutzt die Middleware, die
`docker-compose.authelia.yml` selbst definiert — und braucht dafür die beiden
letzten. Deren Name folgt `KAIMARKIT_TRAEFIK_NAME`: Bei abweichendem Namensraum heißt
sie `<name>-auth@docker`. Der Hostname in `AUTHELIA_VERIFY_URL` ist dann der Containername von
Authelia im Traefik-Netz, der `rd`-Parameter dagegen die von außen erreichbare
Anmeldeseite. Beide zeigen auf denselben Dienst, aber aus verschiedenen
Blickwinkeln.

Der Zusatz hinter dem `@` nennt den Traefik-Anbieter und gehört zum Wert: Eine
Authelia, die ihre Middleware aus einer Datei bezieht, heißt `authelia@file`. Beide
Wege, die Stolperstelle mit dem Anbieter und der Umstieg von einer früheren Fassung
stehen unter [Authelia](authelia.md).

Zwei Bedingungen betreffen nicht diese Variablen, sondern Authelias eigene
Konfiguration: `KAIMARKIT_DOMAIN` muss unter deren Cookie-Domäne liegen, und deren
`access_control` braucht eine Regel für diesen Namen. Fehlt das erste, antwortet
Authelia mit 400, bevor sich jemand anmelden kann; fehlt das zweite, greift die
`default_policy`. Beides steht ausführlich unter [Authelia](authelia.md).
