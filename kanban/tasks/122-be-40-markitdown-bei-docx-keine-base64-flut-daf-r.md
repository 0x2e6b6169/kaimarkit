---
id: 122
title: 'BE-40 · MarkItDown bei docx: keine base64-Flut, dafür eine Warnung'
status: todo
priority: high
created: 2026-09-03T15:13:03.634213602+02:00
updated: 2026-09-03T15:13:22.739087007+02:00
assignee: sophie
tags:
    - backend
    - gh-2
depends_on:
    - 121
class: standard
---

## Ziel

Aus der Messung in BE-38 (#117), und von sophie als das schädlichere der beiden
Verhalten benannt: **MarkItDown warnt bei docx gar nicht** und setzt stattdessen
`![](data:image/png;base64…)` ins Markdown. Bei `.docx` ist MarkItDown unter
`engine=auto` die erste Wahl — der Fall trifft also den Regelweg, nicht einen Randfall.

Zwei Schäden auf einmal. Der Nutzer erfährt nicht, dass der Inhalt des Bildes fehlt. Und
er bekommt an dessen Stelle eine base64-Zeichenkette, die sein Kontextfenster füllt. Für
ein Werkzeug, dessen Zweck es ist, prüfbaren Kontext zu **zeigen**, ist das zweite das
schwerere: Es macht das Ergebnis nicht nur unvollständig, sondern unbrauchbar.

## Eigene Dateien

- `backend/app/converters/markitdown.py` und der Test dazu

`backend/app/converters/docling.py` gehört BE-39. Falls beide Tickets an einer
gemeinsamen Datei mit Warnungstexten hängen, besitzt BE-39 sie; dieses Ticket hängt
über `depends_on` daran und läuft danach.

Nicht hier: `converters/registry.py` — dass MarkItDown bei `.docx` die erste Wahl ist,
bleibt so. Wer die Reihenfolge ändern will, meldet es; die Registry gehört BE-2.

Nicht hier: `docs/formate.md` und `docs/grenzen.md` (DOC-18). Ergibt die Arbeit, dass
dort etwas unwahr wird, melden statt ändern.

## Vorgaben

- Ein eingebettetes Bild, dessen Inhalt nicht übernommen wird, hinterlässt **keine
  base64-Zeichenkette** im Markdown. Was an seiner Stelle steht, entscheidet die
  Umsetzung — ein Platzhalter mit Dateiname, ein leeres `![]()`, gar nichts —, begründet
  in der Notiz.
- Der Fall setzt eine Warnung, und zwar mit demselben Aufbau wie in BE-39: was fehlt,
  warum, und was der Nutzer tun kann. Der Umweg ist hier: das Dokument als PDF abgeben
  und Docling mit OCR nehmen.
- Bilder, deren Inhalt MarkItDown tatsächlich übernimmt, bleiben unverändert.
- Konvention 2 hält: `markitdown` wird nur in diesem Modul importiert.

## Prüfung

- Rot vor grün: Ein Test mit dem docx-Fixture aus BE-38, das den Satz nur im
  eingebetteten Bild führt, prüft, dass im Markdown kein `data:image/` vorkommt — und
  fällt vor der Arbeit durch.
- Ein zweiter Test belegt die Warnung; ihr Wortlaut steht in richtiger Schreibung in der
  Ticketnotiz.
- Die Länge des erzeugten Markdown vor und nach der Änderung steht in der Notiz. Die
  Zahl ist der Beleg dafür, dass das Kontextfenster nicht mehr gefüllt wird.
- `pytest -q -rs` und `ruff check .` sauber; Sammelzahl und Abgewählte gemeldet.
