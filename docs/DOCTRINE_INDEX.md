---
id: doctrine-index
kind: metadata
layer: shared
load: on-demand
load_trigger: When deciding which doctrine file to read, auditing coverage, or adding a new artifact to the kit.
frozen: false
addresses: [7]
status: new
review: living
---

# Doctrine Index — the kit's map of itself

This is the maintained, machine-readable index of every doctrine artifact in the kit: what it is, when
it loads, which principle contexts it enforces, and its build status. It exists so that the agent and the
maintainer can find the right file without loading everything. It is the substrate for context economy
(Principle Context 7) and for any future self-improving meta-loop.

Two jobs:
1. Define the metadata schema (below) that every doc and skill carries in YAML frontmatter.
2. Hold the index table mapping every artifact to its metadata and status. Update this table whenever an
   artifact is added, ported, extended, or retired.

> Single sources of truth. Principles live in [`PRINCIPLES.md`](PRINCIPLES.md) (canonical taxonomy).
> The always-loaded spine is [`CORE.md`](CORE.md). This index never restates principle content; it only
> points. Context numbers below (`addresses:`) refer to the nine legacy contexts in `PRINCIPLES.md`, not
> to the nine pillars of the v2 taxonomy. The numbering differs, and a later migration will reconcile it.

---

## 1 · The metadata schema

Every doctrine doc, protocol, and scaffold template begins with a YAML frontmatter block using these
fields. Skills are the exception: a `SKILL.md` frontmatter stays loader-clean, carrying only the `name`
and `description` the plugin loader requires, so that `claude plugin validate` passes. A skill's metadata
lives in the index table below instead. The schema is therefore the contract for non-skill files in-file,
and for skills in this index.

```yaml
---
id: <short-kebab-slug>            # unique within the kit
kind: <see KIND below>            # the delivery mechanism
layer: general | campaign | shared
load: always | on-demand          # context-economy tier
load_trigger: <one line>          # WHEN this should be pulled into context
frozen: true | false             # part of the non-negotiable honesty/verification core?
addresses: [<context numbers>]    # which PRINCIPLES.md contexts it enforces (1–8)
status: <see STATUS below>        # build state
review: <flag | date | "living" | omit>
---
```

**`kind`** — the delivery mechanism (from the delivery-mechanism taxonomy):

| value | meaning |
|---|---|
| `core-doc` | always-loaded slim spine; the constitution + routing |
| `reference-doc` | on-demand depth; read when a situation calls for it |
| `skill` | an invokable `SKILL.md` (general or campaign) |
| `protocol` | a campaign procedure template (e.g. checkpoint, artifacts) |
| `scaffold-template` | a `*.tmpl` file materialized into a generated campaign tree |
| `metadata` | indexes/schemas about the kit itself (this file) |

**`layer`** — `general` (everyday science requests), `campaign` (autoresearch loops only), or `shared`
(both). The dual-use split: general sessions never pay the context cost of campaign material,
because campaign artifacts are `on-demand` and `layer: campaign`.

**`frozen`** — `true` for the honesty/verification constitution that no self-improvement may weaken:
scientific integrity (Ctx 1), independent verification (Ctx 2), metric integrity (comparability, and no
quiet or self-serving change to the ruler — a metric is revised only as a declared, verified epoch),
context economy. Everything else is `false`.

**`status`** — build state, so this index doubles as the live build tracker:

| value | meaning |
|---|---|
| `new` | authored fresh for this version |
| `ported` | carried over from v2 with reorganization |
| `shipped-v2` | exists in v2, not yet revised |
| `extend` | exists in v2; planned changes not yet applied |
| `planned` | designed but not yet built |
| `deferred` | intentionally postponed |

**`addresses`** — the list of `PRINCIPLES.md` context numbers the artifact primarily enforces. Lets the
maintainer audit that every principle context has a home, and that no orphan files exist.

---

## 2 · The index

Status reflects the kit's build state. "Path" is relative to the kit root. Items not yet built are listed
so the index is a complete map of the intended kit, not just what exists.

### Shared spine (always loaded)

