---
id: 133
title: FE-29 · Grund fuer nicht waehlbare Engine nur per title
status: backlog
priority: medium
created: 2026-09-07T11:19:46.848576906+02:00
updated: 2026-09-07T11:19:46.848576906+02:00
assignee: benny
tags:
    - frontend
    - accessibility
class: standard
---

## Befund (2026-09-07, gemeldet von akar-43 beim Abschluss von DOC-23)

In `EngineSelect.vue` steckt der Grund, warum eine Engine gerade nicht wählbar ist,
allein im `title`-Attribut — mit der Tastatur nicht erreichbar. Die Info-Zeichen
direkt daneben (FE-26) lösen genau dieses Problem für die OCR-Reichweite bereits:
Hover **und** Tastaturfokus, `aria-describedby`. Auf derselben Seite gelten damit
zwei verschiedene Maßstäbe für dieselbe Art Information.

## Eigene Dateien

- `frontend/src/components/EngineSelect.vue` und der Test dazu

## Vorgaben

Denselben Aufbau wie beim OCR-Info-Zeichen aus FE-26 verwenden: der Grund für
"nicht wählbar" bei Hover und bei Tastaturfokus erreichbar, für Screenreader über
`aria-describedby` angehängt, nicht nur im `title`-Attribut.

## Prüfung

- Rot vor grün: ein Test prüft, dass der Grund für eine nicht wählbare Engine per
  Tastaturfokus erreichbar ist (nicht nur `title`) — fällt vor der Arbeit durch.
- `npm run test`, `npm run typecheck` sauber.
