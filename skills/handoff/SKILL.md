---
name: handoff
description: >-
  Write a cold-resumable handoff so a fresh agent (or you, weeks later, with no memory of the session) can
  pick up long or complex work without the original context. Use at the end of a work session, before
  pausing a campaign, when handing off to another person or agent, or whenever context is about to reset.
  It captures four things: the vision and goal, the current state including the in-flight reasoning (what
  you were doing and why), a concrete "run this to confirm state" command that verifies the environment and
  reproduces where things stand, and a prioritized roadmap of next steps. Prior handoffs are archived, never
  overwritten, so the trail of reasoning is preserved. It resumes from LINEAGE.md (the cross-campaign index)
  and checks whole-tree portability. Pairs with campaign-status (health) and the PROJECT_ORIENTATION.md doc
  (goal/tasks).
---

# handoff — make the work cold-resumable

The expensive failure at a session boundary is **lost context**: a fresh agent re-derives what you already
knew, distrusts a state it can't confirm, or pursues a direction you'd already ruled out. A handoff is the
antidote — a single document that lets someone with **only this file and the repo** understand where the
work is, trust that state, and know the next move. Write it whenever the work will outlive your current
context.

The test it must pass: **could a fresh agent, with no memory of this session, read this handoff + the repo
and (a) know what we're trying to do, (b) trust where things stand, and (c) take the next step — without
asking you?** If not, it's incomplete.

