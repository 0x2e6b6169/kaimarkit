---
id: 135
title: DOC-25 · Stellen ausserhalb von docs/ nennen die alten Doku-Pfade
status: backlog
priority: low
created: 2026-09-07T11:43:20.9978058+02:00
updated: 2026-09-07T11:43:20.9978058+02:00
assignee: akar
tags:
    - docs
class: standard
---

## Befund (2026-09-07, gemeldet von akar-44 beim Abschluss von DOC-24)

DOC-24 hat `docs/` in `docs/nutzer/` und `docs/admin/` aufgeteilt und
`docs/betrieb/` aufgelöst. Zehn Dateien außerhalb von `docs/` nennen die alten
Pfade in Prosa oder Kommentaren und sind seither falsch — keine davon ist ein
funktionaler Fehler, aber jede verweist ins Leere:

- `docker/.env.example` (3×)
- `docker-compose.authelia.yml` (3×)
- `docker-compose.traefik.yml` (2×)
- `Makefile`
- `backend/app/uploads.py`
- `backend/tests/test_docling_ocr.py`
- `frontend/src/components/EngineSelect.vue`
- `frontend/src/components/OptionsPanel.vue`

## Eigene Dateien

Die zehn oben genannten Dateien.

## Vorgaben

Jede Fundstelle einzeln ansehen und auf den neuen Pfad bringen (Tabelle in der
Notiz von DOC-24 (#134)). Bevor die Liste als vollständig gilt, noch einmal über
den ganzen Baum außerhalb von `docs/` und `kanban/` greppen — die Liste stammt
aus einem einzelnen Lauf.

## Prüfung

- Keine Fundstelle mehr für einen der alten Pfade (`docs/betrieb/`,
  `docs/formate.md`, `docs/grenzen.md`, `docs/schnellstart.md`, `docs/api.md`,
  `docs/benutzung.md`) außerhalb von `kanban/`.
- `ruff check .`, `npm run typecheck`, `mkdocs build --strict` bleiben sauber.
