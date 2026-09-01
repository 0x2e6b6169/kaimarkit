"""Macht ``app`` importierbar, ohne das Paket zu installieren.

``pytest`` legt nur ``tests/`` auf den Suchpfad; die Anwendung liegt eine Ebene
darueber.

Hier steht ausserdem die Attrappe der Docling-Module. Docling ist in der
Entwicklungsumgebung nicht installiert, und ``_build_pipeline`` importiert die
Bibliothek erst beim Aufruf. Die Tests haengen deshalb Attrappen in
``sys.modules`` und lesen ab, was der Adapter daraus baut. Zwei Testmodule
brauchen das — ``test_docling.py`` und ``test_docling_ocr.py`` —, und solange
jedes seine eigene Attrappe hielt, musste jede Aenderung am Adapter beide
nachziehen.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@dataclass
class FakeOcrAutoOptions:
    """Doclings Vorgabe. ``lang`` bleibt absichtlich leer."""

    lang: list[str] = field(default_factory=list)


@dataclass
class FakeEasyOcrOptions:
    """Die Maschine, die dieses Projekt ausdruecklich verlangt."""

    lang: list[str] = field(default_factory=lambda: ["fr", "de", "es", "en"])


class FakePdfPipelineOptions:
    """Die Felder, die ``_build_pipeline`` setzt — mit Doclings Ausgangswerten."""

    def __init__(self) -> None:
        self.do_ocr = False
        self.do_table_structure = False
        self.generate_picture_images = True
        self.artifacts_path: str | None = None
        self.ocr_options: object = FakeOcrAutoOptions()


@pytest.fixture
def fake_docling(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    """Legt die Attrappen der Docling-Module und merkt sich, was gebaut wurde.

    Zurueck kommt ein Namensraum mit ``pipeline_options`` und ``format_options``,
    wie ``_build_pipeline`` sie an die Bibliothek gereicht hat, dazu ``initialized``
    mit den Formaten, fuer die vorgeladen wurde, und die beiden Options-Klassen fuer
    ``isinstance``-Proben.
    """
    seen = SimpleNamespace(
        pipeline_options=None,
        format_options=None,
        initialized=[],
        EasyOcrOptions=FakeEasyOcrOptions,
        OcrAutoOptions=FakeOcrAutoOptions,
    )

    class FakeFormatOption:
        def __init__(self, pipeline_options: FakePdfPipelineOptions) -> None:
            self.pipeline_options = pipeline_options
            seen.pipeline_options = pipeline_options

    class FakeDocumentConverter:
        def __init__(self, format_options: dict[object, object]) -> None:
            seen.format_options = format_options

        def initialize_pipeline(self, doc_format: object) -> None:
            seen.initialized.append(doc_format)

        def convert(self, path: Path) -> object:
            return SimpleNamespace(
                document=SimpleNamespace(export_to_markdown=lambda image_mode: "# ok")
            )

    modules: dict[str, dict[str, object]] = {
        "docling": {},
        "docling.datamodel": {},
        "docling.datamodel.base_models": {
            "InputFormat": SimpleNamespace(PDF="pdf", IMAGE="image")
        },
        "docling.datamodel.pipeline_options": {
            "PdfPipelineOptions": FakePdfPipelineOptions,
            "EasyOcrOptions": FakeEasyOcrOptions,
            "OcrAutoOptions": FakeOcrAutoOptions,
        },
        "docling.document_converter": {
            "DocumentConverter": FakeDocumentConverter,
            "PdfFormatOption": FakeFormatOption,
            "ImageFormatOption": FakeFormatOption,
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
