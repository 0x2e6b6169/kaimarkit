---
id: 102
title: ORG-4 · Versionsangaben im Quelltext auf 0.2.0
status: done
priority: high
created: 2026-09-02T16:47:44.950141974+02:00
updated: 2026-09-03T11:26:12.319035065+02:00
started: 2026-09-03T11:26:00.703504951+02:00
completed: 2026-09-03T11:26:00.703504951+02:00
assignee: sophie
depends_on:
    - 99
class: standard
---

## Ziel

Die von Hand gepflegten Versionsangaben auf `0.2.0` heben, damit der Tag
`v0.2.0` nicht auf einen Quelltext zeigt, der `0.1.0` von sich behauptet.

## Warum das kein Formalie-Ticket ist

Nach IN-19 (#99) speist `git describe` die Anzeige, und die Angaben im
Quelltext sind nur noch der Rückfall — für einen Bau aus einem Tarball ohne
`.git`. Ein Rückfall, der `0.1.0` sagt, während der Tag `v0.2.0` lautet, ist
schlimmer als gar keiner: Er sieht aus wie eine Auskunft und ist eine falsche.

## Eigene Dateien

- `backend/app/__init__.py`
- `frontend/package.json`

Beide führen heute `0.1.0`. Sonst nichts: `pyproject.toml` liest die Version
über `[tool.hatch.version]` aus `__init__.py` und bleibt unberührt.

## Vorgaben

**Beide Zahlen lauten `0.2.0`**, ohne `v`. Das `v` gehört zum Git-Tag, nicht in
den Quelltext — `git describe` setzt es von selbst davor.

**Sonst nichts anfassen.** Kein CHANGELOG anlegen, keine Doku-Seite nachziehen,
keine Beispielantwort ändern. Die Beispiele in `contracts/api.md`,
`docs/api.md` und `docs/schnellstart.md` hat BE-33 bereits auf die
`git describe`-Form gebracht und nennen keine feste Zahl mehr; ist das doch der
Fall, melden statt ändern.

## Prüfung

1. `grep -rn '0\.1\.0' backend/app/ frontend/package.json` findet nichts mehr.
2. `pytest -q -rs` im Backend grün — Sammelzahl, ausgewählte Zahl und
   Übersprungenes nennen.
3. `cd frontend && npm run build` läuft durch.
4. `cd backend && pip wheel . --no-deps` erzeugt ein Rad, dessen Name `0.2.0`
   trägt. Das belegt, dass `hatchling` die Zahl wirklich aus `__init__.py`
   zieht und nicht irgendwo eine zweite steht.


## Ergebnis (sophie-34)

Merge `8474fb0` auf `main`; `backend/app/__init__.py` und `frontend/package.json` lauten `0.2.0`.

Prüfung: (1) `grep` trifft in den beiden Dateien nichts mehr; (2) `pytest -q -rs`: 152 gesammelt, 145 ausgewählt (7 deselektiert, slow), 145 bestanden, 0 übersprungen; (3) `npm run build` läuft durch, `package-lock.json` unverändert — der Worktree hatte kein `node_modules`, ein `npm ci` ging voraus; (4) `pip wheel . --no-deps` erzeugt `kaimarkit-0.2.0-py3-none-any.whl` — hatchling zieht die Zahl aus `__init__.py`.

## Befunde, nicht geändert

- Prüfpunkt 1 trifft nach der Arbeit noch `backend/app/config.py:51`: ein Kommentar, der die `git describe`-Form mit `v0.1.0` als Beispiel illustriert. Keine Versionsbehauptung, aber der grep aus dem Ticket bleibt dadurch rot.
- Drei Doku-Stellen nennen den Rückfall ohne `.git` als feste `0.1.0`: `contracts/api.md:75`, `docs/api.md:42`, `docs/schnellstart.md:38` („Ein Bau ohne Git-Verlauf meldet `0.1.0`"). Seit diesem Merge meldet er `0.2.0` — die Sätze sind jetzt falsch. Dazu `frontend/src/api.ts:95` und `App.vue:47` als Kommentare mit „Heute ist es `0.1.0`". Die Beispiele `v0.1.0-12-ga22a6c5` in `docs/betrieb/konfiguration.md:49` und den Tests sind reine Formbeispiele und bleiben richtig.
- `frontend/package-lock.json` führt die Paketversion weiter als `0.1.0` (Zeilen 3 und 9); `npm ci` stört das nicht, das nächste `npm install` zieht sie nach.
