---
name: new-campaign
description: Interview a researcher and scaffold a new autonomous-research ("autoresearch") campaign in the physical sciences. Use when the user wants to START or SET UP a new campaign, optimization loop, fitting/decoder campaign, forward-model-improvement campaign, generative-design search, ML-training campaign, or hardware-in-the-loop tuning loop — phrasings like "start a new campaign", "set up an autoresearch loop", "scaffold a campaign to optimize X", "I want to build a loop that improves Y", or "create the charter.md / metric / scoreboard for a new project". Conducts a structured interview (goal, metric, physics, data, levers, constraints, compute, time), co-designs the FROZEN metric, determines which archetype(s) apply, then generates a complete ready-to-run campaign tree (charter.md, protocols, configs, results ledger, and light code stubs) from the kit templates and validates that nothing is left unfilled. NOT for running an existing loop, verifying a result (verify), or writing the end-of-campaign report (final-report).
---

# new-campaign — interview, then scaffold a campaign

Your job is to turn a *fuzzy research goal* into a *running, rigorous, well-documented campaign*. The
deliverable is scaffolding that encodes the campaign's intent so the loop-running agent can't drift
from it: a FROZEN metric, an experiment loop, levers, guardrails, logging, verification, and reporting.

**Stance for the interview** (from `docs/PRINCIPLES.md` §1):
- **Fill from sources first; ask only when unsure. Never ask what you can check.** Before asking
  anything, harvest every answer you can definitively obtain from what's already available: the
  conversation so far, any documents / paper manuscripts the user says describe their setup, data/config
  files in the target directory, and anything you can detect directly (Step 0.5). Ask the user only
  about genuine gaps.
- **When a value came from a source but you're unsure it applies, ask a short question naming the
  source** — e.g. *"should I use the experimental parameters described in Reed et al. for this
  problem?"* — rather than asking the user to supply it from scratch.
- State assumptions explicitly; present multiple interpretations when ambiguous; push back when a
  simpler scope exists; and **co-design the metric** rather than inventing it. Narrow the purpose — a
  campaign explores one idea or one slice, not a whole project.

## When to invoke
- The user wants to start / set up / scaffold a new campaign or optimization loop.
- An existing project needs the autoresearch structure (charter.md + metric + scoreboard) added.

Do NOT use this to run an already-scaffolded loop, to verify a finding (`verify`), or to write
the final report (`final-report`). To **fork a campaign whose findings a bug/correction invalidated** (a
clean break with an archived source + re-verified carry-forward), use **`fork-campaign`**, not this skill.

- **If the idea itself is unvetted**, offer to run **`assess-idea`** first (advisory — feasibility/worth).
  It never blocks scaffolding, but a quick GO / DE-RISK-FIRST / NO-GO can save a campaign built on a
  low-ceiling problem. Off by default; propose it when the user hasn't already pressure-tested the direction.

## Inputs
- The **target directory** where the campaign should be created (ask if not given; default: the current
  working directory). Never overwrite existing files without explicit confirmation.
- Optionally, a one-line goal the user already typed — use it to seed, not skip, the interview.
- Optionally, a **framing artifact** from `frame-problem` (a `FRAMING.md` or a filled `INTAKE.md`) — if one
  exists, compose it (below) rather than re-interviewing.

## Two ways to gather the inputs
**(a) Live interview** (default) — Step 1 below, topic by topic. **(b) Intake-form mode** — for a user who
prefers editing a form to answering in the terminal: emit a pre-filled `INTAKE.md` (from
`${CLAUDE_PLUGIN_ROOT}/templates/campaign/INTAKE.md.tmpl`), filling every field you can detect/harvest and
leaving blanks where you need them; the user edits it in an editor; you read it back and ask only about the
blanks/ambiguities. Either way the result is the same campaign spec (Step 2). Offer the form when the
interview would be long or the user is on a slow channel.

## Compose `frame-problem` — don't re-interview the physics
`frame-problem` owns physics scoping (inventory + verification plan + decomposition) and writes a durable
**framing artifact**. If one exists (or you ran `frame-problem` for this goal in-session), **read it and
*confirm, don't re-ask*** — carry its physics inventory, a-priori bounds, verification plan, and step
decomposition straight into the spec, and only fill the campaign-only gaps (metric co-design, levers/frozen,
data, compute, archetype). If no framing artifact exists and the problem has real physics, **run
`frame-problem` first** (or fold its three outputs into the interview) rather than duplicating the work.
Within a session this is shared context; across sessions the persisted artifact carries it. No
double-interview.

## Step 0 — read the kit before interviewing
Read these so your questions and fills are grounded (paths are under the plugin root):
- `${CLAUDE_PLUGIN_ROOT}/docs/PRINCIPLES.md` — the doctrine every campaign inherits; it's sectioned by 8
  contexts. Skim it now; once the archetype(s) are chosen (Step 1), read **in depth only the contexts they
  lean on** (the cheatsheet maps each archetype to its disciplines) rather than all eight.
- `${CLAUDE_PLUGIN_ROOT}/docs/CORE.md` — the always-on spine + the general skills it routes to
  (`frame-problem`, `verify`, `simulation-design`, `correctness-suite`, `report`, …) that this campaign composes.
- `${CLAUDE_PLUGIN_ROOT}/templates/ARCHETYPE_CHEATSHEET.md` — the campaign archetypes (A–I) and their patterns.
- `${CLAUDE_PLUGIN_ROOT}/templates/PLACEHOLDERS.md` — the fill convention + canonical placeholder list.
- Skim `${CLAUDE_PLUGIN_ROOT}/templates/campaign/` — what you will fill (now including `INTAKE.md`,
  `docs/PROJECT_ORIENTATION.md`, `docs/ENGINEERING_NOTES.md`, `docs/VERIFICATION_PLAN.md`,
  `docs/protocols/expensive-evaluation.md`) — what you will fill. For archetype E, also read
  `${CLAUDE_PLUGIN_ROOT}/docs/reference/hardware-in-the-loop.md` (§0 is an example assembled loop).

