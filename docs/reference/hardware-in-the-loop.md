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

Archetype **E** differs from compute-only campaigns: an "experiment" is a real
measurement on a shared instrument. Such measurements are expensive (hours, not
seconds), often irreversible, drifting, and contended, because humans use the
same rig. Each pattern below names an operational failure mode of unattended
hardware operation and the guard that prevents it.

The patterns are load-bearing wherever the platform is signal-limited, so that a
useful acquisition means heavy averaging over hours. Under that condition a
starved night, an unaborted useless acquisition, or a missed quarantine each
burn instrument-hours that averaging cannot buy back.

Thresholds below are placeholders by design. Set each from your instrument's own
tolerances and, where possible, from a simulation of the measurement's
sensitivity to the hazard. Record the chosen value in `campaign.md`.

One framing consequence up front: in a qualified loop the operational guarantees
are deliverables equal to the number. Uptime, graceful sharing, starvation-free
scheduling, and quarantine hygiene are part of what the campaign produces, not
infrastructure in service of the science. A precise result from a loop that
starved for hours and cannot say so is not a finished result.

## 0. An example loop, assembled

The sections below are components. This is one worked example of how they
compose into a single iteration, an illustration rather than a required
skeleton. What transfers is the ordering: gate before you spend, quarantine
before you score. The step count does not transfer.

1. **PROPOSE** an acquisition within the lever space, carrying an a-priori
   bound: an expected value, a range, and the ceiling argument that justifies
   it (noise floor, coherence/lifetime wall, sampling limit). No range, no
   dispatch. An unbounded proposal cannot be surprised by its own result, so it
   cannot learn from one.
2. **EMISSION GATE** (§7): deterministically reject fatally-flawed designs and
   safety violations, returning the reason to the proposer. The cheapest abort
   is the one that costs no instrument time.
3. **DISPATCH** the work order with its provenance block (§2); the instrument
   side acknowledges by sibling marker.
4. **WHILE WAITING** (§3, §4, §7): idle cheaply by polling at a calm fixed
   cadence and no more; keep the staleness-gated calibration current with the
   starvation guard armed; re-assess the running acquisition and write the
   abort sentinel on a deterministic fatal verdict below the completion
   ceiling.
5. **INGEST** through the quarantine gate (§6), score with the frozen metric,
   append the scoreboard row (§8).
6. **ANALYZE** expected-vs-found. A result outside the step-1 envelope is a bug
   or a discovery, and evidence settles which one. Log it, update the journal,
   repeat.

## 1. The readiness gate: qualify unattended on a known answer

Before any campaign whose answer matters, the loop itself must pass a gate, the
loop-level analog of experiment-000. Run it on an engineering sample whose
answer is already known, so every check is checkable, over a window long enough
to include the hazards that appear only at scale: an overnight stretch, a
calendar-day boundary, busy and idle instrument periods, and at least one
deliberate "human takes the rig" event.

Pass criteria are operational, judged from the run's own records: unattended
uptime; science acquisitions completed per unit time; fraction of acquisitions
quarantined; zero starvation intervals longer than a set bound; state surviving
a controlled restart; and agreement of the measured value with the accepted one
within a pre-set tolerance. That last criterion is pass/fail, not a number to
tune toward. Enforce it mechanically by blinding: the loop never sees the
accepted value, and only a referee outside the loop compares. The criterion is a
hope while the number is in context and a guarantee once it is not.

A gate FAIL names the guard that was missing, the guard is built, and the full
gate is re-run. Fix-and-re-gate is the intended flow. The same applies
mid-campaign: a crash or a wedge is an **operations** bug to fix and re-gate,
never a data point against the physics idea under test. Date the gate-pass
event; later campaigns cite it.

## 2. The agent–instrument handshake: files, not sockets

Couple the agent loop to the instrument-control software through an
**append-only file protocol** in a watched directory, not a live connection. The
agent writes a work order: a queue file carrying a provenance block that names
its origin. The instrument side auto-loads work only from directories matching
the agreed convention, executes, and acknowledges by writing a sibling
*processed* marker. Rejections get a *rejected* marker with the reason.
Extensions follow the same idiom (see §6, §7). The normative spec of this
handshake — order schema, marker semantics, provenance precondition, and the
conformance checklist a lab program must pass — is
`docs/reference/instrument-contract.md`; the kit ships a generic implementation
(gate, transports, serializers, ingest, operator CLI) under `scripts/hardware/`
with a conforming stub instrument in the deterministic test suite.

Files are the channel because both sides restart independently without losing
state, every handoff is durably logged for free, a human can inspect, replay, or
clear the channel with a file manager, and there is no connection to time out.

Three rules govern the channel. (a) The instrument side must only auto-load from
the agreed directories; otherwise a human-authored file left in the tree wedges
the loop forever, waiting for an acknowledgment that never comes. (b) A marker
is a **sibling file**, never a rename, so "pending" is computable by glob.
(c) The agent treats a work order it emitted but cannot see acknowledged as
*in flight*, not lost, with a timeout scaled to the acquisition length.

## 3. Instrument sharing: the pause sentinel and graceful yielding

The rig belongs to humans first. Two mechanisms:

- **Pause sentinel.** A single file (e.g. `PAUSE` in an agreed location) whose
  existence idles the loop completely, with no work orders and no polling churn,
  until it is removed. Handing the instrument to a human is `touch`; handing it
  back is `rm`. No re-toggle, no state loss, no negotiation.
