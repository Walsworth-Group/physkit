# Migrating a campaign to a newer kit layout

Campaigns are **frozen with their doctrine**: a finished campaign wants the exact rules it ran under, so
nothing here runs automatically and nothing rewrites a campaign in place without being asked. Migrate only
a campaign you intend to keep working in.

Each section is a short procedure an agent can follow end to end. Newest layout first. If you are several
versions behind, work upward from the oldest section that matches your tree.

---

> **Reading the commands below on Windows:** `python` is the Microsoft Store alias stub on a stock
> install. It prints "Python was not found" and exits 49 without running the script. Use `py -3` there;
> `python` is correct on macOS and Linux. Every command in this file works either way with that
> substitution.

## To a kit without the principles doc (`docs/PRINCIPLES.md`; kit ≥ v0.12.2, ADR-0034)

Nothing to do for an existing campaign. Its `CLAUDE.md` may name `docs/PRINCIPLES.md` as the reasoning behind
its rules; that line refers to the kit version stamped in `campaign.md`, where the file exists. An upgraded
campaign gets the new line from the template. The rules themselves are unchanged: they are stated in
`docs/CORE.md` and the skills.

## To reshapeable templates — `[[KEEP]]` tags mark what code reads (kit ≥ v0.12.1, ADR-0033)

Nothing to do for an existing campaign. The templates now carry `[[KEEP — …]]` tag lines that tell a setup
agent what must survive a reshaped scaffold; `upgrade_campaign.py` strips them when it merges or creates a file
from a template, and `validate_campaign.py` refuses a leftover one. A hand-copied template section must have
its tag line deleted.

## To the plausible range — the per-experiment prediction is retired; the range is set once at setup (kit ≥ v0.12.1)

