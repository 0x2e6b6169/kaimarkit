---
id: 111
title: ORG-5 · Fünf Stellen behaupten noch den Rückfall 0.1.0, dazu package-lock
status: todo
priority: critical
created: 2026-09-03T11:27:53.391937908+02:00
updated: 2026-09-03T11:27:53.391937908+02:00
assignee: akar
tags:
    - docs
    - frontend
class: standard
---

## Ziel

ORG-4 (#102) hat `__init__.py` und `package.json` auf `0.2.0` gehoben und dabei sechs Stellen gemeldet, die weiter `0.1.0` behaupten. Der Tag `v0.2.0` wartet auf dieses Ticket: Er soll auf einen Stand zeigen, dessen Doku zu ihm passt. Zehn Minuten, dann setzt katche den Tag.

## Eigene Dateien

Von katche am 2026-09-03 mit `grep -rn '0\.1\.0'` bestätigt:

- `contracts/api.md:75` — „… also `0.1.0`." (der Satz über den Rückfall ohne `.git`)
- `docs/api.md:42` — derselbe Satz
- `docs/schnellstart.md:38` — „Ein Bau ohne Git-Verlauf meldet `0.1.0`."
- `frontend/src/api.ts:95` — Kommentar „Heute ist es `0.1.0`"
- `frontend/src/App.vue:47` — Kommentar mit derselben Zahl
- `frontend/package-lock.json:3` und `:9` — `"version": "0.1.0"`

Nicht anfassen: `backend/app/config.py:51`. Dort steht `v0.1.0` als Beispiel für die Form von `git describe`, keine Versionsbehauptung; die Datei gehört BE-35 (#107).

## Vorgaben

- In den drei Prosa-Stellen die feste Zahl durch den Verweis ersetzen, woher sie kommt: der Rückfall ist der Wert aus `app/__init__.py`, ohne `v`. Keine neue feste Zahl hineinschreiben, sonst steht hier beim nächsten Release wieder eine falsche. Die Beispielantworten `v0.1.0-12-ga22a6c5` bleiben; sie zeigen eine Form, nicht den Stand.
- In den zwei Kommentaren ebenso: die Form nennen, nicht die Zahl.
- `package-lock.json` nicht von Hand ändern: `cd frontend && npm install --package-lock-only` schreibt die Zahl aus `package.json` hinein. Das Diff darf nur die zwei Versionszeilen zeigen; ändert sich mehr, abbrechen und melden.
- `contracts/api.md` ist Teil des Dreiklangs. Hier ändert sich nur Prosa, kein Feld; `models.py` und `types.ts` bleiben unberührt, und das steht so in der Notiz.
- Deutsche Prosa nach `SPRACHE.md`.

## Prüfung

1. Vorher rot: `grep -rn '0\.1\.0' contracts/ docs/ frontend/src/ frontend/package-lock.json` findet die sechs Stellen (die Beispielantworten `v0.1.0-12-ga22a6c5` zählen nicht; sie bleiben). Nachher findet der Lauf außer den Beispielantworten nichts.
2. `cd frontend && npm run typecheck && npm run test` grün.
3. `mkdocs build --strict` im Backend-venv ohne Warnung.
4. `git diff --stat` des Ticket-Commits nennt genau die sechs Dateien.
