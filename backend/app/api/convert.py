"""Die Konvertierungsendpunkte.

Hier stehen ``/api/convert`` fuer eine einzelne Datei und ``/api/convert/batch``
fuer den Stapel.

Der Endpunkt kennt keine Engine. Er nimmt den Upload entgegen, laesst die Registry
waehlen und wandeln und formt das Ergebnis in die Antwort, die der Aufrufer im
``Accept``-Kopf verlangt hat. Alles Bibliotheksspezifische bleibt hinter
``app.converters``.
"""

from __future__ import annotations

import time
from pathlib import PurePosixPath
from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, File, Form, Header, Response, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from ..config import get_settings
from ..converters.base import ConvertOptions
from ..converters.registry import convert_with_fallback
from ..errors import ConversionError, TooManyFiles
from ..models import BatchResponse, ConversionEntry, ConversionStatus
from ..packaging import build_archive
from ..uploads import run_conversion, sanitize_filename, stored_upload

router = APIRouter(tags=["convert"])

#: Medientyp der Markdown-Antwort.
MARKDOWN_MEDIA_TYPE = "text/markdown; charset=utf-8"

#: Medientyp und Name des Stapelarchivs.
ZIP_MEDIA_TYPE = "application/zip"
ARCHIVE_NAME = "markdown.zip"


@router.post("/convert", response_model=None)
async def convert(
    file: Annotated[UploadFile, File(description="Die Eingabedatei.")],
    engine: Annotated[str | None, Form(description="Enginename oder auto.")] = None,
    ocr: Annotated[bool | None, Form(description="Ueberschreibt KAIMARKIT_OCR_ENABLED.")] = None,
    accept: Annotated[str, Header()] = "",
) -> Response:
    """Wandelt eine Datei nach Markdown.

    Die Antwort richtet sich nach ``Accept``: ``application/json`` liefert das
    vollstaendige Ergebnis, alles andere das nackte Markdown mit
    ``Content-Disposition``, damit ``curl -O`` unmittelbar die ``.md``-Datei ablegt.

    Ein Fehlschlag der Engine endet als Fehlercode, nicht als 200 mit
    ``status: "failed"`` — das gibt es nur im Stapel.
    """
    options = ConvertOptions(engine=engine or None, ocr=ocr)
    async with stored_upload(file) as stored:
        result = await run_conversion(lambda: convert_with_fallback(stored.path, options))
        filename = stored.filename

    if "application/json" in accept:
        entry = ConversionEntry(
            filename=filename,
            status=ConversionStatus.OK,
            markdown=result.markdown,
            engine=result.engine,
            warnings=result.warnings,
            duration_ms=result.duration_ms,
            error=None,
        )
        return JSONResponse(content=entry.model_dump(mode="json"))

    headers = {
        "Content-Disposition": _content_disposition(_markdown_name(filename)),
        "X-Engine": _header_safe(result.engine),
    }
    if result.warnings:
        headers["X-Warnings"] = _header_safe(" | ".join(result.warnings))
    return Response(content=result.markdown, media_type=MARKDOWN_MEDIA_TYPE, headers=headers)


@router.post("/convert/batch", response_model=None)
async def convert_batch(
    file: Annotated[list[UploadFile], File(description="Die Eingabedateien.")],
    engine: Annotated[str | None, Form(description="Enginename oder auto.")] = None,
    ocr: Annotated[bool | None, Form(description="Ueberschreibt KAIMARKIT_OCR_ENABLED.")] = None,
    accept: Annotated[str, Header()] = "",
) -> Response:
    """Wandelt mehrere Dateien in einem Aufruf.

    Eine gescheiterte Datei nimmt die uebrigen nicht mit: Sie bekommt einen Eintrag
    mit ``status: "failed"``, und im Archiv steht ihr Grund in ``_errors.txt``. Der
    Aufruf antwortet also auch dann mit 200, wenn jede einzelne Datei scheiterte.
    Nur zu viele Dateien scheitern als Anfrage.

    Ohne ``Accept: application/json`` kommt das ZIP.
    """
    settings = get_settings()
    if len(file) > settings.max_files:
        raise TooManyFiles(
            f"Hoechstens {settings.max_files} Dateien je Aufruf, angekommen sind {len(file)}"
        )

    options = ConvertOptions(engine=engine or None, ocr=ocr)
    entries = [await _convert_entry(upload, options) for upload in file]

    if "application/json" in accept:
        succeeded = sum(1 for entry in entries if entry.status == ConversionStatus.OK)
        body = BatchResponse(
            entries=entries,
            total=len(entries),
            succeeded=succeeded,
            failed=len(entries) - succeeded,
        )
        return JSONResponse(content=body.model_dump(mode="json"))

    return StreamingResponse(
        build_archive(entries),
        media_type=ZIP_MEDIA_TYPE,
        headers={"Content-Disposition": _content_disposition(ARCHIVE_NAME)},
    )


async def _convert_entry(upload: UploadFile, options: ConvertOptions) -> ConversionEntry:
    """Wandelt eine Datei des Stapels und faengt ihren Fehler ein.

    Der Kontextmanager loescht die temporaere Datei auch dann, wenn die Engine
    scheitert — jede Datei des Stapels raeumt sich selbst weg.
    """
    started = time.perf_counter()
    try:
        async with stored_upload(upload) as stored:
            result = await run_conversion(lambda: convert_with_fallback(stored.path, options))
            filename = stored.filename
    except ConversionError as exc:
        return ConversionEntry(
            filename=sanitize_filename(upload.filename),
            status=ConversionStatus.FAILED,
            duration_ms=int((time.perf_counter() - started) * 1000),
            error=exc.detail,
        )
    return ConversionEntry(
        filename=filename,
        status=ConversionStatus.OK,
        markdown=result.markdown,
        engine=result.engine,
        warnings=result.warnings,
        duration_ms=result.duration_ms,
    )


def _markdown_name(filename: str) -> str:
    """Derselbe Name mit der Endung ``.md``."""
    stem = PurePosixPath(filename).stem or filename
    return f"{stem}.md"


def _content_disposition(filename: str) -> str:
    """Baut den Kopf so, dass auch ein Name mit Umlauten heil ankommt.

    Kopfzeilen vertragen kein UTF-8. Deshalb steht der Name zweimal darin: einmal
    auf ASCII heruntergebrochen fuer alte Clients, einmal prozentkodiert nach
    RFC 5987 fuer alle uebrigen.
    """
    ascii_name = _header_safe(filename).replace('"', "_").replace("\\", "_")
    return f"attachment; filename=\"{ascii_name}\"; filename*=UTF-8''{quote(filename, safe='')}"


def _header_safe(value: str) -> str:
    """Ersetzt alles, was sich nicht als ASCII schreiben laesst."""
    return value.encode("ascii", "replace").decode("ascii")
