# Autonomous Hardware-in-the-Loop Campaign — THE LOOP (archetype E example)

> Illustrative filled charter for archetype **E** (hardware-in-the-loop /
> experimental control), distilled from a real qualified loop: a low-field
> NV-diamond-detected NMR spectrometer probing microscale sample volumes
> (~1 MHz ¹H Larmor frequency; bias
> field from a pair of SmCo ring magnets, so temperature and slight movement
> drift the resonance — no field lock), driven
> through a file-based work-order protocol, autonomously and repeatedly
> measuring a known spectroscopic parameter **P₀** of a sealed calibration
> standard. (The platform is shared here; the campaign's pulse sequences and
> scientific objectives are reported separately.) Numbers marked ⟨…⟩ are
> placeholders — set them from YOUR instrument's tolerances and record the
> choice here. Companion reference: `docs/reference/hardware-in-the-loop.md`.

## Operating stance (applies to EVERY decision in the loop)

- An experiment here is a **real measurement on real, shared hardware**:
  hours long, drifting, contended, and sometimes irreversible. The platform
  is SNR-limited (microscale sample, low field), so precision is bought
  almost entirely with averaging time — instrument time IS the scarce
  resource; treat a wasted acquisition as the costliest failure short of a
  safety violation.
- Humans outrank the loop on the instrument, always. Yield gracefully
  (pause sentinel; calm polling; off-instrument work while waiting) and
  resume without being re-configured.
- Every scheduling decision is logged as it is made (append-only). If it is
  not in the run log, it did not happen — unattended systems are diagnosed
  from their traces or not at all.
- **Never take an unconfirmed irreversible action on the apparatus** (frozen
  kernel). Safety limits are rejection rules, not levers.

## Mission

Maximize the precision of repeated measurements of P₀ per unit instrument
time, unattended, on the calibration standard — and in doing so keep the
loop QUALIFIED: the operational guarantees (uptime, graceful sharing,
starvation-free scheduling, quarantine hygiene) are deliverables equal to
the number itself.

## The ONE metric (FROZEN)

`FOM = 1 / (σ(P) · √T_wall)` — precision per root instrument-hour, computed
by the frozen scorer from each acquisition's fitted P and its uncertainty,
where T_wall is the acquisition's true wall-clock cost (setup + measurement
+ overhead, from the run records — not the nominal sequence time).

### Metric integrity
- The scoring math never changes mid-campaign. What FEEDS it (acquisition
  parameters, averaging, scheduling) is the lever space.
- σ(P) carries statistical AND systematic parts — never score a single
  read; replicate and use the spread (see Rigor).
- Every scoreboard row carries `metric_version` and `data_version` (the
  standard/sample tag). A "current best" is only valid within one
  (metric_version, data_version) pair; comparisons across versions are
  meaningless even when both numbers are individually real.

## The readiness gate (run ONCE, before the loop is trusted unattended)

The loop does not run unattended until it passes gate **G-0** on the known
standard, over a window including: one overnight stretch, one calendar-day
boundary, busy AND idle instrument periods, and one deliberate
"human takes the rig" event. PASS =
- unattended uptime ≥ ⟨target⟩ with zero unhandled stops;
- ≥ ⟨N⟩ science acquisitions completed AND accepted per ⟨interval⟩, with no
  starvation interval longer than ⟨bound⟩ (progress, not liveness — §5 of
  the reference);
- quarantine rate below ⟨bound⟩, every quarantine carrying its reason;
- state surviving one controlled restart;
- the blinded fit of P consistent with the accepted P₀ within its stated
  uncertainty (pass/fail — P is never a number to tune toward).
A FAIL names the missing guard; build the guard; re-run the gate. Date the
pass event in the ledger — campaigns cite it.

## The Experiment Loop

1. **PROPOSE** an acquisition (parameters within the lever space) with an
   **a-priori bound**: expected FOM point + range and the ceiling argument
   (instrument noise floor, coherence/lifetime wall, sampling limits). No
   range, no dispatch.
2. **EMISSION GATE** (deterministic): reject fatally-flawed designs (e.g.
   provably-aliased sampling; duration ≥ ⟨k⟩× the relevant decay budget) and
   safety violations, reasons returned to the proposer.
3. **DISPATCH** as a work-order file (provenance block; agreed directory).
   The instrument side acknowledges by sibling marker when done.
4. **WHILE WAITING**: off-instrument work only; poll calmly; keep the
   staleness-gated calibration current (starvation guard armed: after ⟨N⟩
   consecutive calibrations with no science acquisition between them,
   proceed on best-available calibration and flag it); re-assess the running
   acquisition — on a deterministic fatal verdict below the ⟨fraction⟩
   completion ceiling, write the abort sentinel.
5. **INGEST** through the quarantine gate (ok / caution / quarantined, with
   reasons); score with the frozen metric; append the scoreboard row.
6. **ANALYZE** expected-vs-found: outside your a-priori envelope = bug or
   discovery — decided by evidence. Log, update the journal, repeat.

## The levers

Acquisition timing/sequencing parameters · averaging and integration depth ·
calibration cadence and staleness window · scheduling policy (within the
starvation guard) · quarantine thresholds ONLY in the direction of more
faithful (never merely more lenient), with the change versioned.

## FROZEN / out of scope (NEVER change; NEVER ask for)

The scoring formula · safety limits (amplitude/power/duty caps — rejection
rules) · the apparatus itself (tune settings; do not modify hardware) · the
calibration standard and its sealed accepted value P₀ (blind: the loop never
sees P₀; only the gate referee compares) · the file-protocol conventions
(directories, marker semantics) · the abort criteria (deterministic, written
here; a model's judgment is never an abort reason).

## Independent verification — assume the result is wrong and REFUTE it

Before any promotion: recompute the fit from the raw record on a fresh
path; check the residual STRUCTURE (a trend or input-dependence is a bug or
missed physics, not noise); confirm the acquisition passed quarantine and
its calibration was in-window; grade on the ladder (CONFIRMED / PROVISIONAL
/ QUESTIONABLE-ASSUMPTION / REFUTED / INCONCLUSIVE). Only CONFIRMED
graduates; promotion follows the verdict, never the number alone.

## Rigor: acquisitions are EXPENSIVE here — design before you burn hours

One lever per acquisition unless a co-varying pair is deliberate and stated.
Replicate before concluding (≥ ⟨n⟩ repeats for any claim about a lever;
interleave A-B-A when drift could masquerade as an effect). Prefer the
cheap discriminating measurement over the long confirmatory one. A crash or
wedge is an OPERATIONS bug to fix and re-gate, never a data point against
the physics idea.

## PERSISTENCE (the defining rule of this campaign)

The loop runs until stopped by a human or a cap — never stops itself on a
plateau, a confusing result, or a quiet instrument. Session state (caps,
counters, completed-work ledger) survives restart; an interrupted
acquisition is either cleanly resumed or cleanly aborted through the
protocol — never silently forgotten. When truly stuck (instrument
unreachable past ⟨timeout⟩, repeated gate failures), idle on the pause path
and say so loudly in the log; do not exit.

## Logging

`results/scoreboard.tsv` — one row per acquisition: id, timestamp,
metric_version, data_version, levers, FOM, σ(P) split (stat/sys), T_wall
(estimated AND actual), calibration age at start, quarantine status+reason,
verdict, notes. Run log: append-only, every scheduling decision with its
reason. Journal: the steering view (NEXT pointer + open threads). Gate
events (G-0 pass, aborts, starvation flags, human-takes-rig intervals) are
first-class ledger entries — they are the qualification evidence.
