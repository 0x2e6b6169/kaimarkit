---
id: 72
title: BE-25 · Zwei Stellen nennen weiterhin 120 Sekunden
status: in-progress
priority: medium
created: 2026-09-01T12:39:26.15386304+02:00
updated: 2026-09-01T12:53:02.34942713+02:00
assignee: sophie
tags:
    - backend
    - config
claimed_by: sophie-21
claimed_at: 2026-09-01T12:53:02.34942713+02:00
class: standard
---

## Befund (01.09.2026, gemeldet von akar beim Abschluss von IN-11)

IN-11 (#59) hat die Zeitgrenze auf einen gemessenen Wert von 600 s gehoben. Zwei
Stellen nennen weiterhin 120 und liegen außerhalb von akars Lane:

- `backend/app/config.py:27` — `conversion_timeout: int = 120`. Für den Container ohne
  Wirkung, weil Compose den Wert aus `.env` durchreicht. Wer das Backend nackt mit
  `uvicorn` startet — also jeder in der Entwicklung —, bekommt weiterhin 120 s und
  damit ein anderes Verhalten als die Auslieferung.
- `contracts/api.md:98` — `"conversion_timeout_s": 120` im Beispielrumpf von
  `/api/capabilities`. Ein Beispiel, das einen Wert zeigt, den keine Auslieferung mehr
  hat.

## Zum Schnittstellen-Dreiklang

`contracts/api.md` gehört dazu, und Konvention 1 verlangt, alle drei Dateien im selben
Commit zu ändern. Hier greift sie **nicht**: Es ändert sich kein Feld, kein Name und
kein Typ, nur ein Beispielwert. `models.py` und `types.ts` enthalten die Zahl gar
nicht, es gäbe dort nichts zu ändern.

Diese Auslegung ist eine Entscheidung des PO und steht hier, damit sie sichtbar ist.
Wer sie beim Umsetzen für falsch hält, meldet das, statt sie stillschweigend zu
befolgen.

## Eigene Dateien

- `backend/app/config.py`
- `contracts/api.md`
- die zugehörigen Tests

## Vorgaben

Beide Stellen nennen 600, mit demselben Wert wie `docker/.env.example`. Wo die
Voreinstellung im Code steht, gehört der Grund als Kommentar dazu — die Messung steht
in der Notiz von #59.

## Prüfung

- `grep -rn "120" backend/app/config.py contracts/api.md` findet die Zeitgrenze nicht
  mehr.
- Ein nackt gestartetes Backend meldet unter `/api/capabilities` denselben Wert wie
  der Container.
- `pytest -q` bleibt grün.
