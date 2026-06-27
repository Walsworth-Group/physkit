---
name: campaign-status
description: Periodic health-check, journal consolidation, and N-experiment checkpoint for a running autoresearch campaign. Use when the user asks for campaign status, a health check, a checkpoint, "where do we stand", or to consolidate/trim a long journal — or automatically every N experiments per the loop. Reads the scoreboard, journal, discoveries, and program.md to summarize progress against the baseline and trivial references, flag plateaus and unverified current-bests, run hygiene checks (every result saved, disputes preserved, the metric self-test passing), consolidate the journal when it grows long, and queue the next orthogonal directions as the NEXT pointer. Read-mostly — it never edits the scoreboard, results, or the frozen scorer/physics. NOT for scaffolding a campaign (new-campaign), verifying a single finding (verify), or writing the end-of-campaign report (final-report).
---

# campaign-status — the operator's checkpoint

A running campaign drifts: the journal balloons, an unverified result quietly becomes "current best",
a lever gets over-mined while an orthogonal one sits untried, progress plateaus without anyone naming
it. This skill is the periodic step back — it reports where the campaign stands, fixes hygiene, trims
the journal, and re-points the loop at the most promising orthogonal directions.

**Read-mostly.** Its only writes are: consolidating the JOURNAL, updating the **NEXT** pointer, and
appending a dated checkpoint note. It never edits the scoreboard, results, configs, or anything FROZEN.

## When to invoke
- Every **N experiments** (the checkpoint cadence named in `docs/program.md`).
- When the JOURNAL has grown long (~150+ lines) and needs consolidation.
- On demand — "where do we stand?", "is the campaign healthy?", "run a checkpoint".

## Step 0 — learn the campaign
Read `docs/program.md` (or `docs/program_<NAME>.md`) for the primary metric + direction, the guardrail,
the baseline/floor, the levers, the checkpoint cadence N, and whether literature search is enabled. Read
the protocols it points to: `docs/protocols/checkpoint.md` and `docs/protocols/journal_consolidation.md`.
Also read **`docs/PROJECT_ORIENTATION.md`** (goal, expectations, goal-linked tasks) and
**`docs/VERIFICATION_PLAN.md`** — the checkpoint re-checks orientation against these, not only the metric.

## Procedure

### 0.5 Orientation re-check
Against `PROJECT_ORIENTATION.md`: is the **goal still the right goal**? Have the **loosely-held
expectations** shifted on the evidence (update them — that's success, not drift)? Are the goal-linked
tasks still serving it, their status current? Has a **discovery unblocked a parked direction** that should
re-open? Realigning here is the point of a checkpoint — the metric can climb while the campaign wanders
off its goal.

### 1. Health summary
From `results/scoreboard.tsv`, `results/JOURNAL.md`, and `results/DISCOVERIES.md`:
- **Current best vs references.** State the current-best primary metric and its margin over the
  baseline (exp 000) **and the trivial/degenerate references** — if a trivial reference is beating the
  current best, that is a red alert (and a *non-physical* trivial winner flags a metric/units problem,
  not a target). Note whether the current best is independently **verified** (CONFIRMED) or still
  PROVISIONAL/unverified.
- **Trend.** Is the primary still climbing, or has it **plateaued** (little gain over the last ~N
  experiments)? Is the guardrail also stuck (capacity/data-limited) or still moving
  (generalization-limited)?
- **Complexity trajectory.** Is the approach getting **more complex without commensurate payoff** — more
  parameters, more moving parts, more special-casing for shrinking gains? Rising complexity at a plateau
  is a pivot signal (and a parsimony smell): flag it, and consider whether a simpler approach was
  abandoned too early.
- **Lever coverage.** Which lever families have been mined hard, which are barely explored — so the
  re-plan can escalate to an *orthogonal* lever rather than the same knob.

### 2. Hygiene checks
Flag (don't silently fix) anything wrong:
- Every scoreboard row has a matching `results/result_<NN>.json` and its config in `configs/`; a result
  that exists only in the console is not saved.
- The **current-best is independently verified** — if a config is acting as current-best or a DISCOVERY
  without a CONFIRMED `verify` verdict, recommend running `verify` on it now.
- **Dispute records are intact** (the JOURNAL's append-only verifier/user challenges) — never trimmed.
- PROVISIONAL findings are tracked and not silently treated as settled.
- The metric **self-test still passes** (`python scripts/metric.py --selftest`) and diagnostics were
  tee'd to logs, not left in the console.
- **The correctness suite is GREEN** — if the campaign maintains a `correctness-suite`, confirm it was
  re-run after the latest core change and passes; a result standing on a red suite is not trustworthy.
- **Every experiment has its reproducibility snapshot** (`results/snapshots/<label>/` — config + code +
  manifest); a result without one is not "saved".

### 3. Consolidate the journal (if long)
If the JOURNAL exceeds ~150 lines (or the protocol's trigger), apply `journal_consolidation.md`:
graduate settled **and CONFIRMED** findings to `DISCOVERIES.md`; keep the live window (recent
experiments + open threads); compress older entries to one line each; **preserve negative-result lessons
and dispute records** (never delete them); never touch the scoreboard.

### 4. Re-plan (diagnose before pivoting)
If the campaign is stuck or plateaued, **diagnose the failure type before jumping** (idea-wrong /
implementation-capped / fixed-choice-fought / near-miss) and take the smallest justified jump on the
refine↔pivot spectrum — escalate to an *orthogonal* lever only once the current family is exhausted, but
do escalate decisively when it is (`docs/reference/pivoting.md`). A rising-complexity plateau argues for a
pivot, not more special-casing; a near-miss argues for gathering more evidence, not abandoning. Write the
few most promising directions as the JOURNAL **NEXT** pointer. If plateaued and literature search is
enabled, trigger a search (per `docs/program.md`) and fold its top priorities in.

### 5. Report
Append a short dated checkpoint note to the JOURNAL (best metric, trend, top issues, next directions),
and give the user a concise status: **current best + margin over baseline/trivial, verified?, trend,
the top 1–3 issues, and the next directions.** Surface any hygiene flag loudly — an unverified
current-best or a trivial reference beating the field is worth interrupting for.

## Notes
- For a large campaign you may fan the hygiene scan and the per-lever progress summary out to subagents,
  then synthesize centrally — but keep the consolidation and the NEXT pointer edits in one place. Those
  fan-out scans suit a **lighter model**; keep the synthesis and the NEXT-pointer judgment on the strong one.
- This skill recommends `verify` and literature searches; it does not run experiments or promote
  results itself.
