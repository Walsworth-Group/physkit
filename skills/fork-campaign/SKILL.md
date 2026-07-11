---
name: fork-campaign
description: >-
  Fork a campaign when a change INVALIDATES or makes misleading its prior findings — the honest,
  clean-break response to contamination (design §4.4b). Use when a bug or correction means the campaign's
  ledger can no longer be trusted to steer the next effort: phrasings like "this forward-model bug means
  the CNN was scored on wrong test data", "our metric was wrong so the rankings are invalid", "fork the
  campaign", "the baseline was contaminated — start clean but keep what still holds", "archive this and
  redo it right". It scaffolds a FRESH-LEDGER sibling campaign, moves the source into campaigns/_archive/
  (frozen, read-only, still indexed in LINEAGE for provenance), carries forward ONLY findings that survive
  independent RE-verification (each re-checked with provenance), and records the fork + what was invalidated
  + what carried over in LINEAGE.md. NOT for a routine fix that preserves rankings (that's a version bump —
  new-campaign / campaign-status), and NOT for a materially new approach with no inheritance (that's a fresh
  new-campaign). Composes new-campaign (the scaffold) and verify (the re-validation gate).
---

# fork-campaign — the invalidation clean break

A campaign's ledger is only as trustworthy as the infrastructure it was scored under. When a change
**invalidates or makes misleading** the findings a campaign accumulated — a forward-model bug meant a decoder
was scored on wrong test data, a metric error inverted the rankings, a corrected dataset changes which
approaches win — the honest response is **not** a quiet version bump that carries the tainted journal forward.
It is a **clean break**: a fresh-ledger campaign, the old one archived read-only, and **only** the findings that
survive re-verification carried across. This skill makes fork-and-archive a first-class move so a journal built
on a known-bad model can never silently steer the next effort (the memory-contamination failure at campaign
scale). See `synthesis/PROJECT_STRUCTURE_DESIGN.md` §4.4.

## First: is a fork actually the right move? (the finding-validity decision, §4.4)
Ask the one question that drives everything: **does this change invalidate or make misleading the campaign's
prior findings?**
- **(a) Findings stay valid** — a small fix, or a metric refinement that *preserves the rankings*. → **NOT a
  fork.** Do a **version bump within the campaign** (`metric_version` / `data_version`), re-score affected rows
  under the comparability guard, and log a one-line change-record in `LINEAGE.md`. (Handled by the normal loop /
  `campaign-status`, not here.)
- **(b) Findings are invalidated or made misleading** — approaches may have been wrongly discarded or promoted
  on bad infrastructure. → **FORK-AND-ARCHIVE. This skill.**
- **(c) A materially new approach** (new architecture / objective / outputs), with no inheritance beyond shared
  data/artifacts. → a **new campaign** (`new-campaign`), not a fork — there's nothing tainted to break from.

If (a) or (c), stop and route there. Only proceed below for (b). When unsure between (a) and (b): if you cannot
show the change *preserves the rankings*, treat it as (b) — the cost of a wrongly-carried-forward tainted
finding is far higher than a clean re-verification.

## Preconditions
- This runs **inside a project** (`new-project` home): the source campaign is `campaigns/<src>/` and there is a
  `../../LINEAGE.md`. (A standalone campaign with no project has no archive/LINEAGE machinery — offer to lift it
  into a project first with `new-project`, or fork manually.)
- Know **what broke** and **which findings it taints** before forking — usually the output of a `debug` /
  `verify` session that exposed the invalidating bug. Do not fork on suspicion; fork on a diagnosed cause.

## Procedure

### 1. Diagnose & record the invalidation
Write down, precisely: **what changed** (the bug/correction), **why it invalidates** the prior findings (which
scored quantities were wrong and how), and **which specific findings/promotions are now suspect** — every
DISCOVERY, every "current best", every written-off approach that was decided on the bad infrastructure. This is
the fork's justification and goes into `LINEAGE.md`. A finding is suspect until *proven* still-valid, not the
reverse.

