"""Macht das Paket ``app`` fuer die Tests auffindbar.

Ohne diesen Eintrag sucht pytest ``app`` im uebrigen ``sys.path`` und findet dort
im Zweifel ein gleichnamiges Paket aus einem anderen Projekt.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
