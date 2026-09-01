"""Smoketests: jede Engine an einer echten Datei.

Die uebrigen Enginetests arbeiten mit Attrappen und pruefen den Adapter. Hier geht
es um das Gegenteil — die Bibliothek liest wirklich eine Datei, und dabei kommt
Markdown heraus, in dem der erwartete Textbaustein steht.

Die Beispieldateien liegen in ``fixtures/`` und stammen aus
``fixtures/build_fixtures.py``. Jede von ihnen enthaelt den Baustein ``MARKER``.

Der Weg fuehrt immer ueber die Registry, nie an ihr vorbei: Die Tests importieren
weder ``markitdown`` noch ``docling`` und rufen kein ``pandoc`` auf.
"""

from __future__ import annotations

import importlib.util
import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest

from app.config import get_settings
from app.converters import registry
from app.converters.base import ConvertOptions
from app.converters.registry import convert_with_fallback, select
from app.errors import EngineUnavailable

FIXTURES = Path(__file__).parent / "fixtures"

#: Der Baustein, den jede Beispieldatei enthaelt.
MARKER = "Kaimarkit Fixture"

#: Alle neun Beispieldateien, in der Reihenfolge der Formate aus dem Ticket.
SAMPLES = (
    "tabelle.pdf",
    "bericht.docx",
    "buch.epub",
    "folien.pptx",
    "tabelle.xlsx",
    "seite.html",
    "liste.csv",
    "text.odt",
    "bild.png",
)

#: Was MarkItDown je Format zusaetzlich braucht.
#:
#: ``markitdown[all]`` bringt diese Pakete mit. Wer nur den Kern installiert hat,
#: bekommt hier eine uebersprungene Pruefung statt eines Fehlschlags.
MARKITDOWN_EXTRAS = {".xlsx": "pandas", ".pdf": "pdfminer"}

needs_pandoc = pytest.mark.skipif(
    shutil.which("pandoc") is None, reason="Pandoc liegt nicht im PATH"
)
needs_docling = pytest.mark.skipif(
    importlib.util.find_spec("docling") is None, reason="docling ist nicht installiert"
)


@pytest.fixture(autouse=True)
def fresh_settings() -> Iterator[None]:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def convert(name: str, engine: str, *, ocr: bool | None = None) -> tuple[str, str]:
    """Wandelt eine Beispieldatei mit einer ausdruecklich genannten Engine."""
    sample = FIXTURES / name
    converter = select(sample.suffix, engine)
    result = converter.convert(sample, ConvertOptions(engine=engine, ocr=ocr))
    return result.markdown, result.engine


def skip_without_extra(name: str) -> None:
    extra = MARKITDOWN_EXTRAS.get(Path(name).suffix)
    if extra is not None and importlib.util.find_spec(extra) is None:
        pytest.skip(f"MarkItDown braucht fuer {Path(name).suffix} das Paket {extra}")


@pytest.mark.parametrize("name", SAMPLES)
def test_jede_beispieldatei_liegt_bereit(name: str) -> None:
    """Neun Formate, alle vorhanden und klein genug, um im Repo zu stehen."""
    sample = FIXTURES / name
    assert sample.exists(), f"{name} fehlt — tests/fixtures/build_fixtures.py baut sie neu"
    assert 0 < sample.stat().st_size < 32 * 1024


@pytest.mark.parametrize(
    "name", ["bericht.docx", "buch.epub", "folien.pptx", "seite.html", "liste.csv", "tabelle.xlsx"]
)
def test_markitdown_findet_den_baustein(name: str) -> None:
    skip_without_extra(name)
    try:
        markdown, engine = convert(name, "markitdown")
    except EngineUnavailable as exc:
        pytest.skip(str(exc))
    assert engine == "markitdown"
    assert markdown.strip()
    assert MARKER in markdown


@needs_pandoc
@pytest.mark.parametrize("name", ["buch.epub", "text.odt", "seite.html"])
def test_pandoc_findet_den_baustein(name: str) -> None:
    markdown, engine = convert(name, "pandoc")
    assert engine == "pandoc"
    assert markdown.strip()
    assert MARKER in markdown


@pytest.mark.slow
@needs_docling
def test_docling_findet_den_baustein_im_pdf() -> None:
    """Docling liest das PDF und liefert Text und Tabelle."""
    markdown, engine = convert("tabelle.pdf", "docling", ocr=False)
    assert engine == "docling"
    assert MARKER in markdown
    assert "|" in markdown  # die gezeichnete Tabelle wird eine Markdown-Tabelle


@pytest.mark.slow
@needs_docling
def test_docling_liest_ein_bild_ohne_zu_scheitern() -> None:
    """Der OCR-Weg laeuft durch.

    Auf den Text wird hier nichts geprueft: Was eine Texterkennung aus einem
    gerenderten Bild macht, haengt am Modell und ist keine Zusage der Engine.
    """
    _, engine = convert("bild.png", "docling", ocr=True)
    assert engine == "docling"


def test_auswahl_ohne_wunsch_nimmt_markitdown_fuer_csv() -> None:
    """Der Weg ueber ``auto``: fuer .csv steht nur MarkItDown in der Matrix."""
    try:
        result = convert_with_fallback(FIXTURES / "liste.csv", ConvertOptions())
    except EngineUnavailable as exc:
        pytest.skip(str(exc))
    assert result.engine == "markitdown"
    assert MARKER in result.markdown
    assert result.duration_ms >= 0


@needs_pandoc
def test_auswahl_ohne_wunsch_nimmt_pandoc_fuer_odt() -> None:
    """Fuer .odt steht nur Pandoc in der Matrix."""
    result = convert_with_fallback(FIXTURES / "text.odt", ConvertOptions())
    assert result.engine == "pandoc"
    assert MARKER in result.markdown


def test_markdown_wird_durchgereicht(tmp_path: Path) -> None:
    """Eine .md-Datei geht unveraendert durch, ohne dass eine Engine laedt."""
    sample = tmp_path / "notiz.md"
    sample.write_text(f"# {MARKER}\n", encoding="utf-8")

    result = convert_with_fallback(sample, ConvertOptions())

    assert result.engine == registry.PASSTHROUGH
    assert result.markdown == f"# {MARKER}\n"


#: Sechs Umlaute, die in ISO-8859-1 je ein Byte belegen, das kein UTF-8 ist.
UMLAUTE = f"# {MARKER}\n\nGrüße über Umlaute: ä ö ü\n"


def test_fremde_kodierung_wird_gemeldet(tmp_path: Path) -> None:
    """Eine .md-Datei in ISO-8859-1 kommt zurueck, aber mit einer Warnung.

    Die sechs Umlaute werden beim Lesen durch U+FFFD ersetzt. Ohne Warnung stuende
    ``status: ok`` ueber einem Text mit sechs zerstoerten Stellen.
    """
    sample = tmp_path / "notiz.md"
    sample.write_bytes(UMLAUTE.encode("iso-8859-1"))

    result = convert_with_fallback(sample, ConvertOptions())

    assert result.engine == registry.PASSTHROUGH
    assert MARKER in result.markdown
    assert len(result.warnings) == 1
    assert "6" in result.warnings[0]
    assert "notiz.md" in result.warnings[0]


def test_utf8_meldet_nichts(tmp_path: Path) -> None:
    """Gegenprobe: dieselbe Datei in UTF-8 kommt unversehrt und ohne Warnung."""
    sample = tmp_path / "notiz.md"
    sample.write_text(UMLAUTE, encoding="utf-8")

    result = convert_with_fallback(sample, ConvertOptions())

    assert result.markdown == UMLAUTE
    assert result.warnings == []
