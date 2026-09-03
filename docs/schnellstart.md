# Schnellstart

Diese Seite führt vom Start des Containers bis zur ersten umgewandelten Datei. Was
dabei im Einzelnen geschieht und welche Variablen es gibt, steht unter
[Lokaler Betrieb](betrieb/lokal.md) und [Konfiguration](betrieb/konfiguration.md).

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
[Lokaler Betrieb](betrieb/lokal.md#was-vorher-da-sein-muss).

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

Dateien kommen per Ablegen oder über die Dateiauswahl hinein. Die Warteschlange
führt jede einzeln auf und nennt nach dem Durchlauf Engine und Dauer; eine
gescheiterte Datei hält die übrigen nicht auf, sondern zeigt ihre Meldung in der
eigenen Zeile. Die Vorschau klappt das gewandelte Markdown auf, herunterladen
lässt es sich einzeln oder als ZIP über alle gelungenen Dateien.

Eine Webseite braucht keinen Download vorweg. Unter „Webseiten, eine Adresse je
Zeile" steht ein mehrzeiliges Feld; „Webseiten wandeln" schickt jede Zeile ab, und
der Dienst holt die Seiten selbst. Jede reiht sich danach in dieselbe Warteschlange
ein wie eine hochgeladene Datei, benannt nach dem Titel der Seite: Aus
`https://example.com/` wird `example-domain.html`, nicht `example-com.html`. Eine
Zeile, die
weder mit `http://` noch mit `https://` beginnt, schickt die Oberfläche gar nicht
erst ab: Sie bleibt im Feld stehen und wird darunter genannt. Alles Übrige prüft der
Dienst — ob der Name auflöst, ob er ins offene Netz zeigt, ob dort ein Dokument
liegt —, und seine Meldung steht dann in der Zeile der Warteschlange. Welche Seiten
er nicht brauchbar wandelt, steht unter [Grenzen](grenzen.md).

Unter „Optionen" steht die Engine für den nächsten Lauf zur Wahl, als Gruppe von
Schaltflächen mit einem Halbsatz zu jeder; das Zeichen dahinter öffnet eine längere
Erklärung, mit der Maus oder per Tab. Vorgewählt ist MarkItDown, die schnelle
Engine. Die Wahl bleibt im Browser gemerkt und steht nach dem nächsten Aufruf der
Seite wieder da. Eine Engine, die gerade nicht in Frage kommt — nicht installiert,
oder in der Warteschlange liegt eine Datei, die sie nicht liest —, bleibt sichtbar,
ist aber nicht wählbar. „automatisch" überlässt die Wahl dem Dienst, wie im nächsten
Abschnitt beschrieben.

Eine laufende Zeile zählt mit, wie lange sie schon läuft. Wem es zu lange dauert,
der drückt „Nicht mehr warten": Die Zeile steht danach auf „abgebrochen", die
nächste wartende Datei rückt nach, und die Warteschlange zählt den Abbruch nicht
als Fehlschlag. Der Knopf heißt genau deshalb so — er beendet die Anfrage des
Browsers, nicht die Arbeit des Dienstes. Der wandelt die Datei im Hintergrund zu
Ende und gibt seinen Platz erst dann oder an der [Zeitgrenze](grenzen.md) frei.

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
