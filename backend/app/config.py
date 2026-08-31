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


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="KAIMARKIT_", extra="ignore")

    # Grenzen
    max_file_size_mb: int = 50
    max_files: int = 20
    max_concurrent: int = 2
    conversion_timeout: int = 120
    pandoc_timeout: int = 60

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

    # Pfade der ausgelieferten statischen Teile. Fehlt ein Verzeichnis, haengt
    # ``main.py`` es nicht ein — so laeuft das Backend auch ohne gebautes Frontend
    # und ohne Dokumentation.
    static_dir: Path = Path("/opt/kaimarkit/static")
    docs_dir: Path = Path("/opt/kaimarkit/docs")

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
