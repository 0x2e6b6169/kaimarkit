---
id: 140
title: BE-42 · PUT /api/process fuer Open WebUI als externe Dokumentenextraktion
status: done
priority: medium
created: 2026-09-23T10:00:00+02:00
updated: 2026-09-23T11:30:00+02:00
started: 2026-09-23T10:00:00+02:00
completed: 2026-09-23T11:30:00+02:00
assignee: sophie
tags:
    - backend
    - docs
class: standard
---

## Herkunft

GitHub-Issue #7, „PUT /api/process: Open WebUI als externe Dokumentenextraktion
bedienen“. Das Issue hält die Protokollprüfung gegen
`ghcr.io/open-webui/open-webui:v0.11.3` vom 22.09.2026 fest; dieser Rumpf fasst
zusammen, verbindlich für den Wortlaut des Protokolls bleibt das Issue.

## Ziel

Open WebUI gibt seine Dokumentenextraktion mit `CONTENT_EXTRACTION_ENGINE=external`
an einen fremden Dienst ab und schickt dazu die Rohbytes per
`PUT <EXTERNAL_DOCUMENT_LOADER_URL>/process`. kaimarkit bekommt dafür den Endpunkt
`PUT /api/process`. Er ist eine zweite Tür zu derselben Maschinerie: Registry,
Engine, Rückfall, Semaphor, Zeitgrenze.

## Eigene Dateien

- `backend/app/uploads.py` — Empfang in Blöcken aus einem beliebigen Bytestrom
  herauslösen; `stored_upload()` ruft ihn danach auf
- `backend/app/api/convert.py` — der Endpunkt
- `backend/app/models.py` — `ProcessResponse`
- `backend/app/config.py` — `process_text_fallback`
- `backend/tests/test_process.py`, neu
- `contracts/api.md` — Abschnitt `PUT /api/process`, dazu der Satz, warum
  `frontend/src/types.ts` unverändert bleibt
- `docker/.env.example` und `docs/admin/konfiguration.md` (Abschnitt „Anwendung“) —
  `KAIMARKIT_PROCESS_TEXT_FALLBACK`
- `docs/admin/api.md` — neuer Abschnitt zum Endpunkt
- `docs/admin/openwebui.md`, neu, samt Eintrag in `mkdocs.yml`

Nicht angefasst: `converters/`, die Präferenzlisten, `/api/convert`,
`/api/convert/batch`, `/api/convert/url` und das Frontend.

## Vorgaben

- Rumpf sind die Rohbytes. Kein `await request.body()`, sondern
  `request.stream()`, damit `KAIMARKIT_MAX_FILE_SIZE_MB` beim Empfang greift.
- Name aus `X-Filename`, prozentkodiert; die Endung wählt die Engine. Fehlt der
  Kopf oder die Endung, kommt sie aus dem `Content-Type` wie bei
  `/api/convert/url`. Fehlt beides: 415 `unsupported_format`.
- Antwort `{ "page_content": …, "metadata": {…} }`. `metadata` nur mit `str` und
  `int` — `filename`, `engine`, `duration_ms`, Warnungen als eine Zeichenkette mit
  ` | ` verbunden. Chroma nimmt keine Listen.
- Engine und OCR kommen aus der Umgebung, je Anfrage wählbar ist nichts.
- `KAIMARKIT_PROCESS_TEXT_FALLBACK` (Vorgabe `true`): Führt die Endung auf keine
  Engine, wird der Rumpf als UTF-8 gelesen; gelingt das, ist das Ergebnis der Text,
  `engine` ist `passthrough`, eine Warnung nennt den Grund. Sonst 415. Gilt nur für
  diesen Endpunkt.
- Fehler im selben Umschlag wie überall.

## Prüfung

- Neue Tests in `backend/tests/test_process.py` nach der Liste im Issue: docx als
  Rohrumpf, prozentkodierter Name mit Umlaut, Endung aus dem MIME-Typ, weder Kopf
  noch MIME → 415, `.py` mit und ohne Textrückfall, zu großer Rumpf → 413 ohne
  Rückstand, `metadata` nur `str`/`int`, leerer Rumpf ohne Stacktrace.
- Rot vor grün: die Tests laufen vor der Arbeit gegen den alten Stand und scheitern.
- `pytest -q -rs` und `ruff check .` sauber; Sammelzahl melden.
- `curl -X PUT --data-binary @backend/tests/fixtures/bericht.docx -H 'X-Filename:
  bericht.docx' localhost:8000/api/process` liefert JSON mit `page_content`.
- Gegenprobe mit einem laufenden Open WebUI und die OCR-Messung aus dem Issue
  (Abnahme 3 und 4) brauchen den Container; sie sind nicht Teil dieses Laufs und
  werden gesondert nachgeholt.


## Erledigt (2026-09-23)

`PUT /api/process` steht in `backend/app/api/convert.py`. Den Empfang in Blöcken hat
`uploads.py` als `stored_stream()` herausgelöst; `stored_upload()` ruft ihn auf, der
Endpunkt reicht `request.stream()` hinein. Die Größenprüfung greift also beim Empfang.

Drei Entscheidungen, die das Issue offenließ:

- **Name ohne Endung.** Mit `X-Filename` ohne Endung kommt sie aus dem
  `Content-Type`. Führt der auf nichts, bleibt der Name ohne Endung, und der
  Textrückfall entscheidet (`Makefile`, `LICENSE`). 415 wegen fehlender Endung gibt
  es nur ohne `X-Filename`.
- **Leerer Rumpf** ist 415 `unsupported_format` mit „… ist leer“, unabhängig von
  der Endung. Ein neuer Fehlercode hätte den Dreiklang berührt.
- **Nullbytes** zählen im Textrückfall als binär, obwohl sie gültiges UTF-8 sind.
- `metadata.warnings` fehlt, wenn es keine Warnung gab, statt leer dazustehen.

`docker/docker-compose.yml` reicht die neue Variable durch; ohne diese Zeile wäre
`KAIMARKIT_PROCESS_TEXT_FALLBACK=false` in `docker/.env` wirkungslos geblieben.

**Prüfung.** `backend/tests/test_process.py`, 16 Tests, vor der Arbeit alle rot
(`16 failed`), danach grün. `pytest -q -rs`: 236 gesammelt, 225 ausgewählt,
215 bestanden, 6 übersprungen (Pandoc nicht im PATH), 4 fehlgeschlagen,
11 abgewählt (slow). Die vier Fehlschläge stehen in `test_pandoc.py` und
scheitern vor der Änderung genauso: Diese Umgebung hat kein Pandoc und keine
pyenv-Umgebung `claude-code`; gelaufen ist eine uv-Umgebung mit Python 3.12.
`ruff check .`: sauber.

curl gegen uvicorn: docx liefert `page_content`, `.yaml` kommt als Text zurück,
Binärdaten mit fremder Endung ergeben 415. Zusätzlich lief der echte
`ExternalDocumentLoader` aus dem Wheel `open_webui-0.11.3` gegen den Server
(nur `open_webui.utils.headers` als Attrappe): docx, xlsx, `.py` mit Umlaut im
Namen und eine Adresse mit Schrägstrich am Ende kamen als `Document` an.

**Offen, Abnahme 3 und 4 aus dem Issue:** der Lauf mit einem Open-WebUI-Container
neben dem gebauten kaimarkit-Abbild und die OCR-Messung an einer gescannten Seite.
Beides braucht das Abbild mit Docling.

Merge: `27ea440` (`--no-ff`), Zweig `task/140-process`.
