---
id: 53
title: DOC-10 · Docling-Abschnitt nennt seine Warnung nicht
status: todo
priority: low
created: 2026-09-01T09:14:12.802860179+02:00
updated: 2026-09-01T13:26:52.178105047+02:00
started: 2026-09-01T13:26:51.486134658+02:00
assignee: sophie
tags:
    - docs
class: standard
---

## Befund (01.09.2026, gemeldet von sophie aus BE-14)

`docs/formate.md`, Abschnitt "Docling", nennt die Platzhalter-Warnung nicht, die
BE-14 (#47) eingebaut hat. Die Abschnitte zu MarkItDown und Pandoc benennen ihre
`warnings`; der Docling-Abschnitt schweigt.

Der Abschnitt wird durch BE-14 nicht unwahr — deshalb hat sophie ihn richtigerweise
gemeldet statt geaendert. Er ist unvollstaendig, und das ist eine andere Sache.

## Ziel

Wer den Abschnitt liest, weiss, dass Docling Bilder durch Platzhalter ersetzt und
dass die Antwort das mit einer Warnung samt Zahl sagt.

## Eigene Dateien

- `docs/formate.md` (Abschnitt "Docling")

Nach dem Ticketschnitt gehoert der Abschnitt der Lane, die den Gegenstand baut —
Aussagen ueber Doclings Verhalten also dem Backend, nicht der Doku-Lane.

## Vorgaben

Zwei bis drei Saetze, in der Form der beiden Nachbarabschnitte. Die Zahl gehoert
erwaehnt: Die Warnung nennt, wie viele Platzhalter im Ergebnis stehen.

## Pruefung

- Der Abschnitt "Docling" nennt die Warnung.
- `make docs-serve` rendert die Seite fehlerfrei.
- Gegenprobe am Gegenstand statt am Werkzeug: Der genannte Wortlaut stimmt mit dem
  ueberein, den `_placeholder_warnings()` erzeugt.

[[2026-09-01]] Tue 13:26
Der Wortlaut ist seit #58 belegt, nicht mehr nur gebaut: `_placeholder_warnings()` wurde mit 0, 1, 2 und 14 Platzhaltern aufgerufen, Zahl und Mehrzahlform stimmen. Wer diesen Abschnitt schreibt, kann den Wortlaut aus der Notiz von #58 übernehmen, statt ihn aus dem Quelltext abzuleiten.

Seit dem Anlegen dieses Tickets ist eine zweite Warnung dazugekommen: #60 hat für MarkItDown bei PDF eine feste Warnung gebaut ("MarkItDown übernimmt keine Bilder aus PDF"). Sie gehört in den Abschnitt "MarkItDown", nicht hierher — aber wer beim Schreiben merkt, dass der eine Abschnitt seine Warnung nennt und der andere nicht, meldet das, statt beide anzufassen. Der MarkItDown-Abschnitt wurde in #60 bereits berichtigt.
