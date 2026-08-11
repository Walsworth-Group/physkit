# Getting Started — PhysKit

A short guide to going from a research idea to a running, autonomous research campaign. This grows as
the kit does; today it covers setup → interview → launching the loop.

> The kit is a **Claude Code plugin** named `physkit`. Its skills appear as `/physkit:<name>`
> once the plugin is loaded.

The kit has **two layers**. A **general science toolkit** — skills like `frame-problem`, `verify`,
`simulation-design`, `correctness-suite`, `debug`, `derive`, and `report` — is useful in *any* session,
campaign or not, and triggers on everyday science requests. A **campaign layer** scaffolds and runs
autonomous-research loops. This guide walks the campaign path; the general skills need no setup beyond
installing the plugin (full list at the bottom).

> **Five skills to know by name** — the rest the agent reaches on its own and suggests when relevant:
> `frame-problem` (start any physics problem here) · `verify` (check before you rely) · `report` (write
> it up, provenance-labeled) · `new-campaign` (stand up a loop) · `campaign-status` (the running loop's
> heartbeat).

---

## 1. Install the kit

The kit is a plugin; installing it makes its skills available as `/physkit:<skill>` in **every**
session on that machine. `<KIT_DIR>` below is the full path to the `kit` folder (quote it — it has
spaces); on the lab Windows machines that's
`G:\Shared drives\PHYS - Walsworth Group\Experiment folders\Machine Learning\physkit-dev\physkit-internal\kit`.
Pick whichever fits where you are:

**Option A — Quick test, no install (per session).** Best while iterating on the kit; reads the files
live, no marketplace needed:
```
claude --plugin-dir "<KIT_DIR>"
```
Re-run `/reload-plugins` after editing the kit. Coexists with `--dangerously-skip-permissions`.

**Option B — Persistent install from GitHub (best across several machines).** Same command on every
computer, no shared-drive dependency:
```
/plugin marketplace add <OWNER>/<REPO>
/plugin install physkit@physkit
```

**Option C — Persistent install from a local / shared-drive copy.** If the machine can see the `kit`
folder directly — including a `kit` folder you've unzipped from a distributed `physkit-kit.zip` (extract
it to a short local path first, e.g. `C:\physkit\kit`):
```
/plugin marketplace add "<KIT_DIR>"
/plugin install physkit@physkit
```
Because the install is cached, after editing the kit run `/plugin marketplace update physkit` to
pull the changes (Option A avoids this — it always reads live).

> **Run B/C as separate commands.** The `marketplace add` / `install` / `reload-plugins` lines are three
> distinct steps — run them one at a time, not pasted together. If `/plugin marketplace add` opens an
> **"Enter marketplace source:"** box, type **only the path — no quotes, nothing after it** — then Enter
> (the quoted form only works when you type the whole `/plugin marketplace add "…"` line at once).

Confirm any install with `/plugin list`, then `/reload-plugins` to activate immediately. After that,
`/physkit:new-campaign` and the other skills are available in all projects, namespaced
`/physkit:<skill>`.

**Make the doctrine always-on (recommended for everyday use).** Installing the plugin makes the *skills*
available, but Claude Code does **not** auto-load the kit's doctrine docs — and a doc read once falls out
of context over a long session. The fix: put the spine in your project's `CLAUDE.md`, which Claude Code
re-injects every turn. Either add one import line pointing at the kit —
`@<path-to-kit>/docs/CORE.md` — or copy the body of `docs/CORE.md` into a `CLAUDE.md` in your project
folder. The import keeps you current automatically; the copy is the fallback if imports don't resolve on
your setup. *(`CORE.md` is the single source — the former `templates/CLAUDE.general.md` duplicate was
retired 2026-07-03.)* (For campaigns it's the other way round: `new-campaign` generates a campaign-specific
`CLAUDE.md` carrying a **frozen, provenance-stamped snapshot** of this spine — the campaign's reproducible
doctrine record, not a live import — see §4.)

## 2. Start a campaign — the interview

### First: the Project home (every campaign lives in one)
Every campaign lives inside a **Project** — one folder that holds the shared **data** and
**physics/conventions/instrument** docs *once* (referenced by every campaign, never copied), a single
**`LINEAGE.md`** index of what each attempt changed and found, and the campaigns + ad-hoc sessions themselves.
There is no bare-campaign mode: in a Project, a campaign grows into a sibling, a fork, or an ad-hoc follow-up
session with **zero reorganization** and no path rewrites.

**You don't have to make it yourself.** `/physkit:new-campaign` finds the Project home or scaffolds one
(`PROJECT.md` · `LINEAGE.md` · `data/` · `shared/` · `campaigns/` · `sessions/` · `reports/`), then continues
into the interview below — wiring the campaign to the shared `../../data` + `../../shared/` and appending its
`LINEAGE.md` row. A campaign built before this default is **lifted into a Project** the same way.

