"""Der Docling-Adapter, geprueft ohne Docling.

Die Bibliothek steckt vollstaendig in ``_build_pipeline``. Die Tests ersetzen diese
Funktion durch eine Attrappe und pruefen, was der Adapter darum herum tut:
vorladen, wiederverwenden, den OCR-Schalter beachten und Ausnahmen uebersetzen.

Die Tests, die wirklich Docling laden, tragen die Marke ``slow``.
"""

from __future__ import annotations

import importlib.util
import sys
import threading
import time
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

from app.config import get_settings
from app.converters import docling as adapter
from app.converters.base import ConvertOptions
from app.errors import EngineFailed, EngineUnavailable

FIXTURES = Path(__file__).parent / "fixtures"
FIXTURE = FIXTURES / "tabelle.pdf"
BILD = FIXTURES / "bild.png"


@pytest.fixture(autouse=True)
def fresh_settings() -> Iterator[None]:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


class FakePipeline:
    """Zaehlt, wie oft gebaut und wie oft gewandelt wurde."""

    def __init__(self, *, markdown: str = "| a | b |", fails: str | None = None) -> None:
        self.markdown = markdown
        self.fails = fails
        self.builds: list[bool] = []
        self.gate = threading.Event()
        self.gate.set()

    def build(self, ocr: bool):  # noqa: ANN201 — liefert die Wandelfunktion
        self.gate.wait(timeout=5)
        self.builds.append(ocr)

        def run(path: Path) -> str:
            if self.fails is not None:
                raise RuntimeError(self.fails)
            return self.markdown

        return run


def install(monkeypatch: pytest.MonkeyPatch, fake: FakePipeline) -> None:
    monkeypatch.setattr(adapter, "_build_pipeline", fake.build)


def test_module_imports_without_docling() -> None:
    """Ohne die Bibliothek bleibt das Modul ladbar — der Import darf nie scheitern."""
    assert adapter.NAME == "docling"
    assert ".pdf" in adapter.EXTENSIONS


def test_missing_library_becomes_engine_unavailable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def explode(ocr: bool) -> None:
        raise ImportError("No module named 'docling'")

    monkeypatch.setattr(adapter, "_build_pipeline", explode)
    converter = adapter.DoclingConverter()
    converter.start_warmup()
    converter._thread.join(timeout=5)

    assert converter.available() is False
    assert converter.state() == "unavailable"
    with pytest.raises(EngineUnavailable):
        converter.convert(tmp_path / "bericht.pdf", ConvertOptions())


