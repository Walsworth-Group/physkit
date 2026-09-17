---
name: campaign-status
description: >-
  Health check or checkpoint for a campaign or project root: where do we stand, plateaus, current
  best, records. Read-mostly.
---

# campaign-status — the operator's checkpoint

A running campaign drifts. The JOURNAL falls behind, an unverified result becomes the current best, one lever
is over-mined while an orthogonal one sits untried, and a plateau goes unnamed. This skill is the periodic step
back: it reports where the campaign stands, fixes hygiene, checks the JOURNAL is bounded and current, and
re-points the loop at the most promising orthogonal directions.

PhysKit resource links in this skill are relative to the directory containing this `SKILL.md`, not to
the campaign working directory. Resolve them to absolute paths before invoking a bundled script.

**Read-mostly.** Its only writes are: the JOURNAL — the **NEXT** pointer, `## Where we stand`, and a short
dated checkpoint note under `## Anything else` or wherever it belongs (keep the bounded document bounded) —
and snapshotting the session transcript to `transcripts/` for provenance. It never
edits the scoreboard, results, configs, or anything FROZEN.

## Two scopes — campaign checkpoint (default) vs project checkpoint
Every campaign lives inside a project, so both scopes are always available. Which one to run follows from the
directory of invocation and from how far back the user asks to step.
- **Inside a campaign** (`CLAUDE.md` present, alongside `results*/scoreboard.tsv` — a campaign scaffolded
  before the §Where things live table existed has the former but not the table, and is still a campaign)
  → the per-campaign checkpoint (the rest of this skill, the default).
- **At the project root** (`PROJECT.md` + `campaigns/`; the old layout also has `LINEAGE.md`) → the cross-campaign checkpoint in
  *Project mode* (next section). Asked for both, or ambiguous → project pass first, then descend into the
  active campaign.

## Project mode — the cross-campaign checkpoint
At a project root, step back over the whole investigation, not one loop:
1. **Read the lineage** — `PROJECT.md` §Lineage (old layout: `LINEAGE.md`), the index of every campaign
   and session. Report, per campaign: its status
   (active / superseded / archived(forked) / done), the headline result, whether its current-best is
   independently verified, and its verified findings. Flag any `active` row whose result is blank or stale.
2. **Cross-campaign FROZEN/MUTABLE consistency.** For each coupled pair, taken from each campaign's
   *Relationship to sibling campaigns* block (route to it via that campaign's own `CLAUDE.md` — siblings
   may not share a layout), confirm the declarations are mutually consistent. What campaign
   A freezes and promotes to a project-level purpose dir (`../../models/`, …; old layout:
   `../../shared/` <!-- lint-ok: intentional pre-consolidation path -->), campaign B must treat as fixed and must consume from that promoted copy — with
   its lineage promotion line — never from A's working folder. **Flag a consumed artifact that has no
   promotion line**: without the mark, promoted and working files are indistinguishable. A lever A
   froze must not be mutated by B. Surface any
   conflict or undeclared cross-campaign dependency loudly: an undeclared dependency is how a forward-model
   change invalidates a sibling's results without anyone noticing (the `fork-campaign` trigger).
3. **Promotion and provenance hygiene.** Verified system-level findings from a campaign's ledger
   `finding` cells are recorded in `PROJECT.md` §Updates from discoveries, each citing its verdict
   artifact by path — check for uncited entries (an old-layout project promotes to `DISCOVERIES.md`
   instead, hook-gated). Durable decisions live in `PROJECT.md` §Durable decisions
   (old layout: `PROJECT_ORIENTATION.md`), and **the guarded overview sections (§Mission, §Standing
   constraints) change only with a matching §Durable decisions entry** — flag a change with no trail
   (project `CLAUDE.md` rule 7). Archived(forked) campaigns
   carry a `FROZEN.md` and stay listed in the lineage.
4. **Run the project validator** for the deterministic structure and portability checks, and fold its flags in:
   run the linked
   [`../new-campaign/scripts/validate_campaign.py`](../new-campaign/scripts/validate_campaign.py) by its
   resolved absolute path against `<project_root>` (it
   auto-detects the project tree and its layout: required files, every campaign indexed in the
   lineage, no local copy
   of the project background, no absolute paths in configs).
5. **Report** across campaigns: what is active, what has plateaued, which sibling coupling needs attention, and
   the next cross-project move — spin a sibling campaign (`new-campaign`), fork an invalidated campaign
   (`fork-campaign`), or promote a verified finding. A change that invalidates a campaign's findings is a fork
   trigger, not a quiet version bump. Name it as such.

