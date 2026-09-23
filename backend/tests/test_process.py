"""``PUT /api/process``, die Tuer fuer Open WebUI.

Open WebUI schickt die Rohbytes einer Datei, den Namen prozentkodiert in
``X-Filename`` und, wenn es ihn kennt, den MIME-Typ in ``Content-Type``. Zurueck
erwartet es ``page_content`` und ``metadata``. Die Tests pruefen den Endpunkt mit
Attrappen statt Engines; nur der erste laesst MarkItDown eine echte Datei wandeln.
"""

from __future__ import annotations

import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.converters import registry
from app.converters.base import ConversionResult, ConvertOptions
from app.main import app
from app.uploads import _semaphore

FIXTURES = Path(__file__).parent / "fixtures"


class DummyEngine:
    """Eine Engine, die ein festes Ergebnis liefert und sich merkt, was sie bekam."""

    def __init__(self, name: str, *, warnings: list[str] | None = None) -> None:
        self.name = name
        self.extensions: tuple[str, ...] = ()
        self.warnings = warnings or []
        self.seen: list[tuple[str, ConvertOptions]] = []

    def available(self) -> bool:
        return True

    def convert(self, path: Path, opts: ConvertOptions) -> ConversionResult:
        self.seen.append((path.name, opts))
        return ConversionResult(
            markdown=f"# {path.suffix} von {self.name}",
            engine=self.name,
            warnings=list(self.warnings),
        )


