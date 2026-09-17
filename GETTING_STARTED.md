# Getting Started — PhysKit

A guide from a research idea to a running, autonomous research campaign. It covers setup, the
interview, and launching the loop.

> PhysKit installs as a full plugin in Claude Code or Codex. Skills appear as `/physkit:<name>` in
> Claude Code and `$physkit:<name>` in Codex; both harnesses may also select them automatically.

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

`<KIT_DIR>` below is the full path to the `kit` folder; quote it if the path contains spaces. Campaigns
need the full plugin package—not a copy of `skills/` alone—because scaffolding reads bundled templates,
doctrine, scripts, and validators.

### Codex

Register the local marketplace and install the full package:

```
codex plugin marketplace add "<KIT_DIR>"
codex plugin add physkit@physkit
```

Confirm with `codex plugin list`, then start a new Codex task so it loads the refreshed plugin. The
skills-only `~/.agents/skills` projection is suitable for general science work but is not a
campaign-capable install.

After changing or updating the local package, rerun `codex plugin add physkit@physkit`, confirm with
`codex plugin list --marketplace physkit`, and start another new task. Marketplace registration is only
needed the first time.

### Claude Code

Installing the plugin makes its skills available as `/physkit:<skill>` in every Claude Code session on
that machine. Pick the option that fits your setup.

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

Confirm a Claude install with `/plugin list`, then `/reload-plugins` to activate immediately.
`/physkit:new-campaign` and the other skills are then available in all projects.

Make the doctrine always-on (recommended for everyday use). The plugin makes the skills available, but
does not automatically inject the doctrine docs into an ordinary project. In Claude Code, put the spine
in `CLAUDE.md`: either add `@<path-to-kit>/docs/CORE.md`, or copy the body of `docs/CORE.md`. In Codex,
copy that body into `AGENTS.md`. If the project is used with both harnesses, author once and materialize
identical `CLAUDE.md` and `AGENTS.md` files; a scaffolded campaign does this and checks consistency for
you. `CORE.md` is the single source for the spine.
Campaigns work the other way round: `new-campaign` stamps the kit **version** into the campaign
(`campaign.md`'s header and the top of `results/logbook.md`) — its doctrine and tooling provenance,
since every release is tagged and the pin recovers the whole kit, not a live import (see §4). The
campaign's own `CLAUDE.md`/`AGENTS.md` twins stay light: always-on carries what binds a turn (the integrity core, the
reflexes, the hard gates, the file map), and the reasoning behind those rules is the plugin's
`docs/CORE.md` at the stamped version rather than in every turn's context.

## 2. Start a campaign — the interview

### First: the Project home (every campaign lives in one)
Every campaign lives inside a **Project**: one folder holding the shared data and the physics,
conventions, and instrument docs once, referenced by every campaign and never copied. It also holds a
single lineage index (`PROJECT.md` §Lineage) of what each attempt changed and found, plus the campaigns and ad-hoc
sessions. There is no bare-campaign mode. Inside a Project a campaign grows into a sibling, a fork,
or an ad-hoc follow-up session with no reorganization and no path rewrites.

