---
name: work-lane
description: Drive your assigned kanban lane on the kaimarkit board. Determines this session's identity dynamically via ~/.claude/bin/session-name, then fans each ready ticket out to a one-ticket subagent (<name>-NN) per the "Rollen und Lanes" + "Kontexthygiene" conventions in CLAUDE.md, keeping the parent session lean. Use when a worker session (benny/sophie/akar) should start or continue burning down its lane. Run as `/work-lane` for a single drive-to-empty pass, or wrap with `/loop` (e.g. `/loop /work-lane`) to keep pulling as new tickets arrive. Language follows the user.
---

# work-lane

Burn down **your** lane on the kaimarkit kanban board, fanning each ticket out to
a short-lived subagent so this session's context stays lean. Identity is resolved
at runtime — the same skill works in every session.

`kanban-md` lives at `~/go/bin/kanban-md` and is **not on the PATH**. Use the full
path in every call.

## 1. Identify yourself (dynamic)

Resolve which lane you own from the session name:

```bash
~/.claude/bin/session-name
```

Call the result **SELF** and branch on it:

- `benny` → **frontend** lane · `sophie` → **backend** lane · `akar` →
  **infrastructure, documentation, organizational + everything else** lane.
- `katche` → you are **PO/SM, not a worker**: do **not** pull an implementation
  lane. Instead do a grooming/standup pass (review the board, refill/rebalance
  lanes, coordinate merges, escalate) per CLAUDE.md "Rollen und Lanes", then stop.
- Anything else (e.g. a short hex id or a descriptive session name, because the
  session was never named for a lane) → **STOP** and tell the user to name the
  session (`claude -n <name>`); never guess a lane.

## 2. Internalize the conventions

Re-read these CLAUDE.md sections **fresh from disk** (they may have changed since
this session started) and follow them exactly:

- **Rollen und Lanes** — lane = the `assignee` field, one subagent ⇄ one ticket,
  concurrency limits, merge serialization.
- **Kontexthygiene** — stay a thin parent; subagents return short results.
- **Verbindliche Konventionen** — the six project rules. Two of them are the reason
  the lanes do not collide: the interface triad (`contracts/api.md`,
  `backend/app/models.py`, `frontend/src/types.ts` change together) and file
  ownership per ticket.

## 3. Finish in-flight work first

If you already hold a claim or have a ticket `in-progress` for SELF, take that to
done before pulling anything new (one active stream of work, no orphaned claims).

## 4. Drive the lane

Repeat until your lane is empty **and** no subagent of yours is still running:

1. From board home on `main`, list your lane:
   ```bash
   ~/go/bin/kanban-md list --assignee <SELF> --unblocked --not-blocked --status todo --sort priority -r
   ```
   **Both flags are required, and they are not the same thing.** `--unblocked`
   hides tickets whose `depends_on` predecessors are still open; `--not-blocked`
   hides tickets carrying an explicit `--block`. This board is wired with
   `depends_on`, so `--not-blocked` alone would list the whole lane as ready and
   a subagent would build BE-9 before the engines exist.

   **Only `todo` is worked.** `backlog` is the PO's idea pool and is **never
   auto-pulled** — katche/PO promotes a ticket to `todo` when it is ready to be
   built.
2. **Verify blockages are real before skipping a blocked ticket.** A block can go
   **stale** (the blocking ticket already merged, or the dependency no longer
   applies). So also list *all* `todo` tickets for SELF and diff them against the
   ready set from step 1:
   ```bash
   ~/go/bin/kanban-md list --assignee <SELF> --status todo --sort priority -r
   ```
   For each hidden (blocked) ticket, check whether the blockage **still holds**:
   is every `depends_on` ticket still open (not `done`/`archived`), and does each
   explicit `--block` still have a real reason?
   - If the blockage is genuine → leave it blocked, skip it.
   - If the blockage is **not real** → do **not** silently unblock and pull it.
     **Request the user's release in a dialog** and only proceed on their approval;
     then clear it (`--unblock` / `--remove-dep <id>`). Never auto-clear a block
     yourself.
3. For the highest-priority unclaimed ticket(s), **dispatch a subagent** named
   `<SELF>-NN` (NN = 01, 02, …) with a **self-contained prompt** (the subagent
   cannot see this session's history). The subagent must: claim the ticket as
   `<SELF>-NN`, then **as its very first action create and `cd` into its own
   worktree** (`git worktree add .worktrees/task-NN -b task/NN-slug`) and make
   **all** edits there — never under the shared board-home root (a guard hook
   blocks that) — through the standard loop (worktree → implement → pass the
   ticket's own **Pruefung** section → **docs (see Definition of done below)** →
   `--no-ff` merge → remove worktree → move the ticket to `done` **and release its
   claim** (`move <NN> done` then `edit <NN> --release`) so the closed ticket
   carries no live claim → leave a short result note), and **return only a short
   summary** `{ticket, done|blocked, branch, one-line note}` — detail goes in the
   board handoff note, not the reply.

   **Definition of done — the ticket's own Pruefung plus docs, not a follow-up.**
   In the **same worktree/merge** as the implementation the subagent MUST:
   - Run the **Pruefung** section from its own ticket body and actually pass it.
     Every ticket carries one; it is what lets the subagent decide "done" without
     asking back.
   - **Report test counts, not just pass/fail.** Run pytest as `pytest -q -rs`
     (`-rs` names every skip with its reason) and state the collection in the
     result note — "126 collected, 122 selected, 122 passed", never just
     "passed". All lanes share one pyenv environment, so a module that silently
     dropped out of collection is only visible in the numbers.
   - **If the Pruefung does not come out as specified, suspect the Pruefung before
     the work.** Report the deviation and hand the ticket back
     (`handoff <ID> --block "..." --note "..."`) instead of adjusting until the
     number fits. This concerns the *assumption* behind the check — a bug in the
     subagent's own code is still its bug and gets fixed.
   - Update the **documentation** (`docs/` pages + `CLAUDE.md`) for any
     user-visible behaviour or architecture/convention change. Note that
     `docker/.env.example` and `docs/betrieb/konfiguration.md` are a pair
     (CLAUDE.md convention 6) — a new variable touches both.
   - **Docs are owned per section, not per page.** Fix what your change made
     false — even on a page another ticket created — and report what was already
     false instead of fixing it. The PO turns reports into tickets.
   - Honour the **interface triad**: a change to `contracts/api.md`,
     `backend/app/models.py` or `frontend/src/types.ts` touches all three in the
     same commit. This one crosses lanes — say so in the ticket note so the other
     lane sees it.
   - A ticket is **not done** until docs reflect the change. Never defer docs to a
     later ticket.
4. **Concurrency:** at most **2–3** subagents at once; spin up only as many as
   there are non-colliding ready tickets; never let two subagents touch the same
   file. The board is cut so this holds — **every ticket body names the files it
   owns**, and no two open tickets own the same file. If you find two ready
   tickets that do share a file, that is a cut error: report it rather than
   running them in parallel. **Serialize merges** to `main` (one merge at a time).
5. **Stay thin:** you only dispatch and read the board — do not read files or run
   tests/builds yourself. That is what keeps the parent context small.

## 5. Stop / loop

When the lane is empty and no `<SELF>-NN` subagent is in flight, post a short
standup (done / in-flight / blocked) and stop.

- `/work-lane` alone → ends here (a single drive-to-empty pass).
- `/loop /work-lane` → this pass re-fires (self-paced, or `/loop <interval>
  /work-lane`) so the session keeps picking up newly-arriving or PO-released
  tickets without manual nudging.
