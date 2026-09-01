"""Tests fuer den Upload-Strom: Groessenlimit, Aufraeumen, Namen, Zeitgrenze."""

from __future__ import annotations

import io
import tempfile
import threading
import time
from pathlib import Path

import anyio
import pytest
from fastapi import UploadFile

from app.config import get_settings
from app.errors import ConversionTimeout, FileTooLarge
from app.uploads import run_conversion, sanitize_filename, stored_upload

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def tmp_spool(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Legt die temporaeren Dateien in ein eigenes Verzeichnis.

    So laesst sich pruefen, dass nach jedem Fall wirklich nichts uebrig bleibt —
    ohne das echte ``/tmp`` durchsuchen zu muessen.
    """
    spool = tmp_path / "spool"
    spool.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(spool))
    return spool


@pytest.fixture
def limits(monkeypatch: pytest.MonkeyPatch):
    """Setzt Grenzwerte aus der Umgebung und raeumt die Zwischenspeicher auf."""
    from app import uploads

    def apply(**env: str) -> None:
        for key, value in env.items():
            monkeypatch.setenv(f"KAIMARKIT_{key.upper()}", value)
        get_settings.cache_clear()
        uploads._semaphore.cache_clear()

    yield apply
    get_settings.cache_clear()
    uploads._semaphore.cache_clear()


def make_upload(payload: bytes, filename: str) -> tuple[UploadFile, io.BytesIO]:
    source = io.BytesIO(payload)
    return UploadFile(file=source, filename=filename), source


async def test_upload_too_large_aborts_before_full_read(tmp_spool: Path, limits) -> None:
    limits(max_file_size_mb="1")
    payload = b"x" * (3 * 1024 * 1024)
    upload, source = make_upload(payload, "gross.pdf")

    with pytest.raises(FileTooLarge) as fehler:
        async with stored_upload(upload):
            pytest.fail("der Rumpf darf nie erreicht werden")

    # Die Meldung erreicht den Nutzer und steht deshalb in deutscher Schreibung.
    assert "überschreitet" in fehler.value.detail
    assert source.tell() < len(payload), "die Datei wurde vollstaendig eingelesen"
    assert list(tmp_spool.iterdir()) == []


async def test_upload_is_removed_after_success(tmp_spool: Path, limits) -> None:
    limits(max_file_size_mb="1")
    upload, _ = make_upload(b"# titel", "bericht.md")

    async with stored_upload(upload) as stored:
        assert stored.path.exists()
        assert stored.path.read_bytes() == b"# titel"
        assert stored.path.suffix == ".md"
        inner = stored.path

    assert not inner.exists()
    assert list(tmp_spool.iterdir()) == []


async def test_upload_is_removed_when_conversion_fails(tmp_spool: Path, limits) -> None:
    limits(max_file_size_mb="1")
    upload, _ = make_upload(b"kaputt", "bericht.pdf")
    seen: list[Path] = []

    with pytest.raises(RuntimeError):
        async with stored_upload(upload) as stored:
            seen.append(stored.path)
            raise RuntimeError("die Engine ist gescheitert")

    assert not seen[0].exists()
    assert list(tmp_spool.iterdir()) == []


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ("../../etc/passwd", "passwd"),
        ("..\\..\\windows\\system.ini", "system.ini"),
        ("/absolut/pfad/bericht.pdf", "bericht.pdf"),
        ("..", "upload"),
        ("", "upload"),
        (None, "upload"),
        ("bericht.pdf", "bericht.pdf"),
    ],
)
def test_sanitize_filename_keeps_only_the_name(given: str | None, expected: str) -> None:
    assert sanitize_filename(given) == expected


async def test_upload_filename_has_no_path(tmp_spool: Path, limits) -> None:
    limits(max_file_size_mb="1")
    upload, _ = make_upload(b"inhalt", "../../etc/bericht.pdf")

    async with stored_upload(upload) as stored:
        assert stored.filename == "bericht.pdf"
        # Jede Datei bekommt ein eigenes Verzeichnis im Spool.
        assert stored.path.parent.parent == tmp_spool


async def test_stored_file_keeps_the_name_it_arrived_under(tmp_spool: Path, limits) -> None:
    """Die Engines nennen in ihren Meldungen ``path.name``.

    Hiesse die Datei auf der Platte ``tmpqwhm57ia.epub``, staende dieser Name in
    der Fehlermeldung und damit in der Oberflaeche — ein Name, den der Nutzer nie
    vergeben hat.
    """
    limits(max_file_size_mb="1")
    upload, _ = make_upload(b"kein zip", "roman.epub")

    async with stored_upload(upload) as stored:
        assert stored.path.name == "roman.epub"


async def test_run_conversion_passes_the_result_through(limits) -> None:
    limits(conversion_timeout="5", max_concurrent="2")
    assert await run_conversion(lambda: "# markdown") == "# markdown"


async def test_run_conversion_gives_up_at_the_time_limit(limits) -> None:
    limits(conversion_timeout="1", max_concurrent="2")

    with pytest.raises(ConversionTimeout) as fehler:
        await run_conversion(lambda: time.sleep(5))

    # Die Meldung erreicht den Nutzer und steht deshalb in deutscher Schreibung.
    assert "überschritten" in fehler.value.detail


async def test_run_conversion_limits_concurrency(limits) -> None:
    limits(conversion_timeout="10", max_concurrent="1")
    lock = threading.Lock()
    running = 0
    peak = 0

    def work() -> None:
        nonlocal running, peak
        with lock:
            running += 1
            peak = max(peak, running)
        time.sleep(0.05)
        with lock:
            running -= 1

    async with anyio.create_task_group() as group:
        for _ in range(3):
            group.start_soon(run_conversion, work)

    assert peak == 1