## Step 0.1 — establish the project home (every campaign lives in one)
**Every campaign lives inside a project** — the home for one physical system investigated over many campaigns
and ad-hoc sessions, so shared data + docs live once and are referenced by relative path. This is
unconditional: there is no bare-campaign mode. A one-off costs ~5 near-empty files for it (the physics /
conventions / instrument docs *move* into `shared/`, they don't multiply) and in exchange grows into a
sibling campaign, a fork, or a follow-up session with **zero reorganization** and no path rewrites.
- **An ancestor holds `PROJECT.md` + `LINEAGE.md`** → use that project. The campaign lives at
  `<project>/campaigns/<NN>_<slug>/`; pick `<NN>` as the next zero-padded index after the last `LINEAGE.md` row.
- **Otherwise → run `new-project` first** to create the home, then come back here. **Carry everything you have
  already gathered** — `new-project` fills its tree from the same answers, so never re-interview (when
  `new-project` invoked *you*, the flow is one-way: do not call back into it). Tell the user the home is being
  created; don't ask permission for it.
- **A pre-existing bare campaign** (imported, hand-built, or scaffolded before this default) is **lifted into a
  project**, not left as-is: create the home around it, move it to `campaigns/01_<slug>/`, hoist its
  `docs/PHYSICS.md` / `CONVENTIONS.md` / `INSTRUMENT.md` into `shared/`, and append its `LINEAGE.md` row.

Consequences — unconditional, with no campaign-local variant:
1. **Physics/conventions/instrument** are **referenced from `../../shared/`, never copied** (design §4.1).
2. **Data** is `../../data`.
3. The campaign **appends a `LINEAGE.md` row** and resolves the charter's *Relationship to sibling campaigns*
   block (KEEP-and-fill if coupled to a sibling; DELETE if independent — coupling, not project membership,
   decides that one).
4. The campaign `CLAUDE.md` **project-context** block is always kept.

## Step 0.5 — harvest sources and detect the environment (before asking anything)
Collect what already answers the interview, so you only ask about real gaps:
- **Read everything the user pointed to** — setup docs, paper manuscripts, prior notes — plus any data
  and config files already in the target directory. Extract concrete values (geometry, parameters,
  units, data shapes) and **note each value's source** so you can cite it (and ask "use the value from
  <source>?" if its applicability is uncertain). For papers, prefer the **arXiv** version and convert
  any PDF with a scientific-PDF→markdown tool to save tokens (see `docs/PRINCIPLES.md` §2).
- **Detect, don't ask, what you can check:** the compute (CPU cores, RAM, and GPU — e.g. run
  `nvidia-smi`), **the free disk space on the volume the campaign will live on**, the available
  Python/toolchain, and the data files present and their shapes.
Carry these harvested facts into the interview.

## Step 0.6 — establish the source-authority ledger (when more than one source describes the system)
Replication and model-improvement campaigns routinely ship **several descriptions of the same system that
disagree** — the paper text, a figure, leftover or post-publication code, a released trained-model or data
artifact, and the user's recollection. Building the baseline on the wrong one is the most expensive setup
mistake there is: a *faithful reproduction of the wrong spec* looks correct and only unravels hours into the
loop (and a "match the published number" gate can then drive the agent to reverse-engineer the original's
bug). Before scaffolding, build a short ledger:
- **Enumerate every source** that describes a load-bearing fact — the architecture/method, the
  training/processing recipe, normalization & units, hyperparameters, the data convention.
- **Rank them by authority.** A *shipped artifact you can parse or run* (trained weights / saved model /
  released data) outranks the *paper text/figure*, which outranks *modified or leftover code*, which
  outranks *human recollection*. The artifact is ground truth; everything else is a *description* of it.
- **Resolve each load-bearing fact to the highest-authority source available by reading the artifact** —
  parse the saved model's topology, probe the data's actual statistics, run the released weights on your
  eval set — rather than inferring it from a lower-authority proxy. The campaign already pins *data*
  conventions empirically (Step 1, topic 5); pin the *method/recipe* with the same rigor — do not defer it
  to "exp 000's job" when an artifact on disk settles it in seconds.
- **Tag each fact's provenance:** *PINNED* (from an authoritative artifact / empirical probe) · *REPORTED*
  (in text) · *INFERRED* (from an untrusted proxy) · *RECALLED* (from memory). Carry the tags into the spec.
- **Quarantine, don't absorb, untrusted or contradictory sources.** State explicitly that the
  leftover/modified code is NOT the spec (and why) so the loop agent doesn't re-anchor on it.
- A load-bearing fact you can only mark INFERRED/RECALLED is a **genuine gap** — ask the user in Step 1,
  naming the source and the conflict (e.g. *"the figure shows no dropout but the leftover code has it — the
  saved model would settle it; do you have the trained weights?"*), rather than silently baking it in.
Seed the resolved ledger into `docs/ENGINEERING_NOTES.md` (Step 3) so the provenance survives into the loop.

## Step 1 — the interview (topic by topic)
Go one topic at a time; confirm understanding before moving on. For each topic, **fill what the sources
already answer and ask only the gaps.** Use the **AskUserQuestion** tool for categorical forks; use
free-form dialogue for the metric and physics narrative. Capture every answer — you will need it to
fill the templates.

**Always ask these — never skip them, even if you think you could infer them:** the internet/literature
level (topic 11) and the user's own ideas to try / avoid (topic 12). Two more are effectively always-ask
because you cannot measure them: the time budget (topic 8) and the environment (topic 9).

**Always determine — for EVERY project — whether there is a simulation component** (a forward model,
device-performance simulation, synthetic/simulated training data, an evaluator/simulator, or a
surrogate). **Most campaigns have one** — assume YES unless it's a clear exception (direct experimental
control, or training/fitting purely on real experimental data). If there is one, apply the V&V doctrine
(`docs/SIMULATION_VALIDATION.md`) and wire its gates into the core docs (Step 3).

