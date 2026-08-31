---
id: 34
title: DOC-6 · OCR-Sprachen und DOCLING_ARTIFACTS_PATH in .env.example und Konfigurationsseite
status: in-progress
priority: medium
created: 2026-08-31T11:45:54.471902201+02:00
updated: 2026-08-31T11:47:43.391917327+02:00
started: 2026-08-31T11:46:25.433276163+02:00
assignee: akar
tags:
    - docs
    - bug
claimed_by: akar-11
claimed_at: 2026-08-31T11:47:43.391917327+02:00
class: standard
---

## Ziel

Zwei Luecken in der Betriebsdokumentation von Docling, beide gemeldet von sophie.

1. `docker/.env.example` setzt `KAIMARKIT_OCR_LANGS=deu,eng`. Das ist die
   Schreibweise von Tesseract. Doclings Voreinstellung ist EasyOCR, und die
   erwartet `de,en`. Wer die Beispieldatei uebernimmt und OCR einschaltet,
   bekommt keine Fehlermeldung, sondern schlechtere Erkennung.
2. `DOCLING_ARTIFACTS_PATH` fehlt in `docs/betrieb/konfiguration.md`. Die
   Variable steht im Dockerfile (IN-1, #23) und der Adapter liest sie (BE-4,
   #7) — beschrieben ist sie nirgends. Ohne sie laedt Docling zur Laufzeit
   Modelle nach, was mit `HF_HUB_OFFLINE=1` fehlschlaegt.

## Eigene Dateien

- `docker/.env.example`
- `docs/betrieb/konfiguration.md`

Beide gehoeren zusammen — Konvention 6 sagt, dass sie gemeinsam geaendert
werden. Genau deshalb ist das ein Ticket und nicht zwei.

## Vorgaben

- Klaeren, welche OCR-Maschine der Docling-Adapter tatsaechlich benutzt, und die
  Beispielwerte danach richten. Wenn beide Schreibweisen vorkommen koennen,
  gehoert das in die Dokumentation, nicht in einen stillen Standardwert.
- `DOCLING_ARTIFACTS_PATH` in `docs/betrieb/konfiguration.md` aufnehmen: was sie
  bedeutet, welchen Wert das Image setzt, und was ohne sie passiert.
- Beim Durchsehen pruefen, ob weitere `KAIMARKIT_*`- oder Docling-Variablen in
  einer der beiden Dateien fehlen. Dieselbe Luecke steht selten allein.

## Pruefung

Jede Variable aus `docker/.env.example` kommt in `docs/betrieb/konfiguration.md`
vor und umgekehrt — einmal gegeneinander abgeglichen, das Ergebnis in der
Ticketnotiz. Die OCR-Sprachen im Beispiel passen zu der Maschine, die der
Adapter aufruft, mit Nachweis aus dem Code.

Erfasst via /findings (Test-Pass 2026-08-31)
