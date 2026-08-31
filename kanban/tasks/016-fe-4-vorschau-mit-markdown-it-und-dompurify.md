---
id: 16
title: FE-4 · Vorschau mit markdown-it und DOMPurify, Rohtext, Kopieren
status: todo
priority: medium
created: 2026-08-31T10:20:20.872199631+02:00
updated: 2026-08-31T10:30:45.6576732+02:00
assignee: benny
tags:
    - frontend
depends_on:
    - 14
class: standard
---

## Ziel

Das Ergebnis ansehen, bevor es weitergegeben wird - der eigentliche Zweck des
Werkzeugs.

## Eigene Dateien

- `frontend/src/components/MarkdownPreview.vue`

## Vorgaben

- Zwei Reiter: gerendertes Markdown und Rohtext.
- `markdown-it` zum Rendern, **immer** durch `DOMPurify` gefiltert. Das Markdown
  stammt aus fremden Dokumenten; ungefiltert eingefuegtes HTML ist eine
  Einladung zu XSS.
- Kopieren in die Zwischenablage mit sichtbarer Rueckmeldung.
- Lange Ergebnisse bremsen die Seite nicht: gerendert wird erst beim Aufklappen.
- Breite Tabellen und Codebloecke scrollen in ihrem eigenen Bereich, die Seite
  selbst scrollt nicht waagerecht.

## Pruefung

Ein Ergebnis mit Tabelle, Codeblock und einem `<script>`-Versuch im Quelltext:
Tabelle und Code werden dargestellt, das Skript nicht ausgefuehrt. Umschalten
zwischen den Reitern behaelt die Scrollposition nicht bei - das ist in Ordnung.
