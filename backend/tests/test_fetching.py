"""Seiten aus dem Netz holen — geprüft ohne Netz.

Das Holen läuft über ``httpx.MockTransport``, die Namensauflösung über eine
Attrappe. Kein Test hier braucht eine Verbindung nach draußen; wer einen
schreibt, der eine braucht, hat den falschen Ort gewählt.
"""

from __future__ import annotations

import ipaddress
import socket
import tempfile
from collections.abc import AsyncIterator, Callable, Iterator
from pathlib import Path

import httpx
import pytest

from app import fetching
from app.config import get_settings
from app.errors import ConversionTimeout, FileTooLarge, InvalidUrl, UnsupportedFormat
from app.fetching import derive_filename, fetch_page, fetched_page, slugify
from app.uploads import _semaphore

pytestmark = pytest.mark.anyio

#: Eine öffentliche und eine private Adresse, wie ``example.com`` und ein Router sie
#: haben. Die Namen darunter sind erfunden; aufgelöst werden sie nie wirklich.
PUBLIC = "93.184.216.34"
PRIVATE = "10.0.0.5"
NAMES: dict[str, list[str]] = {
    "example.com": [PUBLIC],
    "intern.example": [PRIVATE],
    "beides.example": [PUBLIC, PRIVATE],
    "v6.example": ["2606:2800:220:1:248:1893:25c8:1946"],
}

Handler = Callable[[httpx.Request], httpx.Response]


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(autouse=True)
def fake_dns(monkeypatch: pytest.MonkeyPatch) -> None:
    """Löst nur die Namen aus ``NAMES`` auf; alles andere ist unbekannt."""

    def resolve(host: str) -> list[str]:
        try:
            return NAMES[host]
        except KeyError:
            raise socket.gaierror(f"Name or service not known: {host}") from None

    monkeypatch.setattr(fetching, "_resolve", resolve)


@pytest.fixture(autouse=True)
def fresh_settings() -> Iterator[None]:
    get_settings.cache_clear()
    _semaphore.cache_clear()
    yield
    get_settings.cache_clear()
    _semaphore.cache_clear()


@pytest.fixture
def serve(monkeypatch: pytest.MonkeyPatch) -> Callable[[Handler], list[httpx.Request]]:
    """Hängt einen Handler als Transport ein und sammelt, was er gesehen hat."""

    def install(handler: Handler) -> list[httpx.Request]:
        seen: list[httpx.Request] = []

        def record(request: httpx.Request) -> httpx.Response:
            seen.append(request)
            return handler(request)

        monkeypatch.setattr(fetching, "_transport", lambda: httpx.MockTransport(record))
        return seen

    return install


