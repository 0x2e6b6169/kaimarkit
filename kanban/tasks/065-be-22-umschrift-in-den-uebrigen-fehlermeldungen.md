---
id: 65
title: BE-22 · Umschrift in den uebrigen Fehlermeldungen des Backends
status: done
priority: medium
created: 2026-09-01T12:19:20.541493648+02:00
updated: 2026-09-01T12:26:23.880406381+02:00
started: 2026-09-01T12:26:13.592139855+02:00
completed: 2026-09-01T12:26:13.592139855+02:00
assignee: sophie
tags:
    - backend
    - ux
class: standard
---

## Befund (01.09.2026, von sophie beim Abschluss von BE-21 weitergesucht)

BE-21 (#64) hat zwei Meldungen berichtigt. Dieselbe ASCII-Umschrift steht in
nutzersichtbaren Ausnahmetexten in vier weiteren Dateien. Am Gegenstand nachgesehen,
nicht aus einem `grep` uebernommen:

    api/convert.py:101        "Hoechstens {n} Dateien je Aufruf, angekommen sind {m}"
    converters/registry.py:94 "Engine {name} ist nicht verfuegbar: {exc}"
    converters/registry.py:130"Fuer {ext} gibt es keine Engine."
    converters/registry.py:138"Fuer {ext} ist zurzeit keine Engine verfuegbar."
    converters/pandoc.py:70   "Pandoc liest {ext} nicht."
    converters/pandoc.py:91   "Pandoc laesst sich nicht aufrufen: {exc}"
    converters/docling.py:183 "Docling ist nicht verfuegbar: {exc}"

Alle sieben erreichen den Nutzer als Fehlertext in der Oberflaeche.

## Ein Fehler im Rumpf von BE-21, damit er sich nicht wiederholt

BE-21 nannte `errors.py:60`, `:67` und `:74` als Fundstellen. **Das war falsch** — es
sind Docstrings; `errors.py` enthaelt keine nutzersichtbare Zeichenkette. Die Liste
stammte aus einem `grep` des PO, der nicht zwischen Meldung und Kommentar
unterscheidet. sophie hat die Datei zu Recht unberuehrt gelassen und es gemeldet.

Fuer dieses Ticket heisst das: Die Liste oben ist einzeln nachgesehen. Findet sich
trotzdem eine Stelle, die keine Meldung ist, gilt dasselbe — auslassen und melden.

## Eigene Dateien

- `backend/app/api/convert.py`
- `backend/app/converters/registry.py`
- `backend/app/converters/pandoc.py`
- `backend/app/converters/docling.py`
- die zugehoerigen Tests

**`registry.py` ist die Engpassdatei.** Solange dieses Ticket offen ist, darf kein
zweites sie anfassen. Ich halte die Lane entsprechend frei.

Nicht `models.py` — die OpenAPI-Felderklaerungen gehoeren zum
Schnittstellen-Dreiklang und sind eigens geschnitten (#66).

## Vorgaben

Nur die Zeichenketten, die als Meldung zum Nutzer gehen. Nicht Docstrings, nicht
Kommentare, nicht Bezeichner. Von Hand pruefen statt ersetzen zu lassen.

## Pruefung

- Die sieben genannten Meldungen tragen Umlaute.
- Gegenprobe an der echten API, nicht nur im Test: Ein Aufruf mit zu vielen Dateien
  meldet "Höchstens ...", eine unbekannte Endung "Für ... gibt es keine Engine."
- `pytest -q` bleibt gruen; Tests, die den alten Wortlaut pruefen, ziehen mit.

[[2026-09-01]] Tue 12:20
Eine Datei kommt dazu, und der Grund ist lehrreicher als die Datei.

**`backend/app/converters/markitdown.py:60`** — die Warnung, die #60 vorgestern gebaut hat: "MarkItDown uebernimmt keine Bilder aus PDF." Sie ist Minuten nach dem Merge von #64 entstanden, der das Gegenteil hergestellt hat. Dazu der Modul-Docstring in Zeile 6.

**Woher sie kommt:** Ich habe den Wortlaut im Rumpf von #60 vorgeschlagen — in ASCII-Umschrift, weil ich Ticketruempfe gewohnheitsmaessig so schreibe. Der Subagent hat ihn woertlich uebernommen, und das war richtig: Sein Ticket verlangte den Text, nicht die Schreibweise.

Die Umschrift waechst also aus dem Board nach, nicht nur aus dem Quelltext. Wer sie nur dort berichtigt, wo sie steht, holt sie beim naechsten Ticket wieder herein.

**Die Gewohnheit war nie noetig:** Neun der 64 Ticketdateien tragen bereits Umlaute, `kanban-md` kommt damit zurecht. Ein vorgeschlagener Wortlaut gehoert deshalb in richtiger Schreibung in den Rumpf. Steht ab jetzt in `CLAUDE.md`, Abschnitt "Prosa".

Damit besitzt dieses Ticket zusaetzlich `backend/app/converters/markitdown.py` und `backend/tests/test_markitdown.py`.


[[2026-09-01]] Erledigt (sophie-17), Branch task/65-umschrift-meldungen, Merge-Commit 6aa588e.

**Geändert — die acht genannten Meldungen plus eine gefundene neunte:**
`convert.py:101` „Höchstens …"; `registry.py:94` „… ist nicht verfügbar", `:130` „Für … gibt es keine Engine.", `:138` „Für … zurzeit keine Engine verfügbar."; `pandoc.py:91` „Pandoc lässt sich nicht aufrufen"; `docling.py:183` „Docling ist nicht verfügbar"; `markitdown.py:60` „MarkItDown übernimmt keine Bilder aus PDF." und der Modul-Docstring — ganz, Zeilen 3 bis 11. Ihn nur in Zeile 6 zu berichtigen hätte einen halb umgeschriebenen Absatz hinterlassen; das ist schlechter als beides ganz. `test_markitdown.py:119` zieht mit.

**Neu gefunden, im selben Merge behoben:** `registry.py:173` — `EngineUnavailable(f"Fuer {ext} ist keine Engine da.")` am Ende von `convert_with_fallback`. Nutzersichtbar, stand nicht in der Liste. Sie in der Engpassdatei stehen zu lassen hätte eine dritte Runde desselben Tickets erzwungen.

**Ein falscher Eintrag in der Liste:** `pandoc.py:70` lautet `f"Pandoc liest {ext or 'Dateien ohne Endung'} nicht."` und enthält keine Umschrift. Nichts zu tun — dieselbe Art Fehler wie `errors.py` in BE-21.

**Bewusst stehen gelassen:** `docling.py:163`, `log.warning("Docling ist nicht verfuegbar: %s", exc)`. Wortgleich mit `:183`, aber eine Logzeile für den Betreiber, keine Nutzermeldung; die Abgrenzung des Tickets nennt ausdrücklich nur, was beim Nutzer landet. Soll die Umschrift auch aus den Logs verschwinden, ist das ein eigenes Ticket und beträfe alle `log.*`-Aufrufe. Ebenfalls unberührt: sämtliche Docstrings und Kommentare in den fünf Dateien sowie die `ss`- und `ue`-Treffer in englischen Bezeichnern (`subprocess`, `passthrough`, `true`).

**Systematisch geprüft, nicht nur gegrept:** Ein AST-Lauf über die fünf Dateien listet die String-Konstanten ohne die Docstrings. Danach bleiben genau die zwei oben genannten Stellen übrig — `registry.py:173` behoben, `docling.py:163` bewusst gelassen.

**Prüfung:** `pytest -q` 114 passed, 4 deselected. `ruff check .` sauber. Gegenprobe an der echten API, nicht im Test: `uvicorn` auf Port 8765 mit `KAIMARKIT_MAX_FILES=2`, kein Container. Drei Dateien an `/api/convert/batch` → `{"detail":"Höchstens 2 Dateien je Aufruf, angekommen sind 3","code":"too_many_files"}`; eine `.zzz` an `/api/convert` → `{"detail":"Für .zzz gibt es keine Engine.","code":"unsupported_format"}`. Die Umlaute kommen als UTF-8 durch die JSON-Antwort.

`models.py` und der Schnittstellen-Dreiklang bleiben unberührt (#66).
