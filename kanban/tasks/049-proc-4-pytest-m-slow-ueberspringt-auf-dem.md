---
id: 49
title: PROC-4 · pytest -m slow ueberspringt auf dem Entwicklungsrechner still
status: done
priority: medium
created: 2026-08-31T17:08:53.51522673+02:00
updated: 2026-09-01T13:58:58.95370702+02:00
started: 2026-09-01T13:02:59.351411003+02:00
completed: 2026-09-01T13:58:52.590308962+02:00
assignee: akar
tags:
    - docs
    - process
depends_on:
    - 55
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

## Erledigt (01.09.2026, akar-25) — Merge b7c4611, Commit f8d6fd1

### Was gebaut wurde

**Ein eigenes Make-Ziel, nicht der Halbsatz.** `test-slow-image` (Makefile:78–86)
startet das gebaute Abbild, haengt `backend/` lesend hinein, installiert dort pytest
und httpx und wirft den Container danach weg. Bild- und Tagname kommen aus
`docker/.env` (`KAIMARKIT_IMAGE`, `KAIMARKIT_TAG`) statt fest im Makefile zu stehen —
Konvention 4. `docker run --rm` statt `compose run`: Ein laufender Dienst bleibt
unberuehrt, und der Container des Nutzers auf 127.0.0.1:8080 wurde nicht angefasst.

`test-slow` bleibt und laeuft weiter lokal, sagt aber jetzt in `make help`, was es
tut: „Die slow-Tests lokal; ohne Docling ueberspringen sie sich". Die Spaltenbreite
in `help` musste von `%-14s` auf `%-16s`, sonst haette der neue Name die
Beschreibung verschoben.

**`pytest -q -rs` ist der dokumentierte Befehl** in `CLAUDE.md`, `Makefile`,
`.claude/skills/work-lane/SKILL.md` und `docs/entwicklung.md`.

**Die Definition of done verlangt die Sammelzahl** (SKILL.md:103–107, ein Punkt
vor „suspect the Pruefung"). Der Text ist englisch wie der Rest des Skills und nennt
den Grund in einem Satz, damit ein Subagent in fremder Lane ihn ohne Rueckfrage
befolgt.

### Pruefung

- `make help` nennt `test-slow-image` mit Beschreibung; `CLAUDE.md` (Abschnitt
  Befehle) nennt denselben Weg samt Begruendung. Vorher: kein Treffer fuer `-rs` in
  allen vier Dateien, `make help` ohne den Abbild-Weg — die Pruefung war rot.
- `make test-slow-image` laeuft durch: **6 passed, 137 deselected in 67.95s**.
- Gegenprobe ohne markitdown (meta_path-Finder, der `ModuleNotFoundError` wirft —
  ein Stub, der `ImportError` wirft, taugt nicht: `importorskip` faengt seit pytest
  9.1 nur `ModuleNotFoundError`, siehe `_pytest/outcomes.py`):
  `122 passed, 8 skipped, 6 deselected`, und `-rs` nennt
  `SKIPPED [1] tests/test_markitdown.py:19: MarkItDown ist nicht installiert`.
  Ohne `-rs` waere nur die Sammelzahl von 143 auf 136 gefallen.
- Normallauf: **143 gesammelt, 137 ausgewaehlt, 137 bestanden**; `ruff check .`
  sauber; `mkdocs build --strict` sauber.

### Abweichung von der Pruefung — die Zahl, nicht die Sache

Der Rumpf verlangt `3 passed`. Gemessen wurden **6 passed**. Die Zahl stammt aus
INT-2 vom 31.08.; seither sind vier `slow`-Tests dazugekommen
(`tests/test_docling.py:265, 286, 304, 331` neben `tests/test_converters.py:113, 123`).
Die Annahme hinter der Pruefung ist erfuellt — die langsamen Tests laufen im Abbild
wirklich und bestehen alle. Deshalb keine Uebergabe. Aus demselben Grund steht in
`CLAUDE.md` und `docs/entwicklung.md` keine Testanzahl mehr, sondern „lauter
Uebersprungenes und Rueckgabewert 0": Eine Zahl in der Prosa veraltet mit dem
naechsten Test.

### Gemeldet, nicht geaendert

- `ENTWURF.md`, Abschnitt „Pruefung am Ende", nennt weiter `pytest -q -m slow`. Nicht
  angefasst: Das Dokument haelt die Herkunft fest, nicht die Vorschrift (CLAUDE.md,
  Kopfabschnitt). Wer den Entwurf spaeter nachzieht, findet die Stelle hier.
- `docs/entwicklung.md` wurde angefasst — die Befehlsliste (Zeile 47) und der
  Abschnitt „Tests" waeren sonst unwahr geworden. Der Konflikt mit dem bedingten
  Eigentum aus #55 bestand nicht mehr: #55 war beim Start bereits `done`.
- Der Codeblock unter „Befehle" in `CLAUDE.md` schreibt weiter ASCII-Umschrift
  (`laeuft`, `noetig`) in den bestehenden Zeilen. Nicht geaendert, weil ausserhalb
  dieses Tickets; die neue Prosa darunter schreibt Umlaute.
