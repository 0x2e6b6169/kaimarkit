"""Docling hinter dem Converter-Protokoll.

Docling ist die einzige Engine, die vor dem ersten Aufruf laedt: Sie holt Layout-
und Tabellenmodelle in den Speicher und braucht dafuer rund achteinhalb Sekunden.
Deshalb baut dieses Modul seine Konverter genau einmal und im Hintergrund. Solange
noch keiner steht, meldet der Adapter ``warming``; ``available()`` ist dann False,
die Registry nimmt fuer ``engine=auto`` die naechste Engine, und wer Docling
ausdruecklich verlangt, wartet im ``convert()`` auf den fertigen Konverter.

OCR an und OCR aus sind in Docling zwei Pipelines mit verschiedenem Options-Hash.
Der Warmlauf baut beide, die eingestellte Voreinstellung zuerst. Laedt er nur eine,
zahlt die erste Umwandlung mit der anderen Einstellung die Ladezeit ein zweites Mal
— und ``/api/capabilities`` meldet waehrenddessen ``ready``. Dieses Fenster bleibt
zwischen der ersten und der zweiten Pipeline bestehen: Wer dort die andere
Einstellung verlangt, wartet an der Sperre in ``_pipeline`` und bekommt ein
richtiges Ergebnis, nur spaeter.

Die Bibliothek selbst wird erst in ``_build_pipeline`` importiert. Ist sie nicht
installiert, laesst sich dieses Modul trotzdem laden — der Zugriff endet dann in
``EngineUnavailable`` statt in einem ``ImportError``.
"""

from __future__ import annotations

import logging
import os
import threading
from collections.abc import Callable
from pathlib import Path

from ..config import get_settings
from ..errors import EngineFailed, EngineUnavailable
from .base import ConversionResult, ConvertOptions

log = logging.getLogger(__name__)

NAME = "docling"

#: Was Docling in diesem Dienst bedient. Die Praeferenz je Endung steht in der Registry.
EXTENSIONS: tuple[str, ...] = (
    ".pdf",
    ".docx",
    ".pptx",
    ".xlsx",
    ".html",
    ".htm",
    ".png",
    ".jpg",
    ".jpeg",
    ".tiff",
)

#: Wo die vorgebackenen Modelle liegen. Die Variable gehoert Docling, nicht kaimarkit —
#: das Dockerfile setzt sie, damit zur Laufzeit nichts nachgeladen wird.
ARTIFACTS_ENV = "DOCLING_ARTIFACTS_PATH"

#: Was ``ImageRefMode.PLACEHOLDER`` anstelle eines Bildes ins Markdown setzt.
PLACEHOLDER = "<!-- image -->"


def _placeholder_warnings(markdown: str, name: str) -> list[str]:
    """Warnt, wenn im Markdown Platzhalter statt Inhalt stehen.

    Doclings Modell ordnet manches als Bild ein, was Text ist — eine breite Tabelle
    etwa. Der Export setzt dafuer ``<!-- image -->`` ein, und wer das Ergebnis liest,
    sieht sonst nicht, dass ein Stueck der Vorlage fehlt. Die Zahl steht in der
    Warnung: Ein ersetztes Bild ist etwas anderes als vierzehn.
    """
    count = markdown.count(PLACEHOLDER)
    if count == 0:
        return []
    if count == 1:
        ersetzt = "ein Bild durch einen Platzhalter"
        fehlt = "Sein Inhalt fehlt im Markdown."
    else:
        ersetzt = f"{count} Bilder durch Platzhalter"
        fehlt = "Ihr Inhalt fehlt im Markdown."
    return [f"Docling hat in {name} {ersetzt} ersetzt. {fehlt}"]


def _build_pipeline(ocr: bool) -> Callable[[Path], str]:
    """Baut den ``DocumentConverter`` und gibt das Wandeln als Funktion zurueck.

    Alles, was Docling kennt, steht in dieser einen Funktion. Der Aufruf laedt die
    Modelle und dauert deshalb rund achteinhalb Sekunden; das Ergebnis wird
    wiederverwendet. Die Tests ersetzen diese Funktion.
    """
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import EasyOcrOptions, PdfPipelineOptions
    from docling.document_converter import (
        DocumentConverter,
        ImageFormatOption,
        PdfFormatOption,
    )
    from docling_core.types.doc import ImageRefMode

    settings = get_settings()

    options = PdfPipelineOptions()
    options.do_ocr = ocr
    options.do_table_structure = True
    options.generate_picture_images = False

    artifacts = os.environ.get(ARTIFACTS_ENV)
    if artifacts:
        options.artifacts_path = artifacts

    # Die OCR-Maschine steht hier ausdruecklich. Ueberlaesst man sie der Bibliothek,
    # waehlt ``OcrAutoOptions`` selbst eine aus und startet sie mit deren
    # Voreinstellungen — ein vorher gesetztes ``lang`` faellt dabei weg und
    # ``KAIMARKIT_OCR_LANGS`` bliebe wirkungslos. EasyOCR erwartet ISO 639-1.
    langs = [lang.strip() for lang in settings.ocr_langs.split(",") if lang.strip()]
    options.ocr_options = EasyOcrOptions(lang=langs) if langs else EasyOcrOptions()

    # Bilder brauchen denselben Eintrag wie PDF. Ohne ihn legt Docling fuer
    # ``InputFormat.IMAGE`` seine eigene Vorgabe an: Die Texterkennung liefe dort
    # immer, ``KAIMARKIT_OCR_LANGS`` bliebe wirkungslos, und statt EasyOCR startete
    # die von der Bibliothek gewaehlte Maschine. Beide Eintraege teilen sich
    # ``options`` — dieselbe Pipeline, nur ein anderer Zugang zur Datei.
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=options),
            InputFormat.IMAGE: ImageFormatOption(pipeline_options=options),
        }
    )

    def run(path: Path) -> str:
        document = converter.convert(path).document
        # Bilder werden zu ``PLACEHOLDER``. Was dabei verloren geht, zaehlt der
        # Adapter danach und meldet es in ``warnings``.
        return document.export_to_markdown(image_mode=ImageRefMode.PLACEHOLDER)

    return run


