# Schnellstart

Diese Seite führt vom Start des Containers bis zur ersten umgewandelten Datei. Was
dabei im Einzelnen geschieht und welche Variablen es gibt, steht unter
[Lokaler Betrieb](lokal.md) und [Konfiguration](konfiguration.md).

## Was vorher da sein muss

Eine Docker Engine mit dem Compose-Plugin und rund 6 GB freier Arbeitsspeicher. Der
erste Bau backt die Docling-Modelle in das Abbild. Er dauert und braucht mehrere
Gigabyte Platz; dafür lädt der Dienst zur Laufzeit keine Modelle mehr nach. Ins Netz
greift er dann nur noch auf Verlangen: Ein Aufruf von `/api/convert/url` holt genau
die eine Seite, nicht ihre Bilder und nicht ihre Stylesheets. Von sich aus schickt
er nichts hinaus, auch keine Nutzungsdaten.

Ob die Engine wirklich erreichbar ist, beantwortet ein Befehl:

```bash
docker version
```

Er zeigt neben dem Client einen Abschnitt `Server` mit der Version der Engine und
kehrt mit 0 zurück. Meldet er stattdessen `permission denied while trying to connect
to the docker API`, dann läuft die Engine, aber das eigene Konto darf nicht an ihren
Socket. Es fehlt die Gruppe `docker` — wer in ihr steht, wird auf diesem Rechner
allerdings effektiv Root. Den Befehl dafür und die Abwägung dazu nennt
[Lokaler Betrieb](lokal.md#was-vorher-da-sein-muss).

`make up` stellt diese Frage vor dem Bau von selbst und bricht ab, bevor die erste
Stufe anläuft.

## Starten

Aus dem Wurzelverzeichnis des Projekts:

```bash
cp docker/.env.example docker/.env
make up
```

`make up` baut das Abbild und startet den Container. Die Standardwerte aus
`docker/.env.example` reichen für den Anfang; der Dienst antwortet danach unter
<http://127.0.0.1:8080>.

Ob er schon antwortet, sagt der Healthcheck:

```bash
curl -sf localhost:8080/api/health
```

```json
{ "status": "ok", "version": "v0.1.0-12-ga22a6c5" }
```

Die Version ist die des gebauten Abbilds — `git describe` auf der bauenden
Maschine. Ein Bau ohne Git-Verlauf meldet `__version__` aus
`backend/app/__init__.py`, die Nummer ohne `v`.

## Die erste Datei

Ein PDF, eine Antwort, fertig:

```bash
curl -sf -F file=@bericht.pdf localhost:8080/api/convert -o bericht.md
```

Ohne `Accept`-Kopf ist der Rumpf der Antwort das nackte Markdown. Welche Engine es
erzeugt hat, steht in der Kopfzeile `X-Engine`:

```bash
curl -sf -D - -F file=@bericht.pdf localhost:8080/api/convert -o bericht.md | grep -i '^x-'
```

Mit `Accept: application/json` kommt stattdessen das vollständige Ergebnis, also
Markdown, Engine, Warnungen und Dauer in einem Objekt. Alle Aufrufe stehen unter
[API](api.md).

## Über die Oberfläche

Die Oberfläche liegt unter <http://127.0.0.1:8080>, die Dokumentation daneben unter
`/docs`, die maschinenlesbare Beschreibung der Schnittstelle unter `/api/docs`.

Wie man sie bedient — Dateien ablegen, Webseiten wandeln, Optionen, Vorschau,
Warnungen —, steht unter [Die Oberfläche](../nutzer/dateien-wandeln.md).

## Welche Engine kommt zum Zug?

Der Dienst wählt nach der Dateiendung. Was er jetzt wirklich anbietet, sagt er
selbst:

```bash
curl -sf localhost:8080/api/capabilities | jq .
```

Steht Docling dort auf `warming`, lädt es gerade seine Modelle. Bis das fertig ist,
bekommt ein PDF die nächste Engine der Liste, also MarkItDown. Die vollständige
Matrix steht unter [Formate](formate.md).

Wer die Wahl selbst treffen will, nennt die Engine im Aufruf:

```bash
curl -sf -F file=@bericht.pdf -F engine=docling \
     localhost:8080/api/convert -o bericht.md
```

Eine ausdrücklich genannte Engine wird nie durch eine andere ersetzt. Kann sie das
Format nicht, antwortet der Dienst mit 400 statt still etwas anderes zu nehmen.

## Wenn es nicht klappt

Ein Fehlschlag kommt als HTTP-Fehler mit einem `code`, nicht als leere Antwort.
`curl -sf` verschluckt den Rumpf; für die Meldung `-f` weglassen:

```bash
curl -s -F file=@bericht.xyz localhost:8080/api/convert | jq .
```

```json
{ "detail": "Fuer .xyz gibt es keine Engine.", "code": "unsupported_format" }
```

Alle Codes stehen unter [API](api.md), die Grenzen dahinter unter
[Grenzen](grenzen.md).

## Beenden

```bash
make logs      # mitlesen
make down      # beenden und Container entfernen
make help      # alle Ziele
```
