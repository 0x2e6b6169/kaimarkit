---
id: 74
title: BE-27 · Zwei Stellen beschreiben das Vorladen falsch
status: done
priority: medium
created: 2026-09-01T12:57:48.662367545+02:00
updated: 2026-09-01T13:03:37.400854411+02:00
started: 2026-09-01T13:03:31.683196818+02:00
completed: 2026-09-01T13:03:31.683196818+02:00
assignee: sophie
tags:
    - backend
    - docs
class: standard
---

## Befund (01.09.2026, gemeldet von sophie beim Abschluss von BE-17)

Zwei Stellen sagen etwas über das Vorladen, das nicht zutrifft. Beide waren schon vor
#56 falsch und wurden deshalb gemeldet statt nebenbei geändert.

- **`backend/app/main.py:47`** — behauptet „minutenlang". Gemessen sind 8,5 Sekunden
  je Pipeline (akar in #59). Dieselbe Unwahrheit hat #56 im Adapter beseitigt; hier
  steht sie eine Datei weiter.
- **`docs/betrieb/konfiguration.md:144`** — sagt, der Healthcheck warte auf die
  Modelle. Er wartet sie nicht ab: `ready` kommt, bevor die zweite Pipeline steht.
  Das galt vor #56 genauso, nur für die einzige Pipeline.

## Warum zusammen

Es ist eine Aussage an zwei Orten — wie lange das Vorladen dauert und was `healthy`
darüber sagt. Getrennt geschnitten liefe man Gefahr, die eine zu berichtigen und die
andere stehen zu lassen; dann widersprechen sich Code und Dokumentation.

`main.py` gehört nach dem Ticketschnitt allein BE-1 (#4). Das Ticket ist geschlossen,
die Datei damit frei — dieses Ticket besitzt sie, solange es offen ist.

## Eigene Dateien

- `backend/app/main.py`
- `docs/betrieb/konfiguration.md`

## Vorgaben

Beide Stellen nennen, was zutrifft: Das Vorladen dauert Sekunden, nicht Minuten, und
zwar zweimal — je Pipeline. Und `healthy` sagt aus, dass der Dienst antwortet, nicht
dass das Vorladen abgeschlossen ist.

Die Zahlen aus #59 und #56 stehen in deren Notizen. Nicht neu messen, wenn sie
zutreffen — aber ansehen, ob sie es tun.

Kein Verhalten ändern. Wer beim Lesen findet, dass `healthy` etwas anderes aussagen
*sollte*, meldet das und schneidet es nicht hier hinein.

## Prüfung

- Keine der beiden Stellen behauptet „minutenlang" oder ein Warten auf die Modelle.
- Die genannte Größenordnung deckt sich mit den Notizen von #56 und #59.
- `pytest -q` bleibt grün, `make docs-serve` rendert die Seite fehlerfrei.

[[2026-09-01]] Tue 13:03
Umgesetzt (sophie-23, 01.09.2026). Branch task/74-vorladen-beschreiben, Commit c345b0f, nach main gemergt.

## Was geaendert wurde

**backend/app/main.py** — Lifespan-Docstring. Statt „der erste Nutzer wartete minutenlang" steht dort jetzt die gemessene Zahl aus #59: rund achteinhalb Sekunden je Pipeline, und der Warmlauf baut zwei davon, eine mit Texterkennung und eine ohne. Der Modulkopf oben („Er wartet nicht darauf: Der Dienst ist sofort bedienbar") war schon richtig und blieb.

**docs/betrieb/konfiguration.md** (Abschnitt „Container") — der Satz „Docling laedt in dieser Zeit seine Modelle" legte nahe, die Anlaufzeit des Healthchecks decke das Vorladen ab. Jetzt steht dort, was zutrifft: Der Healthcheck ruft `GET /api/health`, und diese Antwort haengt nicht an Docling; `healthy` sagt, dass der Dienst antwortet, nicht dass das Vorladen fertig ist. Danach die Zahl und die zweite Pipeline, und dass `/api/capabilities` `warming` meldet, solange die erste nicht steht.

Die Formulierung ist mit `docs/betrieb/lokal.md` (aus #56) und dem Modulkopf von `converters/docling.py` abgeglichen — dieselbe Zahl, dieselbe Beschreibung.

## Zahlen geprueft, nicht blind uebernommen

Aus der Notiz von #59: 9,24 s und 8,30 s als Differenz zwischen erstem und zweitem Lauf, 8,50 s direkt an `_build_pipeline(True)` gemessen. „Rund achteinhalb Sekunden" deckt sich damit. Dass es zwei Pipelines sind, steht im Quelltext: `docling._warmup` laeuft ueber `(default_ocr, not default_ocr)`.

Dass der Healthcheck nicht wartet, ist ebenfalls am Quelltext geprueft: `docker/docker-compose.yml:50-58` ruft `/api/health`, und `api/meta.py:health` antwortet ohne jeden Bezug auf die Konverter.

## Kein Verhalten geaendert

Nur Docstring und Prosa. Keine Zusage verschoben, kein Test angepasst.

## Pruefung

- Weder „minutenlang" noch ein Warten auf die Modelle steht noch in einer der beiden Dateien.
- `pytest -q`: 120 passed, 4 deselected. `ruff check .`: sauber.
- `mkdocs build --strict` laeuft durch; die gerenderte Seite `betrieb/konfiguration/` zeigt den neuen Abschnitt fehlerfrei.

## Auskunft zur Sammelzahl (angefragt)

`pytest --collect-only -q` meldet **120/124 tests collected (4 deselected)**. Die vier Abgewaehlten sind die `slow`-Tests — 124 Tests im Baum, 120 im Standardlauf. Der Sprung von 116 auf 120 erklaert sich aus neu hinzugekommenen Tests, nicht aus herausgefallenen: Die Notiz von #56 nennt 116 passed + 4 deselected fuer den damaligen Stand. Kein Test ist aus dem Lauf gefallen.
