---
name: new-campaign
description: Interview a researcher and scaffold a new autonomous-research ("autoresearch") campaign in the physical sciences. Use when the user wants to START or SET UP a new campaign, optimization loop, fitting/decoder campaign, forward-model-improvement campaign, generative-design search, ML-training campaign, or hardware-in-the-loop tuning loop — phrasings like "start a new campaign", "set up an autoresearch loop", "scaffold a campaign to optimize X", "I want to build a loop that improves Y", or "create the campaign.md / metric / scoreboard for a new project". Conducts a structured interview (goal, metric, physics, data, levers, constraints, compute, time), co-designs the FROZEN metric, determines which archetype(s) apply, then generates a complete ready-to-run campaign tree (campaign.md, role files, configs, results ledger, and light code stubs) from the kit templates and validates that nothing is left unfilled. NOT for running an existing loop, verifying a result (verify), or writing the end-of-campaign report (final-report).
---

# new-campaign — interview, then scaffold a campaign

Turn a fuzzy research goal into a running, rigorous, documented campaign. The deliverable is scaffolding
that encodes the campaign's intent so the loop-running agent cannot drift from it: a FROZEN metric, an
experiment loop, levers, guardrails, logging, verification, and reporting.

**Stance for the interview** (from `docs/PRINCIPLES.md` §1):
- **Fill from sources first; ask only when unsure. Never ask what you can check.** Before asking anything,
  harvest every answer you can definitively obtain from what is already available: the conversation so far,
  any documents or paper manuscripts the user says describe their setup, data and config files in the
  target directory, and anything you can detect directly (Step 0.5). Ask the user only about genuine gaps.
- **When a value came from a source but you are unsure it applies, ask a short question naming the
  source** — for example, "should I use the experimental parameters described in Reed et al. for this
  problem?" — rather than asking the user to supply it from scratch.
- State assumptions explicitly. Present multiple interpretations when the request is ambiguous. Push back
  when a simpler scope exists. **Co-design the metric** rather than inventing it. Narrow the purpose: a
  campaign explores one idea or one slice, not a whole project.

## When to invoke
- The user wants to start / set up / scaffold a new campaign or optimization loop.
- An existing project needs the autoresearch structure (campaign.md + metric + scoreboard) added.

Do not use this to run an already-scaffolded loop, to verify a finding (`verify`), or to write the final
report (`final-report`). To **fork a campaign whose findings a bug or correction invalidated** — a clean
break with an archived source and a re-verified carry-forward — use **`fork-campaign`**, not this skill.

- **If the idea itself is unvetted**, offer to run **`assess-idea`** first. It is advisory, covering
  feasibility and worth, and never blocks scaffolding, but a quick GO / DE-RISK-FIRST / NO-GO can save a
  campaign built on a low-ceiling problem. Off by default; propose it when the user has not already
  pressure-tested the direction.

## Inputs
- The **target directory** where the campaign should be created (ask if not given; default: the current
  working directory). Never overwrite existing files without explicit confirmation.
- Optionally, a one-line goal the user already typed. Use it to seed the interview, not to skip it.
- Optionally, a **framing artifact** from `frame-problem` (a `FRAMING.md` or a filled `INTAKE.md`). If one
  exists, compose it as described below rather than re-interviewing.

## Two ways to gather the inputs
**(a) Live interview** (default): Step 1 below, topic by topic. **(b) Intake-form mode**, for a user who
prefers editing a form to answering in the terminal: emit a pre-filled `INTAKE.md` (from
`${CLAUDE_PLUGIN_ROOT}/templates/campaign/INTAKE.md.tmpl`), filling every field you can detect or harvest
and leaving blanks where you need them. The user edits it in an editor; you read it back and ask only
about the blanks and ambiguities. Either way the result is the same campaign spec (Step 2). Offer the form
when the interview would be long, or when the user is on a slow channel.

## Compose `frame-problem` — don't re-interview the physics
`frame-problem` owns physics scoping (inventory, verification plan, decomposition) and writes a durable
**framing artifact**. If one exists, or you ran `frame-problem` for this goal in-session, read it and
**confirm rather than re-ask**: carry its physics inventory, a-priori bounds, verification plan, and step
decomposition straight into the spec, and fill only the campaign-only gaps (metric co-design,
levers/frozen, data, compute, archetype). If no framing artifact exists and the problem has real physics,
run `frame-problem` first, or fold its three outputs into the interview, rather than duplicating the work.
Within a session this is shared context; across sessions the persisted artifact carries it. Do not
interview twice.

## Step 0 — read the kit before interviewing
Read these so your questions and fills are grounded (paths are under the plugin root):
- `${CLAUDE_PLUGIN_ROOT}/docs/PRINCIPLES.md` — the doctrine every campaign inherits, sectioned by 8
  contexts. Skim it now. Once the archetype(s) are chosen (Step 1), read in depth only the contexts they
  lean on; the cheatsheet maps each archetype to its disciplines.
- `${CLAUDE_PLUGIN_ROOT}/docs/CORE.md` — the always-on spine and the general skills it routes to
  (`frame-problem`, `verify`, `simulation-design`, `correctness-suite`, `report`, …) that this campaign
  composes.
- `${CLAUDE_PLUGIN_ROOT}/templates/ARCHETYPE_CHEATSHEET.md` — the campaign archetypes (A–I) and their
  patterns.
- `${CLAUDE_PLUGIN_ROOT}/templates/PLACEHOLDERS.md` — the fill convention and canonical placeholder list.
- Skim `${CLAUDE_PLUGIN_ROOT}/templates/campaign/` — what you will fill, now including `INTAKE.md`,
  `docs/PROJECT_ORIENTATION.md`, `docs/ENGINEERING_NOTES.md`, and `docs/VERIFICATION_PLAN.md`. For
  archetype E, also read `${CLAUDE_PLUGIN_ROOT}/docs/reference/hardware-in-the-loop.md` (§0 is an example
  assembled loop).