You need not create the Project yourself. `/physkit:new-campaign` finds the Project home or
scaffolds one (`README.md` · `PROJECT.md` · `CLAUDE.md` · `data/` · `campaigns/` · `sessions/` ·
`reports/`), then continues into the interview below. It wires the campaign to the shared
`../../data` and appends its `PROJECT.md` §Lineage row. A campaign that already exists
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
- the metric, co-designed with you; it governs everything downstream and becomes FROZEN — locked
  against quiet change: a revision is a declared metric epoch, never an in-place edit —
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
  README.md             the front door — a very short "where to find things" map for someone new
  PROJECT.md            THE overview (a living doc, edited by tier): §Mission — the goal and
                        project-wide invariants · §Standing constraints — delivered into every
                        spawned worker/planner prompt, every cycle · the system, instrument, and
                        equations depth · §Updates from discoveries — verified findings, each citing
                        its campaign's verdict · §Durable decisions · §Lineage — every campaign and
                        session, what it changed, what it found
  CLAUDE.md             the project's always-on rules for Claude Code
  AGENTS.md             exact managed twin, auto-loaded by Codex
  data/                 the canonical data, read-only — or a DATA_PATH.txt pointer to where it lives
  scripts/ models/ …    promoted frozen artifacts, in purpose-named dirs created at first promotion
  sessions/             ad-hoc work — one <date>_<slug>/NOTES.md each, no frozen metric
  reports/              the single home for project-level outputs
  campaigns/01_<slug>/  the campaign the interview generates (siblings get 02_, 03_, …)
    README.md             the front door for anyone new to the tree: purpose, how the loop runs,
                          who reads what when, and §Setup status — what is not built yet
    CLAUDE.md             Claude always-on: integrity core + reflexes + gates + §Where things live,
                          this campaign's map of itself
    AGENTS.md             exact managed twin for Codex; resume/spawn checks enforce consistency
    campaign.md           THE campaign definition and the ONE human sign-off surface — mission +
                          done-criteria + expectations, metric, levers, FROZEN, §Known landmines, caps,
                          §Verification (this campaign's own checks), promotion, and the append-only
                          §Decision record tail. Both roles re-read it every cycle; its header stamps
                          the physkit version the campaign runs under
    roles/
      worker.md           the per-experiment procedure: the loop, the iteration contract, the save-set
      planner.md          strategy: getting unstuck, reopening shelved directions
    configs/
      _template.json      copy this per experiment
      exp000_*.json …     one config per experiment   ·   RECOMMENDED.json  the current-best config
      loop.json           the driver's knobs + the campaign properties every check branches on —
                          prediction mode, noise model, comparability tags, metric_revision (who
                          may revise the FROZEN metric: cautious asks you first; autonomous enacts a
                          verified revision as a pending epoch for you to ratify), and verify.preset
                          (how much verification the campaign buys, and of what kind: minimal · light
                          · moderate · intensive — docs/reference/verification-presets.md). A campaign that has
                          revised its metric also carries metric_epochs here — one entry per
                          metric_version with its evidence and standing; a scorer change no epoch
                          declares refuses to run
    predictions/          one per experiment, written BEFORE the solve — the runner refuses to spend
                          an experiment without it
    results/
      scoreboard.tsv      the numbers and the one-line timeline (one row per experiment; a settled
                          fact is its row's verdict-cited `finding` cell) — every cell runner-written
      JOURNAL.md          the campaign's working memory: NEXT pointer, where we stand, live hypotheses,
                          what to try next (bounded; brought up to date every unit)
      logbook.md          the full narrative record (append-only; never opened — `--show <exp>`)
      result_<NN>.json    what one experiment produced   ·   checks_<NN>.json  its mechanical checks,
                          each pass / fail / unavailable, what an unavailable one would need, what the
                          experiment changed, the worker's self-check, and its verification label
      verdicts/           independent-verification verdicts + audit_<NN>.json (the claim audit)   ·
                          correctness_state.json  the standing suite's per-check status — the
                          promotion gate reads both
      queue.json          the loop's worklist — the driver pops a unit at a time, the planner refills it
      snapshots/ images/ data/ diagnostics/    per-experiment artifacts
    scripts/
      metric.py           the FROZEN scorer (+ --selftest)   ·   run_campaign.py  the experiment runner
      guard_promotion.py    the shared hook policy that blocks an unverified, subject-mismatched promotion
      guard_promotion_codex.py  the Codex apply_patch adapter for that unchanged policy
      loop_heartbeat.py     the Stop hook guarding attended sessions (stands down while the driver runs)
    tests/                correctness_checks.py — the standing checks, each declaring its row (invariants
                          every unit · machinery on setup / code change · gates at promotion), plus the
                          setup audit's four contract checks; green before a result is trusted
    .claude/settings.json   Claude hook wiring   ·   .codex/hooks.json  Codex promotion-hook wiring
    LITERATURE.md         only if you enabled literature search or provided sources
```

## 3. Get ready to run

Scaffolding hands off launch-ready: the metric is implemented and `python scripts/metric.py --selftest`
passes (the scorer is frozen, with sign and convention bugs caught before they can corrupt the
campaign), the experiment hooks are wired, and experiment 000 — the baseline gate, which also validates
the data and scoring pipeline — is queued as the loop's first unit. Confirm at any time with:

```
python scripts/run_campaign.py --preflight --backend codex   # from Codex
python scripts/run_campaign.py --preflight --backend claude  # from Claude Code
```

For Codex, open a fresh task from the campaign root and run `/hooks` to review/trust the exact
project-local `.codex/hooks.json` definition before relying on the promotion gate. The scaffold
validator can check the file and command, but host trust is deliberately not inferred.

If scaffolding handed over anything it could not finish (data only you can stage, an instrument to
connect), it is named in the handoff message and in `results/JOURNAL.md` **NEXT** — clear those first;
preflight names them again until they are fixed.

## 4. Launch the loop

The campaign runs in supervisor mode: a deterministic driver pops one experiment unit at a time from
`results/queue.json` and spawns a fresh agent per unit. Every worker re-reads the doctrine and the
campaign definition by construction, context does not accumulate across experiments, and the gates
are enforced in code. Your session supervises; the driver runs the experiments.

Open a fresh task/session from inside the campaign folder. In Codex, confirm `AGENTS.md` is loaded,
run `/hooks` once to review and trust the campaign hook, then invoke:

> $physkit:run-campaign

In Claude Code, start the established trusted session:

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

The skill checks the campaign is launch-ready with the driver's `--preflight --backend <active harness>`,
which reports every failure translated and with its fix, starts
`scripts/run_campaign.py --supervise --backend <active harness>` in the background,
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

Codex workers instead use native `codex exec` with the `workspace-write` sandbox; PhysKit adds neither
dangerous Codex bypass flag. Prompts travel through UTF-8 stdin and the driver records each Codex thread
ID. If Windows resolves `codex` to an inaccessible app alias, preflight asks for the absolute executable
in `AUTORESEARCH_CODEX_EXE`. In `configs/loop.json`, each role's Claude launch reads `model` +
`claude_effort`, while its Codex launch reads `codex_model` + `codex_reasoning_effort`. Leave any field
blank to inherit that harness's configured default. Codex's direct verifier follows the worker Codex pair;
Claude's established nested verifier follows the planner Claude pair.

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
narrative in `results/logbook.md` and the campaign's working memory kept current in `results/JOURNAL.md`.
A basic figure is saved for every experiment, and more for notable ones. Promising findings are
independently verified before being promoted, and a settled conclusion is written into its ledger row's
verdict-cited `finding` cell. The ledger and logbook are the full record, readable at any time.
`/physkit:campaign-status` answers where the campaign stands; the concierge answers what the loop is
doing now.

## Troubleshooting

- Claude `/physkit:…` skills do not appear after install → run `/reload-plugins`, and confirm with
  `/plugin list` that `physkit` is enabled. Codex `$physkit:…` skills do not appear → confirm
  `physkit@physkit` is installed and enabled with `codex plugin list`, then start a new task.
- `scripts/metric.py --selftest` fails → the metric isn't implemented yet, or there is a sign or
  units bug. Fix it before experiment 000; the self-test exists to catch this early.
- The loop keeps pausing for permission → it wasn't launched with `--dangerously-skip-permissions`,
  or not from the campaign folder. Restart it as in §4.
- The launch fails or nothing happens → run `python scripts/run_campaign.py --preflight --backend <active harness>`, which the
  concierge does automatically. Every problem it finds is printed with its fix: a missing agent CLI,
  an unfilled loop knob, a corrupt queue, an unimplemented metric.
- The driver halted overnight → read the tail of the newest `results/diagnostics/supervise_*.log`, or
  ask the concierge why the loop stopped. Single-unit failures don't halt the loop; they are shelved
  in `results/queue.json` with reasons. A halt means an integrity condition (ESCALATE, corrupt queue,
  out of directions) or several failures in a row, indicating an environment problem: CLI,
  credentials, or disk.
- The loop won't stop → create `results/STOP` (graceful) or `Ctrl-C` the driver (immediate). To
  disable the Stop-hook heartbeat for a debugging session, set `AUTORESEARCH_LOOP_HEARTBEAT=off`.
- You want to change something the agent froze, such as the metric or the core physics → the metric is
  revised only as a declared metric epoch, never edited in place. Under `cautious` (the default) the
  loop proposes in `results/ESCALATE.md` and waits for you; under `autonomous` it enacts a verified
  revision as a *pending* epoch that you ratify afterwards. Core physics still needs your explicit
  sign-off.
- A generated file still shows `{{PLACEHOLDER}}` → generation didn't finish cleanly. Ask the agent to
  re-run the new-campaign validation step; it has a checker that flags leftover placeholders.

---

*The kit ships two layers of skills, namespaced `/physkit:<name>` in Claude Code and
`$physkit:<name>` in Codex. **General science toolkit**
(usable in any session): `assess-idea`, `literature-review`, `frame-problem`, `verify`, `simulation-design`,
`correctness-suite`, `debug`, `dimensional-analysis`, `derive`, `attribute-mechanism`, `record-decision`, `cite-check`, `report`. **Campaign layer**:
`new-campaign` (scaffold + interview), `run-campaign` (launch/monitor/steer the supervised loop),
`campaign-status` (periodic checkpoint), `handoff` (cold-resume),
`discovery-loop`, `experiment-design`, `model-selection`; the end-of-campaign capstone is `report` in its campaign mode.*
