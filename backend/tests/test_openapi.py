"""Die veroeffentlichte Schnittstelle, geprueft an der erzeugten OpenAPI-Fassung.

Der Schnittstellen-Dreiklang aus ``contracts/api.md``, ``models.py`` und
``types.ts`` sagt nichts darueber, was der Dienst tatsaechlich veroeffentlicht: Ein
Modell kann in allen drei Dateien stehen und in ``/api/openapi.json`` trotzdem
fehlen, solange dem Endpunkt ein ``response_model`` fehlt. Diese Tests lesen
deshalb die erzeugte Fassung, nicht den Quelltext.

Dazu kommt die Gegenprobe in der anderen Richtung: Was die Endpunkte antworten,
muss sich gegen dasselbe Modell lesen lassen, und zwar Feld fuer Feld.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.converters import registry
from app.converters.base import ConversionResult, ConvertOptions
from app.main import app
from app.models import BatchResponse, ConversionEntry
from app.uploads import _semaphore


class DummyEngine:
    """Eine Engine, die ein festes Ergebnis liefert."""

    name = "markitdown"
    extensions: tuple[str, ...] = ()

    def available(self) -> bool:
        return True

    def convert(self, path: Path, opts: ConvertOptions) -> ConversionResult:
        return ConversionResult(markdown=f"# {path.suffix}", engine=self.name, warnings=["Hinweis"])


@pytest.fixture(autouse=True)
def clean_state(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Leerer Enginecache, frische Einstellungen, frischer Semaphor je Test."""
    monkeypatch.setattr(
        registry,
        "_INSTANCES",
        {registry.PASSTHROUGH: registry._Passthrough(), "markitdown": DummyEngine()},
    )
    get_settings.cache_clear()
    _semaphore.cache_clear()
    yield
    get_settings.cache_clear()
    _semaphore.cache_clear()


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def content_of(document: dict[str, Any], path: str) -> dict[str, Any]:
    """Die Medientypen, die ein Endpunkt fuer 200 nennt."""
    return document["paths"][path]["post"]["responses"]["200"]["content"]


def schema_of(document: dict[str, Any], path: str) -> dict[str, Any]:
    """Das JSON-Schema der 200-Antwort eines Endpunkts."""
    return content_of(document, path)["application/json"]["schema"]


def test_openapi_names_both_answer_types(client: TestClient) -> None:
    """``ConversionEntry`` und ``BatchResponse`` stehen unter ``components``.

    Ohne ``response_model`` an den beiden Endpunkten fehlen sie dort ganz, und wer
    unter ``/api/docs`` nachsieht, findet sie nicht.
    """
    document = client.get("/api/openapi.json").json()

    assert "ConversionEntry" in document["components"]["schemas"]
    assert "BatchResponse" in document["components"]["schemas"]
    assert schema_of(document, "/api/convert")["$ref"].endswith("/ConversionEntry")
    assert schema_of(document, "/api/convert/batch")["$ref"].endswith("/BatchResponse")


def test_openapi_keeps_the_second_branch(client: TestClient) -> None:
    """Beide Endpunkte antworten je nach ``Accept`` zweierlei — beides steht drin.

    Das Modell beschreibt nur den JSON-Zweig. Stuende es allein da, behauptete die
    veroeffentlichte Fassung, es gaebe die Datei nicht, die ``curl -O`` bekommt.
    """
    document = client.get("/api/openapi.json").json()

    assert "text/markdown; charset=utf-8" in content_of(document, "/api/convert")
    assert "application/zip" in content_of(document, "/api/convert/batch")


def test_convert_answers_exactly_a_conversion_entry(client: TestClient) -> None:
    """Die Antwort laesst sich gegen das Modell lesen und hat kein Feld zu viel."""
    body = client.post(
        "/api/convert",
        files={"file": ("bericht.docx", b"x", "application/octet-stream")},
        headers={"Accept": "application/json"},
    ).json()

    assert ConversionEntry.model_validate(body).model_dump(mode="json") == body


def test_batch_answers_exactly_a_batch_response(client: TestClient) -> None:
    """Dasselbe fuer den Stapel, einschliesslich der Eintraege darin."""
    body = client.post(
        "/api/convert/batch",
        files=[
            ("file", ("a.docx", b"x", "application/octet-stream")),
            ("file", ("b.docx", b"y", "application/octet-stream")),
        ],
        headers={"Accept": "application/json"},
    ).json()

    assert BatchResponse.model_validate(body).model_dump(mode="json") == body
    assert body["total"] == 2