def test_warmup_reports_warming_and_then_ready(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakePipeline()
    fake.gate.clear()
    install(monkeypatch, fake)
    converter = adapter.DoclingConverter()

    converter.start_warmup()
    assert converter.state() == "warming"
    assert converter.available() is False

    fake.gate.set()
    converter._thread.join(timeout=5)
    assert converter.state() == "ready"
    assert converter.available() is True


def test_warmup_builds_both_ocr_pipelines(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """OCR an und aus sind zwei Pipelines, und vorgeladen werden beide.

    Docling haengt die OCR-Einstellung an den Options-Hash: Wer nur eine Pipeline
    vorlaedt und danach die andere anfordert, laedt die Modelle ein zweites Mal —
    waehrend ``/api/capabilities`` laengst ``ready`` meldet. Nach dem Warmlauf baut
    deshalb keine der beiden Einstellungen noch etwas.
    """
    fake = FakePipeline()
    install(monkeypatch, fake)
    converter = adapter.DoclingConverter()

    converter.start_warmup()
    converter._thread.join(timeout=5)
    assert sorted(fake.builds) == [False, True]

    sample = tmp_path / "bericht.pdf"
    converter.convert(sample, ConvertOptions(ocr=True))
    converter.convert(sample, ConvertOptions(ocr=False))

    assert len(fake.builds) == 2  # beide kamen aus dem Warmlauf
    assert converter.state() == "ready"


def test_warmup_builds_the_configured_setting_first(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Zuerst die eingestellte Voreinstellung: Sie wird am ehesten verlangt."""
    monkeypatch.setenv("KAIMARKIT_OCR_ENABLED", "false")
    get_settings.cache_clear()
    fake = FakePipeline()
    install(monkeypatch, fake)
    converter = adapter.DoclingConverter()

    converter.start_warmup()
    converter._thread.join(timeout=5)

    assert fake.builds == [False, True]


def test_a_request_while_warming_waits_for_the_same_converter(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake = FakePipeline()
    fake.gate.clear()
    install(monkeypatch, fake)
    converter = adapter.DoclingConverter()
    converter.start_warmup()

    result: list[str] = []

    def request() -> None:
        result.append(converter.convert(tmp_path / "bericht.pdf", ConvertOptions()).markdown)

    caller = threading.Thread(target=request)
    caller.start()
    fake.gate.set()
    caller.join(timeout=5)

    assert result == ["| a | b |"]
    # Der Warmlauf baut beide Einstellungen; die verlangte kam aus ihm, nicht dazu.
    assert fake.builds.count(True) == 1


def test_converter_is_reused(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    fake = FakePipeline()
    install(monkeypatch, fake)
    converter = adapter.DoclingConverter()
    sample = tmp_path / "bericht.pdf"

    converter.convert(sample, ConvertOptions())
    converter.convert(sample, ConvertOptions())

    assert len(fake.builds) == 1


def test_ocr_switch_comes_from_the_options(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake = FakePipeline()
    install(monkeypatch, fake)
    converter = adapter.DoclingConverter()
    sample = tmp_path / "bericht.pdf"

    converter.convert(sample, ConvertOptions(ocr=False))
    converter.convert(sample, ConvertOptions(ocr=True))
    converter.convert(sample, ConvertOptions(ocr=False))

    assert fake.builds == [False, True]  # je Einstellung ein Konverter, dann wiederverwendet


def test_ocr_switch_falls_back_to_the_setting(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("KAIMARKIT_OCR_ENABLED", "false")
    get_settings.cache_clear()
    fake = FakePipeline()
    install(monkeypatch, fake)
    converter = adapter.DoclingConverter()

    converter.convert(tmp_path / "bericht.pdf", ConvertOptions())

    assert fake.builds == [False]


def test_library_failure_becomes_engine_failed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    install(monkeypatch, FakePipeline(fails="Seite 3 ist kaputt"))
    converter = adapter.DoclingConverter()

    with pytest.raises(EngineFailed) as excinfo:
        converter.convert(tmp_path / "bericht.pdf", ConvertOptions())
    assert "bericht.pdf" in excinfo.value.detail


def test_get_converter_starts_the_warmup(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakePipeline()
    install(monkeypatch, fake)
    monkeypatch.setattr(adapter, "_INSTANCE", None)

    converter = adapter.get_converter()
    converter._thread.join(timeout=5)

    assert adapter.get_converter() is converter  # eine Instanz je Prozess
    assert sorted(fake.builds) == [False, True]
    assert converter.available() is True


@pytest.mark.slow
@pytest.mark.skipif(
    importlib.util.find_spec("docling") is None, reason="docling ist nicht installiert"
)
@pytest.mark.skipif(not FIXTURE.exists(), reason="fixtures/tabelle.pdf fehlt")
def test_real_docling_converts_a_table() -> None:
    """Ein PDF mit Tabelle wird zur Markdown-Tabelle, der zweite Lauf ist schneller."""
    converter = adapter.DoclingConverter()

    first = time.perf_counter()
    markdown = converter.convert(FIXTURE, ConvertOptions(ocr=False)).markdown
    first = time.perf_counter() - first

    second = time.perf_counter()
    converter.convert(FIXTURE, ConvertOptions(ocr=False))
    second = time.perf_counter() - second

    assert "|" in markdown
    assert second < first


@pytest.mark.slow
@pytest.mark.skipif(
    importlib.util.find_spec("docling") is None, reason="docling ist nicht installiert"
)
@pytest.mark.skipif(not BILD.exists(), reason="fixtures/bild.png fehlt")
def test_the_ocr_switch_works_on_images() -> None:
    """Dasselbe Bild, zweimal: ohne Texterkennung bleibt es leer, mit ihr nicht.

    Das Bild hat keine Textebene. Alles, was zurueckkommt, hat die Texterkennung
    gelesen — der Schalter entscheidet also allein ueber den Inhalt. Auf einzelne
    Woerter wird nichts geprueft: Was ein Modell aus gerendertem Text macht, ist
    keine Zusage der Engine.
    """
    converter = adapter.DoclingConverter()

    ohne = converter.convert(BILD, ConvertOptions(ocr=False)).markdown
    mit = converter.convert(BILD, ConvertOptions(ocr=True)).markdown

    assert not ohne.strip()
    assert mit.strip()


# --- Welche Formate die Optionen bekommen -----------------------------------
#
# Docling steckt vollstaendig in ``_build_pipeline``. Die folgenden Tests haengen
# Attrappen der benutzten Module in ``sys.modules`` und lesen ab, welche
# ``format_options`` daraus entstehen. Sie laufen ohne die Bibliothek und fangen
# damit dauerhaft, was sonst erst im Container auffaellt.


class FakePipelineOptions:
    def __init__(self) -> None:
        self.do_ocr = False
        self.do_table_structure = False
        self.generate_picture_images = True
        self.artifacts_path: str | None = None
        self.ocr_options: object = None


class FakeEasyOcrOptions:
    def __init__(self, lang: list[str] | None = None) -> None:
        self.lang = lang


def install_fake_docling(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    """Legt Attrappen der Docling-Module und liefert die gesehenen ``format_options``."""
    seen: dict[str, object] = {}

    class FakeFormatOption:
        def __init__(self, pipeline_options: FakePipelineOptions) -> None:
            self.pipeline_options = pipeline_options

    class FakeDocumentConverter:
        def __init__(self, format_options: dict[str, object]) -> None:
            seen["format_options"] = format_options

        def convert(self, path: Path) -> object:
            return SimpleNamespace(
                document=SimpleNamespace(export_to_markdown=lambda image_mode: "# ok")
            )

    modules = {
        "docling": {},
        "docling.datamodel": {},
        "docling.datamodel.base_models": {
            "InputFormat": SimpleNamespace(PDF="pdf", IMAGE="image")
        },
        "docling.datamodel.pipeline_options": {
            "PdfPipelineOptions": FakePipelineOptions,
            "EasyOcrOptions": FakeEasyOcrOptions,
        },
        "docling.document_converter": {
            "DocumentConverter": FakeDocumentConverter,
            "PdfFormatOption": FakeFormatOption,
            "ImageFormatOption": FakeFormatOption,
        },
        "docling_core": {},
        "docling_core.types": {},
        "docling_core.types.doc": {"ImageRefMode": SimpleNamespace(PLACEHOLDER="p")},
    }
    for name, attributes in modules.items():
        module = ModuleType(name)
        for key, value in attributes.items():
            setattr(module, key, value)
        monkeypatch.setitem(sys.modules, name, module)

    return seen


def test_images_get_the_same_pipeline_options_as_pdf(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ohne einen eigenen Eintrag fuer Bilder legt Docling seine Vorgabe an.

    Dann laeuft die Texterkennung dort immer, ``KAIMARKIT_OCR_LANGS`` bleibt
    wirkungslos und statt EasyOCR startet die selbst gewaehlte Maschine.
    """
    monkeypatch.setenv("KAIMARKIT_OCR_LANGS", "de,en")
    get_settings.cache_clear()
    seen = install_fake_docling(monkeypatch)

    adapter._build_pipeline(False)

    format_options = seen["format_options"]
    assert set(format_options) == {"pdf", "image"}
    options = format_options["image"].pipeline_options
    assert options is format_options["pdf"].pipeline_options  # dieselben Optionen
    assert options.do_ocr is False
    assert options.ocr_options.lang == ["de", "en"]


def test_the_ocr_switch_reaches_the_image_options(monkeypatch: pytest.MonkeyPatch) -> None:
    seen = install_fake_docling(monkeypatch)

    adapter._build_pipeline(True)

    assert seen["format_options"]["image"].pipeline_options.do_ocr is True


# --- Platzhalter statt Inhalt ------------------------------------------------
#
# Ordnet Doclings Modell etwas als Bild ein, steht im Markdown nur ein Platzhalter.
# Der Adapter zaehlt diese Stellen und legt eine Warnung dazu; ohne Platzhalter
# bleibt ``warnings`` leer, sonst warnt er immer und die Warnung sagt nichts mehr.


def test_placeholders_become_a_warning_with_their_count(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    markdown = "## Breittabelle\n\n<!-- image -->\n\n<!-- image -->\n\n<!-- image -->\n"
    install(monkeypatch, FakePipeline(markdown=markdown))
    converter = adapter.DoclingConverter()

    result = converter.convert(tmp_path / "bericht.pdf", ConvertOptions())

    assert len(result.warnings) == 1
    warning = result.warnings[0]
    assert "3" in warning
    assert "Platzhalter" in warning
    assert "bericht.pdf" in warning


def test_a_single_placeholder_is_counted_as_one(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    install(monkeypatch, FakePipeline(markdown="## Titel\n\n<!-- image -->\n"))
    converter = adapter.DoclingConverter()

    result = converter.convert(tmp_path / "bericht.pdf", ConvertOptions())

    assert len(result.warnings) == 1
    assert "ein Bild" in result.warnings[0]
    assert "Platzhalter" in result.warnings[0]


def test_markdown_without_placeholders_stays_without_warnings(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Die Gegenprobe: Eine Warnung, die immer kommt, sagt nichts mehr."""
    install(monkeypatch, FakePipeline(markdown="| a | b |\n| - | - |\n"))
    converter = adapter.DoclingConverter()

    result = converter.convert(tmp_path / "bericht.pdf", ConvertOptions())

    assert result.warnings == []
