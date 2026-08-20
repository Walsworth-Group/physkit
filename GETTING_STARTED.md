# Getting Started — PhysKit

A guide from a research idea to a running, autonomous research campaign. It covers setup, the
interview, and launching the loop.

> The kit is a Claude Code plugin named `physkit`. Its skills appear as `/physkit:<name>` once the
> plugin is loaded.

The kit has two layers. The **general science toolkit** (`frame-problem`, `verify`,
`simulation-design`, `correctness-suite`, `debug`, `derive`, `report`, and others) applies in any
session, campaign or not, and triggers on everyday science requests. The **campaign layer** scaffolds
and runs autonomous-research loops. This guide covers the campaign path. The general skills need no
setup beyond installing the plugin; the full list is at the bottom.

> Five skills to know by name; the agent reaches the rest on its own and suggests them when relevant.
> `frame-problem` (start any physics problem here) · `verify` (check a result before relying on it) ·
> `report` (write it up, provenance-labeled) · `new-campaign` (stand up a loop) · `campaign-status`
> (checkpoint a running loop).

---

## 1. Install the kit

Installing the plugin makes its skills available as `/physkit:<skill>` in every session on that
machine. `<KIT_DIR>` below is the full path to the `kit` folder; quote it if the path contains
spaces. Pick the option that fits your setup.

Option A — quick test, no install, per session. It reads the files live and needs no marketplace,
which suits iterating on the kit:
```
claude --plugin-dir "<KIT_DIR>"
```
Re-run `/reload-plugins` after editing the kit. Coexists with `--dangerously-skip-permissions`.

Option B — persistent install from GitHub, for several machines. Same command everywhere, no
shared-drive dependency:
```
/plugin marketplace add <OWNER>/<REPO>
/plugin install physkit@physkit
```

Option C — persistent install from a local or shared-drive copy. Use it when the machine can see the
`kit` folder directly, including one unzipped from a distributed `physkit-kit.zip` (extract to a
short local path first, for example `C:\physkit\kit`):
```
/plugin marketplace add "<KIT_DIR>"
/plugin install physkit@physkit
```
The install is cached: after editing the kit, run `/plugin marketplace update physkit` to pull the
changes. Option A always reads live and avoids this step.

> Run the B and C commands separately. `marketplace add`, `install`, and `reload-plugins` are three
> distinct steps; run them one at a time, not pasted together. If `/plugin marketplace add` opens an
> "Enter marketplace source:" box, type only the path, with no quotes and nothing after it, then
> press Enter. The quoted form works only when the whole `/plugin marketplace add "…"` line is typed
> at once.

Confirm any install with `/plugin list`, then `/reload-plugins` to activate immediately.
`/physkit:new-campaign` and the other skills are then available in all projects.

Make the doctrine always-on (recommended for everyday use). The plugin makes the skills available,
but Claude Code does not auto-load the kit's doctrine docs, and a doc read once falls out of context
over a long session. Put the spine in your project's `CLAUDE.md`, which Claude Code re-injects every
turn: either add the import line `@<path-to-kit>/docs/CORE.md`, or copy the body of `docs/CORE.md`
into a `CLAUDE.md` in your project folder. The import stays current automatically; the copy is the
fallback when imports do not resolve on your setup. `CORE.md` is the single source for this spine.
Campaigns work the other way round: `new-campaign` writes a frozen, provenance-stamped snapshot of the
spine into the campaign's `DOCTRINE_SNAPSHOT.md` — its reproducible doctrine record, not a live import
(see §4). The campaign's own `CLAUDE.md` stays light and references it: always-on carries what binds a
turn (the integrity core, the reflexes, the hard gates, the file map), and the reasoning behind those
rules is one file away rather than in every turn's context.

## 2. Start a campaign — the interview

### First: the Project home (every campaign lives in one)
Every campaign lives inside a **Project**: one folder holding the shared data and the physics,
conventions, and instrument docs once, referenced by every campaign and never copied. It also holds a
single `LINEAGE.md` index of what each attempt changed and found, plus the campaigns and ad-hoc
sessions. There is no bare-campaign mode. Inside a Project a campaign grows into a sibling, a fork,
or an ad-hoc follow-up session with no reorganization and no path rewrites.

You need not create the Project yourself. `/physkit:new-campaign` finds the Project home or
scaffolds one (`PROJECT.md` · `LINEAGE.md` · `data/` · `shared/` · `campaigns/` · `sessions/` ·
`reports/`), then continues into the interview below. It wires the campaign to the shared
`../../data` and `../../shared/` and appends its `LINEAGE.md` row. A campaign that already exists
outside a Project is lifted into one the same way.

If a change invalidated a campaign's findings, such as a forward-model bug or a corrected metric, use
`/physkit:fork-campaign`. It archives the old campaign and starts a clean-ledger sibling, carrying
forward only findings that survive re-verification.

In your session, run:

```
/physkit:new-campaign     # the front door — creates or finds the Project home, then interviews
/physkit:new-project      # start at the Project level instead; ends in the same campaign interview
```

