---
id: 48
title: BE-15 · Fehlermeldungen nennen den internen Tempfile-Pfad
status: in-progress
priority: low
created: 2026-08-31T17:08:52.676542507+02:00
updated: 2026-09-01T13:15:55.054233721+02:00
assignee: sophie
tags:
    - backend
depends_on:
    - 58
claimed_by: sophie-26
claimed_at: 2026-09-01T13:15:55.054233721+02:00
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
