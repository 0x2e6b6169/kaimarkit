---
id: 125
title: DOC-20 · Docling-Versionsangabe ohne Datum
status: backlog
priority: low
created: 2026-09-07T09:44:36.871397532+02:00
updated: 2026-09-07T09:44:46.372806895+02:00
assignee: akar
tags:
    - docs
class: standard
---

## Befund (2026-09-07, gemeldet von akar-42 beim Abschluss von DOC-12)

`docs/formate.md:85` und `docs/grenzen.md:80` nennen denselben Wortlaut
"gemessen im Container-Abbild mit docling 2.124.0" — eine Patch-Version ohne Datum.
Docling ist im Abbild gepinnt, die Zahl veraltet also erst, wenn jemand den Pin hebt.
Das Datum fehlt trotzdem; dieselbe Klasse wie DOC-12 (#86).

**Pfad berichtigt (2026-09-07, katche):** DOC-24 hat die Doku umgezogen. Die
Fundstellen liegen jetzt unter `docs/admin/formate.md` und `docs/admin/grenzen.md`;
die Zeilennummern gelten nicht mehr, erst neu greppen.

## Eigene Dateien

- `docs/admin/formate.md` (Abschnitt "Docling")
- `docs/admin/grenzen.md` (dieselbe Stelle)

## Vorgaben

Wie in DOC-12 gelöst: ein datierter Messwert statt einer nackten Patch-Nummer.

## Prüfung

- Keine nackte Patch-Version mehr im Fließtext der genannten Stellen, geprüft über den
  geflachten Text (nicht zeilenweise).
- `mkdocs build --strict` läuft durch.
