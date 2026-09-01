---
id: 78
title: BE-29 · Passthrough beschaedigt fremde Kodierungen lautlos
status: done
priority: medium
created: 2026-09-01T16:00:28.971140298+02:00
updated: 2026-09-01T16:23:26.753486511+02:00
started: 2026-09-01T16:23:00.572981431+02:00
completed: 2026-09-01T16:23:00.572981431+02:00
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

[[2026-09-01]] Tue 16:23
## Ergebnis (sophie-30)

Umgesetzt: `_encoding_warnings()` in `registry.py` zählt U+FFFD im Ergebnis und legt
bei count>0 eine Warnung dazu — Dateiname, Zahl, Deutung („Die Datei ist vermutlich
anders kodiert."), Singular/Plural nach dem Muster von `_placeholder_warnings()` in
`docling.py`. `errors="replace"` bleibt; die Kodierung wird nicht erraten.

Rot vor grün: `test_fremde_kodierung_wird_gemeldet` schlug gegen den unveränderten
Code fehl (`assert 0 == 1`, `warnings=[]` bei sechs zerstörten Umlauten). Die
Gegenprobe `test_utf8_meldet_nichts` war schon vorher grün und hält die Warnung
davon ab, überall anzuschlagen.

Zahlen: Sammelzahl vorher 143 gesammelt / 137 ausgewählt, nachher 145 / 139;
139 bestanden, 6 deselected (slow), `ruff check .` sauber.
Branch `task/78-passthrough-kodierung`, Commit 25a1210, mit `--no-ff` in main.

### Befund zur Auflage: U+FFFD kann echt in der Vorlage stehen

Eine reine UTF-8-Datei darf das Zeichen enthalten — eine Dokumentation über
Mojibake etwa, oder das Ergebnis einer früheren verlustbehafteten Wandlung.
Nachgestellt: „Ein ersetztes Zeichen sieht so aus: <U+FFFD>", als UTF-8 gespeichert,
strikt dekodierbar. Die Engine warnt trotzdem „In mojibake-doku.md wurde ein Zeichen
ersetzt …". Der Satz ist dann unwahr.

Nicht umgangen, sondern vorgelegt. Zwei Wege:

- **(a) Hinnehmen.** Die Fehlwarnung kostet eine Zeile und trifft seltene Dateien.
- **(b) Genau messen, ohne die Kodierung zu erraten.** `path.read_bytes()`, erst
  strikt dekodieren: Gelingt das, wurde kein Byte ersetzt, also `warnings=[]`. Nur
  bei `UnicodeDecodeError` mit `errors="replace"` lesen und die echten Vorkommen
  abziehen (`raw.count(b"\xef\xbf\xbd")`). Kleiner Eingriff in dieselbe Methode,
  gehört aber in ein eigenes Ticket, weil `registry.py` die Engpassdatei ist.

### Zweiter Befund, nicht geändert (war schon vorher falsch)

`docs/formate.md`, Abschnitt „Die Matrix", sagt über `.md`: „Er liest die Datei und
gibt sie unverändert zurück." Bei fremder Kodierung stimmt das nicht — die Datei
kommt mit U+FFFD zurück, jetzt immerhin mit einer Warnung daneben.
