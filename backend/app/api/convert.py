"""Die Konvertierungsendpunkte.

Stumpf: ``/api/convert`` und ``/api/capabilities`` kommen aus BE-7,
``/api/convert/batch`` aus BE-8. Der Router existiert schon, damit ``main.py`` ihn
einhaengen kann, ohne spaeter noch einmal angefasst zu werden.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["convert"])
