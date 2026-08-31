"""Auskuenfte ueber den Dienst selbst."""

from __future__ import annotations

from fastapi import APIRouter

from .. import __version__
from ..config import get_settings
from ..converters import registry
from ..errors import EngineUnavailable
from ..models import CapabilitiesResponse, EngineState, HealthResponse, Limits

router = APIRouter(tags=["meta"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Antwortet sofort, auch waehrend Docling im Hintergrund laedt.

    Der Healthcheck des Containers haengt daran. Wuerde die Antwort auf die Modelle
    warten, gaelte der Start als Fehlschlag.
    """
    return HealthResponse(status="ok", version=__version__)


@router.get("/capabilities", response_model=CapabilitiesResponse)
async def capabilities() -> CapabilitiesResponse:
    """Was dieser Dienst jetzt kann.

    Die Formate kommen aus der Faehigkeitsmatrix der Registry, nicht aus einer
    zweiten Liste — sonst versprechen Auskunft und Umwandlung Verschiedenes. Eine
    Endung ohne einsatzbereite Engine bleibt weg: Das Frontend soll nichts
    anbieten, was ohnehin scheitert.
    """
    settings = get_settings()
    formats = {ext: names for ext in registry.PREFERENCES if (names := registry.engines_for(ext))}
    engines = {name: _state(name) for name in (*registry.ENGINE_NAMES, registry.PASSTHROUGH)}
    return CapabilitiesResponse(
        formats=formats,
        engines=engines,
        limits=Limits(
            max_file_size_mb=settings.max_file_size_mb,
            max_files=settings.max_files,
            conversion_timeout_s=settings.conversion_timeout,
        ),
        ocr_available=settings.ocr_enabled,
        default_engine=settings.default_engine,
    )


def _state(name: str) -> EngineState:
    """Der Zustand einer Engine, wie ihn ``contracts/api.md`` beschreibt.

    ``warming`` heisst: Das Modul ist da, die Engine arbeitet aber noch nicht —
    bei Docling laden dann gerade die Modelle.
    """
    try:
        converter = registry.get_converter(name)
    except EngineUnavailable:
        return EngineState.UNAVAILABLE
    return EngineState.READY if converter.available() else EngineState.WARMING
