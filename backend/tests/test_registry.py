"""Auswahl und Fallback, geprueft mit Attrappen.

Keine echte Engine ist noetig: Die Tests setzen ihre eigenen Konverter in den Cache
der Registry, den ``_INSTANCES`` haelt.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from app.config import get_settings
from app.converters import registry
from app.converters.base import ConversionResult, ConvertOptions
from app.errors import (
    EngineFailed,
    EngineUnavailable,
    EngineUnsuitable,
    UnsupportedFormat,
)


class DummyEngine:
    """Eine Engine, die zaehlt, wie oft sie gerufen wurde."""

    def __init__(self, name: str, *, ready: bool = True, fails: str | None = None) -> None:
        self.name = name
        self.extensions: tuple[str, ...] = ()
        self.ready = ready
        self.fails = fails
        self.calls = 0

    def available(self) -> bool:
        return self.ready

    def convert(self, path: Path, opts: ConvertOptions) -> ConversionResult:
        self.calls += 1
        if self.fails is not None:
            raise EngineFailed(self.fails)
        return ConversionResult(markdown=f"# {self.name}", engine=self.name)


@pytest.fixture(autouse=True)
def clean_registry(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Leerer Enginecache und frisch gelesene Einstellungen je Test."""
    monkeypatch.setattr(registry, "_INSTANCES", {registry.PASSTHROUGH: registry._Passthrough()})
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def install(*engines: DummyEngine) -> None:
    for engine in engines:
        registry._INSTANCES[engine.name] = engine


def test_preference_order_per_extension() -> None:
    assert registry.preferences_for(".pdf") == ("docling", "markitdown")
    assert registry.preferences_for(".docx") == ("markitdown", "docling", "pandoc")
    assert registry.preferences_for(".epub") == ("pandoc", "markitdown")
    assert registry.preferences_for(".ODT") == ("pandoc",)


def test_pandoc_is_absent_for_pdf() -> None:
    assert "pandoc" not in registry.preferences_for(".pdf")


def test_engines_for_skips_unready_and_missing() -> None:
    # Seit BE-5 gibt es das Pandoc-Modul, und ob es bereit ist, haengt daran, ob
    # pandoc auf dieser Maschine im PATH liegt. Eine dritte Attrappe haelt den Test
    # davon unabhaengig.
    install(
        DummyEngine("markitdown"),
        DummyEngine("docling", ready=False),
        DummyEngine("pandoc", ready=False),
    )
    assert registry.engines_for(".docx") == ["markitdown"]


def test_select_takes_the_first_ready_engine() -> None:
    install(DummyEngine("docling"), DummyEngine("markitdown"))
    assert registry.select(".pdf").name == "docling"


def test_select_skips_an_unready_engine() -> None:
    install(DummyEngine("docling", ready=False), DummyEngine("markitdown"))
    assert registry.select(".pdf").name == "markitdown"


def test_unknown_extension_is_unsupported(tmp_path: Path) -> None:
    assert registry.engines_for(".xyz") == []
    with pytest.raises(UnsupportedFormat):
        registry.select(".xyz")
    sample = tmp_path / "datei.xyz"
    sample.write_text("egal")
    with pytest.raises(UnsupportedFormat):
        registry.convert_with_fallback(sample)


def test_requested_engine_without_aptitude_is_refused(tmp_path: Path) -> None:
    install(DummyEngine("pandoc"), DummyEngine("docling"))
    with pytest.raises(EngineUnsuitable):
        registry.select(".pdf", "pandoc")
    sample = tmp_path / "bericht.pdf"
    sample.write_bytes(b"%PDF-1.4")
    with pytest.raises(EngineUnsuitable):
        registry.convert_with_fallback(sample, ConvertOptions(engine="pandoc"))


def test_unknown_engine_name_is_unavailable() -> None:
    with pytest.raises(EngineUnavailable):
        registry.get_converter("hokuspokus")


def test_missing_module_becomes_engine_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    def explode(name: str) -> None:
        raise ImportError(f"No module named {name!r}")

    monkeypatch.setattr(registry.importlib, "import_module", explode)
    with pytest.raises(EngineUnavailable):
        registry.get_converter("docling")


def test_requested_engine_is_never_replaced(tmp_path: Path) -> None:
    docling = DummyEngine("docling", fails="Modell fehlt")
    markitdown = DummyEngine("markitdown")
    install(docling, markitdown)
    sample = tmp_path / "bericht.pdf"
    sample.write_bytes(b"%PDF-1.4")
    with pytest.raises(EngineFailed):
        registry.convert_with_fallback(sample, ConvertOptions(engine="docling"))
    assert markitdown.calls == 0


def test_fallback_takes_the_next_engine(tmp_path: Path) -> None:
    install(DummyEngine("docling", fails="Modell fehlt"), DummyEngine("markitdown"))
    sample = tmp_path / "bericht.pdf"
    sample.write_bytes(b"%PDF-1.4")
    result = registry.convert_with_fallback(sample)
    assert result.engine == "markitdown"
    assert any("docling" in warning for warning in result.warnings)


def test_fallback_disabled_raises_the_first_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("KAIMARKIT_ENABLE_FALLBACK", "false")
    get_settings.cache_clear()
    docling = DummyEngine("docling", fails="Modell fehlt")
    markitdown = DummyEngine("markitdown")
    install(docling, markitdown)
    sample = tmp_path / "bericht.pdf"
    sample.write_bytes(b"%PDF-1.4")
    with pytest.raises(EngineFailed):
        registry.convert_with_fallback(sample)
    assert markitdown.calls == 0


def test_default_engine_overrides_the_preference(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KAIMARKIT_DEFAULT_ENGINE", "markitdown")
    get_settings.cache_clear()
    assert registry.preferences_for(".pdf") == ("markitdown", "docling")
    assert registry.preferences_for(".epub") == ("markitdown", "pandoc")
    # Was die Endung nicht kann, wandert nicht nach vorn.
    assert registry.preferences_for(".odt") == ("pandoc",)


def test_markdown_is_passed_through(tmp_path: Path) -> None:
    sample = tmp_path / "notiz.md"
    sample.write_text("# Notiz\n", encoding="utf-8")
    result = registry.convert_with_fallback(sample)
    assert result.markdown == "# Notiz\n"
    assert result.engine == registry.PASSTHROUGH
    assert result.duration_ms >= 0
