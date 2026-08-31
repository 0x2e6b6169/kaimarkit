---
id: 36
title: DOC-7 · Ladezeitpunkt von Docling in der Doku nachziehen
status: done
priority: medium
created: 2026-08-31T11:56:15.436625961+02:00
updated: 2026-08-31T12:01:57.491830539+02:00
started: 2026-08-31T11:56:17.087408335+02:00
completed: 2026-08-31T12:01:13.629722009+02:00
assignee: akar
tags:
    - docs
    - bug
class: standard
---

## Ziel

Die Dokumentation behauptet an mehreren Stellen, Docling lade sein Modell erst
beim ersten Zugriff. Seit BE-11 (#33) stimmt das nicht mehr: `main.py` stoesst
das Vorladen beim Hochfahren an.

`docs/grenzen.md` hat sophie-10 im Zuge von BE-11 schon korrigiert. Ein Grep
ueber `docs/` und `contracts/` zeigt eine zweite Stelle, die dieselbe Aussage
weiterfuehrt:

- `docs/entwicklung.md`

Gemeldet von sophie als Nebenbefund aus BE-11.

## Eigene Dateien

- `docs/entwicklung.md`

Kein offenes Ticket besitzt diese Datei. DOC-6 (#34) besitzt
`docker/.env.example` und `docs/betrieb/konfiguration.md` — kein Ueberschnitt.

## Vorgaben

- Die Aussage zum Ladezeitpunkt auf den Stand nach BE-11 bringen: das Vorladen
  beginnt mit dem Hochfahren des Dienstes, `/api/health` wartet trotzdem nie,
  und waehrend des Aufbaus meldet `state()` weiterhin `warming`.
- Den Grep wiederholen, bevor das Ticket schliesst — die Suche oben lief auf dem
  Stand von `main` zum Zeitpunkt der Erfassung, INT-1 (#29) kann bis dahin
  weitere Seiten angefasst haben.
- Nur diese Aussage anfassen. Was sonst in der Datei steht, gehoert anderen
  Tickets.

## Pruefung

Ein Grep nach dem alten Wortlaut ueber `docs/` und `contracts/` findet keine
Stelle mehr, die das Laden beim ersten Zugriff behauptet. `mkdocs build
--strict` endet mit 0.

Erfasst via /findings (Test-Pass 2026-08-31)


## Ergebnis (akar-12)

Korrigiert wurde Schritt 4 des Abschnitts „Eine vierte Engine ergaenzen" in
`docs/entwicklung.md`. Der Satz „meldet sie so lange `False` und laedt im
Hintergrund" sagte nicht, wann das Laden beginnt, und las sich damit weiter als
Anleitung zum verzoegerten Laden beim ersten Zugriff. Ergaenzt: Der Lifespan in
`main.py` stoesst das Laden beim Hochfahren an, `start_warmup()` kehrt sofort
zurueck (Daemon-Thread), `/api/health` wartet nie, `state()` meldet `warming`,
bis der Konverter steht. Eine neue Engine mit Vorbereitung haengt sich ebenso in
den Lifespan.

**Codeanker** (gelesen auf Commit `187705a`, dem Stand vor dem Merge):

- `backend/app/main.py:41-54` — `lifespan()` ruft `docling.start_warmup()`, ohne
  zu warten.
- `backend/app/converters/docling.py:103-115` — `start_warmup()` startet den
  Daemon-Thread `docling-warmup`; `183-185` der Modul-Einhaenger.
- `backend/app/converters/docling.py:127-133` — `state()` meldet `warming`,
  solange kein Konverter steht.
- `backend/app/api/meta.py:16-23` — `/api/health` antwortet sofort.

**Grep, erneut gelaufen vor dem Commit:**

```
grep -rniE "erst beim ersten|beim ersten (Zugriff|Aufruf|Mal)|lazy|verzoeger|verzöger|nachgeladen|nachlädt|erst bei der ersten|on first use|erst mit der ersten" docs/ contracts/
```

Vier Treffer, drei davon richtig:

- `docs/formate.md:68` — „nichts aus dem Netz nachgeladen wird", Aussage ueber
  `DOCLING_ARTIFACTS_PATH`, kein Ladezeitpunkt.
- `docs/entwicklung.md:134` — verzoegerter *Import* der Bibliothek, stimmt
  weiterhin (`_build_pipeline` importiert docling erst im Funktionsrumpf).
- `docs/entwicklung.md:156` — „Die Registry laedt das Modul erst beim ersten
  Zugriff", stimmt weiterhin (`registry.get_converter()` importiert per
  `importlib` on demand); Modul, nicht Modelle.

**Zweite Fundstelle, nicht angefasst (fremde Datei, DOC-6):**

- `docs/betrieb/konfiguration.md:83` — „Ohne `DOCLING_ARTIFACTS_PATH` sucht
  Docling die Modelle im Home-Verzeichnis des Benutzers, findet nichts und laedt
  sie beim ersten Aufruf nach." Seit BE-11 ist dieser erste Aufruf der
  Warmup-Thread beim Hochfahren, nicht die erste Nutzeranfrage. Der Satz ist im
  Kern richtig (er erklaert die Herkunft der Modelle), im Zeitpunkt aber
  ungenau. Kandidat fuer ein eigenes kleines Ticket in akars Lane.

**Pruefung:** `mkdocs build --strict` endet mit 0, ohne Warnung von MkDocs (die
rote Material-Meldung zu MkDocs 2.0 ist ein Herstellerhinweis, keine
Build-Warnung). `grep -inE "tr(ä|a|u)g"` ueber die Seite: ein Treffer,
„eintragen" in Schritt 5 — kein Verlegenheitsverb.

Branch `task/36-ladezeitpunkt`, Merge `4f3c112`.
