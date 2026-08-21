---
name: fork-campaign
description: >-
  Fork a campaign when a change INVALIDATES or makes misleading its prior findings — the honest,
  clean-break response to contamination (design §4.4b). Use when a bug or correction means the campaign's
  ledger can no longer be trusted to steer the next effort: phrasings like "this forward-model bug means
  the CNN was scored on wrong test data", "our metric was wrong so the rankings are invalid", "fork the
  campaign", "the baseline was contaminated — start clean but keep what still holds", "archive this and
  redo it right". It scaffolds a FRESH-LEDGER sibling campaign, moves the source into campaigns/_archive/
  (frozen, read-only, still indexed in the lineage for provenance), carries forward ONLY findings that survive
  independent RE-verification (each re-checked with provenance), and records the fork + what was invalidated
  + what carried over in the project lineage (PROJECT.md §Lineage; old layout: LINEAGE.md). NOT for a routine fix that preserves rankings (that's a version bump —
  new-campaign / campaign-status), and NOT for a materially new approach with no inheritance (that's a fresh
  new-campaign). Composes new-campaign (the scaffold) and verify (the re-validation gate).
---

# fork-campaign — the invalidation clean break

A campaign's ledger is only as trustworthy as the infrastructure it was scored under. Some changes invalidate
or make misleading the findings a campaign accumulated: a forward-model bug that scored a decoder on wrong test
data, a metric error that inverted the rankings, a corrected dataset that changes which approaches win. A
version bump that carries the tainted journal forward is not a permitted response to such a change. The
required response is a clean break: a fresh-ledger campaign, the source archived read-only, and only the
findings that survive re-verification carried across. Fork-and-archive is a first-class move so a journal
built on a known-bad model can never silently steer the next effort, the memory-contamination failure at
campaign scale.

## First: is a fork actually the right move?
One question drives the decision: does this change invalidate or make misleading the campaign's prior findings?
- (a) Findings stay valid — a small fix, or a metric refinement that preserves the rankings. Not a fork. Do a
  version bump within the campaign (`metric_version` / `data_version`), re-score affected rows under the
  comparability guard, and log a one-line change-record in the lineage. The normal loop and `campaign-status`
  handle this, not this skill.
- (b) Findings are invalidated or made misleading — approaches may have been wrongly discarded or promoted on
  bad infrastructure. Fork-and-archive. This skill.
- (c) A materially new approach (new architecture, objective, or outputs), with no inheritance beyond shared
  data and artifacts. A new campaign (`new-campaign`), not a fork: there is nothing tainted to break from.

If (a) or (c), stop and route there. Proceed below only for (b). When unsure between (a) and (b): if you cannot
show the change preserves the rankings, treat it as (b). The cost of a wrongly-carried-forward tainted finding
exceeds the cost of a clean re-verification.

## Preconditions
- The source campaign sits in its project: `campaigns/<src>/` with a `../../PROJECT.md` carrying the
  **lineage** — `PROJECT.md` §Lineage, or the old layout's separate `LINEAGE.md`; "the lineage" below
  means whichever this project has.
- A legacy bare campaign is lifted into a project first (`new-campaign` Step 0.1); the archive and lineage
  machinery this skill needs exists nowhere else.
- Know what broke and which findings it taints before forking. A `debug` or `verify` session that exposed the
  invalidating bug supplies that diagnosis. Do not fork on suspicion; fork on a diagnosed cause.

## Procedure

### 1. Diagnose & record the invalidation
Write down, precisely: what changed (the bug or correction); why it invalidates the prior findings (which
scored quantities were wrong, and how); and which specific findings and promotions are now suspect. The suspect
list covers every DISCOVERY, every current best, and every written-off approach decided on the bad
infrastructure. This is the fork's justification and goes into the lineage. A finding is suspect until proven
still-valid, not the reverse.

