---
id: 52
title: BE-16 · Zwei fast gleiche Docling-Attrappen zusammenlegen
status: done
priority: low
created: 2026-09-01T09:08:32.161989361+02:00
updated: 2026-09-01T13:40:14.673787883+02:00
started: 2026-09-01T13:26:50.821418637+02:00
completed: 2026-09-01T13:39:29.793358269+02:00
assignee: sophie
tags:
    - backend
    - tests
depends_on:
    - 47
    - 58
class: standard
---

## Befund (01.09.2026, gemeldet von sophie aus BE-13)

`backend/tests/test_docling.py` und `backend/tests/test_docling_ocr.py` halten zwei
fast gleiche Attrappen des Docling-Moduls. Jede Aenderung am Adapter muss beide
nachziehen.

In BE-13 ist genau das eingetreten: Der neue Import von `ImageFormatOption` und
`InputFormat.IMAGE` liess die Attrappe aus BE-12 scheitern. Fuenf Zeilen mussten
mit, obwohl kein offenes Ticket die Datei besass. Richtig so — wer ein Verhalten
aendert, berichtigt im selben Merge, was dadurch falsch wird. Aber es waechst mit
jedem weiteren Docling-Ticket.

## Ziel

Eine gemeinsame Attrappe, an einer Stelle gepflegt.

## Eigene Dateien

- `backend/tests/test_docling.py`
- `backend/tests/test_docling_ocr.py`
- `backend/tests/conftest.py`

Haengt an #47 (BE-14), das `test_docling.py` bereits besitzt.

## Vorgaben

Die Attrappe wandert als Fixture nach `conftest.py`; beide Testmodule ziehen sie
von dort. Keine Testaussage aendert sich dabei — das hier ist Umbau, nicht neue
Abdeckung.

## Pruefung

- `pytest -q` und `pytest -q -m slow` bleiben gruen, mit derselben Zahl bestandener
  Tests wie vorher.
- `grep -c "class .*Docling\|MagicMock" backend/tests/test_docling*.py` findet die
  Attrappe nur noch einmal, in `conftest.py`.
- Gegenprobe: Ein Fehler in der gemeinsamen Attrappe laesst beide Module scheitern,
  nicht nur eines.


## Ergebnis (01.09.2026, sophie-27)

Die Attrappe der Docling-Module liegt jetzt als Fixture `fake_docling` in
`backend/tests/conftest.py`; beide Testmodule ziehen sie von dort.
`install_fake_docling` ist aus beiden Dateien verschwunden.

**Worin sich die zwei Kopien unterschieden.** Nur ein Unterschied war noetig: In
`test_docling_ocr.py` starteten die Pipeline-Optionen mit `FakeOcrAutoOptions` —
Doclings echter Vorgabe — und die Modulkarte fuehrte `OcrAutoOptions` mit. Nur so
belegt der Test, dass der Adapter die Vorgabe durch `EasyOcrOptions` ersetzt. Das
gemeinsame Fixture uebernimmt diese Fassung; fuer `test_docling.py` aendert das
keine Aussage. Alles Uebrige war Auseinanderdriften und ist weg: `dict` gegen
`SimpleNamespace` als Rueckgabe, gewoehnliche Klasse gegen `dataclass` bei
`FakeEasyOcrOptions`, `ImageRefMode.PLACEHOLDER` als "p" gegen "placeholder".

**Zahlen, vorher wie nachher gleich.** Sammellauf 137/143 (6 deselected);
`pytest -q -rs` 137 passed; `pytest -q -m slow -rs` 6 skipped (docling nicht
installiert, sauber uebersprungen); `ruff check .` sauber.

**Gegenprobe gefahren.** `ImageFormatOption` aus der gemeinsamen Attrappe
entfernt — genau der BE-13-Fall. Es fallen vier Tests, zwei in `test_docling.py`
und zwei in `test_docling_ocr.py`. Danach zurueckgenommen, wieder gruen.

**Zur Pruefvorgabe.** Das grep aus dem Ticket zaehlt in beiden Dateien 0 — und tat
das auch vorher schon: `MagicMock` kommt im Projekt nirgends vor, und keine
Attrappenklasse heisst `...Docling`. Ersatzprobe: `install_fake_docling` hat 0
Treffer in beiden Testmodulen, die Attrappenklassen stehen nur noch in
`conftest.py`. Der eine verbliebene `class Fake...` in `test_docling.py` ist
`FakePipeline` — die Attrappe von `_build_pipeline`, etwas anderes und nirgends
doppelt.

**Befund, nicht mitgeaendert.** Die autouse-Fixture `fresh_settings` steht
weiterhin wortgleich in beiden Modulen. Sie nach `conftest.py` zu ziehen wuerde sie
projektweit autouse machen und damit das Verhalten der uebrigen Testmodule aendern
— das ist kein Umbau mehr und gehoert in ein eigenes Ticket.

Merge: 7c90174 (--no-ff), Commit 518c736 auf task/52-attrappen-zusammenlegen.
