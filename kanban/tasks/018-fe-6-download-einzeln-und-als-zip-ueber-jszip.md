---
id: 18
title: FE-6 · Download einzeln und als ZIP ueber jszip
status: todo
priority: medium
created: 2026-08-31T10:20:22.18026728+02:00
updated: 2026-08-31T10:30:45.658916793+02:00
assignee: benny
tags:
    - frontend
depends_on:
    - 15
class: standard
---

## Ziel

Das Ergebnis herausbekommen.

## Eigene Dateien

- `frontend/src/download.ts`

## Vorgaben

- Einzeldownload je Zeile als `.md`.
- "Alles herunterladen" packt im Browser mit `jszip`. Der Grund: Die Ergebnisse
  liegen bereits im Browser; sie fuer das Archiv erneut zum Server zu schicken
  hiesse, jede Datei zweimal zu konvertieren.
- Fehlgeschlagene Dateien landen nicht im Archiv, sondern als Zeile in einer
  `_errors.txt` darin.
- Dateinamen im Archiv wie im Backend gesaeubert, Kollisionen durchnummeriert.

## Pruefung

Fuenf Dateien, davon eine fehlgeschlagen: Das Archiv enthaelt vier `.md`-Dateien
und eine `_errors.txt`, laesst sich mit `unzip` entpacken und die Namen stimmen.
