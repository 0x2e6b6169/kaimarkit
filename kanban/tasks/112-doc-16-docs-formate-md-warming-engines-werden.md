---
id: 112
title: 'DOC-16 · docs/formate.md: warming-Engines werden angeboten, nicht verschwiegen'
status: done
priority: medium
created: 2026-09-03T11:42:53.956405461+02:00
updated: 2026-09-03T14:17:37.912907208+02:00
started: 2026-09-03T14:17:31.51382224+02:00
completed: 2026-09-03T14:17:31.51382224+02:00
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

[[2026-09-03]] Thu 14:17
akar-36: Neue Aussage in docs/formate.md: Im Zustand warming nennt GET /api/capabilities Docling unter engines mit diesem Zustand, in formats steht es noch nicht; engine=auto nimmt für ein PDF die nächste Engine der Präferenzliste, eine ausdrückliche Anfrage wartet. Belege: api/meta.py:43 und :77 (engines aus _state, warming enthalten), converters/registry.py:161 (engines_for filtert über available(), warming fällt aus formats) und :199 (auto nimmt candidates aus engines_for, also markitdown), converters/docling.py:226-229 (ausdrückliche Anfrage wartet an _build_lock). Abweichung vom Ticketrumpf: „Nur unavailable fällt aus formats heraus“ stimmt nicht — warming fällt dort ebenso heraus; contracts/api.md sagt nur, dass unavailable fehlt, und widerspricht dem Code nicht. mkdocs build --strict: ohne Warnung, rc=0. Merge-Commit 5d46219.
