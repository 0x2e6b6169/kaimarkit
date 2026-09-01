---
id: 84
title: BE-32 · Die erste Umwandlung dauert doppelt so lang wie die zweite
status: done
priority: medium
created: 2026-09-01T17:28:22.990006761+02:00
updated: 2026-09-01T17:51:36.961161935+02:00
started: 2026-09-01T17:51:36.141553182+02:00
completed: 2026-09-01T17:51:36.141553182+02:00
assignee: sophie
tags:
    - backend
    - performance
class: standard
---

## Befund (01.09.2026, gemessen von akar in IN-13)

Am frischen Container, Abbildstand `6b4c3b4`, **beide Läufe nach abgeschlossenem
Vorladen**:

    erste Umwandlung    28,2 s
    zweite Umwandlung   12,0 s

Rund 16 Sekunden, die das Vorladen nicht abdeckt. `_warmup` baut seit BE-17 (#56)
beide OCR-Pipelines; der Unterschied liegt also woanders.

## Warum das zählt

Es trifft **jede erste Umwandlung nach jedem Start** — also genau den Moment, in dem
jemand das Werkzeug zum ersten Mal ausprobiert. Der Nutzer hat heute Vormittag nach
103 Sekunden gefragt, wie lange das dauern soll; ein Sechzehntel davon wäre erklärbar
gewesen, wenn wir es gewusst hätten.

Es ist außerdem der Rest einer Frage, die schon zweimal beantwortet schien: BE-17 hat
gezeigt, dass das Laden 8,5 s je Pipeline kostet und `ready` zu früh kam. Beides ist
erledigt — und die erste Umwandlung ist trotzdem doppelt so teuer.

## Eigene Dateien

- `backend/app/converters/docling.py`
- `backend/tests/test_docling.py`

## Vorgaben

**Zuerst messen, wo die Zeit hingeht — nicht raten und nicht vorladen.** Denkbar sind
Modelle, die Docling erst beim ersten echten Dokument lädt (Tabellenmodell, OCR-Netz),
Torch-Kernel, die beim ersten Aufruf übersetzt werden, oder ein Zwischenspeicher, den
erst der erste Lauf füllt. Welches davon, sagt eine Messung und keine Überlegung.

Die Aufschlüsselung gehört in die Ticketnotiz, auch wenn danach nichts gebaut wird.

**Erst wenn feststeht, wo die Zeit liegt, ist zu entscheiden, ob sich Vorladen lohnt.**
Es kann sein, dass die Antwort „nichts tun" lautet — 16 Sekunden einmal je Start sind
kein Notstand, und ein Vorladen, das den Start um 16 Sekunden verlängert, verschiebt
die Kosten nur. Das wäre ein gutes Ergebnis und kein gescheitertes Ticket.

## Prüfung

- Die Notiz nennt, wohin die 16 Sekunden gehen, mit Messwerten statt Vermutungen.
- Wird etwas geändert, sind erste und zweite Umwandlung danach erneut gemessen und
  beide Zahlen stehen in der Notiz.
- Wird nichts geändert, steht der Grund in der Notiz und das Ticket schließt trotzdem.
- `pytest -q -rs` bleibt grün, Sammelzahl in der Notiz.

[[2026-09-01]] Tue 17:50

## Wo die Zeit hingeht — gemessen, nicht vermutet

Im Abbild `kaimarkit:local` (docling 2.124.0), Fixture `tests/fixtures/tabelle.pdf`,
Zeiten je Abschnitt mit `perf_counter`, Stufen aus Doclings eigener Messung
(`settings.debug.profile_pipeline_timings`):

    Imports (docling.document_converter u.a.)   26,4 s   einmal je Prozess
    DocumentConverter(ocr=False)                 0,8 s   laedt kein Modell
    conv.initialize_pipeline(PDF)               19,3 s   Layout- und Tabellenmodell
    conv.initialize_pipeline(IMAGE)              0,0 s   dieselbe Pipeline
    danach: Umwandlung #1 15,96 s  #2 13,32 s  #3 13,95 s

Die Stufen der ersten Umwandlung *ohne* vorheriges `initialize_pipeline`:

    pipeline_total   15,85 s      layout   9,69 s      table_structure   5,98 s

**Der Befund: `DocumentConverter(...)` laedt nichts.** Der Konstruktor legt nur die
Optionen ab. Docling holt Layout- und Tabellenmodell erst, wenn das erste Dokument
dieses Formats ankommt — `_get_pipeline` baut die Pipeline verzoegert und legt sie
unter `(pipeline_class, options_hash)` ab. Der Warmlauf bezahlte also allein die
Importe, meldete `ready` und ueberliess die Modelle der ersten Anfrage. Das sind die
16 Sekunden. Kein Torch-Kernel, kein Zwischenspeicher, kein zweites OCR-Netz: das
Modellladen, an der falschen Stelle.

Das erklaert auch, warum BE-17 die zweite Pipeline in 1,3 s baute, wo die erste 8,5 s
brauchte — die 8,5 s waren die Importe, und geladen wurde beide Male nichts.

## Was geaendert wurde

`_build_pipeline` ruft jetzt `converter.initialize_pipeline(fmt)` fuer `PDF` und
`IMAGE`. Beide Formate teilen sich dasselbe `options`-Objekt und damit denselben
Options-Hash — der zweite Aufruf findet die Pipeline im Zwischenspeicher und kostet
0,00 s.

Damit wird auch `ready` wieder wahr. Das war BE-17s Anliegen, nur zur Haelfte
erreicht: Der Zustand kam nach den Importen und nicht nach den Modellen.

## Nachgemessen — gleicher Container, gleiche Bedingungen, A/B

    vorher (main)      Warmlauf 13,40 s (ready)   Umwandlungen 16,77 / 4,94 / 7,00 s
    nachher (task/84)  Warmlauf 16,57 s (ready)   Umwandlungen  3,40 / 4,39 / 3,07 s

Der Abstand zwischen erster und zweiter Umwandlung ist weg; was bleibt, ist Rauschen.
Der Warmlauf waechst hier um gut drei Sekunden, weil die Modelldateien schon im
Seitenzwischenspeicher lagen; am kalten Container kostet er entsprechend mehr. Er
laeuft im Hintergrund-Thread, `/api/health` wartet nie auf ihn, und `engine=auto`
nimmt solange die naechste Engine — die Kosten werden nicht verschoben, sondern in
die Leerlaufzeit nach dem Start gelegt.

## Prueflauf

- Neuer `slow`-Test `test_the_first_conversion_is_no_slower_than_the_second`: warmt
  ausdruecklich vor und verlangt `erste < 1,5 x zweite`. Gegenprobe am alten Stand:
  faellt mit "erste 9,5 s, zweite 3,9 s" (Faktor 2,4).
- `test_the_warmup_loads_the_models_instead_of_the_first_request` haelt die
  Vorladung ohne die Bibliothek fest.
- Der alte `assert second < first` in `test_real_docling_converts_a_table` ist weg —
  nach der Aenderung entscheidet dort das Rauschen. Der Test prueft nur noch die
  Tabelle.
- Im Abbild: `7 passed, 143 deselected` (`-m slow`).
- In der pyenv-Umgebung: **150 gesammelt, 143 ausgewaehlt, 143 bestanden, 0
  uebersprungen** (Stand vorher am selben Moment gemessen: 148/142 — die Differenz
  sind meine zwei neuen Tests). Die frueher gemeldeten 140/134 mit 8 Skips stammen
  von vor der Installation von markitdown+pandas in der geteilten Umgebung durch eine
  andere Lane.
- `ruff check .` sauber.

## Fremde Datei angefasst

`backend/tests/conftest.py`: Die Docling-Attrappe bekam `initialize_pipeline` (No-op
mit Mitschrift in `seen.initialized`). Ohne das waeren `test_docling_ocr.py` und die
Format-Tests an einer Attrappe gescheitert, die nicht mehr kann, wofuer sie steht.
Kein offenes Ticket besitzt diese Datei.
