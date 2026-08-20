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

Lost context is the failure mode at a session boundary: a fresh agent re-derives what the last session
established, distrusts a state it cannot confirm, or repeats a ruled-out direction. A handoff is one
document that lets a reader holding only this file and the repo locate the work, trust its state, and take
the next step. Write one whenever the work will outlive the current context.

The test it must pass: a fresh agent with no memory of this session reads this handoff and the repo, then
(a) knows the goal, (b) trusts where things stand, and (c) takes the next step without asking. A handoff
failing any of the three is incomplete.

Flush converged decisions to disk as they lock; do not wait for the handoff. A plan that exists only in the
conversation is lost when the session is interrupted, or must be reconstructed from the raw transcript.
Write each decision or design, including one locked via an AskUserQuestion, to a real file at the moment it
converges. The handoff distills durable artifacts; it is not where they first appear.

## The four parts

1. **Vision & goal — where this is headed and why.** The end goal and the decision it drives, pulled from
   `PROJECT_ORIENTATION.md` where it exists, and the one-paragraph statement of why the work matters. Enough
   that the resumer understands the purpose, not only the next task.

2. **Current state — including the in-flight reasoning.** What is done, what is in-flight, the current best
   result and its verification status, and the open threads. Capture the reasoning that was mid-stream: the
   hypothesis being tested, why it was being tested, what was expected, and what had just been learned.
   That part evaporates and is the hardest to reconstruct from artifacts. Note any landmine: a known-broken
   thing, a dead end already ruled out, a flaky step.
   - **Leave no orphan.** Complete the narrative and a graded verdict for every scoreboard row and every
     `result_*.json` before the handoff. A result whose analysis is deferred at a session boundary survives
     on disk while its meaning is lost.
   - Search outside the campaign tree before recording a requested deliverable as not done. A prior session
     may have written it to a sibling directory or an absolute path, and listing the campaign root alone
     then reports a finished, smoke-tested deliverable as never created. Grep the recent session
     transcript(s) for `Write` and `Bash` targets. State a deliverable missing only after that search comes
     up empty.

3. **"Run this to confirm state" — a concrete check.** A command, or short sequence, the resumer runs first
   to verify the environment works and the stated state is real: activate the env, run the metric
   `--selftest`, run the `correctness-suite` (expect green), and re-derive the current-best number from its
   snapshot (expect the stated value). A resumer who can reproduce the state trusts it; one who cannot
   learns that before building on it. State the expected output so a mismatch is obvious.

4. **Roadmap / NEXT — prioritized, goal-linked.** The next steps in priority order, each tied to how it
   serves the goal, with enough specificity to act on. "Improve the model" is not actionable; "test the
   canting term on the coercive-band subset, experiment queue in JOURNAL NEXT" is. Keep it in sync with the
   `PROJECT_ORIENTATION` tasks and the JOURNAL NEXT pointer.

## Resume from `LINEAGE.md`, check whole-tree portability
The campaign sits in a project (`PROJECT.md` and `LINEAGE.md` above it), so the handoff is project-aware:
- **Vision/goal** also come from `PROJECT.md`, the investigation-wide goal. The project-wide state is
  `LINEAGE.md`: the index of every campaign and session, what each changed and found. A resumer reads
  `LINEAGE.md` first for where the whole investigation stands (active campaign, archived or forked
  campaigns, what is verified), then descends into the active campaign's own docs. Name `LINEAGE.md` as the
  first resume anchor.
- **Current state** notes which campaign is active by its `LINEAGE.md` row, any sibling coupling in play
  such as a frozen artifact consumed from `../../shared/`, and whether a recent change is a
  `fork-campaign` trigger, meaning it invalidated a sibling's findings, rather than a local matter.
- **Portability check over the project tree.** The tree must relocate as one unit: every reference relative,
  and the resolved `data_path` the only absolute path. Add the project validator to "run this to confirm
  state": `python "${CLAUDE_PLUGIN_ROOT}/skills/new-campaign/scripts/validate_campaign.py" <project_root>`
  checks structure, indexing of every campaign in `LINEAGE.md`, and absence of absolute paths in configs. A
  broken path or an un-indexed campaign is a resume landmine.

## Archive, don't overwrite
A handoff is part of the record. Never overwrite the previous one. Write a new dated file
(`handoff_<UTC-date>.md`) and move the prior one into an `archive/`, or keep an append-only sequence. The
trail of successive handoffs is the campaign's reasoning history: it shows how the understanding evolved and
prevents re-litigating settled decisions. The newest handoff is the live one; the archive answers why a
direction was abandoned. `record-decision` holds the durable why, the handoff holds the moment.

## Composition
- `PROJECT_ORIENTATION.md` — source of the vision/goal and the task roadmap. The handoff references it
  rather than duplicating the full hierarchy.
- `LINEAGE.md` and `PROJECT.md` — the cross-campaign index a resumer reads first, and the
  investigation-wide goal. The handoff points at the active campaign's row rather than duplicating the index.
- `campaign-status` — its latest checkpoint feeds "current state". Run it before a handoff if stale.
- `correctness-suite`, `verify`, and the metric self-test — the "run this to confirm state" commands.
- the logbook / JOURNAL — the narrative the handoff distills. The handoff points into them rather than
  copying.
- a background distiller (`context-economy`, model tiering) — on long runs, a lighter-model watcher that
  extracts decisions, corrections, and open threads into notes keeps the current state and in-flight
  reasoning from evaporating, so the handoff is cheap to assemble and never starts from a blank transcript.

## Bundled asset
- `assets/handoff_template.md` — the four-part structure (vision · state + in-flight reasoning · confirm-state
  command · roadmap), dated, with the archive note.

## Checklist
- [ ] Vision and goal stated: a resumer understands the purpose, not just the next task.
- [ ] Current state captures the in-flight reasoning (hypothesis, why, expectation, last learning), not just artifacts.
- [ ] Current-best result and its verification status recorded; landmines and dead ends noted.
- [ ] No orphaned result handed off: every scoreboard row and `result_*.json` has a completed narrative and a graded verdict.
- [ ] Before asserting a deliverable "wasn't done," the recent transcript(s) were searched for artifacts written outside the campaign root.
- [ ] A "run this to confirm state" command with its expected output is given.
- [ ] A prioritized, goal-linked NEXT roadmap is present and synced with the JOURNAL NEXT.
- [ ] The prior handoff was archived, not overwritten.
- [ ] Resume anchors are current: the newest handoff/JOURNAL covers the latest session; any external digest is advisory and is flagged when its date lags the newest work.
- [ ] `LINEAGE.md` is named as the first resume anchor, and the tree passes the portability/structure validator (no absolute paths; every campaign indexed).
- [ ] Cold-resume test passes: a fresh agent could act from this file and the repo alone.