1. **Goal & the core decision.** What is the campaign trying to achieve, and what *decision* does its
   result drive? Force a narrow scope. If the goal needs several coupled pieces, flag it for the
   multi-stage plan (topic 11).
2. **Archetype(s) — which APPLY (none, one, or several).** Decide which of the archetypes apply
   to this campaign; it may be zero, one, or multiple (a campaign can be both forward-model *and*
   generative-design; a **discovery loop (G)** scored *through* a forward model; or **active design (H)**
   used to **discriminate models (I)**). **Inherit and merge** the metric / lever / FROZEN / failure-mode
   guidance from *every* archetype you deem relevant — do not force a single best-fit. State which apply
   and why, and let the user correct it. If several apply in sequence rather than at once, that is a
   multi-stage campaign (topic 11). Archetypes G (`discovery-loop`), H (`experiment-design`), and I
   (`model-selection`) each have a dedicated operational skill.
3. **The metric — build it together (the most important topic).** Co-design the single FROZEN primary:
   its name, direction (higher/lower = better), precise definition + units, the FROZEN scorer it lives
   in, hard bounds, and the **a-priori plausible range** (predict before running — encode the bounding
   discipline). Then the baseline (exp 000) value/method, any theoretical ceilings, the guardrail
   (necessary-but-not-sufficient), and diagnostics. Pin down what FEEDS the metric vs what is FROZEN.
   **Ask explicitly whether the baseline (the prior work's delivered pipeline/number this campaign will
   freeze and build on) has already been through `verify`.** If not, say so plainly in the campaign spec
   as an open risk rather than silently trusting it — a campaign optimizes *against* its baseline, so an
   unverified baseline is a load-bearing unknown the whole campaign inherits, not a detail.
   These — primary, guardrail, diagnostics — plus the experiment-type **run numerics** (e.g. epochs +
   best epoch for ML; iterations / wall-clock / n_free_params for fits), plus a **`tier`** column
   (Scout/Confirmation/Extended) and the always-present **`metric_version` / `data_version`** comparability
   tags, become the columns of `results/scoreboard.tsv`, the campaign's quantitative ledger (separate from
   the narrative journal).
4. **Physics / system knowledge.** Capture (from sources wherever possible) everything needed to model
   the system:
   - **Physical objects & geometry** — dimensions, arrangement/layout, material(s), and quantities.
     *E.g. for an ASI fit from NV-magnetometry data: the lattice geometry and spacing, island
     dimensions, the material, the sample orientation relative to the measured NV axis, the bias-field
     orientation, and the pixel size / field-of-view.*
   - **Experimental / measurement geometry** — what is measured, by what instrument, in what frame, at
     what standoff/resolution.
   - **Governing physics** — the foundational equations, simulation methods/approximations, the common
     techniques for this problem, and the system's typical behavior *through the lens of this problem*
     (degeneracies, symmetries, regimes — e.g. that magnetization-from-field is non-unique, or how an
     ASI traverses a hysteresis loop). Source from user info, provided literature, or (if enabled) a
     targeted search.
   - **Conventions** — units/sign/ordering (→ `../../shared/CONVENTIONS.md`) and known artifacts / recurring
     bugs to guard against. (Capture the **simulation methods/approximations** here too — the
     always-determine simulation check above decides whether the V&V plan in Step 3 applies.)
   The governing physics + conventions + instrument docs are the project's **shared** docs
   (`../../shared/PHYSICS.md`, `../../shared/CONVENTIONS.md`, `../../shared/INSTRUMENT.md`) — **reference them,
   don't copy.** `new-project` seeded them; fill any thin slot here, and if this campaign surfaced new
   physics/conventions, UPDATE the shared docs (they're living docs shared by every campaign). **Never** create a
   campaign-local `docs/PHYSICS.md` / `docs/CONVENTIONS.md` / `docs/INSTRUMENT.md` — the validator rejects it.
   `CONVENTIONS.md` holds the units/signs/frames; `INSTRUMENT.md` the measurement rig / apparatus + sample
   parameters, with sources. *(There is no `SYSTEM.md`: it was retired and split into the PHYSICS
   target-of-study section + `INSTRUMENT.md`, so each name is unambiguous across subfields.)* **`PHYSICS.md`** is
   the governing physics **+ a *target-of-study* section** describing the object under study (length varies with
   the problem; equations in math blocks with precise, defined notation; a *living doc*; **includes the physics
   inventory** — every relevant effect tagged accounted-for / negligible-by-scale / out-of-scope / deferred /
   unknown, *with a reason*, from the `frame-problem` artifact — **and the predictive framework**: the
   mechanism/model the loop predicts with, at a complexity matched to the problem, plus the discriminating
   thought-experiments it licenses). Link the docs from the README via `{{PHYSICS_DOC}}` / `{{CONVENTIONS_DOC}}`
   (always a `../../shared/…` path — see `PLACEHOLDERS.md` for the per-file depth). Record anything you had to
   ask — the next agent shouldn't have to. *(If a `frame-problem` artifact exists, confirm its inventory rather
   than rebuilding it.)*
