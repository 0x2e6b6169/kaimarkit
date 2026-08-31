---
id: 13
title: FE-1 · Vite, Vue 3, TypeScript, Tailwind und ein Mock-Server fuer /api
status: todo
priority: high
created: 2026-08-31T10:20:19.071093+02:00
updated: 2026-08-31T10:30:45.656025031+02:00
assignee: benny
tags:
    - frontend
depends_on:
    - 3
class: standard
---

## Ziel

Ein lauffaehiges Frontend-Geruest, das ohne Backend entwickelt werden kann.

## Eigene Dateien

- `frontend/package.json`
- `frontend/vite.config.ts`
- `frontend/index.html`
- `frontend/src/main.ts`
- `frontend/src/mocks/`

## Vorgaben

- Vue 3 mit Composition API, TypeScript, Vite, Tailwind. **Kein Pinia, kein Vue
  Router** - eine Seite, der Zustand lebt in einem Composable.
- Der Mock-Server ist der Grund, warum dieser Strang keinen Backend-Commit abwarten
  muss. Er beantwortet `/api/capabilities` und `/api/convert` nach
  `contracts/api.md`, mit kuenstlicher Verzoegerung.
- Der Mock deckt drei Faelle ab: Erfolg, Erfolg mit Warnungen, Fehlschlag. Sonst
  bleibt die Fehlerdarstellung im Frontend ungetestet.
- Vite proxyt `/api` in der Entwicklung auf `localhost:8000`; der Mock laesst sich
  ueber eine Umgebungsvariable statt des Proxys einschalten.
- `npm run typecheck` als Skript einrichten.

## Pruefung

`npm run dev` zeigt eine Seite, `npm run build` erzeugt `dist/`,
`npm run typecheck` meldet nichts. Der Mock liefert im Browser alle drei Faelle.
