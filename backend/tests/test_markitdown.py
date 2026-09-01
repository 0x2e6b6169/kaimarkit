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


_PDF_TEXT = "Ein Bericht mit einer Zeile."


def _write_pdf(target: Path) -> Path:
    """Ein einseitiges PDF mit einer Textzeile, von Hand gesetzt — ohne jedes Bild."""
    stream = f"BT /F1 16 Tf 72 720 Td ({_PDF_TEXT}) Tj ET\n".encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"endstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % number + obj + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n" % (len(objects) + 1)
    out += b"0000000000 65535 f \n"
    for offset in offsets:
        out += b"%010d 00000 n \n" % offset
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (
        len(objects) + 1,
        xref,
    )
    target.write_bytes(bytes(out))
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


def test_pdf_warnt_vor_weggelassenen_bildern(tmp_path: Path) -> None:
    """Die Warnung sagt, was die Engine tut — nicht, was in der Datei stand.

    Dieses PDF enthaelt kein einziges Bild und bekommt die Warnung trotzdem. So ist
    es gewollt: Der Adapter liest die Vorlage kein zweites Mal, um nachzuzaehlen.
    """
    result = get_converter().convert(_write_pdf(tmp_path / "bericht.pdf"), ConvertOptions())
    assert _PDF_TEXT in result.markdown
    assert result.warnings == [
        "MarkItDown uebernimmt keine Bilder aus PDF. "
        "Enthielt bericht.pdf Bilder, fehlt ihr Inhalt hier."
    ]


def test_docx_bekommt_die_bildwarnung_nicht(tmp_path: Path) -> None:
    """Gegenprobe: In .docx steht ein Alt-Text, dort waere die Aussage unwahr."""
    result = get_converter().convert(_write_docx(tmp_path / "sample.docx"), ConvertOptions())
    assert not [warning for warning in result.warnings if "Bilder" in warning]


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
