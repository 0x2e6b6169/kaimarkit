"""Eine Seite aus dem Netz holen, prüfen und benennen.

Drei Dinge passieren hier. Die Adresse wird geprüft — nur öffentliches http(s),
und das vor jedem Sprung einer Weiterleitung. Die Antwort wandert in Blöcken in
ein temporäres Verzeichnis, mit derselben Größenprüfung wie ein Upload. Und die
Datei bekommt einen Namen aus dem ``<title>`` der Seite, damit der Nutzer sie
später wiedererkennt.

Danach geht die Datei denselben Weg wie ein Upload: Registry, Engine, Rückfall.
Einen zweiten Konvertierungspfad gibt es nicht.

Warum die Sperre: Der Dienst steht auf dem VPS im selben Docker-Netz wie Traefik
und Authelia. Ein ``/api/convert/url`` ohne Prüfung wäre ein Sprungbrett dorthin —
und zu ``169.254.169.254``, wo Cloud-Anbieter ihre Metadaten anbieten. Deshalb
wird der Hostname aufgelöst und **jede** zurückgegebene Adresse geprüft; ein Name,
der auf eine öffentliche und eine private Adresse zeigt, wird abgewiesen.

Bekannte Einschränkung: Geprüft wird die Auflösung vor dem Verbindungsaufbau, und
``httpx`` löst den Namen danach noch einmal auf. Ein Name, dessen Antwort zwischen
beiden Aufrufen wechselt, käme durch. Das ist derselbe Rest, den jede Prüfung
dieser Bauart lässt; dagegen hilft nur, die Verbindung selbst an die geprüfte
Adresse zu binden.

Diese Datei ist die einzige außerhalb der Tests, die ``httpx`` importiert. Was
``httpx`` an Fehlern wirft, endet hier als ``ConversionError``; kein
``httpx.ConnectError`` erreicht die API.
"""

from __future__ import annotations

import html
import ipaddress
import re
import socket
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from urllib.parse import urljoin, urlsplit

import anyio
import anyio.to_thread
import httpx

from .config import Settings, get_settings
from .converters.registry import PREFERENCES
from .errors import ConversionTimeout, FileTooLarge, InvalidUrl, UnsupportedFormat
from .uploads import _semaphore

#: Wie oft einer Weiterleitung gefolgt wird. Keine Betriebsgröße — fünf Sprünge
#: reichen jeder echten Seite, und mehr sind ein Kreis.
REDIRECT_LIMIT = 5

#: Längste Namensableitung. Auch keine Betriebsgröße.
SLUG_LENGTH = 80

#: Name, wenn weder Titel noch Adresse ein Zeichen hergeben.
FALLBACK_SLUG = "seite"

#: Wie viel vom Anfang der Seite nach dem ``<title>`` durchsucht wird.
TITLE_WINDOW = 64 * 1024

#: Inhaltstyp auf Endung. Was hier fehlt, entscheidet die Endung im Pfad.
EXTENSIONS: dict[str, str] = {
    "text/html": ".html",
    "application/xhtml+xml": ".html",
    "application/pdf": ".pdf",
    "application/epub+zip": ".epub",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "application/vnd.oasis.opendocument.text": ".odt",
    "application/rtf": ".rtf",
    "text/rtf": ".rtf",
    "text/markdown": ".md",
    "text/plain": ".txt",
    "text/csv": ".csv",
    "application/json": ".json",
    "text/xml": ".xml",
    "application/xml": ".xml",
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/tiff": ".tiff",
}

_UMLAUTS = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"})
_NOT_ALNUM = re.compile(r"[^a-z0-9]+")
_TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_WHITESPACE = re.compile(r"\s+")


@dataclass(frozen=True, slots=True)
class FetchedPage:
    """Die abgelegte Datei und der Name, unter dem sie dem Aufrufer erscheint."""

    path: Path
    filename: str


# ── Namen ─────────────────────────────────────────────────────────────────────


