"""Welche OCR-Maschine der Docling-Adapter baut und mit welchen Sprachen.

Docling ist in der Entwicklungsumgebung nicht installiert. Der Test haengt
deshalb Attrappen der benutzten Module in ``sys.modules`` und liest ab, was
``_build_pipeline`` daraus baut: die Klasse der OCR-Optionen und die Sprachliste,
die hineingeht. Dass EasyOCR danach auch wirklich erkennt, entscheidet sich erst
im Container (INT-2).

Der Adapter darf die Maschine nicht der Bibliothek ueberlassen: Doclings Vorgabe
``OcrAutoOptions`` laesst ``lang`` absichtlich leer und startet die selbst
gewaehlte Maschine mit deren Voreinstellungen. Ein nachtraeglich gesetztes
``lang`` faellt dabei weg.
"""

from __future__ import annotations

import sys
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

from app.config import get_settings
from app.converters import docling as adapter


@pytest.fixture(autouse=True)
def fresh_settings() -> Iterator[None]:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@dataclass
class FakeOcrAutoOptions:
    """Doclings Vorgabe. ``lang`` bleibt absichtlich leer."""

    lang: list[str] = field(default_factory=list)


@dataclass
class FakeEasyOcrOptions:
    """Die Maschine, die dieses Projekt ausdruecklich verlangt."""

    lang: list[str] = field(default_factory=lambda: ["fr", "de", "es", "en"])


class FakePdfPipelineOptions:
    def __init__(self) -> None:
        self.do_ocr = False
        self.do_table_structure = False
        self.generate_picture_images = True
        self.artifacts_path: str | None = None
        self.ocr_options: object = FakeOcrAutoOptions()


def install_fake_docling(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    """Legt die Attrappen der Docling-Module in ``sys.modules`` und merkt sich, was gebaut wurde."""
    seen = SimpleNamespace(pipeline_options=None, format_options=None)

    class FakePdfFormatOption:
        def __init__(self, pipeline_options: FakePdfPipelineOptions) -> None:
            self.pipeline_options = pipeline_options
            seen.pipeline_options = pipeline_options

    class FakeDocumentConverter:
        def __init__(self, format_options: dict[object, object]) -> None:
            seen.format_options = format_options

        def convert(self, path: Path) -> object:
            return SimpleNamespace(
                document=SimpleNamespace(export_to_markdown=lambda image_mode: "# ok")
            )

    modules = {
        "docling": {},
        "docling.datamodel": {},
        "docling.datamodel.base_models": {"InputFormat": SimpleNamespace(PDF="pdf")},
        "docling.datamodel.pipeline_options": {
            "PdfPipelineOptions": FakePdfPipelineOptions,
            "EasyOcrOptions": FakeEasyOcrOptions,
            "OcrAutoOptions": FakeOcrAutoOptions,
        },
        "docling.document_converter": {
            "DocumentConverter": FakeDocumentConverter,
            "PdfFormatOption": FakePdfFormatOption,
        },
        "docling_core": {},
        "docling_core.types": {},
        "docling_core.types.doc": {
            "ImageRefMode": SimpleNamespace(PLACEHOLDER="placeholder")
        },
    }
    for name, attributes in modules.items():
        module = ModuleType(name)
        for key, value in attributes.items():
            setattr(module, key, value)
        monkeypatch.setitem(sys.modules, name, module)

    return seen


def test_the_ocr_engine_is_easyocr_and_not_the_library_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("KAIMARKIT_OCR_LANGS", "de,en")
    get_settings.cache_clear()
    seen = install_fake_docling(monkeypatch)

    adapter._build_pipeline(True)

    assert isinstance(seen.pipeline_options.ocr_options, FakeEasyOcrOptions)
    assert seen.pipeline_options.ocr_options.lang == ["de", "en"]


def test_the_langs_come_from_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KAIMARKIT_OCR_LANGS", "fr, it")
    get_settings.cache_clear()
    seen = install_fake_docling(monkeypatch)

    adapter._build_pipeline(True)

    assert isinstance(seen.pipeline_options.ocr_options, FakeEasyOcrOptions)
    assert seen.pipeline_options.ocr_options.lang == ["fr", "it"]
