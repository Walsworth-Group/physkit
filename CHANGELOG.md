# Changelog — physkit

All notable changes to the kit are recorded here. Format follows
[Keep a Changelog](https://keepachangelog.com/); the kit version lives in `.claude-plugin/plugin.json`.

Dates are UTC. Each entry cites the run/finding that motivated it (the kit's own
`campaign-review → improve-kit` loop) so a future reviewer can trace the "why".

## [Unreleased]

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
