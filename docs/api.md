# API

Die Endpunkte unter `/api` mit Beispielaufrufen für curl.

Der verbindliche Wortlaut steht in `contracts/api.md`; diese Seite zeigt, wie man die
Endpunkte benutzt. Jede Anfrage steht für sich: Der Dienst legt nichts ab, und die
hochgeladene Datei ist gelöscht, sobald die Antwort steht. Eine Authentifizierung
gibt es nicht; wer eine braucht, setzt [Authelia](betrieb/authelia.md) davor.

!!! note "Der Port in den Beispielen"
    Alle Aufrufe hier nennen `localhost:8000`, den Port des Backends in der
    Entwicklung. Im Container liegt der Dienst auf `KAIMARKIT_HOST_PORT`,
    standardmäßig also auf `localhost:8080`. Im Container hört er unverändert auf
    8000 — veröffentlicht wird 8080.

Die Antwort auf einen Fehler hat immer denselben Rumpf, unabhängig vom Endpunkt:

```json
{ "detail": "Fuer .xyz gibt es keine Engine.", "code": "unsupported_format" }
```

`curl -sf` verschluckt diesen Rumpf. Wer die Meldung sehen will, lässt `-f` weg.

## Lebt der Dienst? — `GET /api/health`

Antwortet sofort mit 200, auch während Docling im Hintergrund lädt. Der
Container-Healthcheck hängt daran: Käme die Antwort erst nach den Modellen, gälte
der Start als Fehlschlag.

```bash
curl -sf localhost:8000/api/health
```

```json
{ "status": "ok", "version": "v0.1.0-12-ga22a6c5" }
```

Die Version ist die des gebauten Abbilds: Der Bau setzt `KAIMARKIT_VERSION` auf das
Ergebnis von `git describe --tags --always --dirty` — `v0.1.0` auf dem Tag,
`v0.1.0-12-ga22a6c5` zwölf Commits dahinter, mit `-dirty` bei Änderungen im
Arbeitsbaum. Fehlt die Variable, meldet der Dienst `__version__` aus
`app/__init__.py`: dieselbe Nummer wie auf dem Tag, ohne das `v`.

Die Auskunft sagt nichts darüber, ob eine Engine schon arbeiten kann. Das steht in
`/api/capabilities`.

## Was der Dienst kann — `GET /api/capabilities`

Die Auskunft nennt die Endungen, die jetzt wirklich gehen, die Engines samt Zustand
(`ready`, `warming`, `unavailable`), die geltenden Grenzen und die Standardengine.

```bash
curl -sf localhost:8000/api/capabilities | jq .
```

Die Reihenfolge in `formats` ist die Präferenz: Bei `engine=auto` kommt der erste
Eintrag zum Zug. Eine Engine, die noch lädt oder fehlt, erscheint dort nicht — das
Frontend bietet deshalb nichts an, was ohnehin scheitern würde. Steht Docling auf
`warming`, laden gerade die Modelle; ein paar Sekunden später steht `.pdf` wieder in
der Liste.

In `engines` stehen nur die drei wählbaren Engines. Markdown reicht der Dienst
durch, und dafür gibt es nichts zu wählen: `formats` führt `.md` mit dem Namen
`passthrough`, und derselbe Name steht danach im Feld `engine` des Ergebnisses.

## Eine Datei wandeln — `POST /api/convert`

`multipart/form-data` mit dem Feld `file`. Dazu wahlweise `engine` (ein Enginename
oder `auto`) und `ocr` (überschreibt `KAIMARKIT_OCR_ENABLED`).

Die Antwort richtet sich nach `Accept`. Ohne Angabe kommt das nackte Markdown mit
`Content-Disposition`, die Engine steht in `X-Engine` und Anmerkungen stehen in
`X-Warnings`:

```bash
curl -sf -F file=@bericht.pdf localhost:8000/api/convert -o bericht.md
```

Mit `Accept: application/json` kommt das vollständige Ergebnis samt `engine`,
`warnings` und `duration_ms`:

```bash
curl -sf -F file=@bericht.pdf -F engine=markitdown \
     -H 'Accept: application/json' localhost:8000/api/convert
```

