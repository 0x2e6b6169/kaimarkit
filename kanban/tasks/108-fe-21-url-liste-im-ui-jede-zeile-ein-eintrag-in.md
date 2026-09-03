---
id: 108
title: 'FE-21 · URL-Liste im UI, jede Zeile ein Eintrag in der Warteschlange (GitHub #5)'
status: done
priority: medium
created: 2026-09-03T11:20:27.282910036+02:00
updated: 2026-09-03T14:30:40.443372788+02:00
started: 2026-09-03T14:30:31.951358627+02:00
completed: 2026-09-03T14:30:31.951358627+02:00
assignee: benny
tags:
    - frontend
    - gh-5
depends_on:
    - 105
    - 107
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

Umgesetzt und gemerged (a5d9084). UrlInput.vue: Textfeld mit Label „Webseiten, eine Adresse je Zeile" und Knopf „Webseiten wandeln", unter der Dropzone. Leerzeilen und Leerraum fallen weg; eine Zeile ohne http:// oder https:// wird als role=alert markiert, bleibt im Feld stehen (damit sie sich berichtigen laesst) und geht nicht hinaus — die uebrigen Zeilen gehen trotzdem. Ist alles gueltig, ist das Feld danach leer. api.ts bekam convertUrl(url, options, signal) auf POST /api/convert/url mit UrlConvertRequest als Rumpf; types.ts blieb unberuehrt (BE-35 hatte vorgelegt). In useConversion.ts wurde aus der Map<number, File> eine Map auf QueueSource (Datei oder URL); QueueEntry hat jetzt ein Feld source. Ein URL-Eintrag zeigt die Adresse als Namen, bis die Antwort da ist, danach deren filename — daraus macht download.ts wie bisher .md und nummeriert Doppelte. Grenze (zwei gleichzeitig), Optionen, Abbruch und Archiv gelten fuer beide Quellen gleich.

Pruefung 1 (rot vor gruen belegt: 6 Faelle fielen vor der Arbeit, danach alles gruen): UrlInput.test.ts (4 Faelle) fuer die drei Zeilen, useConversion.test.ts (6 neue Faelle) fuer Namen aus der Antwort, -2 im Archiv, 400 als failed mit Meldung, Abbruch, geteilte Grenze; App.test.ts (3 neue Faelle) end-to-end.
Pruefung 2: Test Files 10 passed (10), Tests 128 passed (128); typecheck und build gruen. Basislinie war 9 Dateien / 115 Tests.
Pruefung 3 von Hand gegen das echte Backend (uvicorn auf :8000, npm run dev als Proxy): https://example.com/ liefert filename example-domain.html und Markdown, eine PDF-Adresse liefert www-w3-org-...-dummy.pdf mit dem MarkItDown-Warnhinweis, http://127.0.0.1/... kommt als 400 invalid_url mit lesbarer Meldung zurueck. Geklickt wurde nicht (kein Browser hier); geprueft wurde derselbe Aufruf, den convertUrl absetzt, durch den Vite-Proxy. Beide Ports danach wieder frei.
Pruefung 4: Textfeld und Knopf sind native Elemente und damit per Tab erreichbar; der Fokusring kommt aus *:focus-visible in style.css. Die neuen Eintraege sind dieselben FileRow wie Dateien. Die aria-live-Ansage ist im App-Test zugesichert.

Drei Dinge ausserhalb der Dateiliste, mit Begruendung:
1. FileQueue.test.ts und FileRow.test.ts bauen QueueEntry-Objekte von Hand; das neue Pflichtfeld source haette den Baum sonst nicht mehr typpruefbar gelassen (je eine Zeile source: 'file'). Kein offenes Ticket fuehrt diese Dateien.
2. App.vue sagte am Ende eines Laufs „Alle Dateien sind fertig" — mit Webseiten in der Warteschlange ist das unwahr. Jetzt „Alles ist fertig"; die Zusicherung in App.test.ts zog mit.
3. filenames fuer OptionsPanel filtert URL-Eintraege heraus. Sonst haette der aus dem Seitentitel abgeleitete Name (example-domain.html) das Engineangebot auf HTML verengt — die Vorgabe verlangt das Gegenteil.

Zwei Befunde, gemeldet statt geaendert:
A. Die Vorgabe „limits.max_files begrenzt Dateien und URLs zusammen, so wie die Dropzone es heute fuer Dateien tut" hat keine Grundlage: max_files wird im Frontend nirgends durchgesetzt (nur in types.ts und in Testfixtures zu finden). Die Dropzone nimmt beliebig viele Dateien an, das Backend weist zurueck. URLs verhalten sich jetzt genauso — also gleich behandelt, aber ohne Grenze. Eine Grenze im Frontend waere ein eigenes Ticket fuer beide Quellen.
B. buildArchive schreibt gescheiterte Eintraege mit sanitizeFilename(filename) nach _errors.txt. Bei einer URL ohne Pfad (https://example.com/) bleibt davon nichts uebrig und die Zeile heisst 'upload'. Betrifft nur den Fall „URL gescheitert und trotzdem Archiv gebaut"; download.ts blieb deshalb unberuehrt.
