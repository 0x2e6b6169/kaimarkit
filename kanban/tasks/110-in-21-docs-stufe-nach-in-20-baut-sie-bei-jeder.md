---
id: 110
title: 'IN-21 · Docs-Stufe nach IN-20: baut sie bei jeder Kontextänderung neu?'
status: backlog
priority: low
created: 2026-09-03T11:21:10.83878559+02:00
updated: 2026-09-03T11:21:10.83878559+02:00
assignee: akar
tags:
    - infra
class: standard
---

## Ziel

akars Vermutung aus IN-20 (#103), ausdrücklich als Vermutung gemeldet: Seit die Docs-Stufe den ganzen Kontext bindet (`--mount=type=bind,source=.,target=/ctx`) statt nur `.git`, könnte BuildKit den `RUN` bei jeder Änderung im Kontext neu ausführen, auch wenn sich nur eine Frontend-Datei geändert hat. Ob das so ist, weiß niemand; das Ticket misst es.

## Eigene Dateien

- `docker/Dockerfile` (Docs-Stufe), nur falls die Messung eine Änderung verlangt
- `docs/entwicklung.md` (Abschnitt zum Bau), nur falls die Aussage dort dadurch falsch wird

## Vorgaben

- Zweimal bauen: einmal vollständig, dann nach einer Änderung an einer Datei außerhalb von `docs/` und `.git` (etwa `frontend/src/App.vue`, eine Leerzeile). Für beide Läufe die BuildKit-Ausgabe der Docs-Stufe festhalten: `CACHED` oder nicht, Dauer.
- Die Maschine ist während der Messung frei; kein anderer Bau läuft.
- Fällt die Stufe aus dem Cache, ist die Frage, ob das etwas kostet: Die Docs-Stufe brauchte in IN-20 unter zwei Sekunden. Eine Änderung lohnt nur, wenn die Messung mehr zeigt.

## Prüfung

1. Die Notiz nennt beide Läufe mit `CACHED`/nicht und Dauer.
2. Ändert das Ticket das Dockerfile: `make build` zweimal, die zweite Docs-Stufe ist `CACHED`, und der Bau ohne `.git` (Prüfung aus IN-20) läuft weiterhin durch.