def slugify(text: str) -> str:
    """Kleinbuchstaben, Umlaute umgeschrieben, alles Übrige zu ``-``.

    Mehrfache Bindestriche fallen zusammen, die Ränder werden beschnitten, und
    nach dem Kürzen auf ``SLUG_LENGTH`` noch einmal — sonst endete ein Name auf
    einem Bindestrich.
    """
    slug = _NOT_ALNUM.sub("-", text.lower().translate(_UMLAUTS)).strip("-")
    return slug[:SLUG_LENGTH].strip("-")


def derive_filename(url: str, ext: str, title: str | None) -> str:
    """Der Dateiname: aus dem Titel, sonst aus Host und Pfad, immer mit Endung.

    Die Endung im Pfad kommt nicht doppelt vor: ``paper.pdf`` wird zu
    ``…-paper.pdf``, nicht zu ``…-paper-pdf.pdf``. Eine andere Endung im Pfad bleibt
    Teil des Namens, weil sie dort etwas bedeutet — ``2301.00001`` ist kein
    ``2301`` mit Endung.
    """
    slug = slugify(title) if title else ""
    if not slug:
        parts = urlsplit(url)
        path = PurePosixPath(parts.path or "/")
        if path.suffix.lower() == ext:
            path = path.with_suffix("")
        slug = slugify(f"{parts.hostname or ''} {path}")
    return f"{slug or FALLBACK_SLUG}{ext}"


def find_title(path: Path, encoding: str | None) -> str | None:
    """Der ``<title>`` aus dem Anfang der Datei, entschärft und bereinigt."""
    with path.open("rb") as source:
        head = source.read(TITLE_WINDOW)
    try:
        text = head.decode(encoding or "utf-8", errors="replace")
    except LookupError:
        text = head.decode("utf-8", errors="replace")
    match = _TITLE.search(text)
    if match is None:
        return None
    title = _WHITESPACE.sub(" ", html.unescape(match.group(1))).strip()
    return title or None


def extension_for(content_type: str | None, url: str) -> str:
    """Die Endung aus dem Inhaltstyp, sonst aus dem Pfad; nichts Erkennbares → 415."""
    media_type = (content_type or "").split(";", 1)[0].strip().lower()
    if media_type in EXTENSIONS:
        return EXTENSIONS[media_type]
    suffix = PurePosixPath(urlsplit(url).path).suffix.lower()
    if suffix in PREFERENCES:
        return suffix
    raise UnsupportedFormat(
        f"Für {url} ist kein Format erkennbar: Inhaltstyp {media_type or 'unbekannt'}, "
        f"Endung {suffix or 'keine'}."
    )


# ── Nur öffentliche Adressen ──────────────────────────────────────────────────


def _resolve(host: str) -> list[str]:
    """Alle Adressen eines Namens. Tests ersetzen diese Funktion."""
    return [
        info[4][0]
        for info in socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    ]


async def check_public(url: str) -> None:
    """Wirft ``InvalidUrl``, wenn die Adresse nicht öffentlich erreichbar ist.

    Geprüft wird das Schema, dann jede Adresse, auf die der Host zeigt. Loopback,
    private Netze, Link-local und alles, was ``is_global`` verneint, sind gesperrt.
    """
    parts = urlsplit(url)
    if parts.scheme not in {"http", "https"}:
        raise InvalidUrl(f"{url}: nur http- und https-Adressen werden geholt.")
    host = parts.hostname
    if not host:
        raise InvalidUrl(f"{url}: die Adresse nennt keinen Host.")
    for address in await _addresses_of(host):
        if not address.is_global:
            raise InvalidUrl(f"{host} zeigt auf {address}, und das ist keine öffentliche Adresse.")