- **Graceful busy behavior.** When the instrument is taken without warning
  (auto-load off, manual session), the loop must keep its autonomy budget
  intact: idle cheaply by polling the acknowledgment channel at a calm fixed
  cadence, and resume cleanly when the rig frees up, re-running any
  staleness-sensitive calibration. Without these guards the loop busy-spins
  through its proposal budget, or abandons an in-flight acquisition.
- **Do not fill the wait with manufactured work.** Spending the gap on
  off-instrument work (analysis, critique, literature) burns more agent budget
  than it returns: it substitutes an expensive kind of spin for a cheap one, and
  the pattern exists to protect the autonomy budget. Do queued off-instrument
  work because it was queued and is worth its cost, never to fill a gap.

## 4. Drift and the calibration–science scheduling trap

Environmental drift is the default on real hardware. Where the bias field comes
from permanent magnets with no active lock, lab temperature fluctuation and
slight mechanical movement make the field wander continuously, and with it the
resonance condition. The resonance then goes stale on a clock, and every
calibration inherits that clock. The standard remedy is an auxiliary calibration
measurement gating each science acquisition, with a staleness window. That
remedy hides a **starvation trap**: if the calibration takes a large fraction of
its own validity window, or intermittently fails, the loop can spend an entire
night re-calibrating and never measure anything, while every health indicator
stays green.

Rules: (a) size the calibration so it consumes a small fraction of its validity
window; (b) add a **starvation guard** — after N consecutive calibrations with
no science acquisition between them, stop recalibrating, proceed on the best
available calibration, and flag the interval, because a slightly degraded
acquisition beats a perfect calibration of nothing; (c) judge the success of a
calibration by its own explicit output, never by ambient state that an earlier
success may have left behind, because an ambient check masks real failures and
defeats the retry limit.

## 5. Monitors must assert scientific progress, not process health

Liveness is not progress. Shallow checks (process up, rounds completing, no
errors, budget sane) stay green while the loop does no science for hours. Watch
the quantity that matters: new science acquisitions completed and accepted per
unit time, with an explicit alarm on its stall. Log every scheduling decision to
an append-only run log as it is made. Post-hoc diagnosis of an unattended system
is impossible without the decision trace.

## 6. Data-quality quarantine at ingest

An acquisition can complete mechanically and still be scientifically void:
drifted out of tolerance mid-run, degraded signal, a known-artifact regime. Gate
at ingest. Deterministic checks stamp each acquisition *ok / caution /
quarantined*, quarantined results are excluded from everything downstream that
steers the campaign, and the reason travels with the record.

Three disciplines govern the gate. Thresholds are set **from the measurement's
own tolerance**: simulate the hazard's effect on your observable, then pick the
line. A quarantine is never silent; it appears in the run records with its
reason, because a quietly-dropped result and a quietly-kept bad result are the
same integrity failure. Thresholds may be **ratcheted only toward more faithful,
never merely more lenient**, and every change is versioned. A threshold that
loosens because too much is being quarantined is the metric-gaming move in a
data-quality costume.

## 7. Abort provably-useless acquisitions — deterministically

Hours-long acquisitions make a new failure class possible: the measurement is
running correctly and cannot possibly be useful (a parameter choice that
provably aliases; signal absent for N consecutive sub-acquisitions). Close the
diagnosis-to-action gap with two gates sharing one rule set:

- **Emission gate:** refuse to dispatch a work order whose design is fatally
  flawed, with the reason returned to the proposer. This is the cheapest abort.
- **Mid-flight abort:** while waiting, re-assess the running acquisition. On a
  fatal verdict, write an *abort* sentinel next to the work order. The
  instrument side, seeing it, stops cleanly and acknowledges through the normal
  *processed* path, so the loop unblocks as if the work completed, and partial
  data ingests under §6.

Constraints that keep this safe: the criteria are **deterministic and written
down**, never a model's judgment call, because an abort is an intervention and
must be reproducible; fatal thresholds sit strictly above advisory warning
levels, so merely-suboptimal designs still run and still get critiqued; past a
completion fraction, let the acquisition finish, because sunk time beats
discarding a nearly-complete record; and one abort request per work order.

## 8. Irreversibility, caps, and budgets

Treat instrument time as the binding budget. Cap wall-clock per acquisition and
per session. Verify duration estimates against actuals, because estimation bugs
compound silently. Enforce hard safety limits (amplitudes, powers, duty cycles)
as **rejection rules at emission**: a safety limit is a constraint, never a
lever. Anything irreversible on the apparatus requires a human gate, with no
exception (the kit-wide frozen kernel). Session state (caps, counters,
completed-work ledger) persists across restarts, keyed to the durable file
protocol of §2, so a controlled restart is a non-event and an uncontrolled one
is recoverable.

A hardware scoreboard therefore needs columns the compute archetypes do not:
**`T_wall` estimated and actual**, because keeping the pair is what exposes an
estimation bug before it has silently compounded; **calibration age at start**,
so a stale-calibration result stays identifiable long after ingest; and
**quarantine status with its reason**.

---

*See also:* `ARCHETYPE_CHEATSHEET.md` §E (metric/levers/frozen for this
archetype) · the `campaign-status` skill (periodic health checks; extend its
checklist with §5's progress assertion for hardware campaigns).
