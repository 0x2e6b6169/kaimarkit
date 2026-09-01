"""Faehigkeitsmatrix, Auswahl und Fallback.

Die Praeferenzliste je Endung steht hier im Code und nicht in der Konfiguration: Sie
beschreibt, was die Bibliotheken koennen, und das aendert sich mit den Abhaengigkeiten,
nicht mit dem Deployment. Pandoc fehlt bei ``.pdf``, weil Pandoc PDF nicht liest.

Diese Datei nennt alle drei Enginenamen und laedt die Module verzoegert — erst beim
ersten Zugriff. Die Enginemodule tragen sich nirgends ein; sie liefern nur
``get_converter()``. Fehlt ein Modul oder eine Bibliothek, endet das in
``EngineUnavailable``, nie in einem ``ImportError``.
"""

from __future__ import annotations

import importlib
import time
from pathlib import Path

from ..config import get_settings
from ..errors import (
    ConversionError,
    EngineFailed,
    EngineUnavailable,
    EngineUnsuitable,
    UnsupportedFormat,
)
from .base import ConversionResult, Converter, ConvertOptions

#: Die drei Engines. BE-3 bis BE-5 liefern je ein Modul dieses Namens neben dieser Datei.
ENGINE_NAMES: tuple[str, ...] = ("markitdown", "docling", "pandoc")

#: Markdown wird durchgereicht statt gewandelt.
PASSTHROUGH = "passthrough"

#: Endung auf Praeferenz, erste Wahl zuerst.
PREFERENCES: dict[str, tuple[str, ...]] = {
    ".pdf": ("docling", "markitdown"),
    ".docx": ("markitdown", "docling", "pandoc"),
    ".epub": ("pandoc", "markitdown"),
    ".pptx": ("markitdown", "docling"),
    ".xlsx": ("markitdown", "docling"),
    ".html": ("markitdown", "pandoc", "docling"),
    ".htm": ("markitdown", "pandoc", "docling"),
    ".odt": ("pandoc",),
    ".rtf": ("pandoc",),
    ".tex": ("pandoc",),
    ".rst": ("pandoc",),
    ".org": ("pandoc",),
    ".csv": ("markitdown",),
    ".json": ("markitdown",),
    ".xml": ("markitdown",),
    ".txt": ("markitdown",),
    ".png": ("docling", "markitdown"),
    ".jpg": ("docling", "markitdown"),
    ".jpeg": ("docling", "markitdown"),
    ".tiff": ("docling", "markitdown"),
    ".md": (PASSTHROUGH,),
    ".markdown": (PASSTHROUGH,),
}


class _Passthrough:
    """Markdown bleibt Markdown — nur lesen, nichts wandeln."""

    name = PASSTHROUGH
    extensions = (".md", ".markdown")

    def available(self) -> bool:
        return True

    def convert(self, path: Path, opts: ConvertOptions) -> ConversionResult:
        try:
            markdown = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise EngineFailed(f"Datei nicht lesbar: {exc}") from exc
        return ConversionResult(markdown=markdown, engine=self.name)


# Einmal geladene Engines bleiben hier stehen. Tests setzen Attrappen direkt ein.
_INSTANCES: dict[str, Converter] = {PASSTHROUGH: _Passthrough()}


def get_converter(name: str) -> Converter:
    """Die Engine zu einem Namen, beim ersten Zugriff geladen."""
    converter = _INSTANCES.get(name)
    if converter is not None:
        return converter
    if name not in ENGINE_NAMES:
        raise EngineUnavailable(f"Unbekannte Engine: {name}.")
    try:
        module = importlib.import_module(f"{__package__}.{name}")
        converter = module.get_converter()
    except Exception as exc:  # ImportError der Bibliothek, Fehler beim Aufbau
        raise EngineUnavailable(f"Engine {name} ist nicht verfügbar: {exc}") from exc
    _INSTANCES[name] = converter
    return converter


def preferences_for(ext: str) -> tuple[str, ...]:
    """Die Praeferenz laut Matrix, mit ``KAIMARKIT_DEFAULT_ENGINE`` vorangestellt.

    Kann die eingestellte Standardengine diese Endung nicht, bleibt die Reihenfolge,
    wie sie ist — eine ungeeignete Engine nach vorn zu ziehen hilft niemandem.
    """
    prefs = PREFERENCES.get(ext.lower(), ())
    default = get_settings().default_engine
    if default != "auto" and default in prefs:
        prefs = (default, *(name for name in prefs if name != default))
    return prefs


def engines_for(ext: str) -> list[str]:
    """Was fuer diese Endung jetzt wirklich geht, in Praeferenzreihenfolge.

    Grundlage von ``/api/capabilities``: Eine Engine, die nicht laedt oder noch nicht
    bereit ist, erscheint hier nicht.
    """
    return [name for name in preferences_for(ext) if _is_ready(name)]


def select(ext: str, requested: str | None = None) -> Converter:
    """Die Engine fuer diese Endung.

    ``requested`` ist ``None`` oder ``"auto"`` fuer die Praeferenzliste. Eine
    ausdruecklich genannte Engine wird nie durch eine andere ersetzt: Kann sie das
    Format nicht, gibt es ``EngineUnsuitable`` statt still ein anderes Ergebnis.
    """
    prefs = preferences_for(ext)
    if not prefs:
        raise UnsupportedFormat(f"Für {ext or 'Dateien ohne Endung'} gibt es keine Engine.")
    if requested and requested != "auto":
        if requested not in prefs:
            raise EngineUnsuitable(f"Engine {requested} kann {ext} nicht wandeln.")
        return get_converter(requested)
    for name in prefs:
        if _is_ready(name):
            return get_converter(name)
    raise EngineUnavailable(f"Für {ext} ist zurzeit keine Engine verfügbar.")


def convert_with_fallback(path: Path, opts: ConvertOptions | None = None) -> ConversionResult:
    """Wandelt die Datei und faellt bei einem Fehlschlag auf die naechste Engine zurueck.

    Der Grund des Fehlschlags steht danach in ``warnings``. Wer eine Engine
    ausdruecklich nennt, bekommt keinen Rueckfall; ``KAIMARKIT_ENABLE_FALLBACK``
    schaltet ihn auch fuer ``auto`` ab.
    """
    opts = opts or ConvertOptions()
    ext = path.suffix.lower()
    started = time.perf_counter()

    requested = opts.engine if opts.engine and opts.engine != "auto" else None
    if requested is not None:
        return _finish(select(ext, requested).convert(path, opts), started)

    candidates = engines_for(ext)
    if not candidates:
        select(ext)  # wirft UnsupportedFormat oder EngineUnavailable mit Klartext
    fallback = get_settings().enable_fallback
    warnings: list[str] = []
    last: ConversionError | None = None
    for name in candidates:
        try:
            result = get_converter(name).convert(path, opts)
        except ConversionError as exc:
            if not fallback:
                raise
            last = exc
            warnings.append(f"Engine {name} ist gescheitert: {exc.detail}")
            continue
        result.warnings = [*warnings, *result.warnings]
        return _finish(result, started)
    raise last if last is not None else EngineUnavailable(f"Für {ext} ist keine Engine da.")


def _is_ready(name: str) -> bool:
    try:
        return get_converter(name).available()
    except EngineUnavailable:
        return False


def _finish(result: ConversionResult, started: float) -> ConversionResult:
    result.duration_ms = int((time.perf_counter() - started) * 1000)
    return result
