---
id: 73
title: BE-26 · Die Fehlerantworten stehen in keiner OpenAPI-Fassung
status: done
priority: medium
created: 2026-09-01T12:53:38.556719389+02:00
updated: 2026-09-01T13:05:34.479921805+02:00
started: 2026-09-01T13:04:52.74634175+02:00
completed: 2026-09-01T13:04:52.74634175+02:00
assignee: sophie
tags:
    - backend
    - api
class: standard
---

## Befund (01.09.2026, gemeldet von sophie beim Abschluss von BE-24)

`ErrorResponse` fehlt in `/api/openapi.json` genauso, wie es `ConversionEntry` und
`BatchResponse` bis #71 taten. Die Fehlercodes entstehen in Exception-Handlern; kein
Endpunkt deklariert seine 4xx- und 5xx-Antworten.

Wer unter `/api/docs` nachsieht, welche Fehler ihn erwarten, findet nichts — obwohl
`contracts/api.md` sie beschreibt und das Frontend sie auswertet.

Das ist dieselbe Lücke wie #71, eine Ebene weiter. Sie war schon vorher da und wurde
deshalb gemeldet statt nebenbei geschlossen.

## Warum das die dritte Stelle derselben Art ist

Der Schnittstellen-Dreiklang prüft `contracts/api.md`, `models.py` und `types.ts`
gegeneinander. Keine dieser drei Dateien sagt etwas darüber, was der Dienst
**tatsächlich veröffentlicht**. Genau dort sind jetzt dreimal Typen verschwunden,
ohne dass die Konvention angeschlagen hätte.

Deshalb gehört zu diesem Ticket mehr als das Nachtragen: eine Prüfung, die die Klasse
des Fehlers abdeckt.

## Eigene Dateien

- `backend/app/api/convert.py`
- `backend/app/api/meta.py`
- `backend/tests/` — der neue Test

`models.py` nur, falls `ErrorResponse` dort fehlt. Ändert sich ein Feld oder ein Name,
greift der Dreiklang.

## Vorgaben

Die Endpunkte deklarieren ihre Fehlerantworten über `responses=`, sodass
`ErrorResponse` in `components` erscheint. Welche Codes je Endpunkt zutreffen, steht
in `contracts/api.md` — abgleichen, nicht erfinden.

Dazu **ein Test, der die Lücke als Klasse schließt**: Er liest die in
`contracts/api.md` beschriebenen Antworttypen und prüft, dass jeder in
`/api/openapi.json` unter `components` steht. Reicht das Format des Vertrags dafür
nicht, genügt eine feste Liste der Typnamen im Test — Hauptsache, das Verschwinden
eines Typs lässt einen Test fehlschlagen und nicht bloß eine Doku veralten.

## Prüfung

- `/api/openapi.json` nennt `ErrorResponse` unter `components`.
- Die Endpunkte führen die Fehlercodes, die `contracts/api.md` ihnen zuschreibt.
- Der neue Test schlägt fehl, wenn man `responses=` an einem Endpunkt entfernt.
- `pytest -q` bleibt grün.


---

## Ergebnis (sophie-22, 01.09.2026)

Commit `ea17e08`, gemerged nach `main`.

**Teil 1 — nachgetragen.** Beide Endpunkte in `convert.py` deklarieren ihre
Fehlerantworten über `responses=` mit `model=ErrorResponse`. `/api/convert`: 400
(`engine_unsuitable` | `engine_unavailable`), 413 (`file_too_large`), 415
(`unsupported_format`), 500 (`conversion_failed`), 504 (`conversion_timeout`).
`/api/convert/batch`: nur 413 (`too_many_files`). `ErrorResponse` und `ErrorCode`
stehen damit unter `components`.

`meta.py` blieb unverändert: `contracts/api.md` schreibt `/api/health` und
`/api/capabilities` keinen Fehlercode zu, und beide werfen auch keinen. `models.py`
blieb unverändert — `ErrorResponse` war dort schon vollständig, der
Schnittstellen-Dreiklang wurde also nicht berührt.

**Teil 2 — die Klasse geschlossen.** `test_openapi_publishes_every_declared_type`
leitet die erwarteten Namen aus `app.models` ab — jede öffentliche `BaseModel`- und
`StrEnum`-Klasse, die dort definiert ist — und prüft, dass jede unter `components`
steht. Ein später hinzugefügtes Modell fällt ohne Zutun unter dieselbe Prüfung. Der
ältere `test_openapi_names_both_answer_types` ist darin aufgegangen; seine
`$ref`-Zusicherungen leben als `test_openapi_binds_each_endpoint_to_its_model`
weiter. Dazu kommt `test_openapi_names_the_error_codes_of_each_endpoint` mit der
Zuordnung Endpunkt → Codes.

**Rot vor grün, ausgeführt.** `responses=` nur an `/api/convert` entfernt: 2 failed
(Fehlercodes und zweiter Zweig). Nur an `/api/convert/batch` entfernt: 2 failed. An
beiden entfernt: 3 failed, darunter `nicht in /api/openapi.json veroeffentlicht:
ErrorCode, ErrorResponse`. Wiederhergestellt: 6 passed. `pytest -q` auf `main` nach
dem Merge: 124 passed, 4 deselected. `ruff check .` sauber.

## Befund — nicht behoben

`contracts/api.md` sagt zu `/api/convert/batch`: „Nur 413 (zu viele Dateien) und 415
gelten für den Stapel als Ganzes." Ein 415 kann der Stapel aber nicht liefern:
`_convert_entry` fängt jede `ConversionError` ab und macht daraus einen Eintrag mit
`status: "failed"`, und `TooManyFiles` ist die einzige Ausnahme, die vor dem `try`
steht. Der Endpunkt deklariert deshalb nur 413.

Entweder streicht der Vertrag das 415, oder der Stapel soll ein unbekanntes Format
doch als Ganzes ablehnen. Das ist eine Produktentscheidung, kein Tippfehler.
`contracts/api.md` gehörte während dieses Tickets einem anderen Subagenten und wurde
deshalb nicht angefasst.

## Auskunft zur schwankenden Sammelzahl

Sie hängt am Interpreter, nicht an verlorenen Tests. `tests/test_markitdown.py` hat
ein `pytest.importorskip("markitdown")` auf Modulebene; fehlt die Bibliothek, fällt
das ganze Modul mit seinen 8 Tests aus der Sammlung. In der pyenv-Umgebung
`claude-code`: vorher 120/124 (4 deselected), nachher 122/126. Ohne die Umgebung:
112/116. Die Differenz ist genau 8.