4b. **Verification — capture the application-specific checks (now).** Decide *how a result will be known to
   be right* before the loop runs: the analytic limits, invariants, convergence, independent-method parity,
   and especially the **field-standard checks, known artifacts, and gotchas for THIS problem** — the part
   generic doctrine can't supply. Mark verification vs validation (held-out data; calibration ≠ validation).
   These author **`docs/VERIFICATION_PLAN.md`** (or, for sim-heavy campaigns, the tailored
   `docs/SIMULATION_VALIDATION.md`), which `verify` reads and `correctness-suite` encodes as regression
   gates. *(Inherit these from the `frame-problem` verification plan if one exists.)*
5. **Data / inputs.** Source; fixed experimental data vs generated/simulated; splits to hold fixed;
   formats, shapes, paths. (Fixed-data campaign → the dataset protocol collapses to a "verify exists,
   READ-ONLY" note.)
6. **Levers vs FROZEN.** What the agent MAY change (the orthogonal lever families) vs what is FROZEN
   (scoring math, core physics, geometry, data) vs READ-ONLY vs MUTABLE code.
7. **Experimental / hardware constraints.** Fairness rules; for a hardware-in-the-loop campaign, the
   **hardware safety limits** (hard constraints), irreversibility, and what actions need confirmation.
8. **Compute resources, time budget, and disk budget.** **Detect** the available hardware rather than
   asking (CPU cores, RAM, GPU via `nvidia-smi`). If it is relevant to the problem (e.g. a GPU for ML),
   **record it explicitly in the scaffolding** (the README Environment section and a note in
   `charter.md`) so future agents don't overlook available resources. Ask the user only for what you
   can't measure — chiefly the
   **time budget** (per-run and overall-loop). Use this to fill the run caps **archetype-specifically**
   (epochs for ML; replication depth for a cheap closed-form fit; expensive/irreversible runs for
   hardware). **Tiered scout/confirmation caps only make sense when** the problem supports a cheaper
   *partial* evaluation (fewer epochs, a partial dataset) AND the full evaluation is genuinely long
   (>10 min, especially >60 min); otherwise fill a single-tier budget. When tiering applies, consider
   **three tiers**: a very short *smoke* check (does the code run at all?), a short *scout* (is the idea
   promising?), and a longer *confirmation/validation* run. If you can't tell whether the eval suits
   partial runs, ask; otherwise just propose the scheme.
   **Size the DISK cost per experiment too, not just the time.** A loop that fills its volume overnight
   corrupts the save-set it was mid-write on, and the failure surfaces as an unrelated-looking gate error
   at 3 a.m. **Derive** the estimate rather than asking: sum what one experiment leaves behind from the
   artifact plan (topic 5 + `protocols/artifacts.md`) — the save-set (result JSON + figure + the
   `scripts/` snapshot copy: usually a few hundred KB) **plus the bulk artifacts that dominate it**
   (trained weights/checkpoints, generated datasets, computed operators, raw field/trace arrays). Compute
   the bulk terms from real shapes where you can (`n_points × n_channels × 8 bytes`, a model's parameter
   count, the size of an existing example file), not from a feeling. Then state the three numbers to the
   user: **MB per experiment · projected total for the planned experiment count · free space detected**.
   - Record the per-unit figure in `configs/loop.json` (`unit_cost.typical_disk_mb`) — the driver refuses
     to launch, and halts at the loop top, below ~3 experiments of headroom.
   - **If the projection is a material fraction of free space (say >25%), stop and design the retention
     plan with the user** before scaffolding: which bulk artifacts are kept, and which are dropped and
     *regenerated on demand* from the snapshot + seed. Fill it into `protocols/artifacts.md`
     (`{{RETENTION_PLAN}}`). The permanent record — scoreboard row, result JSON, figure, snapshot,
     narrative, verdicts — is **never** part of that trade; it is small by construction, and dropping any
     of it un-saves the result. Anything not deterministically regenerable (hardware measurements,
     external services, unrecorded seeds) is likewise never droppable.
   - If experiments are small (a few MB), say so explicitly and note that no plan is needed — a stated
     "not a constraint here" is what stops the next agent from re-litigating it.

   **From the same unit-cost assessment, derive the supervisor loop knobs** (`configs/loop.json` — the
   driver reads these; PLACEHOLDERS §Loop configuration): planner cadence *k*, plateau threshold *m*
   (**dual-denominated**: units AND wall-clock, whichever trips first), the outstanding-units cap
   (default *k*), the iteration timeout (> the Extended cap), the verify full-reproduction threshold
   (ADR-0008), and the planner/worker models (seed sensible defaults; they are the user's to change —
   model tiers shift with every release). **The cadence *inverts* with unit cost:** expensive units →
   plan often (small *k* — the planner is nearly free next to a day-long solve and a wasted solve is the
   real cost); cheap units → plan in strides (large *k* — keep planner overhead a small fraction of loop
   compute). Propose the values with their reasoning; the user confirms them with the spec.
9. **Environment & version control.** Ask which environment the user wants; **default to proposing a fresh
   virtual environment** (a new venv/conda env). Record the choice + setup commands in the README
   Environment / Quick-start. **Offer git, don't impose it:** recommend it for shared/large/long-lived
   projects, but make clear the **per-experiment snapshot is the reproducibility baseline either way** — a
   small solo campaign can skip git without losing reproducibility (`docs/reference/version-control.md`).
   Record the choice; never make git a precondition for starting.
10. **Existing code & tools.** What runnable code/data already exists to reuse, and which libraries to
    prefer (mature/free over from-scratch — `docs/PRINCIPLES.md` §5/§9).
11. **Internet / literature level (ALWAYS ASK — 3 options).** This sets **ongoing** literature use during
    the loop: **none** (no ongoing searches — remove the literature-search rule), **only when needed**
    (search when stuck — the default), or **extensive** (proactively search at setup to seed
    `PHYSICS.md`/`LITERATURE.md`, and periodically thereafter, not only when stuck). Independently, if the
    user **provided any starting literature**, summarize it in `LITERATURE.md` and keep the file — even
    when ongoing search is *none*. For needed/extensive, prefer arXiv and convert PDFs efficiently
    (`docs/PRINCIPLES.md` §2).
12. **User's own ideas (ALWAYS ASK).** Ask the user (a) any ideas/directions they would like you to
    **try**, and (b) anything that should **NOT** be tried (out of scope, known dead ends, forbidden
    approaches). Record the *to-try* ideas as the opening JOURNAL **NEXT** items (attributed to the
    user), and fold the *do-not-try* items into the `charter.md` FROZEN / out-of-scope section. User
    ideas are inputs, not a ceiling — you remain encouraged to propose well-founded novel ideas of your
    own (`docs/PRINCIPLES.md` §2).
13. **Multi-stage plan — propose it proactively.** Many complex tasks are best done as **several
    sequential loops**, not one: validating and improving on a simpler subcase first usually yields a
    more powerful, better-validated final result. Actively **design a staged plan and propose it.**
    Forward-model-before-decoder is one case; others include optimizing on *idealized/simpler physics*
    first (to set a baseline and a solid procedure while the physics is simple) before the real system,
    or inserting a stage that **produces an experimental protocol for the user to carry out** (e.g. a
    gauss-meter measurement) whose results feed the next stage.
    *Example — permanent-magnet array from measured surface fields:* (1) optimize the arrangement with
    *idealized* magnets — establishes a baseline and a solid optimizer while the physics is simple;
    (2) design a measurement protocol the user runs to characterize their real magnets' imperfections;
    (3) optimize the arrangement of the *imperfect* magnets, building on (1) and the data from (2).
    Each stage is a **sibling campaign** — its own `campaigns/<NN>_<slug>/` with its own charter, ledger, and
    `LINEAGE.md` row (Step 3, *Sibling campaigns & multi-stage*). Scaffold stage 1 now; confirm the staging with
    the user and record the later stages as planned successors rather than building them up front.

## Step 2 — write the campaign spec and get sign-off (anti-drift checkpoint)
Before generating anything, write a concise **campaign spec**: the archetype(s) that apply, the FROZEN
metric (with bounds + a-priori range), baseline, guardrail/diagnostics, levers, FROZEN/READ-ONLY/MUTABLE,
constraints, caps (and whether tiering applies), the data plan, the detected compute + chosen
environment, the multi-stage plan (if any), and the values you'll use for the key placeholders. Cite
the source for any value pulled from a document/paper/data, **with its provenance tag (PINNED / REPORTED /
INFERRED / RECALLED) from the Step 0.6 ledger** — and call out every load-bearing fact still at
INFERRED/RECALLED as an open question for the user to resolve before the baseline run. Show it to the user
and get explicit sign-off (or corrections). This is the checkpoint that keeps the build aligned with the
original intent.

## Step 3 — generate the campaign tree
Copy `${CLAUDE_PLUGIN_ROOT}/templates/campaign/` into the target directory and fill it from the spec,
obeying `PLACEHOLDERS.md`:
- **Resolve every `{{PLACEHOLDER}}`** clearly, explicitly, and concisely — specific enough to act on
  without the interview that produced it. Where the user deferred a value, write an explicit TODO noting
  the deferral — never a silent guess.
- **Resolve every `[[OPTIONAL — … ]]` block:** DELETE it if it doesn't apply (keeps the slim core
  slim); KEEP-WITH-A-NOTE a universal section that's merely not-yet-wired (mark it `(DEFERRED)`).
  Include the hardware-safety block only for archetype E. **The ceiling blocks are a SET** — ceilings
  appear in the Metric, Decision/promotion, and Before-accepting sections (and `metric.md`); keep or
  delete them all together. For a fixed-data campaign, delete `protocols/dataset.md` (leave the READ-ONLY
  note) AND drop its row from the `charter.md` Protocol Index.
