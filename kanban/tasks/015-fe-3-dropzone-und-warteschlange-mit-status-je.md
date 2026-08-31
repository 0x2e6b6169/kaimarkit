---
id: 15
title: FE-3 · Dropzone und Warteschlange mit Status je Datei
status: todo
priority: medium
created: 2026-08-31T10:20:20.286425335+02:00
updated: 2026-08-31T10:30:45.657099157+02:00
assignee: benny
tags:
    - frontend
depends_on:
    - 14
class: standard
---

## Ziel

Dateien hinzufuegen und ihren Fortschritt sehen.

## Eigene Dateien

- `frontend/src/components/FileDropZone.vue`
- `frontend/src/components/FileQueue.vue`
- `frontend/src/components/FileRow.vue`

## Vorgaben

- Drag & Drop und Dateiauswahl. Die Dropzone ist per Tastatur erreichbar
  (fokussierbar, Leertaste oeffnet den Dialog).
- Jede Datei erscheint sofort als Zeile mit Status, bevor die Konvertierung
  beginnt.
- Statusaenderungen laufen ueber `aria-live`, damit sie ohne Blick auf den
  Bildschirm wahrnehmbar sind.
- Status wird nicht allein durch Farbe unterschieden, sondern zusaetzlich durch
  Symbol und Text.
- Warnungen stehen sichtbar an der Zeile - genau dort entscheidet sich, ob das
  Ergebnis taugt.
- Eine Zeile laesst sich aufklappen; der Inhalt kommt aus `MarkdownPreview` (FE-4),
  bis dahin genuegt ein Platzhalter.

## Pruefung

Im Browser mit Mock: fuenf Dateien ablegen, Reihenfolge und Status stimmen, eine
fehlgeschlagene Datei zeigt ihre Meldung, Bedienung allein per Tastatur moeglich.
