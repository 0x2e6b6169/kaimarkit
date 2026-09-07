---
id: 129
title: 'DOC-22 · formate.md: das Schweigen bei docx-Bildern ist behoben'
status: backlog
priority: low
created: 2026-09-07T09:58:30.016278557+02:00
updated: 2026-09-07T09:58:30.016278557+02:00
assignee: akar
tags:
    - docs
    - gh-2
class: standard
---

## Befund (2026-09-07, gemeldet von sophie beim Abschluss von BE-40)

`docs/formate.md` sagt bei MarkItDown: "In `.docx`, `.html` und `.epub` steht von
einem Bild nur der Alt-Text im Markdown, nicht sein Inhalt." Das ist durch BE-40
(#122) nicht unwahr geworden — es fehlt nur der Zusatz, dass der Dienst das inzwischen
in `warnings` meldet, mit Grund und Umweg (docling.py + markitdown.py, Wortlaut in den
Notizen von #121 und #122).

**Pfad berichtigt (2026-09-07, katche):** DOC-24 hat die Seite nach
`docs/admin/formate.md` verschoben.

## Eigene Dateien

- `docs/admin/formate.md` (Abschnitt "MarkItDown")

## Vorgaben

Den Satz um die Meldung ergänzen, Wortlaut wörtlich aus #121/#122 übernehmen oder
sinngemäß, richtige Schreibung mit Umlauten.

## Prüfung

- Der Abschnitt nennt jetzt, dass der Dienst das fehlende Bild in `warnings` meldet.
- `mkdocs build --strict` läuft durch.
