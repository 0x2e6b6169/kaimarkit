"""Einstellungen aus der Umgebung.

Alle Werte kommen aus ``KAIMARKIT_*``-Variablen; jeder hat einen Standardwert, damit
der Dienst ohne gesetzte Umgebung startet. Diese Datei und ``docker/.env.example``
beschreiben dieselben Variablen und werden gemeinsam geaendert.

Hier stehen nur die Variablen, die der Prozess selbst liest. Build, Abbild, Traefik
und Authelia werden von Compose ausgewertet und erreichen die Anwendung nie —
``extra="ignore"`` laesst sie deshalb wirkungslos durch.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from . import __version__


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="KAIMARKIT_", extra="ignore")

    # Grenzen
    max_file_size_mb: int = 50
    max_files: int = 20
    max_concurrent: int = 2
    # 600 s ist gemessen, nicht geschaetzt: Das langsamste bekannte Dokument
    # brauchte 326 s, die Streuung auf gleicher Eingabe betraegt Faktor 1,8; 326
    # mal 1,8 sind 587, aufgerundet 600. Zeit kostet nicht die Seitenzahl, sondern
    # die fehlende Textschicht — gescannt mit OCR rund zwei Minuten je Seite, mit
    # Textschicht drei Sekunden. ``docker/.env.example`` nennt denselben Wert,
    # damit ein nackt gestartetes Backend sich verhaelt wie die Auslieferung.
    conversion_timeout: int = 600
    pandoc_timeout: int = 60
    # Zeitgrenze je Abruf fuer ``/api/convert/url``, Weiterleitungen eingeschlossen.
    # Die Umwandlung danach unterliegt ``conversion_timeout`` wie ein Upload.
    url_timeout: int = 30

    # Engines
    default_engine: str = "auto"
    enable_fallback: bool = True
    ocr_enabled: bool = True
    # ISO 639-1: der Docling-Adapter ruft EasyOCR auf, und die erwartet diese
    # Kuerzel. Tesseracts ``deu,eng`` erkennt sie nicht.
    ocr_langs: str = "de,en"

    # Betrieb
    log_level: str = "info"
    workers: int = 1
    # Der Stand, der wirklich laeuft. Der Bau setzt hier ein, was
    # ``git describe --tags --always --dirty`` auf der bauenden Maschine liefert:
    # ``v0.1.0`` auf dem Tag, ``v0.1.0-12-ga22a6c5`` dahinter, mit ``-dirty`` bei
    # Aenderungen im Arbeitsbaum. Der Container hat kein ``.git`` und fragt Git
    # deshalb nie selbst.
    version: str = ""

    # Pfade der ausgelieferten statischen Teile. Fehlt ein Verzeichnis, haengt
    # ``main.py`` es nicht ein — so laeuft das Backend auch ohne gebautes Frontend
    # und ohne Dokumentation.
    static_dir: Path = Path("/opt/kaimarkit/static")
    docs_dir: Path = Path("/opt/kaimarkit/docs")

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    @property
    def service_version(self) -> str:
        """Die Version, die ``/api/health`` meldet.

        Ohne ``KAIMARKIT_VERSION`` gilt ``__version__`` aus ``app/__init__.py``.
        Das ist der Fall in der Entwicklung, und es ist der Fall bei einem Bau ohne
        Git-Verlauf — dann bleibt die Variable leer, und der Dienst startet trotzdem.
        """
        return self.version.strip() or __version__


@lru_cache
def get_settings() -> Settings:
    return Settings()
