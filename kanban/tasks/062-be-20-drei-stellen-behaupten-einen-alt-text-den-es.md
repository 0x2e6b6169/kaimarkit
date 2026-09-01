---
id: 62
title: BE-20 · Drei Stellen behaupten einen Alt-Text, den es bei PDF nicht gibt
status: todo
priority: medium
created: 2026-09-01T12:08:32.215028701+02:00
updated: 2026-09-01T12:08:32.215028701+02:00
assignee: sophie
tags:
    - backend
    - docs
class: standard
---

## Befund (01.09.2026, gemessen in BE-19/#60 von sophie)

Drei Stellen sagen dasselbe Unwahre:

- `backend/app/converters/markitdown.py:1-7` — "Bilder landen dadurch nur als
  Alt-Text im Markdown, und genau das ist die gewuenschte Platzhalter-Behandlung."
- `docs/formate.md:74`
- `docs/grenzen.md:66`

Fuer `.docx`, `.html` und `.epub` stimmt es — dort steht ein Alt-Text im Dokument.
**Fuer PDF stimmt es nicht.** Gemessen mit markitdown 0.1.7 und pdfminer.six
20260107:

- Ein PDF mit zwei Image-XObjects liefert Zeichen fuer Zeichen dasselbe Markdown wie
  dasselbe PDF ohne Bilder.
- Ein PDF, das nur aus einem Bild besteht, liefert die leere Zeichenkette.
- Gegenprobe: `pdfplumber.page.images` sieht in den drei Faellen 2, 0 und 1 Bilder.

Ursache in `_pdf_converter.py` von markitdown: Es ruft `extract_text` und zieht
ausschliesslich Text. Bilder kommen dort nicht vor.

## Warum das ein eigenes Ticket ist

Diese Annahme hat BE-14 (#47) dazu gebracht, markitdown von der Platzhalter-Warnung
auszunehmen. Sie steht seither an drei weiteren Stellen und bleibt falsch, ganz
gleich wie #60 neu geschnitten wird. Was schon vorher falsch war, wird gemeldet statt
nebenbei geaendert — deshalb hat sophie es gemeldet, und deshalb steht es hier.

## Eigene Dateien

- `backend/app/converters/markitdown.py` (Modul-Docstring)
- `docs/formate.md` (Abschnitt "MarkItDown")
- `docs/grenzen.md` (die betroffene Zeile)

Beruehrt `#60`: Wird das dort neu geschnitten, haengt es hinter diesem Ticket.

## Vorgaben

Die drei Stellen sagen, was zutrifft: Bei Formaten mit Alt-Text erscheint der
Alt-Text; **bei PDF verschwinden Bilder ersatzlos und ohne Hinweis.** Der zweite
Halbsatz ist der wichtigere — er ist die Auskunft, die ein Leser braucht, um die
Enginewahl zu verstehen.

Kein Code, keine Warnung. Ob und wie kaimarkit das meldet, entscheidet #60.

## Pruefung

- Keine der drei Stellen behauptet noch einen Alt-Text fuer PDF.
- `pytest -q` bleibt gruen (der Docstring aendert kein Verhalten).
- `make docs-serve` rendert beide Seiten fehlerfrei.
