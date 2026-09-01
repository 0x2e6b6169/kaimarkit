---
id: 79
title: FE-14 · Eine laufende Umwandlung laesst sich nicht abbrechen
status: todo
priority: high
created: 2026-09-01T16:01:34.173915519+02:00
updated: 2026-09-01T16:01:34.173915519+02:00
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
