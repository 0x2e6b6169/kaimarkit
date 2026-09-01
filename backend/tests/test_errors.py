"""Was eine Fehlermeldung nach aussen sagt — und was nur ins Protokoll gehoert.

Die Engines reichen den Wortlaut ihrer Bibliothek weiter, und der nennt die Datei
mit dem Pfad, unter dem sie im Dienst kurz lag. ``ConversionError`` kuerzt jeden
Pfad auf den Dateinamen. Geprueft wird beides: dass der Pfad verschwindet und dass
sonst nichts verschwindet.

Der Wortlaut in ``DOCLING`` stammt aus einem Lauf im Container (INT-2, 31.08.2026)
und ist nicht erfunden.
"""

from __future__ import annotations

import logging

import pytest

from app.errors import ConversionError, EngineFailed, shorten

#: Was Docling an einem beschaedigten PDF meldet, Wort fuer Wort.
DOCLING = (
    "Docling ist an kaputt.pdf gescheitert: Conversion failed for: "
    "/tmp/tmpkxfozixp/kaputt.pdf with status: failure. Errors: docling-parse could "
    "not load document 46ef4e69 : Failed to load document with key "
    "key=/tmp/tmpkxfozixp/kaputt.pdf"
)


def test_ein_beschaedigtes_pdf_nennt_keinen_pfad() -> None:
    fehler = EngineFailed(DOCLING)

    assert "/tmp/" not in fehler.detail
    assert "tmpkxfozixp" not in fehler.detail


def test_die_gekuerzte_meldung_nennt_datei_und_grund() -> None:
    """Die Gegenprobe: nicht auf „Konvertierung gescheitert" eingedampft."""
    detail = EngineFailed(DOCLING).detail

    assert "kaputt.pdf" in detail
    assert "docling-parse could not load document" in detail
    assert "Conversion failed for: kaputt.pdf" in detail


def test_der_ungekuerzte_wortlaut_steht_im_protokoll(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.WARNING, logger="app.errors"):
        fehler = EngineFailed(DOCLING)

    assert fehler.raw_detail == DOCLING
    assert "/tmp/tmpkxfozixp/kaputt.pdf" in caplog.text


def test_eine_meldung_ohne_pfad_bleibt_wie_sie_ist(caplog: pytest.LogCaptureFixture) -> None:
    """Ohne Kuerzung auch keine Protokollzeile — sie haette nichts zu melden."""
    with caplog.at_level(logging.WARNING, logger="app.errors"):
        fehler = ConversionError("Pandoc liest .pdf nicht.")

    assert fehler.detail == "Pandoc liest .pdf nicht."
    assert caplog.text == ""


@pytest.mark.parametrize(
    ("wortlaut", "erwartet"),
    [
        ("Error at /tmp/tmpq/b.epub:12: bad", "Error at b.epub:12: bad"),
        ("[Errno 2] No such file: '/tmp/tmpz/x.pdf'", "[Errno 2] No such file: 'x.pdf'"),
        # Ein Leerzeichen im Dateinamen beendet den Pfad frueh. Weg ist trotzdem
        # nur das Verzeichnis, der Name steht vollstaendig da.
        ("gescheitert an /tmp/tmpq/Mein Bericht.docx", "gescheitert an Mein Bericht.docx"),
    ],
)
def test_pfade_werden_zum_dateinamen(wortlaut: str, erwartet: str) -> None:
    assert shorten(wortlaut) == erwartet


@pytest.mark.parametrize(
    "wortlaut",
    [
        "siehe https://example.com/hilfe/fehler",
        "ein/aus steht auf aus",
        "a / b ist kein Pfad",
        "Höchstens 20 Dateien je Aufruf, angekommen sind 21",
    ],
)
def test_was_kein_pfad_ist_bleibt_stehen(wortlaut: str) -> None:
    assert shorten(wortlaut) == wortlaut
