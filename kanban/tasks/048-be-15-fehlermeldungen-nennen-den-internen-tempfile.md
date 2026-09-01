---
id: 48
title: BE-15 · Fehlermeldungen nennen den internen Tempfile-Pfad
status: done
priority: low
created: 2026-08-31T17:08:52.676542507+02:00
updated: 2026-09-01T14:09:28.90266875+02:00
started: 2026-09-01T13:23:54.726548822+02:00
completed: 2026-09-01T13:23:54.726548822+02:00
assignee: sophie
tags:
    - backend
depends_on:
    - 58
class: standard
---

## Ziel

Eine Fehlermeldung sagt, was schiefging, nicht wo im Container die Datei kurz lag.

## Befund (belegt in INT-2, 31.08.2026)

```
POST /api/convert, engine=docling, beschaedigtes PDF -> 500
{"detail":"Docling ist an kaputt.pdf gescheitert: Conversion failed for:
  /tmp/tmpkxfozixp/kaputt.pdf with status: failure. Errors: docling-parse could
  not load document 46ef4e69... : Failed to load document with key
  key=/tmp/tmpkxfozixp/kaputt.pdf","code":"conversion_failed"}
```

Dieselbe Meldung landet im Stapel in `_errors.txt` und im Browser in der Zeile der
Datei — dort steht sie also vor den Augen dessen, der die Datei hochgeladen hat.

`contracts/api.md` verlangt fuer `error` eine "lesbare Meldung, kein Stacktrace".
Ein Stacktrace ist das nicht. Der Pfad und der Hash helfen aber niemandem, der die
Meldung liest, und der Pfad existiert nach dem `finally` ohnehin nicht mehr
(Konvention 5).

## Eigene Dateien

- `backend/app/errors.py` oder die Stelle im jeweiligen Adapter, an der die
  Ausnahme in `ConversionError` uebersetzt wird
- `backend/tests/test_converters.py`

## Vorgaben

Die Uebersetzung kuerzt die Meldung der Bibliothek auf ihren lesbaren Teil. Der
vollstaendige Wortlaut gehoert ins Protokoll, nicht in die Antwort. Keine neue
Konfiguration dafuer.

## Pruefung

- Ein beschaedigtes PDF ergibt eine `detail`-Meldung ohne `/tmp/`.
- Gegenprobe: Die Meldung nennt weiterhin den Dateinamen und den Grund, ist also
  nicht auf "Konvertierung gescheitert" eingedampft.
- Im Protokoll des Dienstes steht der ungekuerzte Wortlaut.

[[2026-09-01]] Tue 13:15
Hängt an #58, auf Meldung von sophie (01.09.2026) — und der Grund ist wichtiger als die Wartezeit.

Die Eigenen Dateien nennen `errors.py` **oder** die Übersetzungsstelle im Adapter. Der belegte Befund ist eine Docling-Meldung; die Übersetzungsstelle dafür liegt in `converters/docling.py`, und die gehört gerade #58. Bedingtes Eigentum, also kollisionsfrei erst danach.

**Der Ausweg, den ich nicht will:** den Subagenten auf `errors.py` festlegen und den Adapter verbieten. Dann entschiede die Verfügbarkeit einer Datei über den Entwurf statt die Sache. Eine gemeinsame Kürzung in `errors.py` ist wahrscheinlich ohnehin das Bessere — sie gilt dann für alle drei Engines gleich statt dreimal verschieden —, aber das soll aus der Betrachtung folgen und nicht daraus, dass `docling.py` gerade belegt war. Der Satz stammt von sophie und trifft es genauer, als eine Regel es könnte.

**Zur Prüfung, zweiter Hinweis von sophie:** Sie verlangt, dass im Protokoll des Dienstes der ungekürzte Wortlaut steht. Das ist eine Aussage über `log.*`-Aufrufe, und über deren Sprache ist mit #69 (PROC-7) noch nicht entschieden. Kein Hindernis — der Wortlaut der Bibliothek ist ohnehin englisch. Aber wer hier eine Protokollzeile **neu** schreibt, schreibt sie in einer Sprache, die zur Wahl steht: dann die Form der Nachbarzeilen übernehmen und nichts Neues festlegen. #69 entscheidet es für alle auf einmal.

[[2026-09-01]] Tue 13:23
Gekuerzt wird zentral in errors.py, in ConversionError.__init__ — nicht je Adapter.

