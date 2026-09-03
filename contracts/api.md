# API-Vertrag

Diese Datei ist die verbindliche Beschreibung der Schnittstelle zwischen Backend und
Frontend. Sie, `backend/app/models.py` und `frontend/src/types.ts` beschreiben
dieselbe Sache und werden **gemeinsam** geändert. Wer nur eine der drei anfasst,
lässt Backend und Frontend auseinanderlaufen, ohne dass es jemand bemerkt.

Alle Endpunkte liegen unter `/api`. Es gibt keine Authentifizierung und keinen
Zustand: Jede Anfrage steht für sich, nichts wird auf dem Server abgelegt.

---

## Gemeinsame Typen

### `ConversionEntry`

Das Ergebnis für **eine** Datei. Tritt einzeln und in Listen auf.

| Feld | Typ | Immer da | Bedeutung |
|---|---|---|---|
| `filename` | string | ja | Name der Eingabedatei, gesäubert (kein Pfadanteil) |
| `status` | `"ok"` \| `"failed"` | ja | ob die Konvertierung gelang |
| `markdown` | string \| null | bei `ok` | das Ergebnis |
| `engine` | string \| null | bei `ok` | welche Engine es erzeugt hat |
| `warnings` | string[] | ja | leer, wenn nichts anzumerken war |
| `duration_ms` | integer | ja | Dauer der Konvertierung |
| `error` | string \| null | bei `failed` | lesbare Meldung, kein Stacktrace |

`markdown` ist bei `status: "failed"` null, `error` bei `status: "ok"` null. Beide
Felder sind immer vorhanden, damit ein Client nicht auf ihr Fehlen prüfen muss.

In `engine` steht neben `markitdown`, `docling` und `pandoc` auch `passthrough`:
Markdown wird durchgereicht, nicht gewandelt. Wählen lässt sich dieser Weg nicht,
er ergibt sich aus der Endung (siehe `GET /api/capabilities`).

### `EngineState`

`"ready"` — nutzbar. `"warming"` — lädt noch, eine Anfrage wartet.
`"unavailable"` — nicht installiert oder defekt, wird nicht angeboten.

### `ErrorResponse`

Jede Fehlerantwort hat denselben Rumpf:

```json
{ "detail": "Datei ist groesser als 50 MB.", "code": "file_too_large" }
```

| `code` | HTTP | Anlass |
|---|---|---|
| `file_too_large` | 413 | über `KAIMARKIT_MAX_FILE_SIZE_MB` |
| `too_many_files` | 413 | über `KAIMARKIT_MAX_FILES` |
| `unsupported_format` | 415 | Endung in keiner Präferenzliste |
| `engine_unsuitable` | 400 | angeforderte Engine kann dieses Format nicht |
| `engine_unavailable` | 400 | angeforderte Engine ist nicht installiert |
| `conversion_failed` | 500 | die Engine scheiterte |
| `conversion_timeout` | 504 | über `KAIMARKIT_CONVERSION_TIMEOUT` |
| `invalid_url` | 400 | Adresse für `/api/convert/url` taugt nicht: kein öffentliches http(s), nicht auflösbar, Weiterleitung ins Private, zu viele Weiterleitungen, keine Antwort mit Dokument |

### `UrlConvertRequest`

Der Rumpf von `POST /api/convert/url`, als JSON.

| Feld | Typ | Pflicht | Bedeutung |
|---|---|---|---|
| `url` | string | ja | die Adresse, `http` oder `https` |
| `engine` | string | nein | Enginename oder `auto` (Standard) |
| `ocr` | boolean \| null | nein | überschreibt `KAIMARKIT_OCR_ENABLED` |

---

## `GET /api/health`

Antwortet **sofort** mit 200, auch während Docling im Hintergrund lädt. Der
Container-Healthcheck hängt daran; eine Antwort erst nach dem Laden der Modelle
würde den Start als Fehlschlag erscheinen lassen.

```json
{ "status": "ok", "version": "v0.1.0-12-ga22a6c5" }
```