What to expect: the skill first harvests everything it can from what is already available — your
prior messages, any setup docs or paper manuscripts you point it at, data files in the project, and
what it can detect itself, such as your CPU/GPU and data shapes. It then interviews you topic by
topic, asking only about gaps:

- the goal and the core decision it drives,
- which archetype(s) apply — none, one, or several from the kit's catalog (fit/decoder,
  forward-model, generative design, ML training, inverse-problem/reconstruction, hardware-in-the-loop,
  discovery loop, active experimental design, model discrimination; full set A–I in
  `ARCHETYPE_CHEATSHEET.md`),
- the metric, co-designed with you; it governs everything downstream and becomes FROZEN,
- the physics/system (geometry, materials, orientations, governing equations),
- the data, the levers versus what is frozen, any experimental or hardware constraints,
- your compute and time budget, the environment to use, and whether to include literature search,
- and whether the work should be split into multiple sequential loops.

For a good result, point it at the documents and papers that describe your setup; it prefers arXiv
versions and reads them efficiently. Tell it where your data lives. If a long planning discussion
converges before the tree is generated, ask the agent to write the locked decisions to a file as they
settle. A plan that lives only in the chat is lost if the session drops (`handoff` covers this).

Before writing anything, it shows you a campaign spec for sign-off; correct the course there. It then
generates the tree, including the Project home if you lack one, and validates that nothing is left
blank:

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
    CLAUDE.md             always-on: integrity core + reflexes + the hard gates + §Where things live,
                          this campaign's map of itself
    DOCTRINE_SNAPSHOT.md  the frozen doctrine this campaign runs under — referenced, never auto-loaded
    campaign.md           THE campaign definition — mission, metric, levers, FROZEN, caps, promotion.
                          Both roles re-read it every cycle
    roles/
      worker.md           the per-experiment procedure: the loop, the iteration contract, the save-set
      planner.md          strategy: getting unstuck, reopening shelved directions
    docs/
      VERIFICATION_PLAN.md  how you'll know the answer is right — drafted before the work
      PROJECT_ORIENTATION.md  the goal, done-criteria, and the goal-linked task list
      ENGINEERING_NOTES.md  the decision / "why" record (conditions + revisit-if triggers)
    configs/
      _template.json      copy this per experiment
      exp000_*.json …     one config per experiment   ·   RECOMMENDED.json  the current-best config
      loop.json           the driver's knobs + the campaign properties every check branches on —
                          prediction mode, noise model, comparability tags
    predictions/          one per experiment, written BEFORE the solve — the runner refuses to spend
                          an experiment without it
    results/
      scoreboard.tsv      the numbers (one row per experiment)
      JOURNAL.md          the working window + NEXT pointer   ·   DISCOVERIES.md  settled, verified findings
      logbook.md          the full narrative record (append-only; never read whole)
      result_<NN>.json    what one experiment produced   ·   checks_<NN>.json  its mechanical checks,
                          each pass / fail / unavailable, and what an unavailable one would need
      verdicts/           independent-verification verdicts   ·   correctness_state.json  the standing
                          suite's status — the promotion gate reads both
      queue.json          the loop's worklist — the driver pops a unit at a time, the planner refills it
      snapshots/ images/ data/ diagnostics/    per-experiment artifacts
    scripts/
      metric.py           the FROZEN scorer (+ --selftest)   ·   run_campaign.py  the experiment runner
      guard_discoveries.py  the hook that blocks a DISCOVERIES write with no recent verification
      loop_heartbeat.py     the Stop hook guarding attended sessions (stands down while the driver runs)
    tests/                correctness_checks.py — the standing checks, green before a result is trusted
    CLAUDE.md   .claude/settings.json     the campaign's always-on doctrine + the hook wiring
    INTAKE.md   README.md   LITERATURE.md   (LITERATURE.md only if you enabled literature search or provided sources)
