---
name: campaign-status
description: Periodic health-check, journal consolidation, and N-experiment checkpoint for a running autoresearch campaign. Use when the user asks for campaign status, a health check, a checkpoint, "where do we stand", or to consolidate/trim a long journal — or automatically every N experiments per the loop. Reads the scoreboard, journal, discoveries, and program.md to summarize progress against the baseline and trivial references, flag plateaus and unverified current-bests, run hygiene checks (every result saved, disputes preserved, the metric self-test passing), consolidate the journal when it grows long, and queue the next orthogonal directions as the NEXT pointer. Read-mostly — it never edits the scoreboard, results, or the frozen scorer/physics. NOT for scaffolding a campaign (new-campaign), verifying a single finding (verify), or writing the end-of-campaign report (final-report).
---

# campaign-status — the operator's checkpoint

A running campaign drifts: the journal balloons, an unverified result quietly becomes "current best",
a lever gets over-mined while an orthogonal one sits untried, progress plateaus without anyone naming
it. This skill is the periodic step back — it reports where the campaign stands, fixes hygiene, trims
the journal, and re-points the loop at the most promising orthogonal directions.

**Read-mostly.** Its only writes are: consolidating the JOURNAL, updating the **NEXT** pointer, appending
a dated checkpoint note, and snapshotting the session transcript to `transcripts/` (provenance). It never
edits the scoreboard, results, configs, or anything FROZEN.

## When to invoke
- Every **N experiments** (the checkpoint cadence named in `docs/program.md`).
- When the JOURNAL has grown long (~150+ lines) and needs consolidation.
- On demand — "where do we stand?", "is the campaign healthy?", "run a checkpoint".
- **Not only on a count.** Reflection is the campaign's error-correction step — don't let it wait for the
  experiment counter. Also reflect after a **surprising result**, at a **plateau**, **before any "we're done /
  at the ceiling / blocked" stopping decision** (Ctx 9), and after a long stretch of wall-clock with no
  checkpoint. Schedule it, per Wieman's reflective-decision discipline (the reflection decisions are the most
  important *and* the hardest, precisely because the immediate work crowds them out).

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

**Reflect against confirmation bias (the reflective decisions — the campaign's error-correction).** For the
current best and the current direction, run the ritual explicitly, don't just intend to be objective: **state
what you hoped/expected**, **argue the strongest case it's wrong**, **name the observation that would refute
it** (and check you ran it), and **surface the alternative conclusion you've been resisting** (it's noise; a
rival explains it too; it's an artifact). This is the hardest step to do honestly — the pull is to confirm
what you already believe — and it's exactly where a scaffold earns its keep. (Depth: the `verify` §5c ritual.)

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
- **No orphaned result — every row has a written narrative AND a graded verdict.** A `result_<NN>.json`
  (or scoreboard row) with no completed `logbook.md`/`JOURNAL.md` entry and no graded outcome is an
  **orphan**: results sitting on disk while their analysis/verdict was deferred and lost at a session
  boundary is the single most common ledger leak. Flag every orphan to be completed now.
- **The verification gate is actually wired** — `.claude/settings.json` exists and registers the
  `guard_discoveries` PreToolUse hook. An imported / hand-built / relocated tree frequently *loses* it,
  leaving the gate decorative (a real campaign once ran with no `.claude/` at all). If missing, flag loudly
  and re-run the `new-campaign` `.claude` wiring step.
- The **current-best is independently verified** — if a config is acting as current-best or a DISCOVERY
  without a CONFIRMED `verify` verdict, recommend running `verify` on it now. The hook guards *DISCOVERIES
  writes* only — it does **not** see scoreboard edits, so a current-best can be promoted unverified; a
  current-best / DISCOVERY-backed row whose **`verified` column is blank** is a hygiene failure to surface.
- **Comparability tags present** — every scoreboard row carries `metric_version` + `data_version`, and no
  "current best" ranks rows scored under *different* versions; a cross-version comparison is a silent error
  (re-score contenders under the current version first).
- **No premature "done / blocked / at-ceiling."** If the JOURNAL or DISCOVERIES declares the campaign
  finished, optimal, or blocked on new data, confirm an **adversarial attempt to beat it was actually made**
  (an orthogonal lever tried, a reasoned why-any-gain-is-non-physical argument). An unfalsified "we're done"
  is a flag to **resume**, not accept — surface it loudly and queue the orthogonal directions. A plateau with
  the guardrail still moving (generalization-limited, not capacity-limited) especially means keep going.
- **Dispute records are intact** (the JOURNAL's append-only verifier/user challenges) — never trimmed.
- PROVISIONAL findings are tracked and not silently treated as settled.
- The metric **self-test still passes** (`python scripts/metric.py --selftest`) and diagnostics were
  tee'd to logs, not left in the console.
- **The correctness suite is GREEN** — if the campaign maintains a `correctness-suite`, confirm it was
  re-run after the latest core change and passes; a result standing on a red suite is not trustworthy.
- **Every experiment has its reproducibility snapshot** (`results/snapshots/<label>/` — config + code +
  manifest); a result without one is not "saved".

### 2.5 Snapshot the session transcript (provenance)
Preserve this session's Claude Code transcript with the campaign before retention pruning removes it — the
provenance record, and primary data for any write-up. From the campaign dir, run:
```
python "${CLAUDE_PLUGIN_ROOT}/skills/campaign-status/scripts/archive_transcript.py"
```
(use the campaign's python — e.g. `py -3` on Windows). It copies this session's `.jsonl` into
`./transcripts/` with a MANIFEST — idempotent (re-run each checkpoint to refresh as the session grows),
and it never blocks the checkpoint if it errors. The transcript holds the full conversation + tool I/O, so
treat `transcripts/` as sensitive.

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
pivot, not more special-casing; a near-miss argues for gathering more evidence, not abandoning. **Prioritize
deliberately** — rank the candidate directions by *importance × tractability × cost* and commit the top few,
rather than defaulting to the next lever in line (Wieman decision 14). Write the few most promising directions
as the JOURNAL **NEXT** pointer. If plateaued and literature search is
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
