"""ZIP-Bau und Stapelendpunkt, geprueft mit Attrappen statt Engines.

Keine Bibliothek muss installiert sein: Die Tests setzen ihre eigenen Konverter in
den Cache der Registry.
"""

from __future__ import annotations

import io
import zipfile
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.converters import registry
from app.converters.base import ConversionResult, ConvertOptions
from app.errors import EngineFailed
from app.main import app
from app.models import ConversionEntry, ConversionStatus
from app.packaging import ERROR_FILENAME, build_archive
from app.uploads import _semaphore


class DummyEngine:
    """Eine Engine, die ein festes Ergebnis liefert — oder an einer Endung scheitert."""

    def __init__(self, name: str, *, fails_on: str | None = None) -> None:
        self.name = name
        self.extensions: tuple[str, ...] = ()
        self.fails_on = fails_on

    def available(self) -> bool:
        return True

    def convert(self, path: Path, opts: ConvertOptions) -> ConversionResult:
        if self.fails_on is not None and path.suffix == self.fails_on:
            raise EngineFailed("Datei ist beschaedigt")
        return ConversionResult(markdown=f"# {path.suffix} von {self.name}", engine=self.name)


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


def ok(filename: str, markdown: str = "# Inhalt") -> ConversionEntry:
    return ConversionEntry(
        filename=filename,
        status=ConversionStatus.OK,
        markdown=markdown,
        engine="markitdown",
        duration_ms=1,
    )


def failed(filename: str, error: str = "Datei ist beschaedigt") -> ConversionEntry:
    return ConversionEntry(
        filename=filename, status=ConversionStatus.FAILED, duration_ms=1, error=error
    )


def names(archive: zipfile.ZipFile) -> list[str]:
    return archive.namelist()


def test_same_name_from_two_folders_does_not_collide() -> None:
    entries = [ok("a/bericht.pdf", "erster"), ok("b/bericht.docx", "zweiter"), ok("bericht.epub")]

    with zipfile.ZipFile(build_archive(entries)) as archive:
        assert names(archive) == ["bericht.md", "bericht-2.md", "bericht-3.md"]
        assert archive.read("bericht.md").decode() == "erster"
        assert archive.read("bericht-2.md").decode() == "zweiter"


def test_path_in_the_name_disappears() -> None:
    entries = [ok("../../etc/passwd.docx"), ok("C:\\Users\\kai\\notiz.txt")]

    with zipfile.ZipFile(build_archive(entries)) as archive:
        assert names(archive) == ["passwd.md", "notiz.md"]


def test_failed_file_lands_in_the_error_list() -> None:
    entries = [ok("gut.docx"), failed("../kaputt.epub", "Archiv unlesbar")]

    with zipfile.ZipFile(build_archive(entries)) as archive:
        assert names(archive) == ["gut.md", ERROR_FILENAME]
        assert archive.read(ERROR_FILENAME).decode() == "kaputt.epub: Archiv unlesbar\n"


def test_archive_without_failures_has_no_error_list() -> None:
    with zipfile.ZipFile(build_archive([ok("gut.docx")])) as archive:
        assert names(archive) == ["gut.md"]


def test_umlaut_in_the_name_survives_the_archive() -> None:
    with zipfile.ZipFile(build_archive([ok("Übersicht.docx", "# Ü")])) as archive:
        assert names(archive) == ["Übersicht.md"]
        assert archive.read("Übersicht.md").decode() == "# Ü"


def batch(*files: tuple[str, bytes]) -> list[tuple[str, tuple[str, bytes, str]]]:
    return [("file", (name, data, "application/octet-stream")) for name, data in files]


def test_batch_answers_a_zip_with_one_file_per_upload(client: TestClient) -> None:
    registry._INSTANCES["markitdown"] = DummyEngine("markitdown")

    response = client.post(
        "/api/convert/batch",
        files=batch(("a.docx", b"x"), ("b.docx", b"y"), ("c.txt", b"z")),
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    assert 'filename="markdown.zip"' in response.headers["content-disposition"]
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        assert names(archive) == ["a.md", "b.md", "c.md"]


def test_one_failure_does_not_take_down_the_batch(client: TestClient) -> None:
    registry._INSTANCES["markitdown"] = DummyEngine("markitdown", fails_on=".txt")

    response = client.post("/api/convert/batch", files=batch(("a.docx", b"x"), ("b.txt", b"y")))

    assert response.status_code == 200
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        assert names(archive) == ["a.md", ERROR_FILENAME]
        assert "b.txt: Datei ist beschaedigt" in archive.read(ERROR_FILENAME).decode()


def test_batch_answers_json_when_asked(client: TestClient) -> None:
    registry._INSTANCES["markitdown"] = DummyEngine("markitdown", fails_on=".txt")

    response = client.post(
        "/api/convert/batch",
        files=batch(("a.docx", b"x"), ("b.txt", b"y")),
        headers={"Accept": "application/json"},
    )

    body = response.json()
    assert body["total"] == 2
    assert body["succeeded"] == 1
    assert body["failed"] == 1
    assert body["entries"][0]["status"] == "ok"
    assert body["entries"][1] == {
        "filename": "b.txt",
        "status": "failed",
        "markdown": None,
        "engine": None,
        "warnings": [],
        "duration_ms": body["entries"][1]["duration_ms"],
        "error": "Datei ist beschaedigt",
    }


def test_unsupported_format_stays_a_failed_entry(client: TestClient) -> None:
    registry._INSTANCES["markitdown"] = DummyEngine("markitdown")

    response = client.post(
        "/api/convert/batch",
        files=batch(("a.docx", b"x"), ("archiv.zip", b"y")),
        headers={"Accept": "application/json"},
    )

    assert response.status_code == 200
    assert response.json()["entries"][1]["status"] == "failed"


def test_too_many_files_is_413(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KAIMARKIT_MAX_FILES", "2")
    get_settings.cache_clear()
    registry._INSTANCES["markitdown"] = DummyEngine("markitdown")

    response = client.post(
        "/api/convert/batch",
        files=batch(("a.docx", b"x"), ("b.docx", b"y"), ("c.docx", b"z")),
    )

    assert response.status_code == 413
    assert response.json()["code"] == "too_many_files"