**What changed.** Workers no longer write `predictions/<exp>.json`, and the runner no longer refuses to
spend without one: the prediction gate, `prediction_mode` / `prediction_mode_reason` (range · direction ·
none) and the logbook's **Predicted** line are gone. A-priori magnitudes were often wrong, cost time, and
deterred units the worker did not yet understand. What stays is the check the range was for: the
metric's **plausible range**, fixed once at setup and signed off by the user, lives in the FROZEN
`scripts/metric.py` as `PLAUSIBILITY_BOUNDS` (a sensible default: the perfect score at one end, a trivial
predictor's score on the evaluation data at the other). A score outside it is FLAGGED — a probable
implementation error in the scorer, the data or the pipeline — recorded, never blocking:
`results/checks_<NN>.json` `plausible_range` (formerly `hard_bounds`), the logbook's **Plausible range**
line (formerly **Expected vs found**), the ledger's `plausible` cell (formerly `expected_vs_found`). At
`minimal` and `light`, the self-verify trigger is now a score outside the plausible range, so it fires
rarely; the other route to a check is a contest. A zero-evaluation unit's commitment moves into its
config: `"_deliverable": "<what will exist on disk afterwards that does not now>"`, refused by the
deliverable gate when absent and recorded as `deliverable_named`. The `--self-check` artifact field
`apriori` is now `plausible`.

**Procedure.**
1. Run `upgrade_campaign.py <campaign> --preset <its preset>` to replace the runner and merge the role
   and contract text.
2. **Set or confirm the plausible range with the user.** Open `scripts/metric.py`: if `PLAUSIBILITY_BOUNDS`
   is absent or `None`, the check reports `unavailable` on every unit. Propose a range (compute the trivial
   end on the evaluation data; do not guess), get the user's sign-off, and state it in `campaign.md` §The
   ONE metric as one **Plausible range** line with its basis, replacing any **Hard bounds** / **A-priori
   range** lines. `metric.py` is FROZEN core: the edit changes the core hash and invalidates the recorded
   correctness-suite green, which is intended. A range written as "true by construction" under the old
   rule is still valid; widen nothing to fit a result you have already seen.
3. Give every zero-evaluation unit config (a `mode` in `ZERO_EVALUATION_MODES`) that will still run a
   `_deliverable`.
4. Nothing else is required. `predictions/` can stay as history (the runner ignores it);
   `prediction_mode` / `prediction_mode_reason` in `configs/loop.json` are ignored and may be deleted.
   Renaming the ledger header `expected_vs_found` → `plausible` is optional: the runner fills both names.

## To contested gate outcomes — a worker's dispute goes to an independent verifier (kit ≥ v0.12.1)

**What changed.** A worker that disagrees with the gate outcome recorded for its own result no longer
sets it aside: it files a `contest` in the record file (`{claim, disputes: pass|refusal, gate, evidence}`),
the driver spawns an independent, blinded verifier for the charge under every preset, the promotion guard
refuses a pointer write while the contest is pending, and the recorded outcome stands unless the verdict
is REFUTED — a contested pass that stands is promoted by the driver with the verdict's label. The runner,
the guard and the Codex verifier module carry the machinery; the roles and the contract carry the rule.

**Procedure.** Run `upgrade_campaign.py <campaign> --preset <its preset>`: the runner, the Codex verifier
and the guard are replaced or merged; `roles/worker.md`, `campaign.md` and `CLAUDE.md` merge the new
text. Two files the upgrade does not rewrite when present: `roles/verifier.md` and `roles/REFERENCE.md`
(created only when absent). The contest instructions reach the verifier through its VALUES regardless, so
nothing breaks; to carry the rule's text too, copy the **A contest** paragraph from the kit's
`templates/campaign/roles/verifier.md.tmpl` and the contest bullet from `roles/REFERENCE.md.tmpl` §Independent
verification into the campaign's copies. Nothing in `results/` changes; `results/contests/` is created by
the first contest.

## To one check per result — five presets, `heavy`, the survivor check (kit ≥ v0.12.0, ADR-0031)

**What changed.** `verify.preset` is one of `none` · `minimal` (the default) · `light` · `heavy` ·
`intensive` (`docs/reference/verification-presets.md`). Each result gets at most one check, the strongest
its preset owes it: a self-verify in its own worker's session, a peer check by the next worker, or a
driver-spawned verifier; a new best's independent check waits until the next unit has not beaten it.
Review versus re-execution is gone (no `review` / `re_execution` rows, no eligibility rule, no verdict
`mode`; a verdict carries `"kind": "peer" | "verifier"`). Labels: `unverified` · `self-checked` ·
`self-verified` · `self-refuted` · `<VERDICT>/peer` · `<VERDICT>/verifier` · `<VERDICT>/audit`; an old
`/review` or `/re-execution` reads as `/verifier`. `RECOMMENDED.json` follows the true best at once with
its `verification_label`; the guard checks that label, a refuted result never promotes, and the driver
rolls the pointer back on a refutation. The claim audit runs under every preset but `none`, re-checks the
final best, and has no `panel` level; `intensive` has no different-model refuter and no per-block
batching. Workers never spawn verification agents.

**What breaks.** Preflight refuses `verify.preset: "moderate"` (renamed `heavy`, and not the same table:
`heavy` self-verifies every other result and spawns a verifier for each best that survives) and any
`campaign.verification` key (retired; no `per-block` / `promotion-only` mapping remains). `light` changed
meaning: a new best's independent check is the next worker's peer check once it survives, not a spawned
review of every promotion; choose `heavy` for a spawned verifier.

**Procedure.** There is no migration machinery: no campaign ran the ADR-0021 presets for its result. Set
`verify.preset` to one of the five names and delete `campaign.verification` / `verification_reason`;
`upgrade_campaign.py --preset <name>` does both and brings in the runner, the guard and `roles/*.md` (the
worker role has one section per preset, and the brief delivers only yours). Results recorded earlier keep
their labels; one whose checks artifact has no `verification.owed` keeps the established verdict rule at
the guard.

## To runner-placed side documents and the artifact digest (kit ≥ v0.12.0)

**What changed.** A worker's record file takes two more keys - `landmine` (a row of campaign.md §Known
landmines, sourced to the unit) and `discovery` (PROJECT.md §Updates from discoveries, only with a
CONFIRMED verdict the guard's own checks accept); the brief carries the shape of the last two units'
artifacts; `--record` ends with the save-set; `--digest <exp>` is new. A gotcha belongs in the JOURNAL's
*Traps and tooling*, no longer in PROJECT.md by hand.

**Procedure.** `upgrade_campaign.py` brings in the runner and `roles/*.md`; nothing else has to change.
A campaign whose `campaign.md` has no §Known landmines table refuses the `landmine` key until one is added
(the kit's campaign template shows it); a project file without §Updates from discoveries refuses the
`discovery` key the same way.

## To isolated campaign spawns — no auto-memory, no MCP servers (kit ≥ v0.12.0)

**What changed.** Every agent the driver spawns (workers, verifiers, the capstone, the preflight smoke
spawn) now runs with two more defaults, both only on the default claude CLI:
- **Auto-memory off.** The harness keeps a memory folder per working directory
  (`~/.claude/projects/<dir>/memory/`) and loads it into every later session there, so one worker could
  leave notes for the next that appear in no record of the campaign — not the JOURNAL, the ledger or a
  snapshot — and exist on one machine only. The driver's `--settings` now also carries
  `"autoMemoryEnabled": false`. A note worth passing on goes in the JOURNAL's *Traps and tooling*.
- **No MCP servers.** The driver passes `--strict-mcp-config`, so a spawn loads no MCP server: not the
  user's, not a project `.mcp.json`, not the claude.ai account's connectors. A spawn runs unattended,
  and the connectors attach nondeterministically (one probe run in three got two of them, ~8k tokens).

An interactive session opened in the campaign directory is untouched by both.

**Procedure.** Nothing in a campaign tree has to change; `upgrade_campaign.py` brings in the runner that
carries the defaults. If the campaign's workers kept notes in the auto-memory folder, read them once and
move anything still true into the JOURNAL's *Traps and tooling* (or PROJECT.md's *Environment gotchas*)
before the next launch. To change either default, `configs/loop.json` `driver`:
- `auto_memory`: `off` (the default, and what an older `loop.json` without the key gets) or `on`; env
  override `AUTORESEARCH_AUTO_MEMORY`.
- `mcp_servers`: `none` (the default), `inherit` (whatever the harness would load), or the path of an MCP
  config file relative to the campaign — exactly those servers, e.g. an instrument driven through MCP;
  env override `AUTORESEARCH_MCP_SERVERS`. Preflight refuses a path that is not a file.

## To the trimmed brief — the contract is facts and constraints, steering carries its source (kit ≥ v0.12.0)

**What changed.** `roles/worker.md` lost its strategy sections (Decision-making guidelines, Getting
unstuck, Before writing off or accepting, Rigor, After the run, When something looks unphysical) and
kept every mechanical rule; `campaign.md` lost §Operating stance and its advice paragraphs, folded
§Bound expectations into §The ONE metric, and gained a rule: every steering line (a landmine, a check to
guard against, a range) carries its source, and the landmine table has a fourth column, `source`, that
the validator requires. What the setup could only infer is written into the opening JOURNAL marked
`[setup inference]`. `CLAUDE.md`'s gates are shorter, not weaker. The reasoning is ADR-0026.

**Migration.** Nothing breaks: a campaign is frozen with the doctrine it was scaffolded under, and the
runner reads none of the removed text. `upgrade_campaign.py` three-way-merges the three files if you
want the trimmed versions in a running campaign; the removed placeholders need no fill. To adopt the
source rule on an existing `campaign.md`: add the `source` column to §Known landmines and, for each
row, either name where it came from or move it to the JOURNAL as `[setup inference]` - the validator
skips a three-column table, so an untouched campaign stays valid. A campaign scaffolded fresh (a
sibling for the performance test) gets all of it.

## To the seams of the first field split — zero-evaluation units, the payload at the seams, non-comparand rows (kit ≥ v0.12.0)

**What changed.** Seams `experiment.py` lacked, found when photophysics10's `ledger` units stopped
recording after the split (its deliverable arm of the prediction gate, its scoring bypass, its
`theta`-keyed comparand rule and its payload merge were edits to kit-owned functions the split could not
carry): `ZERO_EVALUATION_MODES`; `prediction=` at `campaign_scoreboard_fields` / `campaign_checks`;
`campaign_result_fields`; `campaign_comparand` and a payload `comparand: false`. The release notes have the
detail; the seam file's header documents each.

**Migration.** `upgrade_campaign.py` brings in the runner. Then, only if your campaign had such edits:
1. A mode that records no score: add `ZERO_EVALUATION_MODES = {"<mode>"}` to `experiment.py`; make
   `validate_method` refuse the mode to any config that fits, scores or spends; have `save_figure`
   dispatch a card for it (the payload carries `is_evaluation: False`); its `run_experiment` branch is
   its record gate (the deliverable on disk before the row). Its prediction file names
   `{"predicted": {"deliverable": "..."}}` and no numeric range.
2. Columns computed from the fit: take `prediction` in `campaign_scoreboard_fields` instead of reading
   `result_<NN>.json` back. The payload keys the result JSON used to carry: return them from
   `campaign_result_fields` (photophysics10: every non-private key except the raw arrays, `theta`
   normalised to a list).
3. A threshold row: return `comparand: False` in its payload; for rows already recorded, define
   `campaign_comparand(result)` (photophysics10: `bool(result.get("theta"))`).
4. `tests/correctness_checks.py`: a check that drives the record path redirects the paths of BOTH
   modules (`run_campaign.IMAGES` and `experiment.IMAGES`), takes hooks and constants from
   `experiment` and the record path from `run_campaign`. A check that pins a ledger column by name:
   the narrative cell is `note` since the bounded record (`notes` before it).

## To setup-run baselines and no expectations section (kit ≥ v0.12.0)

**What changed.** New campaigns run experiment 000 in the setup session (the floor is on the ledger at
handoff; `campaign.md` §Decision record ED-000 records it) and carry no §Loosely-held expectations: the
hypotheses live in the JOURNAL's §Live hypotheses as questions. **An existing campaign needs no step**:
its exp 000 has run, and the in-place upgrade merges `campaign.md` three-way - accept the removal of
§Loosely-held expectations (move anything still live into the JOURNAL's §Live hypotheses, as a question)
and of §Baseline gate (the floor is your exp000 row; copy the methods and criteria into an ED-000 entry
if you want them on the record). `campaign-status` now reads the hypotheses from the JOURNAL.

---

## To the contract in the role file (kit ≥ v0.12.0)

**What changed.** The runner no longer carries the worker's, the verifier's or the capstone's
instructions: they live in `roles/worker.md`, `roles/verifier.md` and `roles/capstone.md`, delivered
first in every brief, frozen with the campaign, yours to read and edit. The runner's own prompt is one
opening line (plus the per-spawn values for the verifier and the capstone). Reference material the
worker needs rarely - the metric-epoch procedure, the verification presets, the
reproducibility bundle, quicker-check and extra visualization - lives in `roles/REFERENCE.md`, which no
spawn reads whole; the contract names the section to open. `scripts/experiment.py` is not delivered any
more (open it by line range or grep when a unit changes code). `campaign.md` §Caps is §Targets - the
maxima were never checked; the enforced number is the disk floor in `loop.json`. The retention plan's
reasoning belongs in `campaign.md` §Decision record (the template has an entry for it).

**The step.** `upgrade_campaign.py` (the in-place upgrade below) merges `roles/worker.md` three-way
against the template it was scaffolded from - expect conflicts where your campaign edited the role, and
resolve them knowing that the new file is ONE copy of everything (a rule the old role stated twice is
stated once now). It creates `roles/verifier.md`, `roles/capstone.md` and `roles/REFERENCE.md` from the
templates with the values it can recover; a placeholder it cannot recover is left literal and named in
the upgrade log - copy the rendered text from your old `roles/worker.md` backup beside it. Preflight
requires all four files. A `roles/worker.md` over 24 KB gets a preflight WARN, never a clip.

**Why.** The scaffolding audit (`synthesis/SCAFFOLDING_AUDIT_2026-09.md`) measured a field worker spawn
at ≈166 KB before its first tool call, one third of it duplicated between the runner's prompt string
and the role file, and a prompt string the upgrade rewrote in place as the one instruction surface
that broke the freeze-and-stamp rule. Niko's call (decision 1): the researcher's tree holds the record
of exactly what an agent was told.

---

## To the loop without a queue (kit ≥ v0.12.0)

> **Since the first cut of this section:** the driver's counters live in `results/driver_state.json`,
> not `results/loop_state.json` (that name is the Stop hook's, and the two collided). A campaign that ran
> the queueless driver before the rename: delete the driver's keys (`accepted_units`, `accepted`,
> `pending_verification`, `consecutive_operational_failures`, `last_accept_utc`) from
> `results/loop_state.json` by hand, and relaunch - the driver re-seeds from the archived queue if one
> is there, else starts its counters fresh. And **check `driver.permission_mode`**: the current CLI
> denies a headless `auto` spawn its Write and Bash, and the driver now halts on the first denied spawn
> naming the fix (`bypassPermissions`).

**What changed.** The planner agent and `results/queue.json` are retired (ADR-0024). Niko's tests found
the queue actively negative: agents filled it with trivial variations of the last unit instead of asking
what the problem needs now, and a setup-written direction sat at the head of it for ~20 units while the
campaign's actual question never ran. The driver now spawns a fresh worker per unit with **no unit
assigned**; the worker chooses the one experiment the campaign needs now from the JOURNAL's `**NEXT:**`
line and *What to try next and why*, the ledger's last rows and the previous card, names it
`exp<NN>_<slug>`, writes its config from the template the brief delivers, predicts, runs, records, writes
the JOURNAL anew, and exits. One unit per spawn.

What that removes from your tree and your vocabulary: `results/queue.json` and `results/queue_drop/`,
`--record --propose` / `--decline`, `roles/planner.md`, the planner cadence, the plateau knobs and
`queue.max_outstanding_units`, and unit `block`s. What replaces them:

| Was | Is now |
|---|---|
| a queued unit / a proposal | a ranked entry under the JOURNAL's *What to try next and why*; an idea whose unit is recorded leaves the list, and its ledger row is its record |
| `queue.json` accept counters, `pending_verification` | `results/driver_state.json` — the driver's counters only, driver-written, read by no agent |
| a verifier proposal through `queue_drop/` | the verdict artifact's `follow_up` field on a REFUTED or INCONCLUSIVE verdict; the driver relays it to the next worker as `results/inbox/verifier_<exp>.md` |
| the queue running empty = the loop is done | the worker writes `**NEXT:** STOP - <why>` as the JOURNAL's NEXT line; the driver runs the claim audit, then halts with that reason as a stopping decision for you |
| `loop.json` `planner` block (model / effort) | `loop.json` `verifier` block, which also governs the end-of-loop claim audit. An older file's `planner` block is still honoured by the runner, so this one is optional |

**The step.** From the campaign directory, after the in-place upgrade below:

```bash
python "<kit>/skills/new-campaign/scripts/upgrade_campaign.py" . --retire-queue
```

It archives `results/queue.json` to `results/queue_archive/`, folds its open `next` ideas into
`results/JOURNAL.md` under a *migrated from the retired queue* heading inside *What to try next and why*
(with their rationales, so nothing live is lost), and moves `roles/planner.md` and `results/queue_drop/`
into the archive beside it. Nothing is deleted. Shelved and declined entries stay in the archived file as
the record of what was tried and why it was set aside; fold back by hand only what you still want run.

**Afterwards.** Read the JOURNAL's *What to try next and why* yourself before relaunching: it is now the
only thing steering the campaign, and a migrated list is only as good as the queue it came from. Prune
what the evidence has since killed. A campaign whose JOURNAL leaves that section empty will have its
next worker choose from the ledger alone, which is legitimate but blind; a campaign you believe is
finished should say so through a worker's `NEXT: STOP`, not through an empty list.

---

## Upgrading an existing campaign in place — `upgrade_campaign.py` (kit ≥ v0.11.0, 2026-09-03)

Re-scaffolding a running campaign re-answers an interview whose answers already sit in the rendered
files, and it is expensive. The alternative is an in-place upgrade: every kit-owned file in a campaign
was rendered from a template at the kit commit stamped in `campaign.md` ("Scaffolded by physkit
vX.Y.Z (<hash>, <date>)"), so each can be **three-way merged** — base = the template the campaign was
rendered from, ours = the campaign's file with its own edits, theirs = the current template. Campaign
edits survive; a conflict appears only where both sides changed the same lines. Files the old kit did
not ship are copied in. The FROZEN scorer, the data, `results/`, and `configs/exp*.json` are never
touched.

**Run it** from the campaign directory, with the kit checked out (the stamped commit must be reachable
so the script can fetch the base templates; `--base-dir` points at an older plugin cache instead):

```bash
python "<kit>/skills/new-campaign/scripts/upgrade_campaign.py" . --preset light --base-git <kit repo>[@<ref>]
```

`--preset` is required (there is no default for a campaign that already has a history: `light` is what
a new campaign would get; `docs/reference/verification-presets.md`).
`--dry-run` prints the merge outcome without writing. Every file changed gets a
`<file>.pre_upgrade_<UTC>` backup beside it; the log lands in `results/diagnostics/upgrade_<UTC>.md`;
`campaign.md` and the logbook gain an "Upgraded in place to physkit …" provenance line under the
scaffold stamp. The script also edits `configs/loop.json` (`verify.preset`; `campaign.reproducible`;
`driver.verifier_retries`; the legacy `campaign.verification` / `verification_reason` removed; a
`full_reproduction_threshold_s` removed), adds `_metric_version` to
`RECOMMENDED.json`, and materializes the project-level `AGENTS.md` twin when the project has one
unmarked `CLAUDE.md` and no `AGENTS.md`. Exit 0: merged clean and validated. Exit 2: conflicts left.
Exit 3: the validator failed.

**Resolving conflicts.** The markers carry three sides — `campaign:<file>`, `scaffold-template`, and
`current-template`. Placeholder-only hunks (a line that still reads `{{X}}` in both templates) are
resolved by the script from the campaign's own rendered value. What remains is a real edit on both
sides, and five rules cover every case a v0.10 campaign produced:

1. **Both sides added, at the same spot** (a campaign import beside new kit imports; a campaign helper
   beside a new kit block): keep both, the campaign's first.
2. **Both sides changed the same line** (a logbook format string the campaign rewrote and the kit
   extended): take the template's new structure and the campaign's values — a metric name, a project
   file path, an interpreter path.
3. **The campaign deleted an optional block the template rewrote** (a `[[OPTIONAL …]]` section the
   scaffolder removed as not applicable): the deletion stands; drop the template's new marker lines.
4. **A call signature both sides extended** (`write_checks(…, ledger=…)` beside the kit's
   `timing=…`): the union of the arguments, in both the `def` and every call.
5. **A branch the campaign added where the kit changed the body** (a zero-evaluation branch around
   the checks dict): keep the branch, and update the shared lines inside it to the kit's new
   signatures (`_incumbent(priors, props)`, the `epoch` check, `check_comparability(props, inc, priors)`).

Then remove the markers, `python -m py_compile` the two Python files, and run
`python scripts/sync_agent_instructions.py --scope campaign --from claude --write` (the campaign twin the
script skipped while conflicts stood).

**Declare the suite's rows.** The merge lands the `@check` decorator, the four contract stubs, and the
template's `machinery` declarations on the checks it ships; the campaign's own checks arrive undeclared,
which makes them `invariants` — run every unit, metered. Preflight runs the whole suite once, timed, and
refuses an over-budget every-set by name, each with its row. On photophysics10's sixteen-check suite
(206 s whole, against a 150 s budget) that line named `convergence` (164 s) and
`conservation_invariants` (29 s). Declaring them `@check(row="machinery", depends_on=("scripts/<engine>.py",))`
is the fix under `light` and `heavy`, where machinery runs at setup or on code change: the every-set
fell to 34 s. Under `intensive` the machinery row fires every unit too, so the declaration alone changes
nothing and preflight says so — choose `heavy`, make the check cheaper, or declare a per-result
check `gates`. Fill the contract checks or record `tests/CORRECTNESS_NA.md`.

**Finish** with the validator and preflight, the latter under the campaign's own interpreter (the one
`.claude/settings.json` names, since the campaign's engine imports live there):

```bash
python "<kit>/skills/new-campaign/scripts/validate_campaign.py" .
```

```bash
<campaign python> scripts/run_campaign.py --preflight
```

Read the new HARD GATE 1 in the campaign `CLAUDE.md` and the presets doc before relaunching: each result
gets one check, and the current-best pointer carries its label. Results recorded before the upgrade keep
the established promotion rule (their checks artifacts predate the presets).

## To `report` as the campaign capstone — `final-report` merged away (kit ≥ v0.11.1, 2026-09-16)

**What changed.** The `final-report` skill is gone. Its campaign-specific instructions are
`skills/report/references/campaign-capstone.md`, which `report` reads when its *Where* dial says *in a
campaign*. Nothing in a campaign tree changes; the driver's `capstone` spawn was always the claim audit,
not this skill.

**Procedure.** Where you typed `/physkit:final-report`, type `/physkit:report` from the campaign
directory; it detects the campaign and reads the reference. A campaign `CLAUDE.md` rendered from an older
spine may still say `campaigns: /physkit:final-report` in its report line; that line is a frozen
snapshot and can stay, or be re-rendered by `upgrade_campaign.py`.

## To the name-only skill listing in a campaign (kit ≥ v0.11.1, 2026-09-16)

**What changed.** Every spawn in a campaign carried the plugin's skill descriptions in its system
prompt (≈ 7k tokens on a 1M-context model, every turn) although the campaign's files name each skill
to use. The driver now passes `--settings {"skillListingBudgetFraction":0.0001}` on every spawn it
launches (workers, planners, verifiers, the capstone, the preflight smoke spawn), which lists every
skill by name only inside the spawn; name-only skills are invoked exactly as before. This hides
**every** installed plugin's descriptions from the spawn, not only physkit's: a campaign that wants a
spawn routed to a third-party skill from its description names that skill in `campaign.md` or a role
file, or turns the behaviour off. An interactive session opened in the campaign directory still sees
the descriptions. Measured on one worker spawn of a field campaign: turn-0 context 156,717 → 149,492
tokens.

**Procedure.** Nothing in a campaign tree has to change. The knob is `configs/loop.json` `driver`
`skill_listing`: `names` (the default, and what an older `loop.json` without the key gets) or `full`
(the harness's own listing); env override `AUTORESEARCH_SKILL_LISTING`. The flag itself lives in
`scripts/run_campaign.py`, which `upgrade_campaign.py` replaces wholesale.

## To the bounded record — `--record`, `--card`, the ledger's narrative cells, the JOURNAL as working memory (kit ≥ v0.11.1, 2026-09-11)

**What changed.** The worker's record is placed by the runner, never spliced by hand: `python
scripts/run_campaign.py --record <exp> --analysis "<paragraph>" --next "<line>" [--ledger-note "<≤200
chars>"] [--finding "<one line citing results/verdicts/<id>.json>"] [--decline "<why>"] [--propose
<file>]` (validated, idempotent). Every `--config` run ends with the result card (`--card <exp>` reprints
it); `--show <exp>` prints one logbook entry. `results/scoreboard.tsv` has narrative columns the runner
writes: `what` (was `description`), `expected_vs_found`, `verified`, `note` (was `notes`; capped), `finding`.
The brief delivers the ledger's last rows as a projection (`== LEDGER (last rows) ==`) and the JOURNAL
whole (`== JOURNAL ==`, clipped at 12 KB). `results/JOURNAL.md` is now working memory with fixed sections
(NEXT · Where we stand · Live hypotheses · What to try next and why · Traps and tooling · Open questions ·
Anything else) that the worker brings up to date each unit; the driver archives every version to
`results/journal_archive/` and refuses a unit whose JOURNAL was not written anew after its spawn. The
driver removes the working file after building the brief (which carries the previous JOURNAL), so the
worker writes the new one as a fresh file in one Write; a worker that leaves none gets the archive
restored. The whole record is one file, `results/record_<NN>.json` (self_check, analysis, next,
ledger_note, finding, propose/decline), and one command, `--record <exp> --from-file`; the card ends
every run with the comparisons against the incumbent and the previous unit. The runner no longer appends
a JOURNAL row; the verifier writes no JOURNAL line; the capstone records settled claims with `--record
<exp> --finding`.

**Migration.** `upgrade_campaign.py` does both in one pass, with backups: the ledger columns (rename,
insert, pad; a `notes` essay over 200 chars is trimmed with a `[trimmed]` marker - the full text is the
logbook entry) and the JOURNAL restructure (the old file archived whole in `results/journal_archive/`;
§Findings / §Open threads / §Strategy notes carried under "migrated from the previous JOURNAL" headings
for you to trim; every verdict-cited Findings line also written into the `finding` cell of the experiment
it names). Then trim the migrated blocks: the file is delivered whole every spawn. An un-upgraded
campaign keeps working - the runner writes rows under either spelling and refuses a `--ledger-note` /
`--finding` only when the column is absent (naming the upgrade).

## To the driver fixes — usage-limit backoff, the outstanding-units cap, the planner's queue schema (kit ≥ v0.11.1, 2026-09-09)

**What changed.** (1) A spawn the harness kills in its first turn within seconds (`ok=False turns=1
dur=1s`), or whose result names a usage/rate limit, is the model's usage limit, not the unit: the driver
now waits (doubling from 5 min, up to `driver.limit_wait_max_min`, default 90) and relaunches the same
prompt, spending no retry and never counting toward SYSTEMIC; `0` restores the old behaviour. (2)
`queue.max_outstanding_units` — declared in `loop.json` since v0.10 and enforced nowhere — is now
enforced at the drop merge: agent proposals beyond it wait on the shelf as `kind: "capped"` until the
planner revives, reorders or prunes them; absent = uncapped, `1` = one proposal at a time. (3) The
planner prompt shows the literal queue-entry schema, so an empty first queue cannot produce a
`stem`-keyed entry and a `KeyError: 'config'` crash. (4) Every promotion-guard denial is logged to
`results/guard_denials.log`; `campaign-status` reports the count. Evidence: the colleague records
(`case-studies/time_records_cross-read_2026-09-07.md` §3: three of three halts in one run were
one-second deaths counted as failures; the Opus run's launch-1 crash).

**Migration.** `upgrade_campaign.py` brings in the runner (kit-owned since the split) and the guard;
`loop.json` gains `driver.limit_wait_max_min` (add it, or the code default 90 applies). Check
`queue.max_outstanding_units` in your `loop.json`: a pre-v0.11.1 scaffold set it to the planner cadence,
which now binds — lower it to 1 (the new-campaign default) if you want one proposal at a time.

## To the split runner — the campaign's code in `scripts/experiment.py` (kit ≥ v0.11.1, 2026-09-09)

**What changed.** The five experiment hooks (`validate_method`, `run_experiment`, `load_target`,
`guardrail`, `save_figure`) left `scripts/run_campaign.py` for a new campaign-owned
`scripts/experiment.py`, with four optional seams the runner calls when the campaign defines them (more since
v0.12.0 - the seams section above):
`residual(prediction, target)`, `campaign_scoreboard_fields(cfg, diags, score)` (the campaign's
scoreboard columns), `campaign_checks(exp_id, label, score, diags, cfg)` (merged into
`results/checks_<NN>.json`), and `baseline_config()` (what `--baseline` runs). `run_campaign.py` is now
the kit's machinery: never edited per campaign, replaced wholesale on upgrade. The worker's brief
delivers `experiment.py` by value, and the prompt says the runner's source is not theirs to read or edit.
Evidence: a colleague's audit found the runner Read 64 times in one campaign "because the science hooks
live inside it", and workers writing 30–60 KB bespoke modules per unit rather than finding them.

**Migration.** `upgrade_campaign.py` (above) does the split: it extracts every top-level name your
runner added beyond the template it was scaffolded from — plus the five hooks — into
`scripts/experiment.py` by AST, verbatim and in order, under the current template's header; then
replaces the runner with the kit's. Three things to check by hand:
1. Read the upgrade log. If it names **kit-owned functions the campaign edited in place** (in the
   field campaign that was `append_scoreboard_row`, `write_checks`, `evaluate_and_record`), port those
   edits into the seams from the backup it leaves beside the runner (`run_campaign.py.bak_*`): a
   scoreboard column → `campaign_scoreboard_fields`; an extra check → `campaign_checks`; a second
   figure → dispatch inside `save_figure`; the baseline dict → `baseline_config`. The upgrade exits 2
   until you do.
2. `python scripts/run_campaign.py --preflight`: it imports `experiment.py` and names an import error
   or a hook still stubbed.
3. `tests/correctness_checks.py` that imported a helper from the runner (`from run_campaign import …`)
   now imports it from `experiment`.
A pre-split campaign that is not upgraded keeps working: the validator accepts a runner that still
defines `run_experiment` itself.

## To the writing record — the runner writes what it can derive; the worker owes Analysis and NEXT (kit ≥ v0.11.1, 2026-09-08)

**What changed.** The per-unit record a worker writes shrank to what no code knows. The runner now
writes, at record time, the logbook's **Levers** line (from the config's new `_levers` list), the
**Expected vs found** line (the same judgement `results/checks_<NN>.json` records under `prediction`),
a **Verification** line that starts `pending` and is raised by `--self-check` and by the driver's
verdict stamp (a line written by hand is never overwritten), and the JOURNAL §Recent experiments row.
The worker authors the prediction's one-sentence rationale, the config's `_levers` / one-line
`_comment` / `_hypothesis`, the self-check, and the logbook's **Analysis** (one paragraph; every failed
check answered by name) and **NEXT** (one line). A new mechanical check, `levers`, fails when a config
key moved that `_levers` does not declare (HARD GATE 2 as data). The driver treats a blank Analysis as
an unsaved unit (retry, then shelve). No length is measured or refused anywhere; the budgets are the
prompt's. Measurement: `case-studies/writing_counts.py`. Evidence: the colleague's audit filed as
`case-studies/collective-pulse_worker-time-attribution_fable5_2026-09-07.md`.

**Migration.** `upgrade_campaign.py` (above) brings in the runner, the role file, `CLAUDE.md`, the
logbook and JOURNAL templates' text, and `configs/_template.json`. Existing configs without `_levers`
read `unavailable` on the `levers` check (legitimately, named as such); add the list to new configs.
Older logbook entries without a Verification line are not judged on it. A campaign's JOURNAL must keep
its `## Recent experiments` table for the runner to append rows; without it the runner says so and
the worker adds the row by hand as before. `_predicted`, `_narrative` and `_tier_doc` are gone from
the config template; a config that still carries them is not an error.

## To the compiled brief — orient from the prompt, never the tree (kit ≥ v0.11.1, 2026-09-07)

**What changed.** The driver now compiles the brief into every worker and planner prompt by value:
`campaign.md` (minus its append-only §Decision record), the role file, the project's §Standing
constraints, the JOURNAL working window (the **NEXT** line, §Open threads, §Findings, the last rows of
§Recent experiments), the worker's unit (its queue entry + config) and the scoreboard tail; the planner
also gets `results/queue.json` and `LITERATURE.md`. The prompts tell the agent to orient from the brief
and name the only reads outside it. The prompt travels over stdin (it outgrows the Windows argv cap),
the snapshot manifest's `spawn_prompt_sha256` is the hash of the text actually delivered, and preflight
and every spawn print `brief[role]: N KB (…)` — `(TRUNCATED)` on a section, or a `preflight WARN`, when a
section exceeds the driver's cap. Evidence: `synthesis/BUILD_BACKLOG.md` §2026-09-07.

**Migration.** `upgrade_campaign.py` (above) brings in the runner, `CLAUDE.md`/`AGENTS.md`, `README.md`,
`roles/*.md`; nothing else is touched. Three things to check by hand:
1. `results/JOURNAL.md` must keep the template's section names — a `**NEXT:**` line at the top,
   `## Open threads`, `## Findings …`, `## Recent experiments …` — for the window to be extracted; any
   other section is delivered as a name only. A journal that has grown other sections (planner strategy
   notes, inbox acknowledgements) keeps them on disk; move anything a worker must see into the four
   window sections.
2. Run `--preflight` and read the `brief[worker]` line. A `(TRUNCATED)` section or a `WARN` means the
   window is being delivered cut: consolidate the journal (`campaign-status` step 3) before launching.
3. A custom `AUTORESEARCH_AGENT_CMD` must read the prompt from stdin when `PHYSKIT_PROMPT_STDIN=1` is
   set (the test stub shows the two-line change); the prompt is no longer the last argv element.

## To the verification preset — `configs/loop.json` `verify.preset` (kit ≥ v0.11.0, 2026-09-03)

> **Superseded by ADR-0031** (the section at the top): the four presets' tables, the `review` /
> `re_execution` rows, the verdict `mode`, the `/review` and `/re-execution` labels and the
> `campaign.verification` fallback below are retired, and preflight now refuses that key and `moderate`
> (renamed `heavy`). What follows is the v0.11.0 record; for the edit today, use the top section.

**Symptom.** Preflight prints `preflight OK: verify: preset=… (invariants=… machinery=… gates=…
self_check=… review=… re_execution=… capstone=…)` — or, for an older file,
`rows from campaign.verification='per-block' (legacy - no verify.preset; docs/MIGRATING.md)`. The
driver's log says `verification owed for <exp>: review|re_execution (…)` or `no independent check owed
for <exp> under <preset>` after each accepted unit; the verifier's prompt opens with a
`Verification mode for this spawn: REVIEW|RE-EXECUTION` line; every `results/checks_<NN>.json` carries
`verification` (the preset, its resolved rows, the computed re-execution eligibility, the suite's
due/skipped decisions, and — after a verdict — the `agent` block), `self_check`, `changes`, and a
`label`. `results/correctness_state.json` is per-check. A `capstone` spawn (the claim audit) follows a
graceful STOP or an empty queue.

**What breaks.** Nothing. An older `configs/loop.json` without `verify.preset` is read through its
`campaign.verification`: `per-block` maps to the `intensive` table without its different-model and
blinded extras (every check and an independent check per block — today's behaviour, now metered), and
`promotion-only` maps to the `light` table (an independent review of each promotion candidate, which
that mode used to leave to the worker). A suite with a flat `CHECKS` list and no `@check` declarations
runs whole (every check is row `invariants`), timed as a total, never demoted. Verdicts without a
`mode` field are read as their requested mode. An experiment whose checks artifact predates the
presets keeps the established promotion rule.

**Minimal edit.** Add `"preset": "light"` (or `"intensive"` to keep today's spend) to the `verify`
block and delete `campaign.verification` / `verification_reason`; add `"reproducible": true|false` to
the `campaign` block. Declare rows in `tests/correctness_checks.py` (`@check(row="machinery")` on the
analytic-limit, parity, and convergence checks; `row="gates"` on any per-result gate, which then takes
the experiment as its argument) so the preset can schedule them; undeclared checks stay `invariants`
and count against the every-unit budget (a tenth of `unit_cost.typical_wall_clock_s`, floor 30 s —
preflight names an over-budget set). Add the four contract checks the template ships
(`baseline_reproduces`, `noise_floor_measured`, `metric_discriminates`, `synthetic_recovery`) or a
`tests/CORRECTNESS_NA.md`; the validator asks for them.

**The doctrine that moved.** "Only CONFIRMED graduates" is now "promotion follows the label": every
exported claim carries an honest verification label (`unverified` · `self-checked` · `<verdict>/review`
· `<verdict>/re-execution` · `<verdict>/audit`); where the preset checks promotions only CONFIRMED
graduates, where it does not (`minimal`) the row promotes stamped `unverified` and the guard refuses
one that does not say so. `report` (campaign mode) waits for the claim audit while an exported claim's label is
non-independent. The verbatim sentence lives in `docs/CORE.md`, the campaign
`CLAUDE.md` (HARD GATE 1), and `campaign.md`.

## To measured verification depth, the change manifest, and the time ledgers (kit ≥ v0.11.0, 2026-09-03)

> **Since ADR-0031** there is no verification depth: `verification.re_execution` and the quarter-of-the-
> iteration-timeout rule are gone, and `campaign.reproducible` is only a fact a verifier reads when it
> chooses how to refute. The change manifest and the time ledgers stand.

**Symptom.** A relaunched campaign prints `correctness suite: status=green wall=…s` before each unit,
`[supervise] … done: status=… elapsed=…s` after each spawn, and `utc=` on the driver's decision lines;
`results/diagnostics/spawns.tsv` and `results/timing.tsv` appear; `results/checks_<NN>.json` gains
`run`, `verification.re_execution`, and `changes`; `results/queue.json` gains `supervised_s_since_accept`,
`units_since_accept`, and occasionally `planner_due` / `recommended_mtime`.

**What breaks.** Nothing. Every addition is additive; an older `configs/loop.json` keeps working.

**What changed underneath.**
- `verify.full_reproduction_threshold_s` is no longer set by the scaffold. Re-execution is decided per
  unit from the *measured* solve time (within a quarter of `worker.iteration_timeout_hours`) and
  `campaign.reproducible`. A threshold still present in an older file is honoured as an additional cap;
  delete it when the rule alone is right.
- `campaign.reproducible` (new; boolean). Absent, the runner assumes `false` when
  `configs/instrument.json` exists (hardware-in-the-loop) and `true` otherwise. Set it explicitly for a
  one-shot or unseeded campaign.
- `driver.verifier_retries` (new; inherits `planner_retries` when absent) governs the verifier's retry
  count separately; a verifier that returns ok having written no verdict is retried with a note.
- The plateau clock now counts supervised time, persisted in `queue.json`; the first loop top after
  upgrading falls back to wall-clock since the last accept once, then carries the key. `plateau.units`
  is now enforced; a REFUTED verdict and a change to `configs/RECOMMENDED.json` trigger the planner.
- A block's finished units are verified as soon as the queue head has left the block; a unit the
  planner tags into an old block later forms its own verification group.
- A unit whose save-set is already on disk at the queue head is accepted from the record without a
  worker spawn.
- The post-exit grace for a detached runner ends after two silent runner ticks (or
  `heartbeat_stale_min` if shorter); `detached_grace_min` is only the outer bound.

**Minimal edit.** None required. Recommended: add `"reproducible": true|false` to the `campaign` block
and remove `verify.full_reproduction_threshold_s`.

## To the consolidated project root — README + one overview + rules (kit ≥ v0.10.1, 2026-08-20, ADR-0015)

**Symptom.** The validator reports *"consolidated project still carries LINEAGE.md /
PROJECT_ORIENTATION.md"* or *"still has shared/"* on a half-migrated tree; or you want a five-file
project root (`PROJECT.md` · `PROJECT_ORIENTATION.md` · `LINEAGE.md` · `DISCOVERIES.md` ·
`CLAUDE.md` · `shared/`) brought down to the consolidated three (`README.md` · `PROJECT.md` ·
`CLAUDE.md`).

**What changed.** The project root consolidated (ADR-0015): `PROJECT.md` is THE overview — §Mission
(the old charter), §Standing constraints and the system/instrument/equations depth (the old
`PROJECT_ORIENTATION.md`, section names unchanged), §Updates from discoveries, §Durable decisions,
and §Lineage (the old `LINEAGE.md` tables) — edited by tier (OPEN vs GUARDED; project `CLAUDE.md`
rule 7). A short `README.md` front door carries the directory map, and nothing else does. The
project `DISCOVERIES.md` ledger is **retired**: verified findings live in the campaign that produced
them (journal §Findings + `results/verdicts/`), and the project layer is pointers — the §Lineage
verified-findings column and §Updates-from-discoveries entries citing the verdict by path. `shared/`
is retired for flat purpose-named dirs (`scripts/`, `models/`, …) created at first promotion; the
promotion mark is the §Lineage promotion line. **Era tolerance:** the current driver reads
`## Standing constraints` from `PROJECT.md` and falls back to `PROJECT_ORIENTATION.md`, and the
guard still gates any legacy `DISCOVERIES.md`, so an un-migrated project keeps working and a new
campaign scaffolds into it fine. Migrate for the reading surface, not out of necessity.

**What breaks.** Nothing in an un-migrated project. Do NOT migrate a project whose ACTIVE campaigns
were scaffolded before this change if you cannot re-verify them: their stamped drivers read
`../../PROJECT_ORIENTATION.md` directly, so deleting it breaks *their* preflight. Migrate projects
whose campaigns are done/archived, or whose campaigns are new-era.

**The procedure** (per project; the validator's errors double as the checklist):

1. Scaffold-fresh the two new files from the kit templates (`templates/project/README.md.tmpl`,
   `PROJECT.md.tmpl`), then **move** — do not rewrite — the content: the old `PROJECT.md` charter
   into §Mission; `PROJECT_ORIENTATION.md` wholesale into the matching sections (they kept their
   names); `LINEAGE.md`'s tables into §Lineage.
2. For each `DISCOVERIES.md` entry, add a §Updates-from-discoveries entry citing the same verdict
   artifact path, and make sure the finding's §Lineage row points at its campaign. Then either
   delete the ledger or keep it as read-only history — the guard gates it either way; the validator
   tolerates it.
3. Move each `shared/` artifact to a purpose-named project dir (`models/`, `scripts/`, …), keep its
   version tag, and add its §Lineage promotion line. Update consuming campaigns' `campaign.md`
   §Relationship paths. Delete `shared/`.
4. Delete `PROJECT_ORIENTATION.md` and `LINEAGE.md` (their content now lives in `PROJECT.md`; a
   surviving copy is a fork and the validator flags it). Update the project `CLAUDE.md` from its
   template (new paths + the edit-tier rule).
5. Run the validator on the project root; it detects the new layout and checks §Standing
   constraints, §Lineage indexing, and the retired-file flags:
   `python "<kit>/skills/new-campaign/scripts/validate_campaign.py" <project_root>`

---

## To the consolidated layout — one background document, seven campaign docs, one promotion gate (kit ≥ v0.10.0, 2026-08-20)

**Symptom.** The validator reports *"the project home predates the one-background-document merge: it
has shared/PHYSICS.md and no PROJECT_ORIENTATION.md"*, flags a campaign-level
`docs/PROJECT_ORIENTATION.md`, or reports *"README.md has no 'Setup status' section"*; a newly
scaffolded driver's `--preflight` refuses with *"../../PROJECT_ORIENTATION.md is missing or has no
'## Standing constraints' section"*.

**What changed — project level.** The background became ONE document: `shared/PHYSICS.md`,
`shared/CONVENTIONS.md`, `shared/INSTRUMENT.md`, and the project-root `ENGINEERING_NOTES.md` merged
into `<project>/PROJECT_ORIENTATION.md`, one section each; `shared/` now holds only promoted frozen
artifacts. The driver delivers the doc's `## Standing constraints` into every spawned prompt **by
value** and stamps the spawn prompt's hash into each experiment snapshot's manifest.

**What changed — campaign level.** `campaign.md` is now the whole signed-off contract, absorbing what
were separate files: the goal block and expectations (from the dissolved `docs/PROJECT_ORIENTATION.md`;
tasks go to the queue + JOURNAL NEXT), the campaign-specific verification checks (§Verification, from
`docs/VERIFICATION_PLAN.md` — the generic checklist was the `verify`/`correctness-suite` procedure
restated), and the landmines table + append-only decision record (§Known landmines + §Decision record,
from `docs/ENGINEERING_NOTES.md`). `README.md` is the cold-reader front door; `SETUP_TODO.md` is
retired without a replacement table — setup state is computed live by `--preflight` and the gates,
and README's §Setup status just points there. `DOCTRINE_SNAPSHOT.md` is retired for a kit-**version stamp** in
`campaign.md`'s header and atop `results/logbook.md` — the snapshot recorded only the doctrine spine
while skills, reference docs, and the driver also govern behavior; the version pin recovers the whole
tagged kit (ADR-0012). `INTAKE.md` and `tests/README.md` are retired outright; `docs/` no longer
exists. **`results/DISCOVERIES.md` dissolved into the journal's append-only `## Findings` section**
(V6): settled findings — positive, negative, disputes, REVISES retractions — live there, each citing
its verdict artifact, and consolidation never trims that section. The promotion hook narrowed to the
mechanical surfaces and was renamed `guard_promotion.py`: it gates `configs/RECOMMENDED.json` writes,
scoreboard `CONFIRMED`/`NEW BEST` tokens, and — newly, fail-closed — the **project** ledger
`<project>/DISCOVERIES.md`, whose entries must cite the source campaign's verdict by path
(`campaigns/<slug>/results/verdicts/<id>.json`) with that campaign's suite green. The journal's
Findings section is deliberately not hook-gated (it is working memory); `campaign-status` audits that
every entry's citation resolves.

**What breaks.** Nothing in an un-migrated tree that keeps its own driver — the old campaign's files
still point at paths it still has. The costs are the scattered reading surface and pointer-only
constraint delivery. Migrate a project you are still working in; leave finished campaigns frozen.

**The procedure** (per project; the validator's errors double as the checklist):

1. Create `<project>/PROJECT_ORIENTATION.md` from the kit template
   (`templates/project/PROJECT_ORIENTATION.md.tmpl`) and **move** — do not rewrite — the content:
   the physics inventory, a-priori bound, domain of validity, all unit/sign/frame/ordering
   conventions, known gotchas, and run-constraining rig parameters into `## Standing constraints`
   (keep it lean; it is delivered every cycle); target-of-study, predictive framework, system
   behavior into `## The system under study`; the rig characterization into `## The instrument`;
   equations, simulation methods, common techniques into `## Equations and methods`; the project
   `ENGINEERING_NOTES.md` ED entries into `## Durable decisions`; references into `## References`.
   Then delete the four merged project files.
2. For each **active** campaign, fold into `campaign.md`: the goal / decision-served / done-criteria /
   out-of-scope from `docs/PROJECT_ORIENTATION.md` (§Mission + §FROZEN), its expectations as a
   `## Loosely-held expectations` section, live tasks into `results/queue.json` "next" (with
   rationales) + the JOURNAL NEXT, field-positioning into the project document; the
   campaign-specific checks from `docs/VERIFICATION_PLAN.md` as a `## Verification` section (drop
   the generic checklist rows — they are the skills' procedure — and the bounds rows, which
   §The ONE metric already carries); the landmines table and ED entries from
   `docs/ENGINEERING_NOTES.md` as `## Known landmines` and a `## Decision record` tail. Delete the
   three files and the now-empty `docs/`.
3. Delete `SETUP_TODO.md` — its content is computed live by `--preflight` and the gates — and add a
   short `## Setup status` section to `README.md` pointing there (copy it from the current template);
   move any campaign-specific rows still open into the JOURNAL NEXT list. Delete `tests/README.md`
   too. Stamp the version: copy the kit version from
   `DOCTRINE_SNAPSHOT.md`'s banner (`generated: physkit vX.Y.Z …`) into a
   `> **Scaffolded by physkit vX.Y.Z (…)**` line in `campaign.md`'s header and at the top of
   `results/logbook.md`, then delete `DOCTRINE_SNAPSHOT.md`. Delete `INTAKE.md` after checking it
   holds no proposal the signed-off spec never resolved.
4. Move `results/DISCOVERIES.md`'s entries — D/N findings, REVISES retractions, dispute notes — into a
   `## Findings (settled — positive and negative; append-only, never trimmed)` section of
   `results/JOURNAL.md`, keeping every verdict citation verbatim, then delete the file. Swap the hook:
   copy the new `guard_promotion.py` template into `scripts/`, delete `guard_discoveries.py`, and
   repoint the command in `.claude/settings.json`. The guard is not in the frozen-core file set
   (`CORE_FILES_DEFAULT` is the scorer + the correctness suite), so the swap does not invalidate a
   recorded correctness green.
5. Fix the campaign `CLAUDE.md`: hard gate 1's promotion definition (current-best · scoreboard tokens ·
   the project ledger; findings recorded in the journal), the project-context block, and the §Where
   things live rows — the background doc row points at `../../PROJECT_ORIENTATION.md`, the verification
   / landmines / decision-record rows at their `campaign.md` sections, the settled-findings row at
   `results/JOURNAL.md` §Findings, the setup row at `README.md` §Setup status (the validator enforces
   that table; compare against a freshly scaffolded `CLAUDE.md`).
6. Decide the driver per campaign. By-value constraint delivery, the snapshot prompt-hash, and
   **per-block verification** (the driver spawns an independent verification agent after every
   completed unit or block, stamps the scoreboard's `verified` column from the verdict, and will not
   clear the block without it — `configs/loop.json` `campaign.verification`, default `per-block`)
   all live in `scripts/run_campaign.py`; a migrated campaign keeps the old behavior until you
   re-copy the new driver template and add the `verification` keys to its `campaign` block (today's
   driver refuses that key: set `verify.preset` instead, per the top section). Check
   `frozen_core` before swapping mid-campaign: if the driver is in the core file set, the swap
   changes the core hash and the recorded correctness green no longer applies.
7. Re-run the validator on the project root; it must PASS with zero issues.

---

## To the `campaign` block in `configs/loop.json` (kit ≥ V0/V1, 2026-08-18)

**Symptom.** Every experiment ends with `checks: N not runnable for this campaign`, and each
`results/checks_<NN>.json` lists `comparability`, and the change-vs-incumbent check keyed `noise_floor`,
as `unavailable`, run after run. `campaign-status` reports them as a standing blind spot rather than as
failures.

**What breaks.** Nothing, and the defaults exist to keep it that way. A `configs/loop.json` with no
`campaign` block reads as `prediction_mode` `range` and `noise_model` `stochastic`, which is the behaviour
every campaign already ran under. Blank comparability tags are missing coverage, not a failed check.
Grading them `fail` would raise a permanent red flag on every experiment of every campaign scaffolded
before the block existed, and a red flag no experiment can clear stops being read. An un-migrated campaign
is therefore degraded, never broken, and **this migration is not urgent**. What it costs:

- **Comparability certifies nothing.** A ranking claim is valid only within one (`metric_version`,
  `data_version`) pair. With no tags the check reports `unavailable` and names them, so no ordering of
  two rows in this campaign is machine-certified.
- **The change against the incumbent has no numeric threshold.** "Larger than noise" has no meaning
  until `noise_floor` (stochastic) or `tolerance` (deterministic) carries a number, so that check
  reports the delta as `unavailable` instead of pass or fail.

**What is new.** One top-level `"campaign"` key in `configs/loop.json`, beside `unit_cost`:

| key | legal values | left unset |
|---|---|---|
| `prediction_mode` | `range` · `direction` · `none` | reads `range` |
| `prediction_mode_reason` | free text; required when the mode is `none` | empty — a `none` with no reason is refused at launch |
| `noise_model` | `stochastic` · `deterministic` | reads `stochastic` |
| `noise_floor` | a JSON number ≥ 0, or `null` | `null` — the change-vs-incumbent check stays `unavailable` |
| `tolerance` | a JSON number ≥ 0, or `null` | `null` — the same, for a deterministic campaign |
| `metric_version` · `data_version` | free strings, conventionally `v1` | blank — comparability stays `unavailable` |

A value that is present but out of enum is refused, never defaulted: a typo'd `"determinstic"` falling
back to `stochastic` would hold a deterministic campaign to a spread test it can never satisfy. A quoted
`"0.05"` is a string, not a number, and is refused rather than coerced. Write the number, or `null`, and
never a TODO string. Copy the block's `_doc` field across with the keys; it is the authority on what each
one means.

**The minimal edit.** The two comparability tags:

```json
"campaign": { "metric_version": "v1", "data_version": "v1" }
```

That single change converts the most common `unavailable` into a real check. From then on the runner
stamps both tags onto every `results/scoreboard.tsv` row and into every `results/result_<NN>.json`, which
is what the scoreboard schema always said those columns were for. One wrinkle to expect: the check
compares this run against the incumbent, and a pre-migration incumbent carries no tags of its own, so
comparability keeps reporting `unavailable` (its `needs` says to re-score that experiment under the
current version) until the incumbent is either re-scored or overtaken by a result recorded after the
migration. The tag describes the state the campaign is in now, and is stamped only on rows written from
here on. If the FROZEN scorer or the evaluation data changed at some point in this campaign's history, do
not retro-fit one version onto the older rows: their blank tag is the honest record that nobody certified
them.

**Metric epochs (ADR-0020) — a runner-side behaviour, no new file.** A campaign running the current
runner treats its `metric_version` as a metric *epoch*: the first experiment binds the FROZEN scorer's
hash (`scorer_hash_by_version` in `results/correctness_state.json`), and from then on a change to the scorer's code that
no new epoch declares refuses to spend (comments, docstrings and formatting do not count). Nothing needs adding for that; a tree whose `metric_version` is
blank is simply not enforced. Two optional `campaign` keys in `configs/loop.json` complete the picture:
`"metric_revision": "cautious"` (who may open an epoch; the default when absent) and `metric_epochs` — an
object keyed by `metric_version`, present only once the campaign has revised its metric, each entry
`{kind, status, evidence, expected_direction, opened_by}` (copy `_doc_metric_revision` across; it is the
authority on the fields). If the FROZEN scorer changed at some point in the campaign's history, give each
later version its own entry with what you know as its `evidence`; do not invent a verdict. A campaign
frozen with an older runner keeps its own runner and is untouched. Only an attended session moves
`metric_revision`; a spawned role is refused by the config guard.

**The decision you cannot default.** `prediction_mode` and `noise_model` are setup-time declarations
about what kind of campaign this is. They are not per-experiment knobs, and the defaults do not answer
them:

- *Can this campaign honestly bound its answer before it runs?* `range` if a defensible numeric
  `[low, high]` exists, which is the strongest control. `direction` if the honest claim is only which way
  the metric should move versus a named prior experiment. `none` only if neither is honest, and then with
  a recorded `prediction_mode_reason`. A fabricated range is a fake control, and is worse than none. The
  prediction file stays mandatory in every mode: what relaxes is the bound, never the requirement to write
  an expectation down before spending. The shape the gate demands changes with the mode, so a switch
  applies from the next experiment on.
- *Does re-running one experiment reproduce the metric exactly?* Answer that by running one thing twice,
  not from intuition: re-run a recorded experiment from its own config and compare the metric to the
  number in its `results/result_<NN>.json`. Identical means `deterministic`, and the knob that matters is
  `tolerance` (numerical equality). Anything else means `stochastic`, and the spread over a few repeats is
  the `noise_floor` (`verify`, "Clear the noise floor"). Either may stay `null`, in which case the check
  reports `unavailable` and names the knob. That is honest; a guessed number is not.

Getting either wrong is silent. A stochastic campaign mislabelled `deterministic` promotes
noise as a win. A deterministic one mislabelled `stochastic` is held to a spread test it can never
satisfy, and it fails in the direction that looks like rigor, which is the direction nobody
investigates.

**Migration.** Nothing is re-scaffolded. `configs/loop.json` is user-owned and re-read as the loop runs,
so a live campaign picks the block up at its next unit, and every later
`results/snapshots/<exp>/manifest.txt` records the properties that experiment ran under. A change made
mid-campaign therefore lands in the frozen record, not only in a mutable file.

1. Copy the whole `campaign` block, `_doc` and all, from
   `kit/templates/campaign/configs/loop.json.tmpl` into your `configs/loop.json`.
2. Set `metric_version` / `data_version` (`v1` / `v1` unless this campaign's scorer or data has already
   moved). This alone is a complete and useful migration; the remaining steps can be done later.
3. Answer the two questions above and write the answers into `prediction_mode` and `noise_model`, plus
   `prediction_mode_reason` if the mode is `none`.
4. Set `noise_floor` or `tolerance`, or leave it `null` as recorded debt.

**Done when.** The validator has the last word on whether the block is legal. It rejects an out-of-enum
`prediction_mode` or `noise_model`, and a `none` with an empty `prediction_mode_reason`. From the
PhysKit package root, run:

```bash
python skills/new-campaign/scripts/validate_campaign.py <campaign>
```

It does not fail a campaign with blank tags or an unset resolution, and should not, because that is debt
rather than damage. So it cannot tell you the migration is done. This can, run from the campaign root:

```bash
py -3 - <<'PY'
import json, pathlib
c = json.loads(pathlib.Path("configs/loop.json").read_text(encoding="utf-8-sig")).get("campaign") or {}
def state(key, default):
    v = str(c.get(key) or "").strip().lower()
    return f"{v or default}  ({'declared' if v else 'DEFAULTED - nobody chose this'})"
noise = str(c.get("noise_model") or "stochastic").strip().lower()
knob = "tolerance" if noise == "deterministic" else "noise_floor"
tags = [t for t in ("metric_version", "data_version") if str(c.get(t) or "").strip()]
print("prediction_mode :", state("prediction_mode", "range"))
print("noise_model     :", state("noise_model", "stochastic"))
print(f"{knob:<16}: {c.get(knob)!r}"
      + ("" if c.get(knob) is not None else "  <- change-vs-incumbent check stays unavailable"))
print(f"comparability   : {len(tags)}/2 tags set"
      + ("" if len(tags) == 2 else "  <- comparability stays unavailable"))
PY
```

Migrated reads: both properties `declared` rather than `DEFAULTED`, `2/2 tags set`, and either a number on
the resolution knob or a `null` whose `unavailable` report on every run you accept.

---

## To the split campaign definition (kit ≥ the 2026-08 restructure)

**Symptom.** The validator prints `REFUSING TO VALIDATE` and exit 3, saying the campaign has
`docs/charter.md` and no `campaign.md`. Or a skill sends you to `campaign.md` §The ONE metric and the
file does not exist.

**What breaks.** Nothing, until you try to validate. The campaign runs: its own `CLAUDE.md` describes its
own tree, which is why the routing table was added first. The validator refuses rather than reporting
every required path as missing, because a wall of missing-path errors reads as damage and invites an agent
to repair a frozen campaign. **A finished campaign should not be migrated at all.** Freeze it and read it
where it stands.

**What moved.** One `docs/charter.md` fused three audiences; it is now three files:

| was | is |
|---|---|
| `docs/charter.md` — mission, metric, levers, FROZEN, caps, promotion, scoreboard schema | `campaign.md` |
| `docs/charter.md` — the experiment loop, verification, the save-set, the iteration contract | `roles/worker.md` |
| `docs/charter.md` — getting unstuck, reopening shelved directions, the literature rule | `roles/planner.md` |
| `docs/charter.md` §Ending the loop | deleted — `CLAUDE.md` HARD GATE 5 is the whole contract |
| `docs/protocols/checkpoint.md` §0 · `docs/protocols/artifacts.md` | `roles/worker.md` |
| `docs/protocols/checkpoint.md` (the rest) | the `campaign-status` skill |
| `docs/protocols/metric.md` | deleted — `campaign.md` §The ONE metric said it already |
| `docs/protocols/expensive-evaluation.md` | the kit's `docs/reference/expensive-evaluation.md` |
| `docs/baselines.md` · `docs/dataset.md` | `campaign.md` sections |
| `results/INDEX.md` | deleted — the scoreboard and JOURNAL carry what it indexed |
| the `CORE.md` snapshot inlined in `CLAUDE.md` | `DOCTRINE_SNAPSHOT.md`, referenced not auto-loaded |

**Migration.** For a campaign you intend to keep working in:

1. Scaffold a throwaway campaign with the current kit (`new-campaign`, any answers) and use its tree as
   the shape to copy. That is cheaper and more accurate than transcribing the table above.
2. Split your `docs/charter.md` into `campaign.md` + `roles/worker.md` + `roles/planner.md` by the rows
   above. Keep your own campaign's facts verbatim. Take the generic doctrine from the fresh scaffold
   rather than carrying yours across, so you pick up the corrections.
3. Move the `CORE.md` snapshot out of `CLAUDE.md` into `DOCTRINE_SNAPSHOT.md` **unchanged**. It records
   the doctrine your campaign ran under and must not be re-synced to the current kit.
4. Rewrite `CLAUDE.md` §Where things live from the fresh scaffold's, then **correct every row against your
   tree**. Both the validator and Tier 0 check that each row's file exists and each `§` names a real
   heading, so a copied row that does not match your campaign fails loudly by design.
5. Delete `docs/protocols/`, `results/INDEX.md`, `docs/baselines.md`, `docs/dataset.md` only after
   confirming their content landed somewhere.
6. From the PhysKit package root, run
   `python skills/new-campaign/scripts/validate_campaign.py <campaign>` until it passes. Exit 3 means
   step 2 has not been done yet; exit 1 lists what is still missing.

**Do not** migrate `results/`. The ledger is the record, and its format did not change.

---

## To the `CLAUDE.md` routing table (kit ≥ PR-6)

**Symptom.** A skill tells you to follow the campaign's `CLAUDE.md` §Where things live table and the
campaign has no such section. The campaign was scaffolded before the table existed.

**What breaks.** Nothing hard-fails. A capable agent recovers by reading `docs/charter.md` directly and
reports the named table as missing. The cost is wasted turns, and an agent that believes its
instructions are wrong, which is corrosive over a long loop.

**Migration.** Add the table to the campaign's own `CLAUDE.md`, above `## Standing authorization`. Copy it
from `kit/templates/campaign/CLAUDE.md.tmpl` §Where things live, then **correct every row against the tree
you are in**. That is what the table is for, and a copied row naming a file this campaign does not have is
worse than no table.

Check each row resolves before you finish:

```bash
py -3 - <<'PY'
import re, pathlib
c = pathlib.Path("CLAUDE.md")
rows, on = [], False
for line in c.read_text(encoding="utf-8").splitlines():
    if line.startswith("## "):
        on = "Where things live" in line
    elif on and line.startswith("|"):
        m = re.search(r"`([^`]+)`", line.split("|")[-2])
        if m:
            rows.append(m.group(1))
missing = [r for r in rows if not pathlib.Path(r).exists()]
print(f"{len(rows)} rows, {len(missing)} dangling")
for r in missing:
    print("  MISSING:", r)
PY
```

A campaign with a suffixed charter (`docs/charter_<NAME>.md`, the retired multi-stage layout) names that
file in the table's first rows. That is the case the indirection exists for: one row changes, and no skill
does.

**If you would rather not migrate**, tell the agent so. Reading `docs/charter.md` directly is still
correct in this layout; you are only giving up the indirection.
