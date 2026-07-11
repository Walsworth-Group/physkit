---
id: hardware-in-the-loop
kind: reference
layer: operating
load: on-demand
frozen: false
addresses: [4, 8, 9]
status: active
---

# Hardware-in-the-loop operation — patterns from a qualified loop

Archetype **E** is fundamentally different from compute-only campaigns: an
"experiment" is a real measurement on a shared instrument — **expensive
(hours, not seconds), often irreversible, drifting, and contended** (humans
use the same rig). These patterns come from qualifying a real autonomous
measurement loop for unattended operation — a **low-field NV-diamond-detected
NMR spectrometer (~1 MHz ¹H Larmor frequency) probing microscale sample
volumes**, autonomously and repeatedly
measuring a known spectroscopic parameter of a sealed calibration standard.
The platform is intrinsically **SNR-limited**: microscale volumes at low
field yield little signal per shot, so a useful acquisition means heavy
averaging over hours — which is precisely what makes every pattern below
load-bearing (a starved night, an unaborted useless acquisition, or a
quarantine miss each burn instrument-hours that averaging cannot buy back).
Every pattern answers a failure that actually happened. (The platform is
described here; the campaign's pulse sequences and scientific objectives are
not — they are reported separately.) Thresholds below are
placeholders by design — set each from your instrument's own tolerances (and,
where possible, from a simulation of the measurement's sensitivity to the
hazard), then record the chosen value in the charter.

## 1. The readiness gate: qualify unattended on a known answer

Before any campaign whose answer you care about, the **loop itself** must
pass a gate — the loop-level analog of experiment-000. Run it on an
engineering sample whose answer is already known, so every check is
checkable, over a window long enough to include the hazards that only appear
at scale: an overnight stretch, a calendar-day boundary, busy AND idle
instrument periods, and at least one deliberate "human takes the rig" event.

Pass criteria are **operational**, judged from the run's own records:
unattended uptime; science acquisitions completed per unit time; fraction of
acquisitions quarantined; zero starvation intervals longer than a set bound;
state surviving a controlled restart; and agreement of the measured value
with the accepted one within a pre-set tolerance (pass/fail, not a number to
tune toward). A gate FAIL names the guard that was missing, the guard is
built, and the full gate is re-run — fix-and-re-gate is the intended flow,
not an embarrassment. Date the gate-pass event; later campaigns cite it.

## 2. The agent–instrument handshake: files, not sockets

Couple the agent loop to the instrument-control software through an
**append-only file protocol** in a watched directory, not a live connection:
the agent writes a work order (a queue file, with a provenance block naming
its origin); the instrument side auto-loads work only from directories
matching the agreed convention, executes, and acknowledges by writing a
sibling *processed* marker. Rejections get a *rejected* marker with the
reason. Extensions follow the same idiom (see §6, §7).

Why files: both sides restart independently without losing state; every
handoff is durably logged for free; a human can inspect, replay, or clear
the channel with a file manager; and there is no connection to time out.
Three hard-won rules — (a) the instrument side must **only** auto-load from
the agreed directories, or a human-authored file left in the tree wedges the
loop forever waiting for an acknowledgment that never comes; (b) a marker is
a **sibling file**, never a rename, so "pending" is computable by glob;
(c) the agent treats a work order it emitted but cannot see acknowledged as
*in flight*, not lost — with a timeout scaled to the acquisition length.

## 3. Instrument sharing: the pause sentinel and graceful yielding

The rig belongs to humans first. Two mechanisms:

- **Pause sentinel.** A single file (e.g. `PAUSE` in an agreed location)
  whose existence idles the loop completely — no work orders, no polling
  churn — until removed. Handing the instrument to a human is `touch`;
  handing it back is `rm`. No re-toggle, no state loss, no negotiation.
- **Graceful busy behavior.** When the instrument is taken without warning
  (auto-load off, manual session), the loop must keep its autonomy budget
  intact: fill the wait with off-instrument work (analysis, critique,
  literature), poll the acknowledgment channel at a calm fixed cadence, and
  resume cleanly — re-running any staleness-sensitive calibration — when the
  rig frees up. The failure modes this prevents (busy-spinning through the
  proposal budget; abandoning an in-flight acquisition) both occurred before
  the guards existed.

