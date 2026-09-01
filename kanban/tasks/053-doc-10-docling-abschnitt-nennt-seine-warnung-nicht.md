---
id: 53
title: DOC-10 · Docling-Abschnitt nennt seine Warnung nicht
status: done
priority: low
created: 2026-09-01T09:14:12.802860179+02:00
updated: 2026-09-01T13:32:07.442892715+02:00
started: 2026-09-01T13:26:51.486134658+02:00
completed: 2026-09-01T13:31:49.271377511+02:00
assignee: sophie
tags:
    - docs
class: standard
---

## Befund (01.09.2026, gemeldet von sophie aus BE-14)

`docs/formate.md`, Abschnitt "Docling", nennt die Platzhalter-Warnung nicht, die
BE-14 (#47) eingebaut hat. Die Abschnitte zu MarkItDown und Pandoc benennen ihre
`warnings`; der Docling-Abschnitt schweigt.

Der Abschnitt wird durch BE-14 nicht unwahr — deshalb hat sophie ihn richtigerweise
gemeldet statt geaendert. Er ist unvollstaendig, und das ist eine andere Sache.

## Ziel

Wer den Abschnitt liest, weiss, dass Docling Bilder durch Platzhalter ersetzt und
dass die Antwort das mit einer Warnung samt Zahl sagt.

## Eigene Dateien

- `docs/formate.md` (Abschnitt "Docling")

Nach dem Ticketschnitt gehoert der Abschnitt der Lane, die den Gegenstand baut —
Aussagen ueber Doclings Verhalten also dem Backend, nicht der Doku-Lane.

## Vorgaben

Zwei bis drei Saetze, in der Form der beiden Nachbarabschnitte. Die Zahl gehoert
erwaehnt: Die Warnung nennt, wie viele Platzhalter im Ergebnis stehen.

## Pruefung

- Der Abschnitt "Docling" nennt die Warnung.
- `make docs-serve` rendert die Seite fehlerfrei.
- Gegenprobe am Gegenstand statt am Werkzeug: Der genannte Wortlaut stimmt mit dem
  ueberein, den `_placeholder_warnings()` erzeugt.

[[2026-09-01]] Tue 13:26
Der Wortlaut ist seit #58 belegt, nicht mehr nur gebaut: `_placeholder_warnings()` wurde mit 0, 1, 2 und 14 Platzhaltern aufgerufen, Zahl und Mehrzahlform stimmen. Wer diesen Abschnitt schreibt, kann den Wortlaut aus der Notiz von #58 übernehmen, statt ihn aus dem Quelltext abzuleiten.

Seit dem Anlegen dieses Tickets ist eine zweite Warnung dazugekommen: #60 hat für MarkItDown bei PDF eine feste Warnung gebaut ("MarkItDown übernimmt keine Bilder aus PDF"). Sie gehört in den Abschnitt "MarkItDown", nicht hierher — aber wer beim Schreiben merkt, dass der eine Abschnitt seine Warnung nennt und der andere nicht, meldet das, statt beide anzufassen. Der MarkItDown-Abschnitt wurde in #60 bereits berichtigt.


[[2026-09-01]] sophie-28 — umgesetzt

Branch `task/53-docling-warnung-doku`, Commit `5b6211d`, nach `main` gemerged (Merge unter `flock`).

**Was jetzt dort steht.** Drei Sätze im Abschnitt „Docling: Modelle und OCR", eingefügt zwischen dem OCR-Absatz und dem Absatz zu `DOCLING_ARTIFACTS_PATH`: Docling setzt statt eines Bildes den Platzhalter `<!-- image -->`; das trifft auch breite Tabellen, die das Modell als Bild einordnet; die Antwort sagt das in `warnings` samt Zahl, und bei einem einzigen Platzhalter lautet der Text anders.

**Der Wortlaut stammt aus der Notiz von #58, nicht aus dem Quelltext** — und wurde danach am Gegenstand gegengeprobt: `_placeholder_warnings()` in der pyenv-Umgebung `claude-code` direkt aufgerufen, mit 0, 1, 2 und 14 Platzhaltern. Die Ausgabe stimmt Zeichen für Zeichen mit der gemessenen Fassung aus #58 überein. Ein Vergleichslauf prüft beide zitierten Stellen gegen die Funktionsausgabe im Fließtext der Seite und meldet für 1 und 14 „True".

**Zahlen.** Sammlung 129/135 (6 deselected), vorher wie nachher — geändert wurde allein `docs/formate.md`. `pytest -q -rs`: 122 passed, 8 skipped, 6 deselected. `ruff check .`: sauber. `mkdocs build --strict` läuft fehlerfrei durch; mkdocs 1.6.1 war vorhanden, installiert wurde nichts. `make docs-serve` selbst blieb ungestartet — der strikte Bau beantwortet dieselbe Frage, ohne einen Port zu belegen.

**Befund, gemeldet statt geändert: die drei Abschnitte behandeln ihre Warnungen ungleich.** MarkItDown bekommt zwei volle Absätze — einen zum PDF ohne Bilder samt Begründung, warum der Dienst auch bildlose PDF warnt, einen zum leeren Ergebnis; beide ohne Zitat. Pandoc nennt seine `warnings` in einem Nebensatz und ohne Wortlaut. Docling hat jetzt drei Sätze mit wörtlichem Zitat und Zahl. Das sind drei verschiedene Formen für dieselbe Sache. Eine einheitliche Form — oder eine kurze Aufstellung „Diese Warnungen kann eine Antwort enthalten" — würde dem Leser mehr nützen als jeder einzelne Absatz für sich. Das fasst alle drei Abschnitte an und gehört deshalb in ein eigenes Ticket, nicht nebenbei erledigt.
