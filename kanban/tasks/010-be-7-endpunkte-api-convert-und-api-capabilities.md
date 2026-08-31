---
id: 10
title: BE-7 · Endpunkte /api/convert und /api/capabilities
status: todo
priority: high
created: 2026-08-31T10:20:17.133031658+02:00
updated: 2026-08-31T10:30:45.065205261+02:00
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
