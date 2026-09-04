---
name: run-campaign
description: >-
  Launch, monitor, and steer a scaffolded autoresearch campaign's supervised loop. Use for requests to
  start, run, restart, stop, or inspect the loop, and for process-level questions about what it is doing
  or why it halted. Run the deterministic driver's preflight, launch its supervisor, narrate progress
  from diagnostics and queue state, relay user notes through the inbox, diagnose halt categories, and
  perform graceful stop control. This is a concierge, never an experiment executor: it does not run loop
  units itself or edit results, ledgers, configs, or FROZEN files. Not for scaffolding, substantive
  campaign progress or plateau review (campaign-status), retrospectives, or result verification.
---

# run-campaign — the loop's cockpit

The loop is executed by the deterministic driver, not by this session. An interactive session that runs
the loop itself accumulates context until the campaign definition falls out of the window, stops re-reading the
docs, stops prematurely in ways prompting does not reliably fix, and uses verification sparingly
unless the gates are enforced in code. Hence the division of labor: the driver executes the loop with
fresh-context workers, and this session is the cockpit around it — launcher, monitor, and intermediary.

**Concierge, never executor.** Your write surface, in full: (1) `results/inbox/` notes; (2) the
launch/stop controls (the `--supervise` process and `results/STOP`); (3) launch-config repairs only
(`configs/loop.json` knobs, the harness executable override, a missing tool on PATH), because configs are
user-owned and are not ledgers. Never run a loop unit. Never edit the ledgers (`results/queue.json`,
scoreboard, logbook, journal incl. its Findings) or anything FROZEN on your own judgment. Where a repair to
one of those is needed (a corrupt queue, a resolved ESCALATE), propose the exact edit and apply it only
on the user's explicit go-ahead. The science happens in the driver's workers, and everything you relay
travels through artifacts, so this session holds no scientific state and is disposable by design. While
the driver runs, idle cheaply: watch, relay, answer. Manufactured filler work burns agent budget without
buying the campaign anything. Two metric-epoch writes are the user's decisions relayed through you, on
their explicit word only: setting a pending epoch's `status` in `configs/loop.json`
`campaign.metric_epochs` (`ratified` / `rolled-back`), and moving the `campaign.metric_revision` dial
(`python scripts/run_campaign.py --set-metric-revision <mode>`). You never open an epoch yourself and
never judge one; `roles/worker.md` §Metric epochs is the loop's procedure, not yours.

**Where this runs.** A session opened in the campaign root. The campaign's managed instruction file
(`CLAUDE.md` in Claude, `AGENTS.md` in Codex) and hooks bind only there (`new-campaign` Step 5's
fresh-session rule). While the driver's `results/.driver_alive` sentinel
is fresh, the Stop hook stands down for attended sessions like this one; campaign-level loop persistence
is the driver's job.

## When to invoke
- Right after `new-campaign` finishes — it hands off preflight-green (metric implemented, selftest
  passing, exp 000 queued as the first unit). This is the handoff's destination.
- "Start / launch / restart the loop", "resume the campaign."
- Process questions mid-run: "is it still running?", "what is it doing?", "why did it stop?"
- "Tell the loop to …" — any steering the user wants relayed without killing the run.
- Not for substance ("where do we stand", plateau, hygiene): compose `campaign-status` for those. It
  reads the ledgers; you read the process.

## Step 0 — learn the campaign
Read the active harness's instruction twin and follow its **§Where things live** table to the loop contract this
cockpit operates (`roles/worker.md` §How the loop runs — supervisor mode, and its HARD GATE 5
for how the loop ends; no table means the campaign predates it — read `docs/charter*.md` directly), `configs/loop.json`
(the knobs: timeouts, retries, `driver.*`, user-owned and hot-reloaded by the driver), and the current
state: `results/queue.json` (`next`, `shelved`; note any `kind: "operational"` entries and their
`failures`), the newest `results/diagnostics/supervise_*.log` if one exists (how the last run ended),
and `results/ESCALATE.md` if present. An `ESCALATE.md` means a fork already awaits the user: surface it
first.

## Procedure

### 0.5 Confirm launch settings
Before every stopped-campaign start, restart, or resume, show the user the task's active harness and the
campaign's selected backend plus the planner and worker model/effort settings in `configs/loop.json`.
Render a blank setting as **default/inherited**. If this harness exposes trustworthy live concierge model
or effort metadata in the current session, compare it; otherwise say the live value is unavailable and
ask the user to confirm it from the app's model/effort picker. Never guess from a stale session-start value
or edit the app's own setting. A difference is informational, not a preflight failure: campaign roles may
intentionally differ from the concierge.

Offer four choices: keep the campaign settings; copy the concierge model/effort to both roles; choose
planner and worker separately; or blank the role overrides so they inherit harness defaults. Change only
the active harness's fields (`model` + `claude_effort`, or `codex_model` +
`codex_reasoning_effort`), only with the user's explicit approval, and only while no supervisor is running.
Then run preflight, whose read-only launch-settings line is the final confirmation of what will spawn.