## 4. Drift and the calibration–science scheduling trap

Environmental drift is the default on real hardware — on this platform the
bias field comes from a simple pair of SmCo ring magnets, so lab temperature
fluctuations and slight mechanical movement make the field (and with it the
resonance condition) wander continuously. There is no field lock: the
resonance goes stale on a clock, and every calibration inherits that clock. The standard remedy — an auxiliary calibration measurement gating
each science acquisition, with a staleness window — hides a **starvation
trap**: if the calibration takes a large fraction of its own validity window
(or intermittently fails), the loop can spend an entire night re-calibrating
and never measure anything, while every health indicator stays green.

Rules: (a) size the calibration so it consumes a small fraction of its
validity window; (b) add a **starvation guard** — after N consecutive
calibrations with no science acquisition between them, stop recalibrating,
proceed on the best available calibration, and flag the interval (a slightly
degraded acquisition beats a perfect calibration of nothing); (c) judge the
success of a calibration by its own explicit output, never by ambient state
that an earlier success may have left behind (the ambient check masked real
failures and defeated the retry limit).

## 5. Monitors must assert scientific progress, not process health

The starvation night produced the sharpest lesson: **liveness is not
progress.** Every shallow check — process up, rounds completing, no errors,
budget sane — stayed green while the loop did no science for hours. Watch
the quantity you actually care about: *new science acquisitions completed
and accepted per unit time*, with an explicit alarm on its stall. Log every
scheduling decision to an append-only run log as it is made — post-hoc
diagnosis of an unattended system is impossible without the decision trace,
and the one night the trace was missing is the night it was needed.

## 6. Data-quality quarantine at ingest

An acquisition can complete mechanically and still be scientifically void
(drifted out of tolerance mid-run, degraded signal, a known-artifact
regime). Gate at ingest: deterministic checks stamp each acquisition
*ok / caution / quarantined*, quarantined results are excluded from
everything downstream that steers the campaign, and the reason travels with
the record. Two disciplines: thresholds are set **from the measurement's own
tolerance** (simulate the hazard's effect on your observable, then pick the
line), and a quarantine is never silent — it appears in the run records with
its reason, because a quietly-dropped result and a quietly-kept bad result
are the same integrity failure.

## 7. Abort provably-useless acquisitions — deterministically

Hours-long acquisitions make a new failure class possible: the measurement
is *running perfectly* and *cannot possibly be useful* (a parameter choice
that provably aliases; signal absent for N consecutive sub-acquisitions).
Close the diagnosis→action gap with two gates sharing one rule set:

- **Emission gate:** refuse to dispatch a work order whose design is fatally
  flawed, with the reason returned to the proposer (cheapest possible abort).
- **Mid-flight abort:** while waiting, re-assess the running acquisition; on
  a fatal verdict, write an *abort* sentinel next to the work order. The
  instrument side, seeing it, stops cleanly and acknowledges through the
  normal *processed* path — the loop unblocks as if the work completed, and
  partial data ingests under §6.

Constraints that keep this safe: the criteria are **deterministic and
written down** (never a model's judgment call — an abort is an intervention
and must be reproducible); fatal thresholds sit strictly above advisory
warning levels, so merely-suboptimal designs still run and still get
critiqued; past a completion fraction, let it finish (sunk time beats
discarding a nearly-complete record); and one abort request per work order.

## 8. Irreversibility, caps, and budgets

Treat instrument time as the binding budget: cap wall-clock per acquisition
and per session, verify duration estimates against actuals (estimation bugs
compound silently), and enforce hard safety limits (amplitudes, powers,
duty cycles) as **rejection rules at emission** — a safety limit is a
constraint, never a lever. Anything irreversible on the apparatus requires a
human gate, full stop (the kit-wide frozen kernel). Session state — caps,
counters, completed-work ledger — persists across restarts keyed to the
durable file protocol of §2, so a controlled restart is a non-event and an
uncontrolled one is recoverable.

---

*See also:* `ARCHETYPE_CHEATSHEET.md` §E (metric/levers/frozen for this
archetype) · `examples/charter-files/charter_hardware_loop.md` (a filled
charter exercising these patterns) · the `campaign-status` skill (periodic
health checks — extend its checklist with §5's progress assertion for
hardware campaigns).