Die Version ist die des gebauten Abbilds: Der Bau setzt `KAIMARKIT_VERSION` auf das
Ergebnis von `git describe --tags --always --dirty` — `v0.1.0` auf dem Tag,
`v0.1.0-12-ga22a6c5` zwölf Commits dahinter, mit `-dirty` bei Änderungen im
Arbeitsbaum. Fehlt die Variable, meldet der Dienst `__version__` aus
`app/__init__.py`: dieselbe Nummer wie auf dem Tag, ohne das `v`.

```bash
curl -sf localhost:8000/api/health
```

---

## `GET /api/capabilities`

Was dieser Dienst kann. Das Frontend baut daraus seine Auswahl und bietet nichts an,
was ohnehin scheitern würde.

```json
{
  "formats": {
    ".pdf":  ["docling", "markitdown"],
    ".docx": ["markitdown", "docling", "pandoc"],
    ".epub": ["pandoc", "markitdown"],
    ".md":   ["passthrough"]
  },
  "engines": {
    "markitdown": "ready",
    "docling":    "warming",
    "pandoc":     "ready"
  },
  "limits": {
    "max_file_size_mb":    50,
    "max_files":           20,
    "conversion_timeout_s": 600
  },
  "ocr_available": true,
  "default_engine": "auto"
}
```

Die Reihenfolge in `formats` ist die Präferenz: Der erste Eintrag wird bei
`engine: auto` genommen. Eine Engine im Zustand `unavailable` taucht in `formats`
nicht auf.

**`engines` nennt nur, wozwischen sich wählen lässt:** `markitdown`, `docling`,
`pandoc`. Markdown braucht keine davon — es wird gelesen und unverändert
zurückgegeben. `formats` führt `.md` deshalb mit dem Namen `passthrough`, und
derselbe Name steht anschließend im Feld `engine` des Ergebnisses. In `engines`
taucht er nicht auf, weil es dort nichts zu wählen gibt.

```bash
curl -sf localhost:8000/api/capabilities | jq .
```

---

## `POST /api/convert`

Eine Datei nach Markdown. `multipart/form-data`.

| Feld | Typ | Pflicht | Bedeutung |
|---|---|---|---|
| `file` | Datei | ja | die Eingabe |
| `engine` | string | nein | Enginename oder `auto` (Standard) |
| `ocr` | boolean | nein | überschreibt `KAIMARKIT_OCR_ENABLED` |

Eine ausdrücklich genannte Engine wird **nie** durch eine andere ersetzt. Kann sie
das Format nicht, antwortet der Dienst mit 400 statt still etwas anderes zu nehmen.

**Die Antwort richtet sich nach `Accept`:**

*Ohne Angabe oder `text/markdown`* — der Rumpf ist das Markdown, dazu
`Content-Disposition: attachment; filename="<name>.md"`. So liefert `curl -O` direkt
die fertige Datei. Engine und Warnungen stehen in den Kopfzeilen `X-Engine` und
`X-Warnings`.

```bash
curl -sf -F file=@bericht.pdf localhost:8000/api/convert -o bericht.md
```

*`application/json`* — ein `ConversionEntry`:

```bash
curl -sf -F file=@bericht.pdf -F engine=markitdown \
     -H 'Accept: application/json' localhost:8000/api/convert
```

```json
{
  "filename": "bericht.pdf",
  "status": "ok",
  "markdown": "# Bericht\n\n...",
  "engine": "markitdown",
  "warnings": ["Seite 4 enthielt ein Bild, das durch einen Platzhalter ersetzt wurde."],
  "duration_ms": 412,
  "error": null
}
```

Ein Fehlschlag der Engine ist hier **kein** 200 mit `status: "failed"`, sondern ein
Fehlercode. `status: "failed"` gibt es nur im Stapel, wo eine Datei scheitern darf,
ohne die übrigen mitzunehmen.

---

## `POST /api/convert/batch`

Mehrere Dateien in einem Aufruf. Gedacht für die Nutzung per Skript — das Frontend
ruft stattdessen `/api/convert` je Datei auf, weil es Fortschritt und Vorschau
einzeln zeigt.

Felder wie oben, `file` mehrfach. Höchstens `KAIMARKIT_MAX_FILES` Dateien.

**Ein Fehler bei einer Datei bricht den Stapel nicht ab.**

