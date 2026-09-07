"""MarkItDown hinter dem Converter-Protokoll.

MarkItDown ist die schnelle Engine: keine Modelle, kein OCR, dafür breite
Formatabdeckung. Einen LLM-Client setzt der Adapter bewusst nicht ein: Kein Bild
wird beschrieben. In ``.docx``, ``.html`` und ``.epub`` bleibt davon der Alt-Text
stehen; das Bild selbst setzt MarkItDown als Data-URI daneben. ``convert()``
entfernt sie und meldet, dass der Inhalt fehlt. Aus einem PDF übernimmt MarkItDown
dagegen gar nichts — dort fällt jedes Bild ersatzlos weg, und auch das steht in
einer Warnung.

Achtung beim Lesen: Diese Datei heißt wie die Bibliothek. ``from markitdown import
MarkItDown`` meint trotzdem die Bibliothek, denn Python 3 importiert absolut; das
Nachbarmodul erreicht man nur über ``from . import markitdown``.
"""

from __future__ import annotations

import re
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


#: Ein Bild im Markdown, dessen Ziel eine Data-URI ist — so schreibt MarkItDown jedes
#: eingebettete Bild. Ein Titel hinter der Adresse steht mit in der Klammer und fällt
#: deshalb mit ihr weg; ein Bild trägt selten einen.
_DATA_URI_IMAGE = re.compile(r"!\[(?P<alt>[^\]]*)\]\(data:[^)]*\)")


def _drop_data_uris(markdown: str) -> tuple[str, int]:
    """Nimmt jedem eingebetteten Bild sein Ziel und zählt, wie oft.

    MarkItDown setzt ein Bild aus ``.docx``, ``.html`` oder ``.epub`` als Data-URI
    ins Markdown — in der Voreinstellung gekürzt auf ``data:image/png;base64...``,
    mit ``keep_data_uris`` in voller Länge. Lesen lässt sich keine von beiden
    Fassungen: Die gekürzte ist ein Rest ohne Inhalt, die volle eine Zeichenkette,
    die ein Kontextfenster füllt, ohne etwas beizutragen. Dieser Dienst soll den
    Kontext zeigen, den man einem Modell gibt; dazu taugt weder die eine noch die
    andere.

    Zurück bleibt ``![Alt-Text]()``. Der Alt-Text ist das Einzige, was MarkItDown aus
    einem Bild übernimmt, und er bleibt deshalb stehen; die leere Klammer zeigt, dass
    an dieser Stelle etwas fehlt. Doclings ``<!-- image -->`` steht hier absichtlich
    nicht: Das ist Doclings Exportformat. Beide Engines dasselbe schreiben zu lassen
    behauptete eine Gleichheit, die es nicht gibt — Docling kennt keinen Alt-Text.

    Ein Bild, das auf eine Adresse zeigt, bleibt unangetastet. Sein Inhalt liegt
    weiterhin dort, wohin die Adresse führt.
    """
    return _DATA_URI_IMAGE.subn(lambda match: f"![{match.group('alt')}]()", markdown)


def _embedded_image_warnings(count: int, name: str) -> list[str]:
    """Meldet die Bilder, deren Inhalt beim Wandeln verlorengeht.

    Die Warnung nennt vier Dinge: was in der Vorlage steckt, was im Markdown fehlt,
    warum MarkItDown es dort nicht liest, und was dagegen hilft (BE-40, GitHub #2).
    Die Zahl steht darin: Ein Bild ist etwas anderes als vierzehn.

    Der Umweg ist in diesem Stand begehbar. Docling liest Text aus Bildern nur in
    einer PDF-Datei oder in einer Bilddatei (BE-38, im Abbild gemessen); für ``.pdf``
    ist es die erste Wahl der Registry, die Enginewahl steht im Frontend als
    Schaltergruppe, und die Texterkennung ist voreingestellt an.
    """
    if count == 0:
        return []
    if count == 1:
        steckt = "steckt ein Bild"
        fehlt = "Sein Inhalt fehlt im Markdown."
    else:
        steckt = f"stecken {count} Bilder"
        fehlt = "Ihr Inhalt fehlt im Markdown."
    return [
        f"In {name} {steckt}. {fehlt}"
        " MarkItDown liest keinen Text aus Bildern. Wer ihn braucht, speichert das"
        " Dokument als PDF und lädt es mit der Engine docling und eingeschalteter"
        " Texterkennung erneut hoch."
    ]


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
        "MarkItDown übernimmt keine Bilder aus PDF. "
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

        markdown, embedded = _drop_data_uris(markdown)

        warnings: list[str] = []
        if not markdown.strip():
            warnings.append(f"MarkItDown hat in {path.name} keinen Text gefunden.")
        warnings.extend(_embedded_image_warnings(embedded, path.name))
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
