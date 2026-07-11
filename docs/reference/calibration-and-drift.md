---
id: calibration-and-drift
kind: reference
layer: operating
load: on-demand
frozen: false
addresses: [4, 5, 7]
status: active
---

# Calibration & drift — every measurement inherits its calibration's staleness

Calibration is the chain that ties your readout to a known standard; **drift** is the clock that makes that
chain go stale. On real hardware, environmental drift is the default — a bias field from permanent magnets
wanders with lab temperature, a laser's power ages, an amplifier's gain creeps — so the resonance/scale you
calibrated at 2 pm is not the one you have at 2 am. Managing calibration and drift is measurement science,
not just operations; `hardware-in-the-loop.md` §4 handles the *scheduling* of it, this reference handles
the *measurement* of it. (This is where an uncalibrated "readout" becomes a "measurement.")

## 1. Trace to a standard

A calibration relates your readout to a reference of **known value**; that reference should trace to an
accepted / SI standard, or at least to a stable, independently characterized artifact (a sealed sample, a
reference oscillator). A **calibration error is a systematic** (`systematic-errors.md`) that biases
everything downstream by the scale error — a 1 % wrong scale factor is a 1 % bias on every result, invisible
in the scatter. An uncalibrated number is a readout, not a measurement.

## 2. Characterize the drift before you fight it

You cannot set a sensible re-calibration policy without knowing *how* the calibration ages. Is the drift
**white** (jitter around a stable mean), **1/f**, a **linear ramp**, or **stepped** (a jump on a lab-temp
change or a re-lock)? Measure it: repeat the calibration over the relevant timescales and take the **Allan
deviation of the reference** (home: `uncertainty-and-error-budgets.md` §5) — it gives the drift timescale
and whether averaging the calibration even helps. A stepped drift needs event-triggered recalibration; a
smooth one needs a staleness window (§3).

## 3. The staleness window — validity is bounded by drift ÷ tolerance

A calibration is valid only for a bounded time: **re-calibrate before the drift consumes its allocated line
in the error budget** (`uncertainty-and-error-budgets.md`). Set the window from the measured drift rate and
your tolerance, not by habit. And **size the calibration to consume a small fraction of its own validity
window** — a calibration that eats most of its window starves the science it's meant to enable (the
starvation trap, `hardware-in-the-loop.md` §4). Stamp each result with its **calibration age at
acquisition**, so a stale-calibration result is flaggable after the fact.

## 4. Interleave to separate drift from effect

When drift is present, **never** take all-A-then-all-B: a slow drift aliases straight into the A−B you
care about. Interleave (**A-B-A**) or randomize the order so drift averages out of the comparison, and
re-measure the reference *between* compared points. This is the same reversal/interleaving logic as
`systematic-errors.md` §2, applied to the calibration axis. (For a hardware loop, this is a scheduling
rule; for a benchtop measurement, a sequencing one.)

## 5. Bracket the science with reference measurements

Measure the reference just *before and after* each science point and interpolate — the drift across the
bracket becomes a correction with a (propagated) uncertainty instead of an unknown bias. Where a nuisance
can be watched continuously, **co-reference** a parallel witness channel instead (a co-magnetometer, a
monitor detector — `systematic-errors.md` §4).

## 6. Judge a calibration by its own output, never by ambient state

A calibration **succeeded** only if its own explicit output says so — a fitted reference value within
tolerance, a lock acquired, a residual below threshold. Do **not** infer success from a downstream flag or
cached state that an *earlier* success may have left behind: that ambient check reads green while the
current calibration silently fails, and it defeats any retry/staleness logic built on it. (The
"success inferred from ambient state" gotcha — `debug` catalog; `hardware-in-the-loop.md` §4c.)

## 7. Version calibrations — a recalibration is a comparability boundary

A calibration change is a **version boundary**. Tag it (a `calibration_version` alongside `metric_version`
/ `data_version`), because a result compared across a calibration change is a comparison *across versions* —
meaningless even when both numbers are individually real (comparability is honesty,
`uncertainty-and-error-budgets.md` / integrity doctrine). Conversely, a recalibration is exactly the
"premise changed" that **legitimately re-opens** a previously settled or ruled-out result — re-check it
under the new calibration rather than assuming the old verdict still holds (the re-open trigger in the
principles' *ruled-out-mechanism-is-a-verdict* rule).

## Checklist

- [ ] Reference traced to a standard / characterized artifact (not a floating internal number)?
- [ ] Drift *characterized* (type + timescale, via the Allan deviation) before setting a policy?
- [ ] Staleness window set from drift ÷ tolerance; calibration small vs its own window; calibration age
      stamped on each result?
- [ ] Comparisons interleaved (A-B-A) / bracketed so drift doesn't alias into the effect?
- [ ] Calibration success judged by its *own* output, not ambient state?
- [ ] Calibration changes versioned; results not compared across a calibration boundary?

## Composition

`hardware-in-the-loop.md` §4 owns the *scheduling / ops* (staleness-gated calibration, starvation guard,
pause-sentinel); this doc owns the *measurement science* · `systematic-errors.md` (calibration error is a
systematic; interleaving) · `uncertainty-and-error-budgets.md` (drift as a budget line; the Allan
deviation) · `noise-and-sensitivity.md` (responsivity *is* a calibration) · `signal-extraction-pitfalls.md`
(a tuned analysis pipeline embodies calibration — change it only versioned).

## Sources *(cite-checked 2026-07-03; confirm final formatting/DOIs at paper time)*

Standard metrology / measurement-science practice. Verified grounding: **metrological traceability** and the
vocabulary of calibration — the **VIM** (JCGM 200:2012) and the **GUM** (JCGM 100:2008); the **Allan
deviation** (Allan, *Proc. IEEE* **54**, 1966, 221–230) for drift characterization. Interleaving / bracketing
are standard precision-measurement technique.