## Step 0.1 — establish the project home (every campaign lives in one)
**Every campaign lives inside a project**: the home for one physical system investigated over many
campaigns and ad-hoc sessions, so shared data and docs live once and are referenced by relative path. This
is unconditional; there is no bare-campaign mode. A one-off costs about five near-empty files for it, since
the physics, conventions, and instrument docs move into `shared/` rather than multiplying. In exchange it
grows into a sibling campaign, a fork, or a follow-up session with no reorganization and no path rewrites.
- **An ancestor holds `PROJECT.md` + `LINEAGE.md`**: use that project. The campaign lives at
  `<project>/campaigns/<NN>_<slug>/`; pick `<NN>` as the next zero-padded index after the last
  `LINEAGE.md` row.
- **Otherwise, run `new-project` first** to create the home, then come back here. **Carry everything you
  have already gathered**: `new-project` fills its tree from the same answers, so never re-interview. When
  `new-project` invoked you, the flow is one-way: do not call back into it. Tell the user the home is being
  created; do not ask permission for it.
- **A pre-existing bare campaign** (imported, hand-built, or scaffolded before this default) is lifted into
  a project rather than left as it is: create the home around it, move it to `campaigns/01_<slug>/`, hoist
  its physics, conventions, and instrument docs into `shared/`, and append its `LINEAGE.md` row.

Consequences, unconditional, with no campaign-local variant:
1. **Physics/conventions/instrument** are referenced from `../../shared/`, never copied (design §4.1).
2. **Data** is `../../data`.
3. The campaign appends a `LINEAGE.md` row and resolves `campaign.md` §Relationship to sibling campaigns:
   keep and fill if coupled to a sibling, delete if independent. Coupling decides that one, not project
   membership.
4. The campaign `CLAUDE.md` **project-context** block is always kept.

## Step 0.5 — harvest sources and detect the environment (before asking anything)
Collect what already answers the interview, so you only ask about real gaps:
- **Read everything the user pointed to**: setup docs, paper manuscripts, prior notes, plus any data and
  config files already in the target directory. Extract concrete values (geometry, parameters, units, data
  shapes) and note each value's source, so you can cite it and ask "use the value from <source>?" if its
  applicability is uncertain. For papers, prefer the **arXiv** version and convert any PDF with a
  scientific-PDF-to-markdown tool to save tokens (see `docs/PRINCIPLES.md` §2).
- **Detect, do not ask, what you can check:** the compute (CPU cores, RAM, and GPU, e.g. by running
  `nvidia-smi`), the free disk space on the volume the campaign will live on, the available
  Python/toolchain, and the data files present and their shapes.

Carry these harvested facts into the interview.

## Step 0.6 — establish the source-authority ledger (when more than one source describes the system)
Replication and model-improvement campaigns routinely ship several descriptions of the same system that
disagree: the paper text, a figure, leftover or post-publication code, a released trained-model or data
artifact, and the user's recollection. Building the baseline on the wrong one is the most expensive setup
mistake available. A faithful reproduction of the wrong spec looks correct and only unravels hours into the
loop, and a "match the published number" gate can then drive the agent to reverse-engineer the original's
bug. Before scaffolding, build a short ledger:
- **Enumerate every source** that describes a load-bearing fact: the architecture/method, the
  training/processing recipe, normalization and units, hyperparameters, the data convention.
- **Rank them by authority.** A shipped artifact you can parse or run (trained weights, saved model,
  released data) outranks the paper text or figure, which outranks modified or leftover code, which
  outranks human recollection. The artifact is ground truth; everything else is a description of it.
- **Resolve each load-bearing fact to the highest-authority source available by reading the artifact.**
  Parse the saved model's topology, probe the data's actual statistics, run the released weights on your
  eval set, rather than inferring from a lower-authority proxy. The campaign already pins data conventions
  empirically (Step 1, topic 5); pin the method and recipe with the same rigor. Do not defer it to "exp
  000's job" when an artifact on disk settles it in seconds.
- **Tag each fact's provenance:** *PINNED* (from an authoritative artifact or empirical probe) · *REPORTED*
  (in text) · *INFERRED* (from an untrusted proxy) · *RECALLED* (from memory). Carry the tags into the spec.
- **Quarantine, do not absorb, untrusted or contradictory sources.** State explicitly that the leftover or
  modified code is not the spec, and why, so the loop agent does not re-anchor on it.
- A load-bearing fact you can only mark INFERRED or RECALLED is a **genuine gap**. Ask the user in Step 1,
  naming the source and the conflict — for example, "the figure shows no dropout but the leftover code has
  it; the saved model would settle it, do you have the trained weights?" — rather than silently baking it in.

Seed the resolved ledger into `docs/ENGINEERING_NOTES.md` (Step 3) so the provenance survives into the loop.

## Step 1 — the interview (topic by topic)
Go one topic at a time and confirm understanding before moving on. For each topic, **fill what the sources
already answer and ask only the gaps.** Use the **AskUserQuestion** tool for categorical forks, and
free-form dialogue for the metric and physics narrative. Capture every answer; you will need it to fill the
templates.

**Always ask these, even if you think you could infer them:** the internet/literature level (topic 11) and
the user's own ideas to try or avoid (topic 12). Two more are effectively always-ask because you cannot
measure them: the time budget (topic 8) and the environment (topic 9).

**Always determine, for every project, whether there is a simulation component:** a forward model,
device-performance simulation, synthetic or simulated training data, an evaluator or simulator, or a
surrogate. Most campaigns have one, so assume yes unless this is a clear exception (direct experimental
control, or training or fitting purely on real experimental data). If there is one, apply the V&V doctrine
(`docs/SIMULATION_VALIDATION.md`) and wire its gates into the core docs (Step 3).

1. **Goal & the core decision.** What is the campaign trying to achieve, and what decision does its result
   drive? Force a narrow scope. If the goal needs several coupled pieces, flag it for the multi-stage plan
   (topic 11).
2. **Archetype(s) — which apply (none, one, or several).** Decide which of the archetypes apply to this
   campaign; it may be zero, one, or several. A campaign can be both forward-model and generative-design; a
   **discovery loop (G)** can be scored through a forward model; **active design (H)** can be used to
   **discriminate models (I)**. **Inherit and merge** the metric, lever, FROZEN, and failure-mode guidance
   from every archetype you deem relevant; do not force a single best fit. State which apply and why, and
   let the user correct it. If several apply in sequence rather than at once, that is a multi-stage
   campaign (topic 11). Archetypes G (`discovery-loop`), H (`experiment-design`), and I
   (`model-selection`) each have a dedicated operational skill.
