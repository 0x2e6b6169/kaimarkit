---
id: 47
title: BE-14 · Ein Platzhalter statt Inhalt bleibt ohne Warnung
status: done
priority: high
created: 2026-08-31T17:08:22.240557722+02:00
updated: 2026-09-01T09:12:51.767203218+02:00
started: 2026-09-01T09:12:07.741377092+02:00
completed: 2026-09-01T09:12:07.741377092+02:00
assignee: sophie
tags:
    - backend
    - bug
depends_on:
    - 46
class: standard
---

## Ziel

Wer ein Ergebnis bekommt, soll erkennen koennen, dass ein Teil der Vorlage nicht im
Markdown steht. Heute steht dort ein Platzhalter und `warnings` bleibt leer.

## Befund (belegt in INT-2, 31.08.2026, im laufenden Container)

Ein PDF mit einer siebenspaltigen Tabelle, echte Textebene, durch beide Engines:

```
engine=auto (docling)   17266 ms   warnings=[]
    ## Kaimarkit Breittabelle
    <!-- image -->

engine=markitdown          35 ms   warnings=[]
    Kaimarkit Breittabelle
    | Kennung | Format | Engine     | OCR  | Groesse | Dauer | Ergebnis     |
    | ------- | ------ | ---------- | ---- | ------- | ----- | ------------ |
    | A-01    | pdf    | docling    | ja   | 12 MB   | 8,4 s | vollstaendig |
    ... vier Zeilen vollstaendig ...
```

Docling steht in `/api/capabilities` fuer `.pdf` an erster Stelle und ist damit die
Engine bei `engine=auto`. Sie hat die Tabelle als Bild eingeordnet und durch
`<!-- image -->` ersetzt. Die Antwort lautet `status: "ok"`, `warnings` ist leer.
Nichts an ihr sagt, dass der halbe Inhalt fehlt.

## Worum es hier geht

Ob Doclings Tabellenmodell diese Tabelle erkennt, entscheidet Docling. Dass
kaimarkit einen Platzhalter ohne ein Wort weiterreicht, entscheidet kaimarkit.

`backend/app/converters/docling.py:86` waehlt den Platzhaltermodus ausdruecklich:

```python
return document.export_to_markdown(image_mode=ImageRefMode.PLACEHOLDER)
```

Eine Warnung dafuer ist im Vertrag bereits vorgesehen. `contracts/api.md:158`
fuehrt sie als Beispiel:

```json
"warnings": ["Seite 4 enthielt ein Bild, das durch einen Platzhalter ersetzt wurde."]
```

Gebaut wurde sie nie. `grep -n warning app/converters/docling.py` findet eine
einzige Zeile, und die protokolliert nur, dass Docling fehlt.

## Eigene Dateien

- `backend/app/converters/docling.py`
- `backend/tests/test_docling.py`

## Vorgaben

Enthaelt das erzeugte Markdown Platzhalter, zaehlt sie der Adapter und legt eine
Warnung dazu. Die Zahl gehoert hinein — ein einzelnes ersetztes Bild ist etwas
anderes als vierzehn.

Ob markitdown dasselbe braucht, entscheidet sich am eigenen Modul: Es setzt den
Alt-Text ein, laut Kopfkommentar in `markitdown.py:5` gewollt. Ein Alt-Text ist
kein leerer Platzhalter, deshalb steht hier nur Docling.

## Pruefung

- Das PDF aus dem Befund liefert eine nichtleere `warnings`-Liste, die den
  Platzhalter benennt.
- Gegenprobe: Ein PDF ohne Platzhalter im Ergebnis liefert weiterhin `warnings: []`.
  Sonst warnt der Adapter immer und die Warnung sagt nichts mehr.
- `pytest -q` bleibt gruen.

[[2026-09-01]] Tue 08:53
Vom PO auf high gehoben und nach todo gezogen. Der Nutzer will die Fassung selbst im Browser pruefen, und dieser Fehler trifft genau das: Eine Tabelle verschwindet, `status` sagt `ok`, `warnings` ist leer. Wer den Kontext sehen will, den er einem LLM gibt — der Zweck dieses Projekts —, sieht hier das Gegenteil und merkt es nicht.

Ausserdem: **#46 und #47 besitzen dieselben zwei Dateien** (`docling.py`, `test_docling.py`). Nach dem Ticketschnitt duerfen sie nicht gleichzeitig laufen. Deshalb haengt #47 jetzt an #46 — `--unblocked` blendet es aus, bis #46 durch ist. Kein Schnittfehler, sondern zwei Befunde aus demselben Lauf am selben Modul; die Reihenfolge loest es.

[[2026-09-01]] Tue 09:12
Gebaut: `_placeholder_warnings(markdown, name)` in `docling.py` zaehlt `<!-- image -->` im exportierten Markdown; `convert()` legt daraus genau eine Warnung ins Ergebnis. Der Text nennt Datei und Zahl: "Docling hat in bericht.pdf 3 Bilder durch Platzhalter ersetzt. Ihr Inhalt fehlt im Markdown." Bei genau einem Platzhalter: "... ein Bild durch einen Platzhalter ersetzt. Sein Inhalt fehlt im Markdown."

Rot vor gruen: Die drei neuen Tests liefen zuerst gegen den unveraenderten Adapter — `2 failed, 12 passed, 2 deselected`, beide Zaehltests mit `assert 0 == 1` auf leeren `warnings`. Die Gegenprobe war schon vorher gruen, wie sie sollte. Nach der Aenderung: `pytest -q` = 112 passed, 4 deselected; `ruff check .` sauber.

Geprueft auf der Ebene, die ohne docling laeuft: gegen die Nachbearbeitung des Markdown-Strings ueber die vorhandene `FakePipeline`. Ein echter Docling-Lauf gegen das Befund-PDF steht aus und ist im Container zu pruefen — docling ist in der geteilten pyenv-Umgebung nicht installiert und darf es dort nicht werden.

`test_docling_ocr.py` blieb unberuehrt und gruen. markitdown blieb aussen vor: Es setzt den Alt-Text ein, das ist laut Kopfkommentar gewollt und kein leerer Platzhalter.

Befund fuer den PO: In `docs/formate.md` (Abschnitt "Docling") wird durch die Aenderung nichts unwahr, aber der Abschnitt erwaehnt die neue Warnung nicht — anders als die Abschnitte zu MarkItDown und Pandoc, die ihre `warnings` benennen. Ein Satz dort waere konsequent.
