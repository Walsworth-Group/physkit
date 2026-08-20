---
name: campaign-status
description: Periodic health-check, journal consolidation, and N-experiment checkpoint for a running autoresearch campaign — and, at a project root, a cross-campaign checkpoint. Use when the user asks for campaign status, a health check, a checkpoint, "where do we stand", project status / "how's the whole investigation", or to consolidate/trim a long journal — or automatically every N experiments per the loop. In a campaign it reads the scoreboard, journal, discoveries, and campaign.md to summarize progress against the baseline and trivial references, flag plateaus and unverified current-bests, run hygiene checks (every result saved, disputes preserved, the metric self-test passing), consolidate the journal when it grows long, and queue the next orthogonal directions as the NEXT pointer. At a PROJECT root it reads LINEAGE.md to report across campaigns and checks cross-campaign FROZEN/MUTABLE (sibling-coupling) consistency. Read-mostly — it never edits the scoreboard, results, or the frozen scorer/physics. NOT for scaffolding a campaign (new-campaign) or project (new-project), process-level loop questions — launching, "is the loop still running", "why did it halt", steering (run-campaign), forking an invalidated campaign (fork-campaign), verifying a single finding (verify), or writing the end-of-campaign report (final-report).
---

# campaign-status — the operator's checkpoint

A running campaign drifts. The journal grows, an unverified result becomes the current best, one lever is
over-mined while an orthogonal one sits untried, and a plateau goes unnamed. This skill is the periodic step
back: it reports where the campaign stands, fixes hygiene, trims the journal, and re-points the loop at the
most promising orthogonal directions.

**Read-mostly.** Its only writes are: consolidating the JOURNAL, updating the **NEXT** pointer, appending
a dated checkpoint note, and snapshotting the session transcript to `transcripts/` for provenance. It never
edits the scoreboard, results, configs, or anything FROZEN.

## Two scopes — campaign checkpoint (default) vs project checkpoint
Every campaign lives inside a project, so both scopes are always available. Which one to run follows from the
directory of invocation and from how far back the user asks to step.
- **Inside a campaign** (`CLAUDE.md` present, alongside `results*/scoreboard.tsv` — a campaign scaffolded
  before the §Where things live table existed has the former but not the table, and is still a campaign)
  → the per-campaign checkpoint (the rest of this skill, the default).
- **At the project root** (`PROJECT.md` + `LINEAGE.md` + `campaigns/`) → the cross-campaign checkpoint in
  *Project mode* (next section). Asked for both, or ambiguous → project pass first, then descend into the
  active campaign.

## Project mode — the cross-campaign checkpoint
At a project root, step back over the whole investigation, not one loop:
1. **Read `LINEAGE.md`** — the index of every campaign and session. Report, per campaign: its status
   (active / superseded / archived(forked) / done), the headline result, whether its current-best is
   independently verified, and its verified discoveries. Flag any `active` row whose result is blank or stale.
2. **Cross-campaign FROZEN/MUTABLE consistency.** For each coupled pair, taken from each campaign's
   *Relationship to sibling campaigns* block (route to it via that campaign's own `CLAUDE.md` — siblings
   may not share a layout), confirm the declarations are mutually consistent. What campaign
   A freezes and promotes to `../../shared/`, campaign B must treat as fixed and must consume from
   `../../shared/`, never from A's working folder. A lever A froze must not be mutated by B. Surface any
   conflict or undeclared cross-campaign dependency loudly: an undeclared dependency is how a forward-model
   change invalidates a sibling's results without anyone noticing (the `fork-campaign` trigger).
3. **Promotion and provenance hygiene.** Verified system-level findings are promoted from a campaign's
   journal Findings section to the project `DISCOVERIES.md`, where they survive fork-and-archive. Durable
   decisions live in the project's `PROJECT_ORIENTATION.md` §Durable decisions. Archived(forked) campaigns
   carry a `FROZEN.md` and stay listed in `LINEAGE.md`.
4. **Run the project validator** for the deterministic structure and portability checks, and fold its flags in:
   `python "${CLAUDE_PLUGIN_ROOT}/skills/new-campaign/scripts/validate_campaign.py" <project_root>` (it
   auto-detects the project tree: required files, every campaign indexed in `LINEAGE.md`, no local copy
   of the project background doc, no absolute paths in configs).
5. **Report** across campaigns: what is active, what has plateaued, which sibling coupling needs attention, and
   the next cross-project move — spin a sibling campaign (`new-campaign`), fork an invalidated campaign
   (`fork-campaign`), or promote a verified finding. A change that invalidates a campaign's findings is a fork
   trigger, not a quiet version bump. Name it as such.

