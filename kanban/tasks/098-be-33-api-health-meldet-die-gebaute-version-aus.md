---
id: 98
title: BE-33 · /api/health meldet die gebaute Version aus der Umgebung
status: todo
priority: high
created: 2026-09-02T16:37:59.663775366+02:00
updated: 2026-09-02T16:37:59.663775366+02:00
assignee: sophie
class: standard
---

## Ziel

`/api/health` meldet den Stand, der wirklich läuft. Heute steht in
`app/__init__.py` von Hand `0.1.0`; ob der Dienst auf dem Tag sitzt oder zwölf
Commits dahinter, sieht man ihm nicht an. Künftig kommt der Wert aus der
Umgebung, und `__version__` ist nur noch der Rückfall.

Der Nutzer hat am 2026-09-02 entschieden: **die Form von `git describe`**, also
`v0.1.0` auf dem Tag, `v0.1.0-12-ga22a6c5` dahinter, mit `-dirty` bei
Änderungen im Arbeitsbaum.

## Eigene Dateien

- `backend/app/config.py`
- `backend/app/__init__.py`
- `backend/tests/test_version.py` — neu
- `contracts/api.md` (Abschnitt `GET /api/health`)
- `docs/api.md` (Abschnitt `GET /api/health`)
- `docs/schnellstart.md` (die Zeile mit der Beispielantwort)

`main.py` und `models.py` sind **nicht** aufgeführt: Wenn die Änderung sie
braucht, ist der Entwurf falsch. Melden statt anfassen.

## Vorgaben

**Der Wert kommt über `config.py`,** wie jede andere Einstellung auch
(Konvention 4): `KAIMARKIT_VERSION`. Ist die Variable leer oder fehlt sie, gilt
`__version__` aus `app/__init__.py`. Kein Aufruf von `git` zur Laufzeit — der
Container hat kein `.git`, und ein Unterprozess im Healthcheck wäre der falsche
Preis für eine Zeichenkette.

**`__version__` bleibt stehen und behält `0.1.0`.** Es ist der Rückfall für die
Entwicklung ohne Bau und die Quelle für `hatchling` (`[tool.hatch.version]`
zeigt darauf). Nicht entfernen, nicht auf die Umgebung umstellen.

**Der Schnittstellen-Dreiklang.** `models.py` sagt `version: str`, `types.ts`
sagt `version: string` — beides bleibt richtig, es ändert sich nur der
Beispielwert. Trotzdem beide Dateien einmal ansehen und in der Notiz
festhalten, dass sie unverändert bleiben durften; genau hier laufen die Seiten
sonst auseinander.

**Die Beispielwerte in Vertrag und Doku werden wahr gemacht.** In
`contracts/api.md`, `docs/api.md` und `docs/schnellstart.md` steht heute
`{ "status": "ok", "version": "0.1.0" }`. Das ist nach dieser Änderung nicht
mehr, was ein gebauter Container antwortet. Beispiel auf die neue Form bringen
und in einem Satz sagen, woher der Wert stammt und was der Rückfall ist.

## Prüfung

1. Neu in `test_version.py`: Mit gesetztem `KAIMARKIT_VERSION` antwortet
   `/api/health` genau mit diesem Wert; ohne die Variable mit `__version__`.
   Beide Fälle vor der Änderung rot — einmal belegen.
2. `pytest -q -rs` — Sammelzahl, ausgewählte Zahl und Übersprungenes nennen,
   nicht nur „bestanden".
3. `ruff check .` ohne Befund.
4. Kein Treffer mehr für `"version": "0.1.0"` in `contracts/` und `docs/`.