Eine ausdrücklich genannte Engine wird nie durch eine andere ersetzt. Kann sie das
Format nicht, antwortet der Dienst mit 400, statt still etwas anderes zu nehmen. Bei
`auto` dagegen rückt nach einem Fehlschlag die nächste Engine der Präferenzliste
nach; warum die erste ausschied, steht danach in den Warnungen.

Scheitert die Umwandlung, gibt es einen Fehlercode und keine leere Antwort:

| HTTP | `code` | Anlass |
|---|---|---|
| 413 | `file_too_large` | über `KAIMARKIT_MAX_FILE_SIZE_MB` |
| 415 | `unsupported_format` | für diese Endung gibt es keine Engine |
| 400 | `engine_unsuitable` | die verlangte Engine kann das Format nicht |
| 400 | `engine_unavailable` | die verlangte Engine ist nicht installiert |
| 500 | `conversion_failed` | die Engine ist an der Datei gescheitert |
| 504 | `conversion_timeout` | über `KAIMARKIT_CONVERSION_TIMEOUT` |

## Mehrere Dateien wandeln — `POST /api/convert/batch`

Dieselben Felder, nur `file` mehrfach. Höchstens `KAIMARKIT_MAX_FILES` Dateien je
Aufruf. Der Endpunkt ist für Skripte gedacht; das Frontend ruft `/api/convert` je
Datei auf, weil es Fortschritt und Vorschau einzeln zeigt.

Ohne `Accept` kommt ein ZIP mit je einer `.md`-Datei:

```bash
curl -sf -F file=@a.pdf -F file=@b.epub -F file=@c.docx \
     localhost:8000/api/convert/batch -o ergebnis.zip
```

Im Archiv steht nur der blanke Name, nie ein Verzeichnis davor. Zwei gleich benannte
Dateien aus verschiedenen Ordnern überschreiben einander deshalb nicht: Die zweite
heißt `bericht-2.md`, die dritte `bericht-3.md`.

Eine gescheiterte Datei nimmt die übrigen nicht mit. Sie fehlt im Archiv und
bekommt stattdessen eine Zeile in `_errors.txt`, die nur dann darin liegt, wenn
wirklich etwas schieflief. Jede Zeile nennt den Dateinamen und den Grund, den die
Engine gemeldet hat:

```text
kaputt.epub: Archiv unlesbar
```

Mit `Accept: application/json` kommt dieselbe Auskunft als Liste von Einträgen,
dazu die Zählung:

```bash
curl -sf -F file=@a.pdf -F file=@b.epub \
     -H 'Accept: application/json' localhost:8000/api/convert/batch
```

```json
{
  "entries": [
    { "filename": "a.pdf", "status": "ok", "markdown": "# A", "engine": "docling",
      "warnings": [], "duration_ms": 3120, "error": null },
    { "filename": "b.epub", "status": "failed", "markdown": null, "engine": null,
      "warnings": [], "duration_ms": 88, "error": "Archiv unlesbar" }
  ],
  "total": 2,
  "succeeded": 1,
  "failed": 1
}
```

Der Aufruf antwortet mit 200, auch wenn jede einzelne Datei scheiterte — die Anfrage
selbst war ja in Ordnung. Als Anfrage scheitert nur ein zu großer Stapel: mehr als
`KAIMARKIT_MAX_FILES` Dateien enden mit 413 und `too_many_files`.

## Eine Webseite wandeln — `POST /api/convert/url`

Hier lädt niemand etwas hoch: Der Dienst holt die Seite selbst und wandelt sie
danach wie eine hochgeladene Datei. Der Rumpf ist JSON, eine Adresse je Aufruf.

| Feld | Typ | Pflicht | Bedeutung |
|---|---|---|---|
| `url` | string | ja | die Adresse, `http` oder `https` |
| `engine` | string | nein | ein Enginename oder `auto` (Standard) |
| `ocr` | boolean \| null | nein | überschreibt `KAIMARKIT_OCR_ENABLED` |

