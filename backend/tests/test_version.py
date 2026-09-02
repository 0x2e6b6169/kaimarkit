"""Welche Version ``/api/health`` meldet.

Der Wert kommt aus ``KAIMARKIT_VERSION``. Der Bau schreibt dort hinein, was
``git describe`` liefert; der Container fragt Git nie selbst. Fehlt die Variable
oder ist sie leer, gilt ``__version__`` aus ``app/__init__.py`` — der Rückfall
für die Entwicklung ohne Bau.
"""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app import __version__
from app.config import get_settings
from app.main import app


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[pytest.MonkeyPatch]:
    """Ein Prozess ohne jede ``KAIMARKIT_*``-Variable und mit leerem Cache."""
    for key in list(os.environ):
        if key.startswith("KAIMARKIT_"):
            monkeypatch.delenv(key)
    get_settings.cache_clear()
    yield monkeypatch
    get_settings.cache_clear()


def test_health_meldet_die_version_aus_der_umgebung(clean_env: pytest.MonkeyPatch) -> None:
    """Was der Bau gesetzt hat, steht wörtlich in der Antwort."""
    clean_env.setenv("KAIMARKIT_VERSION", "v0.1.0-12-ga22a6c5")
    get_settings.cache_clear()
    with TestClient(app) as client:
        assert client.get("/api/health").json()["version"] == "v0.1.0-12-ga22a6c5"


def test_health_faellt_ohne_umgebung_auf_die_paketversion_zurueck(
    clean_env: pytest.MonkeyPatch,
) -> None:
    """Ohne gesetzte Variable antwortet der Dienst mit ``__version__``.

    Geprüft wird auch, wo der Rückfall steht: in ``config.py``. Ein fest
    verdrahtetes ``__version__`` im Endpunkt beantwortete dieselbe Frage richtig
    und ließe trotzdem nie einen anderen Wert durch.
    """
    assert get_settings().service_version == __version__
    with TestClient(app) as client:
        assert client.get("/api/health").json()["version"] == __version__

    clean_env.setenv("KAIMARKIT_VERSION", "")
    get_settings.cache_clear()
    assert get_settings().service_version == __version__
