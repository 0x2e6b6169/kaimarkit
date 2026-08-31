"""Macht ``app`` importierbar, ohne das Paket zu installieren.

``pytest`` legt nur ``tests/`` auf den Suchpfad; die Anwendung liegt eine Ebene
darueber.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
