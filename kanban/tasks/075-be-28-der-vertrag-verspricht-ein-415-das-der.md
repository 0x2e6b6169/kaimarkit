---
id: 75
title: BE-28 · Der Vertrag verspricht ein 415, das der Stapel nie liefert
status: todo
priority: medium
created: 2026-09-01T13:06:46.35052092+02:00
updated: 2026-09-01T13:06:46.35052092+02:00
assignee: sophie
tags:
    - backend
    - api
class: standard
---

## Befund (01.09.2026, gemeldet von sophie beim Abschluss von BE-26)

`contracts/api.md` schreibt `/api/convert/batch` ein 415 „für den Stapel als Ganzes"
zu. **Der Code kann es nie liefern.** `_convert_entry` fängt jede `ConversionError`
ab; nur `TooManyFiles` steht vor dem `try`. Eine unbekannte Endung im Stapel wird
damit zum Eintragsfehler und nie zur Antwort für den Stapel.

Das ist keine Schreibweise und kein fehlender Eintrag, sondern eine Zusage im Vertrag
ohne Deckung im Verhalten.

## Entscheidung des PO

Zwei Wege standen zur Wahl. **Der Vertrag folgt dem Verhalten, nicht umgekehrt.**

Das heutige Verhalten ist das bessere: Wer fünf Dateien schickt und eine hat eine
unbekannte Endung, bekommt vier Umwandlungen und einen benannten Fehler — nicht
fünfmal nichts. Die Oberfläche ist genau darauf gebaut: Sie führt jede Datei einzeln
mit eigenem Zustand und zählt „1 fehlgeschlagen" neben den fertigen.

Den Stapel als Ganzes abzulehnen wäre eine Verhaltensänderung, die dem Nutzer etwas
wegnimmt. Sie steht nicht zur Debatte.

## Eigene Dateien

- `contracts/api.md`

Kein Dreiklang: Es entfällt eine Zusage über einen Statuscode, kein Feld, kein Name,
kein Typ. `models.py` führt `unsupported_format` weiterhin — für Einträge gilt es
unverändert. Dieselbe Auslegung wie in #72, dort am Gegenstand bestätigt.

## Vorgaben

Das 415 für den Stapel als Ganzes entfällt. Stattdessen sagt der Vertrag, was
zutrifft: Eine unbekannte Endung im Stapel erscheint als Fehler **des Eintrags**, der
Stapel selbst antwortet weiterhin mit 200.

Beim Lesen prüfen, ob der Vertrag dem Stapel weitere Codes zuschreibt, die aus
demselben Grund nie eintreten. Findet sich einer, gehört er in denselben Merge — es
ist dieselbe Aussage.

## Prüfung

- `contracts/api.md` schreibt dem Stapel kein 415 mehr zu.
- Ein Test schickt einen Stapel mit einer unbekannten Endung: Antwort 200, der
  betroffene Eintrag trägt `unsupported_format`, die übrigen sind umgewandelt.
- Gegenprobe: Der Test schlägt fehl, wenn der Stapel als Ganzes scheitert.
- `pytest -q -rs` bleibt grün, Sammelzahl in der Notiz.
