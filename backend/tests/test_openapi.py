"""Die veroeffentlichte Schnittstelle, geprueft an der erzeugten OpenAPI-Fassung.

Der Schnittstellen-Dreiklang aus ``contracts/api.md``, ``models.py`` und
``types.ts`` sagt nichts darueber, was der Dienst tatsaechlich veroeffentlicht: Ein
Modell kann in allen drei Dateien stehen und in ``/api/openapi.json`` trotzdem
fehlen, solange dem Endpunkt ein ``response_model`` fehlt. Diese Tests lesen
deshalb die erzeugte Fassung, nicht den Quelltext.

Dreimal ist an dieser Stelle schon ein Typ verschwunden, ohne dass eine Regel
angeschlagen haette. Der erste Test deckt deshalb nicht mehr einzelne Namen ab,
sondern die Klasse: Was ``models.py`` als Schnittstelle beschreibt, muss in der
veroeffentlichten Fassung stehen — jeder Typ, auch der naechste, den jemand
hinzufuegt.

Dazu kommt die Gegenprobe in der anderen Richtung: Was die Endpunkte antworten,
muss sich gegen dasselbe Modell lesen lassen, und zwar Feld fuer Feld.
"""

from __future__ import annotations

from collections.abc import Iterator
from enum import StrEnum
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app import models
from app.config import get_settings
from app.converters import registry
from app.converters.base import ConversionResult, ConvertOptions
from app.main import app
from app.models import BatchResponse, ConversionEntry
from app.uploads import _semaphore

#: Die Fehlercodes je Endpunkt, wie ``contracts/api.md`` sie zuschreibt.
#:
#: Der Stapel steht nur mit 413 darin: Eine gescheiterte Datei wird dort zum
#: Eintrag mit ``status: "failed"``, nicht zur Fehlerantwort. Uebrig bleibt der
#: Fehler, der die Anfrage als Ganzes betrifft.
ERROR_CODES: dict[str, set[str]] = {
    "/api/convert": {"400", "413", "415", "500", "504"},
    "/api/convert/batch": {"413"},
}


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


def declared_types() -> set[str]:
    """Alles, was ``models.py`` als Schnittstelle beschreibt.

    Die Liste steht nicht im Test, sondern kommt aus dem Modul: Ein neues Modell
    faellt damit unter dieselbe Pruefung, ohne dass jemand daran denkt.
    """
    return {
        name
        for name, obj in vars(models).items()
        if not name.startswith("_")
        and isinstance(obj, type)
        and issubclass(obj, (BaseModel, StrEnum))
        and obj.__module__ == models.__name__
    }


def test_openapi_publishes_every_declared_type(client: TestClient) -> None:
    """Jeder Typ aus ``models.py`` steht unter ``components``.

    Der Schnittstellen-Dreiklang prueft ``contracts/api.md``, ``models.py`` und
    ``types.ts`` gegeneinander — keine der drei Dateien sagt etwas darueber, was
    der Dienst tatsaechlich ausliefert. Genau dort sind ``ConversionEntry``,
    ``BatchResponse`` und ``ErrorResponse`` nacheinander verschwunden. Diese
    Pruefung schliesst die Luecke als Klasse, nicht Name fuer Name.
    """
    published = set(client.get("/api/openapi.json").json()["components"]["schemas"])

    missing = sorted(declared_types() - published)
    assert not missing, f"nicht in /api/openapi.json veroeffentlicht: {', '.join(missing)}"
    assert "ErrorResponse" in published


def test_openapi_names_the_error_codes_of_each_endpoint(client: TestClient) -> None:
    """Beide Endpunkte fuehren die Fehlercodes, die der Vertrag ihnen zuschreibt.

    Die Codes entstehen im Ausnahmebehandler, nicht im Endpunkt. FastAPI sieht sie
    deshalb nicht; ohne ``responses=`` verspricht ``/api/docs`` nur 200 und 422.
    """
    document = client.get("/api/openapi.json").json()

    for path, codes in ERROR_CODES.items():
        responses = document["paths"][path]["post"]["responses"]
        assert codes <= set(responses), f"{path} nennt {sorted(codes - set(responses))} nicht"
        for code in codes:
            schema = responses[code]["content"]["application/json"]["schema"]
            assert schema["$ref"].endswith("/ErrorResponse"), f"{path} {code}"


def test_openapi_binds_each_endpoint_to_its_model(client: TestClient) -> None:
    """Die 200-Antwort verweist je Endpunkt auf das richtige Modell."""
    document = client.get("/api/openapi.json").json()

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
