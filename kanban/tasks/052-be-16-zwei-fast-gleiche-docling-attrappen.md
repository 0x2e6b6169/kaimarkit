---
id: 52
title: BE-16 · Zwei fast gleiche Docling-Attrappen zusammenlegen
status: backlog
priority: low
created: 2026-09-01T09:08:32.161989361+02:00
updated: 2026-09-01T09:08:33.341501608+02:00
assignee: sophie
tags:
    - backend
    - tests
depends_on:
    - 47
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
