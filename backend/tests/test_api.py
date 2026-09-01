"""Die Endpunkte, geprueft mit Attrappen statt Engines.

Keine Bibliothek muss installiert sein: Die Tests setzen ihre eigenen Konverter in
den Cache der Registry und stellen die Einstellungen ueber die Umgebung.
"""

from __future__ import annotations

import tempfile
import time
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.converters import registry
from app.converters.base import ConversionResult, ConvertOptions
from app.errors import EngineFailed
from app.main import app
from app.uploads import _semaphore


class DummyEngine:
    """Eine Engine, die ein festes Ergebnis liefert."""

    def __init__(
        self,
        name: str,
        *,
        ready: bool = True,
        fails: str | None = None,
        sleep: float = 0.0,
        warnings: list[str] | None = None,
    ) -> None:
        self.name = name
        self.extensions: tuple[str, ...] = ()
        self.ready = ready
        self.fails = fails
        self.sleep = sleep
        self.warnings = warnings or []
        self.seen: list[ConvertOptions] = []

    def available(self) -> bool:
        return self.ready

    def convert(self, path: Path, opts: ConvertOptions) -> ConversionResult:
        self.seen.append(opts)
        if self.sleep:
            time.sleep(self.sleep)
        if self.fails is not None:
            raise EngineFailed(self.fails)
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


def upload(name: str = "bericht.docx", data: bytes = b"x") -> dict[str, object]:
    return {"file": (name, data, "application/octet-stream")}


def test_capabilities_lists_only_ready_engines(client: TestClient) -> None:
    install(
        DummyEngine("markitdown"),
        DummyEngine("docling", ready=False),
        DummyEngine("pandoc", ready=False),
    )

    body = client.get("/api/capabilities").json()

    assert body["formats"][".docx"] == ["markitdown"]
    assert body["formats"][".pdf"] == ["markitdown"]
    # Nur Pandoc kann .odt, und Pandoc waermt noch: die Endung faellt weg.
    assert ".odt" not in body["formats"]
    # ``passthrough`` steht nicht in ``engines``: Markdown wird durchgereicht,
    # gewaehlt wird dort nichts. Siehe contracts/api.md.
    assert body["engines"] == {
        "markitdown": "ready",
        "docling": "warming",
        "pandoc": "warming",
    }


