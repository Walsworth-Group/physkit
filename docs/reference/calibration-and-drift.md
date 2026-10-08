---
id: calibration-and-drift
kind: reference
layer: operating
load: on-demand
frozen: false
---

# Calibration & drift — every measurement inherits its calibration's staleness

Calibration ties a readout to a known standard. **Drift** is what makes that tie go stale. On real
hardware, environmental drift is the default: a bias field from permanent magnets wanders with lab
temperature, a laser's power ages, an amplifier's gain creeps. The resonance or scale factor calibrated in
the afternoon is not the one in force overnight. Calibration and drift are measurement science, not
operations alone. `hardware-in-the-loop.md` §4 covers the scheduling; this reference covers the
measurement.

## 1. Trace to a standard

A calibration relates the readout to a reference of known value. Trace that reference to an accepted or SI
standard; failing that, to a stable, independently characterized artifact (a sealed sample, a reference
oscillator).
A calibration error is a **systematic** (`systematic-errors.md`): it biases everything downstream by the
scale error. A scale factor wrong by 1 % puts a 1 % bias on every result, invisible in the scatter. An
uncalibrated number is a readout, not a measurement.

## 2. Characterize the drift before you fight it

A re-calibration policy requires knowing how the calibration ages. Determine the form of the drift:
**white** (jitter around a stable mean), **1/f**, a **linear ramp**, or **stepped** (a jump on a
lab-temperature change or a re-lock). Measure it: repeat the calibration over the relevant timescales and
take the Allan deviation of the reference (`uncertainty-and-error-budgets.md` §5 owns that method). It
gives the drift timescale and whether averaging the calibration helps at all. A stepped drift needs
event-triggered recalibration; a smooth one needs a staleness window (§3).

## 3. The staleness window — validity is bounded by drift ÷ tolerance

A calibration is valid only for a bounded time. Re-calibrate before the drift consumes its allocated line
in the error budget (`uncertainty-and-error-budgets.md`). Set the window from the measured drift rate and
the tolerance, not from habit. Size the calibration to consume a small fraction of its own validity
window: one that eats most of its window starves the science it exists to enable (the **starvation trap**,
`hardware-in-the-loop.md` §4). Stamp each result with its **calibration age at acquisition**, so a
stale-calibration result is identifiable afterward.

## 4. Interleave to separate drift from effect

When drift is present, never take all-A-then-all-B: a slow drift aliases directly into the A−B under
study. Interleave (**A-B-A**) or randomize the order so that drift averages out of the comparison, and
re-measure the reference between compared points. This is the reversal and interleaving logic of
`systematic-errors.md` §2 applied to the calibration axis. In a hardware loop it is a scheduling rule; on
a benchtop measurement it is a sequencing rule.

## 5. Bracket the science with reference measurements

Measure the reference before and after each science point, then interpolate. The drift across the bracket
becomes a correction with a propagated uncertainty instead of an unknown bias. Where a nuisance can be
watched continuously, **co-reference** a parallel witness channel instead: a co-magnetometer or a monitor
detector (`systematic-errors.md` §4).

## 6. Judge a calibration by its own output, never by ambient state

A calibration succeeded only if its own explicit output says so: a fitted reference value within
tolerance, a lock acquired, a residual below threshold. Do not infer success from a downstream flag or
cached state that an earlier success may have left behind. Such an ambient check reads green while the
current calibration fails silently, and it defeats any retry or staleness logic built on it. This is the
success-inferred-from-ambient-state failure catalogued in `debug` and `hardware-in-the-loop.md` §4c.

## 7. Version calibrations — a recalibration is a comparability boundary

A calibration change is a **version boundary**. Tag it with a `calibration_version` alongside
`metric_version` and `data_version`. A result compared across a calibration change is a comparison across
versions, meaningless even when both numbers are individually real; comparability is part of honesty
(`uncertainty-and-error-budgets.md`, integrity doctrine). A recalibration is also a changed premise, which
re-opens a previously settled or ruled-out result. Re-check that result under the new calibration rather
than assuming the old verdict still holds (the re-open trigger in the principles'
*ruled-out-mechanism-is-a-verdict* rule).

## Checklist

- [ ] Reference traced to a standard / characterized artifact (not a floating internal number)?
- [ ] Drift characterized (type + timescale, via the Allan deviation) before setting a policy?
- [ ] Staleness window set from drift ÷ tolerance; calibration small vs its own window; calibration age
      stamped on each result?
- [ ] Comparisons interleaved (A-B-A) / bracketed so drift doesn't alias into the effect?
- [ ] Calibration success judged by its own output, not ambient state?
- [ ] Calibration changes versioned; results not compared across a calibration boundary?

## Composition

`hardware-in-the-loop.md` §4 owns the scheduling and ops (staleness-gated calibration, starvation guard,
pause-sentinel); this doc owns the measurement science · `systematic-errors.md` (calibration error is a
systematic; interleaving) · `uncertainty-and-error-budgets.md` (drift as a budget line; the Allan
deviation) · `noise-and-sensitivity.md` (responsivity is a calibration) · `signal-extraction-pitfalls.md`
(a tuned analysis pipeline embodies calibration; version any change to it).

## Sources

Standard metrology and measurement-science practice. Verified grounding for metrological traceability and
the vocabulary of calibration: the VIM (JCGM 200:2012) and the GUM (JCGM 100:2008). The Allan deviation
(Allan, *Proc. IEEE* **54**, 1966, 221–230) covers drift characterization. Interleaving and bracketing are
standard precision-measurement technique. Confirm every reference's formatting and identifier before the
paper cites it.
