---
id: 128
title: FE-26 · OCR-Reichweite im Options-Panel sichtbar
status: todo
priority: medium
created: 2026-09-07T09:55:45.859306412+02:00
updated: 2026-09-07T09:55:45.859306412+02:00
assignee: benny
tags:
    - frontend
    - gh-2
class: standard
---

## Ziel

Der OCR-Schalter im Options-Panel sagt nicht, wo er wirkt. Ein Nutzer schaltet ihn bei
einem docx mit fotografiertem Absatz ein, bekommt trotzdem nichts — und weiss nicht,
ob das ein Fehler ist oder eine Grenze. Die Grenze ist seit DOC-18 (#123) belegt und in
`docs/grenzen.md` beschrieben; sie gehört jetzt auch ins UI, an die Stelle, wo die
Wahl getroffen wird.

## Eigene Dateien

- `frontend/src/components/OptionsPanel.vue` und der Test dazu

## Vorgaben

- Direkt beim OCR-Feld ein kurzer Satz, sichtbar ohne Interaktion, z. B. "Wirkt nur bei
  PDF und Bilddateien." Genauer Wortlaut nach Ermessen der Lane, in richtiger Schreibung.
- Daneben ein i-Icon mit ausfuehrlicherer Erlaeuterung bei Hover **und** bei
  Tastaturfokus (nicht nur `:hover` — sonst unerreichbar ohne Maus). Der Screenreader
  bekommt denselben Text, nicht nur das Icon.
- Inhaltlich identisch mit der belegten Aussage aus `docs/grenzen.md`
  ("OCR greift nur in PDF und Bilddateien"): Texterkennung liest Bildtext nur in PDF
  und den Formaten .png/.jpg/.jpeg/.tiff; bei .docx/.pptx/.xlsx/.html/.epub bleibt sie
  aus, unabhaengig vom Schalter. Umweg: das Dokument als PDF speichern und mit OCR
  erneut hochladen.
- Der Hinweis gilt statisch, unabhaengig von der aktuellen Dateiauswahl in der
  Warteschlange — keine dynamische Herleitung je Datei noetig.
- Erscheint nur, wenn der OCR-Schalter selbst erscheint (`ocrAvailable`), sonst nichts
  zu erklaeren.

## Prüfung

- Rot vor grün: ein Test prüft, dass der Kurzhinweis und das i-Icon mit dem
  Tooltiptext im Options-Panel vorhanden sind — schlägt vor der Arbeit fehl.
- Der ausführliche Text ist per Tastaturfokus erreichbar, nicht nur per Hover; ein Test
  belegt das (z. B. Tab auf das Icon, Text sichtbar/erreichbar für AT).
- `npm run test`, `npm run typecheck` sauber.
