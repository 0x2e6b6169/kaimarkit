---
id: 74
title: BE-27 · Zwei Stellen beschreiben das Vorladen falsch
status: todo
priority: medium
created: 2026-09-01T12:57:48.662367545+02:00
updated: 2026-09-01T12:57:48.662367545+02:00
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
