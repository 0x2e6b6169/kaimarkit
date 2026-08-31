# Formate

Welche Dateiendung welche Engine bedient und wo die Engines sich unterscheiden,
steht hier.

## Die Matrix

Die Reihenfolge ist die Präferenz: Bei `engine=auto` bekommt die Datei die erste
Engine, die gerade bereit ist. Diese Liste steht im Code
(`backend/app/converters/registry.py`) und nicht in der Konfiguration — sie
beschreibt, was die Bibliotheken können, und das ändert sich mit den Abhängigkeiten,
nicht mit dem Deployment.

| Endung | Präferenz (erste Wahl zuerst) |
|---|---|
| `.pdf` | docling, markitdown |
| `.docx` | markitdown, docling, pandoc |
| `.epub` | pandoc, markitdown |
| `.pptx`, `.xlsx` | markitdown, docling |
| `.html`, `.htm` | markitdown, pandoc, docling |
| `.odt`, `.rtf`, `.tex`, `.rst`, `.org` | pandoc |
| `.csv`, `.json`, `.xml`, `.txt` | markitdown |
| `.png`, `.jpg`, `.jpeg`, `.tiff` | docling (mit OCR), markitdown |
| `.md`, `.markdown` | durchreichen, keine Engine |

Pandoc fehlt bei `.pdf`, weil Pandoc PDF nicht liest. Markdown reicht der Dienst
durch: Er liest die Datei und gibt sie unverändert zurück.

Was von dieser Tabelle im Betrieb übrig bleibt, meldet `GET /api/capabilities`. Eine
Engine, die nicht installiert oder noch nicht geladen ist, erscheint dort nicht.

## Auswahl und Rückfall

Eine ausdrücklich genannte Engine wird nie durch eine andere ersetzt. Kann sie das
Format nicht, antwortet der Dienst mit 400 (`engine_unsuitable`), statt stillschweigend
etwas anderes zu nehmen.

Bei `engine=auto` nimmt der Dienst die nächste Engine der Liste, wenn die erste
scheitert. Der Grund des Fehlschlags steht danach in `warnings` des Ergebnisses.
`KAIMARKIT_ENABLE_FALLBACK=false` schaltet diesen Rückfall ab.
`KAIMARKIT_DEFAULT_ENGINE=<name>` zieht eine Engine in allen Listen nach vorn,
sofern sie die Endung überhaupt bedient.

Eine Endung außerhalb der Tabelle lehnt der Dienst mit 415 (`unsupported_format`) ab.

## Docling: Modelle und OCR

Docling lädt beim Start Layout- und Tabellenmodelle in den Speicher. Das dauert
und geschieht deshalb im Hintergrund: `GET /api/health` antwortet sofort, während
Docling noch lädt. Solange gilt die Engine als `warming` — `GET /api/capabilities`
bietet sie nicht an, und `engine=auto` nimmt für ein PDF die nächste Engine der
Liste. Wer Docling ausdrücklich verlangt, wartet stattdessen, bis die Modelle da
sind.

Fehlen die Modelle oder ist die Bibliothek nicht installiert, meldet der Dienst
400 (`engine_unavailable`), sobald jemand Docling ausdrücklich verlangt. Bei
`engine=auto` bleibt Docling einfach aus der Liste.

`KAIMARKIT_OCR_ENABLED` legt fest, ob Docling gescannte Seiten und Bilder durch die
Texterkennung schickt; eine einzelne Anfrage überschreibt das mit dem Feld `ocr`.
Für jede der beiden Einstellungen hält der Dienst einen eigenen Konverter, den er
wiederverwendet — der erste Aufruf mit umgeschaltetem OCR ist deshalb langsamer als
die folgenden. Die Sprachen kommen aus `KAIMARKIT_OCR_LANGS`; ihre Kürzel müssen zu
der Texterkennung passen, die Docling benutzt.

Wo die vorgebackenen Modelle liegen, sagt `DOCLING_ARTIFACTS_PATH`. Die Variable
gehört Docling, nicht kaimarkit; das Container-Abbild setzt sie, damit zur Laufzeit
nichts aus dem Netz nachgeladen wird.
