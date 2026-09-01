---
id: 79
title: FE-14 · Eine laufende Umwandlung laesst sich nicht abbrechen
status: done
priority: high
created: 2026-09-01T16:01:34.173915519+02:00
updated: 2026-09-01T16:29:56.640555758+02:00
assignee: benny
tags:
    - frontend
    - ux
class: standard
---

## Befund (01.09.2026, Frage des Nutzers)

Der Nutzer fragte, ob die Zeitgrenze noch nötig sei, wo doch die verstrichene Zeit
angezeigt wird — er könne ja selbst abbrechen. **Kann er nicht.** In `frontend/src`
kommt weder `AbortController` noch `abort` noch `cancel` vor. „Entfernen" nimmt die
Zeile aus der Liste; die Anfrage läuft weiter.

Seit FE-12 sieht er also, dass etwas seit 4:12 läuft, und hat keine Möglichkeit, es
zu beenden. Die Anzeige hat die Frage erst sichtbar gemacht, die es vorher auch schon
gab.

## Ziel

Wer wartet, kann aufhören zu warten.

## Eigene Dateien

- `frontend/src/composables/useConversion.ts`
- `frontend/src/components/FileRow.vue`
- `frontend/src/components/FileQueue.vue`
- die zugehörigen Tests

## Vorgaben

Ein `AbortController` je laufender Datei, ein Abbruch-Bedienelement an der laufenden
Zeile. Danach steht die Datei in einem eigenen Zustand — „abgebrochen", nicht
„fehlgeschlagen": Der Nutzer hat entschieden, es ist kein Fehler.

**Ehrlich bleiben, was der Abbruch tut.** Er beendet das Warten des Browsers. Ob der
Dienst die Arbeit ebenfalls einstellt, ist eine andere Frage und liegt in #80 — die
Umwandlung läuft dort in einem Thread, und ein abgebrochener HTTP-Aufruf beendet den
nicht von selbst. Der Text am Bedienelement darf deshalb nichts versprechen, was
dahinter nicht steht: „Nicht mehr warten" ist wahr, „Umwandlung stoppen" womöglich
nicht.

Kein neues Feld in `/api/capabilities` und keine Änderung am Vertrag — der Abbruch
ist ein Client-Vorgang. Braucht es doch eines, ist das der Schnittstellen-Dreiklang:
melden, nicht nebenbei einbauen.

## Prüfung

- Eine laufende Zeile hat ein Bedienelement, das mit der Tastatur erreichbar ist.
- Nach dem Abbruch steht die Datei auf „abgebrochen", die Zeit zählt nicht weiter,
  und die Warteschlange zählt sie nicht als Fehler.
- Ein Test belegt, dass `AbortController.abort()` tatsächlich gerufen wird.
- `npm run test` und `npm run typecheck` bleiben grün; Testdateien und Tests je mit
  Sammelzahl gemeldet.

## Ergebnis (benny-15)

Ein AbortController je laufender Zeile: `useConversion` haelt sie in einer Map,
`convertFile` reicht das Signal an `fetch` weiter. Der Knopf an der laufenden Zeile
heisst **Nicht mehr warten** (`data-test="abort-row"`); `Entfernen` bricht eine
laufende Zeile jetzt ebenfalls ab, statt die Anfrage weiterlaufen zu lassen.

Der neue Zustand `aborted` steht in `QueueStatus` in `useConversion.ts` — ein reiner
Client-Zustand, `types.ts` und der Vertrag bleiben unberuehrt. `App.vue` zaehlt nur
`failed`, ein Abbruch gilt also nicht als Fehler; der Ticker aus FE-12 haengt am
Status und stoppt mit ihm.

Mitgezogen, weil es sonst nicht typpruefbar oder unwahr geworden waere — kein offenes
Ticket besitzt diese Dateien: `api.ts` (optionales `signal` an `convertFile`, ein
Abbruch wird nicht mehr als „Dienst nicht erreichbar" verkleidet), `download.ts`
(`DownloadEntry.status` um `aborted` erweitert, sonst passt `QueueEntry` nicht mehr
darauf), `App.vue` (eine Zeile: `abort` aus `useConversion` an `FileQueue`).

Die schwache Beschriftung ist gemessen, nicht zaghaft: BE-30 hat gezeigt, dass
uvicorn die ASGI-Aufgabe beim Verbindungsabbruch nicht abbricht — der Handler laeuft
bis zur Zeitgrenze, der Platz blieb acht Sekunden laenger belegt als der Aufruf.
„Umwandlung stoppen" oder ein blankes „Abbrechen" waere damit nachweislich falsch.
Der Grund steht als Kommentar in `FileRow.vue` und `useConversion.ts`, damit der
Naechste den Text nicht „schoener" macht. Die abgebrochene Zeile sagt es auch dem
Nutzer: „Der Dienst wandelt sie im Hintergrund zu Ende — abgebrochen ist das Warten,
nicht die Umwandlung." `docs/schnellstart.md` (Abschnitt „Ueber die Oberflaeche")
beschreibt dasselbe.

Prueflauf: `Test Files 9 passed (9)`, `Tests 100 passed (100)`, `npm run typecheck`
Exit 0.

Zwei Befunde am Rande: `frontend/node_modules` fehlte im Checkout, `npm ci" war
noetig — und die Abschlussansage in `App.vue` („Alle Dateien sind fertig: N
gelungen") erwaehnt abgebrochene Dateien nicht.
