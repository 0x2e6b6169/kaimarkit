---
id: 119
title: FE-24 · Abgewiesene Adressen bleiben im Textfeld stehen
status: done
priority: low
created: 2026-09-03T14:56:09.430537774+02:00
updated: 2026-09-03T15:13:49.126156134+02:00
started: 2026-09-03T15:13:43.14412863+02:00
completed: 2026-09-03T15:13:43.14412863+02:00
assignee: benny
tags:
    - frontend
class: standard
---

## Ziel

Befund von benny beim Abschluss von FE-22 (#115): Adressen, die `UrlInput` durchlässt und
die Warteschlange dann wegen `max_files` abweist, verschwinden trotzdem aus dem Textfeld.
Der Nutzer erfährt die Zahl — „3 wurden nicht übernommen" — aber nicht mehr, welche drei.
Er hat sie auch nicht mehr zum Wiederholen; sie sind weg.

benny hat das in #115 bewusst nicht gebaut: Der Rumpf schrieb ausdrücklich nur Zahlen vor.
Richtig so, und deshalb steht es hier.

## Eigene Dateien

- `frontend/src/components/UrlInput.vue` und `UrlInput.test.ts`
- `frontend/src/composables/useConversion.ts` und `useConversion.test.ts`
- `frontend/src/App.vue` und `App.test.ts`, nur falls der Meldungstext dort steht

Nicht hier: `frontend/src/download.ts`, `frontend/src/api.ts`, `frontend/src/types.ts`,
`frontend/src/components/FileRow.vue` und `FileQueue.vue`.

## Vorgaben

- Was die Warteschlange abweist, bleibt im Textfeld stehen. Was durchkommt, verschwindet
  daraus — wie bisher.
- Die Meldung bleibt, wie FE-22 sie gebaut hat. Sie zählt; das Feld zeigt, welche.
- Zeilen, die schon vor dem Absenden als ungültig markiert werden (kein `http://` oder
  `https://`), verhalten sich unverändert. Dieses Ticket ändert nur den Fall „gültig,
  aber kein Platz mehr".
- Die Reihenfolge der übriggebliebenen Zeilen bleibt die eingegebene.

## Prüfung

- Rot vor grün: Ein Test gibt bei `max_files: 20` und 18 belegten Plätzen fünf Adressen
  ein, erwartet zwei in der Warteschlange und die drei abgewiesenen im Textfeld — und
  fällt vor der Arbeit durch, weil das Feld leer ist.
- Ein Test belegt, dass das Feld leer wird, wenn alle Adressen Platz finden.
- `npm run test`, `npm run typecheck`, `npm run build` grün. Basislinie nach FE-22:
  10 Dateien / 134 Tests.

Umgesetzt. `enqueueUrls` gibt zurueck, wofuer kein Platz mehr war; `UrlInput` legt es ueber `keep()` zurueck ins Feld — zwischen den Zeilen ohne Schema, in der eingegebenen Reihenfolge. App.vue reicht beides zusammen (`submitUrls`). Die Meldung aus FE-22 blieb unveraendert; die Kopfprosa in UrlInput.vue war danach unwahr und ist berichtigt. Rot vor gruen: Der App-Test mit 18 belegten Plaetzen und fuenf Adressen fiel vorher durch, weil das Feld leer war. Vitest vorher 10 Dateien / 134 Tests, nachher 10 / 137 (zwei App-Tests, ein UrlInput-Test; zwei bestehende useConversion-Tests um den Rueckgabewert erweitert). typecheck und build gruen.

Befund, nicht geaendert (aelter als dieses Ticket): Der FE-22-Test 'nimmt nur so viele Eintraege an, wie limits.max_files zulaesst, und sagt es' in App.test.ts braucht auf ruhiger Maschine 2,5 bis 3,7 s von 5 s Vitest-Zeitgrenze und faellt unter Last anderer Lanes reproduzierbar mit Timeout durch — auch ohne die Aenderungen dieses Tickets (zweimal am gestashten Stand belegt, load ~9). Zwanzig Eintraege werden dort vollstaendig gewandelt, obwohl der Test nur die Aufnahme prueft; ein Wandeln, das stehen bleibt, macht ihn schnell (so geloest im neuen Test). Gruener Gesamtlauf entstand bei load 3,73.
