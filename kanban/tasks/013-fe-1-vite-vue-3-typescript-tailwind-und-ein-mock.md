---
id: 13
title: FE-1 · Vite, Vue 3, TypeScript, Tailwind und ein Mock-Server fuer /api
status: done
priority: high
created: 2026-08-31T10:20:19.071093+02:00
updated: 2026-08-31T10:53:57.503590863+02:00
started: 2026-08-31T10:52:55.227288714+02:00
completed: 2026-08-31T10:52:55.227288714+02:00
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

[[2026-08-31]] Mon 10:53
## Ergebnis FE-1

Geruest liegt auf main (Merge 30479e6, Branch task/13-frontend-scaffold).

**Aufbau.** Vue 3 mit Composition API, Vite 8, Tailwind 4 ueber `@tailwindcss/vite`,
TypeScript mit Projektverweisen: `tsconfig.app.json` fuer `src`, `tsconfig.node.json`
fuer `vite.config.ts` und `src/mocks`. Kein Pinia, kein Vue Router. `App.vue` ist eine
Geruestseite, die FE-3 bis FE-7 ersetzen.

**Mock.** Liegt in `frontend/src/mocks/` und haengt sich als Vite-Middleware vor den
Proxy, nicht als Attrappe fuer `fetch` im Browser. Deshalb antwortet er auch auf
`curl`. Eingeschaltet ueber `VITE_KAIMARKIT_MOCK=1`; in dieser Betriebsart wird der
Proxy auf localhost:8000 gar nicht erst eingerichtet, sonst liefe jede unbekannte
Route still in ein Backend, das keiner gestartet hat. Beantwortet `/api/health`,
`/api/capabilities` und `/api/convert` nach `contracts/api.md`, mit 400 bis 1600 ms
Verzoegerung. Die drei Faelle haengen am Dateinamen: `fehler` im Namen gibt 500
`conversion_failed`, `warnung` gibt 200 mit zwei Warnungen, alles andere 200 ohne.
Dazu 415 `unsupported_format` und 400 `engine_unsuitable`, damit die Fehlerdarstellung
auch die Grenzfaelle sieht. `/api/convert/batch` fehlt bewusst — das Frontend ruft je
Datei `/api/convert`.

**Pruefung, tatsaechlich gelaufen.**

- `npx vue-tsc --build --force` — keine Ausgabe, Exit 0
- `npm run build` — `dist/index.html`, `dist/assets/index-*.css` (7,76 kB),
  `dist/assets/index-*.js` (64,01 kB), 12 Module, 387 ms
- `VITE_KAIMARKIT_MOCK=1 npm run dev` — Seite 200, `/api/health` liefert
  `{"status":"ok","version":"0.1.0-mock"}`, `/api/capabilities` vollstaendig
- `curl -F file=@bericht.pdf` — 200, `status: ok`, `engine: docling`, `warnings: []`
- `curl -F file=@bericht-warnung.pdf` — 200, `status: ok`, zwei Warnungen
- `curl -F file=@bericht-fehler.pdf` — 500, `{"code":"conversion_failed"}`
- ohne `Accept`-Kopf — `text/markdown`, `Content-Disposition: attachment;
  filename="bericht.md"`, `X-Engine: docling`, `X-Warnings: 0`
- `npm run dev` ohne die Variable — Seite 200, `/api/health` 502, der Proxy greift also

**Fuer FE-2.** `types.ts` lag bereits vollstaendig vor und deckt sich mit
`contracts/api.md` und `models.py`; der Dreiklang blieb unberuehrt. In `package.json`
stehen `markdown-it`, `dompurify`, `jszip`, `vitest`, `@vue/test-utils` und `jsdom`
schon drin, dazu das Skript `npm run test` — `package.json` gehoert allein diesem
Ticket, sonst muessten FE-2, FE-4 und FE-6 daran. Der Mock setzt die Engine-Regeln
durch (`auto` folgt der Praeferenzliste, eine genannte Engine wird nie ersetzt); die
Bremse von hoechstens zwei gleichzeitigen Laeufen liegt bei FE-2.

**Luecke fuer akar.** `docs/` ist noch leer (DOC-1 legt die Stuempfe an, DOC-2 die
Inhalte). Der Entwicklungsablauf und die Variable `VITE_KAIMARKIT_MOCK` gehoeren nach
`docs/entwicklung.md`; vorerst stehen sie im Kopfkommentar von
`frontend/src/mocks/index.ts` und als Befehlszeile in `CLAUDE.md`. Es kam kein
`KAIMARKIT_*`-Betriebsparameter dazu — `docker/.env.example` und
`docs/betrieb/konfiguration.md` bleiben unberuehrt.
