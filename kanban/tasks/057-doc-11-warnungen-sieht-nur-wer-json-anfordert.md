---
id: 57
title: DOC-11 · Warnungen sieht nur, wer JSON anfordert
status: backlog
priority: low
created: 2026-09-01T10:24:28.290403131+02:00
updated: 2026-09-01T10:24:28.290403131+02:00
assignee: akar
tags:
    - docs
class: standard
---

## Befund (01.09.2026, aus IN-9)

`/api/convert` liefert ohne `Accept: application/json` reines Markdown, kein JSON. So
steht es im Vertrag (`contracts/api.md:138-152`) und so ist es richtig.

`docs/betrieb/lokal.md` zeigt unter "Pruefen, ob der Dienst antwortet" aber nur die
Datei-Variante mit `-o`. Wer so aufruft, sieht die `warnings` nie — also auch nicht
die Warnung aus BE-14 (#47), die sagt, dass ein Teil der Vorlage fehlt. Genau die
Auskunft, wegen der es dieses Projekt gibt, bleibt auf dem dokumentierten Weg
unsichtbar.

## Eigene Dateien

- `docs/betrieb/lokal.md` (Abschnitt "Pruefen, ob der Dienst antwortet")

Nur dieser Abschnitt. Die Abschnitte "Drei Schritte" und "Was vorher da sein muss"
gehoeren BE-17 (#56).

## Vorgaben

Ein bis zwei Saetze und ein Aufruf: `-H "Accept: application/json"` oder die
Kopfzeile `X-Warnings`. Der Grund gehoert dazu, nicht nur der Schalter — sonst liest
es sich wie eine Feinheit.

## Pruefung

- Der gezeigte Aufruf liefert am laufenden Dienst tatsaechlich JSON mit einem Feld
  `warnings`, am Gegenstand geprueft und nicht abgeschrieben.
- `make docs-serve` rendert die Seite fehlerfrei.

## Zurueckgestellt

Vom Nutzer zurueckgestellt, bis die Abnahmefassung steht (01.09.2026).
