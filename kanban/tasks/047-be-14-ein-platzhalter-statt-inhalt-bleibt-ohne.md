---
id: 47
title: BE-14 · Ein Platzhalter statt Inhalt bleibt ohne Warnung
status: backlog
priority: medium
created: 2026-08-31T17:08:22.240557722+02:00
updated: 2026-08-31T17:08:22.240557722+02:00
assignee: sophie
tags:
    - backend
    - bug
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
