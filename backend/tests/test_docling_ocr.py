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
"""

from __future__ import annotations

from collections.abc import Iterator
from types import SimpleNamespace

import pytest

from app.config import get_settings
from app.converters import docling as adapter


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