```bash
curl -sf -H 'Content-Type: application/json' \
     -d '{"url": "https://example.com/"}' localhost:8000/api/convert/url
```

Die Antwort ist immer ein `ConversionEntry` als JSON. Den Markdown-Zweig über
`Accept`, den `/api/convert` kennt, gibt es hier nicht.

```json
{
  "filename": "example-domain.html",
  "status": "ok",
  "markdown": "# Example Domain\n\nThis domain is for use in documentation examples ...",
  "engine": "markitdown",
  "warnings": [],
  "duration_ms": 10,
  "error": null
}
```

Den Dateinamen leitet der Dienst ab, statt ihn zu übernehmen. Er kommt aus dem
`<title>` der Seite: Kleinbuchstaben, Umlaute umgeschrieben (`ä` → `ae`,
`ß` → `ss`), alles außer `[a-z0-9]` zu `-`, höchstens 80 Zeichen. Fehlt ein Titel —
bei einer PDF etwa —, entsteht der Name auf dieselbe Art aus Host und Pfad:
`https://arxiv.org/pdf/2502.16161` wird zu `arxiv-org-pdf-2502-16161.pdf`. Die
Endung ist die der geholten Datei; sie folgt dem `Content-Type` und sonst dem Pfad.
Doppelt steht sie nie da: `…/resources/pdf/dummy.pdf` endet auf `-dummy.pdf`, nicht
auf `-dummy-pdf.pdf`. Gleiche Namen nummeriert der Client, nicht der Dienst.

Nach dem Holen geht die Datei denselben Weg wie ein Upload: Registry, Engine,
Rückfall. Deshalb gelten dieselben Fehler wie bei `/api/convert`, und `invalid_url`
kommt dazu:

| HTTP | `code` | Anlass |
|---|---|---|
| 400 | `invalid_url` | kein öffentliches http(s), Host nicht auflösbar, Weiterleitung ins Private, mehr als fünf Weiterleitungen, oder die Gegenstelle antwortet nicht mit 2xx |
| 400 | `engine_unsuitable` | die verlangte Engine kann das gelieferte Format nicht |
| 400 | `engine_unavailable` | die verlangte Engine ist nicht installiert |
| 413 | `file_too_large` | die Antwort überschreitet `KAIMARKIT_MAX_FILE_SIZE_MB` |
| 415 | `unsupported_format` | weder `Content-Type` noch Pfad führen auf eine bekannte Endung |
| 500 | `conversion_failed` | die Engine ist an der Seite gescheitert |
| 504 | `conversion_timeout` | über `KAIMARKIT_URL_TIMEOUT` beim Holen oder `KAIMARKIT_CONVERSION_TIMEOUT` beim Wandeln |

Eine gesperrte Adresse nennt die geprüfte Adresse mit. `http://127.0.0.1/` etwa
antwortet mit 400:

```bash
curl -s -H 'Content-Type: application/json' \
     -d '{"url": "http://127.0.0.1/"}' localhost:8000/api/convert/url
```

```json
{
  "detail": "127.0.0.1 zeigt auf 127.0.0.1, und das ist keine öffentliche Adresse.",
  "code": "invalid_url"
}
```

Den Namen umgeht das nicht: `http://localhost:8000/api/health` endet mit derselben
Meldung, weil der Dienst den Namen auflöst, bevor er verbindet.

Was der Dienst dabei bewusst nicht kann — Seiten hinter einer Anmeldung, Seiten, die
ihren Inhalt erst per JavaScript aufbauen —, steht unter [Grenzen](grenzen.md).

## Die Schnittstelle maschinenlesbar

FastAPI erzeugt die Beschreibung selbst. Sie liegt unter `/api/openapi.json`, die
Oberfläche dazu unter `/api/docs` und `/api/redoc`. Alles Maschinelle liegt unter
`/api`, weil `/docs` dieser Dokumentation gehört.

```bash
curl -sf localhost:8000/api/openapi.json | jq '.paths | keys'
```

Verbindlich ist trotzdem `contracts/api.md`. Die erzeugte Beschreibung folgt dem
Code; weichen beide voneinander ab, ist der Code falsch und nicht der Vertrag.