3. **The metric — build it together (the most important topic).** Co-design the single FROZEN primary: its
   name, direction (higher or lower is better), precise definition and units, the FROZEN scorer it lives
   in, hard bounds, and the **a-priori plausible range**, which encodes the predict-before-running
   discipline. Then the baseline (exp 000) value and method, any theoretical ceilings, the guardrail
   (necessary but not sufficient), and diagnostics. Pin down what feeds the metric and what is FROZEN.

   **Ask explicitly whether the baseline has already been through `verify`** — that is, the prior work's
   delivered pipeline or number this campaign will freeze and build on. If not, say so plainly in the
   campaign spec as an open risk rather than silently trusting it. A campaign optimizes against its
   baseline, so an unverified baseline is a load-bearing unknown the whole campaign inherits, not a detail.

   Capture the hard bounds in both forms while you have the answer: the prose (`{{METRIC_HARD_BOUNDS}}`,
   `{{HARD_BOUNDS}}`) and the Python literal the FROZEN scorer enforces (`{{PLAUSIBILITY_BOUNDS}}`, e.g.
   `(None, 1.0)` for a metric that cannot exceed 1, or `None` if this campaign has none). Press for what is
   true by construction: a correlation cannot exceed 1, a variance cannot be negative. Do not let the
   plausible range be entered here. That is the a-priori prediction, it belongs in `predictions/`, and
   encoding it as a hard bound turns a mathematical impossibility into a disappointing-result alarm that
   fires forever.

   **Then ask the two questions that decide what every mechanical check means.** Both are campaign-wide,
   both are written into `configs/loop.json` `campaign`, and neither has a safe default:
   - **Can this campaign honestly bound its answer in advance?** → `{{PREDICTION_MODE}}`. Use `range` if a
     defensible numeric `[low, high]` exists; that is the default and the strongest control. Use
     `direction` if the honest claim is only which way the metric should move versus a named prior
     experiment. Use `none` if neither is honest — exploratory discovery, a first-of-kind measurement, a
     search over an unknown landscape — which requires a recorded `{{PREDICTION_MODE_REASON}}`. Offer
     `direction` explicitly rather than letting the answer collapse to `none`: a fabricated range is a fake
     control, and so is a mode chosen because it asks less. Do not infer this from the archetype; ask it.
   - **Does re-running one experiment reproduce the metric exactly?** → `{{NOISE_MODEL}}`. This is a
     question about the pipeline, not the physics, and it is answered by running one thing twice rather
     than from intuition: an analytic solve with no RNG is `deterministic`; anything with sampling,
     stochastic optimization, or hardware noise is `stochastic`. Then set the resolution below which a
     change is not a change: `{{METRIC_TOLERANCE}}` for a deterministic campaign, or `{{NOISE_FLOOR}}`, the
     replicate spread, for a stochastic one. Either may be `null` if it is not yet known; the checks
     artifact then reports that check `unavailable` and names the knob, which is honest, where a guessed
     number is not. **Write `null`, never a TODO string:** both are JSON numbers, and prose there breaks
     the parse.

   Getting either wrong is silent and expensive: a stochastic campaign mislabelled deterministic promotes
   noise, and a deterministic one mislabelled stochastic is held to a spread test it can never satisfy.

   Finally, set `{{METRIC_VERSION}}` / `{{DATA_VERSION}}` (default `v1` / `v1`). The runner stamps them
   onto every scoreboard row and result, and they are bumped whenever the FROZEN scorer or the evaluation
   data changes.

   The primary, guardrail, and diagnostics, plus the experiment-type **run numerics** (e.g. epochs and best
   epoch for ML; iterations, wall-clock, and n_free_params for fits), plus a `tier` column
   (Scout/Confirmation/Extended) and the always-present `metric_version` / `data_version` comparability
   tags, become the columns of `results/scoreboard.tsv`, the campaign's quantitative ledger, which is
   separate from the narrative journal.
4. **Physics / system knowledge.** Capture, from sources wherever possible, everything needed to model the
   system:
   - **Physical objects & geometry**: dimensions, arrangement or layout, material(s), and quantities.
     *For an ASI fit from NV-magnetometry data, for example: the lattice geometry and spacing, island
     dimensions, the material, the sample orientation relative to the measured NV axis, the bias-field
     orientation, and the pixel size and field of view.*
   - **Experimental / measurement geometry**: what is measured, by what instrument, in what frame, at what
     standoff and resolution.
   - **Governing physics**: the foundational equations, simulation methods and approximations, the common
     techniques for this problem, and the system's typical behavior through the lens of this problem
     (degeneracies, symmetries, regimes — for instance that magnetization-from-field is non-unique, or how
     an ASI traverses a hysteresis loop). Source this from user information, provided literature, or, if
     enabled, a targeted search.
   - **Conventions**: units, signs, and ordering (→ `../../shared/CONVENTIONS.md`), and known artifacts or
     recurring bugs to guard against. Capture the simulation methods and approximations here too; the
     always-determine simulation check above decides whether the V&V plan in Step 3 applies.

   The governing physics, conventions, and instrument docs are the project's **shared** docs
   (`../../shared/PHYSICS.md`, `../../shared/CONVENTIONS.md`, `../../shared/INSTRUMENT.md`). Reference
   them; do not copy them. `new-project` seeded them, so fill any thin slot here, and if this campaign
   surfaced new physics or conventions, update the shared docs, which are living docs shared by every
   campaign. `CONVENTIONS.md` holds the units, signs, and frames. `INSTRUMENT.md` holds the measurement rig
   or apparatus and the sample parameters, with sources. There is no `SYSTEM.md`: it was retired and split
   into the PHYSICS target-of-study section and `INSTRUMENT.md`, so each name is unambiguous across
   subfields.

   **`PHYSICS.md`** is the governing physics plus a *target-of-study* section describing the object under
   study. Its length varies with the problem; equations go in math blocks with precise, defined notation;
   it is a living doc. It includes the **physics inventory** — every relevant effect tagged accounted-for /
   negligible-by-scale / out-of-scope / deferred / unknown, with a reason, from the `frame-problem`
   artifact — and the **predictive framework**: the mechanism or model the loop predicts with, at a
   complexity matched to the problem, plus the discriminating thought-experiments it licenses.

   Link the docs from the README via `{{PHYSICS_DOC}}` / `{{CONVENTIONS_DOC}}`, always a `../../shared/…`
   path; see `PLACEHOLDERS.md` for the per-file depth. Record anything you had to ask, so the next agent
   does not have to. If a `frame-problem` artifact exists, confirm its inventory rather than rebuilding it.
