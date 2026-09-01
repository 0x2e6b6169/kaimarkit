---
id: 58
title: BE-18 · Die Platzhalter-Warnung hat keinen Fall im Repo
status: backlog
priority: medium
created: 2026-09-01T10:25:37.13806965+02:00
updated: 2026-09-01T10:52:04.69285299+02:00
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
