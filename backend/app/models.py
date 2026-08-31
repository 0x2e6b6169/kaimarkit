"""Schemas der HTTP-Schnittstelle.

Diese Datei, ``contracts/api.md`` und ``frontend/src/types.ts`` beschreiben dieselbe
Schnittstelle und werden gemeinsam geaendert. Siehe CLAUDE.md, Konvention 1.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class ConversionStatus(StrEnum):
    OK = "ok"
    FAILED = "failed"


class EngineState(StrEnum):
    READY = "ready"
    WARMING = "warming"
    UNAVAILABLE = "unavailable"


class ErrorCode(StrEnum):
    FILE_TOO_LARGE = "file_too_large"
    TOO_MANY_FILES = "too_many_files"
    UNSUPPORTED_FORMAT = "unsupported_format"
    ENGINE_UNSUITABLE = "engine_unsuitable"
    ENGINE_UNAVAILABLE = "engine_unavailable"
    CONVERSION_FAILED = "conversion_failed"
    CONVERSION_TIMEOUT = "conversion_timeout"


class ErrorResponse(BaseModel):
    detail: str
    code: ErrorCode


class ConversionEntry(BaseModel):
    """Ergebnis fuer genau eine Datei.

    ``markdown`` und ``error`` sind immer vorhanden, damit ein Client nicht auf ihr
    Fehlen pruefen muss: bei ``ok`` ist ``error`` None, bei ``failed`` ``markdown``.
    """

    filename: str
    status: ConversionStatus
    markdown: str | None = None
    engine: str | None = None
    warnings: list[str] = Field(default_factory=list)
    duration_ms: int
    error: str | None = None


class BatchResponse(BaseModel):
    entries: list[ConversionEntry]
    total: int
    succeeded: int
    failed: int


class Limits(BaseModel):
    max_file_size_mb: int
    max_files: int
    conversion_timeout_s: int


class CapabilitiesResponse(BaseModel):
    """Was dieser Dienst kann.

    In ``formats`` ist die Reihenfolge die Praeferenz: Der erste Eintrag wird bei
    ``engine=auto`` genommen. Engines im Zustand ``unavailable`` erscheinen hier nicht.
    """

    formats: dict[str, list[str]]
    engines: dict[str, EngineState]
    limits: Limits
    ocr_available: bool
    default_engine: str


class HealthResponse(BaseModel):
    status: Literal["ok"]
    version: str
