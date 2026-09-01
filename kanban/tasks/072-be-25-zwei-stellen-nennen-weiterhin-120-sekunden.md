---
id: 72
title: BE-25 · Zwei Stellen nennen weiterhin 120 Sekunden
status: done
priority: medium
created: 2026-09-01T12:39:26.15386304+02:00
updated: 2026-09-01T13:01:32.152743092+02:00
started: 2026-09-01T13:01:23.638794792+02:00
completed: 2026-09-01T13:01:23.638794792+02:00
assignee: sophie
tags:
    - backend
    - config
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

[[2026-09-01]] Tue 13:01
## Ergebnis (sophie-21)

Beide Stellen nennen 600, denselben Wert wie `docker/.env.example`.

- `backend/app/config.py:27ff` — `conversion_timeout: int = 600`, mit der Messung
  aus #59 als Kommentar: 326 s langsamstes bekanntes Dokument mal Faktor 1,8
  Streuung sind 587, aufgerundet 600; die Zeit kostet die fehlende Textschicht,
  nicht die Seitenzahl.
- `contracts/api.md:98` — `"conversion_timeout_s": 600` im Beispielrumpf.
- `backend/tests/test_config_defaults.py` (neu) — zwei Tests halten die drei
  Stellen zusammen. Der erste entfernt alle `KAIMARKIT_*`-Variablen aus der
  Umgebung, startet das Backend im `TestClient` und vergleicht
  `limits.conversion_timeout_s` aus `/api/capabilities` mit dem Wert in
  `docker/.env.example`. Der zweite vergleicht den Beispielwert aus
  `contracts/api.md` mit derselben Quelle. Gegenprobe gelaufen: Mit 120 in
  `config.py` faellt der erste Test.

## Pruefung

- `grep -rn "120" backend/app/config.py contracts/api.md` findet die Zeitgrenze
  nicht mehr. Ein Treffer bleibt und hat nichts damit zu tun:
  `contracts/api.md:195` — `"duration_ms": 3120` im Beispiel einer Stapelantwort.
- Nacktes Backend gegen Auslieferung: ausgefuehrt ueber den `TestClient`, ohne
  Container.
- `pytest -q`: 122 passed, 4 deselected. `ruff check .`: sauber.
- Merge `--no-ff` nach main unter `flock`, Commit `7be52bf`.

## Zum Schnittstellen-Dreiklang

Die Auslegung des PO ist richtig. Es aendert sich kein Feld, kein Name und kein
Typ, nur ein Beispielwert. `models.py` fuehrt `conversion_timeout_s` als Feld von
`Limits`, ohne Zahl; `types.ts` nennt die Zahl ebenfalls nicht. Dort gaebe es
nichts zu aendern.

## Befund zur Sammelzahl der Tests — Auskunft, nichts repariert

Die schwankende Zahl hat eine harmlose Ursache: `tests/test_markitdown.py:19`
ruft `pytest.importorskip("markitdown")` auf Modulebene auf. Fehlt das Paket,
sammelt pytest die acht Tests der Datei gar nicht erst, sondern meldet eine
einzige Zeile `SKIPPED` — die Sammelzahl faellt um sieben, obwohl kein Test
verloren geht. Beim ersten Lauf in diesem Worktree fehlte `markitdown` noch
(105 passed, 8 skipped, 4 deselected, 117 Zeilen); Minuten spaeter war es
installiert (120 passed, 4 deselected, 124 gesammelt). Die uebrigen sieben
Uebersprungenen kamen aus derselben Wurzel: fuenf aus `test_converters.py:98`
(„No module named 'markitdown'"), einer aus `test_converters.py:79` (`.xlsx`
braucht `pandas`), einer aus `test_converters.py:140` (fuer `.csv` war keine
Engine verfuegbar). Kein Test ist unbemerkt aus dem Lauf gefallen. Nach dem
Merge sammelt der Zweig 126 Tests, 122 davon ausgewaehlt.
