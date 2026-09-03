---
id: 118
title: DOC-17 · Zwei Stellen, die BE-35 unwahr gemacht hat
status: todo
priority: medium
created: 2026-09-03T14:55:03.218310731+02:00
updated: 2026-09-03T14:55:03.218310731+02:00
assignee: akar
tags:
    - docs
class: standard
---

## Ziel

Zwei Befunde von akar beim Abschluss von DOC-15 (#109), beide durch BE-35 entstanden und
beide bewusst nicht mitgeändert, weil sie fremden Abschnitten gehören.

1. `docs/schnellstart.md:12` sagt, der Dienst hole zur Laufzeit nichts mehr aus dem Netz.
   Seit `POST /api/convert/url` stimmt das so absolut nicht mehr. Der Abschnitt „Was der
   Dienst gar nicht tut" in `docs/grenzen.md` ist schon berichtigt; diese Stelle nicht.
2. In der Tabelle „Vier Werte begrenzen einen Aufruf" fehlt `KAIMARKIT_URL_TIMEOUT`. Mit
   der neuen Variable sind es fünf — und die Überschrift zählt mit.

## Eigene Dateien

- `docs/schnellstart.md` (Zeile 12 und ihr Absatz)
- die Seite mit der Tabelle „Vier Werte begrenzen einen Aufruf" samt Überschrift

Die zweite Datei steht hier bewusst nicht mit Namen: Erst nachsehen, wo die Tabelle
steht — `docs/betrieb/konfiguration.md` ist die Vermutung, nicht der Befund. Steht sie an
zwei Stellen, gehören beide dazu; Konvention 6 zieht `docker/.env.example` mit, falls
dort eine Zahl oder ein Kommentar dieselbe Aussage macht.

Nicht hier: `docs/grenzen.md`, `docs/api.md`, `docs/index.md`, `docs/formate.md` — alle
vier hat DOC-15 zuletzt angefasst und sie stimmen.

## Vorgaben

- Die Aussage in `schnellstart.md` wird genau, nicht gestrichen. Der Dienst holt eine
  Seite, wenn man ihn ausdrücklich darum bittet, und sonst nichts — kein Nachladen von
  Modellen, keine Telemetrie, keine eingebetteten Ressourcen einer geholten Seite.
- Die Überschrift nennt die Zahl, die die Tabelle führt. Wer eine Zeile ergänzt, ändert
  die Zahl mit; sonst entsteht genau der Fehler wieder, der dieses Ticket ist.

## Prüfung

- Rot vor grün, ohne Test: Vor der Arbeit einmal belegen, dass beide Stellen den
  bemängelten Wortlaut führen (Zeilennummer und Zitat in die Notiz), und danach, dass
  sie ihn nicht mehr führen.
- `grep -rn "Vier Werte" docs/` findet nach der Arbeit nichts mehr.
- `mkdocs build --strict` ohne Warnung.