*Ohne Angabe oder `application/zip`* — ein ZIP mit je einer `.md` pro gelungener
Datei. Scheiterte etwas, liegt zusätzlich eine `_errors.txt` darin, eine Zeile je
Datei. Gleiche Namen werden durchnummeriert (`bericht.md`, `bericht-2.md`).

```bash
curl -sf -F file=@a.pdf -F file=@b.epub -F file=@c.docx \
     localhost:8000/api/convert/batch -o ergebnis.zip
```

*`application/json`* — eine Liste von `ConversionEntry`:

```json
{
  "entries": [
    { "filename": "a.pdf", "status": "ok", "markdown": "...", "engine": "docling",
      "warnings": [], "duration_ms": 3120, "error": null },
    { "filename": "b.epub", "status": "failed", "markdown": null, "engine": null,
      "warnings": [], "duration_ms": 88,
      "error": "pandoc: konnte die Datei nicht lesen (beschaedigtes Archiv)" }
  ],
  "total": 2,
  "succeeded": 1,
  "failed": 1
}
```

Der Aufruf antwortet mit 200, auch wenn jede einzelne Datei scheiterte — die
Anfrage selbst war ja in Ordnung. Auch eine unbekannte Endung bleibt ein Fehler ihres
Eintrags: Was `/api/convert` mit 415 abweist, wird hier zu `status: "failed"` mit dem
Grund in `error`. Für den Stapel als Ganzes bleibt allein 413 (zu viele Dateien).

---

## `POST /api/convert/url`

Eine Seite aus dem Netz nach Markdown. Der Rumpf ist ein `UrlConvertRequest`,
ein Aufruf je Adresse — das Frontend ruft ihn je Zeile auf, wie `/api/convert` je
Datei.

```bash
curl -sf -H 'Content-Type: application/json' \
     -d '{"url": "https://example.com/"}' localhost:8000/api/convert/url
```

Die Antwort ist immer ein `ConversionEntry`; einen Markdown-Zweig über `Accept`
gibt es hier nicht.

```json
{
  "filename": "example-domain.html",
  "status": "ok",
  "markdown": "# Example Domain\n\n...",
  "engine": "markitdown",
  "warnings": [],
  "duration_ms": 412,
  "error": null
}
```

**`filename` ist abgeleitet, nicht übernommen.** Der Name kommt aus dem `<title>`
der Seite: Kleinbuchstaben, Umlaute umgeschrieben (`ä` → `ae`, `ß` → `ss`), alles
außer `[a-z0-9]` zu `-`, Mehrfach-Bindestriche zusammengezogen, Ränder beschnitten,
höchstens 80 Zeichen. Ohne `<title>` — bei einer PDF etwa — entsteht er auf dieselbe
Art aus Host und Pfad: `https://example.org/papers/paper.pdf` wird zu
`example-org-papers-paper.pdf`. Die Endung ist die der geholten Datei, aus dem
`Content-Type` (`text/html` → `.html`, `application/pdf` → `.pdf`) oder sonst aus
dem Pfad; das Frontend macht daraus `.md`, wie bei einem Upload. Gleiche Namen
nummeriert der Client, nicht der Dienst.

**Nur öffentliches http(s).** Loopback, private Netze, Link-local und alles, was
nicht öffentlich erreichbar ist, weist der Dienst mit 400 `invalid_url` ab — auch
dann, wenn erst eine Weiterleitung dorthin führt. Der Hostname wird aufgelöst und
jede zurückgegebene Adresse geprüft. Höchstens fünf Weiterleitungen. Kein
JavaScript: Was der Server als HTML liefert, ist die Seite.

Danach geht die Datei denselben Weg wie ein Upload: Registry, Engine, Rückfall.
Deshalb gelten dieselben Fehler wie bei `/api/convert`, dazu `invalid_url`. Die
Antwort des fernen Servers unterliegt `KAIMARKIT_MAX_FILE_SIZE_MB` (413, abgebrochen
beim Empfang), der Abruf `KAIMARKIT_URL_TIMEOUT` (504) und die Umwandlung
`KAIMARKIT_CONVERSION_TIMEOUT` (504). Führt der `Content-Type` auf keine bekannte
Endung und der Pfad auch nicht, antwortet der Dienst mit 415.
