---
id: 4
title: BE-1 · FastAPI-Geruest, config.py, /api/health, Einhaengen von SPA und /docs
status: done
priority: high
created: 2026-08-31T10:20:13.081397967+02:00
updated: 2026-08-31T10:49:59.681529708+02:00
started: 2026-08-31T10:49:34.904509443+02:00
completed: 2026-08-31T10:49:34.904509443+02:00
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


## Ergebnis (sophie-01)

Gebaut: `pyproject.toml` (hatchling, Version aus `app/__init__.py`, Gruppen `dev` und
`docs`), `config.py`, `errors.py`, `api/meta.py`, `api/convert.py` als Stumpf,
`main.py`.

Geprueft, alles gruen: `uvicorn app.main:app` startet ohne `frontend/dist` und ohne
Dokumentation; `/api/health` gibt 200 mit `{"status":"ok","version":"0.1.0"}`,
`/api/docs`, `/api/redoc` und `/api/openapi.json` geben 200; `/` und `/docs/` geben
ohne die Verzeichnisse 404 statt beim Start zu scheitern. Ein zweiter Lauf mit
gesetzten `KAIMARKIT_STATIC_DIR` und `KAIMARKIT_DOCS_DIR` liefert die `index.html`
unter `/`, unter einer unbekannten Unterseite (SPA-Fallback) und unter `/docs/`.
`ruff check .` ohne Befund, der Fehlerhandler bildet alle Codes aus dem Vertrag auf
415/400/400/500/413/413/504 ab.

Was die anderen Backend-Tickets erben:

- BE-2, BE-6, BE-7, BE-8 lesen ihre Werte aus `get_settings()` in `config.py`. Dort
  stehen die Variablen der Abteilung „Anwendung" aus `docker/.env.example`; die
  Variablen fuer Build, Abbild, Traefik und Authelia wertet Compose aus und
  erreichen den Prozess nie (`extra="ignore"`).
- Die Fehler heben aus `errors.py` ab und werden ueber `register_error_handlers`
  auf den Rumpf `{"detail", "code"}` abgebildet. **Abweichung vom Ticketrumpf:**
  Neben den fuenf genannten Klassen liegen dort auch `TooManyFiles` (413) und
  `EngineUnsuitable` (400). `contracts/api.md` nennt beide Codes, und da `errors.py`
  BE-1 gehoert, muesste BE-6 beziehungsweise BE-7 die Datei sonst nachtraeglich
  anfassen — genau die Kollision, die der Schnitt vermeiden soll.
- `api/convert.py` haelt einen leeren `APIRouter`, den `main.py` bereits unter
  `/api` einhaengt. BE-7 und BE-8 fuellen ihn, ohne `main.py` anzufassen.
- Der Schnittstellen-Dreiklang blieb unberuehrt: weder `contracts/api.md` noch
  `models.py` noch `types.ts` wurden geaendert.
