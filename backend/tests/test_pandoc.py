"""Der Pandoc-Adapter.

Die Beispieldatei entsteht im Test selbst — die gesammelten Fixtures unter
``tests/fixtures/`` gehoeren BE-9. Was ohne Pandoc pruefbar ist, prueft eine
Attrappe fuer ``subprocess.run``; nur der eine Test, der wirklich wandelt, braucht
das Programm und ueberspringt sich sonst.
"""

from __future__ import annotations

import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import Any

import pytest

from app.config import get_settings
from app.converters.base import ConvertOptions
from app.converters.pandoc import PandocConverter, get_converter
from app.errors import ConversionTimeout, EngineFailed, EngineUnavailable, UnsupportedFormat

needs_pandoc = pytest.mark.skipif(
    shutil.which("pandoc") is None, reason="Pandoc liegt nicht im PATH"
)

_CONTAINER = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles><rootfile full-path="OEBPS/content.opf"
 media-type="application/oebps-package+xml"/></rootfiles>
</container>"""

_OPF = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="id">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:identifier id="id">urn:uuid:kaimarkit-test</dc:identifier>
<dc:title>Ein kleines Buch</dc:title>
<dc:language>de</dc:language>
<meta property="dcterms:modified">2026-01-01T00:00:00Z</meta>
</metadata>
<manifest>
<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
<item id="kap1" href="kap1.xhtml" media-type="application/xhtml+xml"/>
</manifest>
<spine><itemref idref="kap1"/></spine>
</package>"""

_NAV = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>Inhalt</title></head>
<body><nav epub:type="toc"><ol><li><a href="kap1.xhtml">Erstes Kapitel</a></li></ol></nav></body>
</html>"""

_CHAPTER = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Erstes Kapitel</title></head>
<body><h1>Erstes Kapitel</h1><p>Ein Absatz mit <em>Betonung</em>.</p></body>
</html>"""


def _write_epub(target: Path) -> Path:
    with zipfile.ZipFile(target, "w") as archive:
        archive.writestr("mimetype", "application/epub+zip", zipfile.ZIP_STORED)
        archive.writestr("META-INF/container.xml", _CONTAINER)
        archive.writestr("OEBPS/content.opf", _OPF)
        archive.writestr("OEBPS/nav.xhtml", _NAV)
        archive.writestr("OEBPS/kap1.xhtml", _CHAPTER)
    return target


class _Run:
    """Attrappe fuer ``subprocess.run``: merkt sich den Aufruf, liefert ein Ergebnis."""

    def __init__(self, *, returncode: int = 0, stdout: str = "", stderr: str = "") -> None:
        self.result = subprocess.CompletedProcess(
            args=[], returncode=returncode, stdout=stdout, stderr=stderr
        )
        self.command: list[str] = []
        self.kwargs: dict[str, Any] = {}

    def __call__(self, command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        self.command = command
        self.kwargs = kwargs
        return self.result


@pytest.fixture(autouse=True)
def frische_einstellungen() -> Any:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@needs_pandoc
def test_get_converter_liefert_immer_dieselbe_instanz() -> None:
    assert get_converter() is get_converter()
    assert get_converter().name == "pandoc"


@needs_pandoc
def test_epub_ergibt_markdown(tmp_path: Path) -> None:
    result = get_converter().convert(_write_epub(tmp_path / "sample.epub"), ConvertOptions())
    assert result.engine == "pandoc"
    assert "# Erstes Kapitel" in result.markdown
    assert "*Betonung*" in result.markdown
    assert result.warnings == []


def test_pdf_wird_direkt_abgelehnt(tmp_path: Path) -> None:
    # Die Registry reicht PDF gar nicht erst hierher; der direkte Aufruf sagt es
    # trotzdem deutlich, statt Pandoc daran scheitern zu lassen.
    assert ".pdf" not in PandocConverter.extensions
    sample = tmp_path / "bericht.pdf"
    sample.write_bytes(b"%PDF-1.4")
    with pytest.raises(UnsupportedFormat):
        PandocConverter().convert(sample, ConvertOptions())


def test_jeder_aufruf_traegt_sandbox_und_die_zeitgrenze(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("KAIMARKIT_PANDOC_TIMEOUT", "7")
    run = _Run(stdout="# Titel\n")
    monkeypatch.setattr(subprocess, "run", run)
    sample = tmp_path / "buch.epub"
    sample.write_bytes(b"nicht gelesen")

    result = PandocConverter().convert(sample, ConvertOptions())

    assert result.markdown == "# Titel\n"
    assert Path(run.command[0]).name == "pandoc"
    assert "--sandbox" in run.command
    assert "--to=gfm-raw_html" in run.command
    assert "--wrap=none" in run.command
    assert run.command[-1] == str(sample)
    assert run.kwargs["timeout"] == 7
    assert "shell" not in run.kwargs


def test_zeitgrenze_wird_zu_conversion_timeout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def explodiert(command: list[str], **kwargs: Any) -> None:
        raise subprocess.TimeoutExpired(cmd=command, timeout=kwargs["timeout"])

    monkeypatch.setattr(subprocess, "run", explodiert)
    sample = tmp_path / "gross.odt"
    sample.write_bytes(b"egal")
    with pytest.raises(ConversionTimeout):
        PandocConverter().convert(sample, ConvertOptions())


def test_fehlschlag_nennt_die_ersten_zeilen_von_stderr(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        subprocess, "run", _Run(returncode=64, stderr="Erste Zeile\nZweite Zeile\n")
    )
    sample = tmp_path / "kaputt.rtf"
    sample.write_bytes(b"egal")
    with pytest.raises(EngineFailed) as fehler:
        PandocConverter().convert(sample, ConvertOptions())
    assert "Erste Zeile" in fehler.value.detail


def test_meldungen_auf_stderr_werden_zur_warnung(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        subprocess, "run", _Run(stdout="# Titel\n", stderr="[WARNING] Bild fehlt\n")
    )
    sample = tmp_path / "buch.epub"
    sample.write_bytes(b"egal")
    result = PandocConverter().convert(sample, ConvertOptions())
    assert len(result.warnings) == 1
    assert "Bild fehlt" in result.warnings[0]


def test_fehlendes_programm_endet_in_engine_unavailable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PATH", str(tmp_path))
    converter = PandocConverter()
    assert converter.available() is False
    sample = tmp_path / "buch.epub"
    sample.write_bytes(b"egal")
    with pytest.raises(EngineUnavailable):
        converter.convert(sample, ConvertOptions())
    # Auch der Weg ueber die Registry endet dort, nie in einem FileNotFoundError.
    with pytest.raises(EngineUnavailable):
        get_converter()
