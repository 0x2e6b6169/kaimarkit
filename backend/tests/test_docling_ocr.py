"""Welche OCR-Maschine der Docling-Adapter baut und mit welchen Sprachen.

Docling ist in der Entwicklungsumgebung nicht installiert. Die Tests nehmen
deshalb das Fixture ``fake_docling`` aus ``conftest.py`` — es haengt Attrappen der
benutzten Module in ``sys.modules`` — und lesen ab, was ``_build_pipeline`` daraus
baut: die Klasse der OCR-Optionen und die Sprachliste, die hineingeht. Dass EasyOCR
danach auch wirklich erkennt, entscheidet sich erst im Container (INT-2).

Der Adapter darf die Maschine nicht der Bibliothek ueberlassen: Doclings Vorgabe
``OcrAutoOptions`` laesst ``lang`` absichtlich leer und startet die selbst
gewaehlte Maschine mit deren Voreinstellungen. Ein nachtraeglich gesetztes
``lang`` faellt dabei weg.

Am Ende stehen vier Tests mit der Marke ``slow``. Sie laden Docling wirklich und
laufen nur im Abbild (``make test-slow-image``). Die ersten beiden schicken zwei
Bilder mit demselben Satz hindurch — eines aufrecht, eines wie eine Kamera es ablegt.
Die beiden letzten fragen, wie weit die Texterkennung in ein Dokument hineinreicht,
in dem ein Bild steckt.
"""

from __future__ import annotations

import importlib.util
from collections.abc import Iterator
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.config import get_settings
from app.converters import docling as adapter
from app.converters.base import ConvertOptions

FIXTURES = Path(__file__).parent / "fixtures"
SCAN = FIXTURES / "scan.png"
FOTO = FIXTURES / "foto_exif6.jpg"

BILD_DOCX = FIXTURES / "bild_im_dokument.docx"
BILD_PDF = FIXTURES / "bild_im_dokument.pdf"

#: Der Satz, den beide Bilder zeigen. Er steht in ``fixtures/build_fixtures.py``.
SENTENCE = "Dieser Satz stammt aus einem Scan"

#: Der Satz, der in den beiden Dokumenten allein im eingebetteten Bild steht — in
#: keiner Textebene. Auch er steht in ``fixtures/build_fixtures.py``. Der Punkt am
#: Ende fehlt hier: Was die Texterkennung liest, ist der Satz, nicht seine
#: Zeichensetzung.
IMAGE_SENTENCE = "Dieser Satz steckt nur im Bild"


@pytest.fixture(autouse=True)
def fresh_settings() -> Iterator[None]:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_the_ocr_engine_is_easyocr_and_not_the_library_default(
    monkeypatch: pytest.MonkeyPatch, fake_docling: SimpleNamespace
) -> None:
    monkeypatch.setenv("KAIMARKIT_OCR_LANGS", "de,en")
    get_settings.cache_clear()

    adapter._build_pipeline(True)

    options = fake_docling.pipeline_options.ocr_options
    assert isinstance(options, fake_docling.EasyOcrOptions)
    assert options.lang == ["de", "en"]


def test_the_langs_come_from_the_environment(
    monkeypatch: pytest.MonkeyPatch, fake_docling: SimpleNamespace
) -> None:
    monkeypatch.setenv("KAIMARKIT_OCR_LANGS", "fr, it")
    get_settings.cache_clear()

    adapter._build_pipeline(True)

    options = fake_docling.pipeline_options.ocr_options
    assert isinstance(options, fake_docling.EasyOcrOptions)
    assert options.lang == ["fr", "it"]


# --- Was die Texterkennung im Abbild wirklich liest --------------------------


@pytest.mark.slow
@pytest.mark.skipif(
    importlib.util.find_spec("docling") is None, reason="docling ist nicht installiert"
)
@pytest.mark.skipif(not SCAN.exists(), reason="fixtures/scan.png fehlt")
def test_ocr_reads_an_upright_scan() -> None:
    """Die Gegenprobe zum Foto: Aufrecht gelegt kommt der Satz zurueck.

    Ohne sie sagt ein rotes Foto nur, dass irgendetwas an der Texterkennung klemmt.
    Erst zusammen zeigen die beiden Tests, dass es an der Lage liegt.
    """
    markdown = adapter.DoclingConverter().convert(SCAN, ConvertOptions(ocr=True)).markdown

    assert SENTENCE in markdown