**Flush converged decisions to disk as they lock — don't wait for the handoff.** A design or plan that
exists only in the conversation is one interrupted session away from gone. When a decision or plan
converges (e.g. locked via an AskUserQuestion, or a design you've settled), write it to a real file *then*;
the handoff *distills* durable artifacts, it is not the only place they should first appear. (A real
~80-turn design session ended with zero files written and had to be reconstructed from the raw transcript.)

## The four parts

1. **Vision & goal — where this is headed and why.** The end goal and the decision it drives (pull from
   `PROJECT_ORIENTATION.md` if it exists), and the one-paragraph "why this matters" that orients everything
   else. Enough that the resumer understands the *point*, not just the next task.

2. **Current state — including the in-flight reasoning.** Where things actually stand: what's done, what's
   in-flight, the current best/result and its **verification status**, and the open threads. Critically,
   capture the **reasoning you were mid-stream on** — the hypothesis being tested, *why* you were testing
   it, what you expected, and what you'd just learned. This is the part that evaporates and is the hardest
   to reconstruct from artifacts. Note any landmine (a known-broken thing, a dead end already ruled out,
   a flaky step).
   - **Leave no orphan.** Every scoreboard row / `result_*.json` must have its narrative completed and a
     **graded verdict** before you hand off — a result whose analysis was deferred at the session boundary
     is the single most common thing lost (it survives on disk while its meaning evaporates).
   - **Before claiming a requested deliverable "wasn't done," look outside the campaign tree.** A prior
     session may have written it to a sibling directory or an absolute path. **Grep the recent session
     transcript(s) for `Write`/`Bash` targets**, don't just `ls` the campaign root — a real handoff once
     declared a finished, smoke-tested deliverable "never created" because it read only the tree. State a
     deliverable missing only after that search comes up empty.

3. **"Run this to confirm state" — a concrete check.** A command (or short sequence) the resumer runs
   *first* to verify the environment works and the stated state is real: e.g. activate the env, run the
   metric `--selftest`, run the `correctness-suite` (expect green), and re-derive the current-best number
   from its snapshot (expect the stated value). A resumer who can reproduce the state trusts it; one who
   can't knows immediately, before building on sand. State the **expected output** so a mismatch is
   obvious.

4. **Roadmap / NEXT — prioritized, goal-linked.** The next steps in priority order, each tied to how it
   serves the goal, with enough specificity to act on (not "improve the model" but "test the canting term
   on the coercive-band subset — exp queue in JOURNAL NEXT"). Keep it in sync with the `PROJECT_ORIENTATION`
   tasks and the JOURNAL NEXT pointer.

## Resume from `LINEAGE.md`, check whole-tree portability
The campaign sits in a project (`PROJECT.md` + `LINEAGE.md` above it), so the handoff is project-aware:
- **Vision/goal** also come from `PROJECT.md` (the investigation-wide goal), and the project-wide state is
  **`LINEAGE.md`** — the index of every campaign + session, what each changed and found. A resumer reads
  `LINEAGE.md` **first** to see where the whole investigation stands (which campaign is active, what's
  archived/forked, what's verified), then descends into the active campaign's own docs. Name `LINEAGE.md` as the
  first resume anchor.
- **Current state** notes which campaign is active (its `LINEAGE.md` row), any sibling coupling in play (a frozen
  artifact consumed from `../../shared/`), and whether a recent change is a **`fork-campaign`** trigger
  (invalidated a sibling's findings) rather than a local matter.
- **Portability check over the project tree.** The tree must relocate as one unit — every reference relative, the
  only absolute path the resolved `data_path`. Add the project validator to "run this to confirm state":
  `python "${CLAUDE_PLUGIN_ROOT}/skills/new-campaign/scripts/validate_campaign.py" <project_root>` (structure +
  every campaign indexed in `LINEAGE.md` + no absolute paths in configs). A broken path or an un-indexed
  campaign is a resume landmine.

## Archive, don't overwrite
A handoff is part of the record. **Never overwrite the previous one** — write a new dated file
(`handoff_<UTC-date>.md`) and move the prior into an `archive/` (or keep an append-only sequence). The
trail of successive handoffs is the campaign's reasoning history; it shows how the understanding evolved and
prevents re-litigating settled decisions. The newest handoff is the live one; the archive is consulted when
"why did we abandon X?" comes up (`record-decision` holds the durable why; the handoff holds the moment).

## Composition
- **`PROJECT_ORIENTATION.md`** — source of the vision/goal and the task roadmap (the handoff *references* it,
  doesn't duplicate the full hierarchy).
- **`LINEAGE.md` + `PROJECT.md`** — the cross-campaign index a resumer reads first and the investigation-wide
  goal; the handoff points at the active campaign's row rather than duplicating the index.
- **`campaign-status`** — its latest checkpoint feeds "current state"; run it before a handoff if stale.
- **`correctness-suite` / `verify` / the metric self-test** — the "run this to confirm state" commands.
- **the logbook / JOURNAL** — the narrative the handoff distills; the handoff points into them rather than
  copying.
- **a background distiller** (`context-economy`, model tiering) — on long runs, a lighter-model watcher that
  continuously extracts decisions / corrections / open threads into notes keeps the "current state +
  in-flight reasoning" from evaporating, so the handoff is cheap to assemble and never starts from a blank
  transcript.

## Bundled asset
- `assets/handoff_template.md` — the four-part structure (vision · state + in-flight reasoning · confirm-state
  command · roadmap), dated, with the archive note.

## Checklist
- [ ] Vision & goal stated — a resumer understands the point, not just the next task.
- [ ] Current state captures the **in-flight reasoning** (hypothesis, why, expectation, last learning), not just artifacts.
- [ ] Current-best result + its verification status recorded; landmines/dead-ends noted.
- [ ] **No orphaned result** handed off — every scoreboard row / `result_*.json` has a completed narrative and a graded verdict.
- [ ] Before asserting a deliverable "wasn't done," the recent transcript(s) were searched for artifacts written **outside** the campaign root.
- [ ] A "run this to confirm state" command with its **expected output** is given.
- [ ] A prioritized, goal-linked NEXT roadmap is present and synced with the JOURNAL NEXT.
- [ ] The prior handoff was archived, not overwritten.
- [ ] Resume anchors are current: the newest handoff/JOURNAL covers the **latest** session; any external digest (e.g. a user's `_claude-archive/INDEX.md`) is treated as advisory and flagged if its date lags the newest work.
- [ ] `LINEAGE.md` is named as the first resume anchor, and the tree passes the portability/structure validator (no absolute paths; every campaign indexed).
- [ ] Cold-resume test passes: a fresh agent could act from this file + the repo alone.
