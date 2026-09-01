---
id: 86
title: DOC-12 · Eine Versionsnummer in der Prosa veraltet von selbst
status: backlog
priority: low
created: 2026-09-01T17:57:09.634238845+02:00
updated: 2026-09-01T17:57:09.634238845+02:00
assignee: akar
tags:
    - docs
class: standard
---

## Befund (01.09.2026, gemeldet von akar beim Abschluss von IN-15)

`docs/betrieb/authelia.md` nennt „Traefik 3.6.7". Das Abbild `traefik:v3.6` liefert
heute 3.6.25. Beide Zahlen stehen jetzt auf derselben Seite, weil IN-15 eine Messung
an 3.6.25 hinzugefügt hat.

Die 3.6.7 stammt aus IN-4 (#25) und war dort richtig. Sie ist niemandes Fehler — sie
ist alt geworden.

## Die Klasse, nicht der Fall

Dasselbe hat PROC-4 (#49) heute Vormittag für Testzahlen entschieden: In der Prosa
steht seither keine Testanzahl mehr, weil eine Zahl, die bei jedem neuen Test unwahr
wird, eine Zusage ist, die niemand halten kann. Eine Patch-Version eines Abbilds mit
gleitendem Tag ist derselbe Fall — sie veraltet ohne Zutun.

## Eigene Dateien

- `docs/betrieb/authelia.md`
- `docs/betrieb/traefik.md`, falls dort dasselbe steht

## Vorgaben

Wo eine Version genannt wird, sagt sie, was sie ist: entweder die Reihe, an die sich
das Abbild hält (`traefik:v3.6`), oder ein datierter Messwert („geprüft mit 3.6.25 am
01.09.2026"). Eine nackte Patch-Nummer im Fließtext gehört weg.

Beim Lesen prüfen, ob weitere Zahlen dieser Art auf den Betriebsseiten stehen —
Versionen, Größen, Dauern. Was sich von selbst ändert und nicht datiert ist, gehört
gemeldet; ob es in diesem Ticket mitgeht, entscheidet die Lane nach Umfang.

## Prüfung

- Keine nackte Patch-Version mehr im Fließtext der genannten Seiten.
- Wo ein Messwert steht, steht das Datum dabei.
- `mkdocs build --strict` läuft durch.