@pytest.fixture
def rebinding_dns(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ein gegnerischer DNS: erst die oeffentliche Adresse, danach die private.

    So sieht die Pruefung eine oeffentliche Adresse, und der Verbindungsaufbau
    saehe eine private — genau die Luecke, um die es hier geht.
    """
    calls: list[str] = []

    def resolve(host: str) -> list[str]:
        calls.append(host)
        return [PUBLIC] if len(calls) == 1 else [PRIVATE]

    monkeypatch.setattr(fetching, "_resolve", resolve)


def connect_target(request: httpx.Request) -> str:
    """Wohin ein echter Transport verbaende.

    Steht im Host schon eine Adresse, ist sie das Ziel. Steht dort ein Name, loest
    der Transport ihn im Augenblick des Verbindungsaufbaus selbst auf — das ist
    die zweite Aufloesung, die ``httpx`` sonst hinter unserem Ruecken macht.
    """
    host = request.url.host
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return fetching._resolve(host)[0]
    return host


def html(title: str | None, body: str = "<p>Hallo</p>") -> httpx.Response:
    head = f"<head><title>{title}</title></head>" if title is not None else "<head></head>"
    return httpx.Response(
        200,
        content=f"<html>{head}<body>{body}</body></html>".encode(),
        headers={"content-type": "text/html; charset=utf-8"},
    )


# ── Namen ─────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("text", "slug"),
    [
        ("Example Domain", "example-domain"),
        ("Über Grüße & Straße", "ueber-gruesse-strasse"),
        ("  Viel --- Zeichen!!  ", "viel-zeichen"),
        ("x" * 100, "x" * 80),
        ("a" * 79 + "-b", "a" * 79),
        ("!!!", ""),
    ],
)
def test_slugify(text: str, slug: str) -> None:
    assert slugify(text) == slug


def test_without_a_title_host_and_path_make_the_name() -> None:
    assert derive_filename("https://example.com/blog/post", ".html", None) == (
        "example-com-blog-post.html"
    )


def test_the_extension_in_the_path_is_not_doubled() -> None:
    assert derive_filename("https://example.com/papers/paper.pdf", ".pdf", None) == (
        "example-com-papers-paper.pdf"
    )


def test_a_title_made_of_punctuation_falls_back_to_the_address() -> None:
    assert derive_filename("https://example.com/", ".html", "!!!") == "example-com.html"


# ── Holen ─────────────────────────────────────────────────────────────────────


async def test_the_title_becomes_the_filename(serve, tmp_path: Path) -> None:
    seen = serve(lambda request: html("Example Domain"))

    page = await fetch_page("https://example.com/", tmp_path)

    assert page.filename == "example-domain.html"
    assert page.path == tmp_path / "example-domain.html"
    assert b"<p>Hallo</p>" in page.path.read_bytes()
    assert seen[0].headers["user-agent"].startswith("kaimarkit/")


async def test_umlauts_in_the_title_are_transcribed(serve, tmp_path: Path) -> None:
    serve(lambda request: html("Größenordnung &amp; Maß"))

    page = await fetch_page("https://example.com/", tmp_path)

    assert page.filename == "groessenordnung-mass.html"


async def test_without_a_title_the_address_names_the_file(serve, tmp_path: Path) -> None:
    serve(lambda request: html(None))

    page = await fetch_page("https://example.com/blog/post", tmp_path)

    assert page.filename == "example-com-blog-post.html"


async def test_a_pdf_keeps_its_extension(serve, tmp_path: Path) -> None:
    serve(
        lambda request: httpx.Response(
            200, content=b"%PDF-1.4", headers={"content-type": "application/pdf"}
        )
    )

    page = await fetch_page("https://example.com/papers/paper.pdf", tmp_path)

    assert page.filename == "example-com-papers-paper.pdf"
    assert page.path.suffix == ".pdf"


async def test_an_unknown_media_type_takes_the_extension_from_the_path(
    serve, tmp_path: Path
) -> None:
    serve(
        lambda request: httpx.Response(
            200, content=b"x", headers={"content-type": "application/octet-stream"}
        )
    )

    page = await fetch_page("https://example.com/bericht.docx", tmp_path)

    assert page.filename == "example-com-bericht.docx"


async def test_nothing_recognisable_is_unsupported(serve, tmp_path: Path) -> None:
    serve(
        lambda request: httpx.Response(
            200, content=b"x", headers={"content-type": "application/octet-stream"}
        )
    )

    with pytest.raises(UnsupportedFormat):
        await fetch_page("https://example.com/download", tmp_path)


# ── Nur öffentliche Adressen ──────────────────────────────────────────────────


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1/",
        "http://10.0.0.1/",
        "http://172.16.0.1/",
        "http://192.168.1.1/",
        "http://169.254.169.254/",
        "http://[::1]/",
        "http://[fe80::1]/",
        "http://[fd00::1]/",
        "http://[::ffff:127.0.0.1]/",
        "http://0.0.0.0/",
        "file:///etc/passwd",
        "ftp://example.com/",
        "https:///pfad",
        "kein-url",
        "http://intern.example/",
        "http://beides.example/",
        "http://unbekannt.example/",
    ],
)
async def test_non_public_addresses_are_rejected(serve, tmp_path: Path, url: str) -> None:
    seen = serve(lambda request: html("nie"))

    with pytest.raises(InvalidUrl):
        await fetch_page(url, tmp_path)

    assert seen == [], "die Adresse wurde trotz Sperre angefragt"


async def test_a_public_ipv6_host_is_allowed(serve, tmp_path: Path) -> None:
    serve(lambda request: html("v6"))

    page = await fetch_page("https://v6.example/", tmp_path)

    assert page.filename == "v6.html"


async def test_a_redirect_into_a_private_network_is_rejected(serve, tmp_path: Path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.headers["host"] == "example.com":
            return httpx.Response(302, headers={"location": "http://192.168.1.1/"})
        return html("Router")

    seen = serve(handler)

    with pytest.raises(InvalidUrl):
        await fetch_page("https://example.com/", tmp_path)

    assert [request.headers["host"] for request in seen] == ["example.com"]


async def test_a_redirect_to_a_public_address_is_followed(serve, tmp_path: Path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/alt":
            return httpx.Response(301, headers={"location": "/neu"})
        return html("Neu")

    seen = serve(handler)

    page = await fetch_page("https://example.com/alt", tmp_path)

    assert page.filename == "neu.html"
    assert [request.url.path for request in seen] == ["/alt", "/neu"]


async def test_more_than_five_redirects_are_rejected(serve, tmp_path: Path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        hop = int(request.url.path.strip("/") or 0)
        return httpx.Response(302, headers={"location": f"/{hop + 1}"})

    seen = serve(handler)

    with pytest.raises(InvalidUrl):
        await fetch_page("https://example.com/0", tmp_path)

    assert len(seen) == 6


async def test_the_connection_goes_to_the_checked_address(
    serve, tmp_path: Path, rebinding_dns: None
) -> None:
    """Wechselt der Name zwischen Pruefung und Verbindung, gilt die geprueste Adresse."""
    seen = serve(lambda request: html("Rebinding"))

    await fetch_page("https://example.com/", tmp_path)

    assert [connect_target(request) for request in seen] == [PUBLIC]
    assert seen[0].headers["host"] == "example.com"
    assert seen[0].extensions["sni_hostname"] == "example.com"


async def test_the_pinned_request_keeps_path_and_port(serve, tmp_path: Path) -> None:
    seen = serve(lambda request: html("Port"))

    await fetch_page("https://example.com:8443/blog/post?a=1", tmp_path)

    assert str(seen[0].url) == f"https://{PUBLIC}:8443/blog/post?a=1"
    assert seen[0].headers["host"] == "example.com:8443"


async def test_every_redirect_hop_is_pinned_too(serve, tmp_path: Path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/alt":
            return httpx.Response(301, headers={"location": "https://v6.example/neu"})
        return html("Neu")

    seen = serve(handler)

    page = await fetch_page("https://example.com/alt", tmp_path)

    assert page.filename == "neu.html"
    assert [request.url.host for request in seen] == [PUBLIC, NAMES["v6.example"][0]]
    assert [request.headers["host"] for request in seen] == ["example.com", "v6.example"]


# ── Grenzen und Fehler ────────────────────────────────────────────────────────


class CountingStream(httpx.AsyncByteStream):
    """Ein Strom, der zählt, wie viele Blöcke abgerufen wurden."""

    def __init__(self, chunks: list[bytes]) -> None:
        self.chunks = chunks
        self.served = 0

    async def __aiter__(self) -> AsyncIterator[bytes]:
        for chunk in self.chunks:
            self.served += 1
            yield chunk


async def test_a_response_over_the_limit_aborts_before_the_end(
    serve, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("KAIMARKIT_MAX_FILE_SIZE_MB", "1")
    get_settings.cache_clear()
    stream = CountingStream([b"x" * (1024 * 1024)] * 4)
    serve(lambda request: httpx.Response(200, stream=stream, headers={"content-type": "text/html"}))

    with pytest.raises(FileTooLarge):
        await fetch_page("https://example.com/", tmp_path)

    assert 0 < stream.served < len(stream.chunks), "der Strom wurde bis zum Ende gelesen"


async def test_a_connection_error_becomes_a_conversion_error(serve, tmp_path: Path) -> None:
    def refuse(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("Connection refused")

    serve(refuse)

    with pytest.raises(InvalidUrl) as fehler:
        await fetch_page("https://example.com/", tmp_path)

    assert "example.com" in fehler.value.detail


async def test_an_error_status_is_no_document(serve, tmp_path: Path) -> None:
    serve(lambda request: httpx.Response(404, content=b"nicht da"))

    with pytest.raises(InvalidUrl) as fehler:
        await fetch_page("https://example.com/weg", tmp_path)

    assert "404" in fehler.value.detail


async def test_a_timeout_is_a_conversion_timeout(serve, tmp_path: Path) -> None:
    def slow(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out")

    serve(slow)

    with pytest.raises(ConversionTimeout):
        await fetch_page("https://example.com/", tmp_path)


# ── Nichts bleibt liegen ──────────────────────────────────────────────────────


@pytest.fixture
def tmp_spool(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    spool = tmp_path / "spool"
    spool.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(spool))
    return spool


async def test_the_page_is_removed_afterwards(serve, tmp_spool: Path) -> None:
    serve(lambda request: html("Example Domain"))

    async with fetched_page("https://example.com/") as page:
        assert page.path.is_file()
        assert page.path.is_relative_to(tmp_spool)

    assert list(tmp_spool.iterdir()) == []


async def test_the_page_is_removed_after_a_failure(serve, tmp_spool: Path) -> None:
    serve(lambda request: html("Example Domain"))

    with pytest.raises(RuntimeError):
        async with fetched_page("https://example.com/"):
            raise RuntimeError("die Engine scheitert")

    assert list(tmp_spool.iterdir()) == []
