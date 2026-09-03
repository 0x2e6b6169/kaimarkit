---
id: 116
title: FE-23 · _errors.txt nennt bei URLs die Adresse, nicht "upload"
status: todo
priority: low
created: 2026-09-03T14:37:20.062736571+02:00
updated: 2026-09-03T14:37:20.062736571+02:00
assignee: benny
tags:
    - frontend
class: standard
---

## Ziel

Befund von benny beim Abschluss von FE-21 (#108): `buildArchive` schreibt gescheiterte
Einträge mit `sanitizeFilename(filename)` in `_errors.txt`. Bei einer URL ohne Pfad —
`https://example.com/` — bleibt davon nichts übrig, und die Zeile heißt „upload". Wer
das ZIP öffnet, erfährt nicht, welche Adresse gescheitert ist.

benny hat `download.ts` deshalb in FE-21 nicht angefasst; die Datei gehört diesem Ticket.

## Eigene Dateien

- `frontend/src/download.ts`
- `frontend/src/__tests__/download.spec.ts`

Nicht hier: `useConversion.ts`, `FileDropZone.vue`, `UrlInput.vue`, `App.vue` — die
gehören FE-22.

## Vorgaben

- Ein gescheiterter Eintrag aus einer URL steht in `_errors.txt` mit seiner Adresse,
  nicht mit einem aus dem Dateinamen gewonnenen Rest. Die Adresse liegt im Eintrag
  bereits vor; `sanitizeFilename` ist für Dateinamen im ZIP da, nicht für eine Zeile
  in einer Textdatei.
- Für Einträge aus Dateien ändert sich nichts.
- `sanitizeFilename` selbst bleibt, wie es ist. Wer die Funktion ändert, ändert auch
  die Namen der Dateien im Archiv — das ist nicht gefragt.

## Prüfung

- Rot vor grün: Ein Test, der einen gescheiterten Eintrag mit der Quelle
  `https://example.com/` durch `buildArchive` schickt und in `_errors.txt` die Adresse
  erwartet, fällt vor der Arbeit durch und nennt „upload" als Ist-Wert.
- Ein Test belegt, dass die Zeile für einen gescheiterten Eintrag aus einer Datei
  unverändert bleibt.
- `npm run test`, `npm run typecheck`, `npm run build` grün.
