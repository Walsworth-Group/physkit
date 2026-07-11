---
id: systematic-errors
kind: reference
layer: operating
load: on-demand
frozen: false
addresses: [2, 4, 1]
status: active
---

# Systematic errors — hunting the biases that don't average down

A systematic error shifts your central value **without widening your scatter** — so it is invisible to the
one check that catches statistical error (repeat, look at the spread). Scatter you can beat with √N; a
systematic you cannot. In precision measurement the *systematic* budget, not the statistical one, usually
sets the real result — and bounding it is the hard, creative, most important part of the work. The stance
this reference enforces: **assume a systematic is present until you have bounded it.**

Distinct from `attribute-mechanism` (which explains a signature that has already *appeared* in the data):
a systematic often shows no signature at all — it just moves the answer. This is how you go looking for it.

## 1. The mindset — a result is only as good as its systematic budget

The **statistical** error says how precisely you measured *what you measured*; the **systematic** error
says how close *what you measured* is to *what you meant to measure*. A 0.1 % statistical error on a value
biased 2 % by an uncontrolled temperature drift is a 2 % measurement reported as 0.1 % — the classic way a
careful experiment lies. Every candidate systematic ends **bounded** (a line in the error budget) or
**blocking** (the result is not ready); "assumed negligible" counts only when accompanied by the estimate
that shows it is.

## 2. Reversal & null tests — make the signal flip (or vanish) on command

The sharpest tool. Find a knob that, *by the physics*, should **reverse** the signal (a field polarity, a
sequence phase, a sign convention) — or a configuration where the signal must be **zero** (a null). Take
data both ways.

- Under a reversal the **signal** flips but an **additive systematic** (offset, pickup, slow drift) does
  not, so `(A−B)/2` isolates the signal and `(A+B)/2` *measures the systematic*. This is the workhorse of
  precision measurement (co-magnetometry, spin echo, lock-in with reference reversal).
- In a **null** configuration, anything nonzero you measure *is* systematic — a direct read of the floor.
- The dangerous case is a **reversing systematic** (one that flips with the knob, mimicking signal): hunt
  it with a *second, independent* reversal it should not survive.

## 3. Vary the suspect — exaggerate, then extrapolate

You often cannot eliminate a suspected source, but you can **bound** it: deliberately **amplify** it (raise
the drive power, detune, misalign, warm the lab) far beyond nominal, measure how much the result moves, and
extrapolate the slope back to operating conditions. A source whose exaggerated effect stays below target is
bounded and closed; a steep slope is a budget line — or a redesign. **"We couldn't see it" is not a bound;
"we drove it 10× and the result moved < X" is.**

## 4. Auxiliary monitors & co-measurement — measure the nuisance directly

Where a nuisance parameter (field, temperature, phase, power) can drift, **measure it in parallel** — a
witness channel, a co-magnetometer, a monitor photodiode — and either correlate the result against it (if
they correlate, it is your systematic) or co-reference it out. An *unmonitored* drift is indistinguishable
from signal; a *monitored* one becomes a correction carrying its own (propagated) uncertainty.

## 5. Blind analysis — defeat the experimenter, not just the apparatus

The most insidious systematic is the analyst: cuts, corrections, and stopping rules unconsciously tuned
until the answer matches expectation — a previous result, a theory value, a "nice" number. **Blind the
analysis:** add a hidden offset or salt to the quantity of interest, **freeze the cuts, corrections, and
error budget while blind**, and **unblind once**, reporting whatever comes out. Pre-register what you will
do; treat any post-unblinding change as a red flag that must be disclosed. Blinding is one-way — it exists
precisely because good, honest people pull toward the expected value.

## 6. The usual suspects — a starting catalog (have a *written* list)

Not exhaustive; the point is to enumerate for **this** measurement and check each:

- **Drift** (thermal, mechanical, field) — the #1 systematic; interleave A-B-A (`calibration-and-drift.md`).
- **Calibration error** — a wrong scale factor biases everything downstream; trace to a standard.
- **Cross-talk / pickup / ground loops** — one channel leaking into another; test by driving one with the
  other disconnected.
- **Nonlinearity / saturation / dead time** — the response isn't what you assumed at the operating point;
  check linearity across the range.
- **Misalignment / geometry** — a projected component or a frame/handedness error; resolve from an
  *independent* geometric reference (`coordinate-frames.md`).
- **Selection / cut bias** — a cut correlated with the signal sculpts it; check on a signal-free sample
  (`signal-extraction-pitfalls.md`).
- **Back-action** — the measurement perturbs the system (probe-power broadening, measurement-induced
  shifts).
- **Aliasing / timing** — an under-sampled or mistimed acquisition folds a real effect to a fake frequency.

## 7. Fold every systematic into the budget

A hunted systematic ends in exactly one place: a **bounded line** in the error budget
(`uncertainty-and-error-budgets.md`) with its magnitude and *how* it was bounded, or a **blocking issue**
that stops promotion until resolved. A large statistical precision does not license skipping this — it
makes it more urgent (there is nowhere left for a systematic to hide).

## Checklist

- [ ] A **written** list of candidate systematics for THIS measurement (not a generic gesture)?
- [ ] A reversal or null test wherever the physics allows one?
- [ ] Each dominant suspect varied/exaggerated and bounded by a *slope*, not by "couldn't see it"?
- [ ] Drifting nuisances monitored in parallel (or interleaved out)?
- [ ] Analysis blinded where experimenter bias is a risk; cuts frozen before unblinding?
- [ ] Every systematic either a bounded budget line or an explicit blocker?

## Composition

`attribute-mechanism` attributes a *found* systematic to its physical cause ·
`uncertainty-and-error-budgets.md` is where each bounded systematic lands ·
`hardware-in-the-loop.md` §4 (drift/interleaving) and `calibration-and-drift.md` handle the #1
suspect · `signal-extraction-pitfalls.md` covers analysis-chain systematics · `coordinate-frames.md`
covers geometry/misalignment · `noise-and-sensitivity.md` for technical-noise / nonlinearity sources ·
`verify` grades whether the systematic budget is complete before a promotion.

## Sources *(named works cite-checked 2026-07-03; confirm final formatting/DOIs at paper time)*

Field-standard precision-measurement methodology codified into the kit. Reversal/null tests,
co-magnetometry, and "vary-the-suspect" bounding are standard practice (atomic-physics / EDM literature —
cite specific sources at paper time); for blind analysis see **Klein & Roodman**, "Blind Analysis in
Nuclear and Particle Physics" (*Annu. Rev. Nucl. Part. Sci.* **55**, 2005, 141–163).
