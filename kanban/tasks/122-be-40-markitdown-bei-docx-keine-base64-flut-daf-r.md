---
id: 122
title: 'BE-40 · MarkItDown bei docx: keine base64-Flut, dafür eine Warnung'
status: done
priority: high
created: 2026-09-03T15:13:03.634213602+02:00
updated: 2026-09-07T09:58:18.718266086+02:00
started: 2026-09-07T09:56:37.085391067+02:00
completed: 2026-09-07T09:56:37.085391067+02:00
assignee: sophie
tags:
    - backend
    - gh-2
depends_on:
    - 121
class: standard
---

## Ziel

Aus der Messung in BE-38 (#117), und von sophie als das schädlichere der beiden
Verhalten benannt: **MarkItDown warnt bei docx gar nicht** und setzt stattdessen
`![](data:image/png;base64…)` ins Markdown. Bei `.docx` ist MarkItDown unter
`engine=auto` die erste Wahl — der Fall trifft also den Regelweg, nicht einen Randfall.

Zwei Schäden auf einmal. Der Nutzer erfährt nicht, dass der Inhalt des Bildes fehlt. Und
er bekommt an dessen Stelle eine base64-Zeichenkette, die sein Kontextfenster füllt. Für
ein Werkzeug, dessen Zweck es ist, prüfbaren Kontext zu **zeigen**, ist das zweite das
schwerere: Es macht das Ergebnis nicht nur unvollständig, sondern unbrauchbar.

## Eigene Dateien

- `backend/app/converters/markitdown.py` und der Test dazu

`backend/app/converters/docling.py` gehört BE-39. Falls beide Tickets an einer
gemeinsamen Datei mit Warnungstexten hängen, besitzt BE-39 sie; dieses Ticket hängt
über `depends_on` daran und läuft danach.

Nicht hier: `converters/registry.py` — dass MarkItDown bei `.docx` die erste Wahl ist,
bleibt so. Wer die Reihenfolge ändern will, meldet es; die Registry gehört BE-2.

Nicht hier: `docs/formate.md` und `docs/grenzen.md` (DOC-18). Ergibt die Arbeit, dass
dort etwas unwahr wird, melden statt ändern.

## Vorgaben

- Ein eingebettetes Bild, dessen Inhalt nicht übernommen wird, hinterlässt **keine
  base64-Zeichenkette** im Markdown. Was an seiner Stelle steht, entscheidet die
  Umsetzung — ein Platzhalter mit Dateiname, ein leeres `![]()`, gar nichts —, begründet
  in der Notiz.
- Der Fall setzt eine Warnung, und zwar mit demselben Aufbau wie in BE-39: was fehlt,
  warum, und was der Nutzer tun kann. Der Umweg ist hier: das Dokument als PDF abgeben
  und Docling mit OCR nehmen.
- Bilder, deren Inhalt MarkItDown tatsächlich übernimmt, bleiben unverändert.
- Konvention 2 hält: `markitdown` wird nur in diesem Modul importiert.

## Prüfung

- Rot vor grün: Ein Test mit dem docx-Fixture aus BE-38, das den Satz nur im
  eingebetteten Bild führt, prüft, dass im Markdown kein `data:image/` vorkommt — und
  fällt vor der Arbeit durch.
- Ein zweiter Test belegt die Warnung; ihr Wortlaut steht in richtiger Schreibung in der
  Ticketnotiz.
- Die Länge des erzeugten Markdown vor und nach der Änderung steht in der Notiz. Die
  Zahl ist der Beleg dafür, dass das Kontextfenster nicht mehr gefüllt wird.
- `pytest -q -rs` und `ruff check .` sauber; Sammelzahl und Abgewählte gemeldet.


---

## Umsetzung (sophie-44, Merge 6e06582)

### Der Wortlaut der Warnung

Bei einem Bild:

> In bild_im_dokument.docx steckt ein Bild. Sein Inhalt fehlt im Markdown. MarkItDown liest keinen Text aus Bildern. Wer ihn braucht, speichert das Dokument als PDF und lädt es mit der Engine docling und eingeschalteter Texterkennung erneut hoch.

Bei mehreren, am Beispiel von zweien:

> In seite.html stecken 2 Bilder. Ihr Inhalt fehlt im Markdown. MarkItDown liest keinen Text aus Bildern. Wer ihn braucht, speichert das Dokument als PDF und lädt es mit der Engine docling und eingeschalteter Texterkennung erneut hoch.

Vier Sätze, derselbe Aufbau wie in BE-39: was in der Vorlage steckt, was im Markdown
fehlt, warum, und was dagegen hilft. Der Umweg ist in diesem Stand begehbar und
nachgesehen statt angenommen: `PREFERENCES[".pdf"]` nennt `docling` zuerst,
`Settings.ocr_enabled` steht auf `True`, und die Enginewahl steht im Frontend als
Schaltergruppe (`EngineSelect.vue`). Die Engine ist ausdrücklich genannt, weil das
Frontend die zuletzt gewählte merkt (`rememberEngine`) — wer markitdown gewählt hat,
bekäme sonst auch aus dem PDF nichts.

### Was an die Stelle des Bildes tritt

`![Alt-Text](data:…)` wird zu `![Alt-Text]()`. Der Alt-Text ist das Einzige, was
MarkItDown aus einem Bild übernimmt, und er bleibt deshalb stehen; die leere Klammer
zeigt, dass an dieser Stelle etwas fehlt. Doclings `<!-- image -->` steht dort
absichtlich nicht: Das ist Doclings Exportformat, und beide Engines dasselbe schreiben
zu lassen behauptete eine Gleichheit, die es nicht gibt — Docling kennt keinen
Alt-Text. Ein Bild, dessen Ziel eine Adresse ist, bleibt unangetastet.

### Die Markdown-Länge — und eine widerlegte Annahme

`bild_im_dokument.docx` durch markitdown 0.1.7:

| | Zeichen |
|---|---|
| vorher | 86 |
| nachher | 62 |

Der Ticketrumpf nimmt an, die base64-Zeichenkette fülle das Kontextfenster. **Das
stimmt in diesem Stand nicht.** MarkItDown kürzt jede Data-URI selbst, solange
niemand `keep_data_uris=True` setzt — `converters/_markdownify.py:107` schneidet sie
auf `data:image/png;base64...` zurück. Im Markdown stand deshalb kein Klotz, sondern
ein Rest von 30 Zeichen. Auch die Messung in BE-38 (#117) zeigt genau diese gekürzte
Form; gelesen wurde sie als Anfang einer langen Zeichenkette.

Zum Vergleich: Mit `keep_data_uris=True` wären es 5868 Zeichen statt 86 gewesen. Die
Gefahr ist also real, aber von der Bibliothek schon abgewendet.

Damit bleibt von den zwei Schäden im Ziel **einer**, und es ist der erste: Der Nutzer
erfuhr nicht, dass der Inhalt des Bildes fehlt. Dazu kam ein unlesbarer Rest an einer
Stelle, an der ein Werkzeug für prüfbaren Kontext nichts Unlesbares stehen lassen
sollte. Beides ist behoben.

### Prüfung

- **Rot vor grün**, die drei neuen Tests gegen die alte `markitdown.py`:
  `3 failed, 8 passed` — `assert "data:image/" not in result.markdown` scheitert am
  docx-Fixture und an der HTML-Gegenprobe, `assert result.warnings == [_BILDWARNUNG]`
  scheitert mit `[] == [...]`. Danach `11 passed`.
- Drei Tests in `tests/test_markitdown.py`: keine Data-URI mehr, der Wortlaut der
  Warnung, und eine Gegenprobe mit Alt-Text, Plural und einem Bild mit Adresse.
- `pytest -q -rs`: **217 gesammelt, 206 ausgewählt, 206 bestanden, 11 abgewählt**
  (`-m "not slow"`), 0 übersprungen. `ruff check .`: All checks passed.

### Befunde für den PO

1. **Die Annahme im Ticketrumpf gehört berichtigt** (siehe oben): MarkItDown 0.1.7
   kürzt Data-URIs selbst. Wer den Rumpf später liest, soll sehen, dass die Zahl
   einmal anders geschätzt war.
2. **Die Doku kennt die neue Warnung nicht.** Unwahr wird durch diesen Merge nichts —
   `docs/formate.md` („In `.docx`, `.html` und `.epub` steht von einem Bild nur der
   Alt-Text im Markdown, nicht sein Inhalt.") wird durch die Änderung sogar erst
   richtig, denn bis eben stand dort auch noch eine Data-URI. Es fehlt aber der Satz,
   dass der Dienst das jetzt meldet. `docs/formate.md` und `docs/grenzen.md` gehören
   DOC-18 — gemeldet statt geändert.

## Berichtigung einer Annahme im Ziel oben (2026-09-07, sophie)

Das Ziel behauptete zwei Schäden: eine base64-Flut und Schweigen darüber. **Die
base64-Flut gab es in diesem Stand nicht.** MarkItDown kürzt jede Data-URI selbst
(`converters/_markdownify.py:107`), solange niemand `keep_data_uris=True` setzt; die
BE-38-Messung zeigte einen gekürzten Rest von 30 Zeichen, gelesen als Anfang einer
langen Kette. Mit `keep_data_uris=True` wären es 5868 statt 86 Zeichen Markdown-Länge
gewesen. Von den zwei genannten Schäden blieb also einer: das Schweigen. Das Ticket
war trotzdem richtig — nur aus dem anderen der beiden Gründe.