## When to invoke
- Every N experiments (the checkpoint cadence, a step of the campaign definition's Experiment Loop).
- When the JOURNAL has grown long (~150+ lines) and needs consolidation.
- On demand: "where do we stand?", "is the campaign healthy?", "run a checkpoint".
- **Not only on a count.** Reflection is the campaign's error-correction step. Do not let it wait for the
  experiment counter. Reflect also after a surprising result, at a plateau, before any "we're done / at the
  ceiling / blocked" stopping decision, and after a long stretch of wall-clock with no checkpoint. Schedule
  the reflection; the immediate work otherwise crowds it out.

## Step 0 — learn the campaign
Read the campaign's `CLAUDE.md` and follow its **§Where things live** table — that campaign's own map — to
the primary metric and direction, the guardrail, the baseline/floor, the levers, the checkpoint cadence N
(a step of the Experiment Loop, not a `loop.json` knob), and whether literature search is enabled. *No
table means the campaign predates it: read `docs/charter*.md` directly.* The checkpoint procedure it
points to is this skill; the per-unit iteration contract is in `roles/worker.md`. (Journal consolidation
is step 3 of this skill; it no longer has a separate protocol file.)
Also read `campaign.md` §Mission (goal, the decision served, done-criteria), §Loosely-held
expectations, and §Verification. The checkpoint re-checks orientation against these, not
only against the metric. *(A pre-merge campaign keeps these in `docs/PROJECT_ORIENTATION.md` and
`docs/VERIFICATION_PLAN.md` — lint-ok: names the retired layout on purpose.)*

**A campaign with no scoreboard rows yet is in setup, not stalled.** Its status IS the mechanical
check: run `python scripts/run_campaign.py --preflight` and report its output verbatim — the
authoritative list of what is unbuilt and how to fix it. Do not reconstruct setup state from the
docs; the scaffold is deliberately not runnable until the physics hooks are written, and preflight
is the one source that cannot be stale.

## Procedure

### 0.5 Orientation re-check
Against `campaign.md` §Mission and §Loosely-held expectations: is the goal still the right goal? Have the
loosely-held expectations shifted on the evidence? Update them when they have; an updated expectation is
success, not drift. Are the queued units (`results/queue.json`) and the JOURNAL NEXT still serving the
goal? Has a discovery unblocked a shelved direction that should re-open? Realignment is the purpose of a
checkpoint: the metric can climb while the campaign wanders off its goal.

**Reflect against confirmation bias.** For the current best and the current direction, run the ritual
explicitly: state the expectation held before the result, argue the strongest case that it is wrong, name
the observation that would refute it and confirm that observation was run, and state the alternative
conclusion that has not been adopted (the effect is noise; a rival explanation covers it; it is an artifact).
Depth: `verify`.

### 1. Health summary
From `results/scoreboard.tsv` and `results/JOURNAL.md` (including its Findings section):
- **Current best vs references.** State the current-best primary metric and its margin over the
  baseline (exp 000) and over the trivial/degenerate references. A trivial reference beating the current
  best is a red alert. A non-physical trivial winner indicates a metric or units problem, not a target.
  Note whether the current best is independently verified (CONFIRMED) or still PROVISIONAL/unverified.
- **Trend.** Is the primary still climbing, or has it plateaued (little gain over the last ~N
  experiments)? Is the guardrail also stuck (capacity- or data-limited) or still moving
  (generalization-limited)?
- **Complexity trajectory.** Is the approach getting more complex without commensurate payoff: more
  parameters, more moving parts, more special-casing for shrinking gains? Rising complexity at a plateau
  is a pivot signal and a parsimony smell. Flag it, and check whether a simpler approach was abandoned
  too early.
- **Lever coverage.** Which lever families have been mined hard, and which are barely explored, so the
  re-plan can escalate to an orthogonal lever rather than the same knob.

### 2. Hygiene checks
Flag anything wrong; do not silently fix it.
- Every scoreboard row has a matching `results/result_<NN>.json` and its config in `configs/`. A result
  that exists only in the console is not saved.
- **No orphaned result: every row has a written narrative and a graded verdict.** A `result_<NN>.json`
  (or scoreboard row) with no completed `logbook.md`/`JOURNAL.md` entry and no graded outcome is an
  **orphan**. Results sitting on disk while their analysis and verdict were deferred are lost at a session
  boundary, and that is a recurring ledger leak. Flag every orphan to be completed now.
- **Every mechanical check is answered, not just recorded.** Read every `results/checks_<NN>.json`.
  For each experiment, three things matter and they are different:
  - a **`fail`** is a red flag the runner raised and a human or agent still owes an answer to. Confirm
    the logbook Analysis slot for that experiment actually addresses it *by name*. An unexplained flag is
    not a passed check, and "the number still looked fine" is not an explanation. Report the count of
    unanswered flags — it is the single most direct measure of whether this campaign reads its own
    instruments.
  - an **`unavailable`** is coverage this campaign never had. Its `needs` field names exactly what would
    make the check real (a `noise_floor` nobody estimated, a guardrail threshold nobody set). Report which
    checks have been unavailable on *every* experiment: that is a standing blind spot, and one that has
    been silently unavailable for forty runs is worth more attention than one that failed once.
  - a check that is **absent entirely** (no `checks_<NN>.json` beside a `result_<NN>.json`) means that
    experiment predates this artifact or bypassed the runner. Say which.
  Do not fix a flag by editing the checks file — it is the runner's output, not a worksheet.
- **The campaign's declared properties still match what it is doing.** `configs/loop.json` `campaign`
  records `prediction_mode` and `noise_model`. Both are setup-time decisions, so a change is a real
  event: compare the current values against the `prediction_mode` / `noise_model` lines stamped in the
  oldest and newest `results/snapshots/<exp>/manifest.txt`. If they differ mid-campaign, say so plainly
  and name the experiments on each side — earlier and later rows were judged under different rules, and a
  ranking across that boundary is not a ranking. Flag `prediction_mode: none` for a campaign whose answer
  has since become boundable: the mode's honest use is an answer nobody can bound, not one nobody wants
  to commit to.
- **The enforcement layer is wired.** Assert all of it, loudly. An imported, hand-built, or relocated tree
  can lose the gates, leaving the doctrine unenforced. Check each:
  - `.claude/settings.json` exists and registers the promotion-guard PreToolUse hook
    (`guard_promotion.py`; `guard_discoveries.py` in a pre-V6 tree — lint-ok: names the retired hook
    on purpose);
  - the registered guard script is present and current (the verdict-artifact version);
  - `predictions/` exists and every scoreboard row has its `predictions/<exp_name>.json` — report
    coverage as n/N (the runner's spend gate makes new gaps impossible; a gap means the tree predates the
    gate or bypassed the runner);
  - `results/verdicts/` exists and **every journal Findings entry cites a verdict artifact that resolves**
    (exists, CONFIRMED, named refuter; kill entries carry a graduating tier). The Findings section is not
    hook-gated — this audit is its enforcement, so an uncited entry is a loud flag, not a note;
  - `configs/loop.json` `campaign.verification` is `per-block`, or `promotion-only` **with a recorded
    `verification_reason`** — an unrecorded downgrade of routine verification is an unowned control;
  - `results/queue.json` `pending_verification` is not accumulating: entries there are accepted
    experiments the driver has not yet gotten verified, so a growing backlog means verification is
    failing while science continues — read the driver log's `verifier[...]` lines and flag loudly;
  - `configs/loop.json` parses, when the campaign runs supervisor mode;
  - supervised runs left their decision trace: each `--supervise` launch has a
    `results/diagnostics/supervise_*.log`, and a run with no driver log was launched outside the driver.
    `results/inbox/` holds no un-archived note older than the newest launch; an unarchived note means the
    driver never picked it up, so the user's steering went nowhere.
  Any miss: flag loudly and re-run the `new-campaign` `.claude`/wiring step.
  **Also check `results/gate_failures.log`:** any line there is a recorded fail-open/allowed-on-error
  bypass. Treat a non-empty log as a hard hygiene failure and re-verify every finding written since its
  earliest timestamp.
- **The loop gate is wired, and the loop is producing.** `.claude/settings.json` also registers
  the `loop_heartbeat` Stop hook. It guards attended sessions. Under `--supervise` the driver is the
  liveness monitor and workers end per unit, so the hook stands down for driver-spawned workers, and for
  attended sessions while `results/.driver_alive` is fresh.
  Then read `results/loop_stops.log`. A `STALL_RELEASE` line is the loud one: the loop was continued to its
  cap without producing a single new scoreboard row, so the wall-clock since the preceding entry bought
  nothing. Diagnose why (a hung run, an erroring script, re-planning instead of executing) rather than
  restarting into the same stall. `SENTINEL` / `STOP_REQUEST` lines are normal history. Cross-check any
  archived `exhausted` request in `results/stop_requests/` against the levers list: a direction declared
  finished while an untried lever existed is a finding for the review.
- **The current-best is independently verified.** If a config is acting as current-best or a DISCOVERY
  without a CONFIRMED `verify` verdict, recommend running `verify` on it now. The hook also guards the
  scoreboard `verified: CONFIRMED` / `NEW BEST` mark and `RECOMMENDED.json`: a token-marked promotion needs
  a recorded CONFIRMED verdict. A current-best asserted without those tokens can still slip past, and a
  current-best or DISCOVERY-backed row whose `verified` column is blank is a hygiene failure to surface.
- **The load-bearing upstream step is non-degenerate** (promotion check). Whatever transform feeds the
  current-best before the metric sees it — registration, pose fitting, normalization, resampling — validate
  the *transform* on the data it is applied to, not just the score it produces. A degenerate upstream step
  passes the metric and the guardrail while quietly corrupting a subset of inputs: one campaign promoted a
  best whose registration was mis-aligning some frames, and every downstream number looked healthy. Spot-check
  the transform's output against inputs it should map predictably, and flag any input class it silently drops.
- **The SHELVED pool is reviewed, not forgotten.** Units shelved after two declinations or an
  EVIDENCE-AGAINST kill sit in `results/queue.json` with their reasons. Confirm each still deserves its
  shelf; a promotion or frame change since it was shelved is a revival trigger for the planner. Confirm
  that accumulating EVIDENCE-AGAINST entries against one branch have been consolidated into a prune
  decision rather than left dangling. `kind: "operational"` entries are a different species: the driver
  shelved them because a worker failed (their `failures` records say how), not because their science was
  judged. Confirm the planner revived them or the user pruned them, and treat a pattern in their failure
  statuses (all timeouts, all spawn errors) as an environment finding, not a science one.
- **The disk runway is still real.** Compare free space on the campaign's volume against
  `configs/loop.json` `unit_cost.typical_disk_mb` and against the size `results/` has reached.
  The estimate was made before any experiment ran; measure the current figure now, as bytes-so-far ÷
  experiments-so-far. Report the remaining runway in experiments. A short runway is a finding now: apply
  the `roles/worker.md` retention plan or move the tree, rather than leaving the driver to halt on
  its disk floor mid-run. If the measured footprint is far off the scaffold-time estimate, correct
  `unit_cost.typical_disk_mb` so the floor guards the real number.
- **Comparability tags present** — every scoreboard row carries `metric_version` + `data_version`, and no
  "current best" ranks rows scored under different versions. The runner fills both from
  `configs/loop.json` `campaign`, so a blank tag now means the row was written by hand or by a runner
  older than that, and the checks artifact for that experiment will have flagged it. A cross-version comparison is a silent error:
  re-score contenders under the current version first. If a version change invalidates prior findings
  (rankings no longer hold, or an approach was scored on wrong infrastructure), as opposed to a
  rank-preserving bump, that is a `fork-campaign` clean break, not a quiet bump: archive, fresh ledger,
  re-verified carry-forward.
- **No premature "done / blocked / at-ceiling."** If the JOURNAL (its Findings included) declares the campaign
  finished, optimal, or blocked on new data, confirm an adversarial attempt to beat it was made:
  an orthogonal lever tried, or a reasoned argument that any further gain is non-physical. An unfalsified
  "we're done" is a flag to resume, not to accept. Surface it loudly and queue the orthogonal directions.
  A plateau with the guardrail still moving is generalization-limited, not capacity-limited, and means
  keep going.
- **Resume anchors reflect the latest session (stale-digest guard).** The source of truth for resuming is
  physkit's own record: the newest `handoff` (in `archive/`), the JOURNAL, and the scoreboard. Confirm the
  latest handoff covers the most recent work; a handoff that read only the campaign tree can misstate its
  own state. Any external resume digest (for example a user-maintained `_claude-archive/INDEX.md`) is
  advisory only. If its stated latest or "Active range" date lags the newest session log or JOURNAL entry,
  flag it stale ("digest ends `<date>`, work ran to `<date>`") and advise regenerating it with whatever
  produced it. Never let an external digest override physkit's own handoff or journal on resume.
- **Dispute records are intact** (the JOURNAL's append-only verifier/user challenges) — never trimmed.
- PROVISIONAL findings are tracked and not treated as settled.
- The metric self-test still passes (`python scripts/metric.py --selftest`), and diagnostics were
  tee'd to logs rather than left in the console.
- **The correctness suite is green.** Confirm `results/correctness_state.json` is `green` (≥1 active
  check) and was re-run after the latest core change. Only an affirmative green green-lights a promotion;
  `red`, `empty` (zero active checks), `error`, and `absent` all block it. An empty suite cannot
  green-light a promotion. If the campaign is promoting under a `tests/CORRECTNESS_NA.md` waiver
  (absent/empty excused), surface that explicitly: a recorded N/A is legitimate, but it must be a visible,
  deliberate decision, not an unnoticed gap.
- **Every experiment has its reproducibility snapshot** (`results/snapshots/<label>/` — config + code +
  manifest). A result without one is not saved.

### 2.5 Snapshot the session transcript (provenance)
Preserve this session's Claude Code transcript with the campaign before retention pruning removes it. It is
the provenance record, and primary data for any write-up. From the campaign dir, run:
```
python "${CLAUDE_PLUGIN_ROOT}/skills/campaign-status/scripts/archive_transcript.py"
```
Use the campaign's python (`py -3` on Windows). It copies this session's `.jsonl` into `./transcripts/`
with a MANIFEST. It is idempotent: re-run it each checkpoint to refresh as the session grows, and it never
blocks the checkpoint if it errors. The transcript holds the full conversation and tool I/O, so treat
`transcripts/` as sensitive.

### 3. Consolidate the journal (if long)
If the JOURNAL exceeds ~150 lines (or the campaign's stated trigger):

1. **The full record is safe, so trim freely.** Every entry already exists verbatim in
   `results*/logbook.md` (append-only) and every number in `results*/scoreboard.tsv`. Consolidation
   prunes the JOURNAL's *working window* and loses nothing. Say this to yourself before trimming — an
   agent that treats the JOURNAL as the record trims too timidly and the working memory stays unusable,
   which is the failure this step exists to fix.
2. **Graduate settled findings.** A finding confirmed by multiple experiments AND an independent
   verification (CONFIRMED) moves into the JOURNAL's §Findings, citing its verdict artifact.
3. **Keep the live window** — roughly the last 10–15 experiments plus every open thread, PROVISIONAL or
   QUESTIONABLE-ASSUMPTION finding, and unresolved dispute. **Drop** older entries from §Recent
   experiments rather than compressing them in place; a one-line pointer (exp id → outcome) is optional,
   since the logbook already holds them. **§Findings is never trimmed** — it is the settled record, the
   one part of the journal consolidation must not touch.
4. **Preserve the NEXT pointer** at the top, so the loop resumes cleanly.

**Never edit or trim the append-only files** — `results*/logbook.md`, `results*/scoreboard.tsv` and the
`results*/diagnostics/` logs hold the record permanently. Negative-result lessons and dispute records
live there for good; keep the open ones in the JOURNAL window until resolved, but trimming the window
never loses them.

### 4. Re-plan (diagnose before pivoting)
If the campaign is stuck or plateaued, diagnose the failure type before jumping (idea-wrong /
implementation-capped / fixed-choice-fought / near-miss) and take the smallest justified jump on the
refine↔pivot spectrum. Escalate to an orthogonal lever only once the current family is exhausted, and
escalate decisively when it is (`docs/reference/pivoting.md`). A rising-complexity plateau argues for a
pivot, not more special-casing; a near-miss argues for gathering more evidence, not abandoning. Rank the
candidate directions by importance × tractability × cost and commit the top few, rather than defaulting to
the next lever in line. Write the few most promising directions as the JOURNAL **NEXT** pointer. If
plateaued and literature search is enabled, trigger a search (per the campaign definition) and fold its top
priorities in.
When the plateau resists lever escalation (one-lever experiments across ≥2 lever families pinned at the
same floor, or the current best far from its own a-priori expectation with no lever moving the gap),
suspect an inherited cause that no lever can fix and recommend running `assumption-audit` before more
optimization runs: enumerate the values the current best inherits (calibrations, derived quantities,
classifications) with their provenance, and spend one discriminating experiment that solves for the top
suspect's value from scratch rather than confirming the incumbent.

### 5. Report
Append a short dated checkpoint note to the JOURNAL (best metric, trend, top issues, next directions),
and give the user a concise status: current best and margin over baseline/trivial, verified or not, trend,
the top 1–3 issues, and the next directions. Surface any hygiene flag loudly. An unverified current-best,
or a trivial reference beating the field, is worth interrupting for.

## Notes
- For a large campaign the hygiene scan and the per-lever progress summary can be fanned out to subagents
  and synthesized centrally, but keep the consolidation and the **NEXT** pointer edits in one place. Those
  fan-out scans suit a lighter model; keep the synthesis and the NEXT-pointer judgment on the strong one.
- This skill recommends `verify` and literature searches. It does not run experiments or promote
  results itself.
