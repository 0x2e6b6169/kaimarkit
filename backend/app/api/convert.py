"""Die Konvertierungsendpunkte.

Hier steht ``/api/convert`` fuer eine einzelne Datei; ``/api/convert/batch`` kommt
aus BE-8 und haengt sich an denselben Router.

Der Endpunkt kennt keine Engine. Er nimmt den Upload entgegen, laesst die Registry
waehlen und wandeln und formt das Ergebnis in die Antwort, die der Aufrufer im
``Accept``-Kopf verlangt hat. Alles Bibliotheksspezifische bleibt hinter
``app.converters``.
"""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, File, Form, Header, Response, UploadFile
from fastapi.responses import JSONResponse

from ..converters.base import ConvertOptions
from ..converters.registry import convert_with_fallback
from ..models import ConversionEntry, ConversionStatus
from ..uploads import run_conversion, stored_upload

router = APIRouter(tags=["convert"])

#: Medientyp der Markdown-Antwort.
MARKDOWN_MEDIA_TYPE = "text/markdown; charset=utf-8"


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
