---
id: 30
title: INT-2 · Ende-zu-Ende-Pruefung im Container
status: todo
priority: medium
created: 2026-08-31T10:21:44.348462086+02:00
updated: 2026-08-31T11:28:58.790508419+02:00
assignee: akar
tags:
    - infra
depends_on:
    - 29
    - 26
    - 27
class: standard
---

## Ziel

Belegen, dass das gebaute Image tut, was der Plan verspricht.

## Eigene Dateien

Keine - dieses Ticket prueft und meldet, es baut nicht.

## Vorgaben

Der Abschnitt "Pruefung am Ende" des Plans, vollstaendig durchlaufen:

- pytest mit und ohne `-m slow`
- die curl-Beispiele fuer Einzeldatei, Stapel-ZIP und die Fehlerpfade 413/415/400
- `make up`, dann `/api/health`, `/docs/`, `/docs/versions.json`, `/api/docs`
- `docker compose ... config` ueber alle drei Dateien: kein `${...}`, kein leerer
  Wert
- ein Build mit absolut gesetztem `KAIMARKIT_BUILD_CONTEXT`

Von Hand: ein gescanntes PDF mit und ohne OCR, ein PDF mit breiter Tabelle ueber
MarkItDown und Docling im Vergleich, ein ePub ueber Pandoc, ein Durchlauf im
Browser mit gemischten Dateien.

Nach einem zweiten `make docs-release`: zwischen den Versionen umschalten und
pruefen, dass die Links auf `/docs/<version>/` zeigen und nicht auf die Wurzel.

## Pruefung

Jeder Punkt oben abgehakt. Was nicht gelingt, wird als eigenes Ticket angelegt,
nicht stillschweigend uebergangen.


## Nachtrag aus DOC-2 (#21) und IN-4 (#25)

- `docs/schnellstart.md` enthaelt einen `!!! info`-Kasten, der sagt, dass die
  Oberfläche noch das Geruest ist. Sobald INT-1 (#29) `App.vue` verdrahtet hat,
  gehoert der Kasten weg.
- Die Anmeldung im Browser gegen ein echtes Authelia ist nie gelaufen. IN-4 hatte
  weder Image noch Netz dafuer und hat den Nachweis hierher uebergeben.