| id | path | kind | frozen | addresses | status |
|---|---|---|---|---|---|
| core | `docs/CORE.md` | core-doc | true | 1,2,7,8,9 | new |
| principles | `docs/PRINCIPLES.md` | reference-doc | true | 1–9 | new |
| doctrine-index | `docs/DOCTRINE_INDEX.md` | metadata | false | 7 | new |
| migrating | `docs/MIGRATING.md` | reference-doc | false | 1,6,7 | new (per-layout migration procedures for a campaign frozen under an older kit; opens with the in-place upgrade — `skills/new-campaign/scripts/upgrade_campaign.py`, a three-way merge against the campaign's own scaffold templates, and the conflict rules — then one section per change, newest first) |

### General reference docs (on-demand)

| id | path | kind | addresses | status |
|---|---|---|---|---|
| simulation-validation | `docs/SIMULATION_VALIDATION.md` | reference-doc | 2,5 | ported+augmented |
| dimensional-analysis-ref | `docs/reference/dimensional-analysis.md` | reference-doc | 4,5 | new |
| pivoting | `docs/reference/pivoting.md` | reference-doc | 3 | new |
| version-control | `docs/reference/version-control.md` | reference-doc | 7 | new |
| context-economy | `docs/reference/context-economy.md` | reference-doc | 7 | new |
| verification-presets | `docs/reference/verification-presets.md` | reference-doc | 2,7 | new (the single description of `none` · `minimal` · `light` · `heavy` · `intensive`; `new-campaign` presents it verbatim) |
| coordinate-frames | `docs/reference/coordinate-frames.md` | reference-doc | 5 | new |
| hardware-in-the-loop | `docs/reference/hardware-in-the-loop.md` | reference-doc | 4,8,9 | new |
| instrument-contract | `docs/reference/instrument-contract.md` | reference-doc | 4,6,8,9 | new |
| signal-extraction-pitfalls | `docs/reference/signal-extraction-pitfalls.md` | reference-doc | 2,4,5 | new |
| uncertainty-and-error-budgets | `docs/reference/uncertainty-and-error-budgets.md` | reference-doc | 2,5,1 | new |
| systematic-errors | `docs/reference/systematic-errors.md` | reference-doc | 2,4,1 | new |
| noise-and-sensitivity | `docs/reference/noise-and-sensitivity.md` | reference-doc | 5,4,2 | new |
| calibration-and-drift | `docs/reference/calibration-and-drift.md` | reference-doc | 4,5,7 | new |
| ip-and-attribution | `docs/reference/ip-and-attribution.md` | reference-doc | 1,7 | new |
| prompt-surface-audit | `docs/reference/prompt-surface-audit.md` | reference-doc | 9,1 | new |
| expensive-evaluation | `docs/reference/expensive-evaluation.md` | reference-doc | 4,6 | moved out of the campaign template  — situational by its own first sentence ("when evaluations are cheap, ignore this"), and three skills already cited it |
| reporting-standards | — | reference-doc | 1 | absorbed into `report` skill (§standards) |
| latex-toolchain | — | reference-doc | 1 | absorbed into `report` assets README |

### General skills (on-demand; `layer: general`)

| id | path | addresses | status |
|---|---|---|---|
| frame-problem | `skills/frame-problem/SKILL.md` | 5,4,3 | new |
| verify | `skills/verify/SKILL.md` | 2 | new (generalizes v2 verify-finding) |
| simulation-design | `skills/simulation-design/SKILL.md` | 5 | new |
| correctness-suite | `skills/correctness-suite/SKILL.md` | 2,5 | new |
| claim-audit | `skills/claim-audit/SKILL.md` | 2,1 | new (the end-of-campaign capstone: the seven campaign-scale checks; composed by `report` in campaign mode, spawned by the driver at STOP) |
| debug | `skills/debug/SKILL.md` | 3 | new |
| dimensional-analysis | `skills/dimensional-analysis/SKILL.md` | 5,3 | new |
| record-decision | `skills/record-decision/SKILL.md` | 7 | new |
| cite-check | `skills/cite-check/SKILL.md` | 1 | new (lifted from the campaign capstone) |
| report | `skills/report/SKILL.md` | 1 | new |
| derive | `skills/derive/SKILL.md` | 2,5 | new (analytical/symbolic theory) |
| assess-idea | `skills/assess-idea/SKILL.md` | 8,4,9 | new (feasibility and worth triage; front-end cluster) |
| literature-review | `skills/literature-review/SKILL.md` | 1,8 | new (understand the field, with verified citations; front-end cluster) |
| attribute-mechanism | `skills/attribute-mechanism/SKILL.md` | 2,5,3 | new (mechanism attribution: simulate before attributing; composes frame-problem/dimensional-analysis/signal-extraction-pitfalls/debug/verify) |
| assumption-audit | `skills/assumption-audit/SKILL.md` | 3,4 | new (plateau to diagnosis mode-change; solve-don't-confirm and operating-point validity) |

### Project skills (`layer: campaign`)

| id | path | addresses | status |
|---|---|---|---|
| new-project | `skills/new-project/SKILL.md` | 7,8 | new; the default path, not on-demand. Every campaign lives in a project, so `new-campaign` Step 0.1 runs this whenever no project home exists, and it composes new-campaign for the first campaign |
| fork-campaign | `skills/fork-campaign/SKILL.md` | 2,1 | on-demand; new (clean break after invalidation; composes new-campaign + verify) |

### Campaign skills (on-demand; `layer: campaign`)

| id | path | addresses | status |
|---|---|---|---|
| new-campaign | `skills/new-campaign/SKILL.md` | 4,8 | ported+extended (project-aware: reference shared, LINEAGE row, §5 relationship) |
| run-campaign | `skills/run-campaign/SKILL.md` | 9,7 | new: the cockpit around `--supervise` — instruction-twin preflight, background launch, monitor via driver log, relay via `results/inbox/`, halt triage. Never an executor |
| campaign-status | `skills/campaign-status/SKILL.md` | 3,4 | ported+extended (+ project mode: cross-campaign, FROZEN/MUTABLE) |
| campaign-capstone | `skills/report/references/campaign-capstone.md` | 1 | the campaign-specific instructions `report` reads in campaign mode (merged from the former `final-report` skill) |
| handoff | `skills/handoff/SKILL.md` | 7 | new (project-aware: resume from LINEAGE, whole-tree portability) |
| discovery-loop | `skills/discovery-loop/SKILL.md` | 6 | new (archetype G) |
| experiment-design | `skills/experiment-design/SKILL.md` | 4 | new (archetype H) |
| model-selection | `skills/model-selection/SKILL.md` | 2,4 | new (archetype I) |

### Project scaffold (`layer: campaign`; materialized by `new-project` for the project every campaign lives in)

| id | path | kind | addresses | status |
|---|---|---|---|---|
| project-readme | `templates/project/README.md.tmpl` | scaffold-template | 7,8 | the consolidated layout's front door — a very short where-to-find-things map, the directory map's ONLY home |
| project-overview | `templates/project/PROJECT.md.tmpl` | scaffold-template | 5,7 | THE consolidated overview, merging the retired charter / orientation / lineage rows below: §Mission · §Standing constraints (delivered into every spawned prompt by the campaign driver) · system + instrument + equations depth · §Updates from discoveries (verdict-cited pointers) · §Durable decisions · §Lineage (the campaign + session index). Edited by tier (OPEN/GUARDED banners; project CLAUDE.md rule 7) |
| project-claude | `templates/project/CLAUDE.md.tmpl` | scaffold-template | 1,7 | canonical source for the byte-identical project `CLAUDE.md`/`AGENTS.md` twins (always-on rules incl. the edit tiers) |
| project-charter | — | scaffold-template | 7 | absorbed into `PROJECT.md.tmpl` §Mission during project-document consolidation |
| lineage | — | scaffold-template | 7 | absorbed into `PROJECT.md.tmpl` §Lineage during project-document consolidation |
| project-discoveries | — | scaffold-template | 2,7 | retired after the project-layer re-decision: verified findings stay in the campaign that produced them (the ledger's `finding` cells + `results/verdicts/`); the project layer is pointers — §Lineage's verified-findings column + §Updates from discoveries entries citing the verdict by path. A legacy ledger stays hook-gated |
| project-orientation | — | scaffold-template | 5,7 | absorbed into `PROJECT.md.tmpl` during project-document consolidation; its §Standing constraints keeps its name and its delivered-into-every-prompt role, with the driver falling back to a pre-consolidation `PROJECT_ORIENTATION.md` |
| project-engineering-notes | — | scaffold-template | 7 | absorbed into `PROJECT.md.tmpl` §Durable decisions (via the retired orientation doc) |
| shared-physics | — | scaffold-template | 5 | absorbed into `PROJECT.md.tmpl` (§Standing constraints inventory · §The system under study · §Equations and methods) |
| shared-conventions | — | scaffold-template | 5 | absorbed into `PROJECT.md.tmpl` §Standing constraints |
| shared-instrument | — | scaffold-template | 5 | absorbed into `PROJECT.md.tmpl` §The instrument (the SYSTEM.md retirement carries over) |
| shared-dir | — | convention | 7 | retired during project-document consolidation: promoted artifacts live in flat purpose-named project dirs (`scripts/`, `models/`, …) created at first promotion; the promotion mark is the `PROJECT.md` §Lineage promotion line, not a directory name |
| data-readme | `templates/project/data/README.md.tmpl` | scaffold-template | 7 | new (read-only + DATA_PATH pointer convention) |
| reports-readme | `templates/project/reports/README.md.tmpl` | scaffold-template | 1 | new (single project outputs location) |
| session-notes | `templates/project/sessions/NOTES.md.tmpl` | scaffold-template | 7,8 | new (ad-hoc session record at true tier) |

### Campaign scaffold (`layer: campaign`; materialized per campaign)

| id | path | kind | addresses | status |
|---|---|---|---|---|
| campaign-definition | `templates/campaign/campaign.md.tmpl` | scaffold-template | 3,4 | THE campaign definition, compiled into every spawn (minus its append-only §Decision record): mission, the FROZEN metric (revised only as a declared metric epoch; §The ONE metric carries the epoch-vs-fork rule), levers, caps, promotion, the baseline gate and the dataset - the problem's facts and the campaign's constraints, no strategy; every steering line carries its source, the setup's guesses go to the JOURNAL as `[setup inference]` (MIGRATING: the trimmed brief). Split out of the retired single-file charter, which had fused it with the per-role procedure |
| campaign-role-worker | `templates/campaign/roles/worker.md.tmpl` | scaffold-template | 3,5 | the per-experiment procedure: the reads, the loop, the iteration contract, long solves and escalation, the save-set - procedure and record, no strategy (the reasoning is CORE / PRINCIPLES and `docs/reference/pivoting.md`, never restated per spawn). Assembled into every worker spawn. THE contract: every instruction a spawned worker must act on lives here, frozen with the campaign  |
| campaign-role-planner | — | scaffold-template | 5,7 | **retired (MIGRATING: the loop without a queue)**: agents filled its queue with trivial variations instead of asking what the problem needs now. Strategy is the worker's, from the JOURNAL's *What to try next and why*; Getting unstuck and reopening shelved directions moved into `roles/worker.md`, the literature rule into `LITERATURE.md`. Copy in `archive/planner-retired-2026-09/` |
| physics | — | scaffold-template | 5 | merged into the project overview `templates/project/PROJECT.md.tmpl` (project scaffold table above); the campaign-local copy was already retired with standalone mode |
| intake | — | scaffold-template | 8 | retired: the input form is replaced by draft-document mode — `new-campaign` emits a pre-filled draft `campaign.md` the user edits directly, finalized at sign-off ([PROPOSED] tags refused by the validator) |
| campaign-orientation | — | scaffold-template | 7,8 | dissolved: goal / done-criteria / expectations → `templates/campaign/campaign.md.tmpl` §Mission (the expectations went to the JOURNAL's §Live hypotheses, 2026-09: a setup-written first instinct is not evidence); the task hierarchy → the JOURNAL's NEXT pointer + §What to try next and why; field-positioning → `templates/project/PROJECT.md.tmpl` §Where this sits in the field |
| engineering-notes | — | scaffold-template | 7 | absorbed into `templates/campaign/campaign.md.tmpl` (§Known landmines + the append-only §Decision record tail); project-outliving decisions promote to `PROJECT.md` §Durable decisions |
| verification-plan | — | scaffold-template | 2 | absorbed into `templates/campaign/campaign.md.tmpl` §Verification (the campaign-specific checks only; the procedure is `verify`/`correctness-suite`, the V&V&UQ method the plugin's `SIMULATION_VALIDATION.md`) |
| artifacts-protocol | — | protocol | 7 | absorbed into `templates/campaign/roles/worker.md.tmpl` — the save-set, the artifact tiers, the save discipline, and the "Retention plan" subsection |
| campaign-doctrine-snapshot | — | scaffold-template | 1,6 | retired after the provenance re-decision: the snapshot recorded only the spine while skills, reference docs, and the driver also govern behavior — a partial record reading as complete. Replaced by the `{{PHYSKIT_VERSION}}` stamp in `campaign.md`'s header + the logbook top; every release is tagged, so the pin recovers the WHOLE kit. Still never re-synced: the stamp records what governed THIS run |
| campaign-baselines | — | scaffold-template | 2,5 | the campaign's own exp-000 fills were kept; the generic doctrine around them was deleted, the kit already stating it in `verify`, `CORE.md` and `debug`. The remainder folded into `templates/campaign/campaign.md.tmpl`, and since the setup-to-baseline change (2026-09) into `new-campaign` Step 3.5 (exp 000 runs at setup) and the campaign's §Decision record ED-000 (the floor) |
| campaign-dataset | — | scaffold-template | 6,7 | the campaign's own data fills were kept; the never-overwrite-inputs rule moved to `debug`. The remainder folded into `templates/campaign/campaign.md.tmpl` §Dataset / inputs and deleted the file, repairing on the way a sentence fragment the restructure had stranded |
| campaign-claude | `templates/campaign/CLAUDE.md.tmpl` | scaffold-template | 1,2,7,9 | canonical source for byte-identical campaign `CLAUDE.md`/`AGENTS.md` twins: the integrity core, research reflexes, hard gates, and `## Where things live` map. The managed twins are checked before resume/spawn; stamped legacy Claude campaigns are not silently rewritten. The reasoning behind the rules remains the plugin's `CORE.md` at the stamped version |
| promotion-guard | `templates/campaign/scripts/guard_promotion.py.tmpl` | scaffold-template | 2 | PreToolUse hook: blocks a mislabelled promotion write — current-best (`RECOMMENDED.json` `verification_label`) and scoreboard `CONFIRMED`/`NEW BEST` tokens must carry the checks artifact's label, and a refuted result never promotes — and the project ledger (fail-closed, source-campaign suite checked). Renamed from `guard_discoveries.py` when the campaign DISCOVERIES surface dissolved (V6); the ledger's `finding` cells are runner-written + `campaign-status`-audited, not a hook surface |
| promotion-guard-codex-adapter | `templates/campaign/scripts/guard_promotion_codex.py.tmpl` | scaffold-template | 2 | Codex-only perimeter: parses every canonical `apply_patch` operation from documented hook input, resolves paths from hook `cwd`, fails closed for ambiguous protected patches/moves, and delegates protected writes to the unchanged promotion guard |
| loop-heartbeat | `templates/campaign/scripts/loop_heartbeat.py.tmpl` | scaffold-template | 9 | new (Stop hook: refuses an unearned end-of-turn; stop via `results/STOP` or a recorded `stop_request.json`; stands down for driver-spawned workers and, while `results/.driver_alive` is fresh, for attended sessions) |
| supervisor-lock | `templates/campaign/scripts/supervisor_lock.py` | scaffold-template | 7 | cross-platform process-held ownership lock: only one live `--supervise` process may own a campaign; persistent JSON is diagnostics, OS ownership is authoritative |
| hook-settings | `templates/campaign/.claude/settings.json.tmpl` | scaffold-template | 2,9 | new (wires the guard + heartbeat hooks; uses `{{PYTHON_CMD}}`) |
| codex-hook-settings | `templates/campaign/.codex/hooks.json.tmpl` | scaffold-template | 2 | synchronous canonical `apply_patch` PreToolUse wiring for the Codex adapter; project-local trust is an operator prerequisite checked with `/hooks`, not something the campaign validator can infer |
| campaign-experiment | `templates/campaign/scripts/experiment.py.tmpl` | scaffold-template | 4,9 | the campaign's OWN code: the five experiment hooks (`validate_method` · `run_experiment` · `load_target` · `guardrail` · `save_figure`) and the seams (`residual` · `campaign_scoreboard_fields` · `campaign_result_fields` · `campaign_checks` · `campaign_comparand` · `campaign_card_fields` · `baseline_config`; the `ZERO_EVALUATION_MODES` constant) the runner calls through `_exp()` / `_seam()`. The one script a campaign edits; delivered in the worker's brief; created-if-absent and never touched by `upgrade_campaign.py`, which splits a pre-split runner into it by AST |
| campaign-runner | `templates/campaign/scripts/run_campaign.py.tmpl` | scaffold-template | 9,2,4 | KIT-OWNED machinery, replaced wholesale on upgrade (the campaign's code is `experiment.py`): per-experiment gates (prediction/save-set/selftest/correctness) + the `--supervise` driver (degrade-loud halt taxonomy, liveness heartbeat + detached-runner grace, `--preflight`, driver log + rendered worker feed, `results/inbox/` relay, the compiled brief — campaign.md, the role file, the JOURNAL whole, the config template, the ledger's last rows, delivered over stdin and sized at preflight and every spawn; `--record` / `--card` / `--show`, the worker's record surface) |
| loop-knobs | `templates/campaign/configs/loop.json.tmpl` | scaffold-template | 9,4 | per-campaign loop knobs (first-launch harness, per-role Claude/Codex model and effort — `worker` and `verifier`, the latter also governing the end-of-loop claim audit; worker timeouts, `driver.*` — all `driver` keys code-defaulted); user-owned, hot-reloaded by the driver. Blank model/effort inherits the selected harness's configured default. Its `campaign` block is different in kind: `prediction_mode` (what the spend gate accepts) and `noise_model` (spread vs tolerance) with their resolution knobs and the `metric_version`/`data_version` tags are SETUP-TIME declarations every mechanical check branches on — changing one mid-campaign is a real event, and every snapshot manifest stamps them so it is visible. `metric_revision` (the metric-epoch design) is the one knob only an ATTENDED session may set — who may revise the FROZEN metric: `cautious` (default; a revision raises `ESCALATE.md`) or `autonomous` (a verified revision is enacted as a pending epoch). `metric_epochs` is the metric-epoch record itself, keyed by `metric_version` and present only once a campaign has revised its metric (the first epoch is implicit): kind, evidence (a kill verdict against the old metric, or the check that reproduced a discrepancy), expected direction, and STANDING (`pending` until the user ratifies; `ratified` / `rolled-back`; never deleted). Append-only and hook-guarded; the runner binds each epoch's scorer hash in `results/correctness_state.json` on its first experiment and refuses to spend when the scorer's code on disk (normalized: comments, docstrings, formatting do not count) matches no declared epoch — a metric change cannot happen quietly. The driver logs every change it detects |
| unit-queue | — | ledger | 9,7 | **retired (MIGRATING: the loop without a queue)**, with the planner: open ideas live in the JOURNAL's *What to try next and why* (an idea whose unit is recorded leaves the list; its ledger row is its record), and the driver's own counters in `results/driver_state.json` (driver-only, never read by an agent). `upgrade_campaign.py --retire-queue` archives an existing `queue.json` and folds its open `next` entries into the JOURNAL |
| loop-state | `results/driver_state.json` (written by the driver) | ledger | 9 | the driver's counters, nothing else: `accepted_units`, `last_accept_utc`, `accepted`, `pending_verification`, `consecutive_operational_failures`. Atomic writes; no agent reads or writes it |
| prediction-gate-dir | `predictions/` (campaign tree; enforced by the runner's spend gate) | ledger | 2,4 | an a-priori prediction per experiment, written before the solve. WHAT it must carry is the campaign's `prediction_mode` (`configs/loop.json` `campaign`): a numeric range, a direction versus a named experiment, or none with a recorded reason |
| checks-artifact | `results/checks_<NN>.json` (campaign tree; written by the runner, read by `campaign-status`) | ledger | 2,3 | the mechanical checks for one experiment — prediction met, change vs the incumbent, comparability, correctness-suite state, save-set. Also `run` (the measured gates / suite / solve / record timing), and `changes` (what this experiment changed since the last checked unit — code compared as code, config keys, version tags — the record a check starts from; `changes_independent`, since the last independent check, when one is owed); plus `self_check` (the worker's recorded checks, written through `--self-check`), `self_verify`, `verification` (the preset and its resolved rows, `new_best`, the ONE check `owed`, the suite's due/skipped decisions, and the `agent` block after a verifier's verdict), and `label` — the honest verification label every exported claim carries (`unverified` · `self-checked` · `self-verified` · `self-refuted` · `<VERDICT>/peer` · `<VERDICT>/verifier` · `<VERDICT>/audit`). Three-valued: `pass` / `fail` / `unavailable`, the last carrying a `needs` field naming what would make the check real |
| verdicts-dir | `results/verdicts/` (campaign tree; read by `guard_promotion`) | ledger | 2 | verify-skill verdict artifacts: the promotion gate's evidence |
| claude-general | ~~`templates/CLAUDE.general.md`~~ | scaffold-template | 1,2,7 | retired — it duplicated the spine and drifted; `docs/CORE.md` is the single source. Users import it from their project `CLAUDE.md` (`@<kit>/docs/CORE.md`) or copy its body (see `GETTING_STARTED.md` §1) |

### Report assets

| id | path | kind | addresses | status |
|---|---|---|---|---|
| report-skeleton | `skills/report/assets/report_skeleton.tex` | scaffold-template | 1 | new (compiles) |
| report-macros | `skills/report/assets/report-macros.sty` | scaffold-template | 1 | new |
| draft-article | `skills/report/assets/draft_article.tex` | scaffold-template | 1 | new |
| revtex-vendored | `skills/report/assets/{revtex4-2.cls, aps*.rtx, revsymb4-2.sty, ltxgrid.sty, ltxutil.sty, apsrev4-2.bst}` | scaffold-template | 1 | vendored (compiles) |

### Archetypes (campaign reference)

| id | path | addresses | status |
|---|---|---|---|
| archetype-cheatsheet | `templates/ARCHETYPE_CHEATSHEET.md` | 4,6 | extended (added G,H,I) |
| archetype-G-discovery | (cheatsheet + `discovery-loop` skill) | 6 | new |
| archetype-H-active-design | (cheatsheet + `experiment-design` skill) | 4 | new |
| archetype-I-model-selection | (cheatsheet + `model-selection` skill) | 2,4 | new |

---

## 3 · Coverage audit

Every principle context should have at least one `frozen` or always-loaded home plus on-demand depth:

| Ctx | Home(s) |
|---|---|
| 1 Integrity | CORE + PRINCIPLES (frozen); `report`, `cite-check`, reporting-standards, `ip-and-attribution`, `prompt-surface-audit` |
| 2 Verification | CORE + PRINCIPLES (frozen); `verify`, `correctness-suite`, SIMULATION_VALIDATION, `signal-extraction-pitfalls`, `attribute-mechanism`, `uncertainty-and-error-budgets`, `systematic-errors`, `noise-and-sensitivity` |
| 3 Problem-solving | PRINCIPLES; `debug`, `pivoting`, `assumption-audit`, campaign-status |
| 4 Experimental design | PRINCIPLES; campaign.md (the levers, caps, the a-priori bound), roles/worker.md (the loop), `new-campaign`, archetypes, `hardware-in-the-loop`, `systematic-errors`, `noise-and-sensitivity`, `calibration-and-drift`, `assumption-audit` |
| 5 Physics & simulation | PRINCIPLES; `frame-problem`, `simulation-design`, SIMULATION_VALIDATION, PHYSICS, `attribute-mechanism`, `uncertainty-and-error-budgets`, `noise-and-sensitivity`, `calibration-and-drift` |
| 6 Discovery-loop | PRINCIPLES; `discovery-loop`, archetype G (cheatsheet), expensive-evaluation |
| 7 Records & reproducibility | CORE (context economy: doctrine, unfrozen); this index, `handoff`, `record-decision`, scaffold, `run-campaign` (the driver log + `driver_state.json` as the run's process record) |
| 8 Autonomy & collaboration | CORE (frozen-adjacent: clarify-the-goal); `new-campaign`, frame-problem |
| 9 Operating unattended | CORE (Running unattended) + PRINCIPLES §9; `roles/worker.md` (the STOP judgement), `campaign.md` (promotion), `CLAUDE.md` HARD GATE 5 (how the loop ends), `run-campaign` (the cockpit around `--supervise`), `campaign-status`, `expensive-evaluation`, `hardware-in-the-loop` (archetype E), `campaign.md` §Known landmines, the CLAUDE.md gates + the promotion and loop-heartbeat hooks, `prompt-surface-audit` |

Open gaps: none. Every artifact in the index is built, so remaining work is testing and iteration rather
than net-new artifacts. Context 9 overlaps 7–8 by design; its organization relative to those contexts is
flagged for revisit.

## Changelog
- **v0.8 (unreleased)** — the project and campaign `CLAUDE.md.tmpl` rows are now explicitly the sole
  sources for byte-identical Claude/Codex instruction twins; `run-campaign` indexes their fail-closed
  resume/spawn consistency gate.
- **v0.7 (unreleased)** — re-classed `new-project` from an on-demand Project skill to the default path,
  and the project scaffold as the home every campaign has. The standalone bare-campaign mode is retired,
  so `new-campaign` Step 0.1 finds the project home or runs `new-project` to create it.
- **v0.6** — added `assumption-audit` (skills-table row plus Ctx 3/4 coverage: the plateau-to-diagnosis
  mode-change, solve-don't-confirm, operating-point validity) and `prompt-surface-audit` (reference-doc
  row plus Ctx 9/1 coverage: rendered-context auditing for multi-agent loops). PRINCIPLES Ctx 9 gained
  the twin bullet (v1.9); CORE's plateau line gained the second species.
- **v0.5** — added `ip-and-attribution`, the cite-and-adapt-never-reproduce guardrail for capability
  work: reference-doc row plus Ctx 1 coverage. It is the constraint doc for the capability library;
  its posture is provisional pending formal confirmation.
- **v0.4** — indexed the measurement-science reference cluster (`uncertainty-and-error-budgets`,
  `systematic-errors`, `noise-and-sensitivity`, `calibration-and-drift`): added their rows plus Ctx 2/4/5
  coverage. Context-numbered `addresses` remap with the nine-pillar migration.
- **v0.3** — indexed the mechanism-attribution and hardware-loop additions: added the
  `attribute-mechanism` skills-table row, whose SKILL.md had shipped unindexed, and wired
  `attribute-mechanism`, `signal-extraction-pitfalls`, and `hardware-in-the-loop` into the §3 coverage
  audit (Ctx 2/4/5/9). The two reference docs were already row-indexed. No principle content changed.
- **v0.2** — added Context 9 · Operating unattended to the coverage audit (home: CORE "Running
  unattended" + PRINCIPLES §9; enforced via `campaign.md` + `roles/*.md` / `campaign-status` / `expensive-evaluation` /
  ENGINEERING_NOTES landmines / the CLAUDE.md gates). Bumped CORE `addresses` to `1,2,7,8,9` and
  PRINCIPLES to `1–9`.
- **v0.1** — initial index + metadata schema. Enumerates the full intended kit, built and planned.
