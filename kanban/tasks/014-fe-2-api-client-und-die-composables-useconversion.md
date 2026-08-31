---
id: 14
title: FE-2 · API-Client und die Composables useConversion und useCapabilities
status: done
priority: high
created: 2026-08-31T10:20:19.634429753+02:00
updated: 2026-08-31T11:00:46.7798436+02:00
started: 2026-08-31T11:00:00.248161434+02:00
completed: 2026-08-31T11:00:00.248161434+02:00
assignee: benny
tags:
    - frontend
depends_on:
    - 13
class: standard
---

## Ziel

Die einzige Stelle, an der das Frontend mit dem Backend spricht, und der Zustand
der Warteschlange.

## Eigene Dateien

- `frontend/src/api.ts`
- `frontend/src/composables/useConversion.ts`
- `frontend/src/composables/useCapabilities.ts`

## Vorgaben

- `api.ts` nutzt ausschliesslich die Typen aus `src/types.ts`. Wer hier ein Feld
  braucht, das dort fehlt, aendert `contracts/api.md`, `models.py` und `types.ts`
  gemeinsam - nicht nur eine der drei Dateien.
- `useConversion` haelt eine Liste von Eintraegen mit Status
  (`queued`, `running`, `ok`, `failed`), Ergebnis, Warnungen und Fehler.
- **Hoechstens zwei Konvertierungen gleichzeitig**, die uebrigen warten. Das
  Backend bremst zwar selbst, aber ohne Begrenzung im Frontend sieht der Nutzer
  zwanzig gleichzeitig laufende Zeilen, von denen sich nichts bewegt.
- `useCapabilities` laedt `/api/capabilities` einmal und stellt bereit, welche
  Engines je Endung zur Wahl stehen und ob OCR verfuegbar ist.
- Netzfehler und HTTP-Fehler landen als lesbare Meldung am Eintrag, nicht in der
  Konsole.

## Pruefung

Ein Vitest-Test fuer `useConversion` mit einem Attrappen-Client: fuenf Dateien,
hoechstens zwei laufen gleichzeitig, ein Fehlschlag stoppt die uebrigen nicht.


## Ergebnis (benny-02)

Gemerged als bec39d4, Branch `task/14-api-client-composables`, `--no-ff` nach main.

**Gebaut**

- `src/api.ts` — die einzige Stelle zum Backend: `fetchCapabilities()` und
  `convertFile(file, options)`. Jeder Netz- und HTTP-Fehler kommt als `ApiError`
  (`message` ist das `detail` aus dem Rumpf, dazu `status` und `code`);
  `messageFromError(cause)` liefert die Meldung fuer die Oberflaeche.
  `Accept: application/json` steht an jeder Anfrage — ohne den Kopf gaebe
  `/api/convert` Markdown als Download zurueck. `ocr` geht nur mit, wenn es
  nicht `null` ist.
- `src/composables/useConversion.ts` — `createConversionQueue({convert, maxParallel})`
  als Fabrik, `useConversion()` als geteilte Warteschlange im Modul (kein Pinia,
  kein Provide). Ein Eintrag: `{id, filename, status, markdown, engine, warnings,
  error, durationMs}` mit `status` aus `queued|running|ok|failed`. Hoechstens zwei
  Laeufe gleichzeitig, das Nachruecken passiert im `finally`. Die `File`-Objekte
  liegen ausserhalb der Reaktivitaet, weil `FormData.append` keinen Vue-Proxy annimmt.
- `src/composables/useCapabilities.ts` — laedt einmal, mehrere Aufrufe teilen sich
  denselben Abruf. Bietet `capabilities`, `loading`, `error`, `extensions`,
  `engines`, `limits`, `ocrAvailable`, `enginesFor(filename)`, `supports(filename)`,
  `load()`, `reload()`.
- `src/composables/useConversion.test.ts` — der Test aus der Pruefung.

**Pruefung, tatsaechlich gelaufen**

- `npm run test` -> `Test Files 1 passed (1)`, `Tests 3 passed (3)`. Fuenf Dateien,
  gemessener Hoechststand zwei gleichzeitig, ein Fehlschlag laesst die uebrigen
  vier durchlaufen.
- `npm run typecheck` -> ohne Ausgabe, also sauber.
- `npm run build` -> 12 Module, fertig in 911 ms.

**Fuer FE-3 bis FE-7**

- FE-3 ruft `enqueue(files)` und `remove(id)`, `clear()` leert die Liste; `busy`
  zeigt, ob noch etwas wartet oder laeuft.
- FE-5 bindet an `queue.options.value` (`{engine, ocr}`). Die Auswahl gilt fuer den
  naechsten Start, nicht rueckwirkend fuer laufende Zeilen. Welche Engines zur Wahl
  stehen, sagt `enginesFor(filename)`; `load()` muss einmal gerufen werden, am
  besten in `App.vue`.
- FE-4 und FE-6 lesen `markdown` und `filename` vom Eintrag. Das ZIP baut das
  Frontend selbst, `/api/convert/batch` ruft niemand.

**Schnittstellen-Dreiklang unberuehrt.** `types.ts`, `models.py` und
`contracts/api.md` blieben unveraendert, es fehlte kein Feld.

**Doku-Luecke fuer akar:** `docs/entwicklung.md` gehoert DOC-2 (#21) und ist noch
ein Stumpf. Der Aufbau des Frontends — `api.ts` als einzige Grenze, zwei
gleichzeitige Laeufe in der Warteschlange, Zustand in Composables statt Pinia —
gehoert dorthin. Solange steht die Begruendung in den Kopfkommentaren der drei
Dateien.
