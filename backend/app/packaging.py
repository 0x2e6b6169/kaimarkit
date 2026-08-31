"""Die Ergebnisse eines Stapels zu einem ZIP buendeln.

Das Archiv entsteht vollstaendig im Speicher. Der Dienst legt nichts auf Platte ab,
auch nicht das fertige Paket.

Zwei Entscheidungen fallen hier. Der Name im Archiv hat keinen Pfadanteil: Ein Client
bestimmt ihn, und ein entpacktes ``../../etc/passwd`` waere ein Einbruch. Und zwei
Dateien gleichen Namens ueberschreiben einander nicht — die zweite heisst
``bericht-2.md``, die dritte ``bericht-3.md``.
"""

from __future__ import annotations

import io
import zipfile
from collections.abc import Iterable
from pathlib import PurePosixPath

from .models import ConversionEntry, ConversionStatus
from .uploads import sanitize_filename

#: Liegt im Archiv, sobald eine Datei des Stapels gescheitert ist.
ERROR_FILENAME = "_errors.txt"

#: Steht in ``_errors.txt``, wenn ein Eintrag keinen Grund nennt.
UNKNOWN_ERROR = "Unbekannter Fehler"


def build_archive(entries: Iterable[ConversionEntry]) -> io.BytesIO:
    """Packt die gelungenen Ergebnisse und schreibt die gescheiterten in eine Liste.

    Zurueck kommt ein Puffer am Anfang, den der Endpunkt an den Client streamt.
    """
    buffer = io.BytesIO()
    taken: set[str] = set()
    errors: list[str] = []
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for entry in entries:
            if entry.status == ConversionStatus.OK and entry.markdown is not None:
                archive.writestr(_unique(_markdown_name(entry.filename), taken), entry.markdown)
            else:
                reason = entry.error or UNKNOWN_ERROR
                errors.append(f"{sanitize_filename(entry.filename)}: {reason}")
        if errors:
            archive.writestr(ERROR_FILENAME, "\n".join(errors) + "\n")
    buffer.seek(0)
    return buffer


def _markdown_name(filename: str) -> str:
    """Der blanke Name mit der Endung ``.md``, ohne Verzeichnis davor."""
    stem = PurePosixPath(sanitize_filename(filename)).stem
    return f"{stem}.md"


def _unique(name: str, taken: set[str]) -> str:
    """Haengt ``-2``, ``-3`` an, bis der Name im Archiv noch frei ist."""
    candidate = name
    if candidate in taken:
        path = PurePosixPath(name)
        counter = 2
        while f"{path.stem}-{counter}{path.suffix}" in taken:
            counter += 1
        candidate = f"{path.stem}-{counter}{path.suffix}"
    taken.add(candidate)
    return candidate
