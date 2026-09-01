---
id: 60
title: BE-19 · MarkItDown verschweigt, was es an Bildern weglaesst
status: todo
priority: medium
created: 2026-09-01T11:23:01.248130894+02:00
updated: 2026-09-01T12:10:22.698034118+02:00
started: 2026-09-01T12:03:27.525130027+02:00
assignee: sophie
tags:
    - backend
    - bug
blocked: true
block_reason: markitdown hinterlaesst keine zaehlbare Marke
class: standard
---

## Befund (01.09.2026, Frage des Nutzers waehrend der Abnahme)

`docling` sagt jetzt, wenn Inhalt fehlt: "Docling hat in X 3 Bilder durch Platzhalter
ersetzt." `markitdown` sagt nichts — bei derselben Datei, mit demselben Verlust.

`backend/app/converters/markitdown.py:1-7` haelt die Entscheidung fest: Ein
LLM-Client wird bewusst nicht gesetzt, "Bilder landen dadurch nur als Alt-Text im
Markdown, und genau das ist die gewuenschte Platzhalter-Behandlung."

## Die Annahme, die dahintersteckt

BE-14 (#47) hat markitdown ausdruecklich ausgenommen, mit dieser Begruendung: "Es
setzt den Alt-Text ein ... Ein Alt-Text ist kein leerer Platzhalter, deshalb steht
hier nur Docling."

Das stimmt fuer `.docx`, `.html` und `.epub` — dort steht ein Alt-Text im Dokument.
**Fuer PDF stimmt es nicht.** Ein PDF fuehrt keine Alt-Texte; wer dort ein Bild
weglaesst, laesst es ersatzlos weg. Und PDF ist das Format, in dem markitdown als
schnelle Alternative zu docling ueberhaupt in Frage kommt.

Die Entscheidung wurde also unter einer Annahme getroffen, die im wichtigsten Fall
nicht zutrifft.

## Warum das mehr ist als eine Ungleichheit

Wer zwischen den Engines waehlt, waehlt heute nebenbei mit, ob er von fehlendem
Inhalt erfaehrt. Das ist die eine Auskunft, wegen der es dieses Projekt gibt.

## Eigene Dateien

- `backend/app/converters/markitdown.py`
- `backend/tests/test_markitdown.py`

## Vorgaben

Erst messen, dann bauen: Was liefert markitdown fuer ein PDF mit Bildern
tatsaechlich — eine leere Bildmarke, gar nichts, einen Alt-Text? Der beobachtete
Wortlaut gehoert in die Ticketnotiz.

Danach eine Warnung nach dem Muster von `_placeholder_warnings()` in `docling.py`,
mit Zahl und Mehrzahlform. Zeigt die Messung, dass markitdown Bilder ersatzlos
weglaesst, ohne eine Marke zu hinterlassen, gehoert das gemeldet und neu geschnitten
— dann ist es kein Zaehlen mehr, sondern ein Vergleich.

## Pruefung

- Ein PDF mit Bildern durch `markitdown` liefert eine nichtleere `warnings`-Liste.
- Gegenprobe: Ein PDF ohne Bilder liefert weiterhin `warnings: []`.
- `pytest -q` bleibt gruen.

## Zurueckgestellt

Vom Nutzer zurueckgestellt, bis die Abnahme abgeschlossen ist (01.09.2026).

[[2026-09-01]] Tue 12:06
MESSUNG (markitdown 0.1.7, pdfminer.six 20260107, pdfplumber), zwei unabhaengig gebaute PDFs:
- Handgebautes PDF, eine Textzeile plus zwei Image-XObjects -> markdown == 'Bericht mit Bildern\n\n'. Dasselbe PDF ohne die Bilder liefert Zeichen fuer Zeichen dasselbe.
- PIL-PDF, das nur aus einem Bild besteht -> markdown == '' (leer).

Beobachteter Wortlaut fuer ein Bild: keiner. Keine Bildmarke, kein Alt-Text, kein Kommentar. Die Bilder verschwinden spurlos, das Ergebnis unterscheidet sich nicht von dem einer Vorlage ohne Bilder.

Ursache in der Bibliothek: markitdown/converters/_pdf_converter.py zieht ausschliesslich Text (pdfplumber page.extract_text, sonst pdfminer.high_level.extract_text). Bilder kommen dort nicht vor.

Zaehlen nach dem Muster von _placeholder_warnings() entfaellt damit. Noetig waere ein Vergleich Vorlage/Ergebnis: pdfplumber -- markitdowns eigene Abhaengigkeit -- sieht die Bilder sehr wohl (page.images ergab 2 / 0 / 1 fuer die drei Messdateien). Die Warnung muesste also die Vorlage oeffnen und dort zaehlen, statt eine Marke im Ergebnis zu zaehlen.

NEU SCHNEIDEN, weil das drei Fragen aufwirft, die #60 nicht stellt: pdfplumber als direkte Abhaengigkeit des Adapters; je Format verschiedene Antwort (docx/epub/html fuehren Alt-Texte, PDF nicht -- die Warnung darf nur fuer .pdf gelten); und ob die Zahl aus der Vorlage ueberhaupt zur Zahl der verlorenen Bilder passt (Hintergrundgrafiken, Trennlinien als Bild).

Nichts geaendert, kein Commit, Branch und Worktree wieder entfernt.

NEBENBEFUND, schon vor diesem Ticket falsch, deshalb nur gemeldet: markitdown.py Zeile 1-7, docs/formate.md Zeile 74 und docs/grenzen.md Zeile 66 behaupten, Bilder erschienen bei MarkItDown als Alt-Text. Fuer PDF stimmt das nicht.

[[2026-09-01]] Tue 12:08
Zurueck in den Ideenspeicher, bis der Nutzer ueber den Zuschnitt entschieden hat. Die Uebergabe war richtig: Der zweite der beiden Faelle aus dem Ticketrumpf ist eingetreten, und er verlangt einen anderen Schnitt, kein Weiterbauen.

**Eine Korrektur an sophies Einordnung, geprueft im laufenden Container:** Der Vergleich braucht **keine neue Abhaengigkeit**. `pdfplumber 0.11.10` liegt bereits im Abbild und im venv — es ist ueber markitdown oder docling mitgekommen. Auch `pdfminer.six 20260107` ist da; `pypdf` fehlt.

Damit lautet die Produktfrage anders als gedacht. Nicht "eine neue Bibliothek fuer eine Warnung", sondern: eine bereits vorhandene Bibliothek ausdruecklich in `pyproject.toml` aufnehmen — sich auf eine mitgeschleppte Abhaengigkeit zu verlassen ist bruechig — und ein zweites Lesen des PDF in Kauf nehmen. Was das zweite Lesen kostet, ist ungemessen und gehoert vor die Entscheidung.

[[2026-09-01]] Tue 12:10
## Neuer Zuschnitt (01.09.2026) — ersetzt Ziel, Vorgaben und Pruefung oben

Entscheidung des Nutzers, woertlich: "Explizit machen, dass Bildinformationen bei
markitdown fehlen. Ich brauche eine pragmatische, keine akademisch perfekte
Loesung."

Damit faellt der Vergleich von Vorlage und Ergebnis weg. Kein zweites Lesen des PDF,
kein `pdfplumber`, keine Zahl. Gebaut wird die **Aussage**, nicht die Messung.

### Ziel

Wer ein PDF durch markitdown schickt, erfaehrt, dass Bilder darin nicht uebernommen
werden. Ob die Vorlage welche enthielt, sagt kaimarkit nicht — und behauptet es auch
nicht.

### Eigene Dateien

- `backend/app/converters/markitdown.py` (einschliesslich Modul-Docstring)
- `backend/tests/test_markitdown.py`
- `docs/formate.md` (Abschnitt "MarkItDown")
- `docs/grenzen.md` (die betroffene Zeile)

**#62 (BE-20) ist hier aufgegangen und geschlossen.** Die drei falschen Stellen
gehoeren zur selben Aussage und werden im selben Merge berichtigt, statt zwei Tickets
auf dieselbe Datei zu setzen.

### Vorgaben

Wandelt markitdown ein PDF, legt der Adapter eine feste Warnung dazu. Sinngemaess:
"MarkItDown uebernimmt keine Bilder aus PDF. Enthielt die Vorlage Bilder, fehlt ihr
Inhalt hier." Der Wortlaut gehoert in die deutsche Prosa des Projekts.

Nur fuer PDF. Bei `.docx`, `.html` und `.epub` setzt markitdown den Alt-Text ein —
dort ist die Aussage unwahr.

Bewusst in Kauf genommen: Ein PDF ohne Bilder bekommt die Warnung auch. Deshalb sagt
sie, was die Engine tut, und nicht, was in der Datei stand. Das ist der Preis dafuer,
nicht zweimal zu lesen — und er ist es wert.

Dieselbe Aussage gehoert an die drei Stellen, die heute das Gegenteil behaupten:
Modul-Docstring, `docs/formate.md:74`, `docs/grenzen.md:66`. Gemessen wurde das in
diesem Ticket bereits (siehe Notiz oben): Ein PDF mit zwei Bildern liefert Zeichen
fuer Zeichen dasselbe Markdown wie dasselbe PDF ohne.

### Pruefung

- Ein PDF durch `markitdown` liefert eine nichtleere `warnings`-Liste mit dieser
  einen Warnung.
- Gegenprobe: Eine `.docx` durch `markitdown` liefert sie **nicht**.
- Keine der drei Doku-/Kommentarstellen behauptet noch einen Alt-Text fuer PDF.
- `pytest -q` bleibt gruen; ohne die Aenderung faellt der neue Test durch.
