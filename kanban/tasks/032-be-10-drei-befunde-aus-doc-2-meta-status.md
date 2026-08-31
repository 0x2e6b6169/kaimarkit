---
id: 32
title: 'BE-10 · Drei Befunde aus DOC-2: meta-Status, Fehlertext, passthrough'
status: done
priority: medium
created: 2026-08-31T11:28:58.151721591+02:00
updated: 2026-08-31T12:04:46.393452106+02:00
started: 2026-08-31T11:41:57.129004125+02:00
completed: 2026-08-31T12:04:46.405841382+02:00
assignee: sophie
tags:
    - backend
depends_on:
    - 29
class: standard
---

## Ziel

Beim Schreiben von `docs/api.md` (DOC-2, #21) sind drei Abweichungen aufgefallen.
Keine bricht den Schnittstellenvertrag, alle drei zeigen sich aber im Betrieb.

## Befunde

1. `meta.py::_state()` meldet ein dauerhaft fehlendes Docling als `warming`, weil
   es `available()` aufruft statt der `state()` des Adapters — die gaebe
   `unavailable` zurueck. Wer darauf wartet, wartet ewig.
2. Fehlermeldungen nennen die temporaere Datei statt der hochgeladenen:
   „Pandoc ist an tmp0mgyapow.epub gescheitert". Der Name sagt dem Nutzer nichts.
3. `capabilities.engines` enthaelt zusaetzlich `passthrough`. Das Beispiel in
   `contracts/api.md` fuehrt es nicht auf. Entweder das Beispiel ergaenzen oder die
   Engine ausblenden — der Dreiklang aus Konvention 1 entscheidet mit.

## Pruefung

Zu jedem Punkt ein Test, der den falschen Zustand vorher zeigt.

## PO-Entscheidung zu Befund 3 (2026-08-31)

`capabilities.engines` fuehrt nur die drei waehlbaren Engines: `markitdown`,
`docling`, `pandoc`. `passthrough` verschwindet aus dieser Liste — es ist keine
Engine, die jemand waehlt, und ein vierter Eintrag im Auswahlmenue tut fuer keine
Nicht-Markdown-Datei etwas.

Im Ergebnis einer Wandlung bleibt der Name erhalten: eine `.md`-Datei meldet
weiterhin `engine: "passthrough"`. Der Vertrag dokumentiert diesen Wert als
moegliche Auskunft des Feldes `engine`, ohne ihn in `capabilities.engines`
aufzunehmen.

Damit faellt dieser Befund unter Konvention 1: `contracts/api.md`,
`backend/app/models.py` und `frontend/src/types.ts` werden im selben Commit
angefasst. Die Frontend-Lane muss es sehen — in der Ticketnotiz vermerken.

## Reihenfolge

Dieses Ticket haengt an INT-1 (#29). Grund ist kein fachlicher Vorlauf, sondern
Dateieigentum: INT-1 korrigiert Abweichungen in beiden Straengen und arbeitet
gerade in `backend/app/api/meta.py` — derselben Datei wie Befund 1. Erst nach dem
Merge von INT-1 ziehen.

## Geschlossen ohne eigene Arbeit (PO, 2026-08-31)

Alle drei Befunde sind in INT-1 (#29) miterledigt worden, das denselben Code
angefasst hat. Nachgeprueft auf `main`:

1. `meta.py:41` bildet die Engines nur noch ueber `ENGINE_NAMES`, `_state()`
   fragt den Adapter nach seinem eigenen Zustand. INT-1 hat die Ursache tiefer
   gefunden als dieses Ticket sie beschrieb: `docling.py` laedt sein Modul auch
   ohne die Bibliothek, deshalb kann `available()` Vorladen und dauerhaftes
   Fehlen nicht unterscheiden. `converters/base.py` nennt `state()` jetzt als
   optionalen Teil des Protokolls, Regressionstest
   `test_engine_reports_its_own_state`.
2. Fehlermeldungen nennen die hochgeladene Datei. `uploads.py` legt den Upload
   unter seinem gesaeuberten Namen in ein eigenes `TemporaryDirectory` — das
   repariert alle drei Engines, ohne eine davon anzufassen. Konvention 5 in
   CLAUDE.md nachgezogen.
3. `passthrough` ist aus `capabilities.engines` entfernt, `formats` behaelt
   `.md -> ["passthrough"]`, der Name bleibt als `engine` eines Ergebnisses.
   Umgesetzt wie in der PO-Entscheidung oben. Der Dreiklang wurde im selben
   Commit angefasst, `OptionsPanel` filtert auf `name in engines`.

Es bleibt nichts zu bauen. Das Ticket wird geschlossen, statt einen Subagenten
auf eine leere Aufgabe zu schicken.