## When to invoke
- Every N experiments (the checkpoint cadence, a step of the campaign definition's Experiment Loop).
- When the driver reports the JOURNAL over its cap — a `preflight WARN: brief[worker]` line, or
  `(TRUNCATED)` in a per-spawn `brief[…]` line, means the JOURNAL is being delivered clipped at 12 KB
  with a loud marker.
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
points to is this skill; the per-unit iteration contract is in `roles/worker.md`. (The JOURNAL check
is step 3 of this skill; it no longer has a separate protocol file.)
Also read `campaign.md` §Mission (goal, the decision served, done-criteria), §Loosely-held
expectations, and §Verification. The checkpoint re-checks orientation against these, not
only against the metric. *(A pre-merge campaign keeps these in `docs/PROJECT_ORIENTATION.md` <!-- lint-ok: intentional pre-consolidation path --> and
`docs/VERIFICATION_PLAN.md` — lint-ok: names the retired layout on purpose.)*

**A campaign with no scoreboard rows yet is in setup, not stalled.** Its status IS the mechanical
check: run `python scripts/run_campaign.py --preflight --backend <active harness>` and report its output verbatim — the
authoritative list of what is unbuilt and how to fix it. Do not reconstruct setup state from the
docs; `new-campaign` hands off preflight-green, so a red preflight here means an incomplete or
imported/hand-built scaffold, and preflight is the one source that cannot be stale.

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
From `results/scoreboard.tsv` (its `finding` cells included) and `results/JOURNAL.md`:
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
  (or scoreboard row) with no completed `logbook.md` entry and no graded outcome is an
  **orphan**. "Completed" means the Analysis and NEXT slots are non-blank and every failed check is
  answered by name - never that the entry is long. The runner writes the other lines (Expected vs
  found, Levers, Verification) and the ledger row; a three-line Analysis that answers its flags is a
  complete entry, a 2,000-word one that answers none is an orphan with prose. Results sitting on disk while their analysis and verdict were deferred are lost at a session
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
  - the **`levers`** check is HARD GATE 2 as data: a `fail` names a config key that moved without being
    declared in the config's `_levers`; `unavailable` on every experiment means the campaign's configs
    never declare their levers (pre-`_levers` configs read that way, legitimately).
  - the **`self_check`** block is the worker's own record (written through `--self-check`, never by
    hand): report how many experiments have it `recorded` versus `absent`, and, for the recorded ones,
    whether every change the runner listed under `changes` was considered (`changes_unconsidered`
    empty). A campaign whose workers never record a self-check is one whose lightest label is
    `unverified` on every row; a self-check that ignores what the unit changed is decoration.
  - the **`label`** on each artifact (`unverified` · `self-checked` · `<verdict>/review` ·
    `<verdict>/re-execution`) is what every exported claim carries: tally them, and name any promoted
    row whose label is below what its preset requires.
  Do not fix a flag by editing the checks file — it is the runner's output, not a worksheet.
- **What the promotion guard denied.** `results/guard_denials.log` holds one line per denial (utc, the
  reason). Report the count and the reasons: it is the evidence for whether the hook earns its keep
  in this campaign (a guard that never denies is a deterrent or dead weight; only the log can tell),
  and a denial the worker then worked around by hand is a finding.
- **What the driver waited out.** `resource:` lines in the driver log are usage-limit deaths the
  driver relaunched instead of counting as failures; report their number and total wait.
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
  - `results/verdicts/` exists and **every ledger `finding` cell cites a verdict artifact that resolves**
    (exists, CONFIRMED, named refuter; kill findings carry a graduating tier) — except a metric-epoch
    line (`metric epoch <version> opened …`), whose evidence is its `campaign.metric_epochs` entry.
    The `finding` cells are not
    hook-gated — this audit is their enforcement, so an uncited finding is a loud flag, not a note;
  - `configs/loop.json` `verify.preset` is one of `minimal` · `light` · `moderate` · `intensive` (the
    driver's preflight line prints the table it resolves to, and every `checks_<NN>.json` stamps the
    preset it ran under — report a mid-campaign change of preset as a fact about the record, with the
    units on each side). An older file without `verify.preset` is read through its
    `campaign.verification` (`per-block`, or `promotion-only` with a recorded reason); say so;
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
  The current-best also carries its metric epoch: its `metric_version` is the campaign's current one, and
  that epoch is not rolled back.
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
  re-score contenders under the current version first. A metric-version change is a **metric epoch**
  (`campaign.md` §The ONE metric is the rule): when the ruler was wrong but the save-sets are valid and
  re-scorable, the ledger survives — a new `metric_version` with its `campaign.metric_epochs` entry,
  evidence, and standing, earlier rows keeping their version, the contenders re-scored. Only when the
  artifacts themselves are tainted (a forward-model bug, corrupted data) is it a `fork-campaign` clean
  break: archive, fresh ledger, re-verified carry-forward.
