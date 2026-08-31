---
id: 48
title: BE-15 · Fehlermeldungen nennen den internen Tempfile-Pfad
status: backlog
priority: low
created: 2026-08-31T17:08:52.676542507+02:00
updated: 2026-08-31T17:08:52.676542507+02:00
assignee: sophie
tags:
    - backend
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
