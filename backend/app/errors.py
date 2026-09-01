"""Die Fehler der Schnittstelle.

Jede Engine wandelt ihre eigenen Ausnahmen in eine dieser Klassen um; eine
bibliotheksspezifische Ausnahme darf die API nie erreichen. Klasse, HTTP-Status und
``code`` aus ``contracts/api.md`` stehen hier beieinander, damit sie nicht
auseinanderlaufen.

Hier faellt auch der Pfad aus der Meldung. Die Engines reichen den Wortlaut ihrer
Bibliothek weiter, und der nennt die Datei so, wie sie im Dienst kurz lag:
``/tmp/tmpkxfozixp/kaputt.pdf``. Diese Meldung steht spaeter im Browser in der Zeile
der Datei und im Stapel in ``_errors.txt`` — vor den Augen dessen, der die Datei
hochgeladen hat. Ihm sagt das Verzeichnis nichts, und nach dem ``finally`` gibt es
das Verzeichnis ohnehin nicht mehr. ``__init__`` kuerzt jeden Pfad deshalb auf seinen
letzten Bestandteil, also auf den Namen der Datei, den der Aufrufer kennt. Der Grund
bleibt Wort fuer Wort stehen.

Die Kuerzung sitzt in ``ConversionError`` und nicht in den drei Adaptern: Alle drei
bauen ihre Meldung gleich — eigener Satz, dann der Wortlaut der Bibliothek —, und
den Pfad schleppt jede Bibliothek auf ihre Weise mit. An dieser einen Stelle gilt sie
auch fuer den Durchreicher der Registry, fuer die Warnung des Rueckfalls und fuer die
Engine, die es hier noch nicht gibt.

Was die Antwort nicht mehr sagt, sagt das Protokoll: ``__init__`` schreibt den
ungekuerzten Wortlaut einmal ins Log, sobald er sich vom gekuerzten unterscheidet.
Der Stapel faengt seine Fehler selbst ab, sie erreichen den Ausnahmebehandler also
nie — nur im Konstruktor ist der volle Wortlaut sicher zu haben.
"""

from __future__ import annotations

import logging
import re

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .models import ErrorCode, ErrorResponse

log = logging.getLogger(__name__)

#: Ein absoluter Pfad mit mindestens einem Verzeichnis vor dem Namen.
#:
#: Das ``(?<![\w:/])`` haelt die Adressen heraus: In ``https://host/a/b`` steht vor
#: jedem Schraegstrich ein Wortzeichen, ein Doppelpunkt oder ein zweiter
#: Schraegstrich, und keiner davon beginnt einen Pfad. Ein einzelner Schraegstrich
#: wie in „ein/aus“ bleibt ebenfalls stehen, weil mindestens zwei Bestandteile
#: verlangt sind. Am Ende faellt Satzzeichen weg, damit aus ``…/kaputt.pdf:`` der
#: Name ohne Doppelpunkt wird.
_PATH = re.compile(r"""(?<![\w:/])/(?:[^/\s'"]+/)+[^/\s'",;:]*""")


def _basename(match: re.Match[str]) -> str:
    """Der letzte Bestandteil eines Pfades, sonst der Pfad selbst."""
    parts = [part for part in match.group(0).split("/") if part]
    return parts[-1] if parts else match.group(0)


def shorten(detail: str) -> str:
    """Ersetzt jeden Pfad in der Meldung durch den blossen Dateinamen."""
    return _PATH.sub(_basename, detail)


class ConversionError(Exception):
    """Basis aller Fehler, die als Fehlerantwort nach aussen gehen."""

    status_code: int = 500
    code: ErrorCode = ErrorCode.CONVERSION_FAILED

    #: Der ungekuerzte Wortlaut, so wie die Engine ihn gebaut hat. Er geht nie nach
    #: aussen; er steht im Protokoll und hilft beim Nachsehen im Betrieb.
    raw_detail: str

    def __init__(self, detail: str) -> None:
        self.raw_detail = detail
        self.detail = shorten(detail)
        super().__init__(self.detail)
        if self.detail != detail:
            log.warning("Fehlermeldung gekuerzt. Ungekuerzt: %s", detail)


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