**If a change invalidated a campaign's findings** (a forward-model bug, a corrected metric), use
**`/physkit:fork-campaign`** — it archives the old campaign and starts a clean-ledger sibling, carrying forward
only findings that survive re-verification.

In your session, run:

```
/physkit:new-campaign     # the front door — creates or finds the Project home, then interviews
/physkit:new-project      # start at the Project level instead; ends in the same campaign interview
```

**What to expect.** The skill first harvests everything it can from what's already available — your
prior messages, any setup docs or paper manuscripts you point it at, data files in the project, and
things it can detect itself (your CPU/GPU, data shapes). Then it interviews you **topic by topic**,
asking only about genuine gaps:

- the **goal** and the core decision it drives,
- which **archetype(s)** apply — none, one, or several from the kit's catalog (fit/decoder,
  forward-model, generative design, ML training, inverse-problem/reconstruction, hardware-in-the-loop,
  discovery loop, active experimental design, model discrimination; full set A–I in
  `ARCHETYPE_CHEATSHEET.md`),
- the **metric** — co-designed with you (this is the most important step; it becomes FROZEN),
- the **physics/system** (geometry, materials, orientations, governing equations),
- the **data**, the **levers vs what's frozen**, any **experimental/hardware constraints**,
- your **compute and time budget**, the **environment** to use, and whether to include **literature
  search**,
- and whether the work should be split into **multiple sequential loops**.

**Tips for a good result:** point it at the documents/papers that describe your setup (it prefers arXiv
versions and reads them efficiently), and tell it where your data lives. If a long planning discussion
converges before the tree is generated, ask the agent to write the locked decisions to a file as they
settle — a plan that lives only in the chat is lost if the session drops (`handoff` covers this habit).

Before writing anything, it shows you a **campaign spec** for sign-off — your chance to correct course.
Then it generates the tree — the Project home, if you don't already have one, and the campaign inside it —
and validates that nothing is left blank:

```
your-project/
  PROJECT.md            the system, the end goal, project-wide invariants, the data/shared pointers
  LINEAGE.md            the index — every campaign and session, what it changed, what it found
  DISCOVERIES.md        project-wide verified findings, promoted from campaigns (survive a fork)
  ENGINEERING_NOTES.md  durable project-wide decisions and their "why"
  CLAUDE.md             the project's always-on rules, auto-loaded anywhere in the tree
  data/                 the canonical data, read-only — or a DATA_PATH.txt pointer to where it lives
  shared/               referenced by every campaign, never copied
    PHYSICS.md          governing equations, methods, the effect inventory (a living doc)
    CONVENTIONS.md      units, signs, ordering — the bug-prevention reference
    INSTRUMENT.md       the measurement rig / apparatus + sample parameters (when relevant)
  sessions/             ad-hoc work — one <date>_<slug>/NOTES.md each, no frozen metric
  reports/              the single home for project-level outputs
  campaigns/01_<slug>/  the campaign the interview generates (siblings get 02_, 03_, …)
    docs/
      charter.md            the loop charter the agent re-reads every iteration
      VERIFICATION_PLAN.md  how you'll know the answer is right — drafted before the work
      PROJECT_ORIENTATION.md  the goal, done-criteria, and the goal-linked task list
      ENGINEERING_NOTES.md  the decision / "why" record (conditions + revisit-if triggers)
      protocols/            metric · baselines · checkpoint · journal_consolidation · artifacts · dataset · expensive-evaluation
    configs/
      _template.json      copy this per experiment
      exp000_*.json …     one config per experiment   ·   RECOMMENDED.json  the current-best config
    results/
      scoreboard.tsv      the numbers (one row per experiment)
      INDEX.md            the map (each experiment → its config, snapshot, result, figures, status)
      JOURNAL.md          the working window + NEXT pointer   ·   DISCOVERIES.md  settled, verified findings
      logbook.md          the full narrative record (append-only; never read whole)
      snapshots/ images/ data/ diagnostics/    per-experiment artifacts
    scripts/
      metric.py           the FROZEN scorer (+ --selftest)   ·   run_campaign.py  the experiment runner
      guard_discoveries.py  the hook that blocks a DISCOVERIES write with no recent verification
      loop_heartbeat.py     the hook that keeps the loop running until you stop it (§4)
    tests/                correctness_checks.py — the standing checks, green before a result is trusted
    CLAUDE.md   .claude/settings.json     the campaign's always-on doctrine + the hook wiring
    INTAKE.md   README.md   LITERATURE.md   (LITERATURE.md only if you enabled literature search or provided sources)
```

## 3. Get ready to run

The generated campaign tells you the first action, which is always:

1. Implement the metric in `scripts/metric.py` and make `python scripts/metric.py --selftest` pass —
   this freezes the scorer and catches sign/convention bugs before they can corrupt the campaign.
2. Run **experiment 000** (the baseline gate), which also validates the data/scoring pipeline.

(If you prefer, the loop-running agent will do these as its first steps.)

## 4. Launch the loop

