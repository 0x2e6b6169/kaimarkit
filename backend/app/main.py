"""Die FastAPI-Anwendung.

Sie haengt drei Dinge ein, und die Reihenfolge entscheidet: Die letzte Einhaengung
faengt alles ab, was uebrig bleibt.

1. ``/api`` — die Router
2. ``/docs`` — die gebaute Dokumentation
3. ``/`` — das gebaute Frontend

Weil ``/docs`` der Dokumentation gehoert, zieht FastAPIs eigene Oberflaeche nach
``/api/docs`` um. Alles Maschinelle liegt damit unter ``/api``.

CORS bleibt aus: ein Container, eine Herkunft.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response
from starlette.types import Scope

from . import __version__
from .api import convert, meta
from .config import get_settings
from .errors import register_error_handlers

settings = get_settings()
logging.basicConfig(level=settings.log_level.upper())

app = FastAPI(
    title="kaimarkit",
    version=__version__,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

register_error_handlers(app)
app.include_router(meta.router, prefix="/api")
app.include_router(convert.router, prefix="/api")


class SpaStaticFiles(StaticFiles):
    """Statische Dateien, bei denen unbekannte Pfade die ``index.html`` bekommen.

    Nur so ueberlebt ein Neuladen auf einer Unterseite: Der Server kennt die Route
    nicht, das Frontend schon.
    """

    async def get_response(self, path: str, scope: Scope) -> Response:
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code == 404:
                return await super().get_response("index.html", scope)
            raise


# Beide Verzeichnisse werden nur eingehaengt, wenn es sie gibt. In der Entwicklung
# fehlen sie, und ohne diese Pruefung liesse sich das Backend allein nicht starten.
if settings.docs_dir.is_dir():
    app.mount("/docs", StaticFiles(directory=settings.docs_dir, html=True), name="docs")

if settings.static_dir.is_dir():
    app.mount("/", SpaStaticFiles(directory=settings.static_dir, html=True), name="spa")
