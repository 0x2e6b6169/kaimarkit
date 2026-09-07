---
id: 86
title: DOC-12 · Eine Versionsnummer in der Prosa veraltet von selbst
status: done
priority: low
created: 2026-09-01T17:57:09.634238845+02:00
updated: 2026-09-07T09:44:19.504300707+02:00
started: 2026-09-07T09:33:05.441030625+02:00
completed: 2026-09-07T09:43:15.148209171+02:00
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

[[2026-09-07]] Mon 09:43
## Umgesetzt (akar-42, 07.09.2026)

Jede genannte Version ist jetzt ein datierter Messwert. Die Daten stammen aus
`git blame` der jeweiligen Zeile, also aus dem Tag, an dem der Satz geschrieben wurde.

`docs/betrieb/authelia.md` — funf Stellen:

- ungenutzte Middleware-Definition: „Am 01.09.2026 fuhrte Traefik 3.6.25 …"
- falscher Anbieterzusatz: „Am 01.09.2026 mit Traefik 3.6.25 … gemessen"
- leeres `middlewares=`: „Am 31.08.2026 mit Traefik 3.6.7 geprueft" — die 3.6.7 aus
  IN-4 bleibt also stehen, aber nicht mehr nackt. Dieselbe Aussage steht in der
  Tabelle darunter noch einmal, gemessen an 3.6.25 am 01.09.2026; beide Zahlen sind
  jetzt als zwei Messungen zu zwei Zeitpunkten lesbar.
- Tabelle der Middlewarewahl: „ist am 01.09.2026 gegen Traefik 3.6.25 durchgemessen"
- vollstaendiger Durchlauf: „am 31.08.2026 gegen Authelia 4.38.19 hinter Traefik 3.6"

`docs/betrieb/traefik.md` — dieselbe Klasse stand dort zweimal:

- Compose-Merge-Verhalten: „Am 01.09.2026 mit Compose v5.1.4 nachgemessen"
- doppelter Routername: „Am 01.09.2026 mit Traefik 3.6.25 nachgemessen"

Nicht angefasst: `Compose 2.24 oder neuer` in traefik.md. Das ist eine Untergrenze,
die der `!reset`-Tag verlangt, kein Messwert — sie veraltet nicht von selbst.

## Pruefung

Ein Skript ueber den geflachten Text (Codebloecke entfernt, danach `' '.join(split())`,
dann satzweise): jeder Satz mit einer Version `X.Y.Z` ohne Datum `TT.MM.JJJJ` im selben
Satz ist eine Fundstelle.

- vorher: authelia.md 5, traefik.md 2
- nachher: authelia.md 0, traefik.md 0

`mkdocs build --strict` laeuft durch (der rote Material-Hinweis auf MkDocs 2.0 ist der
Herstellerhinweis, keine Warnung des Baus).

Zweig `task/86-doc-12`, Merge `47d11ac`.

## Befunde ausserhalb der eigenen Dateien — als Ticket vorgeschlagen

Dieselbe Klasse steht noch an vier Stellen, alle ausserhalb der beiden eigenen Dateien
und deshalb hier nur gemeldet:

- `docs/formate.md` Zeile 85 und `docs/grenzen.md` Zeile 80: „gemessen im
  Container-Abbild mit docling 2.124.0" — nackte Patch-Version, kein Datum, zweimal
  derselbe Wortlaut. Docling steht im Abbild aber gepinnt, anders als `traefik:v3.6`;
  die Zahl veraltet also erst, wenn jemand den Pin hebt. Trotzdem fehlt das Datum.
- `docs/betrieb/lokal.md` Zeile 8: „etwa 6 GB freier Arbeitsspeicher" und
  `docs/betrieb/konfiguration.md` Zeile 99: „rund 2 GB" je Worker — gemessene Groessen
  ohne Datum. Sie wachsen mit dem Abbild, ohne dass jemand die Seite anfasst.

Kein Befund: `PANDOC_VERSION` `3.6.4` in konfiguration.md Zeile 31. Das ist der
dokumentierte Vorgabewert einer Variablen, kein Satz in der Prosa — er veraltet nicht
von selbst, sondern nur mit dem Dockerfile, und dann faellt es dort auf.