@pytest.mark.slow
@pytest.mark.skipif(
    importlib.util.find_spec("docling") is None, reason="docling ist nicht installiert"
)
@pytest.mark.skipif(not FOTO.exists(), reason="fixtures/foto_exif6.jpg fehlt")
def test_ocr_reads_a_photo_that_only_exif_puts_upright() -> None:
    """Ein Foto vom Handy: Die Pixel liegen quer, die Drehung steht im EXIF-Tag.

    Doclings ``ImageDocumentBackend`` oeffnet das Bild mit ``img.convert("RGB")`` und
    wertet den Tag nicht aus. EasyOCR sieht den Satz dann hochkant und findet nichts
    — im Abbild gemessen ein einzelnes ``g`` statt drei Zeilen, ohne Warnung
    (BE-34, GitHub #2). Der Adapter richtet das Bild deshalb selbst auf.

    Dieselbe Vorlage wie in ``test_ocr_reads_an_upright_scan``, nur gedreht: Was
    dieser Test gegenueber jenem misst, ist allein die Orientation.
    """
    markdown = adapter.DoclingConverter().convert(FOTO, ConvertOptions(ocr=True)).markdown

    assert SENTENCE in markdown


# --- Wie weit die Texterkennung in ein Dokument hineinreicht -----------------


@pytest.mark.slow
@pytest.mark.skipif(
    importlib.util.find_spec("docling") is None, reason="docling ist nicht installiert"
)
@pytest.mark.skipif(not BILD_PDF.exists(), reason="fixtures/bild_im_dokument.pdf fehlt")
def test_ocr_reads_an_image_embedded_in_a_pdf() -> None:
    """Ein PDF mit Textebene und einem Bild darin: Der Satz aus dem Bild kommt zurueck.

    Docling faehrt PDF durch die ``StandardPdfPipeline``, und die schickt die
    Bildflaechen einer Seite durch EasyOCR. Der zweite Lauf ist die Gegenprobe: Ohne
    ``ocr`` fehlt der Satz. Erst er belegt, dass der erste Lauf den Satz aus dem Bild
    liest und nicht aus der Textebene — dort steht er naemlich nicht.
    """
    converter = adapter.DoclingConverter()

    mit_ocr = converter.convert(BILD_PDF, ConvertOptions(ocr=True)).markdown
    ohne_ocr = converter.convert(BILD_PDF, ConvertOptions(ocr=False)).markdown

    assert IMAGE_SENTENCE in mit_ocr
    assert IMAGE_SENTENCE not in ohne_ocr


@pytest.mark.slow
@pytest.mark.skipif(
    importlib.util.find_spec("docling") is None, reason="docling ist nicht installiert"
)
@pytest.mark.skipif(not BILD_DOCX.exists(), reason="fixtures/bild_im_dokument.docx fehlt")
def test_ocr_does_not_reach_an_image_embedded_in_a_docx() -> None:
    """Dasselbe Bild in einem Word-Dokument: Der Satz kommt nicht zurueck.

    Dieser Test haelt eine Grenze der Engine fest, keinen erwuenschten Zustand. Docling
    2.124.0 gibt ``InputFormat.DOCX`` an die ``SimplePipeline``, und die kennt keine
    Texterkennung: ``ocr_model`` wird im ganzen Paket ``docling/pipeline/`` nur in
    ``standard_pdf_pipeline.py`` gebaut, und ``ConvertPipelineOptions`` — die Optionen
    der ``SimplePipeline`` — fuehrt ``do_ocr`` gar nicht. Es gibt also keinen Schalter,
    der hier anzuschalten waere; deshalb steht in ``docling.py`` nichts dazu (BE-38,
    GitHub #2).

    Der Test steht trotzdem hier, weil eine spaetere Docling-Fassung das aendern kann.
    Faellt er durch, ist das die Meldung, dass die Grenze weg ist — und dass
    ``docs/grenzen.md`` und die Warnung nachzuziehen sind.

    Zugesichert wird nur, dass ueberhaupt gewarnt wird, nicht der Wortlaut. Dass die
    Warnung den Grund nicht nennt, ist ein eigener Befund und gehoert in ein eigenes
    Ticket; dieser Test soll ihm nicht im Weg stehen.
    """
    result = adapter.DoclingConverter().convert(BILD_DOCX, ConvertOptions(ocr=True))

    assert IMAGE_SENTENCE not in result.markdown
    assert adapter.PLACEHOLDER in result.markdown
    assert result.warnings
