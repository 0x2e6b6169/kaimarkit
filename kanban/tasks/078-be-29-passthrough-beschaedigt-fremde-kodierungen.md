---
id: 78
title: BE-29 · Passthrough beschaedigt fremde Kodierungen lautlos
status: todo
priority: medium
created: 2026-09-01T16:00:28.971140298+02:00
updated: 2026-09-01T16:00:28.971140298+02:00
assignee: sophie
tags:
    - backend
    - bug
class: standard
---

## Befund (01.09.2026, beim Prüfen der Passthrough-Engine)

`backend/app/converters/registry.py:73`:

```python
markdown = path.read_text(encoding="utf-8", errors="replace")
```

`errors="replace"` ersetzt jedes Byte, das kein gültiges UTF-8 ist, durch U+FFFD (`�`)
— **stillschweigend**. Eine Markdown-Datei in ISO-8859-1, im deutschsprachigen Raum
keine Seltenheit, kommt mit zerstörten Umlauten zurück: `status: "ok"`, `warnings: []`,
nichts sagt etwas.

Das ist genau das Muster, das BE-14 (#47) für Docling-Platzhalter und BE-19 (#60) für
MarkItDown-Bilder beseitigt hat — Inhalt geht verloren, und die Antwort schweigt.
Hier trifft es die einzige Engine, bei der der Nutzer sicher ist, dass nichts
passieren kann: Sie reicht ja nur durch.

## Warum `errors="replace"` trotzdem richtig bleibt

Die Alternative wäre ein Fehlschlag statt eines Ergebnisses. Für einen Stapel ist das
schlechter: Eine Datei mit einem einzigen krummen Byte risse sonst ihren Eintrag
weg, statt ihn mit einem Hinweis zu liefern. Also nicht die Ersetzung abschaffen,
sondern sie benennen.

## Eigene Dateien

- `backend/app/converters/registry.py` (Klasse `_Passthrough`)
- `backend/tests/test_converters.py`

`registry.py` ist die Engpassdatei — solange dieses Ticket offen ist, fasst sie kein
zweites an.

## Vorgaben

Zählt das Ergebnis U+FFFD, legt die Engine eine Warnung dazu, nach dem Muster von
`_placeholder_warnings()` in `docling.py`: Datei, Zahl, und was das bedeutet. Etwa
„In X wurden N Zeichen ersetzt, die kein gültiges UTF-8 waren. Die Datei ist
vermutlich anders kodiert."

Die Zahl gehört hinein — ein ersetztes Zeichen ist etwas anderes als vierhundert.

**Nicht** die Kodierung erraten und umwandeln. Das wäre ein anderes Ticket und eine
andere Zusage; hier geht es darum, den Verlust zu melden, nicht ihn zu heilen.

Prüfen, ob U+FFFD auch **echt** in der Vorlage stehen kann — dann warnt die Engine zu
Unrecht. Ist das der Fall, gehört es gemeldet statt umgangen.

## Prüfung

- Eine Markdown-Datei in ISO-8859-1 mit Umlauten liefert eine nichtleere
  `warnings`-Liste mit der Zahl der ersetzten Zeichen.
- Gegenprobe: Dieselbe Datei in UTF-8 liefert `warnings: []`.
- Der Inhalt kommt in beiden Fällen zurück; die Umwandlung schlägt nicht fehl.
- `pytest -q -rs` bleibt grün, Sammelzahl in der Notiz.
