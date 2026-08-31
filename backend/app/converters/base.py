"""Die Abstraktion, hinter der die Engines verschwinden.

Ausserhalb dieses Pakets kennt niemand ``markitdown``, ``docling`` oder ``pandoc``.
Was eine Engine leisten muss, steht vollstaendig im Protokoll ``Converter``.

Jedes Enginemodul (``markitdown.py``, ``docling.py``, ``pandoc.py``) stellt genau eine
Funktion ``get_converter() -> Converter`` bereit. Die Registry ruft sie beim ersten
Zugriff auf und merkt sich das Ergebnis; ein Enginemodul traegt sich nirgends ein.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol


@dataclass(slots=True)
class ConversionResult:
    """Was eine Engine zurueckgibt.

    ``duration_ms`` setzt die Registry: Sie misst die Gesamtdauer einschliesslich
    gescheiterter Versuche, und genau die meldet die API. Eine Engine darf das Feld
    auf 0 lassen.
    """

    markdown: str
    engine: str
    warnings: list[str] = field(default_factory=list)
    duration_ms: int = 0


@dataclass(slots=True)
class ConvertOptions:
    """Was der Aufrufer zur Konvertierung mitgibt.

    ``engine`` ist ``None`` oder ``"auto"`` fuer die Praeferenzliste, sonst ein
    Enginename — dann wird diese Engine nie durch eine andere ersetzt. ``ocr`` ist
    ``None``, solange ``KAIMARKIT_OCR_ENABLED`` gilt.
    """

    engine: str | None = None
    ocr: bool | None = None


class Converter(Protocol):
    """Was eine Engine koennen muss.

    ``available()`` beantwortet die Frage, ob die Engine jetzt arbeiten kann — bei
    Docling also erst, wenn die Modelle geladen sind. ``convert()`` wandelt jede
    eigene Ausnahme in einen ``ConversionError`` um.
    """

    name: str
    extensions: tuple[str, ...]

    def available(self) -> bool: ...

    def convert(self, path: Path, opts: ConvertOptions) -> ConversionResult: ...
