---
id: 29
title: INT-1 · Frontend gegen das echte Backend, Mock entfernen
status: in-progress
priority: medium
created: 2026-08-31T10:21:43.644388097+02:00
updated: 2026-08-31T11:35:15.316324766+02:00
assignee: benny
tags:
    - frontend
depends_on:
    - 12
    - 19
    - 11
claimed_by: benny-08
claimed_at: 2026-08-31T11:35:15.316324766+02:00
class: standard
---

## Ziel

Die beiden Straenge zusammenfuehren und die Attrappe entfernen.

## Eigene Dateien

- `frontend/src/mocks/` (Loeschung)
- Fehlerkorrekturen in beiden Straengen, wo die Wirklichkeit vom Vertrag abweicht

## Vorgaben

- Jede Abweichung zwischen Mock und echter API wird in `contracts/api.md`,
  `models.py` und `types.ts` gemeinsam geradegezogen - nicht einseitig im Frontend
  weggepatcht.
- Der Mock verschwindet vollstaendig, einschliesslich seiner Abhaengigkeiten in
  `package.json` und des Schalters in `vite.config.ts`.

## Pruefung

`npm run dev` gegen das laufende Backend: fuenf gemischte Dateien, darunter eine,
die fehlschlaegt. Vorschau, Einzeldownload und ZIP funktionieren.
`npm run typecheck` und `pytest -q` bleiben gruen.
