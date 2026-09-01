"""Die Voreinstellungen im Code gegen die Auslieferung.

Wer das Backend nackt mit ``uvicorn`` startet, setzt keine ``KAIMARKIT_*``-Variablen
und bekommt die Voreinstellungen aus ``config.py``. Der Container bekommt seine Werte
aus ``docker/.env``. Laufen beide auseinander, verhaelt sich die Entwicklung anders
als die Auslieferung — und zwar lautlos. Diese Tests halten die Zeitgrenze zusammen.
"""

from __future__ import annotations

import os
import re
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app

REPO = Path(__file__).resolve().parents[2]
ENV_EXAMPLE = REPO / "docker" / ".env.example"
CONTRACT = REPO / "contracts" / "api.md"


def env_example(name: str) -> str:
    """Der Wert einer Variablen aus ``docker/.env.example``."""
    pattern = re.compile(rf"^{name}=(.*)$", re.MULTILINE)
    match = pattern.search(ENV_EXAMPLE.read_text(encoding="utf-8"))
    assert match is not None, f"{name} fehlt in {ENV_EXAMPLE}"
    return match.group(1).strip()


@pytest.fixture
def bare_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """Ein Backend ohne jede ``KAIMARKIT_*``-Variable, wie in der Entwicklung."""
    for key in list(os.environ):
        if key.startswith("KAIMARKIT_"):
            monkeypatch.delenv(key)
    get_settings.cache_clear()
    with TestClient(app) as client:
        yield client
    get_settings.cache_clear()


def test_zeitgrenze_ohne_umgebung_gleicht_der_auslieferung(bare_client: TestClient) -> None:
    limits = bare_client.get("/api/capabilities").json()["limits"]
    assert limits["conversion_timeout_s"] == int(env_example("KAIMARKIT_CONVERSION_TIMEOUT"))


def test_beispielrumpf_im_vertrag_zeigt_dieselbe_zeitgrenze() -> None:
    """``contracts/api.md`` zeigt einen Wert, den es auch wirklich gibt."""
    shown = re.search(r'"conversion_timeout_s":\s*(\d+)', CONTRACT.read_text(encoding="utf-8"))
    assert shown is not None
    assert int(shown.group(1)) == int(env_example("KAIMARKIT_CONVERSION_TIMEOUT"))
