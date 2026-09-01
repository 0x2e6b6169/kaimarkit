---
id: 73
title: BE-26 · Die Fehlerantworten stehen in keiner OpenAPI-Fassung
status: todo
priority: medium
created: 2026-09-01T12:53:38.556719389+02:00
updated: 2026-09-01T12:53:38.556719389+02:00
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
