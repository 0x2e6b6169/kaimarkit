"""Auskuenfte ueber den Dienst selbst."""

from __future__ import annotations

from fastapi import APIRouter

from .. import __version__
from ..models import HealthResponse

router = APIRouter(tags=["meta"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Antwortet sofort, auch waehrend Docling im Hintergrund laedt.

    Der Healthcheck des Containers haengt daran. Wuerde die Antwort auf die Modelle
    warten, gaelte der Start als Fehlschlag.
    """
    return HealthResponse(status="ok", version=__version__)
