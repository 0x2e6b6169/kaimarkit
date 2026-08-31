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

## MarkItDown

MarkItDown kommt ohne Modelle und ohne OCR aus und ist deshalb die schnelle Engine.
Einen LLM-Client setzt der Dienst bewusst nicht ein: Bilder erscheinen im Markdown
nur als Alt-Text, nicht als beschriebener Inhalt.

Findet MarkItDown in einer Datei keinen Text — bei einem gescannten PDF etwa —, ist
das kein Fehler. Das Ergebnis bleibt leer und die Antwort nennt den Grund in
`warnings`. Wer aus solchen Dateien Text braucht, wählt Docling mit OCR.
