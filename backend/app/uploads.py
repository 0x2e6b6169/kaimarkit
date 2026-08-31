"""Uploads entgegennehmen und die Last begrenzen.

Drei Dinge passieren hier. Der Dateiname wird gesaeubert, der Inhalt wandert in
Bloecken in eine temporaere Datei, und der blockierende Aufruf der Engine laeuft
unter Semaphor und Zeitgrenze.

Der Dienst speichert nichts: Jede temporaere Datei wird im ``finally`` geloescht,
auch wenn die Umwandlung scheitert.
"""

from __future__ import annotations

import asyncio
import re
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path, PurePosixPath
from tempfile import NamedTemporaryFile

import anyio
import anyio.to_thread
from fastapi import UploadFile

from .config import get_settings
from .errors import ConversionTimeout, FileTooLarge

#: Blockgroesse beim Empfang. Kleiner Wert, damit die Groessenpruefung frueh greift.
CHUNK_SIZE = 1024 * 1024

#: Name fuer Uploads ohne brauchbaren Dateinamen.
FALLBACK_NAME = "upload"

#: Steuerzeichen haben in einem Dateinamen nichts zu suchen.
_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")

#: Laengste Dateinamen der gaengigen Dateisysteme.
_MAX_NAME_LENGTH = 255


def sanitize_filename(name: str | None) -> str:
    """Behaelt vom Dateinamen nur den Namensteil.

    Ein Client bestimmt diesen Namen, also darf er weder ein Verzeichnis nennen
    noch aus dem Zielverzeichnis herausfuehren. Uebrig bleibt, was hinter dem
    letzten Trennzeichen steht — bei ``../../etc/passwd`` also ``passwd``.
    """
    if not name:
        return FALLBACK_NAME
    candidate = PurePosixPath(name.replace("\\", "/")).name
    candidate = _CONTROL_CHARS.sub("", candidate).strip()
    if not candidate or candidate in {".", ".."}:
        return FALLBACK_NAME
    # Von vorn kuerzen, damit die Endung erhalten bleibt: Sie waehlt die Engine.
    return candidate[-_MAX_NAME_LENGTH:]


@dataclass(frozen=True, slots=True)
class StoredUpload:
    """Die abgelegte Datei und der gesaeuberte Name, unter dem sie ankam."""

    path: Path
    filename: str


@asynccontextmanager
async def stored_upload(upload: UploadFile) -> AsyncIterator[StoredUpload]:
    """Nimmt einen Upload in Bloecken entgegen und raeumt ihn danach weg.

    Die Groesse wird waehrend des Empfangs geprueft, nicht danach: Wer erst nach
    dem vollstaendigen Einlesen misst, hat die Datei bereits im Speicher. Sobald
    ``KAIMARKIT_MAX_FILE_SIZE_MB`` ueberschritten ist, bricht der Empfang ab.
    """
    settings = get_settings()
    filename = sanitize_filename(upload.filename)
    tmp = NamedTemporaryFile(suffix=PurePosixPath(filename).suffix, delete=False)
    path = Path(tmp.name)
    try:
        try:
            written = 0
            while chunk := await upload.read(CHUNK_SIZE):
                written += len(chunk)
                if written > settings.max_file_size_bytes:
                    raise FileTooLarge(f"{filename} ueberschreitet {settings.max_file_size_mb} MB")
                tmp.write(chunk)
        finally:
            tmp.close()
        yield StoredUpload(path=path, filename=filename)
    finally:
        path.unlink(missing_ok=True)


@lru_cache
def _semaphore() -> asyncio.Semaphore:
    """Begrenzt die gleichzeitigen Umwandlungen auf ``KAIMARKIT_MAX_CONCURRENT``.

    Ohne diese Bremse legen drei parallele Docling-Laeufe den Container lahm.
    """
    return asyncio.Semaphore(get_settings().max_concurrent)


async def run_conversion[T](func: Callable[[], T]) -> T:
    """Fuehrt den blockierenden Aufruf im Thread aus, unter Semaphor und Zeitgrenze.

    Bekannte Einschraenkung: ``KAIMARKIT_CONVERSION_TIMEOUT`` beendet den
    Wartevorgang, nicht den Thread. Der laeuft weiter, bis er von selbst fertig
    ist, und belegt so lange einen Platz im Threadpool. Siehe ``docs/grenzen.md``.
    """
    settings = get_settings()
    async with _semaphore():
        try:
            with anyio.fail_after(settings.conversion_timeout):
                return await anyio.to_thread.run_sync(func, abandon_on_cancel=True)
        except TimeoutError as exc:
            raise ConversionTimeout(
                f"Die Umwandlung hat die Zeitgrenze von {settings.conversion_timeout} s "
                "ueberschritten"
            ) from exc
