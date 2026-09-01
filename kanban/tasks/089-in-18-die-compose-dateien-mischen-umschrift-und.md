---
id: 89
title: IN-18 · Die Compose-Dateien mischen Umschrift und Umlaute
status: backlog
priority: low
created: 2026-09-01T18:28:03.783151797+02:00
updated: 2026-09-01T18:28:03.783151797+02:00
assignee: akar
tags:
    - infra
    - docs
class: standard
---

## Befund (01.09.2026, gemeldet von akar beim Abschluss von IN-17)

Die vier Dateien unter `docker/` stehen vollständig in ASCII-Umschrift. IN-17 hat dort neue Sätze mit Umlauten ergänzt — die Dateien sind seither **gemischt**, und das ist schlechter als beides einheitlich.

Betroffen: `docker/docker-compose.yml`, `docker/docker-compose.traefik.yml`, `docker/docker-compose.authelia.yml`, `docker/.env.example`.

## Abgrenzung zu BE-21/22/23

Dort ging es um Zeichenketten, die der **Nutzer** liest — Fehlermeldungen, Feldbeschreibungen. Hier geht es um **Kommentare** in Konfigurationsdateien. Der Leser ist ein Betreiber, kein Anwender.

Nach `CLAUDE.md` gilt trotzdem dasselbe: Deutsche Fließtexte folgen `SPRACHE.md`, und ein erklärender Kommentar ist Fließtext. Diese Dateien sind bewusst erklärend geschrieben; ihre Kommentare sind ihr halber Zweck.

## Warum es nicht drängt

Keine Wirkung auf Verhalten, keine auf den Nutzer. Es ist eine Frage der Einheitlichkeit — mit dem Zusatz, dass gemischte Schreibung schlechter ist als konsequente Umschrift.

## Eigene Dateien

- `docker/docker-compose.yml`
- `docker/docker-compose.traefik.yml`
- `docker/docker-compose.authelia.yml`
- `docker/.env.example`

Alle vier zusammen — getrennt geschnitten bliebe die Mischung bestehen.

## Vorgaben

Nur Kommentare und Hinweistexte. **Keine Variablennamen, keine Werte, keine Zeichenkette, die Compose liest.** Ein Umlaut in einem Wert wäre eine Verhaltensänderung.

Von Hand prüfen statt ersetzen zu lassen — dieselbe Auflage wie bei BE-21.

## Prüfung

- `docker compose -f … config` liefert vor und nach der Änderung **byteweise dieselbe Ausgabe**, in allen drei Kombinationen. Das ist der Beleg, dass nur Kommentare betroffen sind.
- `git diff` zeigt ausschließlich Kommentarzeilen.
- Keine der vier Dateien enthält noch gemischte Schreibung.