Der Grund ist der Befund selbst: Alle drei Adapter bauen ihre Meldung nach demselben Muster (eigener deutscher Satz mit Dateiname, dann der Wortlaut der Bibliothek), und den Pfad schleppt jede Bibliothek auf ihre eigene Weise mit — Docling zweimal im selben Satz, Pandoc ueber stderr, MarkItDown im OSError. Eine Kuerzung je Adapter waere dreimal dieselbe Regel und faenge trotzdem nicht alles: Auch der Durchreicher der Registry (_Passthrough, 'Datei nicht lesbar: [Errno 13] ... /tmp/...') und die Rueckfallwarnung in convert_with_fallback, die aus exc.detail gebaut wird, nennen den Pfad. Beide liegen ausserhalb der Adapter. Am Konstruktor der Ausnahme kommt jede dieser Stellen vorbei, auch die Engine, an die heute niemand denkt.

Was passiert: _PATH ersetzt jeden absoluten Pfad mit mindestens einem Verzeichnis durch seinen letzten Bestandteil. Aus 'Conversion failed for: /tmp/tmpkxfozixp/kaputt.pdf with status: failure. Errors: docling-parse could not load document ...' wird 'Conversion failed for: kaputt.pdf with status: failure. Errors: docling-parse ...'. Der Grund bleibt Wort fuer Wort stehen; nur das Verzeichnis faellt weg. URLs bleiben unangetastet (Lookbehind gegen ':' und '/'), ein einzelner Schraegstrich wie in 'ein/aus' ebenfalls (mindestens zwei Bestandteile verlangt), und ein Leerzeichen im Dateinamen beendet zwar den Treffer frueh, laesst den Namen im Text aber vollstaendig stehen.

Der ungekuerzte Wortlaut steht in ConversionError.raw_detail und geht einmal per log.warning ins Protokoll, sobald er sich vom gekuerzten unterscheidet. Der Konstruktor ist dafuer die einzige sichere Stelle: Der Stapel faengt seine Fehler in _convert_entry selbst ab, sie erreichen den Ausnahmebehandler nie. Die Protokollzeile folgt der Form der Nachbarzeilen in docling.py (deutsch, ohne Umlaute) und legt nichts Neues fest — PROC-7 entscheidet das.

Nicht angefasst: der Hash ('could not load document 46ef4e69...'). Die Pruefung nennt nur den Pfad, und eine generische Regel gegen lange Hex-Ketten frisst am Ende auch Fehlercodes und laesst ' : ' ohne Bezug stehen. Wer den Hash auch weg will, braucht ein eigenes Ticket mit einer Aussage darueber, was ein Bezeichner in einer Meldung ueberhaupt soll. Keine neue Konfiguration.

Rot vor gruen: tests/test_docling.py::test_a_failure_names_the_file_but_not_its_path scheitert gegen den unveraenderten Code mit AssertionError — '/tmp/pytest-of-kai/pytest-28/test_a_failure_names_the_file_0' steht im detail. Danach gruen.

Sammelzahl: 125/131 vorher, 137/143 nachher (+11 in tests/test_errors.py, +1 in tests/test_docling.py). pytest -q -rs: 137 passed, 6 deselected. ruff check .: All checks passed.

Nicht belegt und offen: der Weg durch den echten Container mit echtem Docling. Docling ist in der geteilten pyenv-Umgebung nicht installiert, der Adaptertest arbeitet deshalb mit dem Wortlaut aus dem INT-2-Lauf statt mit einem echten Docling-Fehlschlag. Im Container zu pruefen, nicht als bestanden gemeldet.

docs/ und contracts/api.md unveraendert: contracts/api.md verlangt fuer error bereits eine 'lesbare Meldung, kein Stacktrace' — die Aenderung stellt das her, statt etwas anderes zu versprechen. Der Dreiklang ist nicht beruehrt, models.py und types.ts bleiben gleich.

[[2026-09-01]] Tue 13:25
Entscheidung des PO zur gemeldeten Abweichung (01.09.2026): **Der Hash bleibt. Kein Folgeticket.**

Der Rumpf sagte „Der Pfad und der Hash helfen aber niemandem" — das war zu pauschal, und der Subagent hat den Unterschied gesehen, den ich übersehen hatte. Der Pfad war unserer: Wir reichen ihn in die Bibliothek hinein, also können wir ihn auch wieder herausnehmen. Der Hash steht im Wortlaut der Bibliothek selbst (`could not load document 46ef4e69…`) und bezeichnet dort ein Objekt.

Ihn zu entfernen hieße, fremde Prosa umzuschreiben statt eigene zu kürzen. Die vorgeschlagene generische Regel gegen lange Hex-Ketten träfe außerdem Fehlercodes mit und ließe ein `: ` ohne Bezug stehen — der Subagent nennt beides. Und „could not load document" ohne Bezeichner sagt weniger als mit: Im Protokoll ist er der einzige Anhalt, welches Objekt gescheitert ist.

