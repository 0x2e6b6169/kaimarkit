---
id: 3
title: SETUP-1 · Verzeichnisgeruest und Schnittstellenvertrag festschreiben
status: done
priority: critical
created: 2026-08-31T10:20:12.489631912+02:00
updated: 2026-08-31T10:30:46.826891033+02:00
started: 2026-08-31T10:24:55.290278442+02:00
completed: 2026-08-31T10:24:55.290278442+02:00
assignee: akar
tags:
    - setup
class: standard
---

## Ziel

Die Schnittstellen zwischen Backend, Frontend und Infrastruktur festschreiben, bevor
jemand mit der Umsetzung beginnt. Danach koennen die drei Straenge unabhaengig
arbeiten.

## Eigene Dateien

- `contracts/api.md`
- `backend/app/models.py`
- `frontend/src/types.ts`
- `docker/.env.example`
- `CLAUDE.md`
- `.gitignore`
- leere Verzeichnisse des Baums aus dem Plan

## Vorgaben

- `contracts/api.md` beschreibt jeden Endpunkt vollstaendig: Pfad, Methode,
  Anfragefelder, Antwortschema, Fehlercodes (400, 413, 415, 500, 504) und ein
  curl-Beispiel. Endpunkte: `GET /api/health`, `GET /api/capabilities`,
  `POST /api/convert`, `POST /api/convert/batch`.
- `models.py` und `types.ts` bilden dieses Dokument ab. Feldnamen identisch,
  keine Abweichung in der Schreibweise.
- Antwort je Datei: `filename`, `markdown`, `engine`, `warnings[]`, `duration_ms`,
  `status` (`ok` | `failed`), `error` (nur bei `failed`).
- `capabilities`: `formats` (Endung -> Enginenamen), `engines` (Name -> Zustand
  `ready` | `warming` | `unavailable`), `limits`, `ocr_available`.
- `.env.example` listet jede Variable aus dem Plan mit Standardwert und einem
  Kommentar, der ihre Wirkung nennt.
- `CLAUDE.md` nach dem Abschnitt des Plans, einschliesslich der sechs Konventionen.
- `.gitignore`: `kanban/` NICHT ausschliessen, das Board gehoert ins Repo.

## Pruefung

Ein Leser kann allein aus `contracts/api.md` einen Client schreiben, ohne den Code
zu sehen. `python -c "import app.models"` laeuft durch, `npx tsc --noEmit` auf
`types.ts` meldet nichts.

[[2026-08-31]] Mon 10:24
Pruefung bestanden: models.py importiert und erzeugt exakt das JSON aus contracts/api.md; types.ts besteht 'tsc --noEmit --strict'. Verzeichnisgeruest, .gitignore (kanban/ bewusst nicht ausgeschlossen), docker/.env.example mit 33 Variablen und CLAUDE.md mit sechs Konventionen angelegt.
