# Entwicklung

Wie das Projekt aufgebaut ist, wie man eine weitere Engine ergänzt und wie das
Board die Arbeit verteilt.

## Tests

Die Suite läuft aus `backend/` heraus, in der pyenv-Umgebung `claude-code`:

```bash
pytest -q            # der Standardlauf, ohne Docling
pytest -q -m slow    # nur die Tests, die die Docling-Modelle brauchen
```

Der Standardlauf blendet die Marke `slow` aus; das steht in `backend/pyproject.toml`
und gilt damit auch für jeden Aufruf ohne Argumente. Wer `-m slow` angibt,
überschreibt die Einstellung und bekommt genau die ausgeblendeten Tests. Sie laden
die Modelle und dauern deshalb; ohne Docling überspringen sie sich.

Die meisten Enginetests arbeiten mit Attrappen und prüfen den Adapter. Die
Smoketests in `backend/tests/test_converters.py` tun das Gegenteil: Sie lassen jede
Engine eine echte Datei lesen und prüfen, dass der erwartete Textbaustein im
Markdown steht und die richtige Engine gearbeitet hat.

## Beispieldateien

Unter `backend/tests/fixtures/` liegt je eine möglichst kleine Datei für PDF, docx,
epub, pptx, xlsx, HTML, CSV, odt und PNG. Alle enthalten den Baustein
`Kaimarkit Fixture`, auf den sich die Smoketests verlassen.

Die Dateien sind selbst erzeugt, keine fremden Inhalte. `build_fixtures.py` im selben
Verzeichnis baut sie neu:

```bash
python tests/fixtures/build_fixtures.py
```

Sieben der neun Dateien entstehen mit der Standardbibliothek — die OOXML- und
ODF-Formate sind von Hand geschriebene ZIP-Archive, das PDF ein von Hand gesetzter
Inhaltsstrom mit gezeichneter Tabelle. Nur `tabelle.xlsx` braucht openpyxl und
`bild.png` braucht Pillow; beide Pakete kommen mit `markitdown[all]`.

Fehlt ein Paket aus `markitdown[all]`, überspringt sich der betroffene Smoketest,
statt zu scheitern — im Skelett ohne Extras bleibt so nur die Prüfung übrig, die
dort auch laufen kann.
