---
id: 112
title: 'DOC-16 · docs/formate.md: warming-Engines werden angeboten, nicht verschwiegen'
status: todo
priority: medium
created: 2026-09-03T11:42:53.956405461+02:00
updated: 2026-09-03T11:42:53.956405461+02:00
assignee: akar
tags:
    - docs
class: standard
---

## Ziel

Befund aus FE-20 (#105), von katche bestätigt: `docs/formate.md` sagt im Abschnitt „Docling", eine Engine im Zustand `warming` werde von `GET /api/capabilities` nicht angeboten. Das Gegenteil gilt. `contracts/api.md` führt `warming` als Wert in `engines` („lädt noch, eine Anfrage wartet"), `api/meta.py` liefert ihn, und das Frontend bietet die Engine mit dem Zusatz „(lädt noch)" an. Nur `unavailable` fällt aus `formats` heraus.

## Eigene Dateien

- `docs/formate.md` (Abschnitt „Docling: Modelle und OCR"), die Sätze ab „Solange gilt die Engine als `warming`"

## Vorgaben

- Quelle ist `contracts/api.md` (Abschnitt `GET /api/capabilities` und `EngineState`) und `backend/app/api/meta.py`; was dort steht, gilt. Insbesondere prüfen, was `engine=auto` mit einer `warming`-Engine für ein PDF tut: nächste Engine der Liste oder warten. `registry.py` und `meta.py` geben die Antwort; nicht raten.
- Nur die falschen Sätze ändern; der Rest des Abschnitts bleibt.

## Prüfung

1. Vorher rot: `grep -n 'bietet sie nicht an' docs/formate.md` findet die Stelle. Nachher findet es nichts.
2. Die neue Aussage stimmt mit `contracts/api.md` überein, und die Notiz nennt die Zeile in `meta.py` oder `registry.py`, die sie belegt.
3. `mkdocs build --strict` im Backend-venv ohne Warnung.