async def _addresses_of(host: str) -> list[ipaddress.IPv4Address | ipaddress.IPv6Address]:
    """Die Adressen hinter einem Host — die eine, wenn er selbst eine ist."""
    try:
        return [ipaddress.ip_address(host)]
    except ValueError:
        pass
    try:
        resolved = await anyio.to_thread.run_sync(_resolve, host)
    except socket.gaierror as exc:
        raise InvalidUrl(f"{host} lässt sich nicht auflösen: {exc}") from exc
    if not resolved:
        raise InvalidUrl(f"{host} lässt sich nicht auflösen.")
    return [ipaddress.ip_address(address) for address in resolved]


# ── Holen ─────────────────────────────────────────────────────────────────────


def _transport() -> httpx.AsyncBaseTransport | None:
    """Der Transport des Clients. ``None`` ist das Netz; Tests hängen eine Attrappe ein."""
    return None


async def fetch_page(url: str, directory: Path) -> FetchedPage:
    """Holt die Seite nach ``directory`` und leitet ihren Namen ab.

    Weiterleitungen werden von Hand verfolgt, damit jedes Ziel vor dem Sprung
    geprüft wird. Die Zeitgrenze ``KAIMARKIT_URL_TIMEOUT`` gilt für den ganzen
    Abruf, alle Sprünge eingeschlossen.
    """
    settings = get_settings()
    target = url
    try:
        with anyio.fail_after(settings.url_timeout):
            async with httpx.AsyncClient(
                transport=_transport(),
                follow_redirects=False,
                timeout=settings.url_timeout,
                headers={"User-Agent": f"kaimarkit/{settings.service_version}"},
            ) as client:
                for _ in range(REDIRECT_LIMIT + 1):
                    await check_public(target)
                    async with client.stream("GET", target) as response:
                        if response.is_redirect:
                            target = urljoin(target, response.headers["location"])
                            continue
                        if not response.is_success:
                            raise InvalidUrl(f"{target} antwortet mit {response.status_code}.")
                        return await _store(response, target, directory, settings)
                raise InvalidUrl(f"{url} leitet öfter als {REDIRECT_LIMIT}-mal weiter.")
    except (TimeoutError, httpx.TimeoutException) as exc:
        raise ConversionTimeout(
            f"{target} hat innerhalb von {settings.url_timeout} s nicht geantwortet."
        ) from exc
    except httpx.HTTPError as exc:
        raise InvalidUrl(f"{target} ist nicht erreichbar: {exc}") from exc


async def _store(
    response: httpx.Response, url: str, directory: Path, settings: Settings
) -> FetchedPage:
    """Schreibt die Antwort in Blöcken und bricht ab, sobald sie zu groß wird."""
    ext = extension_for(response.headers.get("content-type"), url)
    download = directory / f"download{ext}"
    written = 0
    with download.open("wb") as sink:
        async for chunk in response.aiter_bytes():
            written += len(chunk)
            if written > settings.max_file_size_bytes:
                raise FileTooLarge(f"{url} überschreitet {settings.max_file_size_mb} MB")
            sink.write(chunk)
    title = find_title(download, response.charset_encoding) if ext == ".html" else None
    filename = derive_filename(url, ext, title)
    path = download.rename(directory / filename)
    return FetchedPage(path=path, filename=filename)


@asynccontextmanager
async def fetched_page(url: str) -> AsyncIterator[FetchedPage]:
    """Holt die Seite in ein eigenes Verzeichnis und räumt es danach weg.

    Der Abruf läuft unter demselben Semaphor wie die Umwandlungen: Wer zwanzig
    Adressen auf einmal schickt, belegt nicht zwanzig Verbindungen zugleich. Die
    Umwandlung danach holt sich den Platz erneut, unter ihrer eigenen Zeitgrenze.

    Das Verzeichnis fällt im ``finally`` mitsamt Inhalt weg — der Dienst speichert
    nichts, auch nicht, was er selbst geholt hat.
    """
    spool = TemporaryDirectory()
    try:
        async with _semaphore():
            page = await fetch_page(url, Path(spool.name))
        yield page
    finally:
        spool.cleanup()
