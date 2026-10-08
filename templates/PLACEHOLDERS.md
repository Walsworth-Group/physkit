# Placeholder Convention — spec for the `new-campaign` setup skill

How the `*.tmpl` files under `templates/campaign/` are filled into a generated campaign. This file is
guidance for the setup skill and is not copied into a campaign. The canonical placeholder list at the
bottom is authoritative: every `{{NAME}}` appearing in any template must be listed here, and every name
listed here must be used by at least one template, in both directions, enforced by Tier 0.
Scope is `kit/templates/`. Tokens in a skill's own assets (`kit/skills/*/assets/`) are
filled by that skill and documented by it, not here.

## Syntax
- **`{{UPPER_SNAKE_CASE}}`** — a substitution the setup skill fills. Names that are plural or end in
  `_LIST` / `_ROWS` / `_TABLE` / `_FIELDS` / `_NOTES` may expand to multi-line content: a bulleted list,
  table rows, JSON fields. Singular names are short inline phrases.
- **`[[OPTIONAL — <condition>: … ]]`** — a block included only if `<condition>` holds. May span multiple
  lines, with the closing `]]` on its own line. See the delete-vs-keep rule below.
- **`[PROPOSED]`** — an inline tag on a speculative or optional discipline. The setup skill presents these
  to the user to keep or cut; surviving ones lose the tag, and cut ones are deleted.
- **`[[KEEP — <reason>]]`** — a line marking what must survive the fill: an element code reads (`read by
  <consumer>: …` - a heading, key, column or line, spelled exactly) or the frozen integrity core. The setup
  skill keeps the element and deletes the tag line. Everything unmarked is a starting point the setup agent
  may reshape, or drop with the user's sign-off (new-campaign Step 2). The JSON configs and hook settings
  carry no tags (JSON has no comments): treat them as machine config - change values, not keys; `_doc`
  strings are free text.
- **`.tmpl` suffix** — marks a file that contains placeholders. Stripped on generation
  (`campaign.md.tmpl` → `campaign.md`).
- **`<NN>`, `<slug>`, `<label>`, `<G>`** in prose or example text are literal illustrative placeholders
  showing how filenames look at runtime. They are not substitutions; leave them as they are. Only
  `{{...}}` is substituted. `{{NN}}` and `{{SLUG}}` are substitutions: they appear in the config
  templates' `exp_name`.

## Delete-vs-keep rule (no half-resolved files)
- **`[[OPTIONAL]]` blocks and OPTIONAL-marked files: delete when they do not apply.** A ceilings block for
  a metric with no ceiling, or `campaign.md` §Dataset / inputs for a fixed-dataset campaign, is removed
  entirely. This keeps the slim core slim.
- **Universal but momentarily empty sections: keep with a note, never delete.** A planned-but-unwired
  guardrail stays in the Decision Metrics section marked `(DEFERRED — wired after <milestone>)`.
- **Rule of thumb:** part of the universal discipline (metric integrity, verification, FROZEN rules,
  logging) means keep-with-note; a domain feature that is not present means delete the optional block.
- **Hard requirement:** a generated file containing any literal `{{...}}`, any unresolved `[[OPTIONAL`, any
  leftover `[[KEEP` tag, or any leftover `[PROPOSED]` the user did not rule on is an error. The setup skill
  must scan every generated file and fail loudly if one remains.

## Filling guidance
- Pick the closest archetype from `ARCHETYPE_CHEATSHEET.md` first; it names the typical metric, levers,
  FROZEN set, and failure modes to slot in.
- Fill from the interview: goal, metric, physics, data, constraints, compute, time. Where the user defers,
  for example a parameter they will fit later, write the placeholder's content as an explicit TODO with
  the deferral noted, rather than a silent guess.
- Keep fills clear, explicit, and concise, and specific enough to act on without the interview that
  produced them.
