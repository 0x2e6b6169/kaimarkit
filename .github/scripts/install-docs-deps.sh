#!/usr/bin/env bash
# Holt mkdocs-material und mike aus der Gruppe "docs" in backend/pyproject.toml.
#
# Nicht "pip install backend[docs]": Ein Extra bringt immer die Laufzeit mit,
# und die heisst hier docling samt Torch. Der Laeufer baut Seiten, keine
# Modelle. Die Fassungen stehen trotzdem nur an einer Stelle.
set -euo pipefail

python - <<'PY' >"$RUNNER_TEMP/requirements-docs.txt"
import pathlib
import tomllib

data = tomllib.loads(pathlib.Path("backend/pyproject.toml").read_text(encoding="utf-8"))
print("\n".join(data["project"]["optional-dependencies"]["docs"]))
PY

cat "$RUNNER_TEMP/requirements-docs.txt"
pip install -r "$RUNNER_TEMP/requirements-docs.txt"
