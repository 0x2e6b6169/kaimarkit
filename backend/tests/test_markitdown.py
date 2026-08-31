"""Der MarkItDown-Adapter, ohne Fixtures aus dem Repo.

Die Beispieldateien entstehen im Test selbst. Die gesammelten Fixtures unter
``tests/fixtures/`` gehoeren BE-9; dieser Test kommt ohne sie aus und laeuft
deshalb auch, bevor es sie gibt.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from app.converters.base import ConvertOptions
from app.converters.markitdown import MarkItDownConverter, get_converter
from app.errors import EngineFailed, EngineUnavailable

pytest.importorskip("markitdown", reason="MarkItDown ist nicht installiert")

_CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="xml" ContentType="application/xml"/>
<Default Extension="rels"
 ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Override PartName="/word/document.xml"
 ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""

_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1"
 Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
 Target="word/document.xml"/>
</Relationships>"""

_DOCUMENT = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>
<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Erste Ueberschrift</w:t></w:r></w:p>
<w:p><w:r><w:t>Ein Absatz mit Text.</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Heading2"/></w:pPr><w:r><w:t>Zweite Ueberschrift</w:t></w:r></w:p>
</w:body></w:document>"""


def _write_docx(target: Path) -> Path:
    with zipfile.ZipFile(target, "w") as archive:
        archive.writestr("[Content_Types].xml", _CONTENT_TYPES)
        archive.writestr("_rels/.rels", _RELS)
        archive.writestr("word/document.xml", _DOCUMENT)
    return target


def test_get_converter_liefert_immer_dieselbe_instanz() -> None:
    assert get_converter() is get_converter()
    assert get_converter().name == "markitdown"


def test_available_meldet_true_wenn_die_bibliothek_da_ist() -> None:
    assert get_converter().available() is True


def test_docx_ergibt_markdown_mit_ueberschriften(tmp_path: Path) -> None:
    result = get_converter().convert(_write_docx(tmp_path / "sample.docx"), ConvertOptions())
    assert result.engine == "markitdown"
    assert "# Erste Ueberschrift" in result.markdown
    assert "## Zweite Ueberschrift" in result.markdown
    assert result.warnings == []


def test_leeres_ergebnis_gibt_eine_warnung_und_keinen_fehler(tmp_path: Path) -> None:
    leer = tmp_path / "leer.txt"
    leer.write_text("   \n\n", encoding="utf-8")
    result = get_converter().convert(leer, ConvertOptions())
    assert result.markdown.strip() == ""
    assert len(result.warnings) == 1


def test_ausnahmen_der_bibliothek_werden_zu_engine_failed(tmp_path: Path) -> None:
    # Es gibt die Datei nicht; MarkItDown wirft einen OSError, und der darf nicht
    # nach aussen dringen.
    with pytest.raises(EngineFailed):
        get_converter().convert(tmp_path / "fehlt.docx", ConvertOptions())


def test_fehlende_bibliothek_endet_in_engine_unavailable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    converter = MarkItDownConverter()
    monkeypatch.setattr(
        converter,
        "_get_engine",
        lambda: (_ for _ in ()).throw(EngineUnavailable("nicht installiert")),
    )
    assert converter.available() is False
    with pytest.raises(EngineUnavailable):
        converter.convert(tmp_path / "egal.docx", ConvertOptions())
