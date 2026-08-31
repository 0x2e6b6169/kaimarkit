---
id: 14
title: FE-2 · API-Client und die Composables useConversion und useCapabilities
status: todo
priority: high
created: 2026-08-31T10:20:19.634429753+02:00
updated: 2026-08-31T10:30:45.656596969+02:00
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
