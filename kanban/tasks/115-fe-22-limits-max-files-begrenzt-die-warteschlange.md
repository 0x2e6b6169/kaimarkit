---
id: 115
title: FE-22 · limits.max_files begrenzt die Warteschlange, Dateien und URLs zusammen
status: todo
priority: medium
created: 2026-09-03T14:37:19.300372352+02:00
updated: 2026-09-03T14:37:19.300372352+02:00
assignee: benny
tags:
    - frontend
class: standard
---

## Ziel

Befund von benny beim Abschluss von FE-21 (#108): Der Ticketrumpf von FE-21 verlangte,
`limits.max_files` solle Dateien und URLs zusammen begrenzen, „so wie die Dropzone es
heute für Dateien tut". Diese Grenze gibt es nicht. `max_files` steht in `types.ts` und
in Testfixturen, wird aber nirgends durchgesetzt. URLs verhalten sich seit FE-21 genauso
— also ebenfalls ohne Grenze. Der Satz im Rumpf beschrieb einen Zustand, den ich nicht
nachgeprüft hatte; die Grenze fehlt für beide Quellen.

Das Backend lehnt einen zu großen Stapel ab. Die Oberfläche soll es vorher sagen, statt
zwanzig Anfragen loszuschicken, von denen die Hälfte scheitert.

## Eigene Dateien

- `frontend/src/composables/useConversion.ts` und `useConversion.test.ts`
- `frontend/src/components/FileDropZone.vue` und `FileDropZone.test.ts`
- `frontend/src/components/UrlInput.vue` und `UrlInput.test.ts`
- `frontend/src/App.vue` und `App.test.ts`, nur falls die Meldung dort ausgegeben wird

Nicht hier: `frontend/src/download.ts` (gehört FE-23), `frontend/src/api.ts`,
`frontend/src/types.ts` — `max_files` steht dort schon.

## Vorgaben

- Die Grenze zählt die Warteschlange als Ganzes, nicht je Quelle. Dateien und URLs
  zusammen gegen `limits.max_files` aus `/api/capabilities`.
- Was über die Grenze hinausgeht, wird gar nicht erst aufgenommen und die Oberfläche
  sagt in einem Satz, wie viele Einträge zulässig sind und wie viele abgewiesen wurden.
  Der Satz erscheint dort, wo Fehler heute schon erscheinen; keine neue Stelle erfinden.
- Kommt `/api/capabilities` nicht durch oder fehlt `limits`, gilt keine Grenze. Eine
  erfundene Voreinstellung wäre schlimmer als keine.
- Die Meldung ist deutsch und nennt Zahlen, keine Fachbegriffe: „Höchstens 20 Einträge
  auf einmal. 3 wurden nicht übernommen."

## Prüfung

- Rot vor grün: Ein Test, der 21 Dateien in eine Warteschlange mit `max_files: 20` gibt,
  fällt vor der Arbeit durch.
- Ein Test für die gemischte Zählung: 15 Dateien und 8 URLs bei `max_files: 20` nehmen
  zusammen 20 Einträge auf.
- Ein Test für den fehlenden Grenzwert: ohne `limits` wird nichts abgewiesen.
- `npm run test`, `npm run typecheck`, `npm run build` grün. Die Basislinie vor der
  Arbeit steht in der Notiz (nach FE-21: 10 Dateien / 128 Tests).
