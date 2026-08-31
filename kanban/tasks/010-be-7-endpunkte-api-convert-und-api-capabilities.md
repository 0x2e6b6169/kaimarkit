---
id: 10
title: BE-7 · Endpunkte /api/convert und /api/capabilities
status: done
priority: high
created: 2026-08-31T10:20:17.133031658+02:00
updated: 2026-08-31T11:06:28.718430571+02:00
started: 2026-08-31T11:06:16.670296594+02:00
completed: 2026-08-31T11:06:16.670296594+02:00
assignee: sophie
tags:
    - backend
depends_on:
    - 5
    - 9
class: standard
---

## Ziel

Die Einzeldatei-Konvertierung ueber HTTP.

## Eigene Dateien

- `backend/app/api/convert.py` (Einzeldatei-Teil)
- Ergaenzung von `backend/app/api/meta.py` um `/api/capabilities`

## Vorgaben

- `POST /api/convert`: multipart mit `file`, Formularfelder `engine` (optional) und
  `ocr` (optional, ueberschreibt den Standard).
- Die Antwort richtet sich nach `Accept`: ohne Angabe `text/markdown` mit
  `Content-Disposition`, damit `curl -O` direkt die `.md`-Datei liefert; mit
  `application/json` das vollstaendige Ergebnis samt `engine`, `warnings` und
  `duration_ms`.
- `GET /api/capabilities` liefert Formate, Engines je Format samt Zustand, Limits
  und ob OCR verfuegbar ist. Das Frontend baut daraus seine Auswahl.
- Fehlercodes wie in `contracts/api.md`: 413 zu gross, 415 unbekannte Endung,
  400 angeforderte Engine ungeeignet, 504 Zeitgrenze.
- Kein Zustand, keine Ablage auf dem Server.

## Pruefung

`pytest backend/tests/test_api.py -q` gruen. Die curl-Beispiele aus
`contracts/api.md` funktionieren unveraendert.


## Ergebnis (sophie-06)

Gebaut: `POST /api/convert` in `backend/app/api/convert.py` und
`GET /api/capabilities` in `backend/app/api/meta.py`, dazu `backend/tests/test_api.py`
(13 Tests, nur Attrappen — keine Engine muss installiert sein) und der API-Abschnitt
in `docs/api.md`.

Der Endpunkt spricht ausschliesslich mit der Registry: `stored_upload` nimmt die Datei
entgegen, `run_conversion` haelt Semaphor und Zeitgrenze, `convert_with_fallback`
waehlt und wandelt. Die Antwort haengt am `Accept`-Kopf — ohne Angabe Markdown mit
`Content-Disposition`, `X-Engine` und `X-Warnings`, mit `application/json` ein
`ConversionEntry`. Namen mit Umlauten stehen zweimal im Kopf (ASCII und RFC 5987),
sonst scheitert Starlette beim Kodieren der Kopfzeile.

`/api/capabilities` speist sich aus `registry.PREFERENCES` und `engines_for`; eine
Endung ohne einsatzbereite Engine faellt weg, jede Engine meldet
ready/warming/unavailable, `passthrough` ist dabei. `ocr_available` ist
`KAIMARKIT_OCR_ENABLED` — welche Engine OCR koennte, weiss die Registry, nicht die API.

Geprueft: `pytest tests/test_api.py -q` gruen (13), volle Suite nach dem Merge auf
main 56 passed / 1 skipped, `ruff check .` sauber. Die curl-Beispiele aus
`contracts/api.md` gegen einen laufenden uvicorn ausprobiert (Markdown, JSON, 415).

Fuer BE-8 wiederverwendbar: derselbe Router, `stored_upload` + `run_conversion` je
Datei, `_markdown_name`, `_content_disposition` und `_header_safe` in `convert.py`.

Schnittstellen-Dreiklang **nicht** angefasst: `contracts/api.md`, `models.py` und
`types.ts` waren bereits deckungsgleich und reichten aus.
