# API

Die Endpunkte unter `/api` mit Beispielaufrufen für curl.

Der verbindliche Wortlaut steht in `contracts/api.md`; diese Seite zeigt, wie man die
Endpunkte benutzt. Jede Anfrage steht für sich: Der Dienst legt nichts ab, und die
hochgeladene Datei ist gelöscht, sobald die Antwort steht.

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
