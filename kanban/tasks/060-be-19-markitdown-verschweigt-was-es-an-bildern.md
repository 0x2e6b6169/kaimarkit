---
id: 60
title: BE-19 · MarkItDown verschweigt, was es an Bildern weglaesst
status: todo
priority: medium
created: 2026-09-01T11:23:01.248130894+02:00
updated: 2026-09-01T12:03:27.521240605+02:00
started: 2026-09-01T12:03:27.525130027+02:00
assignee: sophie
tags:
    - backend
    - bug
class: standard
---

## Befund (01.09.2026, Frage des Nutzers waehrend der Abnahme)

`docling` sagt jetzt, wenn Inhalt fehlt: "Docling hat in X 3 Bilder durch Platzhalter
ersetzt." `markitdown` sagt nichts — bei derselben Datei, mit demselben Verlust.

`backend/app/converters/markitdown.py:1-7` haelt die Entscheidung fest: Ein
LLM-Client wird bewusst nicht gesetzt, "Bilder landen dadurch nur als Alt-Text im
Markdown, und genau das ist die gewuenschte Platzhalter-Behandlung."

## Die Annahme, die dahintersteckt

BE-14 (#47) hat markitdown ausdruecklich ausgenommen, mit dieser Begruendung: "Es
setzt den Alt-Text ein ... Ein Alt-Text ist kein leerer Platzhalter, deshalb steht
hier nur Docling."

Das stimmt fuer `.docx`, `.html` und `.epub` — dort steht ein Alt-Text im Dokument.
**Fuer PDF stimmt es nicht.** Ein PDF fuehrt keine Alt-Texte; wer dort ein Bild
weglaesst, laesst es ersatzlos weg. Und PDF ist das Format, in dem markitdown als
schnelle Alternative zu docling ueberhaupt in Frage kommt.

Die Entscheidung wurde also unter einer Annahme getroffen, die im wichtigsten Fall
nicht zutrifft.

## Warum das mehr ist als eine Ungleichheit

Wer zwischen den Engines waehlt, waehlt heute nebenbei mit, ob er von fehlendem
Inhalt erfaehrt. Das ist die eine Auskunft, wegen der es dieses Projekt gibt.

## Eigene Dateien

- `backend/app/converters/markitdown.py`
- `backend/tests/test_markitdown.py`

## Vorgaben

Erst messen, dann bauen: Was liefert markitdown fuer ein PDF mit Bildern
tatsaechlich — eine leere Bildmarke, gar nichts, einen Alt-Text? Der beobachtete
Wortlaut gehoert in die Ticketnotiz.

Danach eine Warnung nach dem Muster von `_placeholder_warnings()` in `docling.py`,
mit Zahl und Mehrzahlform. Zeigt die Messung, dass markitdown Bilder ersatzlos
weglaesst, ohne eine Marke zu hinterlassen, gehoert das gemeldet und neu geschnitten
— dann ist es kein Zaehlen mehr, sondern ein Vergleich.

## Pruefung

- Ein PDF mit Bildern durch `markitdown` liefert eine nichtleere `warnings`-Liste.
- Gegenprobe: Ein PDF ohne Bilder liefert weiterhin `warnings: []`.
- `pytest -q` bleibt gruen.

## Zurueckgestellt

Vom Nutzer zurueckgestellt, bis die Abnahme abgeschlossen ist (01.09.2026).
