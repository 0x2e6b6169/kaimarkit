---
id: 84
title: BE-32 · Die erste Umwandlung dauert doppelt so lang wie die zweite
status: todo
priority: medium
created: 2026-09-01T17:28:22.990006761+02:00
updated: 2026-09-01T17:28:22.990006761+02:00
assignee: sophie
tags:
    - backend
    - performance
class: standard
---

## Befund (01.09.2026, gemessen von akar in IN-13)

Am frischen Container, Abbildstand `6b4c3b4`, **beide Läufe nach abgeschlossenem
Vorladen**:

    erste Umwandlung    28,2 s
    zweite Umwandlung   12,0 s

Rund 16 Sekunden, die das Vorladen nicht abdeckt. `_warmup` baut seit BE-17 (#56)
beide OCR-Pipelines; der Unterschied liegt also woanders.

## Warum das zählt

Es trifft **jede erste Umwandlung nach jedem Start** — also genau den Moment, in dem
jemand das Werkzeug zum ersten Mal ausprobiert. Der Nutzer hat heute Vormittag nach
103 Sekunden gefragt, wie lange das dauern soll; ein Sechzehntel davon wäre erklärbar
gewesen, wenn wir es gewusst hätten.

Es ist außerdem der Rest einer Frage, die schon zweimal beantwortet schien: BE-17 hat
gezeigt, dass das Laden 8,5 s je Pipeline kostet und `ready` zu früh kam. Beides ist
erledigt — und die erste Umwandlung ist trotzdem doppelt so teuer.

## Eigene Dateien

- `backend/app/converters/docling.py`
- `backend/tests/test_docling.py`

## Vorgaben

**Zuerst messen, wo die Zeit hingeht — nicht raten und nicht vorladen.** Denkbar sind
Modelle, die Docling erst beim ersten echten Dokument lädt (Tabellenmodell, OCR-Netz),
Torch-Kernel, die beim ersten Aufruf übersetzt werden, oder ein Zwischenspeicher, den
erst der erste Lauf füllt. Welches davon, sagt eine Messung und keine Überlegung.

Die Aufschlüsselung gehört in die Ticketnotiz, auch wenn danach nichts gebaut wird.

**Erst wenn feststeht, wo die Zeit liegt, ist zu entscheiden, ob sich Vorladen lohnt.**
Es kann sein, dass die Antwort „nichts tun" lautet — 16 Sekunden einmal je Start sind
kein Notstand, und ein Vorladen, das den Start um 16 Sekunden verlängert, verschiebt
die Kosten nur. Das wäre ein gutes Ergebnis und kein gescheitertes Ticket.

## Prüfung

- Die Notiz nennt, wohin die 16 Sekunden gehen, mit Messwerten statt Vermutungen.
- Wird etwas geändert, sind erste und zweite Umwandlung danach erneut gemessen und
  beide Zahlen stehen in der Notiz.
- Wird nichts geändert, steht der Grund in der Notiz und das Ticket schließt trotzdem.
- `pytest -q -rs` bleibt grün, Sammelzahl in der Notiz.
