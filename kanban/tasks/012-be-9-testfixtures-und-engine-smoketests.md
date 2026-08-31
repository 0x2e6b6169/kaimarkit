---
id: 12
title: BE-9 · Testfixtures und Engine-Smoketests
status: done
priority: medium
created: 2026-08-31T10:20:18.427682548+02:00
updated: 2026-08-31T11:23:26.367657867+02:00
started: 2026-08-31T11:22:55.939746058+02:00
completed: 2026-08-31T11:22:55.939746058+02:00
assignee: sophie
tags:
    - backend
depends_on:
    - 6
    - 7
    - 8
class: standard
---

## Ziel

Belegen, dass jede Engine mit einer echten Datei arbeitet.

## Eigene Dateien

- `backend/tests/fixtures/*`
- `backend/tests/test_converters.py`
- `backend/tests/test_api.py`

## Vorgaben

- Je eine moeglichst kleine Beispieldatei pro Format: pdf, docx, epub, pptx, xlsx,
  html, csv, odt, png. Selbst erzeugt, keine fremden Inhalte.
- `test_converters.py` prueft je Engine: Ergebnis ist nicht leer, enthaelt einen
  erwarteten Textbaustein, `engine` stimmt.
- Docling-Tests mit `@pytest.mark.slow` versehen und in `pyproject.toml` aus dem
  Standardlauf ausschliessen - sie brauchen die Modelle und dauern.
- `test_api.py` deckt die Fehlerpfade ab: 413, 415, 400 bei ungeeigneter Engine.

## Pruefung

`pytest -q` laeuft ohne Docling-Modelle durch. `pytest -q -m slow` laeuft mit
Modellen durch.


## Ergebnis (sophie-09)

Neun selbst erzeugte Beispieldateien in `backend/tests/fixtures/`: tabelle.pdf,
bericht.docx, buch.epub, folien.pptx, tabelle.xlsx, seite.html, liste.csv,
text.odt, bild.png. Jede traegt den Baustein `Kaimarkit Fixture`.
`tests/fixtures/build_fixtures.py` baut sie neu und erklaert im Kopf, wie: OOXML
und ODF als von Hand geschriebene ZIP-Archive, das PDF als von Hand gesetzter
Inhaltsstrom mit gezeichneter Tabelle (Standardbibliothek); nur tabelle.xlsx
braucht openpyxl und bild.png braucht Pillow.

BE-4 ist bedient: `tabelle.pdf` liegt unter dem erwarteten Namen und enthaelt eine
Tabelle mit Rahmenlinien. `test_docling.py` blieb unangetastet.

`test_converters.py` fuehrt jede Engine ueber die Registry an eine echte Datei und
prueft Baustein, Enginenamen und nicht leeres Ergebnis — MarkItDown ueber sechs
Formate, Pandoc ueber drei, Docling ueber pdf und png (Marke `slow`). Dazu der
Auto-Weg fuer csv und odt und der Durchreichweg fuer Markdown.

`test_api.py` um fuenf Faelle ergaenzt, ohne die 13 aus BE-7 anzufassen: 400 fuer
eine nicht ladbare und fuer eine unbekannte Engine, 415 fuer eine Datei ohne
Endung, und zweimal die Zusicherung, dass nach einer Konversion keine temporaere
Datei zurueckbleibt — im Erfolgs- wie im Fehlerfall.

`pyproject.toml` nimmt `addopts = ["-m", "not slow"]` auf; `pytest -m slow` holt
die ausgeblendeten Tests zurueck. `.gitattributes` markiert das Fixtureverzeichnis
als binary, damit die xref-Offsets des unkomprimierten PDF keine
Zeilenendenwandlung erleben. `docs/entwicklung.md` bekam zwei Abschnitte: wie man
die Suite faehrt und was die Fixtures sind.

Stand auf main nach dem Merge: `pytest -q` 99 passed, 1 skipped, 3 deselected;
`pytest -q -m slow` 3 skipped; `ruff check .` sauber.

**Ungeprueft geblieben:** Docling fehlt in der geteilten Umgebung, also
uebersprangen sich alle drei `slow`-Tests. Ob das PDF wirklich als
Markdown-Tabelle herauskommt und ob die Texterkennung das PNG liest, zeigt erst
INT-2 im Container. Ebenso uebersprungen: der MarkItDown-Smoketest fuer xlsx —
dafuer fehlt pandas aus `markitdown[all]`. Die Zuordnung Format -> Zusatzpaket
steht in `MARKITDOWN_EXTRAS` in test_converters.py.
