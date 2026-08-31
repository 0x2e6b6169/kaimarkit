#!/usr/bin/env bash
# PreToolUse guard (Edit|Write|MultiEdit): Ticket-CODE gehoert in einen git
# worktree (.worktrees/task-NN), niemals in den gemeinsamen Board-Home-Checkout.
#
# Board-Home ist reserviert fuer Board-Operationen (kanban-md), Merges und die
# Board-/Prozess-Commits von PO/SM. Dieser Hook blockiert Code-Aenderungen an der
# Wurzel und laesst genau die Dateien durch, die dort legitim liegen.
#
# Die Entscheidung haengt am ABSOLUTEN Zielpfad gegen $CLAUDE_PROJECT_DIR (das
# Board-Home, von Claude Code gesetzt) und ist damit unabhaengig vom cwd.
# Grenze: Wurde eine Sitzung *innerhalb* eines Worktrees gestartet, ist
# CLAUDE_PROJECT_DIR dieser Worktree und Board-Home-Aenderungen fallen nicht auf.
# Sitzungen starten im Board-Home, in der Praxis genuegt das.
#
# Exit 0 = erlauben; Exit 2 = blockieren (stderr geht an das Modell).

python3 -c '
import json, os, sys

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)  # bei einem Parse-Fehler niemals blockieren

ti = data.get("tool_input") or {}
fp = ti.get("file_path") or ti.get("path") or ""
cwd = data.get("cwd") or ""
proj = os.environ.get("CLAUDE_PROJECT_DIR", "")
if not fp or not proj:
    sys.exit(0)

proj = os.path.normpath(proj)
ap = fp if os.path.isabs(fp) else os.path.normpath(os.path.join(cwd, fp))

# Ausserhalb des Projekts (andere Repos, /tmp, ...) -> nicht unsere Sache.
if ap != proj and not ap.startswith(proj + os.sep):
    sys.exit(0)

rel = os.path.relpath(ap, proj)
parts = rel.split(os.sep)

# Innerhalb eines Worktrees -> normale Ticketarbeit.
if parts[0] == ".worktrees":
    sys.exit(0)

# Board-Home-Allowlist (Board- und Prozessdateien, die PO/SM hier committet).
if parts[0] in ("kanban", ".claude") or rel in ("CLAUDE.md", "CHANGELOG.md", ".gitattributes"):
    sys.exit(0)

sys.stderr.write(
    "Guard: Ticketcode gehoert in einen Worktree (.worktrees/task-NN), nicht ins "
    "gemeinsame Board-Home (" + rel + "). Board-Home = Board-Operationen + Merges "
    "+ PO/SM-Prozess-Commits — siehe CLAUDE.md \"Arbeitsweise mit mehreren Agenten\".\n"
)
sys.exit(2)
'
