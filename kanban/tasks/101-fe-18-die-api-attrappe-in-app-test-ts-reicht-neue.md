---
id: 101
title: FE-18 · Die api-Attrappe in App.test.ts reicht neue Exporte durch
status: done
priority: medium
created: 2026-09-02T16:46:38.261202148+02:00
updated: 2026-09-02T16:50:15.298784822+02:00
started: 2026-09-02T16:50:14.1377958+02:00
completed: 2026-09-02T16:50:14.1377958+02:00
assignee: benny
class: standard
---

## Ziel

Die Attrappe von `./api` in `App.test.ts` zählt jeden Export einzeln auf. Ein
neuer Export im API-Client fehlt dort, bis jemand daran denkt — und wer ihn
dann benutzt, bringt die ganze Testdatei zum Scheitern. Die Attrappe soll
durchreichen, was sie nicht selbst ersetzt.

*(Berichtigt am 02.09.2026: Der Rumpf sagte zuerst, der fehlende Export laufe
still ins Leere. Das war eine Vermutung, keine Beobachtung — Vitest legt einen
Proxy über den Namensraum und wirft. Siehe die Notiz am Ende.)*

## Herkunft

Gemeldet von benny aus FE-17 (#100). Dort fiel es auf, weil `api.ts` und
`App.test.ts` demselben Ticket gehörten. Ein Ticket, das nur `api.ts` besitzt,
hat diesen Schutz nicht.

Das Muster steht bereits in derselben Datei, fünf Zeilen tiefer: Die Attrappe
von `./download` holt sich `importOriginal` und überschreibt nur die eine
Funktion, um die es geht. `./api` tut das nicht.

Belegbar heute schon: `ApiError` ist ein Export von `api.ts` und fehlt in der
Aufzählung. Niemand stolpert darüber, weil nur `useConversion.test.ts` die
Klasse benutzt und diese Datei ihre eigenen Attrappen hat. Der Fehler ist
angelegt, nicht eingetreten.

## Eigene Dateien

- `frontend/src/App.test.ts`

Nur diese. Weder `api.ts` noch `App.vue` werden angefasst; ändert sich dort
etwas, ist der Entwurf falsch.

## Vorgaben

**Dem Muster folgen, das daneben steht.** `vi.mock('./api', async
(importOriginal) => ({ ...(await importOriginal<…>()), … }))`, und darin nur die
Ausdrücke ersetzen, die der Test wirklich steuern muss. Kein neues Verfahren
erfinden; die Datei hat schon eines.

**Was heute ersetzt wird, bleibt ersetzt.** `fetchCapabilities`, `fetchHealth`
und `convertFile` steuert der Test, und `messageFromError` ist absichtlich
vereinfacht. Alle vier behalten ihr jetziges Verhalten — dieses Ticket ändert
kein Testergebnis, es ändert nur, was mit einem **neuen** Export geschieht.

**Keine Zusicherung streichen, keine hinzufügen** außer der einen aus der
Prüfung. Die 104 bestehenden Tests bleiben, wie sie sind.

## Prüfung

1. Neue Zusicherung in `App.test.ts`: `ApiError` aus `./api` ist unter der
   Attrappe definiert und eine Funktion. **Vor** der Änderung ist sie
   `undefined` — das ist das Rot, und genau der Fehler, den das Ticket
   beseitigt. Einmal belegen.
2. `npm run test` — Datei- **und** Testzahl beider Zeilen nennen. Erwartet sind
   9 Dateien und 105 Tests; weicht eine Zahl ab, ist das ein Befund, keine
   Anpassung.
3. `npm run typecheck`
4. `npm run build`

[[2026-09-02]] Wed 16:50
## Ergebnis (benny-19)

Die Attrappe von `./api` nutzt jetzt `importOriginal` und spreizt das echte Modul; ersetzt bleiben nur `fetchCapabilities`, `fetchHealth`, `convertFile` und das absichtlich vereinfachte `messageFromError`. Das Muster stammt von der `./download`-Attrappe fünf Zeilen tiefer.

Rot vor grün, beide Läufe:

- vor dem Umbau, mit der neuen Zusicherung: Test Files 1 failed | 8 passed (9), Tests 1 failed | 104 passed (105)
- nach dem Umbau: Test Files 9 passed (9), Tests 105 passed (105)

Beide Zahlen wie im Rumpf erwartet. `npm run typecheck` und `npm run build` ohne Befund.

**Befund zur Formulierung im Rumpf.** „Vor der Änderung ist sie undefined" trifft nicht ganz: Vitest legt einen Proxy über den attrappierten Modulnamensraum und wirft beim Zugriff auf einen fehlenden Export — `No "ApiError" export is defined on the "./api" mock.` Am Ticket ändert das nichts, die Zusicherung ist vorher rot und nachher grün. Es ändert die Einschätzung des Schadens: Ein Test, der einen neuen Export benutzt hätte, wäre nicht still danebengelaufen, sondern hätte die ganze Datei zum Scheitern gebracht.

Weder `api.ts` noch `App.vue` angefasst. Keine Aussage unter `docs/` betroffen — die Änderung ändert kein Verhalten, das der Nutzer sieht.
