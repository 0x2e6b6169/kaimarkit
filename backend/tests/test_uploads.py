"""Tests fuer den Upload-Strom: Groessenlimit, Aufraeumen, Namen, Zeitgrenze."""

from __future__ import annotations

import io
import socket
import struct
import tempfile
import threading
import time
from contextlib import contextmanager
from pathlib import Path

import anyio
import pytest
import uvicorn
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


# ---------------------------------------------------------------------------
# Der abgebrochene Aufruf und sein Semaphor-Platz (BE-30)
#
# Der folgende Test haelt fest, was am 01.09.2026 gemessen wurde — nicht, was
# wuenschenswert waere. Gemessen mit einer eigenen uvicorn-Instanz, einer
# Attrappe als Engine (bekannte Dauer) und einem Client, der die Verbindung mit
# RST schliesst:
#
#   KAIMARKIT_MAX_CONCURRENT=2, Umwandlung 10,0 s, Abbruch nach 2,0 s.
#   Der Platz wurde erst bei 10,0 s frei, also 8,0 s nach dem Abbruch. Der
#   dritte Aufruf startete genau in dieser Sekunde und brauchte 17,0 s statt
#   10,0 s.
#
#   Zweiter Lauf, KAIMARKIT_CONVERSION_TIMEOUT=5, Umwandlung 20 s, Abbruch nach
#   2,0 s: Der Platz wurde bei 5,0 s frei — an der Zeitgrenze, nicht am Abbruch.
#   Der Handler endete mit ``ConversionTimeout``, nicht mit ``CancelledError``.
#
# Der Grund liegt nicht in ``run_conversion``: uvicorn bricht die Aufgabe beim
# Verbindungsabbruch gar nicht erst ab. ``async with _semaphore()`` wird deshalb
# nie vorzeitig verlassen, und ``abandon_on_cancel=True`` kommt nie zum Zuge.
# Der Platz kehrt nur zurueck, wenn die Umwandlung von selbst endet oder in die
# Zeitgrenze laeuft.
#
# Faellt dieser Test eines Tages, ist das die gute Nachricht: Dann gibt ein
# Abbruch den Platz frei, und die Zeitgrenze ist nur noch ein Notnagel.
# ---------------------------------------------------------------------------

#: Dauer der Attrappe. Lang genug, dass der Abbruch klar davor liegt.
_WORK_SECONDS = 1.0

#: Wann der Client die Verbindung wegwirft — deutlich vor dem Ende der Arbeit.
_ABORT_AFTER = 0.2


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def _wait_for(condition, timeout: float = 10.0) -> None:
    deadline = time.monotonic() + timeout
    while not condition():
        if time.monotonic() > deadline:
            raise AssertionError("die Attrappe kam nicht in der erwarteten Zeit an die Reihe")
        time.sleep(0.01)


@contextmanager
def _serving(app, port: int):
    """Faehrt eine eigene uvicorn-Instanz hoch und wieder herunter.

    Eine eigene Instanz auf einem freien Port, damit die Messung keinen laufenden
    Dienst saettigt.
    """
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error", lifespan="off")
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    try:
        _wait_for(lambda: server.started)
        yield
    finally:
        server.should_exit = True
        thread.join(timeout=10)


def _send_request(port: int) -> socket.socket:
    client = socket.create_connection(("127.0.0.1", port), timeout=10)
    client.sendall(b"GET /convert HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n")
    return client


def _abort(client: socket.socket) -> None:
    """Wirft die Verbindung weg, wie es ein geschlossener Browsertab tut.

    ``SO_LINGER`` mit Zeit 0 schickt ein RST statt eines geordneten FIN — so
    sieht der Server den Abbruch sofort und nicht erst nach dem Zeitablauf.
    """
    client.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))
    client.close()


def test_an_aborted_call_keeps_its_semaphore_slot(limits) -> None:
    """Gemessener Ist-Zustand: Der Abbruch gibt den Platz nicht frei.

    Ein Platz, ein Aufruf, der nach einem Fuenftel der Arbeit abbricht, und ein
    zweiter, der danach wartet. Kaeme der Platz beim Abbruch zurueck, startete
    der zweite Aufruf sofort. Er startet stattdessen erst, wenn die erste
    Umwandlung von selbst zu Ende ist.
    """
    limits(max_concurrent="1", conversion_timeout="30")
    starts: list[float] = []

    def work() -> str:
        starts.append(time.monotonic())
        time.sleep(_WORK_SECONDS)
        return "ok"

    async def app(scope, receive, send) -> None:
        await run_conversion(work)
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})

    port = _free_port()
    with _serving(app, port):
        first = _send_request(port)
        _wait_for(lambda: len(starts) == 1)
        time.sleep(_ABORT_AFTER)
        _abort(first)
        aborted = time.monotonic()

        second = _send_request(port)
        try:
            _wait_for(lambda: len(starts) == 2)
            second_start = starts[1]
            second.recv(64)
        finally:
            second.close()

    held_after_abort = second_start - aborted
    held_overall = second_start - starts[0]

    # Der Platz kam nicht beim Abbruch zurueck, sondern erst am Ende der Arbeit.
    assert held_after_abort > (_WORK_SECONDS - _ABORT_AFTER) / 2, (
        f"der Platz wurde {held_after_abort:.2f} s nach dem Abbruch frei — "
        "das sieht danach aus, als gaebe der Abbruch ihn inzwischen frei"
    )
    assert held_overall >= _WORK_SECONDS * 0.9, (
        f"der Platz war nur {held_overall:.2f} s belegt, die Arbeit dauert {_WORK_SECONDS} s"
    )
