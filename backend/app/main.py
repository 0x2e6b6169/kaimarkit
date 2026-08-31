"""Die FastAPI-Anwendung.

Sie haengt drei Dinge ein, und die Reihenfolge entscheidet: Die letzte Einhaengung
faengt alles ab, was uebrig bleibt.

1. ``/api`` — die Router
2. ``/docs`` — die gebaute Dokumentation
3. ``/`` — das gebaute Frontend

Weil ``/docs`` der Dokumentation gehoert, zieht FastAPIs eigene Oberflaeche nach
``/api/docs`` um. Alles Maschinelle liegt damit unter ``/api``.

Beim Hochfahren stoesst der Lifespan das Vorladen von Docling an. Er wartet nicht
darauf: Der Dienst ist sofort bedienbar, Docling kommt hinterher.

CORS bleibt aus: ein Container, eine Herkunft.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response
from starlette.types import Scope

from . import __version__
from .api import convert, meta
from .config import get_settings
from .converters import docling
from .errors import register_error_handlers

settings = get_settings()
logging.basicConfig(level=settings.log_level.upper())


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Stoesst beim Hochfahren das Vorladen von Docling an.

    Der Aufruf kehrt sofort zurueck: Er startet einen Daemon-Thread, der Modelle
    laedt. Ohne ihn begaenne das Laden erst mit der ersten Wandlung, und der erste
    Nutzer wartete minutenlang. Fehlt die Bibliothek, bleibt es folgenlos — der
    Thread faengt den ``ImportError`` selbst ab, ``/api/capabilities`` meldet
    Docling danach als ``unavailable``.

    Der Weg fuehrt ueber das Adaptermodul; ``main.py`` kennt Docling nicht.
    """
    docling.start_warmup()
    yield


app = FastAPI(
    title="kaimarkit",
    version=__version__,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
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