4b. **Verification — capture the application-specific checks now.** Decide how a result will be known to be
   right before the loop runs: the analytic limits, invariants, convergence, independent-method parity, and
   above all the **field-standard checks, known artifacts, and gotchas for this problem**, which is the part
   generic doctrine cannot supply. Mark verification versus validation (held-out data; calibration is not
   validation). These author **`docs/VERIFICATION_PLAN.md`**, or, for sim-heavy campaigns, the tailored
   `docs/SIMULATION_VALIDATION.md`, which `verify` reads and `correctness-suite` encodes as regression
   gates. Inherit these from the `frame-problem` verification plan if one exists.
5. **Data / inputs.** Source; fixed experimental data versus generated or simulated; splits to hold fixed;
   formats, shapes, paths. For a fixed-data campaign the dataset protocol collapses to a "verify exists,
   READ-ONLY" note.
6. **Levers vs FROZEN.** What the agent may change (the orthogonal lever families) versus what is FROZEN
   (scoring math, core physics, geometry, data) versus READ-ONLY versus MUTABLE code.
7. **Experimental / hardware constraints.** Fairness rules; for a hardware-in-the-loop campaign, the
   **hardware safety limits** as hard constraints, irreversibility, and what actions need confirmation.
8. **Compute resources, time budget, and disk budget.** Detect the available hardware rather than asking
   for it (CPU cores, RAM, GPU via `nvidia-smi`). If it is relevant to the problem, such as a GPU for ML,
   record it explicitly in the scaffolding — the README Environment section and a note in `campaign.md` —
   so future agents do not overlook available resources. Ask the user only for what you cannot measure,
   chiefly the **time budget**, per-run and overall-loop. Use this to fill the run caps
   archetype-specifically: epochs for ML, replication depth for a cheap closed-form fit, expensive or
   irreversible runs for hardware.

   **Tiered scout/confirmation caps only make sense when** the problem supports a cheaper partial
   evaluation (fewer epochs, a partial dataset) and the full evaluation is genuinely long (over 10 min,
   and especially over 60 min). Otherwise fill a single-tier budget. When tiering applies, consider three
   tiers: a very short *smoke* check (does the code run at all?), a short *scout* (is the idea promising?),
   and a longer *confirmation/validation* run. If you cannot tell whether the evaluation suits partial
   runs, ask; otherwise propose the scheme.

   **Size the disk cost per experiment too, not just the time.** A loop that fills its volume overnight
   corrupts the save-set it was mid-write on, and the failure surfaces as an unrelated-looking gate error
   hours later. Derive the estimate rather than asking for it: sum what one experiment leaves behind from
   the artifact plan (topic 5 and `roles/worker.md` §The save-set). That is the save-set (result JSON,
   figure, and the `scripts/` snapshot copy: usually a few hundred KB) plus the bulk artifacts that
   dominate it (trained weights and checkpoints, generated datasets, computed operators, raw field or trace
   arrays). Compute the bulk terms from real shapes where you can (`n_points × n_channels × 8 bytes`, a
   model's parameter count, the size of an existing example file), not from an impression. Then state the
   three numbers to the user: **MB per experiment · projected total for the planned experiment count · free
   space detected**.
   - Record the per-unit figure in `configs/loop.json` (`unit_cost.typical_disk_mb`). The driver refuses to
     launch, and halts at the loop top, below about three experiments of headroom.
   - **If the projection is a material fraction of free space (say over 25%), stop and design the retention
     plan with the user** before scaffolding: which bulk artifacts are kept, and which are dropped and
     regenerated on demand from the snapshot and seed. Fill it into `roles/worker.md`
     (`{{RETENTION_PLAN}}`, in §Retention plan). The permanent record — scoreboard row, result JSON,
     figure, snapshot, narrative, verdicts — is never part of that trade: it is small by construction, and
     dropping any of it un-saves the result. Anything not deterministically regenerable (hardware
     measurements, external services, unrecorded seeds) is likewise never droppable.
   - If experiments are small, a few MB, say so explicitly and note that no plan is needed. A stated "not a
     constraint here" is what stops the next agent from re-litigating it.

   **From the same unit-cost assessment, derive the supervisor loop knobs** (`configs/loop.json`, which the
   driver reads; PLACEHOLDERS §Loop configuration): planner cadence *k*, plateau threshold *m*
   (dual-denominated: units and wall-clock, whichever trips first), the outstanding-units cap (default
   *k*), the iteration timeout (greater than the Extended cap), the verify full-reproduction threshold, and
   the planner and worker models. Seed sensible defaults for the models; they are the user's to change,
   because model tiers shift with every release. **The cadence inverts with unit cost:** expensive units
   mean planning often, with a small *k*, since the planner is nearly free next to a day-long solve and a
   wasted solve is the real cost; cheap units mean planning in strides, with a large *k*, which keeps
   planner overhead a small fraction of loop compute. Propose the values with their reasoning; the user
   confirms them with the spec.
9. **Environment & version control.** Ask which environment the user wants, and **default to proposing a
   fresh virtual environment** (a new venv or conda env). Record the choice and setup commands in the
   README Environment / Quick-start. **Offer git, do not impose it:** recommend it for shared, large, or
   long-lived projects, but make clear that the **per-experiment snapshot is the reproducibility baseline
   either way**. A small solo campaign can skip git without losing reproducibility
   (`docs/reference/version-control.md`). Record the choice; never make git a precondition for starting.
10. **Existing code & tools.** What runnable code or data already exists to reuse, and which libraries to
    prefer (mature and free over from-scratch — `docs/PRINCIPLES.md` §5/§9).
11. **Internet / literature level (always ask; 3 options).** This sets ongoing literature use during the
    loop: **none** (no ongoing searches; remove the literature-search rule), **only when needed** (search
    when stuck, the default), or **extensive** (proactively search at setup to seed
    `PHYSICS.md`/`LITERATURE.md`, and periodically thereafter, not only when stuck). Independently, if the
    user provided any starting literature, summarize it in `LITERATURE.md` and keep the file, even when
    ongoing search is *none*. For needed and extensive, prefer arXiv and convert PDFs efficiently
    (`docs/PRINCIPLES.md` §2).
12. **User's own ideas (always ask).** Ask the user for (a) any ideas or directions they would like you to
    try, and (b) anything that should not be tried: out of scope, known dead ends, forbidden approaches.
    Record the to-try ideas as the opening JOURNAL **NEXT** items, attributed to the user, and fold the
    do-not-try items into `campaign.md` §FROZEN / out of scope. User ideas are inputs, not a ceiling; you
    remain encouraged to propose well-founded novel ideas of your own (`docs/PRINCIPLES.md` §2).
13. **Multi-stage plan — propose it proactively.** Many complex tasks are best done as several sequential
    loops rather than one: validating and improving on a simpler subcase first usually yields a more
    powerful, better-validated final result. Design a staged plan and propose it.
    Forward-model-before-decoder is one case. Others include optimizing on idealized or simpler physics
    first, to set a baseline and a solid procedure while the physics is simple, before the real system; or
    inserting a stage that produces an experimental protocol for the user to carry out, such as a
    gauss-meter measurement, whose results feed the next stage.
    *Example — permanent-magnet array from measured surface fields:* (1) optimize the arrangement with
    idealized magnets, which establishes a baseline and a solid optimizer while the physics is simple;
    (2) design a measurement protocol the user runs to characterize their real magnets' imperfections;
    (3) optimize the arrangement of the imperfect magnets, building on (1) and the data from (2).
    Each stage is a **sibling campaign**: its own `campaigns/<NN>_<slug>/` with its own `campaign.md`,
    ledger, and `LINEAGE.md` row (Step 3, *Sibling campaigns & multi-stage*). Scaffold stage 1 now; confirm
    the staging with the user and record the later stages as planned successors rather than building them
    up front.

## Step 2 — write the campaign spec and get sign-off (anti-drift checkpoint)
Before generating anything, write a concise **campaign spec**: the archetype(s) that apply, the FROZEN
metric with bounds and a-priori range, baseline, guardrail and diagnostics, levers,
FROZEN/READ-ONLY/MUTABLE, constraints, caps and whether tiering applies, the data plan, the detected
compute and chosen environment, the multi-stage plan if any, and the values you will use for the key
placeholders. Cite the source for any value pulled from a document, paper, or dataset, with its provenance
tag (PINNED / REPORTED / INFERRED / RECALLED) from the Step 0.6 ledger, and call out every load-bearing
fact still at INFERRED or RECALLED as an open question for the user to resolve before the baseline run.
Show the spec to the user and get explicit sign-off or corrections. This is the checkpoint that keeps the
build aligned with the original intent.

## Step 3 — generate the campaign tree
Copy `${CLAUDE_PLUGIN_ROOT}/templates/campaign/` into the target directory and fill it from the spec,
obeying `PLACEHOLDERS.md`. **The copy is what creates the tree: take the whole directory, not a hand-picked
subset.** The bullets below say what to fill; they are not the file list. Files the copy brings that no
bullet dwells on must still survive the fill. Four are checked by the Step 4 validator:
**`roles/worker.md` + `roles/planner.md`** (the two role files `campaign.md` delegates procedure to),
**`configs/_template.json`** (the per-experiment config template), **`scripts/frozen_core.py`** (the
FROZEN-core file list and content hash that `run_campaign.py` stamps and `guard_discoveries.py` recomputes
at promotion), and **`tests/correctness_checks.py`** (the standing suite). **`configs/RECOMMENDED.json`**
(the current-best pointer) is not validator-checked, but the promotion rule writes to it, so keep it too.
- **Fill the two role files** (`roles/worker.md`, `roles/planner.md`) from the spec like every other
  template. The loop's per-unit procedure and the planner's strategy live there, not in `campaign.md`.
- **Resolve every `{{PLACEHOLDER}}`** clearly, explicitly, and concisely, specific enough to act on
  without the interview that produced it. Where the user deferred a value, write an explicit TODO noting the deferral,
  never a silent guess.
- **Resolve every `[[OPTIONAL — … ]]` block:** delete it if it does not apply, which keeps the slim core
  slim; keep with a note a universal section that is merely not yet wired, marked `(DEFERRED)`. Include the
  hardware-safety block only for archetype E. **The ceiling blocks are one set**: ceilings appear in the
  Metric, Decision/promotion, and Before-accepting sections, so keep or delete them together. For a
  fixed-data campaign, delete `campaign.md` §Dataset / inputs entirely, leaving in its place the READ-ONLY
  note its `[[OPTIONAL]]` marker quotes.
- **Resolve every `[PROPOSED]` tag:** present each speculative discipline to the user to keep or cut; drop
  the tag on kept ones, and delete cut ones.
- **Strip the `.tmpl` suffix** on write (`campaign.md.tmpl` → `campaign.md`, and so on).
- **Always-on context — render the FROZEN doctrine spine.** This is what keeps the doctrine in context and
  the verify gate un-skippable. Generate **`CLAUDE.md`** (from `CLAUDE.md.tmpl`) in the campaign root.
  Claude Code auto-loads it every session, and it is the only reliable always-on context: a plugin's
  `docs/` are not auto-loaded, so the always-loaded spine lives here per campaign. Every line of it is
  re-injected every turn, so it carries only what the running loop acts on: no kit-design rationale, no
  scaffolding-time instructions (the fresh-session launch is Step 5's handoff message to the user), and no
  commentary on how the file was produced. Do not add a header comment; the freeze and provenance fact is
  stated once, in the spine banner below.

  **The spine does not go in `CLAUDE.md`.** It lives in **`DOCTRINE_SNAPSHOT.md`**, which is referenced and
  never auto-loaded, because 13.6 KB of reference material otherwise rides in every worker's context on
  every turn, while `CLAUDE.md` should carry only what binds a turn: the integrity core, the research
  reflexes, the hard gates, and the routing table.

  Fill `DOCTRINE_SNAPSHOT.md`'s **`{{PHYSKIT_SPINE}}`** block by rendering a campaign-tailored, FROZEN
  snapshot of `${CLAUDE_PLUGIN_ROOT}/docs/CORE.md`. Do not `@`-import CORE.md, and do not vendor a separate
  `PHYSKIT_CORE.md` and hash-check it against live: a generated campaign freezes and stamps its doctrine as
  part of its reproducible record, and does not track a moving CORE (kit-dev `CLAUDE.md` §single-source:
  *source* minimizes forks, *output* freezes-and-stamps). To render the spine:
  1. **Read** `${CLAUDE_PLUGIN_ROOT}/docs/CORE.md` in full.
  2. **Tailor for a running campaign.** Keep the meaning; cut only what a mid-campaign loop never fires.
     *Drop* the YAML frontmatter (`id`/`load`/`load_trigger`/… is kit-internal routing metadata about how
     the kit ships, not doctrine the loop acts on). *Reframe* the opening line to "running an autonomous
     research campaign" and point the goal at `campaign.md`. *Replace* the "Stage 0 — clarify the goal"
     section, whose `→ /physkit:new-campaign` routing is dead once the campaign exists, with a short
     "re-anchor each iteration — the goal is fixed in the campaign definition" paragraph that keeps the
     state-assumptions, present-interpretations, push-back, and stop-when-confused discipline. *Drop*
     exactly the three routing-table rows a running loop never uses: `assess-idea` (pre-campaign),
     `new-campaign` (already done), and `new-project`. **Keep everything else verbatim**: the whole
     Constitution, the working loop, When-stuck, Running-unattended, Honest reporting, and the nine-pillar
     list. Do not create a static tailored-CORE file in the kit or the campaign; that would be the retired
     `CLAUDE.general.md` duplicate anti-pattern. The snapshot exists only as inlined text.
  3. **Prepend the provenance banner** — the freeze stamp, which makes the snapshot legible and
     hand-edit-proof:
     ```
     > **Doctrine spine — frozen snapshot.** Derived from physkit CORE.md at scaffold time and frozen with
     > this campaign as part of its reproducible record. **Do not hand-edit this block** — to change doctrine,
     > edit kit/docs/CORE.md and re-scaffold, or (if a result is invalidated) fork-campaign.
     > generated: physkit <plugin-version> · CORE.md <core-ref> · <YYYY-MM-DD> · spine-sha256 <hash>
     ```
     Fill `<plugin-version>` from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`; `<core-ref>` from
     `git -C "${CLAUDE_PLUGIN_ROOT}" rev-parse --short HEAD` when the plugin is a git checkout, else a
     short sha256 of `CORE.md`; `<spine-sha256>` is the sha256 of the rendered spine body, excluding the
     banner. The banner followed by the tailored body together are the `{{PHYSKIT_SPINE}}` fill, and they
     go in `DOCTRINE_SNAPSHOT.md`, not `CLAUDE.md`. Never re-sync the snapshot against a newer `CORE.md`:
     it records what governed this run, and a later kit version does not retroactively govern a run that
     already happened.
- **The enforcement layer.** Generate **`.claude/settings.json`** (from its `.tmpl`) and
  **`scripts/loop_heartbeat.py`**, the Stop hook guarding attended sessions in a live campaign. That hook
  refuses an end-of-turn that is not the human's `results/STOP` or a recorded `results/stop_request.json`,
  and its block message routes toward launching the driver; it stands down for driver-spawned
  supervisor-mode workers, whose per-unit end-of-turn is earned, and for any attended session while the
  driver's `results/.driver_alive` sentinel is fresh. Also generate **`scripts/guard_discoveries.py`**, the
  PreToolUse hook that denies a `DISCOVERIES.md` write whose entry does not cite a promotable verdict
  artifact (`results/verdicts/<id>.json`, written by `verify`; CONFIRMED with a named refuter; an
  INCONCLUSIVE kill is denied; fail-closed on the promote path). Fill **`{{PYTHON_CMD}}`** with the python
  invocation detected in Step 0.5 (`py -3` on Windows, `python3` on macOS/Linux) so the hook command runs
  on this machine.

  Generate **`configs/loop.json`**: its `campaign` block from topic 3 (prediction mode, noise model, the
  resolution knob, the version tags) and its loop knobs from topic 8. Fill **`configs/_template.json`**,
  the do-not-run per-experiment config every unit is copied from, with its input paths, lever fields, and
  run and cost fields from topics 5–8. Fill **`configs/RECOMMENDED.json`**, the current-best pointer,
  mirroring exp 000 until the first promotion. Create the artifact-gate directories **`predictions/`** (the
  runner's spend gate refuses any solve without `predictions/<exp_name>.json`) and **`results/verdicts/`**.

  Seed **`results/queue.json`** with exp 000 as the first unit, then the user's topic-12 to-try ideas as
  proposed units with rationales, attributed to the user. **Every unit references one concrete runnable
  config path** — the driver validates a unit by that config's `exp_name` save-set. An idea spanning
  several solves becomes several units, or one unit whose single config encodes the pre-registered sweep;
  never a prose meta-unit with no config behind it:
  `{"next": [{"config": "...", "rationale": "...", "proposed_by": "user", "declined": []}, ...],
  "shelved": [], "accepted_units": 0, "last_accept_utc": null, "units_since_planner": 0}`.

  **Verify the layer is wired** before handoff: `.claude/settings.json` registering `guard_discoveries`,
  both gate directories present, and `loop.json` and `queue.json` parsing. A tree without them runs with no
  gates at all, and a tree assembled by hand rather than by this skill is the case where that happens;
  `campaign-status` asserts all of it. The hook guards both promotion surfaces: DISCOVERIES writes, and
  current-best writes — `configs/RECOMMENDED.json`, or a scoreboard edit introducing a `CONFIRMED` or
  `NEW BEST` token — which need a recent CONFIRMED verdict with a named refuter.
- **Code stubs.** Fill `scripts/metric.py` (the FROZEN scorer and `--selftest`) and
  `scripts/run_campaign.py` (the runner). These are intentionally light: leave the TODO hooks for the agent
  to implement the physics in-loop, but wire the names and metric so `--selftest` is the gate for exp 000.
  Leave **`scripts/frozen_core.py`**'s `CORE_FILES_DEFAULT` alone, since editing it per campaign forks the
  one authority; if this campaign's frozen physics spans more files, such as a shared simulator or a
  forward model from topic 6, declare them in `configs/frozen_core.json` instead.
  **`tests/correctness_checks.py`**, the **correctness suite**, ships as skip-stubs. From
  `docs/VERIFICATION_PLAN.md`, seed at least the analytic-limit and invariant checks for the frozen forward
  model; see the `correctness-suite` skill. It is green-gated: `run_campaign` warns on red under
  `--selftest`, and `verify` blocks promotion on it.
- **Author the orientation, verification, and engineering docs.** Fill **`docs/PROJECT_ORIENTATION.md`**:
  the goal, the decision it drives, the loosely-held expectations, and the numbered goal-linked task
  hierarchy, graduating the `frame-problem` decomposition. When the field has them, also fill the optional
  "Where this sits in the field" block: the gap or novelty, adjacent work, the threshold ladder and named
  precedents for the key quantity, and what not to claim. Ask the user or draw on the topic-4 literature;
  skip the block if the quantity has no canonical thresholds, and never invent them. Fill
  **`docs/VERIFICATION_PLAN.md`** with the application-specific checks from topic 4b, the gate `verify` and
  `correctness-suite` consume. Seed **`docs/ENGINEERING_NOTES.md`** with the Step 0.6 source-authority
  ledger: one ED per load-bearing fact resolved from a source, giving its value, the authoritative artifact
  it is PINNED to, the provenance tag, and the lower-authority sources quarantined and why. An empty header
  is correct only if there was a single source. Put the user's ideas to try as the opening
  `PROJECT_ORIENTATION` tasks and JOURNAL NEXT items.
- **Reference docs (see topic 4).** Physics, conventions, and instrument are the project's shared docs, so
  the campaign tree carries no copy of them. Fill `{{PHYSICS_DOC}}` / `{{CONVENTIONS_DOC}}` with the
  `../../shared/…` path at the correct relative depth per file (see PLACEHOLDERS.md), and update the shared
  docs in place if this campaign added physics or conventions. Record the detected compute and the chosen
  environment and setup commands in the README (Environment / Quick-start), note available compute in
  `campaign.md` §Caps, and register any new docs in the README.
- **Project wiring — always, from Step 0.1:**
  1. Reference the canonical data as **`../../data`**; never copy it into the campaign.
  2. **Append a row to `../../LINEAGE.md`** (Campaigns table): index `<NN>`, campaign name, date, the
     `approach` tag, the FROZEN primary metric, what changed from the predecessor (or "— (first)"),
     headline result (leave `pending` until exp 000), verified discoveries (none yet), `@KB-key` (—), and
     status `active`.
  3. Resolve `campaign.md` §**Relationship to sibling campaigns**: keep it and fill
     `{{SIBLING_FROZEN_MUTABLE}}` and `{{CONSUMED_ARTIFACTS}}` if this campaign is coupled to a sibling
     (what it FREEZES versus MUTATES; which `../../shared/<artifact>` it consumes); delete it if
     independent. Coupling decides this block, not project membership, so the first campaign in a fresh
     project deletes it.
  4. **Keep** the campaign `CLAUDE.md` project-context block.
  5. A verified finding that is a fact about the **system**, rather than a config that scored well, is
     later promoted from `results/DISCOVERIES.md` to the project `../../DISCOVERIES.md`, which survives
     fork-and-archive. Note this in the handoff so the loop agent knows the promotion path.
- **Literature (per the topic-11 level).** The ongoing-search rule and the `LITERATURE.md` file are decided
  separately:
  - *Ongoing-search rule in `roles/planner.md` §Literature search rule:* for **none**, resolve the
    `[[OPTIONAL — literature search enabled]]` block as delete; for **only-when-needed** and **extensive**,
    keep it and fill `{{LITERATURE_LEVEL}}` with the chosen intensity (search-when-stuck versus
    proactive-and-periodic).
  - *`LITERATURE.md` itself:* keep it and seed it with summaries of any literature the user provided
    (prefer arXiv; convert PDFs; cache), even when ongoing search is *none*. Delete the file only when
    ongoing search is *none* and the user provided no starting literature. When kept under *none*, treat it
    as a static reference: keep the summaries and references, and drop the roadmap and next-search sections.
- **Simulation validation (conditional on topic 4).** If the campaign has a simulation aspect, author
  `docs/SIMULATION_VALIDATION.md` for it, a tailored V&V&UQ plan from
  `${CLAUDE_PLUGIN_ROOT}/docs/SIMULATION_VALIDATION.md`, and wire its gates into the core docs: a
  **verify-before-validate gate**, under which the simulator must pass code and solution verification
  before any simulator-based result is trusted, plus the **sim-to-experiment guardrail** in `campaign.md`
  §Mind the simulation-to-experiment gap. Record the simulator's assumptions, domain of validity, and V&V
  status in `../../shared/PHYSICS.md`, and keep *calibration is not validation* by holding out independent
  validation data. Register it in the README.
- **Seed the user's directions.** Put the user's ideas to try (topic 12) as the opening JOURNAL **NEXT**
  items, attributed to the user, and fold the do-not-try items into `campaign.md`'s FROZEN and out-of-scope
  list.
- **Sibling campaigns & multi-stage (project model, §5).** A second track, approach, or stage is always a
  **sibling campaign**: its own `campaigns/<NN>_<slug>/` with its own `campaign.md` and ledger, coupled via
  `campaign.md` §Relationship to sibling campaigns and shared promoted artifacts (`../../shared/`).
  Scaffold each by re-running this skill in the project, with a new `LINEAGE.md` row per sibling. The
  retired `_<NAME>`-suffix-in-one-tree form is not an option: that was the bare-campaign fallback, and
  every campaign now has a project home.
- Seed `results/scoreboard.tsv` with its header. Leave `results/logbook.md` (append-only full record),
  `results/JOURNAL.md` (the working window), and `results/DISCOVERIES.md` with their intros and the first
  **NEXT** pointer, queueing exp 000. The logbook, scoreboard, and `diagnostics/` logs are append-only and
  never read in full, which is what keeps the record complete without bloating the loop's context. If the
  user wants hard separation, the logbook and diagnostics can be redirected to a path outside the campaign
  tree; the default is in-tree for reproducibility.

## Step 4 — validate (deterministic gate)
Run the bundled validator on the generated tree and fix anything it flags:
```
python "${CLAUDE_PLUGIN_ROOT}/skills/new-campaign/scripts/validate_campaign.py" <target_dir>
```
It fails if any literal `{{…}}`, dangling `[[OPTIONAL`, or stray `[PROPOSED]` remains, or if a required
file is missing. A generated campaign with an unresolved token is not done.

## Step 5 — hand off (and start a fresh session)
Tell the user what was created, and **name the destination up front: the loop runs in supervisor mode,
launched and watched through the `run-campaign` skill.** The fresh session's job is setup, then
`/physkit:run-campaign`, never executing the loop by hand.

The **critical handoff rule: do not start the loop in this setup session.** The campaign's `CLAUDE.md`
(always-on doctrine and hard gates) and the enforcement hooks only take effect in a session that starts in
the campaign folder. This setup session was already open when they were written, so it has loaded neither.
Instruct the user to launch a fresh session from the campaign directory:
```
cd "<absolute path to campaign dir>"
claude --dangerously-skip-permissions
```
**Give the absolute path, never one relative to this setup session's cwd.** The fresh session's shell has
no memory of where this session was running: a relative or partial path that resolved correctly here will
point at the wrong place, or nowhere, in the new terminal. Resolve the campaign dir to its full path before
handing over the command.
*(add `--plugin-dir "<KIT_DIR>"` if running the kit per-session rather than installed).*

In that fresh session, the sequence is:
1. **Pre-loop setup, not the loop:** implement `scripts/metric.py` and `save_figure()` and make
   `--selftest` pass; write `predictions/exp000_baseline.json`, which the spend gate requires and whose
   expected floor is in `campaign.md` §Baseline gate; run experiment 000, the baseline gate. Confirm with
   `/context` that `CLAUDE.md` is loaded.
2. **Then invoke `/physkit:run-campaign`.** That session becomes the loop's cockpit: it runs the driver's
   preflight and translates any failure into its fix, launches `--supervise` in the background, narrates
   progress from the driver log, and relays the user's steering into `results/inbox/`. Fallback, if no
   skill is available: hand over `<python> scripts/run_campaign.py --preflight`, then `--supervise`,
   writing out the actual python command detected in Step 0.5, e.g. `py -3`, and never the literal
   placeholder.

The driver runs its preflight (agent CLI, loop and queue config, metric self-test; each failure names its
fix, and `--preflight` runs it standalone), pops units from the seeded `results/queue.json`, spawns a fresh
worker agent per unit (the frozen spine and `campaign.md` auto-load in each), and enforces the artifact
gates. Failures split by kind. An **operational** failure — a worker that dies, hangs, or leaves its unit
unvalidated — is retried, then shelved with the failure recorded, and the loop continues. The driver
hard-halts only on **integrity** conditions (`results/ESCALATE.md`, a corrupt or post-planner-empty queue)
or **systemic** failure (several units failing in a row). Loop knobs live in `configs/loop.json`, which is
user-owned; `roles/worker.md` §How the loop runs explains the contract.

**Attended work means watching and steering through the cockpit, not executing by hand.** A by-hand
`--config` run is for debugging a single experiment; it is not a mode for running the loop. The
interactive-executor pattern is retired, because it produced unbounded context, docs that were never
re-read, premature stops, and verification decay — the failure record that motivated the driver.
- The campaign lives at `<project>/campaigns/<NN>_<slug>/` and its opening `../../LINEAGE.md` row is
  `status: active`. Hand over the absolute path to the campaign dir, not the project root. Remind the loop
  agent that shared data and docs are `../../data` and `../../shared/`, referenced and never copied, with
  the ancestor `../../CLAUDE.md` carrying the project rules; that ad-hoc follow-up work belongs in
  `../../sessions/<date>_<slug>/` rather than in this tree; and that a verified system-level finding is
  later promoted from `results/DISCOVERIES.md` to the project `../../DISCOVERIES.md`.
- **If the loop runs agents beyond the main session** — Task subagents, or SDK-spawned generation and
  critic roles — those contexts inherit nothing from `CLAUDE.md`; their prompts replace the doctrine stack.
  Before the first real experiment, run the prompt-surface audit
  (`docs/reference/prompt-surface-audit.md`): capture each role's context as rendered, including
  dynamically generated blocks, and verify every relied-upon rule is physically present. Re-run it after
  any prompt change.

## Notes
- This skill scaffolds; it does not run the loop. After hand-off, the loop-running agent executes
  `campaign.md` and its role file.
- Never overwrite existing files without confirmation. If the target already holds a campaign, add a
  **sibling campaign** in the project (a new `campaigns/<NN>_<slug>/` and `LINEAGE.md` row), or stop and
  ask.
- **Imported, relocated, or hand-built trees silently lose the enforcement layer.** A tree not generated by
  this skill — copied in, assembled from frozen inputs, or moved — usually lacks `.claude/settings.json`,
  `scripts/guard_discoveries.py`, `scripts/loop_heartbeat.py`, the gate directories (`predictions/`,
  `results/verdicts/`), `configs/loop.json`, and `results/queue.json`. The promotion gate, the loop gate,
  and the driver are then all absent, and the doctrine prose in `CLAUDE.md` is decorative. Re-run the Step
  3 enforcement-layer wiring for any such tree, and lift it into a project home per Step 0.1;
  `campaign-status` asserts the whole set.
- The metric and core physics you scaffold are FROZEN by construction. Say so to the user, and make the
  `--selftest` real before exp 000 so a convention or sign slip cannot corrupt the whole campaign.