The campaign is designed to **run continuously** — hypothesize → run → evaluate → log → verify →
repeat — until you stop it. Because it issues many tool calls, the smoothest way to run it is from the
Claude CLI with permission prompts disabled, **from inside the campaign folder**:

```
cd "E:\path\to\your\campaign"
claude --dangerously-skip-permissions
```
*(If you used the per-session `--plugin-dir` method instead of installing, add
`--plugin-dir "<KIT_DIR>"` to this command too.)*

**This fresh session is required, not optional.** Starting Claude *inside the campaign folder* is what
auto-loads the campaign's `CLAUDE.md` (the always-on doctrine + hard gates) and activates the two
enforcement hooks — the DISCOVERIES verify gate and the loop heartbeat that keeps the run going.
**Do not run the loop in the same session that scaffolded the campaign** — it has neither. Confirm with
`/context` that `CLAUDE.md` is loaded before you start.

Then kick it off with a prompt like:

> Read `docs/charter.md` and the `results/` ledger, then run the autonomous research loop continuously
> until I stop you.

**Why `--dangerously-skip-permissions`:** the loop runs unattended and makes many edits, runs, and
file writes; without it you'd have to approve each one and the loop would stall. **Use it deliberately:**
run it from the campaign's own folder, in a project you trust, so the agent's actions stay scoped to the
work.

### Stopping the loop

The campaign keeps going on its own: a `Stop` hook (`scripts/loop_heartbeat.py`) refuses an end-of-turn
that isn't a real stop and hands the agent back its own `NEXT` pointer, because "the experiment finished"
is not a reason to stop. So there are two ways to end a run:

- **`Ctrl-C`** — immediate, mid-experiment. Nothing in flight gets logged.
- **Create `results/STOP`** — the graceful stop. The agent finishes and logs the experiment it is running,
  then exits cleanly. Do this from any other terminal while the loop runs; delete the file to resume.

  ```bash
  New-Item -ItemType File "results/STOP"
  ```

The agent can also end the run itself, but only by *recording why* in `results/stop_request.json` — an
ambiguous goal that needs your call, a hard-to-reverse action awaiting your confirmation, a real external
blocker, or a direction that is genuinely exhausted (which it may not claim while any lever it has named
remains untried). Every stop is logged to `results/loop_stops.log`, so "why did this campaign end?" is
always answerable from the ledger. If the loop is continued repeatedly without producing a new scoreboard
row it releases itself and records a `STALL_RELEASE` — that means the run was alive but doing no science,
and is worth diagnosing before you restart.

**What to expect while it runs:** every experiment is logged to `results/scoreboard.tsv` (the numbers)
and indexed in `results/INDEX.md` (a map to each experiment's config, snapshot, result, and figures),
with a narrative in `results/JOURNAL.md`; a basic figure is saved for every experiment (more for notable
ones); promising findings are independently verified before being promoted; and settled conclusions
graduate to `results/DISCOVERIES.md`. Check in whenever you like — the ledger and index are the full record.

## Troubleshooting

- **`/physkit:…` skills don't appear after install** → run `/reload-plugins`, and confirm with
  `/plugin list` that `physkit` is enabled.
- **`scripts/metric.py --selftest` fails** → the metric isn't implemented yet, or there's a sign/units
  bug. Fix it before experiment 000 — the self-test exists precisely to catch this early.
- **The loop keeps pausing for permission** → it wasn't launched with `--dangerously-skip-permissions`
  (or not from the campaign folder). Restart it as in §4.
- **The loop stops after every experiment and needs nudging** → the heartbeat hook isn't firing. Check that
  `.claude/settings.json` has a `Stop` entry for `scripts/loop_heartbeat.py`, that the python command in it
  actually runs on this machine, and that the session was started *inside* the campaign folder (§4). An
  imported or hand-assembled tree is the usual culprit — `/physkit:campaign-status` flags a missing hook.
- **The loop won't stop** → create `results/STOP` (graceful) or press `Ctrl-C` (immediate). To disable the
  heartbeat entirely for a debugging session, set `AUTORESEARCH_LOOP_HEARTBEAT=off` before launching.
- **You want to change something the agent froze** (the metric, the core physics) → those need your
  explicit sign-off; just tell the agent — it won't change them on its own.
- **A generated file still shows `{{PLACEHOLDER}}`** → generation didn't finish cleanly; ask the agent to
  re-run the new-campaign validation step (it has a checker that flags leftover placeholders).

---

*The kit ships two layers of skills, all namespaced `/physkit:<name>`. **General science toolkit**
(usable in any session): `assess-idea`, `literature-review`, `frame-problem`, `verify`, `simulation-design`,
`correctness-suite`, `debug`, `dimensional-analysis`, `derive`, `attribute-mechanism`, `record-decision`, `cite-check`, `report`. **Campaign layer**:
`new-campaign` (scaffold + interview), `campaign-status` (periodic checkpoint), `handoff` (cold-resume),
`discovery-loop`, `experiment-design`, `model-selection`, and `final-report` (end-of-campaign report).*
