"""MarkItDown hinter dem Converter-Protokoll.

MarkItDown ist die schnelle Engine: keine Modelle, kein OCR, dafuer breite
Formatabdeckung. Einen LLM-Client setzt der Adapter bewusst nicht ein: Kein Bild
wird beschrieben. In ``.docx``, ``.html`` und ``.epub`` bleibt davon der Alt-Text
stehen. Aus einem PDF uebernimmt MarkItDown dagegen gar nichts — dort faellt jedes
Bild ersatzlos weg, und ``convert()`` legt dafuer eine Warnung dazu.

Achtung beim Lesen: Diese Datei heisst wie die Bibliothek. ``from markitdown import
MarkItDown`` meint trotzdem die Bibliothek, denn Python 3 importiert absolut; das
Nachbarmodul erreicht man nur ueber ``from . import markitdown``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..errors import EngineFailed, EngineUnavailable
from .base import ConversionResult, ConvertOptions

#: Alles, wofuer die Praeferenzliste in ``registry.py`` diese Engine nennt.
EXTENSIONS: tuple[str, ...] = (
    ".pdf",
    ".docx",
    ".epub",
    ".pptx",
    ".xlsx",
    ".html",
    ".htm",
    ".csv",
    ".json",
    ".xml",
    ".txt",
    ".png",
    ".jpg",
    ".jpeg",
    ".tiff",
)


def _pdf_image_warnings(path: Path) -> list[str]:
    """Warnt bei einem PDF davor, dass MarkItDown die Bilder weglaesst.

    MarkItDown zieht aus einem PDF nur die Textebene. Ein Bild hinterlaesst dort
    weder eine Marke noch einen Alt-Text: Ein PDF mit Bildern liefert Zeichen fuer
    Zeichen dasselbe Markdown wie dasselbe PDF ohne. Zaehlen laesst sich am Ergebnis
    deshalb nichts.

    Die Warnung nennt darum das Verhalten der Engine und nicht den Inhalt der
    Vorlage. Der Preis dafuer, die Datei kein zweites Mal zu lesen: Ein PDF ganz ohne
    Bilder bekommt sie auch. Das ist so entschieden.

    Nur fuer PDF. In ``.docx``, ``.html`` und ``.epub`` setzt MarkItDown den Alt-Text
    ein — dort waere die Aussage unwahr.
    """
    if path.suffix.lower() != ".pdf":
        return []
    return [
        "MarkItDown uebernimmt keine Bilder aus PDF. "
        f"Enthielt {path.name} Bilder, fehlt ihr Inhalt hier."
    ]


class MarkItDownConverter:
    """Der Adapter. Die Bibliothek wird verzoegert geladen und einmal aufgebaut."""

    name = "markitdown"
    extensions = EXTENSIONS

    def __init__(self) -> None:
        self._engine: Any | None = None

    def available(self) -> bool:
        """Ob die Bibliothek da ist. Wirft nie."""
        try:
            self._get_engine()
        except EngineUnavailable:
            return False
        return True

    def convert(self, path: Path, opts: ConvertOptions) -> ConversionResult:
        """Wandelt die Datei. ``opts`` bleibt ungenutzt: MarkItDown kennt kein OCR."""
        engine = self._get_engine()
        try:
            markdown = engine.convert(path).markdown
        except Exception as exc:  # jede Ausnahme der Bibliothek
            raise EngineFailed(f"MarkItDown ist an {path.name} gescheitert: {exc}") from exc

        warnings: list[str] = []
        if not markdown.strip():
            warnings.append(f"MarkItDown hat in {path.name} keinen Text gefunden.")
        warnings.extend(_pdf_image_warnings(path))
        return ConversionResult(markdown=markdown, engine=self.name, warnings=warnings)

    def _get_engine(self) -> Any:
        if self._engine is None:
            try:
                from markitdown import MarkItDown
            except ImportError as exc:
                raise EngineUnavailable(f"MarkItDown ist nicht installiert: {exc}") from exc
            self._engine = MarkItDown(enable_plugins=False)
        return self._engine


_CONVERTER = MarkItDownConverter()


def get_converter() -> MarkItDownConverter:
    """Was die Registry aufruft."""
    return _CONVERTER