### 2. Archive the source (frozen, read-only, still indexed)
- Move `campaigns/<src>/` → **`campaigns/_archive/<src>/`** (create `_archive/` if absent). Nothing is deleted —
  the archived campaign stays for provenance.
- Mark it **frozen/read-only**: drop a `FROZEN.md` at its root stating it was archived by a fork on `<date>`,
  the invalidation reason, and "read-only — do not resume; superseded by `campaigns/<new>/`." (On a shared drive,
  filesystem read-only is unreliable — the marker + the `LINEAGE.md` status are the real enforcement, not perms.)
- Its `results/`, `JOURNAL.md`, `scoreboard.tsv`, `DISCOVERIES.md` **do NOT become working documents of the new
  effort.** They are read-only history. The new campaign starts from a clean ledger — never by copying these
  forward.

### 3. Scaffold the fresh-ledger campaign (compose `new-campaign`)
Invoke **`new-campaign`** in the project to create a new sibling `campaigns/<NN>_<slug>/` with a **clean
scoreboard / JOURNAL / DISCOVERIES**. Carry over, deliberately and explicitly:
- the **corrected** infrastructure (the fixed forward model / metric / dataset) — validated *before* it is
  re-frozen (`correctness-suite`: the sign/convention round-trip + symmetry self-tests that would have caught
  the original bug — add the check that failed as a standing regression gate);
- the shared data + promoted artifacts from `../../shared/` (unchanged — referenced, never copied);
- the FROZEN metric spec and levers, re-examined for whether the bug touched them.
Do **not** carry over the old ledger, the old current-best config as "best", or any conclusion — those are
re-earned in step 4.

### 4. Carry forward ONLY what survives RE-verification (the honesty gate)
For each prior finding the user wants to keep, **re-verify it from scratch under the corrected setup** — re-run
`verify` (which spawns an independent refuter), recompute every number on the fixed infrastructure, and grade it
again. Then:
- A finding that returns **CONFIRMED** under the corrected setup carries forward into the new campaign's
  `DISCOVERIES.md`, tagged with its **provenance**: "carried from `<src>` and re-verified after the fork on
  `<date>`, verdict CONFIRMED" — never on the strength of the *old* verdict.
- A finding that does **not** survive is **left in the archive**, not carried — and if it had been promoted, note
  in `LINEAGE.md` that the fork retracted it.
- **No claim-splitting, no silent inheritance.** A number is inseparable from the infrastructure it was scored
  under; if that infrastructure was the bug, the number is refuted-until-re-earned.

### 5. Record the fork in `LINEAGE.md`
Update the project index so the history is complete and honest:
- Set the archived campaign's **status → `archived(forked)`**; leave its row (provenance never disappears).
- Append the **new campaign's row** (status `active`), with *what changed from predecessor* = the fork reason,
  and a note linking it to the archived source.
- Record, in the row or a fork note: **what was invalidated** and **what carried over re-verified** (with the
  verify verdicts). Anyone reading `LINEAGE.md` must be able to see that a fork happened, why, and which prior
  conclusions did and didn't survive.

## Verify (before you hand off)
- The source is in `campaigns/_archive/`, carries its `FROZEN.md`, and its `LINEAGE.md` status is `archived(forked)`.
- The new campaign has a **clean** ledger (no copied scoreboard/JOURNAL rows) and passes `validate_campaign.py`.
- Every carried-forward finding shows a **post-fork** CONFIRMED verdict with provenance; nothing rode in on an
  old verdict.
- `LINEAGE.md` records the fork, the invalidation reason, and the carried/dropped findings.

## Composition & boundaries
Composes **`new-campaign`** (the fresh scaffold) and **`verify`** (the re-validation gate); pairs with **`debug`**
(which usually diagnoses the invalidating bug) and **`correctness-suite`** (which re-validates the corrected
infrastructure before re-freezing). It is the honest counterpart to a version bump: a version bump keeps the
ledger because rankings held; a fork breaks the ledger because they didn't. NOT for scaffolding a brand-new
investigation (`new-project`), a routine fix (version bump), or a new approach (`new-campaign`).
