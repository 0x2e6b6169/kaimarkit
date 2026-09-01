"""Was beim Hochfahren des Dienstes passiert.

Docling laedt seine Modelle rund achteinhalb Sekunden je Pipeline, und der Warmlauf
baut zwei davon. Beginnt das erst mit der ersten Wandlung, wartet der erste Nutzer
darauf. Deshalb stoesst der Lifespan es an — und diese Tests halten fest, dass er es
tut, ohne den Start aufzuhalten und ohne an einer fehlenden Bibliothek zu scheitern.
"""

from __future__ import annotations

import threading
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import main
from app.converters import docling as adapter


@pytest.fixture(autouse=True)
def fresh_adapter(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Jeder Test bekommt seinen eigenen Adapter, kein Erbe aus einem frueheren."""
    monkeypatch.setattr(adapter, "_INSTANCE", None)
    yield


def test_lifespan_starts_the_warmup() -> None:
    """Der Start ruft ``start_warmup()`` — sonst laedt Docling erst beim ersten PDF."""
    calls: list[str] = []

    original = adapter.start_warmup

    def record() -> None:
        calls.append("start_warmup")
        original()

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(main.docling, "start_warmup", record)
        with TestClient(main.app):
            pass

    assert calls == ["start_warmup"]


def test_startup_survives_a_missing_docling(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ohne die Bibliothek faellt das Vorladen still aus: Der Dienst laeuft, Docling nicht."""

    def explode(ocr: bool) -> Callable[[Path], str]:
        raise ImportError("No module named 'docling'")

    monkeypatch.setattr(adapter, "_build_pipeline", explode)

    with TestClient(main.app) as client:
        assert client.get("/api/health").status_code == 200
        converter = adapter._INSTANCE
        assert converter is not None  # der Start hat das Vorladen angestossen
        converter._thread.join(timeout=5)
        assert converter.state() == "unavailable"


def test_startup_does_not_wait_for_the_models(monkeypatch: pytest.MonkeyPatch) -> None:
    """Der Start haelt nicht an: ``/api/health`` antwortet, waehrend die Modelle laden."""
    gate = threading.Event()

    def slow_build(ocr: bool) -> Callable[[Path], str]:
        gate.wait(timeout=5)
        return lambda path: ""

    monkeypatch.setattr(adapter, "_build_pipeline", slow_build)

    try:
        with TestClient(main.app) as client:
            assert client.get("/api/health").status_code == 200
            converter = adapter._INSTANCE
            assert converter is not None
            assert converter.state() == "warming"  # laedt noch, und der Dienst antwortet
    finally:
        gate.set()
