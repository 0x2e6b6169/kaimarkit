---
id: 68
title: FE-12 · Die Warteschlange sagt nicht, wie lange etwas schon laeuft
status: done
priority: medium
created: 2026-09-01T12:26:28.862983617+02:00
updated: 2026-09-01T12:34:58.250037783+02:00
started: 2026-09-01T12:34:58.299989826+02:00
completed: 2026-09-01T12:34:58.299989826+02:00
assignee: benny
tags:
    - frontend
    - ux
class: standard
---

## Befund (01.09.2026, aus der Abnahme des Nutzers)

Der Nutzer hat ein PDF hochgeladen und nach einer Minute gefragt: "Wie lange soll das
dauern?" Die Frage ist der Befund. In der Warteschlange stand nur „läuft" — kein
Anhalt, ob das Sekunden oder Minuten bedeutet und ob überhaupt noch etwas geschieht.

Gemessen an seinen eigenen Dokumenten:

    Bahnrechnung, 1 Seite   docling   103,5 s
    Anmeldung               docling   326,1 s
    dieselbe Datei          docling   in die Zeitgrenze gelaufen

Fünfeinhalb Minuten ohne Rückmeldung sind der Normalfall bei Docling, nicht die
Ausnahme. Wer nicht weiß, dass das normal ist, hält den Dienst für hängengeblieben —
und genau das ist an diesem Vormittag zweimal passiert, einmal zu Recht und einmal zu
Unrecht.

## Ziel

Wer wartet, sieht, dass etwas geschieht und wie lange schon.

## Eigene Dateien

- `frontend/src/components/FileRow.vue`
- `frontend/src/components/FileQueue.vue`
- die zugehörigen Tests

## Vorgaben

Pragmatisch, nicht schön: Eine mitlaufende Zeitangabe an der laufenden Zeile genügt —
„läuft · 0:47". Mehr ist nicht zu holen, weil das Backend keinen Fortschritt meldet;
es gibt nur Anfang und Ende.

Eine Fortschrittsanzeige, die Vollständigkeit vortäuscht, wäre schlechter als keine.
Was nicht bekannt ist, wird nicht behauptet.

Ob zusätzlich ein Hinweis auf die zu erwartende Größenordnung sinnvoll ist, entscheidet
die Lane — FE-9 nennt bei der Enginewahl bereits, dass Docling Minuten braucht. Zwei
Stellen mit derselben Aussage sind eine zu viel.

## Prüfung

- Eine laufende Zeile zeigt die verstrichene Zeit und zählt weiter.
- Sie verschwindet, sobald die Datei fertig oder fehlgeschlagen ist; die fertige Zeile
  behält die Gesamtdauer, die sie heute schon zeigt.
- Kein Prozentwert und kein Balken, der einen Fortschritt behauptet.
- `npm run test` und `npm run typecheck` bleiben grün; ohne die Änderung fällt der
  neue Test durch.

[[2026-09-01]] Tue 12:34
## Ergebnis (benny-13)

Die laufende Zeile zeigt „läuft · 0:47" und zählt im Sekundentakt weiter. Den
Startzeitpunkt hält `FileRow.vue` selbst; er wird gesetzt, sobald der Status auf
`running` wechselt. `useConversion.ts` und `types.ts` blieben unberührt — außerhalb
der eigenen Dateiliste war nichts nötig. Der Intervall endet beim Wechsel nach `ok`
oder `failed` und beim Unmount. Kein Prozentwert, kein Balken.

Auf einen Hinweis zur Größenordnung verzichtet: `EngineSelect.vue` (FE-9) nennt die
Minuten bei Docling bereits. Keine Zusicherung außerhalb der eigenen Dateien betroffen —
`FileQueue.test.ts` prüft `/läuft/g` und zählt weiterhin richtig.

Vier neue Tests in `FileRow.test.ts` mit `vi.useFakeTimers`; 90 Tests grün, `typecheck`
grün. Gegenprobe ohne die Änderung: drei der vier fallen durch.

Merge: `task/68-laufzeit`, `--no-ff`.
