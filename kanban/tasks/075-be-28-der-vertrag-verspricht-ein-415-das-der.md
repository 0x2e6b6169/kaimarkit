---
id: 75
title: BE-28 · Der Vertrag verspricht ein 415, das der Stapel nie liefert
status: done
priority: medium
created: 2026-09-01T13:06:46.35052092+02:00
updated: 2026-09-01T13:13:08.106668755+02:00
started: 2026-09-01T13:12:40.5500631+02:00
completed: 2026-09-01T13:12:40.5500631+02:00
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

## Ergebnis (sophie-24)

Erledigt auf task/75-vertrag-folgt-verhalten, Commit 74e4a61, --no-ff nach main.

Der Vertrag folgt dem Verhalten: Die Schlusszeile von `POST /api/convert/batch`
verspricht dem Stapel kein 415 mehr. Sie nennt jetzt, was zutrifft — was
`/api/convert` mit 415 abweist, wird im Stapel zu `status: "failed"` mit dem Grund
in `error`; für den Stapel als Ganzes bleibt allein 413 (zu viele Dateien). Kein
Verhalten geändert, kein Dreiklang berührt.

**Auflage geprüft — weitere nie eintretende Codes gibt es nicht.** `_convert_entry`
fängt jede `ConversionError` ab; einzig `TooManyFiles` wird vor dem `try` geworfen.
Damit ist 413 (`too_many_files`) der einzige Code, den der Stapel selbst liefern
kann — genau der steht noch im Vertrag, und `BATCH_RESPONSES` in
`backend/app/api/convert.py` wie auch `tests/test_openapi.py:45` sagen dasselbe.
`docs/api.md` führt seine 415-Zeile unter `/api/convert`, nicht unter dem Stapel —
dort war nichts zu berichtigen.

Test: `backend/tests/test_api.py::test_unknown_extension_in_a_batch_stays_the_error_of_its_entry`.
Der Rumpf nannte die Datei nicht; kein offenes Ticket besitzt sie. Stapel aus
a.docx, archiv.zip, b.docx → 200, Eintrag 2 `failed` mit `Für .zip gibt es keine
Engine.`, Einträge 1 und 3 gewandelt, succeeded 2 / failed 1.

Gegenprobe ausgeführt: `_convert_entry` vorübergehend so geändert, dass ein 415
durchschlägt. Ausgabe: `assert 415 == 200` / `where 415 = <Response [415 Unsupported
Media Type]>.status_code`, 1 failed. Danach mit `git checkout` zurückgenommen; der
Commit enthält keine Codeänderung.

Sammelzahl vorher 124/128 collected (4 deselected), nachher 125/129 (4 deselected).
`pytest -q -rs`: 125 passed, 4 deselected. `ruff check .` sauber.


[[2026-09-01]] Tue 13:3x
**Ablageort des Tests, wie vom PO erbeten:** `backend/tests/test_api.py`, Test
`test_unknown_extension_in_a_batch_stays_the_error_of_its_entry`.

Hintergrund: Der Rumpf fuehrte unter "Eigene Dateien" nur `contracts/api.md`,
verlangte in der Pruefung aber einen Test — die Dateiliste sah keinen Ort dafuer vor.
Die sophie-Sitzung hat `backend/tests/test_api.py` dazugegeben; kein offenes Ticket
besass sie.