- **Steering carries its source.** A fill that steers a worker - a landmine, an artifact to guard
  against, a range, a check - names where it came from (the user, a derivation, a reference, a prior
  campaign's ledger id or verdict). A fill you can only reason your way to is not written into
  `campaign.md`; it goes into the opening `results/JOURNAL.md` marked `[setup inference]`, where the
  worker who tests it can drop it. A contract line cannot be argued with from inside a spawn.

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
| `{{METRIC_PLAUSIBLE_RANGE}}` | The metric's PLAUSIBLE RANGE in prose, signed off by the user at setup (e.g. "RMSE in [0, 0.84 A/m²]: perfect to all-zeros"). A cheap implementation-error check, not a prediction: a score outside it is flagged. Its basis is `{{APRIORI_BOUND_NOTES}}`. |
| `{{PLAUSIBILITY_BOUNDS}}` | The same range as a Python literal for `scripts/metric.py`: `(low, high)` with `None` on an unbounded side (`(0.0, 0.84)` for the example above), or `None` if this campaign encodes none. **A literal, not prose**: a fallback string here is a syntax error in FROZEN core. |
| `{{BASELINE_DESCRIPTION}}` | What exp 000 is and its expected value. |
| `{{BASELINE_VALUE}}` | The baseline metric value (the floor). |
| `{{BASELINE_COMMAND}}` | Command to run exp 000. |
| `{{CEILING_LIST}}` | (optional) Inline list of theoretical ceilings. |
| `{{METRIC_INPUTS}}` | What feeds the metric (crop, preprocessing, normalization, …). |
| `{{COMPARABILITY_AXES}}` | What must match exp 000 for an apples-to-apples comparison. |
| `{{EVAL_TARGET}}` | The data/target the metric is evaluated on. |

### Metrics roster & reporting
| Placeholder | Meaning |
|---|---|
| `{{GUARDRAIL_METRIC}}` | The secondary guardrail metric name. |
| `{{GUARDRAIL_SUMMARY}}` | One-line summary of the guardrail (Mission line). |
| `{{GUARDRAIL_USE}}` | What the guardrail is used for (checkpoint selection, overfit watch). |
| `{{GUARDRAIL_CHECK}}` | The concrete guardrail check run at loop step 5. |
| `{{DIAGNOSTIC_METRICS}}` | Co-tracked diagnostic quantities. |
| `{{SECONDARY_METRICS}}` | Metrics evaluated alongside the primary at step 4. |
| `{{PRIMARY_REPORT_RULE}}` | How to report the primary (e.g. always with the subgroup split). |
| `{{GENERALIZATION_AXIS}}` | campaign.md §Verification: the axis a promoted finding must generalize across (frames/conditions/…), with its source. |

### Loop & run
| Placeholder | Meaning |
|---|---|
| `{{RUN_STEP_NAME}}` | Loop step-3 verb (e.g. "RUN", "TRAIN", "SOLVE"). |
| `{{RUN_COMMAND}}` | The command that runs one experiment. |
| `{{RUN_NOUN}}` | Noun for the caps table title (e.g. "Run", "Training"). |
| `{{IMPLEMENT_VERB}}` | What "IMPLEMENT" means here, as an action phrase only (e.g. "modify the decoder/loss"). The config path is already in the boilerplate; do not repeat it. |
| `{{SANITY_STEP}}` | Name of the loop sanity/guardrail step (e.g. "SANITY"). |
| `{{EVAL_WRITER}}` | The script/function that writes the evaluation output. |
| `{{VALIDATION_CHAIN}}` | The pipeline chain exp 000 validates end-to-end (named in the decision record's baseline entry). |
| `{{ARTIFACT_LIST}}` | What artifacts each run saves (step 8 summary). |
| `{{CHECKPOINT_EVERY}}` | Checkpoint cadence N. |
| `{{COST_UNIT}}` | Unit of run cost (epochs, iterations, seconds, solves). |
| `{{COST_NOTE}}` | (optional) Note on why experiments are cheap/fast. |
| `{{DISK_PER_EXP}}` | Human-readable disk footprint of one experiment (e.g. "1.2 MB" / "~4 GB (checkpoints dominate)"). Derived in the interview from the artifact plan; the machine-readable twin is `{{UNIT_COST_DISK_MB}}`. |
| `{{RETENTION_PLAN}}` | The keep-vs-regenerate plan for bulk artifacts when they are large: which are kept, which are regenerated on demand and the command, and any pruning cadence. When experiments are small, state that no plan is needed and why; never leave it blank. The permanent record (save-set, snapshot, narrative, verdicts) is never in scope. |

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
| `{{PHYSKIT_VERSION}}` | The kit-version pin, `vX.Y.Z (<ref>, YYYY-MM-DD)`: version from the active harness manifest under the PhysKit package root (`.codex-plugin/plugin.json` on Codex or `.claude-plugin/plugin.json` on Claude; require equality when both exist), `<ref>` from `git -C "<resolved PhysKit package root>" rev-parse --short HEAD` where that root is a Git checkout (omit otherwise), plus the scaffold date. Appears in `campaign.md`'s header and atop `results/logbook.md` — the campaign's doctrine and tooling provenance (every release is tagged, so the pin recovers the whole kit). A record: never updated to a newer version. |
| `{{VERIFY_EXTRA_CHECKS}}` | Archetype-specific extra checks the verifier must do, as a clause fragment appended to "checks for metric contamination" (e.g. ", recomputes the ceilings, and checks the ceiling-vs-gap trap"). Do not repeat "metric contamination". |
| `{{APRIORI_BOUND_NOTES}}` | campaign.md §The ONE metric: the basis of the plausible range — how each end was computed (e.g. the trivial predictor's score on the evaluation data) or the reference it is taken from. |
| `{{PHYSICAL_BOUNDS_NOTES}}` | campaign.md §The ONE metric: the physical bounds/scales of key quantities. |
| `{{SIM_GAP_NOTE}}` | The sim-to-experiment gap specific to this campaign. |

### Levers, FROZEN & code
| Placeholder | Meaning |
|---|---|
| `{{LEVER_SUMMARY}}` | One-line summary of the levers (Mission line). |
| `{{LEVERS_LIST}}` | The full categorized list of levers. |
| `{{LEVER_COLUMNS}}` | The lever columns in the scoreboard (tab-separated). |
| `{{FROZEN_LIST}}` | What is FROZEN besides the scorer. |
| `{{READONLY_LIST}}` | Read-only files (use, don't edit). |
| `{{MUTABLE_LIST}}` | Mutable files: `scripts/experiment.py` (the campaign's hooks and helpers) and the campaign modules it imports — never `scripts/run_campaign.py`, the kit's machinery. |
| `{{DATA_CHOICE_WARNING}}` | (optional) Warning that a data/distribution choice must be held fixed. |
| `{{DATA_DISTRIBUTION}}` | (optional) The distribution that changes if the data choice moves. |
| `{{CODE_SNAPSHOT_RULE}}` | (optional) The code-snapshot rule when code under test is mutable. |
| `{{HARDWARE_LIMITS}}` | (optional, hardware-in-the-loop only) The specific hardware safety limits / safe ranges that are hard constraints. |
| `{{LITERATURE_LEVEL}}` | (optional, when literature search is enabled) The intensity: "only when needed" (search when stuck) or "extensive" (proactive + periodic). |

### Logging & scoreboard
| Placeholder | Meaning |
|---|---|
| `{{SCOREBOARD_COLUMN_LIST}}` | The full scoreboard schema string (in campaign.md), including the runner-written narrative columns `what` · `plausible` · `verified` · `note` · `finding`. |
| `{{PRIMARY_METRIC_COL}}` | The scoreboard column holding the primary metric. |
| `{{PRIMARY_SPREAD_COL}}` | The column holding the replicate spread. |
| `{{GUARDRAIL_COL}}` | The column holding the guardrail value. |
| `{{DIAGNOSTIC_COLUMNS}}` | Supplemental metric / sanity-score columns (tab-separated). |
| `{{RUN_COLUMNS}}` | Experiment-type run numerics (tab-separated): epochs trained + best epoch (ML), iterations / wall-clock / n_free_params (fits), seed / n_reps. May be empty; if so, remove it and its adjacent tab. |

### Protocol stubs
| Placeholder | Meaning |
|---|---|
| `{{BASELINE_METHODS}}` | The baseline method(s) for exp 000 (the decision record's ED-000 entry; exp 000 runs at setup). |
| `{{GATE_CRITERIA}}` | The criteria exp 000 met before handoff (the sanity checks that prove the chain is sound). |
| `{{FLOOR_RECORD_RULE}}` | Where the floor is recorded (the exp000 ledger row; the JOURNAL's §Where we stand). |
| `{{PER_EXP_ARTIFACTS}}` | The always-saved per-experiment artifacts. |
| `{{FIGURE_SPEC}}` | The standard per-experiment figure, panel by panel. |
| `{{PROMOTED_BEST_ARTIFACTS}}` | The heavier artifacts saved on promotion. |
| `{{ARTIFACT_COMMAND}}` | The command/flag that saves the full artifact set. |
| `{{DATA_SOURCE}}` | Where the inputs come from. |
| `{{GENERATE_COMMAND}}` | Command to generate/fetch the data. |
| `{{SPLIT_TABLE}}` | The fixed data splits. |
| `{{LOAD_PIPELINE}}` | How a config loads the data. |
| `{{DISTRIBUTION_NOTE}}` | Which knobs are data-choices vs method-levers. |

### Conventions (fill `PROJECT.md` §Standing constraints)
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
| `{{ENVIRONMENT_NOTES}}` | Environment/dependency notes. |
| `{{PYTHON_CMD}}` | The python invocation for hook commands, from Step 0.5 detection (e.g. `py -3` on Windows, `python3` on macOS/Linux). Used in `.claude/settings.json` and `.codex/hooks.json`. |
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

### Project & promoted-artifact references
The project overview, `PROJECT.md`, lives at a fixed place (the project
root), so the campaign templates carry its path as a literal — `../../PROJECT.md` from the
campaign root, `../../../PROJECT.md` one directory down (`roles/`, `results/`, `docs/`) —
and there is no placeholder to fill. Never replace a literal with a campaign-local copy (the validator
rejects one). Promoted frozen artifacts live in purpose-named project-level dirs (`scripts/`,
`models/`, …), each with a `PROJECT.md` §Lineage promotion line; that line is the durable provenance record:

| Placeholder | Meaning | Value (by file location) |
|---|---|---|
| `{{SIBLING_FROZEN_MUTABLE}}` | (coupled sibling campaigns only — else delete the block) What this campaign FREEZES that a sibling treats as MUTABLE, and vice versa. | — |
| `{{CONSUMED_ARTIFACTS}}` | (coupled sibling campaigns only) The promoted `../../<dir>/<artifact>_<ver>/` artifacts this campaign reads, never a sibling's working folder. | — |

### Project-tree placeholders (`templates/project/`)
Filled by `new-project` when it creates the home. A one-off project fills these from the campaign
interview; they are not a second interview.

| Placeholder | Meaning |
|---|---|
| `{{PROJECT_TITLE}}` | The project/investigation name (the `README.md`, `PROJECT.md`, and project `CLAUDE.md` H1). |
| `{{PHYSICAL_SYSTEM}}` | One line naming the physical system under investigation. |
| `{{GOAL_STATEMENT}}` / `{{DECISION_SERVED}}` / `{{DONE_CRITERIA}}` | The end goal, the decision it serves, and what "done" looks like. `{{GOAL_STATEMENT}}` fills `PROJECT.md`; the other two also fill the campaign's `campaign.md` §Mission (the campaign-scoped answers). |
| `{{SYSTEM_INVARIANTS}}` | Project-wide invariants every campaign inherits (drawn from the topic-4 physics interview). |
| `{{DATA_LOCATION}}` / `{{DATA_PATH}}` | The canonical-data decision: a read-only copy at `data/`, or the absolute path recorded in `data/DATA_PATH.txt`. This pointer is the project's only absolute path. |
| `{{CAMPAIGN_1_NAME}}` / `{{CAMPAIGN_1_DATE}}` / `{{CAMPAIGN_1_APPROACH}}` / `{{CAMPAIGN_1_METRIC}}` / `{{CAMPAIGN_1_RESULT}}` / `{{CAMPAIGN_1_DISCOVERIES}}` | The opening `PROJECT.md` §Lineage Campaigns row for the first campaign (`_RESULT` is `pending` until exp 000; `_DISCOVERIES` is `—`). |
| `{{TARGET_OF_STUDY}}` | `PROJECT.md` §The system under study: what is under investigation — the sample, material, plasma, star, molecule, or device — its identity and structure, and the physical quantities the project aims to determine or optimize. The rig that probes it is §The instrument, not this. |
| `{{INSTRUMENT_DESCRIPTION}}` | `PROJECT.md` §The instrument: what measures what (e.g. NV widefield magnetometer · telescope + detector · spectrometer). |
| `{{INSTR_PARAM_1}}` / `{{INSTR_VALUE_1}}` / `{{INSTR_UNITS_1}}` / `{{INSTR_SOURCE_1}}` | One row of §The instrument's parameter table: name, value, units, and how the value is known. Provenance is part of the row, not optional. Extend with further rows as the rig is characterized. |
| `{{MEASUREMENT_MODEL}}` | §The instrument: how instrument readings map to physical quantities — the forward measurement chain, so raw data is never mistaken for the quantity of interest. |
| `{{INSTRUMENT_ARTIFACTS}}` | §The instrument: drifts, backgrounds, and calibration caveats — the recurring gotchas to guard against. Pairs with `{{KNOWN_GOTCHAS}}` in §Standing constraints. |

### Session notes (`templates/project/sessions/`)
Filled when an ad-hoc, non-campaign session is opened: exploration, debugging, or a one-off analysis with
no frozen metric driving a loop. With such a metric it is a campaign, not a session. Not filled by
`new-project`.

| Placeholder | Meaning |
|---|---|
| `{{SESSION_DATE}}` / `{{SESSION_SLUG}}` | The session's date and short name. They also form its directory, `sessions/<date>_<slug>/`, and its `PROJECT.md` §Lineage Sessions row, so the two must agree. |
| `{{SESSION_GOAL}}` | The question the session set out to answer, or the thing to debug or try. |
| `{{SESSION_WORK}}` | The concrete steps: what was run, inspected, changed. Enough to reconstruct. |
| `{{SESSION_FINDING}}` | One finding from the session. |
| `{{FINDING_TIER}}` | The rigor tier of that finding, stated accurately (e.g. `exploratory (unverified)` · `verify-CONFIRMED` · `PROVISIONAL`). A session finding is not a verified project DISCOVERY unless it passed `verify`; the tag is what stops an ad-hoc conclusion being trusted like a campaign result. |
| `{{SESSION_ARTIFACTS}}` | Files, plots, and scripts produced, with paths inside this session folder. |

### Goal & verification (campaign.md §Mission / §Verification · the project overview PROJECT.md)
The campaign's orienting answers and its own verification checks, filled directly into the signed-off
contract. There is no separate planning doc: `campaign.md` is drafted, user-edited where preferred
(draft-document mode), and frozen at sign-off.

| Placeholder | Meaning |
|---|---|
| `{{OUT_OF_SCOPE}}` | `campaign.md` §FROZEN / out of scope: what is explicitly out of scope / not claimed. |
| `{{DECISION_SERVED}}` | `campaign.md` §Mission: the decision this campaign's result serves. |
| `{{DONE_CRITERIA}}` | `campaign.md` §Mission: what "done" looks like for this campaign. |
| `{{EFFECT_1}}`, `{{EFFECT_2}}`, `{{EFFECT_3}}`, `{{EFFECT_4}}`, `{{EFFECT_5}}` | PROJECT.md §Standing constraints: rows of the physical-effect inventory (extend/trim to fit). |
| `{{APRIORI_BOUND}}` | PROJECT.md §Standing constraints: the a-priori order-of-magnitude bound on the answer (see alias note). |
| `{{DOMAIN_ASSUMPTIONS}}` | PROJECT.md §Standing constraints: assumptions that define the model's domain of applicability. |
| `{{ANALYTIC_LIMITS}}` | campaign.md §Verification: closed-form / limiting cases the result must match. |
| `{{INVARIANTS}}` | campaign.md §Verification: conservation / symmetry invariants to check. |
| `{{CONVERGENCE_PLAN}}` | campaign.md §Verification: how numerical convergence will be demonstrated. |
| `{{PARITY_METHOD}}` | campaign.md §Verification: the independent / mechanism-diverse method used for parity checks. |
| `{{VALIDATION_DATA}}` | campaign.md §Verification: the held-out / independent data used to validate (calibration is not validation). |
| `{{APP_CHECK_1}}` / `{{APP_CHECK_2}}` | campaign.md §Verification: the field-standard, application-specific checks generic doctrine cannot supply. |
| `{{KNOWN_ARTIFACTS}}` | campaign.md §Verification: known artifacts / failure modes to guard against, each with its source (see alias note); a suspected one goes to the JOURNAL as `[setup inference]`. |

### Campaign properties (configs/loop.json `"campaign"` — what kind of campaign this is)
A setup-time declaration the comparison checks branch on, plus its numeric companions and the
comparability tags. It is a decision rather than a default to accept quietly: ask it. `noise_model`
governs whether a win is judged against a replicate spread or a numerical tolerance. Getting it wrong is
silent: a stochastic campaign mislabelled deterministic promotes noise,
and a deterministic one mislabelled stochastic is held to a spread test it can never satisfy.

| Placeholder | Meaning |
|---|---|
| `{{NOISE_MODEL}}` | `stochastic` (default — repeated runs differ, so a win must clear the replicate spread) / `deterministic` (repeated runs are identical, so the test is a numerical tolerance). Decide it by re-running one experiment twice, not from intuition about the method. |
| `{{NOISE_FLOOR}}` | JSON **number or `null`**: the once-estimated replicate spread for a stochastic campaign (`verify` §Clear the noise floor), re-estimated only when something that could move it changes. `null` means not yet estimated, which makes the noise-floor check report `unavailable` rather than silently pass. |
| `{{METRIC_TOLERANCE}}` | JSON **number or `null`**: the numerical equality tolerance for a deterministic campaign. `null` means not yet set, and the check reports `unavailable`. |
| `{{METRIC_VERSION}}` | Comparability tag for the FROZEN metric (e.g. `v1`). Stamped onto every scoreboard row and result JSON. **Bump it whenever the scoring math changes**, and re-score saved contenders before comparing: a number carried across a metric change is not a comparison. A bump is a metric epoch: declare it in `campaign.metric_epochs` (the first epoch is implicit). |
| `{{DATA_VERSION}}` | Comparability tag for the dataset/version scored against (e.g. `v1`, `v2_corrected`). Same rule: bump on any change to the evaluation data. |

> Both `{{NOISE_FLOOR}}` and `{{METRIC_TOLERANCE}}` are JSON **numbers**, not prose: a fallback string
> here breaks the parse, the same hazard `{{UNIT_COST_DISK_MB}}` carries. Write `null` when unknown.

### Loop configuration (configs/loop.json — supervisor mode)
Set from the campaign's unit cost during the interview.

| Placeholder | Meaning |
|---|---|
| `{{UNIT_COST_CLASS}}` | One word for a unit's cost scale: `seconds` / `minutes` / `hours` / `days`. |
| `{{UNIT_COST_S}}` | Typical wall-clock seconds for one unit (number, order-of-magnitude is fine). |
| `{{UNIT_COST_DISK_MB}}` | Megabytes one unit adds to `results/` (number; save-set + snapshot + bulk artifacts). Derived from the artifact plan, not asked. Arms the driver's disk floor (refuses to launch / halts below ~3 units of headroom); `0` disables it. Human-readable twin: `{{DISK_PER_EXP}}`. |
| `{{AGENT_BACKEND}}` | Harness that will launch first: `claude` or `codex`. A switchable campaign still records its first launcher here; `--backend` overrides it later. |
| `{{VERIFIER_MODEL}}` | Claude model for the verifier and the end-of-loop claim audit (judgment roles — heavier tier); blank inherits Claude Code's configured default. |
| `{{VERIFIER_CLAUDE_EFFORT}}` | Claude verifier/capstone effort: blank (inherit), `low`, `medium`, `high`, `xhigh`, or `max`; support is model/version dependent. |
| `{{VERIFIER_CODEX_MODEL}}` | Codex model for the verifier and the claim audit; blank inherits Codex's configured default. |
| `{{VERIFIER_CODEX_REASONING_EFFORT}}` | Codex verifier/capstone reasoning effort: blank (inherit), `minimal`, `low`, `medium`, `high`, or `xhigh`. |
| `{{WORKER_MODEL}}` | Claude model for iteration workers (lightest that reliably does the task); blank inherits Claude Code's configured default. |
| `{{WORKER_CLAUDE_EFFORT}}` | Claude worker effort: blank (inherit), `low`, `medium`, `high`, `xhigh`, or `max`; support is model/version dependent. |
| `{{WORKER_CODEX_MODEL}}` | Codex model for iteration workers; blank inherits Codex's configured default. |
| `{{WORKER_CODEX_REASONING_EFFORT}}` | Codex worker reasoning effort: blank (inherit), `minimal`, `low`, `medium`, `high`, or `xhigh`. The direct Codex verifier follows the worker pair. |
| `{{ITERATION_TIMEOUT_HOURS}}` | Hard wall-clock cap on one worker iteration (> the Extended-tier run cap). |
| `{{VERIFICATION_PRESET}}` | The campaign's verification preset — `none` · `minimal` (the default) · `light` · `heavy` · `intensive` — the one user-facing choice of how much verification the campaign buys and of what kind (new-campaign topic 8b; the descriptions are `docs/reference/verification-presets.md`, presented verbatim). Rendered into `configs/loop.json` `verify.preset` only; never embedded in prose. |
| `{{METRIC_REVISION}}` | The metric-revision dial — `cautious` (the default: a metric revision raises ESCALATE and waits) or `autonomous` (the loop may enact a verified revision as a pending epoch and continue). Asked in the same interview step as the preset (topic 8b). Rendered into `configs/loop.json` `campaign.metric_revision`. |

> **Alias note (near-synonyms across docs).** A few tokens name the same quantity in different docs; fill
> them consistently. The metric's plausible range appears as `{{METRIC_PLAUSIBLE_RANGE}}` with its basis
> `{{APRIORI_BOUND_NOTES}}` (campaign.md) and `{{PLAUSIBILITY_BOUNDS}}` (its executable form, in the FROZEN
> scorer): fill both from one signed-off answer, and if you change one, change both. PROJECT.md's
> `{{APRIORI_BOUND}}` (the a-priori bound on the physical answer) may inform it but is not the same token.
> The domain gotchas appear as `{{KNOWN_ARTIFACTS}}` (campaign.md §Verification — what a *check* must
> guard against) and `{{KNOWN_GOTCHAS}}` (PROJECT.md §Standing constraints —
> the project-wide symptom → check catalog). The split is intentional; keep the paired values in sync.
