---
id: 121
title: 'BE-39 · Die Warnung nennt den Grund und den Umweg (GitHub #2)'
status: done
priority: high
created: 2026-09-03T15:13:02.423738476+02:00
updated: 2026-09-07T09:46:08.559729031+02:00
started: 2026-09-07T09:46:07.803649772+02:00
completed: 2026-09-07T09:46:07.803649772+02:00
assignee: sophie
tags:
    - backend
    - gh-2
class: standard
---

## Ziel

Das ist der eigentliche Punkt aus GitHub-Issue #2. Der Nutzer hat eine Warnung gesehen
und wurde daraus nicht klüger — auf die Frage „stand ein Warnhinweis da?" hat er
geantwortet: „Ja, eine Warnung stand da." Gefehlt hat ihm nicht die Warnung, sondern
ihr **Grund**.

Aus BE-38 (#117) liegt der gemessene Wortlaut vor, den MarkItDown bei PDF setzt:

    MarkItDown übernimmt keine Bilder aus PDF. Enthielt bild_im_dokument.pdf Bilder,
    fehlt ihr Inhalt hier.

Der Satz sagt, was fehlt. Er sagt nicht, was der Nutzer tun kann. Und für den gemessenen
Hauptfall — ein Bild in einem docx — gibt es überhaupt keine Warnung; den behandelt
BE-40.

## Eigene Dateien

- `backend/app/converters/docling.py` und der Test dazu
- die Datei, in der die Warnungstexte der Engines stehen, **falls es eine gemeinsame
  gibt** — erst nachsehen, nicht raten. Steht der Wortlaut in mehreren Engine-Modulen,
  gehören sie alle dazu, `markitdown.py` ausgenommen.

`backend/app/converters/markitdown.py` gehört BE-40 (#122). Kollidieren die beiden an
einer gemeinsamen Datei, geht dieses Ticket zuerst; BE-40 hängt daran.

Nicht hier: `docs/formate.md` und `docs/grenzen.md` — die gehören DOC-18 (#123).

## Vorgaben

- Eine Warnung über ausgelassene Bilder nennt drei Dinge: **was** ausgelassen wurde,
  **warum** (die Engine kann es an dieser Stelle nicht), und **was der Nutzer tun kann**.
  Der Umweg ist gemessen: bei PDF hilft Docling mit OCR, bei docx hilft, das Dokument
  als PDF abzugeben.
- Deutsch, ein Satz je Sache, keine Fachbegriffe aus der Bibliothek. Der Leser ist
  jemand, der ein Dokument hochgeladen hat, kein Entwickler.
- Der Dateiname bleibt in der Meldung; er unterscheidet die Zeilen bei einem Stapel.
- Konvention 3 bleibt unberührt: Das sind Warnungen, keine `ConversionError`.

## Prüfung

- Rot vor grün: Ein Test, der die Warnung eines Laufs mit ausgelassenen Bildern auf den
  Umweg hin prüft, fällt vor der Arbeit durch.
- Der neue Wortlaut steht **wörtlich** in der Ticketnotiz, in richtiger Schreibung mit
  Umlauten, damit er im Issue-Kommentar zitiert werden kann.
- `pytest -q -rs` und `ruff check .` sauber; Sammelzahl und Abgewählte gemeldet.
- Wo die Warnung nur im Abbild entsteht: `make test-slow-image`, nicht die pyenv-Umgebung.

[[2026-09-03]] Thu 15:52
## Angehalten: Übernahmestand (sophie, 2026-09-03)

BE-39 ruht, bis der Nutzer freigibt. Kein fachliches Hindernis: Drei Subagenten sind
hintereinander an Serverfehlern gestorben (500, 529, 529), und jeder weitere Anlauf
kostet Tokens des Nutzers, der sein Limit schont. `v0.3.0` ist ohne dieses Ticket
getaggt und nennt es unter den bekannten Einschränkungen.

**Was steht.** Commit `be3904f` auf dem Zweig `task/121-warning-reason`, Worktree
`.worktrees/task-121`, Arbeitsbaum sauber, `main` stand dabei auf `94e7b7f`. Geändert
sind `backend/app/converters/docling.py` (+43/−3) und `backend/tests/test_docling.py`
(+72) — genau die Ticketdateien.

Der Commit heißt „wip" und ist **ungeprüft**. Die Eltern-Sitzung hat ihn gesetzt, um die
Arbeit eines abgestürzten Subagenten festzuhalten, nicht um sie abzunehmen. Der erste
Vorgänger hatte gemeldet, sein neuer Test sei rot gewesen („3 failed"), steckte aber noch
in der Umsetzung.

**Was fehlt.**

- Den Diff prüfen, statt ihm zu vertrauen, weil er schon da ist: Nennt jede geänderte
  Meldung, **was** fehlt, **warum** die Engine es an dieser Stelle nicht kann, und **was
  der Nutzer tun kann**?
- Rot vor grün nachholen — es ist noch belegbar: den neuen Test gegen die alte
  `docling.py` laufen lassen (`git checkout main -- backend/app/converters/docling.py`,
  Test, Fehlschlag mit Zahlen notieren, dann `git checkout HEAD -- …` zurück).
- Der Wortlaut in richtiger Schreibung mit Umlauten, deutsch, ein Satz je Sache, ohne
  Fachbegriff aus der Bibliothek — der Leser hat ein Dokument hochgeladen und ist kein
  Entwickler. Der Dateiname bleibt in der Meldung. Der fertige Wortlaut gehört **wörtlich
  in diese Notiz**: Der PO zitiert ihn im GitHub-Issue.
- Den alten Wortlaut über **alle** Tests greppen, nicht nur die Ticketdatei. Liegt eine
  Fundstelle außerhalb der eigenen Dateien: melden statt ändern.
- `pytest -q -rs` und `ruff check .`; Sammelzahl und die Zahl der **Abgewählten** melden.
  Die slow-Tests fallen über `addopts = -m "not slow"` als *deselected* heraus, nicht als
  *skipped* — `-rs` kann sie gar nicht nennen.

**Auflage, an der das Ticket hängt.** Jeder Umweg, den eine Meldung nennt, muss in genau
diesem Stand funktionieren — also in `v0.3.0` plus diesem Merge. Nichts, was erst BE-40
(#122) bringt: Nach diesem Merge warnt MarkItDown bei docx weiterhin gar nicht und setzt
weiterhin `![](data:image/png;base64…)` ins Markdown. **Kein Satz darf klingen, als würde
bei docx gewarnt** — das schickt den Testenden auf die Suche nach einem Fehler in seiner
eigenen Datei, und das ist schlimmer als das heutige Schweigen. Die zwei möglichen Umwege
sind begehbar: Die Enginewahl steht im Frontend als Schaltergruppe, der OCR-Schalter kommt
aus `/api/capabilities`, und nicht angeklickt gilt die Vorgabe `true`.

**Berichtigung einer Annahme im Rumpf oben.** Der Rumpf zitiert den Nutzer mit „Ja, eine
Warnung stand da." **Das hat er widerrufen.** Es war ein Word-Dokument, und es stand gar
keine Warnung da; bei docx warnt MarkItDown nicht. Der Grund für dieses Ticket bleibt
unberührt — die Warnungen, die es gibt, nennen weder den Grund noch den Umweg. Was der
Nutzer erlebt hat, behebt BE-40 (#122).

**Eine gemeinsame Warnungsdatei gibt es nicht.** Betroffen sind nur `docling.py` und sein
Test; BE-40 kann `markitdown.py` unberührt besitzen.

Der Claim bleibt `sophie-41`. Wer übernimmt, benutzt denselben Namen oder gibt ihn vorher
frei — `kanban-md` verlangt bei jeder Änderung denselben Claim.

## Ergebnis (sophie-41, Uebernahme des geretteten Stands)

Der gerettete Commit `be3904f` war brauchbar, aber nicht fertig: Der dritte Fall
(PDF/Bilddatei mit schon eingeschalteter Texterkennung) nannte keinen Grund, sondern
nur einen Zustand („Die Texterkennung war bereits eingeschaltet."), und die Aussage im
docx-Fall war zu breit — sie schloss Bilddateien aus, in denen Docling sehr wohl Text
liest. Beides ist berichtigt.

**Der fertige Wortlaut, wörtlich.** Der erste Teil ist unverändert und zählt weiter mit
(„ein Bild … Sein Inhalt fehlt" / „3 Bilder … Ihr Inhalt fehlt"). Angehängt wird je nach
Format und Schalter genau einer von drei Sätzen samt Umweg:

1. `.docx`, `.pptx`, `.xlsx`, `.html`, `.htm`:

    Docling hat in bild.docx ein Bild durch einen Platzhalter ersetzt. Sein Inhalt
    fehlt im Markdown. Text aus einem Bild liest Docling nur in einer PDF-Datei oder
    in einer Bilddatei. Wer ihn braucht, speichert das Dokument als PDF und lädt es
    mit eingeschalteter Texterkennung erneut hoch.

2. PDF und Bilddateien, Texterkennung aus:

    Docling hat in bericht.pdf ein Bild durch einen Platzhalter ersetzt. Sein Inhalt
    fehlt im Markdown. Ohne eingeschaltete Texterkennung liest Docling den Text aus
    einem Bild nicht. Wer ihn braucht, schaltet die Texterkennung ein und lädt die
    Datei erneut hoch.

3. PDF und Bilddateien, Texterkennung an:

    Docling hat in bericht.pdf ein Bild durch einen Platzhalter ersetzt. Sein Inhalt
    fehlt im Markdown. Auch mit eingeschalteter Texterkennung nimmt Docling Bilder
    nicht ins Markdown auf. Ein Blick ins Original zeigt, was dort stand.

**Die Auflage ist eingehalten.** Kein Satz spricht von MarkItDown, keiner behauptet eine
Warnung, die es nicht gibt. Beide Umwege sind in diesem Stand begehbar: Die Enginewahl
steht im Frontend, der OCR-Schalter kommt aus `/api/capabilities` und ist ohne Klick
`true`, und `PREFERENCES` in `registry.py` führt für `.pdf` ohnehin `docling` an erster
Stelle — wer dem docx-Hinweis folgt und das PDF hochlädt, landet auch mit `engine=auto`
bei Docling. Nachgesehen, nicht angenommen.

Der dritte Satz ist zahlneutral formuliert („nimmt Docling Bilder nicht ins Markdown
auf … was dort stand"), weil derselbe Text auch an einer Meldung über vierzehn
Platzhalter hängt.

**Rot vor grün, nachgeholt und mit dem endgültigen Wortlaut wiederholt.** Neue
`docling.py` weggenommen (`git checkout main -- backend/app/converters/docling.py`),
`pytest -q -rs tests/test_docling.py`: **5 failed, 16 passed, 5 deselected**. Fünf, nicht
drei: die drei neuen Fälle plus die zwei vorhandenen Platzhaltertests, deren erwarteter
Text sich mitändert. Danach zurückgeholt, alles grün.

**Zahlen.** `pytest -q -rs` im Backend: **214 gesammelt, 203 ausgewählt, 203 bestanden,
11 abgewählt** (die `slow`-Tests über `addopts = -m "not slow"`), 0 übersprungen.
Nach dem Merge auf `main` noch einmal dieselben Zahlen. `ruff check .`: All checks
passed. `mkdocs build --strict`: Rückgabewert 0, keine Build-Warnung (die rote Meldung
des Material-Themes ist ein Herstellerhinweis).

**Der alte Wortlaut über alle Tests gegrept.** „Platzhalter ersetzt" / „Inhalt fehlt im
Markdown" steht nur in `backend/tests/test_docling.py` und in `docling.py` selbst — beide
gehören diesem Ticket. `contracts/api.md:175` und `frontend/src/components/FileRow.test.ts:114`
führen einen anderen, erfundenen Beispieltext („Seite 4 enthielt ein Bild, das durch
einen Platzhalter ersetzt wurde."); der ist von dieser Änderung nicht berührt und bleibt
unangetastet.

**Doku im selben Merge.** `docs/formate.md` zitierte die Warnung und hörte nach dem
ersten Teil auf; nach dieser Änderung hätte das Zitat als ganze Meldung gelesen. Ein Satz
nennt jetzt, was folgt. Die Seite gehörte DOC-18 (#123), das ist geschlossen; kein
offenes Ticket führt sie. `docs/grenzen.md` bleibt unberührt und wahr.

**Befund für den PO (melden statt ändern).** `ruff format --check` würde im Backend acht
Dateien umformatieren, zwei davon meine — es sind durchweg alte Stellen mit
Zeilenumbrüchen, die `ruff format` zusammenzöge (Zeilenlänge). Das Projekt fährt nur
`ruff check` (Makefile-Ziel `lint`); `ruff format` steht nirgends. Entweder man nimmt es
auf und formatiert einmal alles, oder man lässt es ausdrücklich weg. Nichts geändert.

Commits `b3a373e` und `109aef4` auf `task/121-warning-reason`, Merge `e5b90aa` (--no-ff,
unter flock). Worktree entfernt, Zweig gelöscht.