class DoclingConverter:
    """Der Adapter. Haelt je OCR-Einstellung einen fertigen Konverter."""

    name = NAME
    extensions = EXTENSIONS

    def __init__(self) -> None:
        self._pipelines: dict[bool, Callable[[Path], str]] = {}
        # Serialisiert den Aufbau: Eine Anfrage waehrend des Vorladens wartet hier,
        # statt einen zweiten Konverter danebenzustellen.
        self._build_lock = threading.Lock()
        self._start_lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._failure: str | None = None

    def start_warmup(self) -> None:
        """Laedt beide Konverter im Hintergrund. Mehrfach aufzurufen schadet nicht.

        Der Aufruf kehrt sofort zurueck — der Start des Dienstes und ``/api/health``
        warten nie auf die Modelle.
        """
        with self._start_lock:
            if self._thread is not None:
                return
            self._thread = threading.Thread(
                target=self._warmup, name="docling-warmup", daemon=True
            )
            self._thread.start()

    def _warmup(self) -> None:
        """Baut beide Pipelines, die eingestellte Voreinstellung zuerst.

        Scheitert die erste, fehlt meist die Bibliothek. Dann ist auch die zweite
        nicht zu bauen, und der Warmlauf endet hier.
        """
        default_ocr = get_settings().ocr_enabled
        for ocr in (default_ocr, not default_ocr):
            try:
                self._pipeline(ocr)
            except Exception as exc:  # noqa: BLE001 — der Thread darf nichts nach aussen werfen
                self._failure = str(exc)
                log.warning("Docling ist nicht verfuegbar: %s", exc)
                return
            log.info("Docling ist bereit (OCR: %s).", ocr)

    def state(self) -> str:
        """``ready``, ``warming`` oder ``unavailable`` — die Werte aus ``contracts/api.md``."""
        if self._pipelines:
            return "ready"
        if self._failure is not None:
            return "unavailable"
        return "warming"

    def available(self) -> bool:
        return bool(self._pipelines)

    def convert(self, path: Path, opts: ConvertOptions) -> ConversionResult:
        ocr = get_settings().ocr_enabled if opts.ocr is None else opts.ocr
        try:
            run = self._pipeline(ocr)
        except Exception as exc:  # noqa: BLE001 — jede Ausnahme der Bibliothek
            raise EngineUnavailable(f"Docling ist nicht verfügbar: {exc}") from exc
        try:
            markdown = run(path)
        except Exception as exc:  # noqa: BLE001 — jede Ausnahme der Bibliothek
            raise EngineFailed(f"Docling ist an {path.name} gescheitert: {exc}") from exc
        return ConversionResult(
            markdown=markdown,
            engine=self.name,
            warnings=_placeholder_warnings(markdown, path.name),
        )

    def _pipeline(self, ocr: bool) -> Callable[[Path], str]:
        """Der Konverter zu dieser OCR-Einstellung, beim ersten Mal gebaut.

        Wer hier ankommt, waehrend das Vorladen laeuft, wartet an der Sperre und
        bekommt danach denselben Konverter.
        """
        with self._build_lock:
            run = self._pipelines.get(ocr)
            if run is None:
                run = _build_pipeline(ocr)
                self._pipelines[ocr] = run
                self._failure = None
            return run


_INSTANCE: DoclingConverter | None = None
_INSTANCE_LOCK = threading.Lock()


def get_converter() -> DoclingConverter:
    """Der Adapter, einmal je Prozess. Die Registry ruft nur das auf.

    Der erste Aufruf stoesst das Vorladen an. So laedt Docling auch dann im
    Hintergrund, wenn niemand ``start_warmup()`` im Lifespan gerufen hat.
    """
    global _INSTANCE
    with _INSTANCE_LOCK:
        if _INSTANCE is None:
            _INSTANCE = DoclingConverter()
    _INSTANCE.start_warmup()
    return _INSTANCE


def start_warmup() -> None:
    """Einhaenger fuer den FastAPI-Lifespan: laedt Docling vor, ohne zu blockieren."""
    get_converter()
