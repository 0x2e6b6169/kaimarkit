---
id: 23
title: 'IN-1 · docker/Dockerfile: fuenf Stufen, Torch aus dem CPU-Index, Modelle vorgebacken'
status: done
priority: high
created: 2026-08-31T10:21:38.706562102+02:00
updated: 2026-08-31T11:19:19.429926142+02:00
started: 2026-08-31T11:18:43.732387269+02:00
completed: 2026-08-31T11:18:43.732387269+02:00
assignee: akar
tags:
    - infra
depends_on:
    - 4
    - 13
    - 20
class: standard
---

## Ziel

Ein Image, das ueberall aus dem Quelltext gebaut werden kann und ohne Netzzugriff
arbeitet.

## Eigene Dateien

- `docker/Dockerfile`
- `.dockerignore`

## Vorgaben

Der Build-Kontext ist das Projektwurzelverzeichnis, nicht `docker/`. Alle
`COPY`-Pfade lauten deshalb `backend/`, `frontend/` und so weiter.

Fuenf Stufen:

1. `node:22-alpine` - `npm ci`, `npm run build` -> `frontend/dist`
2. `python:3.12-slim` Builder - venv, Abhaengigkeiten. **Torch aus dem CPU-Index**
   (`--extra-index-url https://download.pytorch.org/whl/cpu`). Die Standard-Wheels
   ziehen CUDA-Bibliotheken nach und blaehen das Image um rund zwei Gigabyte auf.
3. Modell-Stufe - `docling-tools models download` nach `/opt/docling-models`,
   `HF_HOME` auf dasselbe Verzeichnis.
4. Docs-Stufe - `git archive gh-pages | tar -x -C /docs-site`. **Fehlt der Zweig**
   (frischer Klon, noch kein Release), baut die Stufe stattdessen die aktuelle
   Fassung mit `mkdocs build`. Ohne diesen Rueckfall scheitert der allererste Build.
5. Runtime `python:3.12-slim` - venv, Modelle, `dist`, `/docs-site`, App. Per apt
   `tesseract-ocr`, `tesseract-ocr-deu`, `tesseract-ocr-eng`. Pandoc als `.deb` von
   GitHub, Version ueber `ARG PANDOC_VERSION` gepinnt. Non-root-Benutzer.
   `DOCLING_ARTIFACTS_PATH`, `HF_HOME`, `HF_HUB_OFFLINE=1`. HEALTHCHECK auf
   `/api/health`.

- `.dockerignore` schliesst `.git` **nicht** aus - die Docs-Stufe braucht den
  Zweig. Ausgeschlossen werden `node_modules`, `__pycache__`, `.venv`,
  `frontend/dist`, `kanban/`.
- Start ueber uvicorn mit `--proxy-headers --forwarded-allow-ips=*`, Workerzahl aus
  `KAIMARKIT_WORKERS`, Standard 1. Jeder Worker haelt eigene Docling-Modelle im
  Speicher.

## Pruefung

`docker build -f docker/Dockerfile .` laeuft in einem frischen Klon ohne
`gh-pages`-Zweig durch. `docker run` antwortet auf `/api/health` und liefert
`/docs/`. Eine Docling-Konvertierung gelingt bei gesetztem `HF_HUB_OFFLINE=1`.
`docker image ls` zeigt die Groesse; erwartet werden 3 bis 4 GB.


## Ergebnis (akar-05)

`docker/Dockerfile` mit fuenf Stufen und `.dockerignore` liegen auf main
(Merge 8f8d72f).

**Pruefung vollstaendig gelaufen, alles gruen.** Gebaut wurde aus einem frischen
Klon ohne `gh-pages`-Zweig:

- `docker build -f docker/Dockerfile .` — durchgelaufen. Die Docs-Stufe fiel wie
  vorgesehen auf `mkdocs build` zurueck.
- `docker run` — `/api/health` antwortet mit Status ok und Version 0.1.0,
  `/docs/` und `/` liefern 200. Der Prozess laeuft als `kaimarkit`, nicht als root.
- Docling-Konvertierung eines PDF mit `HF_HUB_OFFLINE=1` und `--network none`:
  gelungen, die Modelle kamen aus `/opt/docling-models`.
- `docker image ls`: **3,94 GB** — im erwarteten Bereich. Installiert wurden
  `torch-2.13.0+cpu` und `torchvision-0.28.0+cpu`, der CPU-Index greift also.
- `pandoc 3.6.4`, Tesseract mit `deu` und `eng`.

**Ein Fund waehrend des Baus.** Docling zieht ueber rapidocr das OpenCV-Rad
herein, und `import cv2` scheitert auf `python:3.12-slim` an fehlenden
Systembibliotheken. Ohne sie bricht schon `docling-tools models download` ab.
Die Modell- und die Laufzeitstufe installieren deshalb `libgl1`,
`libglib2.0-0t64` und `libxcb1`. Der Name `libglib2.0-0t64` gilt fuer Debian
trixie; auf bookworm hiesse das Paket `libglib2.0-0`.

**Keine neuen Variablen.** `PANDOC_VERSION` stand schon in
`docker/.env.example`; der `ARG`-Standard im Dockerfile ist auf denselben Wert
`3.6.4` gesetzt. `docker/.env.example` und `docs/betrieb/konfiguration.md`
blieben unberuehrt.

**Zwei Entscheidungen, die eine Nachfrage wert sein koennten.**

1. Die Anwendung steckt im venv — pip hat sie beim Installieren der
   Abhaengigkeiten mitgenommen. Der Quelltext wird nicht ein zweites Mal ins
   Abbild kopiert; sonst waere unklar, welche der beiden Fassungen laeuft.
2. Die Docs-Stufe liest die Abhaengigkeiten der Gruppe `docs` per `tomllib` aus
   `backend/pyproject.toml`, statt Versionen zu wiederholen. So bleibt
   `pyproject.toml` die einzige Quelle dafuer.

`.dockerignore` schliesst `.git` nicht aus (die Docs-Stufe braucht den Zweig),
wohl aber `.worktrees/` — sonst wandert jeder Per-Ticket-Checkout in den
Build-Kontext.
