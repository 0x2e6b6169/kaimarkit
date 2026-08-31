---
id: 39
title: FE-8 · Favicon fuer frontend/index.html
status: done
priority: low
created: 2026-08-31T12:04:19.217951051+02:00
updated: 2026-08-31T12:12:18.839344587+02:00
started: 2026-08-31T12:04:54.100728418+02:00
completed: 2026-08-31T12:11:37.918639408+02:00
assignee: benny
tags:
    - frontend
class: standard
---

## Ziel

`frontend/index.html` nennt kein Favicon. Der Browser fragt bei jedem Aufruf
`/favicon.ico` und bekommt 404. Kosmetisch, keine Abweichung vom Vertrag —
gemeldet von INT-1 (#29).

## Eigene Dateien

- `frontend/index.html`
- die neue Symboldatei unter `frontend/public/`

## Vorgaben

- Ein schlichtes Symbol, das ohne Netz auskommt und im Abbild mitgeliefert wird.
- Kein zusaetzliches Paket dafuer.

## Pruefung

Ein Aufruf der Seite erzeugt keine 404 auf `/favicon.ico` mehr. `npm run build`
nimmt die Datei mit.

[[2026-08-31]] Mon 12:12
## Ergebnis (benny-09)

Umgesetzt in `frontend/public/favicon.svg` (neu) und `frontend/index.html`
(+2 Zeilen: Kommentar und `<link rel="icon" type="image/svg+xml" href="/favicon.svg">`).
Kein neues Paket, kein Netzzugriff: Das Symbol ist eine handgezeichnete SVG-Kachel
von 389 Byte, sky-600 gefuellt, mit weissem M und Abwaertspfeil. Die gefuellte
Flaeche bleibt auf heller wie auf dunkler Browserleiste lesbar. `style.css` blieb
unberuehrt.

**Pruefung, tatsaechlich gelaufen** (Dev-Server auf Port 5199 im Worktree):

- `curl -s http://localhost:5199/ | grep -i icon` liefert die Link-Zeile. Der
  Browser bekommt ein ausdrueckliches Symbol genannt und faellt deshalb nicht mehr
  auf `/favicon.ico` zurueck.
- `curl -o /dev/null -w '%{http_code} %{content_type}' /favicon.svg` antwortet
  `200 image/svg+xml`, 389 Byte.
- `npm run build` meldet `built in 2.05s`; `dist/favicon.svg` liegt mit 389 Byte
  neben `dist/index.html`, dessen Link-Zeile erhalten bleibt.
- `npm run typecheck` ohne Befund, `npm run test` 8 Dateien, 79 Tests, alle gruen.

Eine Anmerkung zur Messung: `/favicon.ico` antwortet weiterhin mit 404, wenn man
den Pfad von Hand abruft. Das ist erwartet, denn die Datei existiert nicht und soll
es nicht. Die 404 verschwindet, weil kein Browser den Pfad noch anfragt, sobald
`<link rel="icon">` im Dokument steht.

Doku nicht angefasst: kein sichtbares Verhalten, keine Konvention, keine Variable.

Branch `task/39-favicon`, Commit 792167b, mit `--no-ff` nach main gemerged (35454b0).
