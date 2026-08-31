# Schnellstart

Diese Seite führt vom Start des Containers bis zur ersten umgewandelten Datei. Was
dabei im Einzelnen geschieht und welche Variablen es gibt, steht unter
[Lokaler Betrieb](betrieb/lokal.md) und [Konfiguration](betrieb/konfiguration.md).

## Was vorher da sein muss

Eine Docker Engine mit dem Compose-Plugin — `docker compose version` muss antworten —
und rund 6 GB freier Arbeitsspeicher. Der erste Bau backt die Docling-Modelle in das
Abbild. Er dauert und braucht mehrere Gigabyte Platz; dafür holt der Dienst zur
Laufzeit nichts mehr aus dem Netz.

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
{ "status": "ok", "version": "0.1.0" }
```

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

!!! info "Die Oberfläche wird noch zusammengesetzt"
    Dropzone, Warteschlange, Optionen und Vorschau stehen als einzelne Bausteine
    bereit, die Startseite zeigt aber bisher nur den Gerüstzustand. Der Weg über
    curl oben ist der, der jetzt vollständig funktioniert.

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
