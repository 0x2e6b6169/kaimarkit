---
id: 49
title: PROC-4 · pytest -m slow ueberspringt auf dem Entwicklungsrechner still
status: in-progress
priority: medium
created: 2026-08-31T17:08:53.51522673+02:00
updated: 2026-09-01T13:50:07.107364906+02:00
started: 2026-09-01T13:02:59.351411003+02:00
assignee: akar
tags:
    - docs
    - process
depends_on:
    - 55
claimed_by: akar-25
claimed_at: 2026-09-01T13:50:07.107364906+02:00
class: standard
---

## Ziel

Ein dokumentierter Pruefbefehl belegt etwas oder sagt, dass er es nicht tut.

## Befund (belegt in INT-2, 31.08.2026)

In der pyenv-Umgebung `claude-code`:

```
pytest -q            -> 107 passed, 3 deselected
pytest -q -m slow    -> 3 skipped, 107 deselected
                        SKIPPED tests/test_converters.py:113: docling ist nicht installiert
```

docling steht nicht in dieser Umgebung; es kommt nur ins Abbild. Der Befehl meldet
"3 skipped" und einen Rueckgabewert 0. Wer ihn abhakt, hat Docling nicht geprueft.

Im Container laufen dieselben Tests wirklich:

```
docker run --rm -u root -v <repo>/backend:/src:ro -w /src kaimarkit:local \
  sh -c "pip install -q pytest httpx && python -m pytest -q -m slow -p no:cacheprovider"
-> 3 passed, 107 deselected in 46.15s
```

## Wo es steht

- `CLAUDE.md`, Abschnitt Befehle: `pytest -q -m slow   # mit Docling, dauert`
- `Makefile`, Ziel `test-slow`: "pytest mit Docling, dauert"
- `ENTWURF.md`, Abschnitt "Pruefung am Ende": derselbe Befehl

`docs/entwicklung.md:85` ist bereits ehrlich ("ohne Docling ueberspringen sie
sich"). Die drei anderen Stellen versprechen mehr, als sie halten.

## Eigene Dateien

- `CLAUDE.md`
- `Makefile`

## Vorgaben

Beide Stellen sagen, wo die langsamen Tests wirklich laufen. Ein eigenes
Make-Ziel, das sie im Abbild ausfuehrt, waere der schoenere Weg; die kurze Fassung
ist ein Halbsatz an beiden Stellen. Was davon, entscheidet die Lane.

Fuer die Marke `slow` selbst aendert sich nichts: Ueberspringen ist auf einem
Rechner ohne docling richtig. Nur soll niemand es fuer bestandene Tests halten.

## Pruefung

- `make help` und `CLAUDE.md` nennen den Weg, auf dem die langsamen Tests wirklich
  laufen.
- Der genannte Weg laeuft durch und meldet `3 passed`.

[[2026-09-01]] Tue 13:02
## Erweitert (01.09.2026) — dieselbe Frage, größerer Fall

sophie hat beim Abschluss von BE-25 (#72) den allgemeinen Fall gefunden. Er gehört
hierher, weil das Ziel dieses Tickets ihn bereits benennt: Ein dokumentierter
Prüfbefehl belegt etwas oder sagt, dass er es nicht tut.

**Die Umgebung, gegen die alle Lanes testen, ändert sich unter ihnen.** Ein Subagent
hat im selben Worktree zweimal hintereinander gemessen, ohne dazwischen etwas zu
ändern:

    105 passed, 8 skipped
    120 passed, 0 skipped

Dazwischen wurde `markitdown` in der geteilten pyenv-Umgebung installiert — von einer
anderen Lane. Ein „grün" aus einem Worktree ist mit einem „grün" aus einem anderen
also nicht vergleichbar, solange nicht feststeht, welche Abhängigkeiten gerade da
waren.

**Verschärfend: `pytest.importorskip` auf Modulebene** (`test_markitdown.py:19`)
nimmt bei fehlender Abhängigkeit das ganze Modul aus der **Sammlung**. Die acht Tests
erscheinen als eine einzige `SKIPPED`-Zeile; die Sammelzahl fällt, ohne dass jemand
sieht, was fehlt. Zweimal hat uns das heute Zahlen erklären lassen, die keine Aussage
hatten.

### Entscheidung des PO

Zwei Abhilfen standen zur Wahl. **Beide billigen, eine ablehnen:**

1. **`pytest -q -rs` wird der dokumentierte Befehl**, nicht `pytest -q`. `-rs` nennt
   jeden übersprungenen Test mit Grund. Ein stiller Übersprung wird damit sichtbar,
   ohne dass jemand daran denken muss.
2. **Ein Subagent meldet die Sammelzahl**, nicht nur bestanden/fehlgeschlagen — also
   „126 gesammelt, 122 ausgewählt, 122 bestanden". Eine verschwundene Sammlung fällt
   dann beim Lesen auf.
3. **Abgelehnt: `importorskip` je Test statt je Modul.** Es behebt das Zählen in
   einem Modul und lässt die Ursache stehen; ein anderes Modul macht es morgen
   wieder. Die Sammelzahl zu melden fängt alle Fälle.

Kein Umbau der Umgebung, keine venv je Worktree — Torch macht das unbezahlbar.

### Zusätzliche eigene Dateien

- `.claude/skills/work-lane/SKILL.md` (Definition of done)

`docs/entwicklung.md` nur, falls dort ein Prüfbefehl steht, der durch die Änderung
unwahr wird.

### Zusätzliche Prüfung

- `CLAUDE.md`, `Makefile` und der Skill nennen `pytest -q -rs`.
- Die Definition of done verlangt die Sammelzahl in der Rückmeldung.
- Gegenprobe: In einer Umgebung ohne `markitdown` nennt der dokumentierte Befehl das
  übersprungene Modul samt Grund.

[[2026-09-01]] Tue 13:04
Hängt an #55 (IN-10), auf Meldung von akar — aus zwei Gründen, von denen der erste allein reicht.

**Die Maschine.** akar-24 misst in #55 Bauzeiten. Der Rechner hat zwei physische Kerne (gemessen in #59), und die Streuung auf identischer Eingabe liegt schon ohne Fremdlast bei Faktor 1,8. Ein paralleler `pytest`-Lauf über 120 Tests samt Gegenprobe im Container nimmt sich einen guten Teil davon. Eine Bauzeit unter fremder Last belegt nichts — und sähe trotzdem aus wie eine Messung.

**Das bedingte Eigentum.** `docs/entwicklung.md` steht in beiden Rümpfen, beide Male unter einer Bedingung: #55 „falls die Bauzeiten dort genannt sind", #49 „nur, falls dort ein Prüfbefehl steht, der unwahr wird". Zwei Tickets, die dieselbe Datei bedingt besitzen, kollidieren erst beim Merge — und dann beim Zweiten. Nach #55 ist außerdem entschieden, ob die Datei überhaupt angefasst wurde.
