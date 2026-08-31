---
id: 4
title: BE-1 · FastAPI-Geruest, config.py, /api/health, Einhaengen von SPA und /docs
status: todo
priority: high
created: 2026-08-31T10:20:13.081397967+02:00
updated: 2026-08-31T10:30:45.059515538+02:00
assignee: sophie
tags:
    - backend
depends_on:
    - 3
class: standard
---

## Ziel

Eine startfaehige FastAPI-Anwendung mit Konfiguration, Gesundheitsendpunkt und den
Einhaengungen fuer Frontend und Dokumentation.

## Eigene Dateien

- `backend/pyproject.toml` (einschliesslich der Abhaengigkeitsgruppe `docs`)
- `backend/app/main.py`
- `backend/app/config.py`
- `backend/app/errors.py`
- `backend/app/api/meta.py`
- `backend/app/api/convert.py` als leerer Router-Stumpf

## Vorgaben

- `config.py` mit `pydantic-settings`, Praefix `KAIMARKIT_`. Jede Variable aus
  `docker/.env.example` hat hier ihre Entsprechung mit Standardwert.
- `main.py` haengt in dieser Reihenfolge ein: `/api` (Router), `/docs`
  (`StaticFiles(html=True)` aus `KAIMARKIT_DOCS_DIR`), `/` (SPA aus
  `KAIMARKIT_STATIC_DIR`, unbekannte Pfade beantwortet `index.html`).
- **Wichtig:** `/docs` und `/` werden nur eingehaengt, wenn das jeweilige Verzeichnis
  existiert. In der Entwicklung gibt es beide nicht; ohne diese Pruefung liesse sich
  das Backend allein nicht starten.
- FastAPI mit `docs_url="/api/docs"`, `redoc_url="/api/redoc"`,
  `openapi_url="/api/openapi.json"` - `/docs` gehoert der Dokumentation.
- `errors.py`: `ConversionError` mit den Unterklassen `UnsupportedFormat`,
  `EngineUnavailable`, `EngineFailed`, `FileTooLarge`, `ConversionTimeout`, dazu ein
  Exception-Handler, der sie auf 415/400/500/413/504 abbildet.
- `pyproject.toml`: Laufzeitabhaengigkeiten, Gruppe `dev` (pytest, ruff), Gruppe
  `docs` (mkdocs-material, mike). Torch wird nicht direkt aufgefuehrt, es kommt
  ueber docling.
- `api/meta.py`: `/api/health` antwortet sofort mit 200, auch waehrend Docling laedt.

## Pruefung

`uvicorn app.main:app` startet ohne `frontend/dist` und ohne Dokumentation,
`curl -sf localhost:8000/api/health` gibt 200, `curl -sf localhost:8000/api/docs`
gibt 200.
