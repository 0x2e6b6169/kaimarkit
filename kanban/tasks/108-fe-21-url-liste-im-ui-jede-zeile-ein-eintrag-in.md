---
id: 108
title: 'FE-21 · URL-Liste im UI, jede Zeile ein Eintrag in der Warteschlange (GitHub #5)'
status: in-progress
priority: medium
created: 2026-09-03T11:20:27.282910036+02:00
updated: 2026-09-03T14:18:31.880777359+02:00
assignee: benny
tags:
    - frontend
    - gh-5
depends_on:
    - 105
    - 107
claimed_by: benny-23
claimed_at: 2026-09-03T14:18:31.880777359+02:00
class: standard
---

## Ziel

GitHub-Issue #5, zweiter Teil: ein mehrzeiliges Textfeld, eine URL je Zeile, ein Knopf „Webseiten wandeln". Jede Zeile wird ein Eintrag in der Warteschlange, mit Status, Vorschau und Download wie eine Datei; das ZIP nimmt sie mit. Der Dateiname kommt aus dem `filename` der Antwort (BE-35 leitet ihn aus dem Seitentitel ab); `download.ts` macht daraus `.md` und nummeriert Doppelte wie bisher.

## Eigene Dateien

- `frontend/src/components/UrlInput.vue` (neu) und `frontend/src/components/UrlInput.test.ts`
- `frontend/src/api.ts`: `convertUrl(url, options)` neben `convertFile`
- `frontend/src/composables/useConversion.ts` und `useConversion.test.ts`: Einträge aus URLs
- `frontend/src/App.vue`, `frontend/src/App.test.ts`
- `frontend/src/download.ts` und `frontend/src/__tests__/download.spec.ts`, nur falls der Name eines URL-Eintrags dort anders behandelt werden muss

`types.ts` hat BE-35 vorbereitet (`UrlConvertRequest`); hier nicht anfassen.

## Vorgaben

- Das Textfeld steht unter der Dropzone, mit `<label>` „Webseiten, eine Adresse je Zeile". Leere Zeilen und Leerraum werden verworfen. Eine Zeile, die nicht mit `http://` oder `https://` beginnt, wird vor dem Absenden markiert und nicht abgeschickt. Die feinere Prüfung (privat, unerreichbar) macht das Backend; seine Meldung landet im Eintrag als `failed`.
- Ein Eintrag aus einer URL zeigt in der Warteschlange die URL als Namen, solange keine Antwort da ist; danach den `filename` aus der Antwort. In `useConversion.ts` bekommt ein Eintrag deshalb eine Quelle: Datei **oder** URL. Aus der `Map<number, File>` wird eine Map auf die Quelle; `convertFile` oder `convertUrl` je nach Art.
- Engine und OCR aus `OptionsPanel` gelten für URLs wie für Dateien. Die Filterung der Engines nach Dateiendung kennt für eine URL keine Endung: Eine URL schränkt das Angebot nicht ein.
- `limits.max_files` aus `/api/capabilities` begrenzt Dateien und URLs zusammen, so wie die Dropzone es heute für Dateien tut.
- Nach dem Absenden leert sich das Feld; die Zeilen leben in der Warteschlange weiter.
- Abbruch (`aborted`) gilt für URL-Einträge wie für Dateien.

## Prüfung

1. Vorher rot, nachher grün: drei Zeilen (eine leer, eine ohne Schema, eine gültig) → ein Eintrag in der Warteschlange, eine markierte Zeile. Antwort mit `filename: "example-domain.html"` → Eintrag zeigt `example-domain.html`, Download heißt `example-domain.md`. Zwei URLs mit gleichem Titel → das ZIP enthält `-2`. Fehlerantwort 400 → Eintrag `failed` mit der Meldung.
2. `cd frontend && npm run test`, `npm run typecheck`, `npm run build` grün.
3. Von Hand gegen das Backend: `https://example.com/` und eine PDF-URL eingeben → zwei Einträge `ok`, Vorschau zeigt Text, ZIP enthält beide.
4. Tastatur: Textfeld, Knopf und die neuen Einträge sind mit Tab erreichbar; `aria-live` meldet den Abschluss wie bei Dateien.
