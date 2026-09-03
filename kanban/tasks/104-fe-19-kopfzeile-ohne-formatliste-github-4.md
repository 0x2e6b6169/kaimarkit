---
id: 104
title: 'FE-19 · Kopfzeile ohne Formatliste (GitHub #4)'
status: done
priority: medium
created: 2026-09-03T11:20:25.12748426+02:00
updated: 2026-09-03T11:26:18.851837696+02:00
started: 2026-09-03T11:26:13.637242137+02:00
completed: 2026-09-03T11:26:13.637242137+02:00
assignee: benny
tags:
    - frontend
    - gh-4
class: standard
---

## Ziel

Der Kopf der Seite sagt zweimal dasselbe: „Angenommen werden .docx · .epub · .pdf …" steht im Einleitungssatz, und die Dropzone direkt darunter nennt dieselbe Liste noch einmal. GitHub-Issue #4 will die Wiederholung weg. Der Satz im Kopf fällt; die Dropzone behält ihre Liste, weil sie dort zur Handlung gehört.

## Eigene Dateien

- `frontend/src/App.vue`
- `frontend/src/App.test.ts`

## Vorgaben

- Der Einleitungssatz bleibt: „kaimarkit wandelt Dokumente nach Markdown, damit man den Kontext liest, den man einem Sprachmodell gibt." Nur das `<template v-if="formats">` mit „Angenommen werden …" verschwindet.
- Das `computed` `formats` in `App.vue` wird dadurch unbenutzt und geht mit. `extensions` bleibt, die Dropzone bekommt es weiterhin.
- Die drei Zusicherungen in `App.test.ts`, die „Angenommen werden" erwarten (Zeilen 99, 315, 346), werden nicht gelöscht, sondern umgedreht: Der `<header>` nennt keine Endung mehr, die Dropzone nennt sie weiterhin. Sonst prüft nach dem Umbau niemand, dass die Liste nicht auch aus der Dropzone verschwunden ist.
- Nichts sonst am Kopf ändern; der GitHub-Verweis aus FE-16 (#93) bleibt, wie er ist.

## Prüfung

1. Vorher rot: `grep -n 'Angenommen werden' frontend/src/App.vue` findet die Stelle. Nachher findet es nichts.
2. `cd frontend && npm run test` grün, `npm run typecheck` grün (ein unbenutztes `formats` fiele hier auf), `npm run build` grün.
3. Im Test: `.pdf` steht im Text der Dropzone und nicht im Text des `<header>`.

[[2026-09-03]] Thu 11:26
## Ergebnis (benny-20)

Der Satz „Angenommen werden …“ und das computed `formats` sind aus `App.vue` heraus; die Dropzone bekommt `extensions` weiterhin. Die drei Zusicherungen in `App.test.ts` sind umgedreht: „.docx · .epub · .pdf“ steht im Text der FileDropZone, `.pdf` nicht im Text des `<header>`. Rot vor grün belegt: Mit der alten `App.vue` schlagen genau diese drei Tests fehl.

- Vitest vorher: Test Files 9 passed (9) / Tests 105 passed (105)
- Vitest nachher: Test Files 9 passed (9) / Tests 105 passed (105)
- typecheck und build grün; `grep -n 'Angenommen werden' frontend/src/App.vue` leer
- `grep -rn 'Angenommen werden' docs/` leer, in `docs/` nichts zu berichtigen
- Merge-Commit d1db109
