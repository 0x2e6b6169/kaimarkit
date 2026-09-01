---
id: 58
title: BE-18 · Die Platzhalter-Warnung hat keinen Fall im Repo
status: done
priority: medium
created: 2026-09-01T10:25:37.13806965+02:00
updated: 2026-09-01T14:06:35.038544633+02:00
started: 2026-09-01T13:06:47.176178135+02:00
completed: 2026-09-01T13:14:43.477822912+02:00
assignee: sophie
tags:
    - backend
    - tests
class: standard
---

## Befund (01.09.2026, aus dem Abnahmelauf von IN-9)

Zwei Sachen an derselben Stelle, beide gemeldet von akar.

**1. Kein Fixture loest die Warnung aus.** `backend/tests/fixtures/tabelle.pdf`
liefert unter `docling` die vollstaendige Tabelle und keine Warnung. Um den Fall
ueberhaupt herzustellen, musste akar-21 sich ein 11-spaltiges PDF von Hand bauen (im
Scratchpad, nicht im Repo). Der Befund, aus dem BE-14 (#47) entstanden ist,
reproduziert also nicht mehr.

Damit haengt die Regressionssicherung in der Luft: Die Warnung ist gebaut und im
echten Lauf einmal gesehen worden, aber nichts im Repo faehrt sie noch einmal an.

Ob BE-13 (#46) das nebenbei mitgeloest hat — dieselben Optionen jetzt auch fuer
Bilder — oder ob `tabelle.pdf` nie die richtige Vorlage war, ist die eigentliche
Frage. Sie entscheidet sich am Gegenstand.

**2. Die Meldung nennt keine Zahl.** Belegter Wortlaut aus dem Container:

    "Docling hat in breit.pdf ein Bild durch einen Platzhalter ersetzt.
     Sein Inhalt fehlt im Markdown."

Datei und Sache stehen drin, im Singular. Die Vorgabe von BE-14 lautete: "Die Zahl
gehoert hinein — ein einzelnes ersetztes Bild ist etwas anderes als vierzehn." Ob
der Text bei mehreren Platzhaltern eine Zahl bildet, ist unbelegt; im geprueften Fall
war es einer.

## Eigene Dateien

- `backend/app/converters/docling.py`
- `backend/tests/test_docling.py`
- `backend/tests/fixtures/` und `build_fixtures.py`

## Vorgaben

Ein Fixture im Repo, das den Platzhalterfall herstellt — nach dem Muster, das
akar-21 benutzt hat. Dazu ein Test, der die Warnung an echter Docling-Ausgabe prueft,
nicht an der Attrappe; er gehoert hinter `-m slow`, wenn er Docling braucht.

Fuer die Zahl: erst messen, dann entscheiden. Bildet der Text bei mehreren
Platzhaltern bereits eine Zahl, ist nur der Test nachzutragen. Bildet er keine, ist
er zu berichtigen — die Vorgabe aus BE-14 steht.

## Pruefung

- Ein Fixture im Repo liefert unter `docling` eine nichtleere `warnings`-Liste.
- Ein Fall mit mehreren Platzhaltern nennt die Zahl. Der Wortlaut steht in der
  Ticketnotiz, aus dem Lauf abgeschrieben und nicht aus dem Quelltext.
- Gegenprobe: `tabelle.pdf` liefert weiterhin die vollstaendige Tabelle und keine
  Warnung.
- `pytest -q` und `pytest -q -m slow` bleiben gruen.

## Zurueckgestellt

Vom Nutzer zurueckgestellt, bis die Abnahmefassung steht (01.09.2026).

[[2026-09-01]] Tue 10:52
Ein echter Fall aus der Abnahme (01.09.2026, Rechnung des Nutzers, einseitig, `engine=auto`): **Docling hat beide Tabellen vollstaendig erkannt** — eine achtspaltige Positionstabelle mit fuenf Zeilen und eine vierspaltige Zahlungstabelle. Kein Platzhalter an ihrer Stelle.

Das stuetzt die erste der beiden Vermutungen in diesem Ticket: Die Tabellenerkennung arbeitet an echten Dokumenten, und `tabelle.pdf` war womoeglich nie die richtige Vorlage fuer den Platzhalterfall. Wer das Ticket umsetzt, sucht die Vorlage also nicht in einer gewoehnlichen Tabelle, sondern in dem, was akar-21 gebaut hat — elf Spalten, vierzehn Zeilen.

Dasselbe Dokument enthaelt einen Platzhalter an anderer Stelle: `<!-- image -->` als erste Zeile, das Logo im Briefkopf. Ob dazu eine Warnung erschienen ist, ist noch offen und beim Nutzer erfragt. Faellt die Antwort "keine Warnung", gehoert das hierher — dann greift der Zaehlweg im Alltagsfall nicht.

[[2026-09-01]] Tue 11:19
Halbe Entwarnung zum zweiten Punkt (Quelltext nachgesehen, 01.09.2026): **`_placeholder_warnings()` bildet sehr wohl eine Zahl.** Bei `count == 1` heisst es "ein Bild durch einen Platzhalter", ab zwei `f"{count} Bilder durch Platzhalter"`. Die Vorgabe aus BE-14 ist also erfuellt; akars Beobachtung galt dem gepruefen Einzelfall, in dem tatsaechlich nur ein Platzhalter vorkam.

Was bleibt, ist der Test: Der Mehrzahlfall ist nirgends gefahren. Dieses Ticket braucht dafuer keine Korrektur mehr, nur die Abdeckung — ein Fall mit zwei oder mehr Platzhaltern, der den Wortlaut festhaelt.

[[2026-09-01]] Tue 11:22
Der Mehrzahlfall ist am echten Dokument belegt (01.09.2026, Abnahme des Nutzers): Dieselbe Anmeldung liefert

    Docling hat in TeleTrusT-T.I.S.P._T.P.S.S.E._CM_2026_Anmeldung.pdf
    3 Bilder durch Platzhalter ersetzt. Ihr Inhalt fehlt im Markdown.

Zahl, Mehrzahl und Wortlaut stimmen. Der zweite Punkt dieses Tickets ist damit erledigt — es bleibt der erste: ein Fixture im Repo, das den Fall festhaelt, damit er nicht nur einmal in einer Abnahme gesehen wurde.


[[2026-09-01]] sophie-25 — umgesetzt

Branch `task/58-platzhalter-fixture`, Commit `087bc61`, nach `main` gemerged.

**Punkt 2 (die Zahl) ist gemessen und erledigt.** `_placeholder_warnings()` direkt aufgerufen, in der pyenv-Umgebung `claude-code`, mit 0/1/2/14 Platzhaltern. Aus dem Lauf abgeschrieben:

    0  -> []
    1  -> Docling hat in breit.pdf ein Bild durch einen Platzhalter ersetzt. Sein Inhalt fehlt im Markdown.
    2  -> Docling hat in breit.pdf 2 Bilder durch Platzhalter ersetzt. Ihr Inhalt fehlt im Markdown.
    14 -> Docling hat in breit.pdf 14 Bilder durch Platzhalter ersetzt. Ihr Inhalt fehlt im Markdown.

Zahl und Mehrzahl stimmen; am Quelltext war nichts zu berichtigen. Die beiden Einheitstests halten jetzt den vollen Wortlaut fest statt einzelner Teilzeichenketten — vorher stand dort nur `"3" in warning`.

**Punkt 1 (das Fixture) ist gebaut.** `backend/tests/fixtures/breit.pdf`, elf Spalten auf vierzehn Zeilen in Sieben-Punkt-Schrift, dazu `build_breit_pdf()` in `build_fixtures.py`. Die Datei ist **byte-identisch** (md5 9d46a776c4337f48efe87038d01bb5a8) mit dem Wegwerf-PDF, das akar-21 im Scratchpad gebaut und an dem er den Platzhalter gesehen hat — die Vorlage ist also nicht nachempfunden, sondern dieselbe.

Der PDF-Behaelter (fuenf Objekte, xref, Offsets) steht jetzt in `_write_pdf()`, den sich beide PDF-Fixtures teilen. Gegenprobe: `tabelle.pdf` baut sich byte-identisch neu (md5 0bdec642644e014fffa05d63c7a7c454 vor und nach dem Umbau). `git check-attr binary` meldet `set` fuer `breit.pdf` — die Regel aus `.gitattributes` greift ohne Zutun.

**Zwei neue Tests hinter `-m slow`** in `test_docling.py`:

- `test_a_wide_table_becomes_a_placeholder_with_a_warning` — `breit.pdf` liefert mindestens einen Platzhalter, genau eine Warnung, und die nennt Datei und Zahl.
- `test_a_plain_table_produces_no_warning` — die Gegenprobe: `tabelle.pdf` liefert keinen Platzhalter und keine Warnung.

**Offen, im Container zu pruefen.** Docling ist in der geteilten Umgebung `claude-code` nicht installiert und wurde dort nicht installiert; beide neuen Tests haben lokal nur uebersprungen. Die Kette Fixture → docling → Warnung ist damit **nicht belegt**, sondern wiederhergestellt: Sie ruht auf akar-21s Beobachtung an derselben Datei. Wer den Container das naechste Mal baut, faehrt `pytest -m slow -k "placeholder or plain_table"` und schreibt das Ergebnis hierher. Faellt der breite Fall dort anders aus, ist die Modellfassung der Unterschied, nicht das Fixture.

**Zahlen.** Sammlung vorher 124/128 (4 deselected), nachher 124/130 (6 deselected) — die zwei neuen slow-Tests. `pytest -q -rs`: 124 passed. `pytest -q -m slow -rs`: 6 skipped, alle mit "docling ist nicht installiert". `ruff check .`: sauber.

**Befund nebenbei, nicht geaendert.** `.gitattributes` markiert `backend/tests/fixtures/**` als binaer. Das trifft auch `build_fixtures.py`, ein Python-Modul: Sein Diff erscheint in jedem Commit als `Bin 13610 -> 15891 bytes` statt als Text. Fuer die Beispieldateien ist die Regel richtig; das Bauskript gehoerte ausgenommen (`backend/tests/fixtures/build_fixtures.py text`). Fremde Datei, deshalb nur gemeldet.

**Aenderung ausserhalb der Dateiliste.** `docs/entwicklung.md`, Abschnitt "Beispieldateien": Er zaehlte neun Dateien und ein PDF; nach dem Merge waeren beide Zahlen falsch. Nach der Regel "Wer ein Verhalten aendert, berichtigt im selben Merge, was dadurch falsch wird" mitkorrigiert und `breit.pdf` in einem Absatz erklaert.

**Die Kette ist belegt** — Lauf im Abbild am 01.09.2026 (IN-12, akar-26).

Abbildstand: `kaimarkit:local`, `sha256:49e8ccc5…`, gebaut am 01.09.2026 um 13:44:22 +0200.
Belegt statt uebernommen: Das im Abbild installierte Paket
`/opt/venv/lib/python3.12/site-packages/app` ist byte-identisch mit `backend/app` aus
`bbf7180` — 16 `.py`-Dateien, die Liste ihrer md5-Summen ergibt beidseits
`52e7111967c67d72b67f08e863a0a9ea`. `git diff bbf7180 HEAD -- backend/` ist leer, das
Abbild bildet also auch den heutigen Stand ab. Fixture `breit.pdf`: md5
`9d46a776c4337f48efe87038d01bb5a8`, unveraendert. docling 2.124.0.

Aufruf (die Bauart von `make test-slow-image`, eigener Wegwerf-Container, `backend/`
nur lesend eingehaengt — der laufende Dienst des Nutzers blieb stehen):

    docker run --rm -u root -v "$PWD/backend:/src:ro" -w /src kaimarkit:local \
      sh -c 'pip install -q pytest httpx && python -m pytest -q -rs -m slow \
             -k "placeholder or plain_table" -p no:cacheprovider'

Ausgang, woertlich:

    tests/test_docling.py::test_a_plain_table_produces_no_warning PASSED     [ 50%]
    tests/test_docling.py::test_a_wide_table_becomes_a_placeholder_with_a_warning PASSED [100%]
    ================ 2 passed, 141 deselected, 1 warning in 29.09s =================

**Beide Tests liefen, keiner uebersprang.** Kein `docling ist nicht installiert` im
`-rs`-Abschnitt; der erste Lauf meldete `2 passed, 141 deselected, 3 warnings in
26.52s`, die Warnungen waren Deprecation-Meldungen aus Starlette und Docling.

Was das Modell heute aus `breit.pdf` macht, gemessen im selben Abbild:

    PLACEHOLDERS 1
    WARNINGS ['Docling hat in breit.pdf ein Bild durch einen Platzhalter ersetzt. Sein Inhalt fehlt im Markdown.']

Genau ein Platzhalter, genau eine Warnung, und sie nennt Datei und Zahl. Das deckt
sich mit der Beobachtung von akar-21 an derselben Datei. Die Kette Fixture → docling →
Warnung ruht damit nicht mehr auf einer Beobachtung, sondern auf einem Lauf gegen den
heutigen Stand.
