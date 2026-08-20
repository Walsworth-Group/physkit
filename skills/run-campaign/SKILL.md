---
name: run-campaign
description: Launch, monitor, and steer a scaffolded autoresearch campaign's supervised loop — the operator's cockpit around the deterministic driver, so nobody has to hand-assemble terminal commands or read raw logs. Use when the user wants to "start/run the campaign", "launch the loop", "restart the loop", asks "is the loop still running", "why did the loop stop/halt", "what is the loop doing right now", or says "tell the loop to …" — process-level questions and actions. It runs the driver's preflight (python scripts/run_campaign.py --preflight) and translates every failure into its fix, launches the loop as a background shell process (--supervise), narrates progress from results/diagnostics/supervise_*.log and results/queue.json, relays user requests into results/inbox/ (the driver injects them verbatim into the next worker/planner prompt), diagnoses halts by kind (operational-shelved vs systemic vs integrity vs ESCALATE), and performs the graceful stop (results/STOP). CONCIERGE FENCE — never an executor: it never runs loop units or experiments, never edits results/ledgers/configs or anything FROZEN; its only writes are results/inbox/ notes and the launch/stop controls. NOT for scaffolding (new-campaign), NOT for progress/substance questions — "where do we stand", plateaus, is-the-best-verified belong to campaign-status (composed on request), NOT for retrospectives (campaign-review) or verifying results (verify).
---

# run-campaign — the loop's cockpit

The loop is executed by the deterministic driver, not by this session. An interactive session that runs
the loop itself accumulates context until the campaign definition falls out of the window, stops re-reading the
docs, stops prematurely in ways prompting does not reliably fix, and uses verification sparingly
unless the gates are enforced in code. Hence the division of labor: the driver executes the loop with
fresh-context workers, and this session is the cockpit around it — launcher, monitor, and intermediary.

**Concierge, never executor.** Your write surface, in full: (1) `results/inbox/` notes; (2) the
launch/stop controls (the `--supervise` process and `results/STOP`); (3) launch-config repairs only
(`configs/loop.json` knobs, `AUTORESEARCH_AGENT_CMD`, a missing tool on PATH), because configs are
user-owned and are not ledgers. Never run a loop unit. Never edit the ledgers (`results/queue.json`,
scoreboard, logbook, journal incl. its Findings) or anything FROZEN on your own judgment. Where a repair to
one of those is needed (a corrupt queue, a resolved ESCALATE), propose the exact edit and apply it only
on the user's explicit go-ahead. The science happens in the driver's workers, and everything you relay
travels through artifacts, so this session holds no scientific state and is disposable by design. While
the driver runs, idle cheaply: watch, relay, answer. Manufactured filler work burns agent budget without
buying the campaign anything.

**Where this runs.** A session opened in the campaign root. The campaign `CLAUDE.md` and hooks bind only
there (`new-campaign` Step 5's fresh-session rule). While the driver's `results/.driver_alive` sentinel
is fresh, the Stop hook stands down for attended sessions like this one; campaign-level loop persistence
is the driver's job.

## When to invoke
- Right after `new-campaign` finishes and the setup work (metric, selftest, baseline) is done. This is
  the handoff's destination.
- "Start / launch / restart the loop", "resume the campaign."
- Process questions mid-run: "is it still running?", "what is it doing?", "why did it stop?"
- "Tell the loop to …" — any steering the user wants relayed without killing the run.
- Not for substance ("where do we stand", plateau, hygiene): compose `campaign-status` for those. It
  reads the ledgers; you read the process.

## Step 0 — learn the campaign
Read the campaign's `CLAUDE.md` and follow its **§Where things live** table to the loop contract this
cockpit operates (`roles/worker.md` §How the loop runs — supervisor mode, and `CLAUDE.md` HARD GATE 5
for how the loop ends; no table means the campaign predates it — read `docs/charter*.md` directly), `configs/loop.json`
(the knobs: timeouts, retries, `driver.*`, user-owned and hot-reloaded by the driver), and the current
state: `results/queue.json` (`next`, `shelved`; note any `kind: "operational"` entries and their
`failures`), the newest `results/diagnostics/supervise_*.log` if one exists (how the last run ended),
and `results/ESCALATE.md` if present. An `ESCALATE.md` means a fork already awaits the user: surface it
first.

## Procedure

### 1. Preflight
Run the driver's own checks and translate them; never reimplement them. Use the campaign's python, the
same command the `.claude/settings.json` hooks use (`py -3` on Windows, for example):
```
python scripts/run_campaign.py --preflight
```
Every failure line names its fix. Apply the launch-config ones yourself (an unfilled `loop.json` knob, a
stale `AUTORESEARCH_AGENT_CMD`, an agent CLI not on PATH). Surface substantive ones to the user: an
unimplemented metric is setup work, so point back at the `new-campaign` handoff list, and a missing
`results/`/`campaign.md`/`roles/worker.md`/`scoreboard.tsv` (the names the preflight itself reports — quote what it
printed, don't translate it) means you are not in a scaffolded campaign root at all. Fix the
directory; do not fabricate the tree. `--smoke` adds one real spawn when the user wants the full dress
rehearsal, at the cost of a model call. Green preflight → launch.

### 2. Launch
Start the driver as a background shell process from the campaign root and note its log file:
```
python scripts/run_campaign.py --supervise
```
This is an OS process you background in your shell, not a background subagent. The worker role's
never-background-a-solve rule covers solver and agent work losing its heartbeat; the driver is the
process that watches heartbeats, and it keeps its own decision trace at
`results/diagnostics/supervise_<ts>.log`. Confirm liveness (the launch banner and `results/.driver_alive`
appearing), tell the user the loop is running and where the log lives, then go quiet.

### 3. Monitor
On request, or at a periodic check-in, read; never re-derive:
- the driver log tail: current unit, rendered worker feed, planner triggers, accepted-unit count, and
  the `verifier[...]` lines — after each accepted unit or completed block the driver spawns the
  verification agent and stamps the scoreboard from its verdicts;
- `results/queue.json`: `accepted_units`, `last_accept_utc`, what's queued/shelved and why, and
  `pending_verification` (accepted experiments whose verdicts the driver is still obtaining — a
  growing list means verification is failing while the loop runs; surface it).
Report process facts in plain language ("worker on exp007, third unit this run; one unit shelved
operational overnight, spawn timeout, planner will review"). You own the progress alarm. CORE requires
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