```

## 3. Get ready to run

The generated campaign states the first action, which is always:

1. Implement the metric in `scripts/metric.py` and make `python scripts/metric.py --selftest` pass.
   This freezes the scorer and catches sign and convention bugs before they can corrupt the campaign.
2. Run experiment 000, the baseline gate, which also validates the data and scoring pipeline.

The loop-running agent will do both as its first steps if you prefer.

## 4. Launch the loop

The campaign runs in supervisor mode: a deterministic driver pops one experiment unit at a time from
`results/queue.json` and spawns a fresh agent per unit. Every worker re-reads the doctrine and the
campaign definition by construction, context does not accumulate across experiments, and the gates
are enforced in code. Your session supervises; the driver runs the experiments.

Open a fresh Claude session from inside the campaign folder:

```
cd "E:\path\to\your\campaign"
claude --dangerously-skip-permissions
```
If you used the per-session `--plugin-dir` method instead of installing, add
`--plugin-dir "<KIT_DIR>"` to this command too.

The fresh session is required, not optional. Starting Claude inside the campaign folder auto-loads
the campaign's `CLAUDE.md` (the always-on doctrine and the hard gates) and activates the enforcement
hooks. Do not run the loop in the session that scaffolded the campaign; it has neither. Confirm with
`/context` that `CLAUDE.md` is loaded.

Then say:

> /physkit:run-campaign

The skill checks the campaign is launch-ready with the driver's `--preflight`, which reports every
failure translated and with its fix, starts `scripts/run_campaign.py --supervise` in the background,
and stays in the session as the loop's concierge:

- Watch. Ask what the loop is doing; it narrates from the driver's live log
  (`results/diagnostics/supervise_*.log`): current unit, worker activity, accepted-unit count,
  planner passes.
- Steer without stopping. A request such as "stop exploring lever X" is dropped in `results/inbox/`,
  the driver hands it verbatim to the next worker or planner, and the worker must acknowledge in the
  journal what it changed.
- Triage. If the driver halts, the concierge reads the log and the queue, explains the cause in plain
  language, and proposes the fix. The driver hard-halts only on integrity conditions or several
  failures in a row; a single misbehaving worker has its unit shelved, with reasons recorded, while
  the loop continues.

Why `--dangerously-skip-permissions`: the loop runs unattended and makes many edits, runs, and file
writes. Without it you would have to approve each one and the loop would stall. Run it from the campaign's
own folder, in a project you trust, so the agent's actions stay scoped to the work.

Why not chat the loop into running in this session? A single growing context degrades the loop in
four ways: the campaign definition is eventually pushed out of the window; agents stop re-reading
the docs they are required to re-read; runs stop prematurely; and verification decays from a gate
into a suggestion. Fresh context per unit and gates in code prevent all four. A by-hand
`python scripts/run_campaign.py --config …` run is still fine for debugging one experiment, under the
same gates, but it is not a way to run the loop.

### Stopping the loop

Ask the concierge to stop the loop, or do it directly from any terminal:

- Create `results/STOP` for the graceful stop. The driver lets the unit in flight finish and log,
  then exits cleanly, recorded in `results/loop_stops.log`. Delete the file before the next launch.

  ```powershell
  New-Item -ItemType File "results/STOP"
  ```
- `Ctrl-C` the driver, or ask the concierge to kill it, for an immediate stop. The current unit is
  killed and stays at the head of the queue, so a relaunch resumes at that unit.

The loop can also stop on its own. A worker that hits a fork needing your decision writes
`results/ESCALATE.md` and the driver halts and reports it; a campaign out of proposed directions
halts as an explicit stopping decision. Every stop leaves a record in `results/loop_stops.log` and
the driver log, so why a campaign ended is always answerable from the ledger.

What to expect while it runs. Every experiment is logged to `results/scoreboard.tsv`, with a
narrative in `results/JOURNAL.md`. A basic figure is saved for every experiment, and more for notable
ones. Promising findings are independently verified before being promoted, and settled conclusions
graduate to `results/DISCOVERIES.md`. The ledger and journal are the full record, readable at any time.
`/physkit:campaign-status` answers where the campaign stands; the concierge answers what the loop is
doing now.

## Troubleshooting

- `/physkit:…` skills don't appear after install → run `/reload-plugins`, and confirm with
  `/plugin list` that `physkit` is enabled.
- `scripts/metric.py --selftest` fails → the metric isn't implemented yet, or there is a sign or
  units bug. Fix it before experiment 000; the self-test exists to catch this early.
- The loop keeps pausing for permission → it wasn't launched with `--dangerously-skip-permissions`,
  or not from the campaign folder. Restart it as in §4.
- The launch fails or nothing happens → run `python scripts/run_campaign.py --preflight`, which the
  concierge does automatically. Every problem it finds is printed with its fix: a missing agent CLI,
  an unfilled loop knob, a corrupt queue, an unimplemented metric.
- The driver halted overnight → read the tail of the newest `results/diagnostics/supervise_*.log`, or
  ask the concierge why the loop stopped. Single-unit failures don't halt the loop; they are shelved
  in `results/queue.json` with reasons. A halt means an integrity condition (ESCALATE, corrupt queue,
  out of directions) or several failures in a row, indicating an environment problem: CLI,
  credentials, or disk.
- The loop won't stop → create `results/STOP` (graceful) or `Ctrl-C` the driver (immediate). To
  disable the Stop-hook heartbeat for a debugging session, set `AUTORESEARCH_LOOP_HEARTBEAT=off`.
- You want to change something the agent froze, such as the metric or the core physics → those need
  your explicit sign-off. Tell the agent; it will not change them on its own.
- A generated file still shows `{{PLACEHOLDER}}` → generation didn't finish cleanly. Ask the agent to
  re-run the new-campaign validation step; it has a checker that flags leftover placeholders.

---

*The kit ships two layers of skills, all namespaced `/physkit:<name>`. **General science toolkit**
(usable in any session): `assess-idea`, `literature-review`, `frame-problem`, `verify`, `simulation-design`,
`correctness-suite`, `debug`, `dimensional-analysis`, `derive`, `attribute-mechanism`, `record-decision`, `cite-check`, `report`. **Campaign layer**:
`new-campaign` (scaffold + interview), `run-campaign` (launch/monitor/steer the supervised loop),
`campaign-status` (periodic checkpoint), `handoff` (cold-resume),
`discovery-loop`, `experiment-design`, `model-selection`, and `final-report` (end-of-campaign report).*
