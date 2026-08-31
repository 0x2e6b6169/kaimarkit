---
id: 23
title: 'IN-1 · docker/Dockerfile: fuenf Stufen, Torch aus dem CPU-Index, Modelle vorgebacken'
status: todo
priority: high
created: 2026-08-31T10:21:38.706562102+02:00
updated: 2026-08-31T10:30:46.279971749+02:00
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