@pytest.fixture(autouse=True)
def clean_state(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Leerer Enginecache, frische Einstellungen, frischer Semaphor je Test."""
    monkeypatch.setattr(registry, "_INSTANCES", {registry.PASSTHROUGH: registry._Passthrough()})
    get_settings.cache_clear()
    _semaphore.cache_clear()
    yield
    get_settings.cache_clear()
    _semaphore.cache_clear()


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def install(*engines: DummyEngine) -> None:
    for engine in engines:
        registry._INSTANCES[engine.name] = engine


def settings(monkeypatch: pytest.MonkeyPatch, **env: str) -> None:
    for key, value in env.items():
        monkeypatch.setenv(f"KAIMARKIT_{key.upper()}", value)
    get_settings.cache_clear()


def test_docx_as_raw_body(client: TestClient) -> None:
    """Der Weg, den Open WebUI nimmt, mit einer echten Datei und einer echten Engine."""
    pytest.importorskip("markitdown")
    data = (FIXTURES / "bericht.docx").read_bytes()

    response = client.put("/api/process", content=data, headers={"X-Filename": "bericht.docx"})

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["page_content"].strip()
    assert body["metadata"]["engine"] == "markitdown"
    assert body["metadata"]["filename"] == "bericht.docx"


def test_percent_encoded_name_is_decoded(client: TestClient) -> None:
    """Open WebUI kodiert den Namen mit ``urllib.parse.quote``; zurueck kommt der Klartext."""
    engine = DummyEngine("markitdown")
    install(engine)

    response = client.put(
        "/api/process",
        content=b"x",
        headers={"X-Filename": "bericht%20f%C3%BCr%20alle.docx"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["metadata"]["filename"] == "bericht für alle.docx"
    assert engine.seen[0][0] == "bericht für alle.docx"


def test_name_cannot_leave_the_spool(client: TestClient) -> None:
    """Auch dekodiert bleibt vom Namen nur der letzte Bestandteil."""
    install(DummyEngine("markitdown"))

    response = client.put(
        "/api/process", content=b"x", headers={"X-Filename": "..%2F..%2Fetc%2Fbericht.docx"}
    )

    assert response.status_code == 200, response.text
    assert response.json()["metadata"]["filename"] == "bericht.docx"


def test_extension_from_content_type(client: TestClient) -> None:
    """Ohne ``X-Filename`` entscheidet der MIME-Typ ueber die Endung."""
    install(DummyEngine("pandoc"), DummyEngine("markitdown"))

    response = client.put(
        "/api/process", content=b"x", headers={"Content-Type": "application/epub+zip"}
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["page_content"] == "# .epub von pandoc"
    assert body["metadata"]["filename"].endswith(".epub")


def test_name_without_extension_takes_it_from_content_type(client: TestClient) -> None:
    install(DummyEngine("markitdown"))

    response = client.put(
        "/api/process",
        content=b"x",
        headers={"X-Filename": "bericht", "Content-Type": "application/pdf"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["metadata"]["filename"] == "bericht.pdf"


def test_neither_name_nor_known_type_is_415(client: TestClient) -> None:
    response = client.put(
        "/api/process", content=b"x", headers={"Content-Type": "application/octet-stream"}
    )

    assert response.status_code == 415
    assert response.json()["code"] == "unsupported_format"


def test_text_fallback_passes_source_code_through(client: TestClient) -> None:
    """Open WebUI schickt auch ``.py`` an die externe Extraktion; der Text kommt zurueck."""
    source = "def gruss() -> str:\n    return 'Grüße'\n"

    response = client.put(
        "/api/process", content=source.encode("utf-8"), headers={"X-Filename": "gruss.py"}
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["page_content"] == source
    assert body["metadata"]["engine"] == "passthrough"
    assert ".py" in body["metadata"]["warnings"]


def test_text_fallback_off_is_415(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    settings(monkeypatch, process_text_fallback="false")

    response = client.put("/api/process", content=b"print(1)\n", headers={"X-Filename": "a.py"})

    assert response.status_code == 415
    assert response.json()["code"] == "unsupported_format"


def test_text_fallback_rejects_binary(client: TestClient) -> None:
    """Was sich nicht sauber als UTF-8 lesen laesst, bleibt 415."""
    response = client.put(
        "/api/process", content=b"\x89PNG\r\n\x1a\n\xff\xfe", headers={"X-Filename": "a.bin"}
    )

    assert response.status_code == 415
    assert response.json()["code"] == "unsupported_format"


def test_text_fallback_rejects_nul_bytes(client: TestClient) -> None:
    """Gueltiges UTF-8 mit Nullbytes ist eine Binaerdatei, kein Text."""
    response = client.put(
        "/api/process", content=b"ELF\x00\x00\x01\x02", headers={"X-Filename": "programm"}
    )

    assert response.status_code == 415


def test_body_over_limit_is_413_and_leaves_nothing(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    spool = tmp_path / "spool"
    spool.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(spool))
    settings(monkeypatch, max_file_size_mb="1")
    install(DummyEngine("markitdown"))

    response = client.put(
        "/api/process",
        content=b"x" * (1024 * 1024 + 1),
        headers={"X-Filename": "gross.docx"},
    )

    assert response.status_code == 413
    assert response.json()["code"] == "file_too_large"
    assert list(spool.iterdir()) == []


def test_metadata_holds_only_scalars(client: TestClient) -> None:
    """Chroma nimmt nur ``str``, ``int``, ``float`` und ``bool``; eine Liste scheitert spaet."""
    install(DummyEngine("markitdown", warnings=["erste", "zweite"]))

    response = client.put("/api/process", content=b"x", headers={"X-Filename": "a.docx"})

    assert response.status_code == 200, response.text
    metadata = response.json()["metadata"]
    assert all(type(value) in (str, int) for value in metadata.values()), metadata
    assert metadata["warnings"] == "erste | zweite"
    assert isinstance(metadata["duration_ms"], int)


def test_no_warnings_no_key(client: TestClient) -> None:
    install(DummyEngine("markitdown"))

    response = client.put("/api/process", content=b"x", headers={"X-Filename": "a.docx"})

    assert response.status_code == 200, response.text
    assert "warnings" not in response.json()["metadata"]


def test_empty_body_is_a_clean_error(client: TestClient) -> None:
    install(DummyEngine("markitdown"))

    response = client.put("/api/process", content=b"", headers={"X-Filename": "leer.docx"})

    assert response.status_code == 415
    body = response.json()
    assert body["code"] == "unsupported_format"
    assert "Traceback" not in body["detail"]


def test_engine_and_ocr_come_from_the_environment(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Die Anfrage kann nichts waehlen; es gelten ``DEFAULT_ENGINE`` und ``OCR_ENABLED``."""
    settings(monkeypatch, default_engine="docling", ocr_enabled="false")
    docling = DummyEngine("docling")
    install(DummyEngine("markitdown"), docling)

    response = client.put("/api/process", content=b"x", headers={"X-Filename": "a.docx"})

    assert response.status_code == 200, response.text
    assert response.json()["metadata"]["engine"] == "docling"
    _, opts = docling.seen[0]
    assert opts.engine is None
    assert opts.ocr is None


def test_openapi_describes_the_endpoint(client: TestClient) -> None:
    document = client.get("/api/openapi.json").json()
    operation = document["paths"]["/api/process"]["put"]

    schema = operation["responses"]["200"]["content"]["application/json"]["schema"]
    assert schema["$ref"].endswith("/ProcessResponse")
    assert {"400", "413", "415", "500", "504"} <= set(operation["responses"])
