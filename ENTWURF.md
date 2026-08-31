# kaimarkit — Entwurf

Der ursprüngliche Entwurf, aus dem dieses Projekt entstanden ist, aufgezeichnet am
31.08.2026. Er ist die **Herkunft**, nicht die Vorschrift: Wo er und der Quelltext
auseinandergehen, gilt der Quelltext.

Verbindlich sind, in dieser Reihenfolge:

- `contracts/api.md` — der Schnittstellenvertrag
- `CLAUDE.md` — Befehle, Konventionen, Arbeitsweise
- das Board unter `kanban/` — was gebaut wird und was gilt
- `docs/` — Betrieb und Bedienung

Der Entwurf bleibt hier, weil zwei Dinge in ihm stehen, die sonst nirgends stehen:
die Begründungen der frühen Entscheidungen und der Abschnitt „Prüfung am Ende",
auf den INT-2 (#30) sich beruft.

---


## Kontext

Wer einem LLM ein PDF, ePub oder docx als Kontext geben will, liefert es heute roh ab
und weiß nicht, was das Modell daraus liest. kaimarkit schiebt einen sichtbaren Schritt
dazwischen: Die Datei wird zu Markdown, das Ergebnis lässt sich vor der Weitergabe
ansehen, prüfen und bei Bedarf verwerfen oder nachbessern.

Das Verzeichnis ist leer, das Git-Repo hat keine Commits — alles entsteht neu.

Die Anwendung besteht aus einem FastAPI-Backend mit drei austauschbaren
Konvertierungs-Engines, einem Vue-Frontend zum Hochladen und Ansehen und einem
Docker-Image, das beides ausliefert. Der Betrieb läuft über drei aufeinander
aufbauende Compose-Dateien, gesteuert allein durch `.env`.

**Entscheidungen aus der Rückfrage:** drei Engines (MarkItDown, Docling, Pandoc — Pandoc
ohne PDF), ein Container, synchrone Verarbeitung mit Limits, Frontend mit Upload,
Vorschau und Download, Docling-Modelle ins Image gebacken, Tesseract-OCR abschaltbar,
Bilder verwerfen und durch Platzhalter ersetzen.

---

## Verzeichnisaufbau

```
kaimarkit/
├── backend/
│   ├── app/
│   │   ├── main.py              FastAPI-App, SPA-Mount, Router, Lifespan
│   │   ├── config.py            pydantic-settings, alle KAIMARKIT_*-Variablen
│   │   ├── models.py            Pydantic-Schemas für Anfrage und Antwort
│   │   ├── errors.py            ConversionError-Hierarchie, Exception-Handler
│   │   ├── api/
│   │   │   ├── convert.py       POST /api/convert, POST /api/convert/batch
│   │   │   └── meta.py          GET /api/health, GET /api/capabilities
│   │   ├── converters/
│   │   │   ├── base.py          Protokoll Converter + Ergebnistyp
│   │   │   ├── registry.py      Fähigkeitsmatrix, Auswahl, Fallback
│   │   │   ├── markitdown.py
│   │   │   ├── docling.py
│   │   │   └── pandoc.py
│   │   ├── uploads.py           Streaming-Empfang mit Größenlimit, Tempfiles
│   │   └── packaging.py         ZIP-Bau, Dateinamen säubern, Kollisionen lösen
│   ├── tests/
│   │   ├── fixtures/            je eine winzige Beispieldatei pro Format
│   │   ├── test_registry.py
│   │   ├── test_api.py
│   │   ├── test_packaging.py
│   │   └── test_converters.py   Engine-Smoketests, Docling als "slow" markiert
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── components/          FileDropZone, FileQueue, FileRow,
│   │   │                        MarkdownPreview, OptionsPanel, EngineSelect
│   │   ├── composables/         useConversion.ts, useCapabilities.ts
│   │   ├── mocks/               Mock-Server für /api, entfällt mit INT-1
│   │   ├── api.ts               Client für /api
│   │   ├── download.ts          Einzeldatei und ZIP über jszip
│   │   ├── style.css
│   │   └── types.ts
│   ├── index.html
│   ├── vite.config.ts
│   └── package.json
├── docker/
│   ├── Dockerfile                   Multi-Stage: Frontend, Python-Build, Runtime
│   ├── docker-compose.yml           lokaler Betrieb, Port veröffentlicht
│   ├── docker-compose.traefik.yml   Ergänzung: Traefik-Labels, externes Netz
│   ├── docker-compose.authelia.yml  Ergänzung: ForwardAuth-Middleware
│   └── .env.example                 Vorlage für docker/.env
├── docs/
│   ├── index.md                 Was kaimarkit ist und wofür
│   ├── schnellstart.md
│   ├── formate.md               Format-Engine-Tabelle, Stärken und Schwächen
│   ├── api.md                   Endpunkte mit curl-Beispielen
│   ├── betrieb/
│   │   ├── konfiguration.md     jede .env-Variable mit Wirkung
│   │   ├── lokal.md
│   │   ├── traefik.md
│   │   └── authelia.md
│   ├── entwicklung.md           Aufbau, eine Engine ergänzen, Board
│   └── grenzen.md               was das Werkzeug nicht kann
├── mkdocs.yml
├── contracts/
│   └── api.md                   verbindliche Schnittstelle zwischen den Strängen
├── kanban/tasks/                kanban-md-Board
├── CLAUDE.md                    Projektgedächtnis für alle Agenten
├── .dockerignore
├── Makefile
└── README.md
```

`.dockerignore` bleibt im Projektwurzelverzeichnis: Docker liest die Datei aus dem
Wurzelverzeichnis des Build-Kontexts, nicht aus dem Verzeichnis der Compose-Datei.
BuildKit würde zwar auch `docker/Dockerfile.dockerignore` erkennen, doch die Datei im
Wurzelverzeichnis gilt für jeden Build-Aufruf, auch für ein blankes `docker build`.

---

## Backend

### Das Converter-Protokoll

`converters/base.py` definiert die schmalste Schnittstelle, die drei sehr
unterschiedliche Werkzeuge gemeinsam haben:

```python
class ConversionResult(NamedTuple):
    markdown: str
    engine: str
    warnings: list[str]
    duration_ms: int

class Converter(Protocol):
    name: str
    extensions: frozenset[str]
    def available(self) -> bool: ...
    def convert(self, path: Path, opts: ConvertOptions) -> ConversionResult: ...
```

Jede Engine kapselt ihre Eigenheiten hinter dieser Schnittstelle und übersetzt eigene
Ausnahmen in `ConversionError` aus `errors.py`. Nichts außerhalb von `converters/`
importiert markitdown, docling oder ruft pandoc auf.

### Fähigkeitsmatrix und Auswahl

`registry.py` hält pro Dateiendung eine Präferenzliste. Sie steht im Code, nicht in der
Konfiguration — sie beschreibt, was die Bibliotheken können, und das ändert sich mit
den Abhängigkeiten, nicht mit dem Deployment:

| Endung | Präferenz (erste Wahl zuerst) |
|---|---|
| `.pdf` | docling, markitdown |
| `.docx` | markitdown, docling, pandoc |
| `.epub` | pandoc, markitdown |
| `.pptx`, `.xlsx` | markitdown, docling |
| `.html`, `.htm` | markitdown, pandoc, docling |
| `.odt`, `.rtf`, `.tex`, `.rst`, `.org` | pandoc |
| `.csv`, `.json`, `.xml`, `.txt` | markitdown |
| `.png`, `.jpg`, `.tiff` | docling (mit OCR), markitdown |
| `.md`, `.markdown` | Durchreichen, keine Engine |

Pandoc taucht bei `.pdf` nicht auf — es kann PDF nicht lesen.

Drei Funktionen genügen:

- `engines_for(ext) -> list[str]` — was geht überhaupt, für `/api/capabilities`
- `select(ext, requested: str | None) -> Converter` — `None` heißt Präferenzliste,
  ein Name heißt genau diese Engine oder ein Fehler mit Klartext
- `convert_with_fallback(...)` — schlägt die erste Engine fehl, versucht die nächste
  und schreibt den Grund in `warnings`. Über `KAIMARKIT_ENABLE_FALLBACK` abschaltbar,
  denn wer eine Engine ausdrücklich nennt, will keine andere.

`KAIMARKIT_DEFAULT_ENGINE` (`auto` | Enginename) überschreibt die Präferenzliste global.

### Die drei Engines

**MarkItDown** — `MarkItDown(enable_plugins=False)`, Aufruf `convert(path)`. Läuft in
Millisekunden, deckt die meisten Formate ab. Bilder werden ohne LLM-Client ohnehin nur
als Alt-Text übernommen, das entspricht der gewünschten Platzhalter-Behandlung.

**Docling** — ein `DocumentConverter` wird beim Start einmal gebaut und
wiederverwendet; ihn pro Anfrage neu zu erzeugen kostet Sekunden. Der Aufbau geschieht
im FastAPI-Lifespan in einem Thread, damit der Health-Endpunkt sofort antwortet;
solange er läuft, meldet `/api/capabilities` Docling als `warming`. Export über
`document.export_to_markdown(image_mode=ImageRefMode.PLACEHOLDER)`. `PdfPipelineOptions`
setzt `do_ocr` aus der Anfrage beziehungsweise `KAIMARKIT_OCR_ENABLED`,
`do_table_structure=True` und `generate_picture_images=False`. `artifacts_path` zeigt
auf die ins Image gebackenen Modelle, damit zur Laufzeit nichts nachgeladen wird.

**Pandoc** — `subprocess.run` mit Argumentliste, niemals `shell=True`, mit
`--sandbox` (Pandoc soll auf keine Datei außer der Eingabe zugreifen),
`--to=gfm-raw_html`, `--wrap=none`, `--extract-media=/dev/null` als Bildbremse und
einem Timeout aus `KAIMARKIT_PANDOC_TIMEOUT`. Ein Rückgabewert ungleich null wird mit
den ersten Zeilen von stderr zu einem `ConversionError`.

### Die Endpunkte

```
GET  /api/health        Liveness, antwortet auch während Docling noch lädt
GET  /api/capabilities  Formate, Engines je Format, Limits, ob OCR verfügbar ist
POST /api/convert       eine Datei  → Markdown oder JSON
POST /api/convert/batch mehrere     → ZIP oder JSON
```

`POST /api/convert` nimmt multipart mit `file` und den Formularfeldern `engine`
(optional), `ocr` (optional, überschreibt den Default). Die Antwort richtet sich nach
`Accept`: ohne Angabe `text/markdown` mit `Content-Disposition` — so liefert
`curl -O` direkt die `.md`-Datei; mit `application/json` das vollständige Ergebnis
samt `engine`, `warnings` und `duration_ms`. Das Frontend nutzt die JSON-Form.

`POST /api/convert/batch` existiert für API-Nutzung und liefert ein ZIP. Das Frontend
ruft stattdessen `/api/convert` pro Datei auf, weil es Fortschritt und Vorschau je
Datei zeigen soll, und packt das ZIP im Browser.

Fehler pro Datei brechen den Stapel nicht ab. Im JSON steht pro Eintrag `status`
(`ok` | `failed`), im ZIP liegt neben den `.md`-Dateien eine `_errors.txt`, wenn etwas
fehlschlug.

### Grenzen und Nebenläufigkeit

Konvertieren ist rechenintensiv und blockiert. Jeder Aufruf läuft über
`anyio.to_thread.run_sync`, davor liegt ein `asyncio.Semaphore` aus
`KAIMARKIT_MAX_CONCURRENT`. Ohne diese Bremse legen drei parallele Docling-Läufe den
Container lahm.

Uploads werden in Blöcken in eine `NamedTemporaryFile` geschrieben und beim
Überschreiten von `KAIMARKIT_MAX_FILE_SIZE_MB` abgebrochen — die Prüfung nach dem
vollständigen Einlesen käme zu spät. Temporäre Dateien räumt ein `finally` weg, auch
im Fehlerfall. Endungen außerhalb der Matrix lehnt die API mit 415 ab.

Eine Zeitgrenze je Datei (`KAIMARKIT_CONVERSION_TIMEOUT`) beendet den Wartevorgang und
meldet 504; der Thread selbst lässt sich nicht abbrechen, deshalb zählt das Semaphor
ihn weiter, bis er endet. Diese Einschränkung gehört ins README.

### Auslieferung der statischen Teile

`main.py` hängt drei Dinge ein, in dieser Reihenfolge — die letzte Einhängung fängt
alles ab, was übrig bleibt:

1. `/api` — die Router
2. `/docs` — die gebaute Dokumentation als `StaticFiles(html=True)`
3. `/` — `frontend/dist`, unbekannte Pfade beantwortet die `index.html`, damit ein
   Neuladen auf einer Unterseite funktioniert

Weil `/docs` an die Dokumentation geht, zieht FastAPIs eigene Oberfläche um:
`FastAPI(docs_url="/api/docs", redoc_url="/api/redoc",
openapi_url="/api/openapi.json")`. Das passt ohnehin besser, weil alles Maschinelle
unter `/api` liegt.

CORS bleibt aus — gleiche Herkunft, ein Container.

---

## Frontend

Vue 3 mit Composition API, TypeScript, Vite und Tailwind. Kein Pinia: Der Zustand
lebt in einem Composable `useConversion`, das eine Liste von Dateieinträgen hält.
Vue Router entfällt, die Anwendung hat eine Seite.

Ablauf: Dateien per Drag & Drop oder Dateiauswahl hinzufügen, jede erscheint sofort
als Zeile mit Status. Zwei Konvertierungen laufen gleichzeitig, die übrigen warten.
Fertige Zeilen lassen sich aufklappen und zeigen zwei Reiter — gerendertes Markdown
(`markdown-it`, durch `DOMPurify` gefiltert) und Rohtext. Je Zeile: kopieren,
einzeln herunterladen. Über allem: alles als ZIP herunterladen (`jszip`, im Browser
gebaut) und alles verwerfen.

Die Engine-Auswahl steht auf „automatisch" und listet daneben, was
`/api/capabilities` für die vorhandenen Formate hergibt. Ein Schalter für OCR
erscheint nur, wenn das Backend OCR meldet. Warnungen aus der Konvertierung stehen
sichtbar an der Zeile, denn genau dort entscheidet sich, ob das Ergebnis taugt.

Gestaltung: ruhiges, flächiges Layout, ein Akzentton, Dark Mode über
`prefers-color-scheme`, Statusfarben zusätzlich durch Symbol und Text unterschieden.
Die Dropzone ist per Tastatur erreichbar, Statusänderungen laufen über `aria-live`.

Vite proxyt in der Entwicklung `/api` auf `localhost:8000`.

---

## Dokumentation

MkDocs mit dem Material-Theme, versioniert durch `mike`, ausgeliefert vom Container
selbst unter `/docs`. Geschrieben auf Deutsch nach den Prosa-Regeln; Bezeichner,
Codebeispiele und Variablennamen bleiben englisch.

### Wo die Versionen herkommen

`mike` verwaltet die Fassungen in einem eigenen Wurzelzweig `gh-pages` — jede Version
in einem Unterverzeichnis, dazu eine `versions.json`, aus der Material den
Auswahl-Dropdown speist. Der Zweig hat keine gemeinsame Historie mit `main` und bläht
das Repo deshalb kaum auf.

Entscheidend ist die Trennung: **`mike` läuft beim Veröffentlichen, nicht beim
Container-Build.** Der Docker-Build liest nur das fertige Ergebnis. Andernfalls hinge
jeder Build davon ab, ob die vollständige Git-Historie im Kontext liegt, und ein
flacher Klon würde ihn scheitern lassen.

```bash
make docs-serve                     # mkdocs serve, Vorschau auf :8001
make docs-release VERSION=0.3       # mike deploy --update-aliases 0.3 latest
                                    # + mike set-default latest
```

Die Docs-Stufe im Dockerfile exportiert den Zweig mit
`git archive gh-pages | tar -x -C /docs-site`. Fehlt der Zweig — frischer Klon, noch
kein Release —, baut sie stattdessen die aktuelle Fassung als einzige Version. So
gelingt der Build auch beim allerersten Mal, und der Versionsauswahl fehlen dann eben
die älteren Einträge.

### `mkdocs.yml`

```yaml
site_name: kaimarkit
site_url: /docs/           # Unterpfad, nicht Wurzel — sonst brechen die Links
theme:
  name: material
  language: de
  features: [navigation.sections, navigation.top, content.code.copy,
             search.suggest, toc.follow]
  palette:                 # Umschalter hell/dunkel, Standard folgt dem System
extra:
  version:
    provider: mike
    default: latest
plugins:
  - search: { lang: de }
markdown_extensions:       # admonition, pymdownx.superfences, pymdownx.tabbed,
                           # tables, attr_list, pymdownx.highlight
```

Ein Hinweis, der bei `site_url` leicht zu übersehen ist: Steht dort die Wurzel,
verlinkt der Versions-Dropdown auf `/0.3/` statt `/docs/0.3/` und läuft ins Leere.

### Was hineingehört und was nicht

Die Dokumentation ist die einzige Quelle für Betrieb und Bedienung. Deshalb entfällt
`docker/README.md` — der Betriebsteil steht in `docs/betrieb/`, sonst pflegt niemand
beide. Das Wurzel-`README.md` bleibt kurz: was das Werkzeug tut, wie man es startet,
Verweis auf `/docs`.

`docs/betrieb/konfiguration.md` und `docker/.env.example` beschreiben dieselben
Variablen und werden gemeinsam geändert — dieselbe Regel wie beim
Schnittstellen-Dreiklang, und sie gehört in `CLAUDE.md`.

Die Abhängigkeiten (`mkdocs-material`, `mike`) liegen in einer eigenen Gruppe in
`backend/pyproject.toml`, damit sie nicht in die Laufzeit des Containers geraten.

---

## Docker

### `docker/Dockerfile`

Der Build-Kontext ist das Projektwurzelverzeichnis, nicht `docker/`. Alle `COPY`-Pfade
lauten deshalb `backend/`, `frontend/` und so weiter — das Dockerfile liegt zwar in
einem Unterverzeichnis, sieht den Baum aber von oben.

Fünf Stufen:

1. `node:22-alpine` — `npm ci`, `npm run build`, Ergebnis `frontend/dist`
2. `python:3.12-slim` als Builder — venv, Abhängigkeiten. **Torch aus dem CPU-Index**
   (`--extra-index-url https://download.pytorch.org/whl/cpu`); die Standard-Wheels
   ziehen CUDA-Bibliotheken nach und blähen das Image um rund zwei Gigabyte auf.
3. Modell-Stufe — lädt die Docling-Modelle nach `/opt/docling-models`
   (`docling-tools models download`), mit `HF_HOME` auf dasselbe Verzeichnis
4. Docs-Stufe — `mkdocs-material` und `mike`, dann der Zweig-Export nach `/docs-site`
   mit dem oben beschriebenen Rückfall auf einen einfachen `mkdocs build`. Braucht
   `.git` im Kontext, weshalb `.dockerignore` das Verzeichnis nicht ausschließt,
   sondern nur den übrigen Ballast (`node_modules`, `__pycache__`, `.venv`,
   `frontend/dist`, `kanban/`).
5. Runtime `python:3.12-slim` — venv, Modelle, `dist`, `/docs-site` und die App;
   per apt `tesseract-ocr`, `tesseract-ocr-deu`, `tesseract-ocr-eng`; Pandoc als
   `.deb` von GitHub mit einer über `ARG PANDOC_VERSION` gepinnten Version.
   Non-root-Benutzer, `DOCLING_ARTIFACTS_PATH` und `HF_HOME` gesetzt,
   `HF_HUB_OFFLINE=1`, `HEALTHCHECK` auf `/api/health`.

Start über `uvicorn` mit `--proxy-headers --forwarded-allow-ips=*`, Workerzahl aus
`KAIMARKIT_WORKERS`. Achtung: Jeder Worker hält eigene Docling-Modelle im Speicher —
der Standard bleibt bei 1, das gehört in `.env.example` als Kommentar.

Zu erwarten sind rund 3 bis 4 GB Image. Wer das nicht will, kann später eine
`ARG WITH_DOCLING=false`-Variante bauen; jetzt wäre das ungefragte Flexibilität.

### Compose-Schichten

Alle drei Dateien liegen in `docker/` und lesen ausschließlich aus `docker/.env` —
auch Netzwerk-, Service- und Projektname sowie der Pfad zu den Quellen.

Zwei Folgen daraus, die in den Dateien berücksichtigt sein müssen:

- Compose leitet das Projektverzeichnis aus der ersten `-f`-Datei ab. Es liest also
  `docker/.env`, und alle relativen Pfade in den Compose-Dateien beziehen sich auf
  `docker/`.
- Damit hieße das Projekt „docker". Ein Top-Level-`name: ${KAIMARKIT_PROJECT_NAME}`
  setzt das gerade.

**`docker/docker-compose.yml`** — lokaler Betrieb:

```yaml
name: ${KAIMARKIT_PROJECT_NAME}

services:
  kaimarkit:
    build:
      context: ${KAIMARKIT_BUILD_CONTEXT}       # Standard: ..
      dockerfile: ${KAIMARKIT_DOCKERFILE}       # Standard: docker/Dockerfile
      args:
        PANDOC_VERSION: ${PANDOC_VERSION}
    image: ${KAIMARKIT_IMAGE}:${KAIMARKIT_TAG}
    container_name: ${KAIMARKIT_CONTAINER_NAME}
    restart: ${KAIMARKIT_RESTART_POLICY}
    environment: [ ... alle KAIMARKIT_*-Variablen ... ]
    ports: ["${KAIMARKIT_BIND_ADDR}:${KAIMARKIT_HOST_PORT}:8000"]
    healthcheck: { test: [...], interval: ..., start_period: ... }
```

`KAIMARKIT_BUILD_CONTEXT` zeigt standardmäßig auf `..`, also das Wurzelverzeichnis
des Projekts, und `KAIMARKIT_DOCKERFILE` liegt relativ dazu. Wer die Compose-Dateien
anderswohin kopiert oder aus einem zweiten Checkout baut, setzt beide Variablen auf
absolute Pfade — die Compose-Dateien selbst bleiben unverändert.

Zwei Feinheiten: Ein absoluter `context` verlangt ein `dockerfile` relativ zu genau
diesem Kontext, und ein `context` außerhalb des Projekts findet die
`.dockerignore`-Datei im Wurzelverzeichnis des dortigen Baums. Beides gehört als
Kommentar in `.env.example`.

**`docker/docker-compose.traefik.yml`** — ergänzt und nimmt zurück:

```yaml
services:
  kaimarkit:
    ports: !reset []
    networks: [proxy]
    labels:
      traefik.enable: "true"
      traefik.docker.network: "${TRAEFIK_NETWORK}"
      traefik.http.routers.${KAIMARKIT_ROUTER}.rule: "Host(`${KAIMARKIT_DOMAIN}`)"
      traefik.http.routers.${KAIMARKIT_ROUTER}.entrypoints: "${TRAEFIK_ENTRYPOINT}"
      traefik.http.routers.${KAIMARKIT_ROUTER}.tls: "true"
      traefik.http.routers.${KAIMARKIT_ROUTER}.tls.certresolver: "${TRAEFIK_CERTRESOLVER}"
      traefik.http.routers.${KAIMARKIT_ROUTER}.tls.domains[0].main: "${KAIMARKIT_DOMAIN}"
      traefik.http.services.${KAIMARKIT_ROUTER}.loadbalancer.server.port: "8000"
networks:
  proxy:
    name: ${TRAEFIK_NETWORK}
    external: true
```

Labels in Map-Form, nicht als Liste: Compose führt Listen additiv zusammen, wodurch
die Authelia-Schicht dasselbe Label nicht überschreiben könnte. `!reset` verlangt
Compose 2.24 oder neuer — die Versionsanforderung kommt ins README, und falls sie im
Zielsystem fehlt, veröffentlicht stattdessen `docker-compose.local.yml` den Port und
die Basisdatei keinen.

**`docker-compose.authelia.yml`** — definiert die ForwardAuth-Middleware am eigenen
Service, damit die Datei für sich steht, und hängt sie an den Router:

```yaml
traefik.http.middlewares.${AUTH_MIDDLEWARE}.forwardauth.address: "${AUTHELIA_VERIFY_URL}"
traefik.http.middlewares.${AUTH_MIDDLEWARE}.forwardauth.trustForwardHeader: "true"
traefik.http.middlewares.${AUTH_MIDDLEWARE}.forwardauth.authResponseHeaders: "${AUTHELIA_RESPONSE_HEADERS}"
traefik.http.routers.${KAIMARKIT_ROUTER}.middlewares: "${AUTH_MIDDLEWARE}@docker"
```

Aufrufe, aus dem Wurzelverzeichnis:

```bash
docker compose -f docker/docker-compose.yml up -d --build
docker compose -f docker/docker-compose.yml \
               -f docker/docker-compose.traefik.yml up -d --build
docker compose -f docker/docker-compose.yml \
               -f docker/docker-compose.traefik.yml \
               -f docker/docker-compose.authelia.yml up -d --build
```

Das `Makefile` im Wurzelverzeichnis hinterlegt die Dateiketten in einer Variablen
`COMPOSE` und darauf `up`, `up-traefik`, `up-authelia`, `down`, `logs`, `build`
sowie `test`, `lint` und `dev`. Wer aus `docker/` heraus arbeitet, kann die Dateien
auch direkt aufrufen — das Ergebnis ist dasselbe, weil das Projektverzeichnis in
beiden Fällen `docker/` ist.

**Ein Punkt, der Beachtung verlangt:** Hinter Authelia ist auch `/api` geschützt, und
ein `curl` ohne Browser-Sitzung bekommt eine Weiterleitung zum Login. Die
Authelia-Datei enthält deshalb einen zweiten Router für `PathPrefix('/api')` mit
höherer Priorität, dessen Middleware-Liste aus `${KAIMARKIT_API_MIDDLEWARES}` kommt.
Wer `KAIMARKIT_API_MIDDLEWARES` auf die Authelia-Middleware setzt, schützt alles; wer
die API per Skript nutzen will, trägt dort eine IP-Allowlist-Middleware ein. Ob
Traefik einen leeren Wert als „keine Middleware" akzeptiert, prüfe ich bei der
Umsetzung; falls nicht, kommt der Block auskommentiert samt Erklärung ins README.

### `docker/.env.example`

Vollständig dokumentiert, in vier Blöcken:

**Quellen und Build** — `KAIMARKIT_BUILD_CONTEXT=..`,
`KAIMARKIT_DOCKERFILE=docker/Dockerfile`, `PANDOC_VERSION`,
`KAIMARKIT_PROJECT_NAME=kaimarkit`

**Anwendung** — `KAIMARKIT_MAX_FILE_SIZE_MB`, `KAIMARKIT_MAX_FILES`,
`KAIMARKIT_MAX_CONCURRENT`, `KAIMARKIT_CONVERSION_TIMEOUT`,
`KAIMARKIT_DEFAULT_ENGINE`, `KAIMARKIT_ENABLE_FALLBACK`, `KAIMARKIT_OCR_ENABLED`,
`KAIMARKIT_OCR_LANGS`, `KAIMARKIT_LOG_LEVEL`, `KAIMARKIT_WORKERS`,
`KAIMARKIT_STATIC_DIR`, `KAIMARKIT_DOCS_DIR`

**Container** — `KAIMARKIT_IMAGE`, `KAIMARKIT_TAG`, `KAIMARKIT_CONTAINER_NAME`,
`KAIMARKIT_RESTART_POLICY`, `KAIMARKIT_BIND_ADDR`, `KAIMARKIT_HOST_PORT`,
`KAIMARKIT_MEM_LIMIT`

**Traefik und Authelia** — `TRAEFIK_NETWORK`, `TRAEFIK_ENTRYPOINT`,
`TRAEFIK_CERTRESOLVER`, `KAIMARKIT_DOMAIN`, `KAIMARKIT_ROUTER`, `AUTH_MIDDLEWARE`,
`AUTHELIA_VERIFY_URL`, `AUTHELIA_RESPONSE_HEADERS`, `KAIMARKIT_API_MIDDLEWARES`

Compose-Variablen ohne Wert brechen den Aufruf nicht ab, sondern setzen still eine
leere Zeichenkette ein — deshalb steht jede Variable mit einem brauchbaren Wert in der
Vorlage, und das Ticket `IN-2` prüft die aufgelöste Konfiguration auf Lücken.

---

## `CLAUDE.md` im Projekt

Die Datei ist das gemeinsame Gedächtnis der Agenten. Sie beantwortet, was ein neu
gestarteter Agent wissen muss, bevor er eine Zeile schreibt, und sonst nichts —
alles, was im Code steht, gehört nicht hinein.

**Was ist das hier.** Drei Sätze zum Zweck, ein Verweis auf diesen Plan.

**Befehle.** Backend `pyenv activate claude-code && cd backend && uvicorn app.main:app
--reload`, `pytest -q`, `ruff check`; Frontend `npm run dev`, `npm run build`,
`npm run typecheck`; Dokumentation `make docs-serve`, veröffentlichen mit
`make docs-release VERSION=x.y`; Betrieb über die übrigen `make`-Ziele. Ausdrücklich:
kein globales Python, immer die pyenv-Umgebung `claude-code`.

**Verbindliche Konventionen.** Fünf Regeln, die zwischen den Strängen gelten und die
einzeln zu verletzen leicht ist:

1. `contracts/api.md`, `backend/app/models.py` und `frontend/src/types.ts` beschreiben
   dieselbe Schnittstelle. Wer eine der drei Dateien ändert, ändert alle drei im selben
   Commit — sonst laufen Backend und Frontend auseinander, ohne dass es jemand merkt.
2. Außerhalb von `backend/app/converters/` importiert nichts `markitdown`, `docling`
   oder ruft `pandoc` auf.
3. Jede Engine übersetzt ihre eigenen Ausnahmen in `ConversionError` aus `errors.py`.
   Bibliotheksspezifische Fehler dringen nicht bis in die API.
4. Konfiguration kommt ausschließlich aus `KAIMARKIT_*`-Variablen über `config.py`.
   Keine Konstante wird im Code festgeschrieben, die im Betrieb umgestellt werden soll.
5. Der Dienst speichert nichts. Hochgeladene Dateien leben in einer `NamedTemporaryFile`
   und werden im `finally` gelöscht.
6. `docker/.env.example` und `docs/betrieb/konfiguration.md` beschreiben dieselben
   Variablen. Wer eine Variable ergänzt, umbenennt oder streicht, ändert beide Dateien
   im selben Commit. Die Dokumentation ist die einzige Quelle für Betrieb und
   Bedienung — es gibt kein zweites README neben ihr.

**Arbeitsweise am Board.** Ein Ticket, ein Branch `task/<ID>-<kurzname>`, ein Agent.
Jedes Ticket nennt in seinem Rumpf die Dateien, die es besitzt; ein Agent ändert keine
Datei, die einem anderen offenen Ticket gehört. Wer eine solche Änderung braucht,
parkt mit `kanban-md handoff` und beschreibt, was fehlt.

**Boardstand.** Am Ende ein durch `kanban-md context --write-to CLAUDE.md` gepflegter
Block, damit ein neuer Agent den aktuellen Stand ohne weiteren Aufruf sieht.

---

## Tickets

Das Board entsteht mit `kanban-md init --name kaimarkit`. Drei Rollen greifen darauf
zu, erkennbar am Tag: `backend`, `frontend`, `infra`. Ein vierter Tag `docs` sammelt
die Dokumentationstickets; sie verlangen keine eigene Rolle, sondern nur, dass das
beschriebene Stück fertig ist.

Die Kürzel `BE-1`, `FE-3` und so weiter sind keine Board-IDs — die vergibt `kanban-md`
selbst. Sie stehen deshalb vorn im Titel (`BE-2 · Converter-Protokoll …`), damit die
Abhängigkeiten aus diesem Plan im Board wiederzufinden sind; die echten IDs verknüpft
das Anlegeskript über `--depends-on`.

**Wovon die Parallelität abhängt.** Drei Agenten können nur dann nebeneinander
arbeiten, wenn die Schnittstellen zwischen ihnen feststehen, bevor jemand anfängt.
Deshalb steht ein einziges Ticket vor allen anderen und schreibt sie fest: das
API-Schema, die TypeScript-Typen, die Variablenliste und das Verzeichnisgerüst.
Danach berühren sich die Stränge kaum noch.

**Und wovon die Konfliktfreiheit abhängt.** Keine zwei gleichzeitig offenen Tickets
besitzen dieselbe Datei. Zwei Stellen verlangen dafür einen bewussten Schnitt:

- `main.py` gehört allein `BE-1`. Das Ticket legt die App samt aller
  `include_router`-Aufrufe an; die Router-Module existieren zunächst als Stümpfe, die
  `BE-7` und `BE-8` füllen.
- `registry.py` gehört allein `BE-2`. Das Ticket schreibt die vollständige
  Fähigkeitsmatrix mit allen drei Enginenamen und lädt die Module verzögert. Die
  Engine-Tickets liefern nur ihr eigenes Modul und tragen sich nirgends ein.

### Vorlauf

| ID | Titel | Tags | Hängt ab von | Besitzt |
|---|---|---|---|---|
| `SETUP-1` | Verzeichnisgerüst, Board und Schnittstellenvertrag festschreiben | `setup` | — | `contracts/api.md`, `backend/app/models.py`, `frontend/src/types.ts`, `docker/.env.example`, `CLAUDE.md`, `.gitignore` |

`SETUP-1` ist kritisch und blockiert alles. Sein Ergebnis: `contracts/api.md`
beschreibt jeden Endpunkt mit Anfrage, Antwort und Fehlercodes; `models.py` und
`types.ts` bilden ihn ab; `.env.example` listet jede Variable mit Standardwert.
Prüfung: Ein Leser kann aus `contracts/api.md` allein einen Client schreiben.

### Backend

| ID | Titel | Hängt ab von | Besitzt |
|---|---|---|---|
| `BE-1` | FastAPI-Gerüst, `config.py`, `/api/health`, Einhängen von SPA und `/docs`, `pyproject.toml` samt Docs-Gruppe | `SETUP-1` | `pyproject.toml`, `main.py`, `config.py`, `errors.py`, `api/meta.py` |
| `BE-2` | Converter-Protokoll, Fähigkeitsmatrix, Auswahl und Fallback | `SETUP-1` | `converters/base.py`, `converters/registry.py`, `tests/test_registry.py` |
| `BE-3` | MarkItDown-Adapter | `BE-2` | `converters/markitdown.py` |
| `BE-4` | Docling-Adapter mit vorgeladenem Konverter und OCR-Schalter | `BE-2` | `converters/docling.py` |
| `BE-5` | Pandoc-Adapter mit `--sandbox` und Zeitgrenze | `BE-2` | `converters/pandoc.py` |
| `BE-6` | Upload-Strom mit Größenlimit, Tempfiles, Semaphor, Zeitgrenze | `BE-1` | `uploads.py` |
| `BE-7` | `/api/convert` und `/api/capabilities` | `BE-2`, `BE-6` | `api/convert.py` (Einzeldatei-Teil) |
| `BE-8` | `/api/convert/batch` und ZIP-Bau | `BE-7` | `packaging.py`, `api/convert.py` (Stapel-Teil), `tests/test_packaging.py` |
| `BE-9` | Testfixtures und Engine-Smoketests | `BE-3`, `BE-4`, `BE-5` | `tests/fixtures/*`, `tests/test_converters.py`, `tests/test_api.py` |

`BE-3`, `BE-4` und `BE-5` sind untereinander unabhängig — drei Agenten können sie
gleichzeitig nehmen. `BE-7` und `BE-8` teilen sich `api/convert.py` und laufen deshalb
nacheinander.

`BE-1` hängt `/docs` und `/` nur ein, wenn die Verzeichnisse aus
`KAIMARKIT_DOCS_DIR` und `KAIMARKIT_STATIC_DIR` vorhanden sind. In der Entwicklung
gibt es beide nicht, und ohne diese Prüfung ließe sich das Backend allein gar nicht
starten — was den ganzen Backend-Strang an den Docs- und Frontend-Strang koppeln
würde.

### Frontend

| ID | Titel | Hängt ab von | Besitzt |
|---|---|---|---|
| `FE-1` | Vite, Vue 3, TypeScript, Tailwind und ein Mock-Server für `/api` | `SETUP-1` | `package.json`, `vite.config.ts`, `index.html`, `src/main.ts`, `src/mocks/` |
| `FE-2` | API-Client und `useConversion`, `useCapabilities` | `FE-1` | `src/api.ts`, `src/composables/*` |
| `FE-3` | Dropzone und Warteschlange mit Status je Datei | `FE-2` | `components/FileDropZone.vue`, `components/FileQueue.vue`, `components/FileRow.vue` |
| `FE-4` | Vorschau mit `markdown-it` und `DOMPurify`, Rohtext, Kopieren | `FE-2` | `components/MarkdownPreview.vue` |
| `FE-5` | Optionen: Enginewahl und OCR-Schalter aus `/api/capabilities` | `FE-2` | `components/OptionsPanel.vue`, `components/EngineSelect.vue` |
| `FE-6` | Download einzeln und als ZIP über `jszip` | `FE-3` | `src/download.ts` |
| `FE-7` | Gestaltung, Dark Mode, Tastaturbedienung, `aria-live` | `FE-3`, `FE-4`, `FE-5` | `src/App.vue`, `src/style.css` |

Der Mock-Server aus `FE-1` ist der Grund, warum der Frontend-Strang keinen einzigen
Backend-Commit abwarten muss. Er liefert für jede hochgeladene Datei eine feste
Beispielantwort im Format aus `contracts/api.md`, einschließlich eines Falls, der
fehlschlägt, und eines mit Warnungen.

### Infrastruktur

| ID | Titel | Hängt ab von | Besitzt |
|---|---|---|---|
| `IN-1` | `docker/Dockerfile`: fünf Stufen, Torch aus dem CPU-Index, Modelle vorgebacken, Docs-Export | `BE-1`, `FE-1`, `DOC-1` | `docker/Dockerfile`, `.dockerignore` |
| `IN-2` | Compose-Basis und `.env.example` mit Quellenverweis über Variablen | `SETUP-1` | `docker/docker-compose.yml` |
| `IN-3` | Traefik-Ergänzung: Labels in Map-Form, externes Netz, `ports: !reset []` | `IN-2` | `docker/docker-compose.traefik.yml` |
| `IN-4` | Authelia-Ergänzung: ForwardAuth-Middleware und API-Router | `IN-3` | `docker/docker-compose.authelia.yml` |
| `IN-5` | `Makefile` mit allen Zielen einschließlich `docs-serve` und `docs-release` | `IN-2`, `DOC-1` | `Makefile` |

`IN-2` kann sofort nach `SETUP-1` beginnen, denn die Variablenliste steht dann fest.
`IN-4` klärt außerdem die offene Frage, ob Traefik ein leeres `middlewares`-Label
akzeptiert, und hält das Ergebnis in `docs/betrieb/authelia.md` fest.

### Dokumentation

| ID | Titel | Hängt ab von | Besitzt |
|---|---|---|---|
| `DOC-1` | MkDocs, Material-Theme und `mike`: `mkdocs.yml`, Navigation, Seitengerüst | `SETUP-1` | `mkdocs.yml`, `docs/*` als Stümpfe |
| `DOC-2` | Inhalte: Schnellstart, Formate, API, Entwicklung, Grenzen | `DOC-1`, `BE-8` | `docs/index.md`, `docs/schnellstart.md`, `docs/formate.md`, `docs/api.md`, `docs/entwicklung.md`, `docs/grenzen.md` |
| `DOC-3` | Inhalte Betrieb: Konfiguration, lokal, Traefik, Authelia | `DOC-1`, `IN-4` | `docs/betrieb/*` |
| `DOC-4` | Wurzel-`README.md` | `DOC-2` | `README.md` |

`DOC-1` steht früh, weil `IN-1` die Docs-Stufe sonst nicht bauen kann — ein leeres
Gerüst genügt dafür. `DOC-2` und `DOC-3` sind untereinander unabhängig und teilen sich
keine Datei; sie warten nur darauf, dass das jeweils beschriebene Stück fertig ist.

`pyproject.toml` gehört durchgehend `BE-1`. Das Ticket legt die Abhängigkeitsgruppe
`docs` mit `mkdocs-material` und `mike` gleich mit an, damit `DOC-1` die Datei nicht
anfassen muss — sonst kollidierten zwei Tickets, die gleichzeitig laufen sollen.

### Zusammenführung

| ID | Titel | Hängt ab von | Besitzt |
|---|---|---|---|
| `INT-1` | Frontend gegen das echte Backend, Mock entfernen | `BE-9`, `FE-7`, `BE-8` | `frontend/src/mocks/` (Löschung), Fehlerkorrekturen |
| `INT-2` | Ende-zu-Ende-Prüfung im Container nach dem Abschnitt „Prüfung am Ende" | `INT-1`, `IN-5`, `DOC-3` | — |

### Wie ein Agent arbeitet

```bash
kanban-md agent-name                                          # einmal je Sitzung
kanban-md pick --claim <agent> --status todo --move in-progress --tags backend
kanban-md show <ID>                                           # Rumpf nennt die eigenen Dateien
git switch -c task/<ID>-<kurzname>
# … arbeiten, Prüfung des Tickets bestehen …
kanban-md edit <ID> -a "Prüfung bestanden: …" -t --claim <agent>
kanban-md edit <ID> --release && kanban-md move <ID> done
```

Fehlt etwas aus einem anderen Strang, endet die Arbeit nicht im Stillstand, sondern
mit `kanban-md handoff <ID> --claim <agent> --block "…" --note "…" -t --release`.

Jedes Ticket bekommt beim Anlegen einen Rumpf nach demselben Muster: **Ziel** in einem
Satz, **Eigene Dateien** als Liste, **Vorgaben** mit den Festlegungen aus diesem Plan
und **Prüfung** mit dem Befehl, der über fertig oder nicht fertig entscheidet. Ohne den
letzten Abschnitt kann ein Agent das Ticket nicht allein abschließen — er müsste
nachfragen, und genau das soll der Schnitt vermeiden.

---

## Prüfung am Ende

```bash
# Backend
cd backend && pytest -q                       # ohne -m slow: ohne Docling
pytest -q -m slow                             # mit Docling, dauert

# Einzelne Datei über die API
curl -sf -F file=@sample.pdf localhost:8000/api/convert -o sample.md
curl -sf -F file=@sample.pdf -F engine=markitdown \
     -H 'Accept: application/json' localhost:8000/api/convert | jq .warnings

# Stapel als ZIP
curl -sf -F file=@a.pdf -F file=@b.epub -F file=@c.docx \
     localhost:8000/api/convert/batch -o out.zip && unzip -l out.zip

# Grenzen greifen
curl -si -F file=@riesig.pdf localhost:8000/api/convert | head -1   # 413
curl -si -F file=@datei.xyz  localhost:8000/api/convert | head -1   # 415
curl -si -F file=@a.pdf -F engine=pandoc localhost:8000/api/convert | head -1  # 400

# Container
make up && curl -sf localhost:${KAIMARKIT_HOST_PORT}/api/health

# Dokumentation wird ausgeliefert, Versionsauswahl gefüllt, Swagger umgezogen
curl -sf localhost:${KAIMARKIT_HOST_PORT}/docs/ | head -5
curl -sf localhost:${KAIMARKIT_HOST_PORT}/docs/versions.json | jq '.[].version'
curl -sfo /dev/null -w '%{http_code}\n' localhost:${KAIMARKIT_HOST_PORT}/api/docs

# Variablen lückenlos aufgelöst: keine leeren Werte, kein übrig gebliebenes ${...}
docker compose -f docker/docker-compose.yml \
               -f docker/docker-compose.traefik.yml \
               -f docker/docker-compose.authelia.yml config | grep -nE '(\$\{|: *""$)'

# Quellenverweis greift: Build aus einem beliebigen Pfad
KAIMARKIT_BUILD_CONTEXT=$(pwd) docker compose -f docker/docker-compose.yml build
```

Von Hand zu prüfen: ein gescanntes PDF mit und ohne OCR, ein PDF mit einer breiten
Tabelle über MarkItDown und über Docling im Vergleich, ein ePub über Pandoc, und ein
Durchlauf im Browser mit gemischten Dateien einschließlich einer, die fehlschlägt.
Für die Dokumentation: nach einem zweiten `make docs-release` zwischen beiden
Versionen umschalten und prüfen, dass die Links im Dropdown auf `/docs/<version>/`
zeigen und nicht auf die Wurzel.

---

## Ausdrücklich nicht enthalten

Authentifizierung im Tool, Job-Queue, Datenbank, Speichern der Ergebnisse auf dem
Server, In-Browser-Editor, LLM-gestützte Bildbeschreibung, CI-Pipeline. Der
In-Browser-Editor lässt sich später ergänzen, ohne die API zu ändern.
