"""Pandoc hinter dem Converter-Protokoll.

Pandoc ist die einzige Engine, die kein Python-Modul ist, sondern ein Programm im
PATH. Deshalb heisst ``available()`` hier: liegt die Binaerdatei da? Fehlt sie,
endet jeder Zugriff in ``EngineUnavailable`` — schon in ``get_converter()``, damit
``/api/capabilities`` die Engine als ``unavailable`` meldet und nicht als
``warming``. Ein ``FileNotFoundError`` des Unterprozesses erreicht die API nie.

Der Aufruf laeuft ueber eine Argumentliste, nie ueber eine Shell. ``--sandbox`` ist
der Grund, warum dieser Dienst fremde Dateien durch Pandoc schicken darf: Pandoc
liest und schreibt damit nur, was auf der Kommandozeile steht. Ein ePub oder eine
LaTeX-Datei kann sonst auf beliebige Pfade des Servers zeigen.

Pandoc liest kein PDF. ``.pdf`` fehlt deshalb in der Endungsmenge, und die Registry
reicht PDF gar nicht erst hierher.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from ..config import get_settings
from ..errors import ConversionTimeout, EngineFailed, EngineUnavailable, UnsupportedFormat
from .base import ConversionResult, ConvertOptions

NAME = "pandoc"

#: Das Programm, so wie es im PATH heisst.
BINARY = "pandoc"

#: Alles, wofuer die Praeferenzliste in ``registry.py`` diese Engine nennt.
EXTENSIONS: tuple[str, ...] = (
    ".docx",
    ".epub",
    ".html",
    ".htm",
    ".odt",
    ".rtf",
    ".tex",
    ".rst",
    ".org",
)

#: Feste Argumente jedes Aufrufs. ``--sandbox`` sperrt Pandoc auf die genannte Datei
#: ein, ``gfm-raw_html`` wirft eingebettetes HTML weg, und ``--wrap=none`` laesst die
#: Zeilen so lang, wie der Absatz ist — umgebrochenes Markdown liest sich in einem
#: Diff schlecht.
ARGUMENTS: tuple[str, ...] = ("--sandbox", "--to=gfm-raw_html", "--wrap=none")

#: So viele Zeilen von stderr wandern in die Fehlermeldung.
STDERR_LINES = 5


class PandocConverter:
    """Der Adapter. Haelt keinen Zustand: jeder Aufruf ist ein eigener Prozess."""

    name = NAME
    extensions = EXTENSIONS

    def available(self) -> bool:
        """Ob das Programm im PATH liegt. Wirft nie."""
        return shutil.which(BINARY) is not None

    def convert(self, path: Path, opts: ConvertOptions) -> ConversionResult:
        """Wandelt die Datei. ``opts`` bleibt ungenutzt: Pandoc kennt kein OCR."""
        ext = path.suffix.lower()
        if ext not in self.extensions:
            raise UnsupportedFormat(f"Pandoc liest {ext or 'Dateien ohne Endung'} nicht.")

        command = [_binary(), *ARGUMENTS, str(path)]
        timeout = get_settings().pandoc_timeout
        try:
            # Die Zeitgrenze haengt am Unterprozess selbst. Laeuft sie ab, toetet
            # ``subprocess.run`` den Prozess, bevor die Ausnahme herauskommt — er
            # laeuft also nicht unbeaufsichtigt weiter.
            process = subprocess.run(
                command,
                capture_output=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise ConversionTimeout(
                f"Pandoc hat {path.name} in {timeout} s nicht gewandelt."
            ) from exc
        except OSError as exc:  # Programm verschwunden oder nicht ausfuehrbar
            raise EngineUnavailable(f"Pandoc laesst sich nicht aufrufen: {exc}") from exc

        if process.returncode != 0:
            raise EngineFailed(
                f"Pandoc ist an {path.name} gescheitert: {_head(process.stderr)}"
            )

        warnings = [f"Pandoc meldet zu {path.name}: {_head(process.stderr)}"]
        return ConversionResult(
            markdown=process.stdout,
            engine=self.name,
            warnings=warnings if process.stderr.strip() else [],
        )


def _binary() -> str:
    """Der Pfad zum Programm. Fehlt es, endet der Zugriff hier."""
    found = shutil.which(BINARY)
    if found is None:
        raise EngineUnavailable("Pandoc ist nicht installiert: kein pandoc im PATH.")
    return found


def _head(stderr: str) -> str:
    """Die ersten Zeilen von stderr, zu einer Meldung zusammengezogen."""
    lines = [line.strip() for line in stderr.splitlines() if line.strip()]
    if not lines:
        return "keine Meldung auf stderr."
    return " ".join(lines[:STDERR_LINES])


_CONVERTER = PandocConverter()


def get_converter() -> PandocConverter:
    """Was die Registry aufruft. Ohne Programm im PATH gibt es keinen Konverter."""
    _binary()
    return _CONVERTER
