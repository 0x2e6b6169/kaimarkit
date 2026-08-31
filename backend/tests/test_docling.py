"""Der Docling-Adapter, geprueft ohne Docling.

Die Bibliothek steckt vollstaendig in ``_build_pipeline``. Die Tests ersetzen diese
Funktion durch eine Attrappe und pruefen, was der Adapter darum herum tut:
vorladen, wiederverwenden, den OCR-Schalter beachten und Ausnahmen uebersetzen.

Der einzige Test, der wirklich Docling laedt, traegt die Marke ``slow``.
"""

from __future__ import annotations

import importlib.util
import threading
import time
from collections.abc import Iterator
from pathlib import Path

import pytest

from app.config import get_settings
from app.converters import docling as adapter
from app.converters.base import ConvertOptions
from app.errors import EngineFailed, EngineUnavailable

FIXTURE = Path(__file__).parent / "fixtures" / "tabelle.pdf"


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
    assert len(fake.builds) == 1  # der Aufbau lief genau einmal


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
    assert len(fake.builds) == 1
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
