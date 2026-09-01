---
id: 64
title: BE-21 · Fehlermeldungen an den Nutzer stehen in ASCII-Umschrift
status: done
priority: medium
created: 2026-09-01T12:12:55.183359933+02:00
updated: 2026-09-01T12:17:56.517979899+02:00
started: 2026-09-01T12:17:50.685808432+02:00
completed: 2026-09-01T12:17:50.685808432+02:00
assignee: sophie
tags:
    - backend
    - ux
class: standard
---

## Befund (01.09.2026, aus dem Befund von benny zu FE-10 weitergesucht)

Dasselbe wie im Frontend, nur schwerer zu sehen, weil es erst im Fehlerfall auftaucht.
Der Nutzer hat es waehrend der Abnahme gelesen:

    Die Umwandlung hat die Zeitgrenze von 120 s ueberschritten

Erzeugt in `backend/app/uploads.py:121-122`. Weitere Stellen:

- `backend/app/uploads.py:91` — "{filename} ueberschreitet {n} MB"
- `backend/app/errors.py:60` — "Die Datei ueberschreitet ..."
- `backend/app/errors.py:67` — "Der Stapel ueberschreitet ..."
- `backend/app/errors.py:74` — "Die Zeitgrenze ... ist abgelaufen."

## Abgrenzung

Nur Zeichenketten, die als Meldung beim Nutzer landen. **Nicht** Docstrings,
Kommentare und Bezeichner — die bleiben, wie sie sind. Das haelt den Diff klein und
die Pruefung eindeutig.

## Eigene Dateien

- `backend/app/errors.py`
- `backend/app/uploads.py`
- die zugehoerigen Tests

Beruehrt sich nicht mit #60 (markitdown-Adapter und Doku).

## Vorgaben

Von Hand pruefen, nicht ersetzen lassen. Wo eine Meldung ohnehin angefasst wird,
gilt `SPRACHE.md` auch fuer den Rest des Satzes.

## Pruefung

- `grep -rnP "ueber|fuer|naech|waeh|groess" backend/app/errors.py backend/app/uploads.py`
  findet keine Treffer mehr in Zeichenketten, die zum Nutzer gehen.
- `pytest -q` bleibt gruen. Prueft ein Test auf den alten Wortlaut, wird er
  mitgezogen — er gehoert zu denselben Dateien.
- Gegenprobe: Eine Umwandlung, die in die Zeitgrenze laeuft, meldet "überschritten".

## Ergebnis (sophie-16, 01.09.2026)

Umgesetzt in `uploads.py`: die beiden Meldungen stehen jetzt mit Umlaut —
"{filename} überschreitet {n} MB" und "Die Umwandlung hat die Zeitgrenze von
{n} s überschritten". Sonst nichts umformuliert; die Saetze waren in Ordnung.

`errors.py` blieb unveraendert. Die drei im Ticket genannten Zeilen (:60, :67,
:74) sind Docstrings, keine Meldungen, und die Abgrenzung des Tickets nimmt
Docstrings ausdruecklich aus. `errors.py` enthaelt ueberhaupt keine Zeichenkette,
die zum Nutzer geht: alle `detail` kommen von den Aufrufern.

**Bewusst stehen gelassen** (Kommentar oder Docstring, nie nutzersichtbar):
`errors.py:60`, `:67`; `uploads.py:29`, `:32`, `:55`, `:71`, `:73`, `:75`.
Der grep des Tickets findet in beiden Dateien nur noch diese.

**Tests:** Die beiden vorhandenen Faelle in `test_uploads.py` pruefen jetzt
zusaetzlich den Wortlaut. Ein Rueckfall bricht damit einen Test, statt nur in der
Oberflaeche aufzutauchen. Kein Test prueft den alten Wortlaut — es musste keiner
nachgezogen werden.

**Pruefung:** `pytest -q` 112 passed, 4 deselected. `ruff check .` sauber.
Gegenprobe ueber die echte API mit TestClient ausgefuehrt, nicht angenommen:
504 mit "Die Umwandlung hat die Zeitgrenze von 1 s überschritten" und
413 mit "gross.pdf überschreitet 1 MB". Kein Container gebaut, kein Dienst
gestartet.

Branch `task/64-meldungen-umlaute`, Commit `8a60f2b`, Merge `07af096`.

## Befund fuer den PO — dieselbe Umschrift ausserhalb dieser Dateien

Nutzersichtbare Meldungen, absichtlich nicht angefasst:

- `api/convert.py:100` — "Hoechstens {n} Dateien je Aufruf"
- `converters/registry.py:94` "ist nicht verfuegbar", `:130` "Fuer {ext} …
  gibt es keine Engine.", `:138` "Fuer {ext} ist zurzeit keine Engine verfuegbar."
- `converters/pandoc.py:70` "Dateien ohne Endung", `:91` "Pandoc laesst sich
  nicht aufrufen"
- `converters/docling.py:183` "Docling ist nicht verfuegbar"
- `markitdown.py` laeuft parallel unter #60, dort nicht geprueft.

Dazu: die Felderklaerungen in `models.py` erscheinen als OpenAPI-Beschreibungen
unter `/docs` und stehen ebenfalls in Umschrift.
