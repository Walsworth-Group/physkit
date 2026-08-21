# Changelog — physkit

All notable changes to the kit are recorded here. Format follows
[Keep a Changelog](https://keepachangelog.com/); the kit version lives in `.claude-plugin/plugin.json`.

Dates are UTC. Each entry cites the run/finding that motivated it (the kit's own
`campaign-review → improve-kit` loop) so a future reviewer can trace the "why".

## [0.10.1] - 2026-08-20

Two user-driven scaffolding fixes, same day: the project root consolidates to three documents, and
`new-campaign` finishes setup before handing off. Both are new-scaffolds-only; old trees keep
working under era-tolerant consumers, and no migration is required.

### Changed — the project root consolidates: README + one overview + rules (ADR-0015)

User request + approved plan (2026-08-20, `synthesis/PROJECT_CONSOLIDATION_PLAN_2026-08.md`): five
project-root files were hard to review, `shared/` was opaque, and even verified discoveries get
superseded. New scaffolds get three root documents — a very short `README.md` front door (the
directory map's only home), **`PROJECT.md` as THE overview** (§Mission · §Standing constraints,
still delivered into every spawned prompt · system/instrument/equations depth · §Updates from
discoveries · §Durable decisions · §Lineage), and a lean `CLAUDE.md` — with `PROJECT.md` edited by
tier (OPEN depth/ledgers vs GUARDED mission/constraints/decisions). The project `DISCOVERIES.md`
ledger is **retired**: verified findings stay in the campaign that produced them (journal §Findings
+ `results/verdicts/`), and the project layer is verdict-cited pointers; a legacy ledger stays
hook-gated. `shared/` flattens into purpose-named project dirs (`scripts/`, `models/`, …), the
promotion mark being the §Lineage promotion line. **Old trees never break**: the driver resolves
`## Standing constraints` from `PROJECT.md` with a `PROJECT_ORIENTATION.md` fallback, the guard and
validator accept both layouts, and migration (`docs/MIGRATING.md`, new top section) is optional.
Threaded across the campaign templates, 15 skills, and the reference docs; verified by validator
green on both layouts, toy preflight green, an era-fallback probe, a legacy-ledger guard check, and
a cold fresh-agent findability audit (all five orientation questions answered in ≤4 hops from the
README, no grepping).

### Changed — scaffold-complete now means launch-ready (`new-campaign` finishes setup)

Motivated by a user report (2026-08-20): freshly scaffolded campaigns failed to run in the fresh
session they hand off to, because the scorer and experiment hooks shipped as deliberate stubs and the
skill's exit gate (the template validator) was weaker than the driver's entry gate (`--preflight`).
`new-campaign` now implements the campaign code in the setup session — the FROZEN scorer
(`--selftest` green), the three experiment hooks and `save_figure()`, and exp 000's prediction — and
gates handoff on the driver's own `--preflight` beside the validator, so the two bars are the same by
construction (ADR-0014, reversing the "deliberately not runnable" stance). Anything only the user can
supply is handed over by name, never silently. The fresh session's job collapses to
`/physkit:run-campaign`; exp 000 runs as the first queued unit under the driver's gates. Threaded:
`new-campaign` / `run-campaign` / `campaign-status` SKILL.md, campaign `README.md.tmpl` §Setup
status, `GETTING_STARTED.md` §3. The template stubs and preflight's stub check are unchanged — they
remain the fill target and the safety net for imported or hand-built trees.

## [0.10.0] - 2026-08-20

The document consolidation and the verification rework, in one clean break. A campaign is now **7
documents on 2 levels** against 15 across 3 in v0.9.0 — one background document per project
(`PROJECT_ORIENTATION.md`, its §Standing constraints delivered into every spawned prompt by value),
one signed-off contract per campaign (`campaign.md`), one cold-reader front door (`README.md`),
findings in the journal — and **verification is driver control flow**: an independent verification
agent runs after every completed unit or block, with a subject-matched promotion gate behind it.
**This is a clean break**: a campaign scaffolded by v0.9.0 keeps working under v0.9.0, and
`kit/docs/MIGRATING.md` §"To the consolidated layout" carries the combined v0.9.0 → v0.10.0
procedure. Provenance changes shape: campaigns pin the kit **version** (`campaign.md` header + the
logbook top) instead of carrying a doctrine-spine snapshot — every release is tagged, and the tag
recovers the whole kit (ADR-0012).

Everything below this heading and above `[0.9.0]` shipped in this release.

### Added — the driver verifies every block; the promotion gate goes subject-matched (Phase C: V2's queue blocks + V3's verify-after + V4's structural guarantee)

Verification stops being agent virtue and becomes control flow. Until now, the independent refuter
ran only when a worker decided something was promotion-worthy — an ordinary experiment was never
independently verified, and nothing ensured the verdict's consumption beyond prose rules and audits.

- **Per-block verification, driver-spawned.** After every accepted unit — or the last unit of a
  **block**, a batch of related queue entries sharing a `"block"` id and a `"hypothesis"` — the
  driver spawns a dedicated verification agent (a third role beside worker and planner;
  `--show-prompt verifier` previews its prompt) that runs the verify skill per experiment. The block
  is not cleared until every verdict artifact exists. The worker never grades its own work, and
  skipping is structurally impossible in supervised mode. Verification cost follows unit cost by
  construction: batch cheap experiments into blocks; an expensive experiment is a block of one.
- **Owed verification survives anything.** `pending_verification` lives in the queue ledger, so
  verification owed by a crashed or interrupted run is serviced first on relaunch. Verifier failures
  degrade loud like worker failures; N in a row halts as SYSTEMIC — the loop must not keep producing
  science nothing verifies. `campaign-status` and `run-campaign` watch the backlog.
- **Consumption goes mechanical.** The driver stamps the scoreboard's `verified` column from the
  verdict artifact (blank cells only — never overwriting a recorded value); the verifier queues the
  named control for a REFUTED and the fix-and-rerun for an INCONCLUSIVE as concrete units.
- **The control is owned.** `configs/loop.json` `campaign.verification`: `per-block` (default) or
  `promotion-only` **with a required recorded reason** — the same contract as
  `prediction_mode: 'none'`, honoring the plan's affordability concern (C3) without an unrecorded
  off-switch. Preflight and the validator both refuse an out-of-enum mode or a reasonless downgrade.
- **The promotion gate is subject-matched.** With every experiment carrying its own verdict,
  `guard_promotion` now demands the verdict **for the experiment being promoted** — matched from the
  exp id the written content carries — instead of accepting any CONFIRMED verdict within a 60-minute
  window (a residual the old gate's own docstring flagged; the `AUTORESEARCH_VERIFY_WINDOW_MIN` knob
  is gone). A write that names no experiment is denied with the fix stated.

The design-before review (V3's other half, with refusal power) is deliberately not included — it is
a separate decision with its own rubber-stamp risks, still open in the plan.

### Changed — findings live in the journal; the promotion gate narrows to its mechanical surfaces (Phase C, V6)

`results/DISCOVERIES.md` dissolved into the journal's append-only **`## Findings`** section: settled
findings — positive, steering-negative with their kill tiers, DISPUTES notes, REVISES retractions —
live in the campaign's working memory, each citing its `results/verdicts/<id>.json`, and
consolidation never trims that section. One less file, and one less prose ledger to guard.

The promotion hook narrowed accordingly and is renamed **`guard_promotion.py`**:

- It gates the **mechanical** surfaces downstream consumers actually trust: `configs/RECOMMENDED.json`
  writes and scoreboard edits that introduce a `CONFIRMED` / `NEW BEST` token (recency-checked
  verdict + named refuter + affirmative non-stale green suite, as before).
- It **newly gates the project ledger** `<project>/DISCOVERIES.md`, fail-closed — closing a gap the
  old guard documented but could not fix: its campaign-root resolution failed above a campaign, so
  every project-ledger write hit an unsatisfiable deny. An entry must cite the source campaign's
  verdict by path (`campaigns/<slug>/results/verdicts/<id>.json`); the gate resolves the verdict
  across campaigns (archived ones included) and requires the source campaign's suite green.
- The campaign DISCOVERIES surface is gone with the file. The journal's Findings section is
  deliberately **not** a hook surface — it is working memory, edited every cycle, and guarding prose
  patterns is the bug-prone shape the old surface's own history showed (the substring-match defect) —
  the rule binds by convention and `campaign-status` audits that every entry's citation resolves.

Hard gate 1's promotion definition, the roles, the planner prompt, verify's campaign mode,
fork-campaign's carry-forward, and the validator's required files all follow. `kit/docs/MIGRATING.md`
carries the move procedure; the hook swap is frozen-core-hash-safe (the guard is not in
`CORE_FILES_DEFAULT`).

### Changed — the campaign folds to seven core documents; provenance becomes a version pin (V1c)

The campaign doc set is redesigned around three reader contexts — loop agents get the assembled
prompt, cold readers get the front door, the human signs one contract:

- **`campaign.md` is the whole signed-off contract.** It absorbs the campaign-specific verification
  checks (§Verification — the retired `docs/VERIFICATION_PLAN.md`'s generic checklist was the
  `verify`/`correctness-suite` procedure restated, and its bounds rows were aliases of §The ONE
  metric's), the landmines table and the append-only decision ledger (§Known landmines + §Decision
  record, from the retired `docs/ENGINEERING_NOTES.md`). `docs/` no longer exists. Landmines need no
  prompt injection anymore: both roles are contractually required to re-read `campaign.md` every
  cycle, so the driver injects only the project's §Standing constraints — the one delivered document
  outside the per-cycle read set.
- **`README.md` is rewritten as the cold-reader front door**: purpose, how the two roles run, a
  who-reads-what-when file map, and §Setup status. `SETUP_TODO.md` is retired **without a
  replacement table**: setup state is mechanical and already enforced plugin-side — preflight
  refuses to launch and names each stub with its fix, the gates hold the rest — so the section is a
  pointer to `--preflight`, the one source that cannot go stale, and campaign-specific setup tasks
  seed the JOURNAL NEXT list. `campaign-status` reports a no-rows-yet campaign by running preflight
  rather than reconstructing state from docs.
- **`DOCTRINE_SNAPSHOT.md` is retired for a kit-version stamp** (`campaign.md` header + the top of
  `results/logbook.md`). The snapshot recorded only the doctrine spine while skills, reference docs,
  and the driver equally govern behavior — a partial record that read as a complete one. Every
  release is tagged, so the version pin recovers the *whole* kit; it is still a frozen record, never
  updated to a newer version. (ADR-0012 — a deliberate reversal of the freeze-and-stamp file.)
- **`INTAKE.md` is retired.** Form-mode users now edit a pre-filled **draft `campaign.md`** directly —
  the document they craft is the campaign definition, not a form transcribed into one — finalized at
  sign-off, where the validator refuses any surviving `[PROPOSED]` tag. `tests/README.md` is retired
  (its policy text lived in the gates and the skill; the run command lives in the suite's docstring).
- **`LITERATURE.md` gains a guaranteed read path** when present: a conditional routing row in
  `CLAUDE.md`, and the planner prompt names it.

With V6 (above) landing in the same release, a scaffolded campaign carries **7 documents on 2
levels** (plus conditional `LITERATURE.md`), against 15 across 3 levels in v0.9.0: `README.md` ·
`campaign.md` · `CLAUDE.md` · `roles/worker.md` · `roles/planner.md` · `results/JOURNAL.md` ·
`results/logbook.md`.

### Changed — one project background document, delivered by value (Phase C, V1b)

Four project docs that each opened by distinguishing themselves from the other three —
`shared/PHYSICS.md`, `shared/CONVENTIONS.md`, `shared/INSTRUMENT.md`, `ENGINEERING_NOTES.md` — are
now ONE `PROJECT_ORIENTATION.md` at the project root, one section each; `shared/` holds only promoted
frozen artifacts. The campaign-level `docs/PROJECT_ORIENTATION.md` dissolved into `campaign.md`
(goal, done-criteria, expectations, out-of-scope), the queue + JOURNAL NEXT (task hierarchy), and the
project document (field positioning). A fresh scaffold now produces 3 project background+charter docs
and a flatter campaign tree instead of 10 documents across three levels.

Two mechanisms ride on the merge, closing the recorded-but-unread gap for constraints:

- **The driver delivers `## Standing constraints` (project) and `## Known landmines` (campaign) into
  every spawned worker/planner prompt by VALUE** — guaranteed present, never merely pointed at —
  through `build_prompt()`, the one assembly path, so `--show-prompt` previews exactly what ships.
  Preflight refuses to launch when the constraints section is absent.
- **Each experiment snapshot stamps the spawn prompt's sha256** into its manifest: the background doc
  is living, so two experiments in one campaign can run under different delivered context, and "what
  did this run under" must be answerable from the frozen record.

The validator gates the new layout (`PROJECT_REQUIRED_FILES`, the constraints-section check, the
widened no-local-copy rule) and names a pre-merge project with the migration pointer instead of
reporting generic damage. `kit/docs/MIGRATING.md` carries the old -> new map. The
`{{PHYSICS_DOC}}`/`{{CONVENTIONS_DOC}}` path placeholders retire — the background doc has a fixed
location, so templates carry literal relative paths and there is no per-campaign depth-counting to
get wrong.

### Fixed — a scaffold that cannot run no longer reports itself ready to launch

`new-campaign` generates a valid tree but deliberately does not write the physics: `validate_method()`,
`run_experiment()` and `load_target()` ship as `raise NotImplementedError` stubs, because only the
campaign knows what an experiment is. Preflight probed the FROZEN scorer and never these three, so a
freshly scaffolded campaign passed every check and was told **"ready for --supervise"** while every unit
was guaranteed to fail. The failures then look identical to each other, so the consecutive-failure halt
classified them as SYSTEMIC — blaming the environment for code that had simply never been written.

- **Preflight now refuses while any hook is still the generated stub**, naming which one and where to
  fix it. Detected from source, never by calling them: `run_experiment()` runs an experiment, so probing
  by invocation would spend a unit to answer a question about setup. A hook whose source cannot be read
  is reported as implemented — silence beats a false accusation that sends someone editing correct code.
- **What is unbuilt is now stated where the researcher will look**, rather than only in a stub's
  traceback: `README.md` §Setup status says the scaffold is deliberately not runnable and points at
  `--preflight` as the authoritative live list; the CLAUDE.md routing table carries the row. (First
  built as a standalone `SETUP_TODO.md` consequence table; the table was dropped as duplicated state
  — preflight and the gates already compute it live — see the V1c entry above.)

### Fixed — the live feed no longer buries the agent under its own session events

Every stream event of type `system` rendered as `session start`. A session emits many of them: one real
worker unit produced **253 such lines against 7 lines of agent text**, burying the only part that says
what the agent is doing — in the log the driver's own docs call the way an unattended run is diagnosed.
The tell was that they printed `model=?`, since a real init event carries a model. Only `subtype: init`
is a session start now; the rest render nothing.


## [0.9.0] - 2026-08-20

The campaign-structure redesign — Phases A-B complete, Phase C through V0-V1 (the a-priori
prediction gate and the per-experiment checks artifact). Phase C's remaining rows (V1b-V6: the
one-background-document merge, the block model, the two reviews) had not shipped as of this
release. A campaign is now organized by **who reads what, and
when**: `docs/charter.md` is split into `campaign.md` + `roles/worker.md` + `roles/planner.md`, the
doctrine spine leaves the always-on file, and `docs/protocols/`, `results/INDEX.md`,
`docs/baselines.md` and `docs/dataset.md` are gone. **This is a clean break** — a campaign scaffolded
by 0.8.0 keeps working under 0.8.0, and `kit/docs/MIGRATING.md` carries the old -> new map and a
six-step procedure. `validate_campaign.py` now *refuses* a pre-restructure tree at exit 3 rather than
reporting every required path as missing, because a wall of missing-path errors reads as damage and
invites an agent to "repair" a frozen campaign.

Everything below this heading and above `[0.8.0]` shipped in this release.

### Changed — the shipped prose is written in one register, and stops teaching from our internal incidents (S-1/S-3/S-3b, 2026-08-15..19)

The kit's prose had accumulated the voice of the sessions that produced it: internal anecdotes, tracker
ids, pinned dates, and paths that exist only in this repo. A reader learning the rule had to first
decide which parts were about them. A style guide (`synthesis/AUTHORING_STYLE.md`) now states the
contract, and three passes applied it — the 58 stable prose files, then the 13 campaign scaffolding
files, then the prose the redesign itself added, including the comment and console text in the code
templates.

- **Anecdotes are replaced by the rule they were teaching**, stated as condition -> action ->
  consequence. Where a rule could not be stated without its originating story, the story stayed.
- **`kit/docs/PRINCIPLES.md` is substantially rewritten** (6,683 -> 6,302 words) and no longer claims
  to be derived from a `synthesis/` content master. It **is** the canonical statement, with
  `kit/docs/CORE.md`; the former upstream master was archived 2026-08-20 for lagging this file.
- **`hard-won` is gone kit-wide** — one slogan replicated into nine files, where in every case the
  sentence's antecedent already scoped the noun.
- Skill `description:` frontmatter was held out of all three passes and is **byte-identical**: it is
  the routing surface the harness selects on, so changing it changes which skill fires.

Register only — no gate, default, threshold or procedure changed. Every pass was checked by
independent verifiers, and **three of five rewrites in the last round were rejected** for changing
meaning rather than register; the code-template edits were verified AST-identical.


### Added — a campaign says what KIND of campaign it is, and the runner writes down what it checked (V0/V1, 2026-08-18)

Two campaigns the kit could not serve honestly: one that cannot bound its answer in advance, and one that
is deterministic. Both were told to do something impossible and both had to fake it. A campaign doing
first-of-kind measurement could only satisfy the a-priori prediction gate by inventing a range wide enough
to be unfalsifiable — which passes the gate and controls nothing, so the gate was already being defeated,
silently. A deterministic campaign was held to a hard gate demanding a win "exceed measurement spread"
when repeated runs of it are identical and there is no spread to exceed.

- **`configs/loop.json` gains a `"campaign"` block.** `prediction_mode` (`range` | `direction` | `none`)
  scopes what the spend gate accepts as a prediction; `noise_model` (`stochastic` | `deterministic`), with
  `noise_floor` and `tolerance`, scopes what clearing the noise means. The prediction FILE stays mandatory
  in every mode — what relaxes is the bound, never the requirement to write an expectation down before
  spending. `none` costs a recorded `prediction_mode_reason`, refused at launch if empty, and `direction`
  (which way, versus a named prior experiment) is the checkable middle so there is no single step from a
  real bound to none at all. Reasoning, and why this is net *stronger* than the gate it replaces:
  `DECISION_RECORDS.md` ADR-0010.
- **Defaults reproduce the previous behaviour exactly**, so a `loop.json` written before this keeps
  working. A *present but out-of-enum* value is refused rather than defaulted: a typo'd `"determinstic"`
  falling back to `stochastic` would hold a deterministic campaign to a test it can never satisfy, and it
  would fail in the direction that looks like rigor — the direction nobody investigates.
- **`results/checks_<NN>.json`** — every experiment now leaves a machine-readable record of what the
  runner checked: whether the result met its prediction, whether the change against the incumbent exceeds
  this campaign's own resolution, comparability, hard bounds, guardrail, correctness-suite green-and-not-
  stale, save-set complete. Before this the runner computed an out-of-range flag, printed `RED FLAG`, and
  **nothing downstream read either**.
- **Three-valued, and that is the point.** A check reports `pass`, `fail`, or `unavailable` — and an
  `unavailable` carries a **`needs`** string naming exactly what this campaign would have to supply to
  make it real. Reporting `pass` for a check that could not run is how a green becomes evidence for
  something nobody measured; a hardcoded `null` is how a written artifact quietly stops being a gate. Two
  checks (hard bounds, guardrail) ship permanently `unavailable` rather than inventing a threshold the kit
  has never defined.
- **`campaign-status` reads them**, and distinguishes three things that are not the same: a `fail` somebody
  still owes an answer to, a standing `unavailable` blind spot, and an absent artifact meaning the
  experiment bypassed the runner. It reports which checks have been unavailable on *every* experiment — a
  check silently unavailable for forty runs deserves more attention than one that failed once.

### Fixed — every scoreboard row the runner wrote was born failing the scoreboard's own rule (2026-08-18)

`results/scoreboard.tsv` states that every row **must** carry `metric_version` and `data_version` and that
a blank tag is a hygiene failure, and that `tier` must be present or cap-compliance stops being
machine-auditable. The runner's row writer passed neither tag nor the tier, and a column missing from the
row dict is written blank — so this was true of every campaign ever scaffolded, and the kit's own worked
exemplar reproduced it. `campaign-status` has been asking agents to verify a property that had never once
held. The runner now emits all three, and carries the two tags in `result_<NN>.json` so a later comparison
reads them with the number rather than beside it.

### Changed — one lever per experiment is stated in two places instead of fifteen (2026-08-18)

Hard gate 2 stopped making one lever a rule or a default in 0.8.0, but the old framing survived across the
kit. A whole-repo sweep found **15** normative restatements in 11 shipped files. They are now cut to
pointers on the campaign surface, and the three doctrine masters the gate is derived from
(`docs/CORE.md`, `docs/PRINCIPLES.md`, and the taxonomy behind them) reworded to the gate's own words so
the constitution and the gate cannot drift apart. `PRINCIPLES.md`'s style rule had been using this very
rule as its worked example of an aspirational rule, which quietly made the style guide a locus of it too.

Untouched, deliberately: the places where "one-lever experiments across ≥2 lever families pin at the same
floor" is the *trigger condition* for an assumption audit rather than a restatement of the rule — cutting
those would break `assumption-audit` — and the uses that share the words but not the concept (`debug`'s
bisect-one-change-at-a-time, `attribute-mechanism`'s one-knob-per-mechanism).

### Changed — the worked example models a healthy campaign (2026-08-18)

The toy campaign shipped with an all-skip correctness suite, so it reported EMPTY on every run and its own
promotion gate was permanently blocked. An exemplar that has learned to live with a red gate teaches the
reader that a failing check is normal. It now carries four real analytic checks on the two-loop field —
midplane symmetry, the closed form at zero separation, the vanishing second derivative at the Helmholtz
condition, and far-field decay — each of which fails on a bug the uniformity metric alone would score
happily. Not stubs seeded to flip EMPTY→GREEN, which remains banned. The toy is also now the kit's worked
example of a `deterministic` campaign, since its field is analytic and no RNG touches the solve path.

### Added — a metric that cannot produce a number now says so, in code (EH-5, 2026-08-18)

`scripts/metric.py` gains `PLAUSIBILITY_BOUNDS` — the hard physical bounds the campaign already stated
in prose, in the one form code can act on. A result outside them is flagged in
`results/checks_<NN>.json` as what it is: a bug in the scorer, the data or the pipeline, not a
disappointing result. Before this the bounds existed only as prose in two documents, so the runner's
plausibility check reported `unavailable` in every campaign that has ever existed.

- **Flagged, not refused.** Refusing would lose the artifact you need to debug the violation, and it
  would put quiet pressure on the next person to widen the bounds until their run goes through — which
  is the fabricated-range failure wearing different clothes.
- **Encode only what is true BY CONSTRUCTION** — a correlation cannot exceed 1, a variance cannot be
  negative. Not the range you expect a good result to land in: that is the a-priori prediction, it
  lives in `predictions/`, and conflating the two turns a mathematical impossibility into a
  disappointing-result alarm that fires forever.
- **The self-test refuses bounds that exclude the scorer's own perfect case**, before experiment 000.
  Bounds that contradict the metric would otherwise flag every experiment for the life of the campaign.
- It lives in FROZEN core deliberately: editing the bounds changes the core hash and invalidates the
  recorded correctness green, because the bounds are part of what the metric *means*.

### Fixed — a supervised loop no longer dies because an agent typed a checkmark (2026-08-18)

The driver relays a live worker's output to the console. That output is arbitrary text written by a
model, and the relay never checked what the console could encode — so on a stock Windows terminal
(cp1252) the first `✓`, arrow, curly quote or emoji a worker emitted raised `UnicodeEncodeError` out
of the watch loop and killed the run mid-unit. An overnight loop could be ended by a decoration.

Found by the first real `claude -p` spawn ever run against this kit version. The deterministic suite
could not have found it: its stub agent emits only ASCII, so the whole relay path had been exercised
exclusively with characters that cannot fail. The fix makes the console lenient
(`errors="replace"`) rather than switching it to UTF-8 — replacement is honest about what the
terminal can show, where UTF-8 would trade the crash for mojibake — and the driver's own log keeps
the full text, since it is opened UTF-8 separately.

### Fixed — the mechanical checks now say only what they measured (2026-08-18)

An adversarial audit of the work above ran 29 mutations against it; twelve survived a fully green
suite. The defects were real and are fixed here, but the shape of them is the part worth recording:
**every one was a check reporting a verdict it had not earned.**

- `save_set` asserted that the figure was on disk without ever looking at it, and could not fail at
  all — the record gate had already hard-exited on the same artifacts, so it was a constant `pass`
  wearing a verification's clothes, inside the one file whose header warns against exactly that. It
  now re-verifies all four artifacts at record time.
- The change-vs-incumbent check computed a delta against a result scored under a **different**
  `(metric_version, data_version)` and graded it `pass`, next to a comparability `fail` saying that
  subtraction is meaningless. It now reports `unavailable` when the incumbent is not comparable.
- The same check read resolvability as goodness: a catastrophic regression scored `pass` and raised
  no flag, while a faithful replicate — the run `verify` requires in order to *estimate* the noise
  floor — was red-flagged. Flagging the procedure the kit prescribes is how a reader learns to skim
  past red flags. A resolvable regression now flags; a within-resolution change is reported as the
  honest "these are the same number".
- Blank comparability tags were graded `fail`, so every experiment of every campaign predating the
  campaign block raised a permanent red flag that no experiment could fix. They are missing
  **coverage** (`unavailable`, with what would supply it); a genuine version mismatch is still a
  failure.
- A missing or corrupt `configs/loop.json`, a `campaign` block that is not an object, a quoted
  number, and a negative resolution all ran or crashed rather than refusing. A negative resolution is
  the worst of them: it makes every noise check pass unconditionally, and fails in the direction that
  looks like a clean result.


### Changed — a campaign is reorganized by who reads what, and when (PR-9…PR-14, 2026-08-17)

**This is a clean break in the campaign layout.** Existing campaigns keep working and are not migrated
automatically; `docs/MIGRATING.md` has the procedure, and `validate_campaign.py` now *refuses* a
pre-restructure tree rather than reporting it as broken.

The problem was never correctness. Testers could not tell what the files were for, and the measurement
said why: a worker was handed 72 KB, of which a single 41 KB `docs/charter.md` fused the campaign's
definition, the worker's procedure and the planner's strategy into one document. A worker structurally
could not act on about a quarter of what it was told to read.

**The new tree.** `CLAUDE.md` (always-on) · `README.md` (human front door) · `campaign.md` (THE
definition — mission, the FROZEN metric, levers, caps, promotion, the baseline gate, the dataset) ·
`roles/worker.md` (per-experiment procedure, the iteration contract, the save-set) · `roles/planner.md`
(strategy, getting unstuck, the literature rule) · `DOCTRINE_SNAPSHOT.md` · `configs/ results/ scripts/
tests/ predictions/` · `docs/{ENGINEERING_NOTES,PROJECT_ORIENTATION,VERIFICATION_PLAN}.md`.

- **Removed:** `docs/charter.md`, `results/INDEX.md`, `docs/protocols/` (7 files), `docs/baselines.md`
  and `docs/dataset.md`. The protocols' two surviving files were absorbed into `roles/worker.md`, not
  exiled; the baseline gate and the dataset became `campaign.md` sections.
- **The always-on file is now light.** The inlined `CORE.md` snapshot — 13.6 KB of reference material
  riding in every turn's context — moved to `DOCTRINE_SNAPSHOT.md`, **referenced, never auto-loaded**
  and never re-synced against a newer `CORE.md` (it records what governed *that* run). `CLAUDE.md`
  keeps only what binds a turn: the integrity core, the research reflexes, the hard gates, and the
  routing table. 21.4 KB → 9.9 KB.
- **Hard gate 2 no longer makes one lever a rule or a default.** It requires that an experiment *name*
  the levers it moved and weigh what moving several together costs: one makes the cause plain, several
  make the result a claim about the combination. Either is legitimate; leaving it unrecorded is not.
- **"The only three ways the loop ends" is retired.** Gate 5 names the two actual decisions
  (`results/STOP`, a recorded `results/stop_request.json`). The ~25-continuation stall release is
  documented in `roles/worker.md` as what the old section itself called it — a failure signature, not
  an exit.
- **New `--show-prompt <worker|planner>`** prints the literal prompt the driver would spawn, with its
  size and hash. Both spawn paths and the preview go through one `build_prompt()`, so a preview cannot
  drift from a spawn.

**Measured, not estimated:** worker feed 72.4 → 51.5 KiB; `roles/worker.md` and `roles/planner.md` share
no substantive content beyond a two-line pointer both roles need; the rendered campaign has no dead
shared-doc links, where it previously had three.

**Fixed on the way through**, each shipping before this release:

- **Every shared-doc link in the rendered charter was dead.** `../../shared/PHYSICS.md` from `docs/`
  resolves to `<project>/campaigns/shared/`. Three things had to be wrong: `PLACEHOLDERS.md` claimed
  the validator checks intra-tree doc links resolve (**it does not**), so nothing enforced the rule;
  its example table then drifted into contradicting the rule stated two lines above it; and the
  renderer reproduced the documented error. The renderer now computes depth.
- **A sentence fragment in `docs/dataset.md`.** A six-line blockquote had been cut down to its last
  line, which began mid-sentence. Repaired to the sentence that was meant to survive.
- **Six hygiene checks were one deletion away from vanishing.** `protocols/checkpoint.md` asserted that
  `campaign-status` encoded them; the assertion had never been tested. Five were covered — the sixth,
  validating that the load-bearing upstream transform feeding the current-best is non-degenerate, was
  not, and is now in `campaign-status` §2.
- **46 unresolvable references** (internal tracker ids, kit PR numbers, dated incidents) were shipping
  into every campaign, defined nowhere a campaign reader could reach. Removed, and a Tier 0 check keeps
  them out.

### Fixed — a wired gate must actually RUN, and a fail-open must land in the campaign it bypassed (F4/F5, 2026-08-15)

Found while running the redesign's cheap confirmations (`synthesis/REDESIGN_CONFIRMATIONS_2026-08-15.md`).

- **The toy campaign's hooks were dead, and no test could see it.** `tests/structured_loop/scaffold.py`
  hardcoded `PYTHON_CMD: "python"`. On a stock Windows box that is the Microsoft Store *App Execution
  Alias* stub: it prints "Python was not found", exits **49**, and never runs the script. Exit 49 is
  non-zero and not 2, so Claude Code reports a non-blocking hook error and **allows the action** — a
  campaign with no promotion gate and no loop persistence, silently. This is the default state of a fresh
  Windows machine (Store aliases on by default, the installer's PATH box off by default). The scaffold now
  **detects** the invocation, executing each candidate before trusting it; `new-campaign` Step 0.5 already
  prescribed this and only the test scaffold disagreed.
- **The suite could not catch it** because `tier1_gates.py` invokes the hook scripts with `sys.executable`,
  bypassing `.claude/settings.json` entirely. New **Tier 1d** drives the gates *through* the settings
  command string, and `validate_campaign.py` makes the same assertion against a real campaign — the item
  that protects a tester rather than the kit's own toy.
- **`guard_discoveries.py` could record a fail-open outside the campaign it bypassed.** It fell back to
  `Path(".")`, so the unparseable-stdin bypass wrote `results/gate_failures.log` into the process's cwd.
  `campaign-status` reads that log *inside* the campaign, so the one path built to keep a fail-open
  non-silent was the path that could silence it — and the stray file would make an unrelated tree
  hard-fail on a bypass that never concerned it. Now resolves from `CLAUDE_PROJECT_DIR` first and, with no
  campaign root, writes nothing and announces on stderr. Still fails open.

Each new check was **falsified before being trusted**: reintroducing `PYTHON_CMD="python"` fails three
Tier 1d checks; reintroducing the `Path(".")` fallback fails three Tier 1e checks.

### Changed — skills route through the campaign's own `CLAUDE.md` map, not a hardcoded charter path (PR-6, 2026-08-15)

The keystone of the campaign-structure redesign (`synthesis/REDESIGN_PLAN_2026-08.md`). Kit skills used to
name `docs/charter.md` directly, so the coming restructure would break every one of them.

- **New `## Where things live` table** in `templates/campaign/CLAUDE.md.tmpl` — the campaign's map of
  itself. `CLAUDE.md` exists in both the current and post-restructure layouts and is frozen with its
  campaign, so a skill that routes through the table is correct in both. Fixed text, per the plan's
  governing principle; a campaign that renames a document corrects the row.
- **Seven live references across six skills repointed** (`verify` Step 0 and the spawned-refuter prompt,
  `campaign-status` Step 0 + cadence + literature trigger + sibling-coupling + its campaign-vs-project
  probe, `run-campaign` Step 0, `final-report`'s standard-homes list, `correctness-suite`,
  `discovery-loop`). The `description:` frontmatter, `final-report`'s non-kit fallback, and `new-campaign`
  (which authors the charter) are deliberately untouched.
- **Legacy fallback**: no campaign scaffolded by a released kit has the table, and freeze-and-stamp means
  none ever will. Tested rather than assumed — a cold agent on a legacy tree *recovered* by inference but
  reported its instructions as wrong. One fallback clause per instruction, plus `kit/docs/MIGRATING.md`.
- **New Tier 0 checks**, each falsified first: every row's path resolves, every `§section` exists, and —
  after the first version shipped a row claiming `configs/loop.json` held the checkpoint cadence, which
  lives in the charter — every row's **leading concept must occur in the file it names**.

## [0.8.0] - 2026-08-13

### Added — size the DISK cost per experiment, not just the time (SV-7, 2026-08-12)

User request from the same supervised-run thread (2026-08-12): the setup interview budgets wall-clock but
never bytes, so a long loop can fill its volume overnight — and the failure mode is the worst available
(a unit writing half a save-set, surfacing at 3 a.m. as an unrelated-looking gate error). The kit's own
record already carried the motivating class: the project layer exists partly because prior multi-version
investigations bloated to **~422 GB across 8 sibling dirs** (0.5.0 notes).

- **`new-campaign` topic 8 is now "Compute resources, time budget, and disk budget."** Free disk is
  *detected*, not asked (Step 0.5 rule); the per-experiment footprint is **derived** from the artifact
  plan — save-set + snapshot (a few hundred KB) plus the bulk terms that actually dominate (checkpoints,
  generated datasets, computed operators, raw arrays), computed from real shapes rather than a feeling.
  The interview states three numbers back: MB/experiment · projected total for the planned count · free
  space. Above ~25% of free space, the **retention plan is designed with the user before scaffolding**.
- **The estimate is machine-readable and enforced**: `configs/loop.json` `unit_cost.typical_disk_mb`
  (new `{{UNIT_COST_DISK_MB}}`) arms a floor in the driver — `--preflight` refuses a launch below
  ~3 experiments of headroom (naming the retention plan as the fix), notes a short runway below ~20, and
  the loop top halts on the same floor **before** a unit can write a partial save-set. `0`/absent
  disables the check, so older campaigns are unaffected.
- **Retention plan section in `protocols/artifacts.md`** (new `{{RETENTION_PLAN}}`, `{{DISK_PER_EXP}}`),
  scoped so it can never erode reproducibility: the permanent record (scoreboard row, result JSON,
  figure, snapshot, narrative, verdicts — hard gate 4) is **never** in the trade and is small by
  construction; only *bulk* artifacts are negotiable, and only when regeneration is deterministic and
  recorded (snapshot pins config+code, manifest pins seed+command). Current-best bulk artifacts are kept;
  anything not deterministically regenerable (hardware, external services, unrecorded seeds) is never
  droppable; dropping is deletion — it needs confirmation and is logged in `INDEX.md`.
- **`campaign-status`** now measures the *actual* footprint (bytes-so-far ÷ experiments-so-far), reports
  the remaining runway in experiments, and corrects `typical_disk_mb` when the scaffold-time estimate was
  off — the estimate was made before any experiment ran. **`run-campaign`** gained the disk-floor halt to
  its triage list. Tests: tier-0 knob/lint checks + tier-2 scenarios G2 (floor refuses a launch) and G3
  (no estimate ⇒ check disables itself, back-compat). Suite 72/72.

### Added — `run-campaign`: the loop's cockpit (SV-6, 2026-08-12; skill count 23 → 24)

Same motivating run as SV-1..SV-5 below, second finding: launching meant hand-typed commands (false
starts included) and the running loop had no conversational surface — and the first user-observed
`new-campaign` handoff funneled toward the retired interactive-executor mode (the handoff's first
command opened an interactive session, setup happened there, the Stop hook armed after exp 000, and
`--supervise` trailed as a code block).

- **New skill `skills/run-campaign/`** — launcher / monitor / intermediary around the deterministic
  driver: runs the driver's `--preflight` and translates every failure into its fix, launches
  `--supervise` as a background shell process, narrates from `results/diagnostics/supervise_*.log` +
  `queue.json`, relays user steering into `results/inbox/`, triages halts by ADR-0009 kind, performs the
  graceful stop. **Concierge fence:** never executes loop units; only writes are inbox notes and
  launch/stop controls — disposable context by design (everything travels through artifacts). Division
  of labor stated on both sides: run-campaign answers *process* questions, `campaign-status` answers
  *science* questions (its NOT-for list now routes process questions here).
- **`new-campaign` Step 5 restructured** — names the destination up front (supervisor mode via
  run-campaign), frames metric/selftest/exp-000 explicitly as *pre-loop setup, not the loop*, hands off
  to `/physkit:run-campaign` (raw commands kept as a fallback line), and retires the "interactive
  session working `--config` by hand remains fine" framing: by-hand runs are single-experiment
  debugging, not a loop mode. Same reframe in `charter.md.tmpl` ("Attended = the cockpit, not by-hand
  execution") and `GETTING_STARTED.md` §4 (rewritten around the cockpit; the executor mode's failure
  record — context growth, doc drift, premature stops, verification decay — stated once so nobody
  regresses to it).
- Registration: `DOCTRINE_INDEX.md` (skill row + coverage rows; also added the previously-unindexed
  CS-3 enforcement layer — runner, loop.json, queue.json, predictions/, verdicts/), `CORE.md` routing
  row, README pillar row + counts 23 → 24 (README, INSTALL_MULTI_HARNESS), GETTING_STARTED catalog,
  `campaign-status` supervisor assertions (driver log present; no stale un-relayed inbox note;
  operational shelvings reviewed as environment findings).
- **Found by the cockpit walkthrough + a fresh-agent audit of the new doctrine (mechanism-diverse
  check), fixed here:**
  - **`results/STOP` was never implemented in the driver** — four docs promised the graceful stop, no
    driver version checked the sentinel (a CS-3-era doctrine/enforcement fork; the only working stop
    was Ctrl-C, exactly the gap the cockpit claims to close). The driver now honours it at the loop top
    (unit in flight completes and records; exit 0; recorded in `results/loop_stops.log`), preflight
    flags a leftover sentinel, and tier-2 scenario D3 pins it.
  - **Driver JSON readers are now BOM-tolerant** (`utf-8-sig` for queue.json/loop.json/inbox) — the
    walkthrough's preflight caught that a PowerShell-written (`Set-Content -Encoding utf8`) queue.json
    carries a BOM and failed plain-utf-8 parsing; any Windows hand-edit would hit it.
  - The concierge fence rewritten with an explicit write surface + named exceptions (ledger repairs are
    propose-then-user-go-ahead, never own-judgment); the "idle cheaply" stance no longer cites
    `hardware-in-the-loop.md` for a claim its current text doesn't make; the cockpit now owns the
    progress alarm (CORE: monitor progress, not liveness); guidance added for the Stop hook re-arming
    when the driver is down (relaunch or `results/STOP`, never start executing units).
  - Charter loop step 12 carries the supervisor caveat inline (worker = steps 1–11 for ONE unit;
    REPEAT is the driver's); stale "single-session mode" vocabulary retired in `campaign-status` +
    `new-campaign`; the driver creates `results/inbox/` at launch; `{{PYTHON_CMD}}` no longer appears
    as a literal in any skill body.

### Changed — supervisor-mode hardening: degrade-loud driver, liveness in code, preflight, live feed, inbox (SV-1..SV-5 + ADR-0009, 2026-08-12)

Motivated by the first REAL supervised campaign run (2026-08-11, user report): one worker went into
background mode, never validated, and the halt-everything driver killed the whole overnight loop; separate
launch false starts; no live view of headless workers and no inbound steering channel. All driver-behavior
changes are in `templates/campaign/scripts/run_campaign.py.tmpl` unless noted; the halt-taxonomy decision
is **ADR-0009** (amends `STRUCTURED_LOOP_PROPOSAL.md` §4.1's "eager halting — annoying, safe", which the
overnight death falsified).

- **SV-1 — the halt taxonomy splits by failure kind.** INTEGRITY conditions keep the hard halt (ESCALATE ·
  queue empty after a planner pass · corrupt `queue.json` — NEW, it previously silently defaulted to an
  empty queue · preflight/metric-selftest failure · planner failure after one retry). An OPERATIONAL
  failure (worker spawn error / timeout / unit unvalidated after retries) now records onto the unit
  (`failures` list), shelves it (`kind: "operational"`, planner-revivable) and the loop CONTINUES;
  N consecutive operational failures (`driver.max_consecutive_failures`, default 3) is SYSTEMIC and halts.
  Halt reasons now go through the driver log, not only stderr.
- **SV-2 — dead-worker detection is structural.** The runner maintains `results/.run_heartbeat` (stage
  transitions + a 60 s ticker through the solve); the driver's watch loop counts a worker alive on stdout
  lines OR heartbeat mtime-change, kills on `worker.inactivity_timeout_min` of neither (absolute cap
  retained), and — the 2026-08-11 signature — a worker that EXITS with a fresh heartbeat gets a bounded
  detached-runner grace (`driver.detached_grace_min`) for the save-set to land before the unit is judged.
  Kept doctrine-clean: mtime-change only, dead-vs-alive only — progress stays the ledger's job (CORE
  "monitor progress, not liveness").
- **SV-3 — preflight.** `--preflight` (also automatic at `--supervise` start, before any spend): agent CLI
  resolves + answers, `loop.json` parses + carries every hard-dereferenced key, `queue.json` schema-sane,
  required tree files, metric selftest (shared seam `metric_selftest_message()`), ESCALATE surfaced; ALL
  failures reported together, each naming its fix; opt-in `--smoke` does one real spawn.
  `validate_campaign.py` gained the matching scaffold-time parse checks.
- **SV-4 — the driver keeps a log and renders the worker feed.** Every launch writes
  `results/diagnostics/supervise_<ts>.log` (append-only decision trace — the driver previously logged
  NOWHERE, contradicting `hardware-in-the-loop.md` §5's own rule); workers spawn with
  `--output-format stream-json --verbose` per `driver.stream` = `auto` (default: only the default claude
  CLI) / `on` / `off`, rendered one compact line per event (tool calls, text snippets, result).
- **SV-5 — `results/inbox/`.** User notes (`*.md`/`*.txt`) are relayed VERBATIM into the next
  worker/planner prompt (concatenation, never `.format` — brace-safe), then archived to
  `inbox/archive/<stamp>_<name>`; whole-note deferral at the size cap, explicit truncation marker for a
  single oversize note; both prompts instruct acknowledgment in the journal. Steering without killing the
  loop; ESCALATE stays the loud outbound channel.
- **Driver-alive stand-down (`templates/campaign/scripts/loop_heartbeat.py.tmpl`).** The driver maintains
  `results/.driver_alive` (refreshed ≤30 s, removed on exit); while it is fresh the Stop hook stands down
  for ATTENDED sessions — without this, any session opened in a live campaign root (the run-campaign
  concierge, a user checking in) is blocked toward the 25-block stall release. Same rationale as the
  existing worker stand-down, extended; a crashed driver re-arms the hook within
  `AUTORESEARCH_DRIVER_ALIVE_WINDOW_MIN` (10 min). The hook's block message now points at supervisor mode
  (`--supervise` / run-campaign) before the by-hand loop steps.
- **Fixed in passing: `AUTORESEARCH_AGENT_CMD` with a space in the interpreter path never worked** — the
  CS-3 driver split it with `str.split()`, so `C:\Program Files\...\python.exe` became `C:\Program`.
  Now quote-aware (`_parse_agent_cmd`); caught by the new preflight on this lab machine's own `py -3`.
- **The CS-3-V regression harness is now IN-REPO** at `tests/structured_loop/` — promoted from the
  session scratchpad it was still living in (the exact at-risk arrangement whose 2026-08-08 predecessor
  the 0.7.0 notes record dying), de-hardcoded to repo-root-relative paths, and extended from 5 to 17
  driver scenarios incl. the detached-runner regression test for the 2026-08-11 failure;
  `test_loop_heartbeat.py` gained the SUPERVISED + driver-alive stand-down cases (38 checks).
  Suites at ship: tier 0 27/27 · tier 1 29/29 · tier 2 62/62 · heartbeat 38/38. (The separate
  out-of-repo tetracoil fixture at `kit-tests/loop-e2e-tetracoil/` still asserts the OLD
  retry-once-then-halt driver behavior and needs a matching update — flagged, not done here.)
- Threaded: `configs/loop.json.tmpl` (new `driver` section, all literals — no new placeholders, no new
  interview burden; stale `ADR-0006` ref → `ADR-0008`), `charter.md.tmpl` "How the loop runs",
  `checkpoint.md.tmpl` §0, `new-campaign/SKILL.md` Step 5's driver description,
  `STRUCTURED_LOOP_PROPOSAL.md` (stale "PROPOSED — nothing applied" banner fixed + §4.1 amendment note).

### Changed — a hardware loop idles cheaply while it waits; it does not manufacture work (HL-1, 2026-08-11)

`docs/reference/hardware-in-the-loop.md` told the loop to fill an instrument wait with off-instrument
work (analysis, critique, literature). The **deployed loop removed it: it burned more agent budget than
it returned.** The instinct is sound — waiting is otherwise dead time, and the work is often worth doing
— but the while-waiting pattern exists to protect the autonomy budget, and substituting a more expensive
kind of spin defeats the guard.

- **§0 step 4** (the assembled loop) and **§3** (graceful busy behavior) now say **idle cheaply**: poll
  the acknowledgment channel at a calm fixed cadence and no more, then resume cleanly — re-running any
  staleness-sensitive calibration — when the rig frees up.
- A new §3 bullet states the rule positively so the instinct doesn't quietly return: do queued
  off-instrument work **because it was queued and is worth its cost — never to fill a gap.**

### Changed — a generated campaign's `CLAUDE.md` carries only what the loop acts on (CO-1/CO-2, 2026-08-11)

The campaign template's header comment is gone. It explained kit-design decisions to the campaign agent —
why the doctrine spine is inlined rather than `@`-imported, how freeze-and-stamp follows from the kit-dev
single-source rule, and a scaffolding-time "start a fresh session" note. `CLAUDE.md` is re-injected every
turn of every session, so non-actionable text there is a permanent context tax. Motivated by a user
finding on a campaign scaffolded that day.

- **Removed** the 11-line comment from `templates/campaign/CLAUDE.md.tmpl`; nothing operational was lost —
  the don't-hand-edit / re-scaffold-or-fork fact is stated once in the spine's provenance banner, and the
  fresh-session launch is `new-campaign` Step 5's handoff message to the *user*.
- **`new-campaign` Step 3** now states the rule that prevents its return: the generated `CLAUDE.md` carries
  only what the running loop acts on — no kit-design rationale, no scaffolding-time instructions, no
  header comment.
- **Spine tailoring (Step 3.2)** now drops `CORE.md`'s YAML frontmatter, which is kit-internal routing
  metadata rather than doctrine and would otherwise be rendered into the campaign spine verbatim.

## [0.7.0] - 2026-08-11

The structured-campaign-loop release: the loop's procedural skeleton moves from prose into code (gates in
the runner, a deterministic supervisor driver, fresh context per iteration), each campaign carries a frozen
provenance-stamped snapshot of the doctrine that governed it, and the promotion gate is bound to an
affirmative, current correctness green. Two promote/accept-path bugs found by the second end-to-end pass are
fixed here as well.

**Deploy note.** The previously shipped plugin (0.6.0, cached from a 2026-07-21 commit) predates every
change below, and both source and cache declared the same version — so an update had nothing to key on.
This bump is what lets the release actually reach agents; refresh the plugin after installing it.

### Fixed — two bugs on the promote/accept path (LT-1, LT-2, 2026-08-10)

Both found by a new out-of-repo loop-test fixture (a four-coil uniformity toy with known ground truth,
run as static / gate / driver tiers), built because the 2026-08-08 acceptance harness lived in a session
scratchpad and died with it — leaving F-2, EH-8, EH-9 and ML-4 shipped but never exercised end-to-end.

- **`"refuter": null` promoted a finding on both surfaces.** `guard_discoveries._check_verdict` used
  `str(v.get("refuter", ""))`, and `str(None)` is the non-empty string `"None"`, so an explicit JSON null
  passed the independent-refuter check — hard gate #1's whole warrant. Missing key, `""` and whitespace
  all denied correctly; only `null` slipped, which is precisely what a model leaves behind when it copies
  the verdict stub without filling the field (and precisely the artifact F-2's own evidence describes).
  Now `str(v.get("refuter") or "")`.

- **A declined-then-completed unit livelocked the supervisor driver.** `declined` was read from a
  persisted list that nothing clears, and was tested before `done`, so a unit that was declined once and
  executed on a later pass was never accepted, never removed from the head of the queue, and was re-run
  on every subsequent iteration — appending a real scoreboard row each time while `accepted_units` stayed
  at 0 (measured: 137 rows, zero accepted). That is the drift-silent failure the structured loop exists to
  replace, reachable with every actor following the documented protocol. The driver now tests `done`
  first: the save-set on disk is the ground truth for "this unit happened".

### Changed — one lever per experiment is a default, not a law (ML-1..ML-5, 2026-08-10)

The rule was absolute on every operational surface, which foreclosed two legitimate cases: **interaction-
dominated spaces** (levers that behave differently in combination — a space one-at-a-time search cannot
explore by construction) and **exploratory screening**. A fork was already present — the principles master
has said "default, not a hard rule" since v3.7, while the charter loop said "Pick **ONE** lever."

**The reframe: multi-lever spends *attribution*, not validity.** Moving several levers together is
legitimate for coupled levers (where holding one fixed measures a broken configuration, so one-at-a-time is
*wrong* rather than merely slow), a screen, or a designed interaction test. Campaign surfaces carry only the
light form — weigh the cost, record which levers moved. The discipline lives in `verify`.

- **A current-best may be promoted without knowing why it won.** The empirical claim ("config X scores Y")
  is attribution-independent and may be CONFIRMED and promoted; the **causal** claim ("lever L is why")
  cannot be CONFIRMED while levers are entangled — it is QUESTIONABLE ASSUMPTION with the confounded set as
  its named premise. The *No claim-splitting* rule is now scoped explicitly: it guards the config's
  validity, not attribution among its levers.
- **A multi-lever negative kills only the combination.** This is the asymmetric risk: the verification
  apparatus is aimed at positives, so a multi-lever win meets the refuter, the verdict artifact, and the
  promotion gate, while a multi-lever loss just updates the journal. The mechanism to hunt is **masking** —
  lever A helps, B hurts more, the combination scores below baseline, and both get retired. The combination
  may earn `EVIDENCE_AGAINST`; every member is INCONCLUSIVE and **remains untried**.
- **New verdict fields** `confounded_levers` / `disentangler` / `resolves_confounded`. Confounding is a
  property of the design, orthogonal to the verdict — the same shape as `kill_tier`. Deliberately not a
  boolean: a non-empty set *requires* the disentangling experiment, and the debt closes only when a later
  verdict names the levers it separated. `verify` gained a *Confounded attribution* section that fires
  whenever more than one lever moved.
- **`loop_heartbeat` refuses an `exhausted` stop while any lever sits in confounded limbo.** Without it a
  confounded negative empties `untried_levers` and one bad combined experiment can end a campaign.
- **`assumption-audit`** now rules out the cheaper rival diagnosis first: a cross-family floor may be an
  interaction-dominated space rather than a wrong inherited value.


### Removed — the example charters; archetype guidance replaces them (EX-1/EX-2, 2026-08-10)

`examples/` is gone. `new-campaign` now starts from `templates/campaign/` and the archetype guidance,
never from another campaign's filled charter. Motivated by a user finding: the four pre-v0.3 charters
(archetypes A/B/D/F) were self-documented as out of date — their own README told the reader they
"predate the current methodology" and were "not current best-practice templates" — and, being *filled*
single-subfield instances (all NV-magnetometry/ASI), they anchored the setup interview toward their
specific metric, lever, and guardrail choices.

- **Removed** `examples/charter-files/` entirely: the four stale charters, then
  `charter_hardware_loop.md` once its content was folded into guidance (below).
- **Folded into `docs/reference/hardware-in-the-loop.md`** — everything the archetype-E charter carried
  that the reference doc did not: a new **§0 "An example loop, assembled"** (the six-step iteration —
  propose with an a-priori bound → emission gate → dispatch → while-waiting → ingest → analyze — as an
  illustration of how §2–§8 compose, since the doc had every component but never the ordering);
  operational guarantees as **deliverables equal to the number** (intro); **blinding** the accepted
  value from the loop so "not a number to tune toward" is mechanical rather than aspirational (§1);
  a crash mid-campaign is an **operations bug to fix and re-gate**, never evidence against the physics
  idea (§1); quarantine thresholds **ratchet only toward more faithful**, versioned (§6); the hardware
  scoreboard columns — `T_wall` estimated AND actual, calibration age at start, quarantine
  status+reason (§8).
- **Folded into `ARCHETYPE_CHEATSHEET.md` §E:** normalizing the primary metric by instrument time
  (`1/(σ·√T_wall)`, true wall-clock from run records, not nominal sequence time) — time is the binding
  budget, so a metric blind to it ranks a ten-hour marginal gain above a one-hour one; and
  passed-quarantine + calibration-in-window as an explicit **precondition of promotion**.
- **Fill guidance de-stylized** (`new-campaign` Step 3, `PLACEHOLDERS.md`): the old rule asked the
  filling agent to match the boilerplate's *voice* and read "as naturally as a hand-written charter" —
  a human-reader premise. Now: clear, explicit, concise, specific enough to act on without the
  interview that produced it.

### Added — the structured campaign loop: gates in code + supervisor mode (CS-3, 2026-08-07)

The charter stays the campaign's constitution; its procedural skeleton now lives in **structure** —
motivated by campaign 03, where every prose gate was present and skipped (2 verify calls / ~184 solves)
while the one code-enforced gate held. Full spec: `synthesis/STRUCTURED_LOOP_PROPOSAL.md`; ADR-0008.

- **Artifact gates in the runner** (`run_campaign.py.tmpl`): the **prediction gate** (no solve without a
  falsifiable a-priori range in `predictions/<exp>.json`, written before the run, snapshotted with it) and
  the **save-set gate** (no scoreboard row until result JSON + figure + snapshot exist). Out-of-envelope
  scores stamped into the result JSON as red flags.
- **`guard_discoveries` redesigned**: per-finding **verdict artifacts** (`results/verdicts/<id>.json`,
  written by `verify` with a named refuter) replace the 60-minute transcript-window heuristic; every
  DISCOVERIES entry cites its verdict file; **fail-closed on the promote path**. Negative-tested (11 cases).
- **Steering-negatives are discoveries** (`DISCOVERIES.md.tmpl`, `charter.md.tmpl`, `verify`): a negative
  the campaign acts on is promoted under the same gate with a **kill tier** — REFUTED (prunes) /
  EVIDENCE AGAINST (shelved, revivable, accumulates) / INCONCLUSIVE (never graduates; fix-and-rerun).
  `verify` gains the negative-refuter checklist (implementation error / strawman / insufficient search /
  mechanism) and **ADR-0008 cost-tiered reproduction** (re-score from raw always; full re-execution below
  the `loop.json` threshold; judgment + cheapest discriminating spot-check above — never zero).
- **Supervisor mode** (`run_campaign.py --supervise`): a deterministic driver pops units from
  `results/queue.json`, spawns a **fresh-context worker agent per unit** (frozen spine + charter auto-load),
  validates the **iteration contract** (`protocols/checkpoint.md` §0 — the ledger is the loop's only
  memory), and spawns a read-mostly **planner agent** on triggers (queue low, cadence *k*, declination,
  dual-denominated plateau). Execute-or-decline; two declinations shelve (revivable); `ESCALATE.md` halts;
  empty queue halts as an explicit stopping decision. Halt-loud beats drift-silent. Smoke-tested (5
  scenarios, stub agents).
- **`configs/loop.json`** (new template): per-campaign knobs set at scaffold from unit cost (cadence
  *inverts* with cost), user-owned thereafter; planner/worker models configurable. 10 new placeholders.
- **Wiring**: `new-campaign` interviews the knobs (topic 8), seeds `queue.json` (exp 000 + user ideas),
  creates the gate dirs, and hands off via `--supervise`; `campaign-status` asserts the whole enforcement
  layer + reviews the SHELVED pool; `validate_campaign.py` requires `loop.json`, `queue.json`,
  `predictions/`, `results/verdicts/`.

### Changed — campaign `CLAUDE.md` freezes-and-stamps the doctrine spine (2026-08-07)

- **`new-campaign` now renders a campaign-tailored, FROZEN snapshot of `docs/CORE.md` into each campaign's
  `CLAUDE.md`** (the new `{{PHYSKIT_SPINE}}` block), stamped with its provenance (physkit version · CORE ref ·
  date · spine hash) and a "do not hand-edit" banner. The snapshot is part of the campaign's reproducible
  record — deliberately **not** re-synced against a later CORE.md, and **not** an `@CORE.md` import or a
  vendored+hash-checked `PHYSKIT_CORE.md` copy. The template's old thin "Frozen core" 5-bullet summary is
  removed, subsumed by the full Constitution the snapshot carries; the campaign-specific HARD GATES + frozen-
  metric identity stay. Motivation: a real campaign (`03_hbn_vb_circular`) ran a week with the spine out of
  context (0 CORE-phrase occurrences; 2 verify calls in ~2095 tool calls). Scoped in kit-dev `CLAUDE.md`
  §single-source (developing-the-kit minimizes forks; using-the-kit freezes-and-stamps). This addresses
  doctrine **availability**, distinct from the Opus-5 instruction-*precedence* regression (2026-08-06 Theme F).
  Loci: `templates/campaign/CLAUDE.md.tmpl`, `skills/new-campaign/SKILL.md` (Step 3), `templates/PLACEHOLDERS.md`,
  `docs/DOCTRINE_INDEX.md`; ledger `synthesis/BUILD_BACKLOG.md` CS-1/CS-2.
### Added — a comparison's scorer is a candidate for being wrong; a disputed verdict escalates to a blinded third party (`E--ASI` `sw_freeze_audit`, 2026-08-03 → 08-06)

Motivating evidence: `@transcript_asi-swfreeze_2026-08-03` — a day in which an independent verification pass
refuted **4 of 6** of the session's own load-bearing claims, was then itself refuted on the one claim it had
reversed, and the agent's rebuttal of *that* was refuted in turn by a blinded adjudication. The same
conclusion was argued for three times by three different wrong arguments, each with one defect: **a
comparison whose scorer, reference, or starting point was entangled with one of the things being compared** —
a scorer that was the incumbent's own response family; a "neutral" arbiter silently importing the incumbent's
fitted nuisance parameter (agreement to 2.8e−14); a sweep scored against its own starting point, making zero
shift the argmin for *every* candidate. Separately, four distinct statistic-choice slips in one day, and a
MuMax run that scrambled to `|m| ≈ 7e-4` behind exit code 0, no NaNs, and an ordinary convergence metric —
reading exactly like the effect under study, at a cost of ~7 GPU-hours.

- **`verify` §2 gains an entanglement gate** — name the scorer, the reference, and the starting point, and
  state what each shares with the candidates. Two tells: the argmin is the incumbent for *every* candidate,
  or the neutral arbiter reproduces one candidate's fitted parameter exactly. The campaign refuter prompt
  (step 4, metric integrity) and the checklist carry the same check.
- **`verify` §4b — when the verdict is disputed, escalate; don't defer and don't re-litigate.** A third
  agent, blinded (positions relabelled, provenance stripped, told not to weight by source) and required to
  run a check *neither* analysis ran. Its verdicts include *both wrong*. A dispute closed by argument rather
  than by a new measurement is still open — and a rebuttal you wrote yourself is not independent of the
  reasoning the checker was called to test. Campaign mode routes load-bearing disagreements here.
- **`verify` §3 — does the statistic answer the question you asked?** Mean where a max belongs (a
  sign-changing quantity nearly cancels); an unpaired spread on a paired comparison; a central statistic
  where the hypothesis is "rare and large"; a fitter fed *(data − model)*.
- **`debug`'s gotcha catalog gains the silent failure that *imitates* the hypothesis** — the gate is a
  physical magnitude floor calibrated on a validated corpus, not the solver's own status. `correctness-suite`
  §4 says the same about promoting that class of bug to a standing gate.

### Changed — sub-agent delegation is pre-authorized; the prompt surface includes the harness (user report + `E--ASI` session, 2026-08-06)

Motivating evidence: Claude Code 2.1.221 appends *"Do not call the AgentTool unless the user requested it"*
to every session on `claude-opus-5` — compiled into the CLI (array `GUp`), gated on the
`opus_5_prompt_bundle` model capability plus a server kill-switch, so it is absent from every settings file,
absent from the kit, and absent on every other model. Agents obeyed it over the kit: hard gate #1's refuter
skipped, prescribed skills abandoned mid-run, loops paused to ask permission. In one session the agent
stated it "followed that over the skill's prescription" and substituted controls of its own design; two
headline correlations (r = 0.873, 0.879) reached a report that a belated independent check invalidated —
the *wrong-configuration* control scored 0.882.

- **Campaign `CLAUDE.md` carries a standing authorization.** A skill that prescribes a sub-agent *is* the
  request; never pause a loop to ask, never substitute a self-run check. Inability to spawn is a BLOCKER —
  record it and stop, don't promote on a self-run check.
- **`verify` §4 closes the silent-substitution path:** no sub-agent ⇒ the check is **INCONCLUSIVE**. A
  control you designed yourself tests the confounds you thought of — which are the ones you already handled.
- **`prompt-surface-audit.md` gains a sixth surface** (the harness-injected, model-conditional bundle) and
  with it a second audit direction: the other five surfaces fail by *omission*, this one by *contradiction*,
  so grep the render for a rule's **opposite**, not only for the rule.
- **`CORE.md` step 5 and the dev `CLAUDE.md` step 3** state the same in the two spines.

### Added — the loop keeps running until you stop it (a Stop gate, not a reminder) (user report, 2026-08-03)

Motivating evidence: campaigns "aren't actually able to run autonomously for long periods — they end up
stopping after a task is complete." The anti-premature-stop norm was already in the kit three times over, in
prose; a turn ends when the model emits no tool call, and prose does not survive that moment. So it is a gate
now — the kit's own "enforce, don't exhort" applied to the one action prose cannot reach: termination.

- **New `scripts/loop_heartbeat.py`** (Stop hook, wired in `.claude/settings.json` alongside
  `guard_discoveries`). It refuses an end-of-turn and hands the agent back the campaign's own next action —
  the `JOURNAL` **NEXT** pointer, the open threads, the next exp id. Never a generic "keep going".
- **Three ways a loop may end, all recorded.** `results/STOP` (human, graceful — the agent finishes and logs
  the experiment in flight, unlike `Ctrl-C`) · `results/stop_request.json` (agent, earned: a reason code from
  a closed vocabulary — `user-fork` / `irreversible-action-confirm` / `hard-blocked` / `exhausted` — plus
  evidence) · the stall release. Every stop lands in `results/loop_stops.log`, so "why did this campaign end?"
  is answerable from the ledger.
- **`exhausted` is hard-gated:** refused while `untried_levers` is non-empty, and it requires a
  `campaign-status` run within 2 h. A campaign may not declare itself finished while holding a lever it has
  itself named as untried.
- **Anti-runaway:** ~25 continuations with no new scoreboard row escalates the reason, then releases the loop
  and records `STALL_RELEASE` — a loop that is alive and producing nothing is a dead run, not progress.
- **Safe by construction:** inert until the campaign is live (so it can't trap the session still building the
  tree), never blocks `SubagentStop` (which would trap the independent refuter), fails open with a logged
  bypass, and `AUTORESEARCH_LOOP_HEARTBEAT=off` disables it.
- Threaded through `charter.md` (new **Ending the loop** section + step 12), `CLAUDE.md` (hard gate 5),
  `new-campaign`, `validate_campaign.py`, `campaign-status`, `checkpoint.md`, `GETTING_STARTED` (a
  **Stopping the loop** section + troubleshooting), `CORE`, `PRINCIPLES`, and `DOCTRINE_INDEX`. Regression
  suite: `kit/skills/new-campaign/scripts/test_loop_heartbeat.py` (32 checks).

### Changed — every campaign lives in a project; standalone mode retired (user request, 2026-07-18)

- **`new-campaign` Step 0.1 now *establishes* the project home rather than detecting a mode.** It uses the
  ancestor project if one exists, else runs `new-project` to create it, then continues. Physics / conventions /
  instrument are always `../../shared/…`; data is always `../../data`; a `LINEAGE.md` row is always appended;
  the campaign `CLAUDE.md` project-context block is always kept. The charter's *Relationship to sibling
  campaigns* block stays conditional — **coupling** decides it, not project membership.
- **The bare-campaign mode is gone**, and with it the `_<NAME>`-suffix multi-stage fallback: each stage is a
  sibling campaign. A legacy bare tree is **lifted into a project** (Step 0.1). Threaded through
  `new-project`, `fork-campaign`, `campaign-status`, `handoff`, `final-report`, `report`, `record-decision`,
  `verify`, `literature-review`, `GETTING_STARTED`, `README`, `INSTALL_FOR_TESTERS`, `DOCTRINE_INDEX`, `CORE`,
  `PLACEHOLDERS`, `ARCHETYPE_CHEATSHEET`, and `SIMULATION_VALIDATION`.
- **The validator enforces it.** A campaign with no project home fails; a campaign-local copy of a shared doc
  fails (previously caught only at project scope); `sessions/` joined the required project dirs; and project
  detection now matches on the parent directory *name*, so a `sessions/<date>_<slug>/` folder is no longer
  mistaken for a campaign.
- **Retired** `templates/campaign/docs/PHYSICS.md.tmpl` + `CONVENTIONS.md.tmpl` — their unique content (the
  Buckingham-π dimensionless-groups bullet; the symptom→check gotchas catalog) was merged into
  `templates/project/shared/` first. **Fixed** `templates/project/LINEAGE.md.tmpl`, whose 7 ceremonial example
  placeholders made a fresh project fail validation.
- Motivation: a bare campaign that later needs a sibling, a fork, or an ad-hoc follow-up session requires
  reorganization plus path rewrites, and `sessions/` existed only in a project — so bare campaigns had nowhere
  to put non-campaign work. Cost measured, not estimated: ~5 near-empty files (the shared docs move, they don't
  multiply); a rendered one-off project validates clean on the documented interview placeholders alone.
  Record: **ADR-0007** (`synthesis/DECISION_RECORDS.md`) — carries the B8 revisit-if. Sign-off: approved
  in-session 2026-07-18. Ledger: `synthesis/BUILD_BACKLOG.md`.

## [0.6.0] - 2026-07-11

### Added — organize ad-hoc work (working-loop step 6 / Traceability; user finding, 2026-07-15)

- **CORE loop step 6 + PRINCIPLES §7 (Traceability) — give work worth keeping an organized home even with
  no campaign scaffold.** Real artifacts, findings, and the reasoning behind them earn a sensible
  subdirectory and a short, **maintained index** (what's where, and why) — never a deliverable that lives
  only in the conversation or as loose files scattered across a shared directory. Generalizes the
  discipline the campaign scaffold enforces automatically to **plugin-only / ad-hoc** sessions (the same
  enforcement-evaporates-without-the-scaffold pattern as the 2026-07-01 ASI plugin-only keepers).
  Motivation: user finding 2026-07-15 — agents save & organize well inside campaigns but often not at all
  in ad-hoc sessions launched from the same directory. Recorded as PRINCIPLES v1.10; propagated from the
  content master `synthesis/PRINCIPLE_TAXONOMY_v2.md` O-6 (v3.11). Sign-off = this change's approval.
  Ledger: `synthesis/BUILD_BACKLOG.md` (AH1).

### Added — assumption-audit skill + prompt-surface-audit doctrine (lab-loop keepers, 2026-07-07)

- **`skills/assumption-audit` (new).** The plateau mode-change from optimizer to diagnostician: when
  one-lever experiments across ≥2 lever families pin at the same floor (or the best result sits far from
  its own a-priori expectation), the stall may live *upstream* of every lever in a wrong **inherited**
  value — a calibration, a derived quantity, or a classification that every experiment silently carries.
  The skill enumerates the inheritance with provenance tags, ranks suspects by
  would-being-wrong-reproduce-this-stall, and buys ONE discriminating experiment under two hard clauses:
  **solve, don't confirm** (the test estimates the suspect value from scratch; a consistency check invites
  reading a mismatch as an artifact) and **operating-point validity** (re-derive any calibration crossing
  an operating-point boundary — a falsification run with an out-of-point calibration can refute a *true*
  hypothesis). Wired into the charter's *Getting Unstuck* block (third bullet) and `campaign-status` §4
  re-plan as the response to a plateau that *resists* lever escalation — the gap being that all previously
  prescribed plateau responses were pivot-escalation (change lever), none a change of *mode* (question
  assumptions) — `pivoting.md` gains the fifth diagnosis row (**Inherited-value-wrong**) and CORE's
  "plateau is a pivot signal" line gains the second species (frozen-doc sign-off = this PR's review).
  Motivation: a hardware-commissioning loop (2026-07) miscounted the lines of a resolved spectral pattern
  (read from memory of the canonical case rather than from the data), inherited a detection frequency a
  few kHz off from it, and pinned dozens of one-lever arms at the same SNR floor while its own signal sat
  in the data — it even ran the right discriminating measurement, framed as *confirmation* of the
  incumbent value, and read the mismatch as an artifact.
- **`docs/reference/prompt-surface-audit.md` (new) + a Ctx9 PRINCIPLES bullet (tightening; frozen-core
  sign-off = this PR's review).** Doctrine only governs an agent whose RENDERED context contains it:
  subagent prompts *replace* the doctrine stack (inherit nothing from CLAUDE.md), SDK-spawned loop roles
  may load no always-on files, and **dynamically rendered** surfaces (observation digests) are part of
  the prompt surface — auditable both for missing doctrine and for stowaway contamination. The audit:
  enumerate roles → list relied-upon rules per role → capture each context *as rendered* → grep for every
  rule → gate the launch on it, re-running after any prompt change. `new-campaign` Step 5 gains the
  launch-checklist bullet and `campaign-status` §2 the matching hygiene check. The Ctx9 principle is
  recorded as PRINCIPLES v1.9; **propagation to the content master (taxonomy) is pending** per the
  derivation note. Motivation (2026-07, same program): two disciplines the designers relied on
  were simply absent from an SDK loop's rendered prompts (each hole cost real instrument time), and a
  static-file leak audit stayed green for two full campaign arms while a dynamically rendered digest
  carried a stale false fact into every round.

### Changed — abstract-only reading discipline: conclude on full text, not the abstract (B5, 2026-07-05)

- **`skills/cite-check` now separates *existence* from *claim-support*.** Confirming a paper exists and its
  metadata may use the abstract page; confirming it **supports the claim** must read the relevant full-text
  section. Support established only from an abstract is a new **PROVISIONAL** grade (flagged
  `read: abstract-only`) that cannot alone carry a claim to "well-evidenced," and every verdict records its
  read-depth. **`skills/literature-review`** gains *screen on abstracts, conclude on full text* plus two
  failure-mode guards — **abstract-driven conclusions** and **confirmation-seeking search** (a paper that
  complicates or refutes the sought claim is a successful result, not a failed row). **`report`/`final-report`**
  thread the PROVISIONAL grade so abstract-only support is carried provisionally, never laundered into
  "established." Motivation: a testing session where the agent gave a ~90%-right reading of an arXiv *abstract*
  then reversed once the full paper loaded (`@meeting_agentic_2026-07-02a` 01:22:01→01:22:28), corroborated by
  three papers ingested as pillar support that a full read showed *complicate* the claim
  (`LIT_SEARCH_BACKLOG.md` item 14). Maintainer-side (KB) companions: a `Read status` field in the resource
  registry + `add-new-resource` / `ingest-transcript`. (User-approved, 2026-07-05.)

### Changed — unified always-on spine: CORE.md is now the single source; CLAUDE.general.md retired (2026-07-03)

- **`templates/CLAUDE.general.md` deleted; `docs/CORE.md` is the one spine.** Motivation: in plugin-only
  mode a doc read once falls out of context over a long session, while CLAUDE.md content is re-injected
  every turn — and maintaining the template as a separate copy had already let the two drift apart. Users
  now make the spine always-on with a one-line import in their project `CLAUDE.md`
  (`@<kit>/docs/CORE.md`), or by copying CORE's body (fallback). `GETTING_STARTED.md` §1,
  `INSTALL_FOR_TESTERS.md` Step 1, and the `DOCTRINE_INDEX` row updated. (User finding + decision,
  2026-07-03.) CORE also gained: the **universalism** constitution bullet extended with the concise
  **literature-disagreement weighing rule**; a **traceability** constitution bullet (a result isn't real
  until recorded and reproducible; provenance never fabricated); **pass-the-why** in the loop's delegation
  step; and the restored **register-vs-facts** line in Honest reporting.
- **CORE working-loop additions (2026-07-04, user-approved):** Frame step += **check what already exists**
  (prior runs, repo artifacts, literature) and **settle statically-answerable questions before an
  expensive run** — an environment check (is there actually a GPU, and is the job using it?) beats hours
  of misplaced compute (recurring failure observed in testing); loop closes with an **iterate coda** (a
  surprise updates the frame, not just the log); step 4 + Honest reporting += **uncertainty-first**: every
  newly derived number carries a propagated uncertainty estimate, PROVISIONAL (value *and* band) until
  systematics are investigated — mirrored into `PRINCIPLES.md` §5 (v1.8) and the taxonomy (v3.7). Also
  2026-07-04 (user edit): the **A3 narration line removed** from the spine ("name the skill as you go") —
  the behavior appears to occur by default; kept under observation during testing. The A1 proactive-
  suggestion line stays.
- **Spine content updated to taxonomy v3.4/v3.5** (`synthesis/PRINCIPLE_TAXONOMY_v2.md`): new
  **Universalism** section (weigh every claim by its evidence, never its source — the researcher's, the
  literature's, your own; includes the literature-disagreement weighing rule, elevated from the campaign
  charter); constitution's reporting kernel extended with Feynman's **report-what-might-invalidate**
  standard; working loop gains **work-the-procedure-step-by-step** (pillar 5, renamed **Methodical
  inquiry**), the **winner's curse** re-verification clause, and **reproducible ≠ correct**; "When stuck"
  gains **never name a cause from resemblance** (→ `attribute-mechanism`); "Running unattended" upgrades
  the liveness check to **monitor progress, not liveness**. Trailing nine-context list replaced by the
  **nine pillars**; `PRINCIPLES.md` depth-pointers now cite sections by name (renumbering-safe until X1).
- **Decision #10 reconciled across the spine:** context economy is doctrine but **no longer in the frozen
  constitution** (it tracks model capability) — updated in the CORE body, `PRINCIPLES.md`
  frozen-core note, `DOCTRINE_INDEX.md` coverage row 7, and `reference/context-economy.md` frontmatter.

### Added — experimental measurement-science reference cluster (2026-07-03)

- `docs/reference/uncertainty-and-error-budgets.md` — statistical vs systematic, the error-budget table,
  propagation (+ Monte-Carlo where linear fails), quadrature/correlation traps, the Allan deviation & drift
  wall, reduced-χ², honest reporting. (Meeting-2026-07-02 item **B2**, scoped.)
- `docs/reference/systematic-errors.md` — hunting the biases that don't average down: reversal/null tests,
  vary-the-suspect bounding, auxiliary monitors, blind analysis, a usual-suspects catalog. (Item **B4**, scoped.)
- `docs/reference/noise-and-sensitivity.md` — a-priori noise floor / PSD, fundamental vs technical noise,
  sensitivity, the √N/√T law and where it breaks. (Net-new.)
- `docs/reference/calibration-and-drift.md` — trace-to-a-standard, drift characterization, staleness
  windows, A-B-A interleaving, judge-by-own-output, calibration versioning. (Net-new; lifts
  `hardware-in-the-loop.md` §4 into standalone measurement science.)

The four form a DRY cross-linked cluster (the Allan deviation lives once, in the uncertainty doc) and, with
the merged trio, cover the measurement lifecycle end-to-end (a-priori floor → acquire → extract → number +
uncertainty → hunt systematics → attribute). Field-standard methodology codified into the kit; canonical
sources named but flagged for `cite-check` (nothing fabricated).

### Added — mechanism attribution + extraction hygiene (lab-loop keepers, 2026-07-02)

- **New skill `attribute-mechanism`** — "simulate before you attribute": enumerate candidate mechanisms,
  build a minimal one-knob-per-mechanism model, sweep, keep only mechanisms that reproduce the observed
  numbers, falsify the survivor in a sharp limit. Fills the gap between `frame-problem`, `debug`, and
  `verify` for the "which physics caused this real signature?" question. Grounded in two dated cases from
  a live lab loop (a modulation mis-attributed to detuning that a 5-minute sim pinned on a 3% amplitude
  miscalibration; a pulse-phase-coherence question settled with a hard-pulse limiting case to 1e-7).
- `docs/reference/signal-extraction-pitfalls.md` — five extraction failure modes that manufactured fake
  signatures (or buried real ones) in real data: detrend-before-FFT, fixed-bin peaks tracking the noise
  floor, tuned-pipeline-vs-naive-re-extraction, incoherent averaging, low-SNR peak-picking; plus the
  two-question reflex (null control + independent path).
- `debug` gotcha catalog +3 (from the same loop's live bugs): latent geometry assumptions armed by
  calibration changes; success inferred from ambient state; path-dependent state resets.

### Added — archetype E gets its example + reference (from a real qualified loop)

- `docs/reference/hardware-in-the-loop.md` — eight operational patterns for hardware-in-the-loop
  campaigns (readiness gate; file-based agent–instrument handshake; pause-sentinel sharing;
  calibration-vs-science starvation guard; progress-not-liveness monitoring; ingest quarantine;
  deterministic emission-gate + mid-flight abort; irreversibility/caps/persistence). Every pattern
  answers a failure that occurred while qualifying a real autonomous loop on a low-field (~1 MHz 1H Larmor) NV-diamond-detected NMR
  spectrometer probing microscale sample volumes; thresholds
  are deliberately placeholders to be set from the instrument's own tolerances.
- `examples/charter-files/charter_hardware_loop.md` — the first archetype-E example charter
  (the cheatsheet's "no real example in the kit yet" gap), exercising those patterns end-to-end,
  including the known-answer readiness gate G-0 and comparability tags on the scoreboard.

Second batch of keepers from the 2026-06-30 transcript review (`case-studies/transcript_review_2026-06-30.md`),
plus the first improvements harvested from the Wieman 29-decisions map (`synthesis/WIEMAN_DECISIONS_MAP.md`).
Each tightens the frozen honesty/verification core; none weakens it.

### Project-structure redesign — housing a whole investigation (2026-07-01)
A **Project** layer now sits above campaigns (`synthesis/PROJECT_STRUCTURE_DESIGN.md`, decisions LOCKED). One
investigation, many campaigns + ad-hoc sessions, sharing `data/` + `shared/` by relative path (**referenced,
never copied**) under a single `LINEAGE.md` index — killing the data-duplication + broken-path problems that
bloated prior multi-version investigations (~422 GB across 8 sibling dirs, in the motivating case).
- **New skill `new-project`** — scaffolds the Project home (`PROJECT.md` · `LINEAGE.md` · `DISCOVERIES.md` ·
  `ENGINEERING_NOTES.md` · `shared/{PHYSICS,CONVENTIONS,INSTRUMENT}.md` · `data/` + a `DATA_PATH.txt` pointer ·
  `campaigns/` · `sessions/` · `reports/`), then composes `new-campaign` for the first campaign.
- **New skill `fork-campaign`** — the honest invalidation clean break (§4.4b): when a bug/correction invalidates
  a campaign's findings, archive it (frozen, still in `LINEAGE`), scaffold a fresh-ledger sibling, and carry
  forward ONLY findings that survive independent RE-verification (with provenance) — never a quiet version bump
  that lets a tainted ledger steer the next effort.
- **`new-campaign` is project-aware** — in a Project it references `../../shared` docs (no campaign-local copies),
  wires `../../data`, appends a `LINEAGE.md` row, and resolves the charter *Relationship to sibling campaigns*
  block (§5); tracks collapse into sibling campaigns, not `_<NAME>` suffixes. Standalone mode unchanged.
  `SYSTEM.md` retired → the PHYSICS "target of study" § + `INSTRUMENT.md` (each name unambiguous across subfields).
- **`campaign-status` gains a Project mode** — at a project root it reads `LINEAGE` across campaigns and checks
  cross-campaign FROZEN/MUTABLE (sibling-coupling) consistency; **`handoff`** resumes from `LINEAGE` and checks
  whole-tree portability; **`validate_campaign.py`** auto-detects and validates a whole Project tree
  (structure, every campaign indexed, no local shared-doc copies, no absolute paths in configs).
- **Knowledge base aligned** (§8) — registry gains optional `Project`/`Campaign`/`Session` provenance + `result`
  and `report` resource types; `ingest-transcript` records Project/Campaign/Session; the rigor-honesty
  (true-tier) rule carries across ingest. A per-project scoped KB (§9) is reserved but **not** built this pass.
- **Campaign charter renamed** `program.md` → `charter.md` (threaded across skills/templates). *Note:* older
  changelog entries above/below that reference `program.md(.tmpl)` predate this rename and are left as-written
  (the file was `program.md` when those changes shipped); the live template is `docs/charter.md.tmpl`.

### Skills & framing (from the Wieman 29-decisions map)
- **New general skill `assess-idea`** (Wieman decision 9): honest feasibility/worth triage of a research idea
  *before* committing — bounds it a priori, locates the crux + cheapest de-risking check, weighs worth, and
  returns GO / DE-RISK-FIRST / NO-GO with confidence + assumptions. The anti-hype counterpart to `verify`
  (licensed to say "no"). Standalone, and an **advisory** (never-blocking) pre-check composable by
  `new-campaign`. Registered in `DOCTRINE_INDEX` / `CORE` routing / `GETTING_STARTED`. *(Front-end cluster
  piece 1 of 3.)*
- **New general skill `literature-review`** (Wieman decisions 1, 7): survey a field honestly — trajectory,
  closest prior art, and the methods that *transfer* to your problem — **self-contained** (no `deep-research`
  dependency, for frictionless adoption), arXiv-first, with a **mandatory `cite-check` gate** so no fabricated
  reference survives; campaign-aware (writes `LITERATURE.md`, seeds `PHYSICS.md`). *(Front-end cluster piece
  2 of 3; `research-direction` deferred — see `synthesis/FRONT_END_CLUSTER_DESIGN.md`.)*
- **Predictive framework (W-PF)** made a first-class output of `frame-problem` (the mechanism + discriminating
  thought-experiments at a justified complexity) with a `PHYSICS.md` "Predictive framework" section; its
  revision log = the existing "Updates from discoveries" (placement provisional). Unifies Wieman decisions
  5, 8, 19, 20, 23.
- **Confirmation-bias reflection ritual (W-reflect)** — Wieman's reflection decisions 23–26 ("most important
  and hardest"): a `verify` §5c ritual (state the hoped-for answer → argue it's wrong → name the refuting
  observation → hear the resisted alternative), echoed in `campaign-status` and `program.md`; plus a
  **non-count reflection trigger** (reflect on surprise / plateau / before a stop / on wall-clock, not only
  every N experiments).
- **Front-end / reflection refinements (Wieman 7, 8, 12, 14, 27)** — `frame-problem` flags the
  crux/highest-uncertainty sub-steps with an acceptable-uncertainty bar (W-12) and enumerates candidate
  approaches before committing (W-8); `campaign-status` re-plan prioritizes directions by importance ×
  tractability × cost (W-14); `final-report` gains a "Broader implications & significance" section and the
  `DISCOVERIES` entry template an Implications line (W-27); `program.md` "idea sources" now captures the
  transferable method/analogy from a related solved problem (W-analogy). Closes out the applyable-anytime
  Wieman keepers.

### Added
- **Machine-checkable `tier` field** (Scout/Confirmation/Extended) on every JOURNAL and scoreboard row, so
  run-length cap-compliance stays auditable and can't silently drop off later entries. *(D3)*
- **Wall-clock liveness self-check** for long runs in `expensive-evaluation.md.tmpl` — arm a monitor for any
  run >~30–60 min (verify process alive AND log advancing; a stalled log is a dead run), don't wait to be
  asked. *(E1)*
- **"Known landmines / Do-not-repeat" block** in `ENGINEERING_NOTES.md.tmpl` — a pre-flight checklist
  re-checked before any matching action (GPU/detached/irreversible) and surfaced to the user before
  complying. *(E2)*
- **Environment-pitfalls guidance** (Windows MAX_PATH → short venv paths + `core.longpaths`, `py -3.x` not
  `python3`, shared-drive symlink limits) in `CONVENTIONS.md.tmpl` and `INSTALL_FOR_TESTERS.md`. *(F5/env)*
- **`verify` §5b — provenance, authority, and irreversible actions**: resolve conflicting facts to the
  highest-authority artifact (a derived statistic is weaker than its source); a fact acted on at
  INFERRED/RECALLED is a claim to falsify; an irreversible action needs a CONFIRMED diagnosis. *(F1, F2, B4)*

### Changed
- **Degenerate-regime check** before writing off an idea (`program.md.tmpl`, `model-selection`): a null
  measured where competing hypotheses are indistinguishable proves nothing. *(C3)*
- **Frozen-infrastructure debugging**: an unphysical symptom (sign flip, mirrored artifact, structured
  residual) now triggers re-verifying the FROZEN forward model/generator *first* — threaded into the `debug`
  gotcha catalog and `frame-problem`'s "keep it living" (a persistent gap can be a bug in reference code, not
  only model-form error). *(B2)*
- **Promotion validates upstream preprocessing** (registration/pose/normalization must be non-degenerate on
  the data it's applied to) in the checkpoint promotion checks and `verify`'s code-soundness step. *(B3)*
- **No INFERRED→PINNED without a falsification attempt** (especially when a cheaper discriminator exists) in
  `program.md.tmpl`'s operating stance and `verify`. *(B4)*
- **Static-check-before-expensive-run** worked example (φ-scan artifact) added to `program.md.tmpl`'s
  a-priori section. *(E3)*
- **`debug`**: exhaust existing evidence (logs/recorded state) before building a reproduction harness; and
  installed tooling must be verified non-intrusive. *(F4)*
- **`handoff` + `GETTING_STARTED`**: flush converged designs/plans to a file at decision-lock points, not
  session end. *(F3)*

### Principles (doctrine)
- **New Context 9 · "Operating unattended"** in `docs/PRINCIPLES.md` (+ always-on essence in `docs/CORE.md`
  "Running unattended", coverage in `docs/DOCTRINE_INDEX.md`, and the paper master
  `synthesis/PRINCIPLE_TAXONOMY.md`): **don't stop prematurely** (a "done/ceiling/blocked" conclusion is a
  load-bearing claim, refuted like a positive result), autonomous-but-safe escalation, CONFIRMED-diagnosis
  before an irreversible action, monitor-long-runs (a stalled log is a dead run), persist hazards/decisions
  when they lock, enforce-don't-exhort, and every-human-correction-is-a-scaffolding-gap.
- **Enforcement of "don't stop prematurely"** threaded into `program.md.tmpl` (Getting Unstuck), `verify`
  (a ceiling/blocked claim is a load-bearing claim to refute; unfalsified ⇒ INCONCLUSIVE), and
  `campaign-status` (flags a premature "done/blocked" as a resume signal).
- **Additions to existing contexts** (all from the 2026-06-30 review): comparability-is-honesty +
  record-carries-its-own-corrections (Ctx 1); validate-before-you-freeze + unphysical-symptom-implicates-
  infrastructure (Ctx 2); exhaust-existing-evidence-before-a-repro-harness (Ctx 3); discriminate-where-
  hypotheses-diverge + sharpened anchoring (Ctx 4); result-not-saved-until-verdict + reconstruct-from-full-
  trail (Ctx 7).

_Deferred / deliberate:_ multi-track campaign support (G2 branching + G3 cross-linked FROZEN/MUTABLE) is
scoped as one workstream in `synthesis/BUILD_BACKLOG.md`; the stale-archive-digest flag (archive) stays queued.
Ctx 9's overlap with Contexts 7–8 (organization) is flagged for a later editorial pass.

## [0.5.0] — 2026-06-30

### Added
- **`CHANGELOG.md`** (this file) — a running, human-readable kit change log.
- **Scoreboard comparability columns** — `metric_version` and `data_version` added to
  `templates/campaign/results/scoreboard.tsv.tmpl`, with a comparability rule (a "current best" is valid only
  *within* one `(metric_version, data_version)` pair; re-score across versions). Threaded into
  `program.md.tmpl` (Logging Protocol + promotion rule), `new-campaign` (column list), and a
  `campaign-status` hygiene check. *(keeper C2)*
- **DISCOVERIES retraction/supersession convention** — `templates/campaign/results/DISCOVERIES.md.tmpl` now
  carries an append-only `REVISES Dn` convention so a reversed finding is corrected *in the same file*, never
  only in a side note. *(keeper C1)*
- **Frozen-≠-validated gate** — `correctness-suite` and `simulation-design` now require a **sign/convention
  round-trip vs a trusted analytic reference + symmetry self-tests** to pass *before* a forward model / data
  generator / scorer is frozen; `program.md.tmpl` FROZEN section states "frozen means locked, not correct"
  and makes an unphysical symptom a trigger to re-verify the frozen infra first. *(keeper B1)*
- **Verify-gate enforcement** — `program.md.tmpl` makes independent verification a named, enforced promotion
  step that also covers scoreboard *current-best* promotion (not only DISCOVERIES writes); `campaign-status`
  now asserts the `guard_discoveries` hook is actually wired and flags a current-best/DISCOVERY row with a
  blank `verified` column; `new-campaign` + the guard hook's docstring document that imported/relocated trees
  lose the gate and must be re-wired. *(keepers A1+A2)*
- **Ledger-hygiene gates** — a "no orphaned result (every row has a written narrative AND a graded verdict)"
  check in `campaign-status` + the checkpoint protocol + `handoff`; and `handoff` must scan recent session
  transcript(s) for artifacts written *outside* the campaign root before asserting a deliverable "wasn't
  done". *(keepers D1+D2)*

### Changed
- **Closed the review→improve loop** — `campaign-review` now mirrors its keepers into a tracked intake table
  in `synthesis/BUILD_BACKLOG.md`, and `improve-kit` marks each keeper `applied`/`rejected` with a commit.
  This fixes the leak where a prior review's keepers were never folded in and the same bugs recurred.
  *(keeper G1; campaign-review + improve-kit are dev-only skills in the workspace `.claude/skills/`)*

### Provenance
- All of the above were harvested by the kit's own `campaign-review` run over the archived transcript corpus
  (Magnetic inverse loop v3/v4, ASI sims v1/V2, ASI fit 3, + misc), 2026-06-30. Full evidence-cited report:
  `case-studies/transcript_review_2026-06-30.md`. Remaining keepers are queued in the
  `synthesis/BUILD_BACKLOG.md` intake table (C3, B2–B4, E1–E2, F1–F5, G2–G3).
- Honesty/verification/metric-integrity core unchanged except to **tighten** enforcement — the one direction
  self-improvement is permitted to move it.

---

## [0.4.0] and earlier
Tracked in the per-file `## Changelog` sections (`docs/PRINCIPLES.md`, `docs/DOCTRINE_INDEX.md`) and the git
history of this repo (e.g. `physkit` rename, always-on `CLAUDE.md` + verify-before-DISCOVERIES gate,
model-tiering guidance). This top-level CHANGELOG begins at the Unreleased entry above.
