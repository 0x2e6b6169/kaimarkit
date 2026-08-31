"""Die Fehler der Schnittstelle.

Jede Engine wandelt ihre eigenen Ausnahmen in eine dieser Klassen um; eine
bibliotheksspezifische Ausnahme darf die API nie erreichen. Klasse, HTTP-Status und
``code`` aus ``contracts/api.md`` stehen hier beieinander, damit sie nicht
auseinanderlaufen.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .models import ErrorCode, ErrorResponse


class ConversionError(Exception):
    """Basis aller Fehler, die als Fehlerantwort nach aussen gehen."""

    status_code: int = 500
    code: ErrorCode = ErrorCode.CONVERSION_FAILED

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class UnsupportedFormat(ConversionError):
    """Die Endung steht in keiner Praeferenzliste."""

    status_code = 415
    code = ErrorCode.UNSUPPORTED_FORMAT


class EngineUnsuitable(ConversionError):
    """Die ausdruecklich verlangte Engine kann dieses Format nicht.

    Sie wird nie still durch eine andere ersetzt.
    """

    status_code = 400
    code = ErrorCode.ENGINE_UNSUITABLE


class EngineUnavailable(ConversionError):
    """Die verlangte Engine ist nicht installiert oder defekt."""

    status_code = 400
    code = ErrorCode.ENGINE_UNAVAILABLE


class EngineFailed(ConversionError):
    """Die Engine ist an der Datei gescheitert."""

    status_code = 500
    code = ErrorCode.CONVERSION_FAILED


class FileTooLarge(ConversionError):
    """Die Datei ueberschreitet ``KAIMARKIT_MAX_FILE_SIZE_MB``."""

    status_code = 413
    code = ErrorCode.FILE_TOO_LARGE


class TooManyFiles(ConversionError):
    """Der Stapel ueberschreitet ``KAIMARKIT_MAX_FILES``."""

    status_code = 413
    code = ErrorCode.TOO_MANY_FILES


class ConversionTimeout(ConversionError):
    """Die Zeitgrenze ``KAIMARKIT_CONVERSION_TIMEOUT`` ist abgelaufen."""

    status_code = 504
    code = ErrorCode.CONVERSION_TIMEOUT


async def conversion_error_handler(request: Request, exc: ConversionError) -> JSONResponse:
    body = ErrorResponse(detail=exc.detail, code=exc.code)
    return JSONResponse(status_code=exc.status_code, content=body.model_dump(mode="json"))


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ConversionError, conversion_error_handler)