- **Resolve every `[PROPOSED]` tag:** present each speculative discipline to the user to keep or cut;
  drop the tag on kept ones, delete cut ones.
- **Strip the `.tmpl` suffix** on write (`charter.md.tmpl` → `docs/charter.md`, etc.).
- **Always-on context — render the FROZEN doctrine spine into `CLAUDE.md` (critical — this is what keeps
  the doctrine in context and the verify gate un-skippable):** generate **`CLAUDE.md`** (from
  `CLAUDE.md.tmpl`) in the campaign root — Claude Code auto-loads it every session, and it is the ONLY
  reliable always-on context (a plugin's `docs/` are NOT auto-loaded, so the always-loaded spine lives here
  per-campaign). **Every line of it is re-injected every turn, so it carries only what the running loop
  acts on** — no kit-design rationale (why the spine is inlined and not `@`-imported), no scaffolding-time
  instructions (the fresh-session launch is Step 5's handoff message to the *user*), no commentary on how
  the file was produced. Do not add a header comment; the freeze/provenance fact is stated once, in the
  spine banner below. Fill the **`{{PHYSKIT_SPINE}}`** block by rendering a campaign-tailored, **FROZEN** snapshot
  of `${CLAUDE_PLUGIN_ROOT}/docs/CORE.md`. **Do NOT `@`-import CORE.md, and do NOT vendor a separate
  `PHYSKIT_CORE.md` + hash-check it against live** — a generated campaign *freezes-and-stamps* its doctrine
  as part of its reproducible record; it does not track a moving CORE (kit-dev `CLAUDE.md` §single-source:
  *source* minimizes forks, *output* freezes-and-stamps). To render the spine:
  1. **Read** `${CLAUDE_PLUGIN_ROOT}/docs/CORE.md` in full.
  2. **Tailor for a running campaign** — keep the meaning; cut only what a mid-campaign loop never fires.
     *Drop* the YAML frontmatter (`id`/`load`/`load_trigger`/… is kit-internal routing metadata about how
     the kit ships, not doctrine the loop acts on). *Reframe* the opening line to "running an autonomous research campaign" and point the goal at
     `docs/charter.md`. *Replace* the "Stage 0 — clarify the goal" section (its `→ /physkit:new-campaign`
     routing is dead once the campaign exists) with a short "re-anchor each iteration — the goal is fixed in
     the charter" paragraph that KEEPS the state-assumptions / present-interpretations / push-back /
     stop-when-confused discipline. *Drop* exactly the three routing-table rows a running loop never uses —
     `assess-idea` (pre-campaign), `new-campaign` (already done), `new-project`. **Keep everything else
     VERBATIM** — the whole Constitution, the working loop, When-stuck, Running-unattended, Honest reporting,
     and the nine-pillar list. (Do not create a static tailored-CORE file in the kit or the campaign — that
     would be the retired `CLAUDE.general.md` duplicate anti-pattern; the snapshot exists ONLY as inlined
     text in this one `CLAUDE.md`.)
  3. **Prepend the provenance banner** (the freeze stamp — makes the snapshot legible and hand-edit-proof):
     ```
     > **Doctrine spine — frozen snapshot.** Derived from physkit CORE.md at scaffold time and frozen with
     > this campaign as part of its reproducible record. **Do not hand-edit this block** — to change doctrine,
     > edit kit/docs/CORE.md and re-scaffold, or (if a result is invalidated) fork-campaign.
     > generated: physkit <plugin-version> · CORE.md <core-ref> · <YYYY-MM-DD> · spine-sha256 <hash>
     ```
     Fill `<plugin-version>` from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`; `<core-ref>` from
     `git -C "${CLAUDE_PLUGIN_ROOT}" rev-parse --short HEAD` when the plugin is a git checkout, else a short
     sha256 of `CORE.md`; `<spine-sha256>` = sha256 of the rendered spine body (banner excluded). The banner
     followed by the tailored body together ARE the `{{PHYSKIT_SPINE}}` fill — the template's old thin
     "Frozen core" 5-bullet summary is gone, subsumed by the Constitution the snapshot carries.
- **The enforcement layer:** generate **`.claude/settings.json`** (from its `.tmpl`),
  **`scripts/loop_heartbeat.py`** — the Stop hook guarding attended sessions in a live campaign (it
  refuses an end-of-turn that isn't the human's `results/STOP` or a recorded `results/stop_request.json`,
  and its block message routes toward launching the driver; it stands down for driver-spawned
  supervisor-mode workers, whose per-unit end-of-turn is earned, and for any attended session while the
  driver's `results/.driver_alive` sentinel is fresh) — and
  **`scripts/guard_discoveries.py`** — the PreToolUse hook that denies a `DISCOVERIES.md` write whose
  entry does not cite a promotable verdict artifact (`results/verdicts/<id>.json`, written by `verify`;
  CONFIRMED + named refuter; an INCONCLUSIVE kill is denied; **fail-closed on the promote path**). Fill
  **`{{PYTHON_CMD}}`** with the python invocation detected in Step 0.5 (`py -3` on Windows, `python3` on
  macOS/Linux) so the hook command runs on this machine. Generate **`configs/loop.json`** (from its
  `.tmpl`, knob values from topic 8) and create the artifact-gate directories **`predictions/`** (the
  runner's spend gate refuses any solve without `predictions/<exp_name>.json`) and **`results/verdicts/`**.
  Seed **`results/queue.json`** — exp 000 as the first unit, then the user's topic-12 *to-try* ideas as
  proposed units with rationales, attributed to the user. **Every unit references ONE concrete runnable
  config path** (the driver validates a unit by that config's `exp_name` save-set) — an idea spanning
  several solves becomes several units, or one unit whose single config encodes the pre-registered
  sweep; never a prose meta-unit with no config behind it:
  `{"next": [{"config": "...", "rationale": "...", "proposed_by": "user", "declined": []}, ...],
  "shelved": [], "accepted_units": 0, "last_accept_utc": null, "units_since_planner": 0}`.
  **Verify the layer is actually wired** before handoff — `.claude/settings.json` registering
  `guard_discoveries`, both gate directories present, `loop.json` + `queue.json` parsing; a tree without
  them runs with **no gates at all** (this has happened on real campaigns whose trees were assembled by
  hand — `campaign-status` asserts all of it). The hook guards only DISCOVERIES writes — current-best
  promotion is enforced by `charter.md`'s promotion rule + the `campaign-status` check (it does not see
  scoreboard edits).
- **Code stubs:** fill `scripts/metric.py` (the FROZEN scorer + `--selftest`) and
  `scripts/run_campaign.py` (the runner). These are intentionally light — leave the TODO hooks for the
  agent to implement the physics in-loop, but wire the names/metric so `--selftest` is the gate for
  exp 000. The `tests/` **correctness suite** ships as skip-stubs — from `docs/VERIFICATION_PLAN.md`, seed at
  least the analytic-limit + invariant checks for the frozen forward model (see the `correctness-suite`
  skill); it is green-gated (`run_campaign` warns on red under `--selftest`; `verify` blocks promotion on it).
- **Author the new orientation/verification/engineering docs:** fill **`docs/PROJECT_ORIENTATION.md`** (the
  goal, the decision it drives, the loosely-held expectations, and the numbered goal-linked task hierarchy —
  graduating the `frame-problem` decomposition); **when the field has them, also fill the optional "Where this
  sits in the field" block** — the gap/novelty, adjacent work, the **threshold ladder + named precedents** for
  the key quantity, and what not to claim (ask the user or draw on the topic-4 literature; skip the block if
  the quantity has no canonical thresholds — never invent them); **`docs/VERIFICATION_PLAN.md`** (the application-specific
  checks from topic 4b — the gate `verify`/`correctness-suite` consume); and seed **`docs/ENGINEERING_NOTES.md`**
  with the **Step 0.6 source-authority ledger** (one ED per load-bearing fact resolved from a source — its
  value, the authoritative artifact it's PINNED to, the provenance tag, and the lower-authority sources
  quarantined and why; an empty header only if there was a single source). Put the
  user's *ideas to try* as the opening `PROJECT_ORIENTATION` tasks + JOURNAL NEXT items.
- **Reference docs (see topic 4):** physics, conventions, and instrument are the project's **shared** docs, so
  the campaign tree carries **no copy of them** — fill `{{PHYSICS_DOC}}` / `{{CONVENTIONS_DOC}}` with the
  `../../shared/…` path at the correct relative depth per file (see PLACEHOLDERS.md), and update the shared docs
  in place if this campaign added physics/conventions. Record the **detected compute** + the **chosen
  environment/setup commands** in the README (Environment / Quick-start), note available compute in
  `charter.md`, and register any new docs in the README.
- **Project wiring — always, from Step 0.1:**
  1. Reference the canonical data as **`../../data`** — never copy it into the campaign.
  2. **Append a row to `../../LINEAGE.md`** (Campaigns table): index `<NN>`, campaign name, date, the `approach`
     tag, the FROZEN primary metric, *what changed from the predecessor* (or "— (first)"), headline result
     (leave `pending` until exp 000), verified discoveries (none yet), `@KB-key` (—), status `active`.
  3. Resolve the charter **Relationship to sibling campaigns** block — KEEP + fill `{{SIBLING_FROZEN_MUTABLE}}`
     and `{{CONSUMED_ARTIFACTS}}` if this campaign is **coupled** to a sibling (what it FREEZES vs MUTATES; which
     `../../shared/<artifact>` it consumes); DELETE it if independent. *(Coupling decides this block, not project
     membership — the first campaign in a fresh project deletes it.)*
  4. **Keep** the campaign `CLAUDE.md` project-context block.
  5. A verified finding that is a fact about the **system** (not just a config that scored well) is later
     **promoted** from `results/DISCOVERIES.md` to the project `../../DISCOVERIES.md` (survives fork-and-archive);
     note this in the handoff so the loop agent knows the promotion path.
- **Literature (per the topic-11 level)** — the ongoing-search rule and the `LITERATURE.md` file are
  decided separately:
  - *Ongoing-search rule in `charter.md`:* for **none**, resolve the `[[OPTIONAL — literature search
    enabled]]` block as DELETE; for **only-when-needed** / **extensive**, keep it and fill
    `{{LITERATURE_LEVEL}}` with the chosen intensity (search-when-stuck vs proactive-and-periodic).
  - *`LITERATURE.md` itself:* keep it and **seed it with summaries of any literature the user provided**
    (prefer arXiv; convert PDFs; cache) — even when ongoing search is *none*. DELETE the file ONLY when
    ongoing search is *none* AND the user provided no starting literature. When kept under *none*, treat
    it as a **static** reference — keep the summaries + references, drop the roadmap / next-search sections.
- **Simulation validation (conditional on topic 4):** if the campaign has a simulation aspect, author
  `docs/SIMULATION_VALIDATION.md` for it — a tailored V&V&UQ plan from
  `${CLAUDE_PLUGIN_ROOT}/docs/SIMULATION_VALIDATION.md` — and wire its gates into the **core docs**: a
  **verify-before-validate gate** (the simulator must pass code + solution verification before any
  simulator-based result is trusted) plus the **sim-to-experiment guardrail** in `charter.md`; the
  simulator's **assumptions, domain of validity, and V&V status** in `../../shared/PHYSICS.md`; and keep
  *calibration ≠ validation* (hold out independent validation data). Register it in the README and the
  `charter.md` Protocol Index.
- **Seed the index and the user's directions:** fill `results/INDEX.md` with its exp 000 row (the loop
  agent maintains it thereafter). Put the user's *ideas to try* (topic 12) as the opening JOURNAL
  **NEXT** items, attributed to the user; fold the *do-not-try* items into `charter.md`'s FROZEN /
  out-of-scope list.
- **Sibling campaigns & multi-stage (project model, §5):** a second track/approach/stage is always a **sibling
  campaign** — its own `campaigns/<NN>_<slug>/` with its own charter + ledger, coupled via the charter
  *Relationship to sibling campaigns* block and shared promoted artifacts (`../../shared/`). Scaffold each by
  re-running this skill in the project (a new `LINEAGE.md` row per sibling). The retired `_<NAME>`-suffix-in-one-tree
  form is **not** an option — that was the bare-campaign fallback, and every campaign now has a project home.
- Seed `results/scoreboard.tsv` with its header; leave `results/logbook.md` (append-only full record),
  `results/JOURNAL.md` (the working window), and `results/DISCOVERIES.md` with their intros + the first
  **NEXT** pointer (queue exp 000). The logbook, scoreboard, and `diagnostics/` logs are **append-only and
  never read in full** — that's what keeps the record complete without bloating the loop's context. (If
  the user wants hard separation, the logbook / diagnostics can be redirected to a path outside the
  campaign tree; default is in-tree for reproducibility.)

## Step 4 — validate (deterministic gate)
Run the bundled validator on the generated tree and FIX anything it flags:
```
python "${CLAUDE_PLUGIN_ROOT}/skills/new-campaign/scripts/validate_campaign.py" <target_dir>
```
It fails if any literal `{{…}}`, dangling `[[OPTIONAL`, or stray `[PROPOSED]` remains, or if a required
file is missing. A generated campaign with an unresolved token is not done.

## Step 5 — hand off (and START A FRESH SESSION)
Tell the user what was created (the tree), and **name the destination up front: the loop runs in
supervisor mode, launched and watched through the `run-campaign` skill.** The fresh session's job is
setup, then `/physkit:run-campaign` — never executing the loop by hand.

The **critical handoff rule: do NOT start the loop in THIS setup session.** The campaign's `CLAUDE.md`
(always-on doctrine + hard gates) and the enforcement hooks only take effect in a session that **starts
in the campaign folder** — this setup session was already open when they were written, so it has loaded
neither. Instruct the user to launch a fresh session from the campaign directory:
```
cd "<absolute path to campaign dir>"
claude --dangerously-skip-permissions
```
**Give the absolute path, never one relative to this setup session's cwd.** The fresh session's shell has
no memory of where this session was running — a relative or partial path that resolved correctly here will
point at the wrong place (or nowhere) in the new terminal. Resolve the campaign dir to its full path before
handing over the command.
*(add `--plugin-dir "<KIT_DIR>"` if running the kit per-session rather than installed).*

In that fresh session, the sequence is:
1. **Pre-loop setup (not the loop):** implement `scripts/metric.py` + `save_figure()` and make
   `--selftest` pass; write `predictions/exp000_baseline.json` (the spend gate requires it — the
   expected floor is in the charter); run experiment 000 (the baseline gate). Confirm with `/context`
   that `CLAUDE.md` is loaded.
2. **Then invoke `/physkit:run-campaign`** — that session becomes the loop's cockpit: it runs the
   driver's preflight and translates any failure into its fix, launches `--supervise` in the background,
   narrates progress from the driver log, and relays the user's steering into `results/inbox/`.
   (Fallback, no skill available: hand over `<python> scripts/run_campaign.py --preflight`, then
   `--supervise` — writing out the actual python command detected in Step 0.5, e.g. `py -3`; never the
   literal placeholder.)

The driver runs its preflight (agent CLI, loop/queue config, metric self-test — each failure names its
fix; standalone: `--preflight`), pops units from the seeded `results/queue.json`, spawns a fresh worker
agent per unit (the frozen spine + charter auto-load in each), and enforces the artifact gates. Failures
split by kind (ADR-0009): an **operational** failure (a worker that dies, hangs, or leaves its unit
unvalidated) is retried, then shelved with the failure recorded — the loop continues; the driver
hard-halts only on **integrity** conditions (`results/ESCALATE.md`, a corrupt or post-planner-empty
queue) or **systemic** failure (several units failing in a row). Loop knobs live in `configs/loop.json`
(user-owned; the charter's "How the loop runs" section explains the contract).
**Attended work = watching and steering through the cockpit, not executing by hand.** A by-hand
`--config` run is for debugging a single experiment — it is not a mode for running the loop; the
interactive-executor pattern is retired (unbounded context, docs never re-read, premature stops,
verification decay — the failure record that motivated the driver).
- **In a project:** the campaign lives at `campaigns/<NN>_<slug>/` and its opening `../../LINEAGE.md` row is
  `status: active`. Remind the loop agent that shared data/docs are `../../data` + `../../shared/` (referenced,
  never copied — the ancestor `../../CLAUDE.md` carries the project rules), and that a verified **system-level**
  finding is later promoted from `results/DISCOVERIES.md` to the project `../../DISCOVERIES.md`.
- The campaign lives at `<project>/campaigns/<NN>_<slug>/` and its opening `../../LINEAGE.md` row is
  `status: active` — hand over the absolute path to **the campaign dir**, not the project root. Remind the loop
  agent that shared data/docs are `../../data` + `../../shared/` (referenced, never copied — the ancestor
  `../../CLAUDE.md` carries the project rules), that ad-hoc follow-up work belongs in `../../sessions/<date>_<slug>/`
  rather than in this tree, and that a verified **system-level** finding is later promoted from
  `results/DISCOVERIES.md` to the project `../../DISCOVERIES.md`.
- **If the loop runs agents beyond the main session** (Task subagents, SDK-spawned generation/critic
  roles): those contexts inherit **nothing** from `CLAUDE.md` — their prompts replace the doctrine stack.
  Before the first real experiment, run the prompt-surface audit
  (`docs/reference/prompt-surface-audit.md`): capture each role's context *as rendered* (including
  dynamically generated blocks) and verify every relied-upon rule is physically present; re-run it after
  any prompt change.

## Notes
- This skill SCAFFOLDS; it does not run the loop. After hand-off, the loop-running agent executes
  `docs/charter.md`.
- Never overwrite existing files without confirmation. If the target already holds a campaign, add a
  **sibling campaign** in the project (a new `campaigns/<NN>_<slug>/` + `LINEAGE.md` row) — or stop and ask.
- **Imported / relocated / hand-built trees silently lose the enforcement layer.** A tree not generated
  by this skill (copied in, assembled from frozen inputs, or moved) usually lacks `.claude/settings.json`
  + `scripts/guard_discoveries.py` + `scripts/loop_heartbeat.py` + the gate directories (`predictions/`,
  `results/verdicts/`) + `configs/loop.json` / `results/queue.json`, so the promotion gate, the loop gate,
  and the driver are all absent and the doctrine prose in `CLAUDE.md` is decorative. Re-run the Step 3
  enforcement-layer wiring for any such tree (and lift it into a project home per Step 0.1);
  `campaign-status` asserts the whole set.
- The metric and core physics you scaffold are FROZEN by construction — say so to the user, and make
  the `--selftest` real before exp 000 so a convention/sign slip can't corrupt the whole campaign.
