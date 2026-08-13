# Placeholder Convention — spec for the `new-campaign` setup skill

How the `*.tmpl` files under `templates/campaign/` are filled into a generated campaign. This file is
**guidance for the setup skill**, not copied into a campaign. The canonical placeholder list at the
bottom is authoritative: every `{{NAME}}` appearing in any template MUST be listed here, and every
name listed here MUST be used by at least one template (the Bucket-1 lint checks both directions).

## Syntax
- **`{{UPPER_SNAKE_CASE}}`** — a substitution the setup skill fills. Names that are plural or end in
  `_LIST` / `_ROWS` / `_TABLE` / `_FIELDS` / `_NOTES` may expand to **multi-line** content (a bulleted
  list, table rows, JSON fields). Singular names are short inline phrases.
- **`[[OPTIONAL — <condition>: … ]]`** — a block included only if `<condition>` holds. May span
  multiple lines (the closing `]]` sits on its own line). See the delete-vs-keep rule below.
- **`[PROPOSED]`** — an inline tag on a speculative/optional discipline. The setup skill presents these
  to the user to **keep or cut**; surviving ones lose the tag, cut ones are deleted.
- **`.tmpl` suffix** — marks a file that contains placeholders. Stripped on generation
  (`charter.md.tmpl` → `docs/charter.md`).
- **`<NN>`, `<slug>`, `<label>`, `<G>`** in **prose/example** text are literal illustrative
  placeholders (how filenames look at runtime), NOT substitutions — leave them as-is. Only `{{...}}` is
  substituted. (`{{NN}}` and `{{SLUG}}` *are* substitutions — they appear in the config templates'
  `exp_name`.)

## Delete-vs-keep rule (no half-resolved files)
- **`[[OPTIONAL]]` blocks and OPTIONAL-marked files → DELETE when they don't apply.** A ceilings block
  for a metric with no ceiling, or `dataset.md` for a fixed-dataset campaign, is removed entirely. This
  keeps the slim core slim.
- **Universal-but-momentarily-empty sections → KEEP WITH A NOTE, never delete.** A planned-but-unwired
  guardrail stays in the Decision Metrics section marked `(DEFERRED — wired after <milestone>)`.
- **Rule of thumb:** part of the universal discipline (metric integrity, verification, FROZEN rules,
  logging) → keep-with-note; a domain feature simply not present → delete the optional block.
- **Hard requirement:** a generated file containing any literal `{{...}}`, any unresolved `[[OPTIONAL`,
  or any leftover `[PROPOSED]` the user didn't rule on is an **ERROR**. The setup skill must scan every
  generated file and fail loudly if one remains.

## Filling guidance
- Pick the closest archetype from `ARCHETYPE_CHEATSHEET.md` first; it tells you the typical metric,
  levers, FROZEN set, and failure modes to slot in.