### 1. Preflight
Run the driver's own checks and translate them; never reimplement them. Select the backend matching this
task (`codex` in Codex, `claude` in Claude), and use the campaign's python:
```
python scripts/run_campaign.py --preflight --backend <codex|claude>
```
Every failure line names its fix. Apply the launch-config ones yourself (an unfilled `loop.json` knob, a
stale backend/model setting, `AUTORESEARCH_AGENT_CMD` for Claude/custom, or
`AUTORESEARCH_CODEX_EXE` when a Windows Codex alias cannot be probed). Surface substantive ones to the user: an
unimplemented metric or hook means scaffolding stopped short of its preflight-green gate (or the tree
was imported/hand-built) — point back at the `new-campaign` handoff list, and a missing
`results/`/`campaign.md`/`roles/worker.md`/`scoreboard.tsv` (the names the preflight itself reports — quote what it
printed, don't translate it) means you are not in a scaffolded campaign root at all. Fix the
directory; do not fabricate the tree. `--smoke` adds one real spawn when the user wants the full dress
rehearsal, at the cost of a model call. Green preflight → launch. Preflight also names the campaign's
metric epoch and, when `campaign.metric_revision` is not `cautious`, prints a NOTICE that the loop may
revise the metric without asking; read that line to the user before launching.

**A mechanics-class preflight failure** — the metric selftest red, a scorer or hook still a stub, a
wiring error the first experiment would trip — is handed back as above when the dial is `cautious`. When
it is `autonomous`, spawn a bounded repair agent instead: a fresh session in the campaign root, told to
follow `roles/worker.md` §Metric epochs as a `mechanics` fix (declare the epoch, fix, selftest and suite
green), then re-run preflight; a substantive failure (an unimplemented specification, data only the user
can stage) still hands back. You launch and narrate; you do not edit the scorer.

### 2. Launch
Start the driver as a background shell process from the campaign root and note its log file:
```
python scripts/run_campaign.py --supervise --backend <codex|claude>
```
Codex uses `codex exec` with a workspace-write sandbox, UTF-8 prompt stdin, and JSONL events; Claude keeps
its established `claude -p` command. Each role has independent harness settings in `configs/loop.json`:
Claude reads `model` + `claude_effort`, while Codex reads `codex_model` + `codex_reasoning_effort`; a blank
value inherits that harness's configured default. With `verify.strategy: auto`, Codex uses a fresh
driver-spawned thread at the worker's Codex model and effort as the refuter and validates its verdict schema,
evidence subject, and recorded thread identity; Claude keeps its established nested-refuter flow at the
planner's Claude model and effort. Stop the current supervisor before changing harness; the process-held lock
rejects an overlapping launch.
This is an OS process you background in your shell, not a background subagent. The worker role's
never-background-a-solve rule covers solver and agent work losing its heartbeat; the driver is the
process that watches heartbeats, and it keeps its own decision trace at
`results/diagnostics/supervise_<ts>.log`. Confirm liveness (the launch banner and `results/.driver_alive`
appearing), tell the user the loop is running and where the log lives, then go quiet.

New or migrated campaigns whose runner includes `scripts/supervisor_lock.py` hold
`results/.supervisor.lock` for the whole supervised run. A second launch refuses before preflight,
logging, queue access, or spend and prints best-effort owner metadata. The file is persistent diagnostic
metadata: its existence alone does not mean the lock is held, so never delete it to recover or switch.
Stop the first supervisor and wait for it to exit, then launch the other harness normally. Legacy campaigns
without that helper have no automatic exclusivity: stop and confirm the current supervisor has exited before
switching, or migrate the campaign first. A hard supervisor crash with a possibly surviving detached child is
not proven safe by kernel-lock release; inspect and stop that child before relaunching.

### 3. Monitor
On request, or at a periodic check-in, read; never re-derive:
- the driver log tail: current unit, rendered worker feed, planner triggers, accepted-unit count, the
  `verification owed for …` / `no independent check owed …` lines (what the campaign's verification
  preset asked for each accepted unit, and the depth — review or re-execution — the driver decided from
  its measured cost), the `verifier[...]` lines that follow, the `suite demotions changed` line when a
  slow check is metered out of the every-set, and the `capstone` spawn at STOP or an empty queue (the
  claim audit at the preset's level);
- `results/queue.json`: `accepted_units`, `last_accept_utc`, what's queued/shelved and why, and
  `pending_verification` (accepted experiments whose verdicts the driver is still obtaining — a
  growing list means verification is failing while the loop runs; surface it).
Report process facts in plain language ("worker on exp007, third unit this run; one unit shelved
operational overnight, spawn timeout, planner will review"). A `[supervise] campaign.metric_epochs:` or
`campaign.metric_version:` line is a metric epoch opening or a ratification — relay it as such, with
the epoch's kind and direction. You own the progress alarm. CORE requires
monitoring progress rather than liveness, because a loop can be alive, logging, and doing zero science:
if `accepted_units` sits flat across real wall-clock (`configs/loop.json` §plateau sets the scale), raise
it unprompted, since no other session is watching. For anything about the science (is the best real, has
progress plateaued for a physics reason, journal hygiene) invoke `campaign-status`. Do not answer
substance from a process log.

### 4. Relay (the inbox)
A user request for the loop becomes a note in `results/inbox/` (any `.md` filename):
- Steering, corrections, context, priorities → inbox (create the folder if the campaign lacks it).
  The driver injects it verbatim into the next worker/planner prompt and archives it; workers must
  acknowledge it in the journal. Check that they did, and tell the user when their note has been picked
  up.
- Write the user's intent, attributed and dated. Do not editorialize. One note per topic.
- Escalation-worthy content is different. If the user is answering an ESCALATE fork, relay their
  decision; on their explicit instruction, record it and delete `results/ESCALATE.md`, then relaunch.
  If the user wants the loop stopped, that is Step 6, not a note.

### 5. Halts
The driver halts loudly and says why. Classify from the log tail and the queue before proposing anything:
- **Operational shelvings** (`kind: "operational"`) did not halt the loop. Mention them; the planner
  handles revival.
- **SYSTEMIC halt** (N consecutive operational failures): an environment problem. Check the agent CLI,
  credentials, disk, and the shelved units' `failures` records; fix, then relaunch on the user's
  go-ahead.
- **Disk-floor halt**: free space fell below this campaign's floor, so the driver stopped before a unit
  could write half a save-set. Report how much is free and what one unit costs (`configs/loop.json`
  `unit_cost.typical_disk_mb`), then offer the options: free space, move the tree to a larger volume, or
  apply the retention plan in `roles/worker.md`. That plan drops regenerable bulk artifacts,
  never the permanent record, and only with the user's confirmation.
- **Metric-revision proposal**: `ESCALATE.md` carrying a `## METRIC-REVISION PROPOSAL` block (the loop
  believes the FROZEN metric is wrong and the dial is `cautious`). Surface it verbatim — the claim, the
  verdict artifact, the proposed specification and scorer change, its kind and direction (an `easier`
  ruler is the one to scrutinize), and the re-baseline cost. The user decides. On their explicit go:
  bump `campaign.metric_version`, add the `campaign.metric_epochs` entry exactly as proposed with
  `status: "pending"` and `opened_by: "user"`, delete `ESCALATE.md`, and relaunch — the relaunched
  worker enacts the specification and scorer change under the declared epoch *before its first unit*
  (`roles/worker.md` §Metric epochs says so; the runner binds an epoch's scorer hash on the first
  experiment, so a unit run first would bind the new epoch to the old scorer) and queues the
  re-baseline. On a decline: note it in the JOURNAL, delete the file, relaunch. A pending epoch opened in `autonomous` mode reaches you
  the same way, later: `campaign-status` lists pending epochs, and the user ratifies through you.
- **Integrity halt**: `ESCALATE.md` (surface the fork verbatim; this is the user's decision, not
  yours), corrupt `queue.json` (diagnose, propose the exact JSON repair, apply it only on the user's
  go-ahead, and never delete it, since it is the loop's only memory), queue empty after a planner pass
  (a stopping decision for the user, since the campaign may be done or may need new directions; suggest
  `campaign-status` for the evidence).
- A driver that died with no halt message (crash, reboot): the log just stops, `.driver_alive` goes
  stale, and the Stop hook re-arms. Relaunch is safe; the unit at the queue head resumes.

### 6. Stop
Graceful stop: create `results/STOP`. The driver honours it at the campaign level, and the current unit
finishes and logs first. Confirm the driver exited, then remind the user that deleting the file re-arms
the loop for the next launch. `Ctrl-C`, or killing the process, is the immediate stop: the current unit
is killed, it stays at the queue head, and relaunch resumes it. Stopping is the user's call. Never stop
the loop on your own judgment; if you believe it should stop, say so and ask.

## Notes
- This skill runs no experiments and interprets no results. A mid-tier model is sufficient for watching
  and relaying. Halt classification and ESCALATE surfacing are judgment calls; do not push those to the
  cheapest tier.
- If the campaign's Stop hook blocks your end-of-turn (it stands down while the driver runs, but the
  campaign is armed and the driver may be down: before launch, after a halt, after a crash), do not
  start executing loop units. The remedy is the block message's own first option: launch or relaunch
  the driver. If the user's intent is to stop, make the stop official (`results/STOP`) instead.
- Composition: `campaign-status` for substance (health, plateau, hygiene, consolidation);
  `campaign-review` after the loop is finished; `verify` is the workers' tool, not yours.
- If this session dies, nothing is lost. The driver does not notice, and any fresh session in the
  campaign root can pick the cockpit back up with this skill.
