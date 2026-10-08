---
id: systematic-errors
kind: reference
layer: operating
load: on-demand
frozen: false
---

# Systematic errors — hunting the biases that don't average down

A systematic error shifts the central value without widening the scatter. The one check that catches
statistical error (repeat, look at the spread) is blind to it. Scatter falls as √N; a systematic does not.
In precision measurement the systematic budget, not the statistical one, usually sets the real result, and
bounding it is the hard part of the work. The stance this reference enforces: assume a systematic is
present until it is bounded.

Distinct from `attribute-mechanism`, which explains a signature that has already appeared in the data: a
systematic often shows no signature at all and only moves the answer. This is how to go looking for it.

## 1. The mindset — a result is only as good as its systematic budget

The **statistical** error says how precisely the measured quantity was measured; the **systematic** error
says how close the measured quantity is to the intended one. A 0.1 % statistical error on a value biased
2 % by an uncontrolled temperature drift is a 2 % measurement reported as 0.1 %. Every candidate systematic
ends **bounded** (a line in the error budget) or **blocking** (the result is not ready); "assumed
negligible" counts only when accompanied by the estimate that shows it is.

## 2. Reversal & null tests — make the signal flip (or vanish) on command

The strongest check available. Find a knob that, by the physics, must reverse the signal (a field polarity,
a sequence phase, a sign convention), or a configuration in which it must be zero (a null). Take data both
ways.

- Under a reversal the signal flips but an additive systematic (offset, pickup, slow drift) does not, so
  `(A−B)/2` isolates the signal and `(A+B)/2` measures the systematic. This is standard practice in
  precision measurement (co-magnetometry, spin echo, lock-in with reference reversal).
- In a null configuration, anything nonzero that is measured is systematic: a direct read of the floor.
- A reversing systematic flips with the knob and mimics signal. Hunt it with a second, independent reversal
  that it should not survive.

## 3. Vary the suspect — exaggerate, then extrapolate

A suspected source that cannot be eliminated can still be bounded. Amplify it (raise the drive power,
detune, misalign, warm the lab) far beyond nominal, measure how much the result moves, and extrapolate the
slope back to operating conditions. A source whose exaggerated effect stays below target is bounded and
closed; a steep slope is a budget line, or a redesign. "We couldn't see it" is not a bound. "It was driven
10× and the result moved < X" is.

## 4. Auxiliary monitors & co-measurement — measure the nuisance directly

Where a nuisance parameter (field, temperature, phase, power) can drift, measure it in parallel: a witness
channel, a co-magnetometer, a monitor photodiode. Then either correlate the result against it (a
correlation identifies the systematic) or co-reference it out. An unmonitored drift is indistinguishable
from signal. A monitored one becomes a correction carrying its own propagated uncertainty.

## 5. Blind analysis — defeat the experimenter, not just the apparatus

The analyst is a source of systematic error: cuts, corrections, and stopping rules get tuned, without
intent, until the answer matches expectation — a previous result, a theory value, a round number. Blind the
analysis: add a hidden offset or salt to the quantity of interest, freeze the cuts, corrections, and error
budget while blind, and unblind once, reporting whatever comes out. Pre-register what will be done. Treat
any post-unblinding change as a red flag that must be disclosed. Blinding is one-way; it cannot be restored
after unblinding.

## 6. The usual suspects — a starting catalog (have a *written* list)

Not exhaustive; enumerate the candidates for this measurement and check each:

- **Drift** (thermal, mechanical, field) — the most common systematic; interleave A-B-A (`calibration-and-drift.md`).
- **Calibration error** — a wrong scale factor biases everything downstream; trace to a standard.
- **Cross-talk / pickup / ground loops** — one channel leaking into another; test by driving one with the
  other disconnected.
- **Nonlinearity / saturation / dead time** — the response is not what was assumed at the operating point;
  check linearity across the range.
- **Misalignment / geometry** — a projected component or a frame/handedness error; resolve from an
  independent geometric reference (`coordinate-frames.md`).
- **Selection / cut bias** — a cut correlated with the signal sculpts it; check on a signal-free sample
  (`signal-extraction-pitfalls.md`).
- **Back-action** — the measurement perturbs the system (probe-power broadening, measurement-induced
  shifts).
- **Aliasing / timing** — an under-sampled or mistimed acquisition folds a real effect to a fake frequency.

## 7. Fold every systematic into the budget

A hunted systematic ends in one of two places: a **bounded line** in the error budget
(`uncertainty-and-error-budgets.md`) recording its magnitude and how it was bounded, or a **blocking issue**
that stops promotion until resolved. High statistical precision does not license skipping this; it makes it
more urgent, because there is nowhere left for a systematic to hide.

## Checklist

- [ ] A written list of candidate systematics for this measurement, not a generic gesture?
- [ ] A reversal or null test wherever the physics allows one?
- [ ] Each dominant suspect varied or exaggerated and bounded by a slope, not by "couldn't see it"?
- [ ] Drifting nuisances monitored in parallel (or interleaved out)?
- [ ] Analysis blinded where experimenter bias is a risk; cuts frozen before unblinding?
- [ ] Every systematic either a bounded budget line or an explicit blocker?

## Composition

`attribute-mechanism` attributes a found systematic to its physical cause ·
`uncertainty-and-error-budgets.md` is where each bounded systematic lands ·
`hardware-in-the-loop.md` §4 (drift/interleaving) and `calibration-and-drift.md` handle the most common
suspect · `signal-extraction-pitfalls.md` covers analysis-chain systematics · `coordinate-frames.md`
covers geometry/misalignment · `noise-and-sensitivity.md` for technical-noise / nonlinearity sources ·
`verify` grades whether the systematic budget is complete before a promotion.

## Sources

Field-standard precision-measurement methodology. Reversal/null tests, co-magnetometry, and
vary-the-suspect bounding are standard practice in the atomic-physics and EDM literature; cite specific
sources when writing this up. For blind analysis see **Klein & Roodman**, "Blind Analysis in Nuclear and
Particle Physics" (*Annu. Rev. Nucl. Part. Sci.* **55**, 2005, 141–163). Confirm formatting and DOIs
against the source before publication.
