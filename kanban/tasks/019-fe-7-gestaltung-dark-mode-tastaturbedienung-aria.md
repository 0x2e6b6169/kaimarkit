---
id: 19
title: FE-7 · Gestaltung, Dark Mode, Tastaturbedienung, aria-live
status: todo
priority: medium
created: 2026-08-31T10:20:22.896316174+02:00
updated: 2026-08-31T10:30:45.659748394+02:00
assignee: benny
tags:
    - frontend
depends_on:
    - 15
    - 16
    - 17
class: standard
---

## Ziel

Aus den Bausteinen eine Seite machen, die sich gut bedienen laesst.

## Eigene Dateien

- `frontend/src/App.vue`
- `frontend/src/style.css`

## Vorgaben

- Ruhiges, flaechiges Layout, ein Akzentton. Kein Farbfeuerwerk - das Werkzeug
  zeigt Text, und der soll lesbar sein.
- Dark Mode ueber `prefers-color-scheme`, keine eigene Umschaltung.
- Sichtbarer Fokusrahmen auf allen bedienbaren Elementen.
- Die Seite funktioniert ab 360 px Breite; breite Inhalte scrollen in ihrem eigenen
  Bereich.
- Leerer Zustand erklaert in einem Satz, was das Werkzeug tut und welche Formate
  es nimmt.

## Pruefung

Bedienung allein per Tastatur von der Dropzone bis zum Download. Im hellen und im
dunklen Modus ist jeder Text lesbar. Bei 360 px Breite scrollt die Seite nicht
waagerecht.