Konvention 3 verlangt, dass jede Engine ihre Ausnahmen übersetzt. Sie verlangt nicht, dass wir die Sätze der Bibliothek neu schreiben.

Damit ist die Prüfung dieses Tickets nicht zu schwach gewesen, sondern genauer als seine Vorgabe.

**Gemessen: kein Rauschen — und die Annahme im Nachtrag stimmte nicht** (IN-12,
akar-26, 01.09.2026, gegen den laufenden Container `kaimarkit:local` aus `bbf7180`).

Zwei Staepel an `POST /api/convert/batch`, dazwischen die Zeilen des Containerlogs
gezaehlt.

*Stapel 1 — fuenf beschaedigte PDFs an Docling.* Alle fuenf scheiterten
(`status: "failed"`), 26 neue Protokollzeilen. Davon:

| Herkunft | Zeilen | je Datei |
|---|---|---|
| `app.errors` (die Zeile aus BE-15) | 5 | 1 |
| `docling.*` (fremde Bibliothek) | 20 | 4 |
| Zugriffsprotokoll von uvicorn | 1 | — |

**Eine Zeile je fehlgeschlagener Datei**, und sie ist eine von 26. Docling selbst
schreibt zu jeder Datei viermal so viel, darunter ohnehin schon den vollen Pfad:
`WARNING:docling.document_converter:Input document /tmp/tmpwvw4ceqh/kaputt1.pdf is not
valid.` Wer diesen Stapel im Log ansieht, findet unsere Zeile nicht in einer Flut,
sondern zwischen vier fremden.

*Stapel 2 — drei Dateien mit unbekannter Endung `.xyz`.* Alle drei scheiterten
(`Fuer .xyz gibt es keine Engine.`), **null** Zeilen aus `app.errors`; die einzige
neue Zeile war das Zugriffsprotokoll.

Damit ist die Voraussetzung des Nachtrags widerlegt: `ConversionError.__init__`
schreibt **nicht** bei jeder Erzeugung. Die Zeile haengt an einer Bedingung —
`backend/app/errors.py:77-78` in `bbf7180`:

    if self.detail != detail:
        log.warning("Fehlermeldung gekuerzt. Ungekuerzt: %s", detail)

Sie faellt nur, wenn `shorten()` tatsaechlich etwas gekuerzt hat, also wenn ein Pfad
in der Meldung stand. `UnsupportedFormat`, `TooManyFiles`, `FileTooLarge` und jede
andere Ausnahme ohne Pfad im Wortlaut schreiben nichts — Stapel 2 zeigt das.

**Bewertung, nicht weiter, als die Zahl hergibt:** Bei 1 Zeile je Datei und nur dort,
wo ohnehin ein Pfad verloren ginge, entsteht kein Rauschen. Kein Folgeticket
vorgeschlagen. Was den Log eines Fehlerstapels fuellt, ist Doclings eigene
Gespraechigkeit, nicht unsere Zeile — wer daran etwas will, braucht ein Ticket ueber
den Log-Level fremder Bibliotheken, nicht ueber `errors.py`.

[[2026-09-01]] Tue 14:09
**Berichtigung meines Nachtrags (01.09.2026, belegt von akar in #76).** Ich hatte geschrieben, „**jede** erzeugte `ConversionError` schreibt eine Zeile". Das stimmt nicht.

`backend/app/errors.py:77-78` schreibt unter `if self.detail != detail:` — also nur, wenn `shorten()` tatsächlich einen Pfad entfernt hat. Gegenprobe gefahren, nicht erschlossen: drei Dateien mit unbekannter Endung, alle drei `failed`, **null** Zeilen aus `app.errors`.

**Die Rauschfrage ist damit beantwortet, und die Antwort zeigt woandershin.** Fünf beschädigte PDFs erzeugen 26 neue Logzeilen: 5 aus `app.errors` — eine je fehlgeschlagener Datei —, 20 aus Docling selbst (vier je Datei, samt vollem Pfad) und eine Zugriffszeile. Das Verhältnis ist vier zu eins gegen Docling.

Wer den Log eines Fehlerstapels leiser will, muss an Doclings Log-Level, nicht an `errors.py`. Kein Folgeticket.

Bemerkenswert an der Messung: Die Frage war „erzeugt das Rauschen?", die Antwort lautet „ja, aber nicht dort". Ohne die Aufschlüsselung wäre die Gesamtzahl 26 hängengeblieben und hätte auf `errors.py` gezeigt — auf die Stelle, die als einzige im Verdacht stand.
