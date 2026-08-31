---
name: findings
description: Triage a list of testing observations into kanban tickets on the kaimarkit board. The user passes findings (bugs, rough edges, ideas) as the skill args — one per line / bullet — and this skill turns each into a well-formed ticket, assigns it to a lane (benny=frontend, sophie=backend, akar=infrastructure/docs/other), sets a priority, and decides per the project policy whether it is urgent work (→ `todo`) or a speculative idea (→ `backlog`). PO/SM (katche) tool. Language follows the user.
---

# findings

Turn a batch of testing observations into triaged kanban tickets. This is a
**PO/SM (katche) workflow** — it grooms the board, it does not implement.

`kanban-md` lives at `~/go/bin/kanban-md` and is **not on the PATH**.

## Input

The findings come in as the skill **args** — typically one observation per line
or bullet (free text; a finding may be a bug, a rough edge, or an idea). If no
args were given, ask the user to paste the list and stop. Treat each distinct
observation as one candidate ticket; **split** a line that clearly bundles
several issues, and only ask the user to clarify a finding that is truly
unparseable (otherwise make a best-effort ticket and flag it as low-confidence
in the report).

## Per-finding procedure

For each observation:

1. **Dedup first.** Search the board for an existing ticket that already covers
   it (`~/go/bin/kanban-md list --compact --status backlog,todo,in-progress,review`
   and grep the titles, or `show <id>` on near-matches). If one exists, **do not
   create a duplicate** — note the match in the report (and, if useful, append the
   new detail to that ticket's body) instead.

2. **Classify the type:** bug / regression, UX rough edge, improvement, or
   idea/feature.

3. **Assign a lane** (`--assignee`), by primary domain:
   - **benny** — frontend (Vue components, Dropzone/Warteschlange, Vorschau,
     Optionen, Download, Gestaltung und Barrierefreiheit).
   - **sophie** — backend (FastAPI, Converter-Engines, Registry, Uploads und
     Grenzen, ZIP-Bau, Tests).
   - **akar** — infrastructure, documentation, organizational + everything else
     (Dockerfile, Compose-Schichten, Makefile, MkDocs, Planung).
   - Cross-cutting/full-stack → the primary domain; note the split in the body.
   - **Watch for the interface triad:** a finding that changes the API shape
     touches `contracts/api.md`, `backend/app/models.py` and
     `frontend/src/types.ts` together (CLAUDE.md convention 1). Put it in one
     lane and say so in the body — never split it into two tickets that would
     each own the same files.

4. **Set a priority** (`--priority low|medium|high|critical`) by severity/impact.

5. **Decide `todo` vs `backlog`** — the key judgement (the user delegates it):
   - **→ `todo` (urgent, gets worked):** confirmed bugs/regressions; broken,
     misleading, or data-losing behaviour; anything that silently produces wrong
     Markdown (the whole point of the tool is that you can trust what you see);
     security issues; anything blocking the core workflow; and small,
     clearly-valuable quick wins.
   - **→ `backlog` (idea pool, not auto-worked):** speculative or nice-to-have
     enhancements, cosmetic polish without clear priority, larger features that
     need a product decision, and anything ambiguous.
   - **When unsure, choose `backlog`** — `todo` is the explicit "build this"
     signal (see CLAUDE.md "Rollen und Lanes"); don't auto-schedule work the user
     hasn't clearly prioritised.

6. **Create the ticket.** `create "<concise title>" --priority <p> --tags
   <type>,<area> --assignee <lane>`, then `edit <id> --body` with a short,
   consistent spec matching the board's existing shape: **Ziel**, **Eigene
   Dateien**, **Vorgaben**, **Pruefung** (1–3 checkable criteria — without this a
   subagent cannot decide "done" on its own), and a trailer line `Erfasst via
   /findings (Test-Pass <date>)`. New tickets default to `backlog`; `move <id>
   todo` the ones you judged urgent.

   **Never let a new ticket own a file that an open ticket already owns.** That is
   the rule the whole parallel setup rests on. If the fix belongs in an open
   ticket's file, append it to that ticket instead of creating a new one.

## Close out

- **Board-sync (katche duty):** `git add kanban/ && git commit -m "chore(board):
  triage findings → #<ids>"` (stage **only** `kanban/`, never `git add -A`).
  (Board ops run from the board home — that's allowed; ticket *code* never is.)
- **Report a table** back to the user so overrides are easy: each finding →
  ticket `#id`, title, lane, `todo`/`backlog`, priority, and any dedup/low-
  confidence notes. Invite the user to re-sort any ticket (`todo`↔`backlog`) or
  re-prioritise.

Do **not** implement any of the tickets here — `/findings` only triages and
records them; the lane sessions build the `todo` ones via `/work-lane`.