- **Metric epochs are declared, bound, and moving toward ratification.** List every
  `configs/loop.json` `campaign.metric_epochs` entry with its kind, direction, and standing. A `pending`
  epoch is owed a user decision: surface it — an `easier` one first, with its evidence — rather than
  letting it age. Confirm the current `metric_version` is declared (or is the implicit first epoch) and
  its scorer hash is bound (`results/correctness_state.json` `scorer_hash_by_version`); the runner
  refuses an undeclared scorer change, so a `METRIC EPOCH` refusal in the driver log is a finding.
  Confirm the re-baseline happened: after an epoch, the retained contenders have rows under the new
  version and the newest checks artifacts no longer report an epoch boundary
  (`checks.comparability.excluded`). The JOURNAL's `## Where we stand` carries one line per epoch.
- **No premature "done / blocked / at-ceiling."** If the JOURNAL, or a ledger `finding`, declares the campaign
  finished, optimal, or blocked on new data, confirm an adversarial attempt to beat it was made:
  an orthogonal lever tried, or a reasoned argument that any further gain is non-physical. An unfalsified
  "we're done" is a flag to resume, not to accept. Surface it loudly and queue the orthogonal directions
  (the claim audit asks the same question of a finished campaign as its search-adequacy check).
  A plateau with the guardrail still moving is generalization-limited, not capacity-limited, and means
  keep going.
- **Resume anchors reflect the latest session (stale-digest guard).** The source of truth for resuming is
  physkit's own record: the newest `handoff` (in `archive/`), the JOURNAL, and the scoreboard. Confirm the
  latest handoff covers the most recent work; a handoff that read only the campaign tree can misstate its
  own state. Any external resume digest (for example a user-maintained `_claude-archive/INDEX.md`) is
  advisory only. If its stated latest or "Active range" date lags the newest session log or JOURNAL update,
  flag it stale ("digest ends `<date>`, work ran to `<date>`") and advise regenerating it with whatever
  produced it. Never let an external digest override physkit's own handoff or journal on resume.
- **Dispute records are intact** (the logbook's `Disputes & responses` lines) — never trimmed.
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
On Claude Code, preserve this session's transcript with the campaign before retention pruning removes it. It is
the provenance record, and primary data for any write-up. From the campaign dir, run:
```
python "<resolved path to this skill>/scripts/archive_transcript.py"
```
Resolve the command from the linked [`scripts/archive_transcript.py`](scripts/archive_transcript.py).
Use the campaign's python (`py -3` on Windows). It copies this session's `.jsonl` into `./transcripts/`
with a MANIFEST. It is idempotent: re-run it each checkpoint to refresh as the session grows, and it never
blocks the checkpoint if it errors. The transcript holds the full conversation and tool I/O, so treat
`transcripts/` as sensitive. This helper is Claude-specific; on Codex, skip this substep without treating
the checkpoint as failed. A Codex transcript export is not claimed until a native source is defined.

### 3. Check the JOURNAL is bounded and current
The JOURNAL is the campaign's working memory, bounded by construction: the worker brings it up to date at
the end of every unit, editing what changed and leaving the rest. This step confirms that held.

1. **Under the cap** (~120 lines). Over it, the fix is an edit in place, not an archive pass: fold what is
   settled into one line under `## Where we stand`, drop what the ledger and the logbook already hold, and
   keep the rest. A settled fact is also its ledger row's `finding` cell, written by the worker through
   `--record <exp> --finding` and citing its verdict — recommend it where a row is missing one.
2. **Current.** The `**NEXT:**` line points at the directions the campaign is actually taking next, and
   `## Where we stand` reflects the newest accepted experiments, with confidence and the ledger id or
   verdict behind each line. A stale NEXT is the failure this step exists to catch: the next worker
   resumes from it.
3. **The full record is safe, so edit freely.** Every narrative already exists verbatim in
   `results*/logbook.md` (append-only) and every number in `results*/scoreboard.tsv`. Editing the JOURNAL
   loses nothing. Say this to yourself before editing — an agent that treats the JOURNAL as the record
   edits too timidly and the working memory stays unusable.
4. **Preserve the NEXT pointer** at the top, so the loop resumes cleanly.

**Never edit or trim the append-only files** — `results*/logbook.md`, `results*/scoreboard.tsv` and the
`results*/diagnostics/` logs hold the record permanently. Negative-result lessons and dispute records
live there for good; keep the open ones in the JOURNAL until resolved, but editing the JOURNAL
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
Put a short dated checkpoint note in the JOURNAL (best metric, trend, top issues, next directions) under
`## Anything else` or wherever it belongs, keeping the document under its cap,
and give the user a concise status: current best and margin over baseline/trivial, verified or not, trend,
the top 1–3 issues, and the next directions. Surface any hygiene flag loudly. An unverified current-best,
or a trivial reference beating the field, is worth interrupting for.

## Notes
- For a large campaign the hygiene scan and the per-lever progress summary can be fanned out to subagents
  and synthesized centrally, but keep the JOURNAL edits and the **NEXT** pointer in one place. Those
  fan-out scans suit a lighter model; keep the synthesis and the NEXT-pointer judgment on the strong one.
- This skill recommends `verify` and literature searches. It does not run experiments or promote
  results itself.