- Fill from the **interview** (goal, metric, physics, data, constraints, compute, time). Where the user
  defers (e.g. a parameter they'll fit later), write the placeholder's content as an explicit TODO with
  the deferral noted, not a silent guess.
- Keep fills clear, explicit, and concise — specific enough to act on without the interview that
  produced them.

---

## Canonical placeholder list

### Identity & framing
| Placeholder | Meaning |
|---|---|
| `{{CAMPAIGN_TITLE}}` | Short campaign name (headers, e.g. "NV Residual Minimization"). |
| `{{CAMPAIGN_KIND}}` | One-word/phrase kind (e.g. "residual-minimization", "forward-model"). |
| `{{PROJECT_TITLE}}` | Project title for the README H1. |
| `{{MISSION_STATEMENT}}` | One sentence: what the campaign optimizes and why. |
| `{{ONE_PARAGRAPH_PROBLEM_STATEMENT}}` | README paragraph framing the problem. |
| `{{APPROACH_SUMMARY}}` | One-line summary of the method/approach. |
| `{{DATE}}` | Generation date (literature "last updated"). |
| `{{DEFAULT_SEED}}` | Default RNG seed in config templates. |

### Metric — definition & bounds
| Placeholder | Meaning |
|---|---|
| `{{PRIMARY_METRIC}}` | Name of the frozen primary metric (e.g. `EXP_RESIDUAL_R2`). |
| `{{PRIMARY_DIRECTION}}` | "higher" or "lower". |
| `{{METRIC_DEFINITION}}` | The precise definition (in words + units). |
| `{{FROZEN_SCORER_PATH}}` | Path to the FROZEN file that computes the metric. |
| `{{METRIC_HARD_BOUNDS}}` | Mathematical bounds (e.g. "≤ 1 by construction; ∈ [−∞, 1]"). |
| `{{METRIC_PLAUSIBLE_RANGE}}` | The a-priori plausible range, with basis. |
| `{{BASELINE_DESCRIPTION}}` | What exp 000 is and its expected value. |
| `{{BASELINE_VALUE}}` | The baseline metric value (the floor). |
| `{{BASELINE_COMMAND}}` | Command to run exp 000. |
| `{{CEILING_LIST}}` | (optional) Inline list of theoretical ceilings. |
| `{{CEILING_DEFINITIONS}}` | (optional) Fuller ceiling definitions for the metric protocol. |
| `{{METRIC_INPUTS}}` | What feeds the metric (crop, preprocessing, normalization, …). |
| `{{COMPARABILITY_AXES}}` | What must match exp 000 for an apples-to-apples comparison. |
| `{{EVAL_TARGET}}` | The data/target the metric is evaluated on. |
| `{{METRIC_VALIDATION_GATE}}` | The do-once check that the scorer is wired correctly. |

### Metrics roster & reporting
| Placeholder | Meaning |
|---|---|
| `{{GUARDRAIL_METRIC}}` | The secondary guardrail metric name. |
| `{{GUARDRAIL_SUMMARY}}` | One-line summary of the guardrail (Mission line). |
| `{{GUARDRAIL_USE}}` | What the guardrail is used for (checkpoint selection, overfit watch). |
| `{{GUARDRAIL_CHECK}}` | The concrete guardrail check run at loop step 5. |
| `{{DIAGNOSTIC_METRICS}}` | Co-tracked diagnostic quantities. |
| `{{SECONDARY_METRICS}}` | Metrics evaluated alongside the primary at step 4. |
| `{{SUBGROUP_SPLIT}}` | (optional) The hard/easy subgroup split to always report. |
| `{{CHEAP_SUBGROUP}}` | The near-trivial subgroup whose improvement is "cheap". |
| `{{PRIMARY_REPORT_RULE}}` | How to report the primary (e.g. always with the subgroup split). |
| `{{GENERALIZATION_AXIS}}` | The axis a real win must generalize across (frames/conditions/…). |

### Loop & run
| Placeholder | Meaning |
|---|---|
| `{{RUN_STEP_NAME}}` | Loop step-3 verb (e.g. "RUN", "TRAIN", "SOLVE"). |
| `{{RUN_COMMAND}}` | The command that runs one experiment. |
| `{{RUN_NOUN}}` | Noun for the caps table title (e.g. "Run", "Training"). |
| `{{IMPLEMENT_VERB}}` | What "IMPLEMENT" means here, as an action phrase only (e.g. "modify the decoder/loss"). The config path is already in the boilerplate — do NOT repeat it. |
| `{{SANITY_STEP}}` | Name of the loop sanity/guardrail step (e.g. "SANITY"). |
| `{{EVAL_WRITER}}` | The script/function that writes the evaluation output. |
| `{{VALIDATION_CHAIN}}` | The pipeline chain exp 000 validates end-to-end. |
| `{{ARTIFACT_LIST}}` | What artifacts each run saves (step 8 summary). |
| `{{CHECKPOINT_EVERY}}` | Checkpoint cadence N. |
| `{{COST_UNIT}}` | Unit of run cost (epochs, iterations, seconds, solves). |
| `{{COST_NOTE}}` | (optional) Note on why experiments are cheap/fast. |
| `{{DISK_PER_EXP}}` | Human-readable disk footprint of ONE experiment (e.g. "1.2 MB" / "~4 GB (checkpoints dominate)"). Derived in the interview from the artifact plan; the machine-readable twin is `{{UNIT_COST_DISK_MB}}`. |
| `{{RETENTION_PLAN}}` | The keep-vs-regenerate plan for BULK artifacts when they are large (which are kept, which are regenerated on demand + the command, any pruning cadence). When experiments are small, state that no plan is needed and why — never leave it blank. The permanent record (save-set, snapshot, narrative, verdicts) is never in scope. |

### Caps
| Placeholder | Meaning |
|---|---|
| `{{SCOUT_TARGET}}` / `{{SCOUT_MAX}}` | Scout-tier target & hard-max cost. |
| `{{CONF_TARGET}}` / `{{CONF_MAX}}` | Confirmation-tier target & hard-max. |
| `{{CONF_CADENCE}}` | How often to run a confirmation (every N exps). |
| `{{EXT_TARGET}}` / `{{EXT_MAX}}` | Extended-tier target & hard-max. |

### Decision, verification & rigor
| Placeholder | Meaning |
|---|---|
| `{{PROMOTION_CONFIRM_RULE}}` | Extra confirmation needed to promote (e.g. "confirm with a 2nd seed"). |
| `{{SPREAD_NOUN}}` | Name for the replicate spread (e.g. "seed/param", "seed-to-seed"). |
| `{{VERIFY_SKILL}}` | The verify skill to invoke (e.g. `/physkit:verify`). |
| `{{PHYSKIT_SPINE}}` | **Rendered by `new-campaign` Step 3 — not a simple fill.** The campaign-tailored, FROZEN snapshot of `docs/CORE.md` (provenance banner + tailored body) inlined into `CLAUDE.md`; the campaign's reproducible doctrine record. NOT `@`-imported and NOT vendored as a separate hash-checked file. See Step 3 for the tailoring + stamp procedure. |
| `{{VERIFY_EXTRA_CHECKS}}` | Archetype-specific extra checks the verifier must do, as a clause FRAGMENT appended to "checks for metric contamination" (e.g. ", recomputes the ceilings, and checks the ceiling-vs-gap trap"). Don't repeat "metric contamination". |
| `{{SYSTEMATIC_AXIS_NOTE}}` | A standalone sentence on the dominant systematic-error axis for this campaign. It follows "…find and fix the cause)." — don't repeat that phrase. |
| `{{OVERFIT_MODE}}` | The campaign's characteristic overfit mode (e.g. "sim-to-real / val overfit"). |
| `{{DECISION_EXAMPLES}}` | Example decisions that are "hypotheses, not givens". |
| `{{MODEL_NOUNS}}` | The model components parsimony applies to (forward, decoder, …). |
| `{{UNITS_EXAMPLE_LINE}}` | One concrete units/scale example sentence. |
| `{{APRIORI_BOUND_NOTES}}` | How to compute the a-priori bound for this metric. |
| `{{PHYSICAL_BOUNDS_NOTES}}` | The physical bounds/scales of key quantities. |
| `{{SIM_GAP_NOTE}}` | The sim-to-experiment gap specific to this campaign. |
| `{{TIEBREAK_COSTS}}` | The costs used to break ties between tied options. |
| `{{UNIT}}` | The per-unit over which distributions are compared (frame, sample, …). |

### Levers, FROZEN & code
| Placeholder | Meaning |
|---|---|
| `{{LEVER_SUMMARY}}` | One-line summary of the levers (Mission line). |
| `{{LEVERS_LIST}}` | The full categorized list of levers. |
| `{{LEVER_CATEGORIES}}` | The orthogonal lever families, named. |
| `{{LEVER_COLUMNS}}` | The lever columns in the scoreboard (tab-separated). |
| `{{FROZEN_LIST}}` | What is FROZEN besides the scorer. |
| `{{READONLY_LIST}}` | Read-only files (use, don't edit). |
| `{{MUTABLE_LIST}}` | Mutable files. |
| `{{STRUCTURAL_LEVERS}}` | The biggest structural levers to escalate to when stuck. |
| `{{STUCK_N}}` | How many flat experiments before "stuck". |
| `{{REANCHOR_DOCS}}` | Docs to re-read when stuck / at a checkpoint. |
| `{{DATA_CHOICE_WARNING}}` | (optional) Warning that a data/distribution choice must be held fixed. |
| `{{DATA_DISTRIBUTION}}` | (optional) The distribution that changes if the data choice moves. |
| `{{CODE_SNAPSHOT_RULE}}` | (optional) The code-snapshot rule when code under test is mutable. |
| `{{HARDWARE_LIMITS}}` | (optional, hardware-in-the-loop only) The specific hardware safety limits / safe ranges that are hard constraints. |
| `{{LITERATURE_LEVEL}}` | (optional, when literature search is enabled) The intensity — "only when needed" (search when stuck) or "extensive" (proactive + periodic). |

### Logging & scoreboard
| Placeholder | Meaning |
|---|---|
| `{{SCOREBOARD_COLUMN_LIST}}` | The full scoreboard schema string (in charter.md). |
| `{{PRIMARY_METRIC_COL}}` | The scoreboard column holding the primary metric. |
| `{{PRIMARY_SPREAD_COL}}` | The column holding the replicate spread. |
| `{{GUARDRAIL_COL}}` | The column holding the guardrail value. |
| `{{DIAGNOSTIC_COLUMNS}}` | Supplemental metric / sanity-score columns (tab-separated). |
| `{{RUN_COLUMNS}}` | Experiment-type run numerics (tab-separated): epochs trained + best epoch (ML), iterations / wall-clock / n_free_params (fits), seed / n_reps. May be empty — if so, remove it and its adjacent tab. |

### Protocol stubs
| Placeholder | Meaning |
|---|---|
| `{{BASELINE_METHODS}}` | The baseline method(s) for exp 000. |
| `{{GATE_CRITERIA}}` | The pass/fail criteria for the baseline gate. |
| `{{FLOOR_RECORD_RULE}}` | How the floor is recorded. |
| `{{SCOREBOARD_REVIEW_SORTS}}` | How to sort the scoreboard at a checkpoint. |
| `{{HYGIENE_CHECKS}}` | The checkpoint hygiene checklist. |
| `{{REPLAN_HORIZON}}` | How many directions to queue at a checkpoint. |
| `{{CONSOLIDATE_TRIGGER}}` | When to consolidate the journal. |
| `{{KEEP_WINDOW}}` | What to keep live when consolidating. |
| `{{PER_EXP_ARTIFACTS}}` | The always-saved per-experiment artifacts. |
| `{{FIGURE_SPEC}}` | The standard per-experiment figure, panel by panel. |
| `{{PROMOTED_BEST_ARTIFACTS}}` | The heavier artifacts saved on promotion. |
| `{{ARTIFACT_COMMAND}}` | The command/flag that saves the full artifact set. |
| `{{DATA_SOURCE}}` | Where the inputs come from. |
| `{{GENERATE_COMMAND}}` | Command to generate/fetch the data. |
| `{{SPLIT_TABLE}}` | The fixed data splits. |
| `{{LOAD_PIPELINE}}` | How a config loads the data. |
| `{{DISTRIBUTION_NOTE}}` | Which knobs are data-choices vs method-levers. |
| `{{EXTRA_PROTOCOL_ROWS}}` | Extra rows for the Protocol Index (campaign-specific protocols). |

### Conventions doc
| Placeholder | Meaning |
|---|---|
| `{{UNITS_TABLE}}` | Quantity · symbol · unit · plausible range table. |
| `{{SIGN_CONVENTIONS}}` | Sign/direction conventions. |
| `{{COORDINATE_CONVENTIONS}}` | Coordinate systems & array/index ordering. |
| `{{DATA_LAYOUT}}` | Shapes/dtypes/axes of the main arrays. |
| `{{KNOWN_GOTCHAS}}` | The recurring bug(s) for this domain + how to detect them. |

### README, config & literature
| Placeholder | Meaning |
|---|---|
| `{{STAGE_TABLE_ROWS}}` | README status-table rows. |
| `{{REPO_MAP}}` | README repository map. |
| `{{ENVIRONMENT_NOTES}}` | Environment/dependency notes. |
| `{{PYTHON_CMD}}` | The python invocation for hook commands, from Step 0.5 detection (e.g. `py -3` on Windows, `python3` on macOS/Linux). Used in `.claude/settings.json`. |
| `{{QUICKSTART_COMMANDS}}` | Quick-start commands. |
| `{{EXTRA_BACKGROUND_DOC_LINKS}}` | Extra links to setup-authored reference docs. |
| `{{NN}}` / `{{SLUG}}` | Experiment number & slug in config `exp_name`. |
| `{{INPUT_PATH_FIELDS}}` | JSON fields for input paths in the config template. |
| `{{METHOD_FIELDS}}` | JSON fields for the method/levers in the config template. |
| `{{RUN_FIELDS}}` | JSON fields for run/cost controls in the config template. |
| `{{FIRST_NEXT_STEP}}` | The initial JOURNAL "NEXT" pointer. |
| `{{SEED_IDEA}}` / `{{SEED_SOURCE}}` / `{{SEED_IMPACT}}` / `{{SEED_EFFORT}}` | First literature roadmap row. |
| `{{SEED_CITATION}}` | A seed citation in the literature techniques section. |
| `{{TOPIC}}` | A literature topic heading. |
| `{{NEXT_SEQUENCE}}` | The recommended next-experiment sequence. |

### Project & shared-doc references
Every campaign lives inside a project, so these always resolve to the project's `shared/` docs — **never a
local copy** (design §4.1; the validator rejects one). Each value is a **relative path from the file that
contains it**, so the depth differs by file — fill each occurrence with the path that actually resolves (the
validator checks intra-tree doc links resolve).

| Placeholder | Meaning | Value (by file location) |
|---|---|---|
| `{{PHYSICS_DOC}}` | Path to the governing-physics doc. | campaign-root (charter/README/INTAKE): `../../shared/PHYSICS.md` · `results/` (INDEX/DISCOVERIES): `../../../shared/PHYSICS.md` |
| `{{CONVENTIONS_DOC}}` | Path to the conventions doc. | campaign-root: `../../shared/CONVENTIONS.md` · `results/`: `../../../shared/CONVENTIONS.md` |
| `{{SIBLING_FROZEN_MUTABLE}}` | (coupled sibling campaigns only — else DELETE the block) What this campaign FREEZES that a sibling treats as MUTABLE, and vice versa. | — |
| `{{CONSUMED_ARTIFACTS}}` | (coupled sibling campaigns only) The promoted `../../shared/<artifact>_<ver>/` artifacts this campaign READS (never a sibling's working folder). | — |

### Project-tree placeholders (`templates/project/`)
Filled by `new-project` when it creates the home. A one-off project fills these from the campaign interview —
they are not a second interview.

| Placeholder | Meaning |
|---|---|
| `{{PROJECT_TITLE}}` | The project/investigation name (the `PROJECT.md`, `LINEAGE.md`, and project `CLAUDE.md` H1). |
| `{{PHYSICAL_SYSTEM}}` | One line naming the physical system under investigation. |
| `{{GOAL_STATEMENT}}` / `{{DECISION_SERVED}}` / `{{DONE_CRITERIA}}` | The end goal, the decision it serves, and what "done" looks like — the same answers that fill the campaign's `PROJECT_ORIENTATION.md`. |
| `{{SYSTEM_INVARIANTS}}` | Project-wide invariants every campaign inherits (drawn from the topic-4 physics interview). |
| `{{DATA_LOCATION}}` / `{{DATA_PATH}}` | The canonical-data decision: a read-only copy at `data/`, or the absolute path recorded in `data/DATA_PATH.txt`. This pointer is the project's ONLY absolute path. |
| `{{PROMOTED_ARTIFACTS}}` | Frozen artifacts promoted to `shared/` — `— (none yet)` in a fresh project. |
| `{{CAMPAIGN_1_NAME}}` / `_DATE` / `_APPROACH` / `_METRIC` / `_RESULT` / `_DISCOVERIES` / `_KBKEY` | The opening `LINEAGE.md` Campaigns row for the first campaign (`_RESULT` is `pending` until exp 000; `_DISCOVERIES` and `_KBKEY` are `—`). |

### Framing & planning docs (INTAKE · PROJECT_ORIENTATION · PHYSICS · VERIFICATION_PLAN · protocols/expensive-evaluation)
These fill the setup/planning docs authored before the loop runs. The `*_PROPOSED` tokens hold the
user's **pre-sign-off** proposals captured in `INTAKE.md`; once the campaign spec is signed off they are
restated (frozen) in `charter.md` / `metric.py` under their final names — see the alias note below.

| Placeholder | Meaning |
|---|---|
| `{{GOAL_PROPOSED}}` | INTAKE: the proposed campaign goal (pre-sign-off). |
| `{{DECISION_PROPOSED}}` | INTAKE: the decision the result is proposed to drive. |
| `{{OUT_OF_SCOPE}}` | What is explicitly out of scope (INTAKE + PROJECT_ORIENTATION). |
| `{{LIT_POSITIONING}}` | INTAKE: how the work is positioned against the literature. |
| `{{PRIMARY_METRIC_PROPOSED}}` | INTAKE: proposed primary metric (→ `{{PRIMARY_METRIC}}` once frozen). |
| `{{SCORER_PROPOSED}}` | INTAKE: proposed scorer/definition (→ `{{METRIC_DEFINITION}}` / `{{FROZEN_SCORER_PATH}}`). |
| `{{GUARDRAIL_PROPOSED}}` | INTAKE: proposed guardrail metric (→ `{{GUARDRAIL_METRIC}}`). |
| `{{BOUNDS_PROPOSED}}` | INTAKE: proposed bounds/plausible range (→ `{{METRIC_HARD_BOUNDS}}` / `{{METRIC_PLAUSIBLE_RANGE}}`). |
| `{{LEVERS_PROPOSED}}` | INTAKE: proposed levers (→ `{{LEVERS_LIST}}`). |
| `{{FROZEN_PROPOSED}}` | INTAKE: proposed FROZEN set (→ `{{FROZEN_LIST}}`). |
| `{{TIERS_PROPOSED}}` | INTAKE: proposed evaluation tiers/caps (→ the Caps table). |
| `{{DATA_PROPOSED}}` | INTAKE: proposed data / eval target (→ `{{DATA_SOURCE}}` / `{{EVAL_TARGET}}`). |
| `{{EVAL_COST}}` | INTAKE: the cost of one evaluation (time/compute). |
| `{{EXPENSIVE_EVAL_FLAG}}` | INTAKE: whether evaluations are expensive (gates the expensive-evaluation protocol). |
| `{{APP_VERIFICATION_TASKS}}` | INTAKE: domain/application-specific verification tasks identified at setup. |
| `{{GIT_CHOICE}}` | INTAKE: whether to use git for this campaign, and why. |
| `{{GOAL_STATEMENT}}` | PROJECT_ORIENTATION: the end goal, stated plainly. |
| `{{DECISION_SERVED}}` | PROJECT_ORIENTATION: the decision the goal serves. |
| `{{DONE_CRITERIA}}` | PROJECT_ORIENTATION: what "done" looks like. |
| `{{TASK_1}}` … | PROJECT_ORIENTATION: a numbered task (one per task: `{{TASK_1}}`, `{{TASK_2}}`, …). |
| `{{TASK_1_RATIONALE}}` … | PROJECT_ORIENTATION: how task N serves the goal (paired with each `{{TASK_N}}`). |
| `{{NEXT_POINTER}}` | PROJECT_ORIENTATION: the current NEXT pointer. |
| `{{EFFECT_1}}`, `{{EFFECT_2}}`, `{{EFFECT_3}}`, `{{EFFECT_4}}`, `{{EFFECT_5}}` | PHYSICS / INTAKE: rows of the physical-effect inventory (extend/trim to fit). |
| `{{TAG_1}}` … | INTAKE: the in/out tag for effect N (accounted / negligible-by-scale / deferred / unknown). |
| `{{WHY_1}}` … | INTAKE: why effect N carries that tag (paired with each `{{EFFECT_N}}`). |
| `{{APRIORI_BOUND}}` | INTAKE / PHYSICS: the a-priori order-of-magnitude bound on the answer (see alias note). |
| `{{DOMAIN_ASSUMPTIONS}}` | INTAKE / PHYSICS: assumptions that define the model's domain of applicability. |
| `{{APRIORI_RANGE}}` | VERIFICATION_PLAN: the a-priori plausible range for the metric (see alias note). |
| `{{HARD_BOUNDS}}` | VERIFICATION_PLAN: the mathematical hard bounds on the metric (see alias note). |
| `{{ANALYTIC_LIMITS}}` | VERIFICATION_PLAN: closed-form / limiting cases the result must match. |
| `{{INVARIANTS}}` | VERIFICATION_PLAN: conservation / symmetry invariants to check. |
| `{{CONVERGENCE_PLAN}}` | VERIFICATION_PLAN: how numerical convergence will be demonstrated. |
| `{{PARITY_METHOD}}` | VERIFICATION_PLAN: the independent / mechanism-diverse method used for parity checks. |
| `{{VALIDATION_DATA}}` | INTAKE / VERIFICATION_PLAN: the held-out / independent data used to validate. |
| `{{VALIDATION_HIERARCHY}}` | VERIFICATION_PLAN: the unit → subsystem → full-system validation ladder. |
| `{{DOMAIN}}` | VERIFICATION_PLAN: the stated domain of applicability (never extrapolate past it unflagged). |
| `{{APP_CHECK_1}}` / `{{APP_CHECK_2}}` | VERIFICATION_PLAN: application-specific verification checks. |
| `{{KNOWN_ARTIFACTS}}` | VERIFICATION_PLAN: known artifacts / gotchas to watch for (see alias note). |
| `{{CLASSICAL_BASELINE}}` | expensive-evaluation: the classical optimizer to benchmark sample-efficiency against. |
| `{{STOP_CRITERION}}` | expensive-evaluation: the diminishing-returns stop criterion. |
| `{{MIN_DELTA}}` | expensive-evaluation: the minimum improvement that counts as progress. |
| `{{PATIENCE}}` | expensive-evaluation: how many non-improving evaluations to allow before stopping. |

### Loop configuration (configs/loop.json — supervisor mode)
Set from the campaign's **unit cost** during the interview; the cadence *inverts* with cost (expensive
units → plan often, small k; cheap units → plan in strides, large k — keep planner overhead a small
fraction of loop compute). The plateau threshold is dual-denominated (units AND wall-clock, whichever
trips first). Rationale: `STRUCTURED_LOOP_PROPOSAL.md` §4.1 rule 4 / ADR-0008.

| Placeholder | Meaning |
|---|---|
| `{{UNIT_COST_CLASS}}` | One word for a unit's cost scale: `seconds` / `minutes` / `hours` / `days`. |
| `{{UNIT_COST_S}}` | Typical wall-clock seconds for one unit (number, order-of-magnitude is fine). |
| `{{UNIT_COST_DISK_MB}}` | Megabytes one unit ADDS to `results/` (number; save-set + snapshot + bulk artifacts). Derived from the artifact plan, not asked. Arms the driver's disk floor (refuses to launch / halts below ~3 units of headroom); `0` disables it. Human-readable twin: `{{DISK_PER_EXP}}`. |
| `{{PLANNER_CADENCE_K}}` | Spawn the planner every k accepted units (also the default outstanding-units cap). |
| `{{PLANNER_MODEL}}` | Model for the planner agent (judgment role — heavier tier; user-owned thereafter). |
| `{{PLATEAU_M_UNITS}}` | Plateau trigger: no accepted result in m units. |
| `{{PLATEAU_M_HOURS}}` | Plateau trigger: no accepted result in this much wall-clock (whichever trips first). |
| `{{MAX_OUTSTANDING_UNITS}}` | Max units queued beyond planner review (default = `{{PLANNER_CADENCE_K}}`). |
| `{{WORKER_MODEL}}` | Model for iteration workers (lightest that reliably does the task; user-owned). |
| `{{ITERATION_TIMEOUT_HOURS}}` | Hard wall-clock cap on one worker iteration (> the Extended-tier run cap). |
| `{{VERIFY_REPRO_THRESHOLD_S}}` | ADR-0008 tier boundary: unit cost at/below → full re-execution in verify; above → judgment + cheapest discriminating spot-check. |

> **Alias note (proposed → final, and near-synonyms).** Several tokens name the **same quantity at
> different stages or in different docs**; fill them consistently. The a-priori bound/range appears as
> `{{APRIORI_BOUND}}` (INTAKE/PHYSICS), `{{APRIORI_RANGE}}` (VERIFICATION_PLAN), `{{APRIORI_BOUND_NOTES}}`
> (charter.md), and `{{METRIC_PLAUSIBLE_RANGE}}` (program/metric); the metric's hard bounds as
> `{{HARD_BOUNDS}}` (VERIFICATION_PLAN) and `{{METRIC_HARD_BOUNDS}}` (program/metric); the domain gotchas
> as `{{KNOWN_ARTIFACTS}}` (VERIFICATION_PLAN) and `{{KNOWN_GOTCHAS}}` (CONVENTIONS/INTAKE). The split is
> intentional — the planning docs are drafted before the charter freezes the final wording — but the
> setup skill should keep the paired values in sync.