### 2. Archive the source (frozen, read-only, still indexed)
- Move `campaigns/<src>/` to `campaigns/_archive/<src>/`, creating `_archive/` if absent. Nothing is deleted:
  the archived campaign stays for provenance.
- Mark it frozen and read-only. Drop a `FROZEN.md` at its root stating that it was archived by a fork on
  `<date>`, the invalidation reason, and "read-only — do not resume; superseded by `campaigns/<new>/`."
- Filesystem read-only permissions are unreliable on a shared drive. The `FROZEN.md` marker and the
  lineage status are the enforcement, not permissions.
- Its `results/` — `JOURNAL.md` (Findings included), `scoreboard.tsv`, the logbook — do not become working
  documents of the new effort. They are read-only history. The new campaign starts from a clean ledger,
  never by copying these forward.

### 3. Scaffold the fresh-ledger campaign (compose `new-campaign`)
Invoke `new-campaign` in the project to create a new sibling `campaigns/<NN>_<slug>/` with a clean scoreboard
and JOURNAL (an empty Findings section included). Carry over, deliberately and explicitly:
- the corrected infrastructure (the fixed forward model, metric, or dataset), validated before it is re-frozen.
  Run `correctness-suite`: the sign and convention round-trip plus the symmetry self-tests that would have
  caught the original bug. Add the check that failed as a standing regression gate.
- the shared data and promoted artifacts from the project level (`../../data`, `../../models/`, …;
  old layout: `../../shared/`), unchanged: referenced, never copied.
- the FROZEN metric spec and levers, re-examined for whether the bug touched them.

Do not carry over the old ledger, the old current-best config as "best", or any conclusion. Those are re-earned
in step 4.

### 4. Carry forward ONLY what survives RE-verification (the honesty gate)
For each prior finding the user wants to keep, re-verify it from scratch under the corrected setup: re-run
`verify`, which spawns an independent refuter, recompute every number on the fixed infrastructure, and grade it
again. Then:
- A finding that returns CONFIRMED under the corrected setup carries forward into the new campaign's
  journal Findings section, tagged with its provenance: "carried from `<src>` and re-verified after the
  fork on `<date>`, verdict CONFIRMED" and citing the NEW verdict artifact. A finding never carries
  forward on the strength of the old verdict.
- A finding that does not survive is left in the archive, not carried. If it had been promoted, note in
  the lineage that the fork retracted it.
- No claim-splitting, no silent inheritance. A number is inseparable from the infrastructure it was scored
  under. If that infrastructure was the bug, the number is refuted-until-re-earned.

### 5. Record the fork in the lineage
Update the project index so the history is complete and honest:
- Set the archived campaign's status to `archived(forked)`. Leave its row in place: provenance never
  disappears.
- Append the new campaign's row with status `active`, with *what changed from predecessor* set to the fork
  reason, and a note linking it to the archived source.
- Record, in the row or a fork note, what was invalidated and what carried over re-verified, with the verify
  verdicts. Anyone reading the lineage must be able to see that a fork happened, why, and which prior
  conclusions did and did not survive.

## Verify (before you hand off)
- The source is in `campaigns/_archive/`, carries its `FROZEN.md`, and its lineage status is `archived(forked)`.
- The new campaign has a clean ledger (no copied scoreboard or JOURNAL rows) and passes
  `validate_campaign.py`.
- Every carried-forward finding shows a post-fork CONFIRMED verdict with provenance; nothing rode in on an old
  verdict.
- The lineage records the fork, the invalidation reason, and the carried and dropped findings.

## Composition & boundaries
Composes `new-campaign` (the fresh scaffold) and `verify` (the re-validation gate). Pairs with `debug` (which
diagnoses the invalidating bug) and `correctness-suite` (which re-validates the corrected infrastructure before
re-freezing). A version bump keeps the ledger because the rankings held; a fork breaks it because they did not.
Not for scaffolding a brand-new investigation (`new-project`), a routine fix (a version bump), or a new
approach (`new-campaign`).