def test_capabilities_reports_limits_from_settings(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("KAIMARKIT_MAX_FILE_SIZE_MB", "7")
    monkeypatch.setenv("KAIMARKIT_MAX_FILES", "3")
    monkeypatch.setenv("KAIMARKIT_CONVERSION_TIMEOUT", "11")
    monkeypatch.setenv("KAIMARKIT_OCR_ENABLED", "false")
    get_settings.cache_clear()

    body = client.get("/api/capabilities").json()

    assert body["limits"] == {"max_file_size_mb": 7, "max_files": 3, "conversion_timeout_s": 11}
    assert body["ocr_available"] is False
    assert body["default_engine"] == "auto"


def test_engine_that_cannot_be_loaded_counts_as_unavailable(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def no_module(name: str) -> None:
        raise ImportError(name)

    monkeypatch.setattr(registry.importlib, "import_module", no_module)

    body = client.get("/api/capabilities").json()

    assert body["engines"] == {
        "markitdown": "unavailable",
        "docling": "unavailable",
        "pandoc": "unavailable",
    }
    # Uebrig bleibt, was ohne Engine geht: Markdown wird durchgereicht.
    assert set(body["formats"]) == {".md", ".markdown"}


def test_engine_reports_its_own_state(client: TestClient) -> None:
    """Eine Engine, die ``state()`` anbietet, bestimmt ihren Zustand selbst.

    Docling braucht das: Sein Modul laedt auch ohne die Bibliothek, damit ein
    fehlendes ``docling`` nicht als ``ImportError`` endet. ``available()`` meldet
    dann False — genau wie beim Vorladen. Ohne die Rueckfrage bliebe eine nicht
    installierte Engine dauerhaft ``warming``, und das Frontend boete sie an.
    """

    class SelfReporting(DummyEngine):
        def state(self) -> str:
            return "unavailable"

    install(DummyEngine("markitdown"), SelfReporting("docling", ready=False))

    body = client.get("/api/capabilities").json()

    assert body["engines"]["docling"] == "unavailable"


def test_convert_answers_markdown_by_default(client: TestClient) -> None:
    install(DummyEngine("markitdown", warnings=["Bild ersetzt"]))

    response = client.post("/api/convert", files=upload())

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/markdown")
    assert response.text == "# .docx von markitdown"
    assert response.headers["x-engine"] == "markitdown"
    assert response.headers["x-warnings"] == "Bild ersetzt"
    assert 'filename="bericht.md"' in response.headers["content-disposition"]


def test_umlaut_in_filename_survives_the_header(client: TestClient) -> None:
    install(DummyEngine("markitdown"))

    response = client.post("/api/convert", files=upload("Übersicht.docx"))

    disposition = response.headers["content-disposition"]
    assert response.status_code == 200
    assert "filename*=UTF-8''%C3%9Cbersicht.md" in disposition


def test_convert_answers_json_when_asked(client: TestClient) -> None:
    install(DummyEngine("markitdown"))

    response = client.post(
        "/api/convert",
        files=upload(),
        data={"engine": "markitdown", "ocr": "true"},
        headers={"Accept": "application/json"},
    )

    body = response.json()
    assert body["filename"] == "bericht.docx"
    assert body["status"] == "ok"
    assert body["engine"] == "markitdown"
    assert body["markdown"] == "# .docx von markitdown"
    assert body["error"] is None
    assert body["duration_ms"] >= 0


def test_options_reach_the_engine(client: TestClient) -> None:
    engine = DummyEngine("pandoc")
    install(engine)

    client.post(
        "/api/convert", files=upload("buch.epub"), data={"engine": "pandoc", "ocr": "false"}
    )

    assert engine.seen == [ConvertOptions(engine="pandoc", ocr=False)]


def test_path_in_the_filename_does_not_escape(client: TestClient) -> None:
    install(DummyEngine("markitdown"))

    response = client.post(
        "/api/convert",
        files=upload("../../etc/passwd.docx"),
        headers={"Accept": "application/json"},
    )

    assert response.json()["filename"] == "passwd.docx"


def test_unknown_extension_is_415(client: TestClient) -> None:
    install(DummyEngine("markitdown"))

    response = client.post("/api/convert", files=upload("archiv.zip"))

    assert response.status_code == 415
    assert response.json()["code"] == "unsupported_format"


def test_requested_engine_that_cannot_do_the_format_is_400(client: TestClient) -> None:
    install(DummyEngine("markitdown"), DummyEngine("pandoc"))

    response = client.post("/api/convert", files=upload("bericht.pdf"), data={"engine": "pandoc"})

    assert response.status_code == 400
    assert response.json()["code"] == "engine_unsuitable"


def test_failing_engine_is_500_not_a_failed_entry(client: TestClient) -> None:
    install(DummyEngine("markitdown", fails="Datei ist beschaedigt"))

    response = client.post("/api/convert", files=upload(), headers={"Accept": "application/json"})

    assert response.status_code == 500
    assert response.json()["code"] == "conversion_failed"


def test_file_over_the_limit_is_413(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KAIMARKIT_MAX_FILE_SIZE_MB", "1")
    get_settings.cache_clear()
    install(DummyEngine("markitdown"))

    response = client.post("/api/convert", files=upload(data=b"y" * (2 * 1024 * 1024)))

    assert response.status_code == 413
    assert response.json()["code"] == "file_too_large"


def test_conversion_over_the_time_limit_is_504(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("KAIMARKIT_CONVERSION_TIMEOUT", "0")
    get_settings.cache_clear()
    _semaphore.cache_clear()
    install(DummyEngine("markitdown", sleep=0.05))

    response = client.post("/api/convert", files=upload())

    assert response.status_code == 504
    assert response.json()["code"] == "conversion_timeout"


def test_engine_that_cannot_be_loaded_is_400(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Eine ausdruecklich verlangte, aber nicht ladbare Engine endet als 400."""

    def no_module(name: str) -> None:
        raise ImportError(name)

    monkeypatch.setattr(registry.importlib, "import_module", no_module)

    response = client.post("/api/convert", files=upload(), data={"engine": "docling"})

    assert response.status_code == 400
    assert response.json()["code"] == "engine_unavailable"


def test_unknown_engine_name_is_400(client: TestClient) -> None:
    """Ein Name, den es gar nicht gibt, kommt nicht bis zu einer Engine."""
    install(DummyEngine("markitdown"))

    response = client.post("/api/convert", files=upload(), data={"engine": "phantasie"})

    assert response.status_code == 400
    assert response.json()["code"] == "engine_unsuitable"


def test_file_without_extension_is_415(client: TestClient) -> None:
    """Ohne Endung waehlt die Matrix nichts aus — das ist kein 500."""
    install(DummyEngine("markitdown"))

    response = client.post("/api/convert", files=upload("LIESMICH"))

    assert response.status_code == 415
    assert response.json()["code"] == "unsupported_format"


def test_nothing_stays_behind_after_a_conversion(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Der Dienst speichert nichts: Die temporaere Datei ist danach weg."""
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    install(DummyEngine("markitdown"))

    assert client.post("/api/convert", files=upload()).status_code == 200
    assert list(tmp_path.iterdir()) == []


def test_nothing_stays_behind_after_a_failure(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Auch im Fehlerfall raeumt der ``finally``-Zweig auf."""
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    install(DummyEngine("markitdown", fails="Datei ist beschaedigt"))

    assert client.post("/api/convert", files=upload()).status_code == 500
    assert list(tmp_path.iterdir()) == []


def test_unknown_extension_in_a_batch_stays_the_error_of_its_entry(client: TestClient) -> None:
    """Was einzeln ein 415 waere, scheitert im Stapel nur als Eintrag.

    Der Stapel antwortet mit 200; die uebrigen Dateien sind gewandelt. Wer fuenf
    Dateien schickt, verliert nicht alle vier guten wegen einer unbekannten Endung.
    """
    install(DummyEngine("markitdown"))
    files = [
        ("file", (name, b"x", "application/octet-stream"))
        for name in ("a.docx", "archiv.zip", "b.docx")
    ]

    response = client.post(
        "/api/convert/batch", files=files, headers={"Accept": "application/json"}
    )

    assert response.status_code == 200
    body = response.json()
    assert [entry["status"] for entry in body["entries"]] == ["ok", "failed", "ok"]
    assert body["entries"][1]["error"] == "Für .zip gibt es keine Engine."
    assert body["entries"][0]["markdown"] and body["entries"][2]["markdown"]
    assert (body["succeeded"], body["failed"]) == (2, 1)
