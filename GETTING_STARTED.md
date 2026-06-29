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

---

## 1. Install the kit

The kit is a plugin; installing it makes its skills available as `/physkit:<skill>` in **every**
session on that machine. `<KIT_DIR>` below is the full path to the `kit` folder (quote it — it has
spaces); on the lab Windows machines that's
`G:\Shared drives\PHYS - Walsworth Group\Experiment folders\Machine Learning\Autoresearch paper\Auto Research Paper\kit`.
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
folder directly:
```
/plugin marketplace add "<KIT_DIR>"
/plugin install physkit@physkit
```
Because the install is cached, after editing the kit run `/plugin marketplace update physkit` to
pull the changes (Option A avoids this — it always reads live).

Confirm any install with `/plugin list`, then `/reload-plugins` to activate immediately. After that,
`/physkit:new-campaign` and the other skills are available in all projects, namespaced
`/physkit:<skill>`.

**Make the doctrine always-on (recommended for everyday use).** Installing the plugin makes the *skills*
available, but Claude Code does **not** auto-load the kit's doctrine docs — so the frozen core isn't in
context unless something pulls it in. For a general (non-campaign) project, copy
`templates/CLAUDE.general.md` from the kit to a `CLAUDE.md` in your project folder; Claude Code auto-loads
it every session, keeping the honesty/verification core in context. (For campaigns, `new-campaign`
generates a campaign-specific `CLAUDE.md` for you — see §4.)

## 2. Start a campaign — the interview

In that session, run:

```
/physkit:new-campaign
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
versions and reads them efficiently), and tell it where your data lives.

Before writing anything, it shows you a **campaign spec** for sign-off — your chance to correct course.
Then it generates a complete campaign folder and validates that nothing is left blank:

```
your-campaign/
  docs/
    program.md            the loop charter the agent re-reads every iteration
    PHYSICS.md            governing equations, methods, the effect inventory (a living doc)
    CONVENTIONS.md        units, signs, ordering — the bug-prevention reference
    VERIFICATION_PLAN.md  how you'll know the answer is right — drafted before the work
    PROJECT_ORIENTATION.md  the goal, done-criteria, and the goal-linked task list
    ENGINEERING_NOTES.md  the decision / "why" record (conditions + revisit-if triggers)
    SYSTEM.md             apparatus / sample parameters (when relevant)
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
auto-loads the campaign's `CLAUDE.md` (the always-on doctrine + hard gates) and activates the
DISCOVERIES enforcement hook. **Do not run the loop in the same session that scaffolded the campaign** —
it has neither. Confirm with `/context` that `CLAUDE.md` is loaded before you start.

Then kick it off with a prompt like:

> Read `docs/program.md` and the `results/` ledger, then run the autonomous research loop continuously
> until I stop you.

**Why `--dangerously-skip-permissions`:** the loop runs unattended and makes many edits, runs, and
file writes; without it you'd have to approve each one and the loop would stall. **Use it deliberately:**
run it from the campaign's own folder, in a project you trust, so the agent's actions stay scoped to the
work. Stop the loop any time with `Ctrl-C`.

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
- **You want to change something the agent froze** (the metric, the core physics) → those need your
  explicit sign-off; just tell the agent — it won't change them on its own.
- **A generated file still shows `{{PLACEHOLDER}}`** → generation didn't finish cleanly; ask the agent to
  re-run the new-campaign validation step (it has a checker that flags leftover placeholders).

---

*The kit ships two layers of skills, all namespaced `/physkit:<name>`. **General science toolkit**
(usable in any session): `frame-problem`, `verify`, `simulation-design`, `correctness-suite`, `debug`,
`dimensional-analysis`, `derive`, `record-decision`, `cite-check`, `report`. **Campaign layer**:
`new-campaign` (scaffold + interview), `campaign-status` (periodic checkpoint), `handoff` (cold-resume),
`discovery-loop`, `experiment-design`, `model-selection`, and `final-report` (end-of-campaign report).*
