---
name: attribute-mechanism
description: >-
  Establish WHICH physical mechanism causes an observed signature before acting on the attribution. Reach
  for it whenever a real feature has appeared in data (a modulation, a drift, an offset, an asymmetry, an
  extra decay) and someone is about to say "that's probably X" — detuning, a pulse error, temperature, a
  ground loop, relaxation, motion. The discipline: enumerate the candidate mechanisms, build a MINIMAL
  simulation with one knob per mechanism, sweep each knob through plausible values, and keep only the
  mechanisms that actually REPRODUCE the signature — then falsify the survivor with a limiting case it
  must pass. Distinct from simulation-design (building production sims right), debug (broken code), and
  verify (checking a result): this attributes an observed REAL effect to its cause. A wrong attribution
  silently corrupts everything downstream — recalibrations, "corrections", discarded data, papers.
---

# attribute-mechanism — simulate before you attribute

An observed signature plus a plausible story is not an attribution. Plausible-but-wrong attributions are
among the most expensive failures in experimental work because they *feel* like understanding: the team
recalibrates the wrong thing, "corrects" data for an effect that isn't there, or builds physics on a bug.
The rule this skill enforces: **never state the cause of a non-trivial signature without a simulation (or
equivalent quantitative model) that reproduces it — and rules the alternatives out.**

Two real, dated failures/wins motivate the discipline:

- A periodic modulation in an echo train was confidently attributed to off-resonance drive, complete with
  alias-folding arithmetic that seemed to match the period. A five-minute two-level simulation showed
  off-resonance **could not** produce the signature at any plausible detuning — while a ~3% pulse-amplitude
  miscalibration reproduced it exactly. The attribution flipped; so did the fix.
- A question about whether pulse-to-pulse carrier phase coherence mattered in a multi-pulse sequence was
  settled the same afternoon it was asked: an exact minimal simulation swept phase schemes × pulse errors,
  and a hard-pulse limiting case (where theory demands exact invariance) validated the model to 1e-7 —
  turning a hand-wave into a quantified boundary ("irrelevant for calibrated pulses, catastrophic beyond
  10% miscalibration").

## The method

1. **Pin the signature quantitatively.** Extract the numbers that any explanation must reproduce:
   frequency/period, amplitude (absolute or relative), phase, scaling with a control parameter, onset
   conditions. A mechanism that matches the *kind* of feature but not its *numbers* is not an explanation.
   (Check the extraction itself first — see `signal-extraction-pitfalls.md`; a fake signature attributes
   to nothing.)
2. **Enumerate candidate mechanisms** — all of them, including the boring ones (miscalibration, drift,
   analysis artifact) alongside the interesting ones. Write the list down; the one you didn't list is the
   one you'll miss. `frame-problem`'s effect inventory is the natural source.
3. **Build the MINIMAL model with one knob per mechanism.** Not the production simulator: the smallest
   model that contains *only* the candidate mechanisms, each behind an explicit, user-controlled knob
   (a detuning, an amplitude error, a phase scheme, a drift rate). Minimality is what makes the sweep
   interpretable — in a kitchen-sink model you cannot tell which ingredient produced the effect. Exactness
   over realism: a 2-component exact model beats a 20-component approximate one for attribution.
4. **Sweep each knob through plausible values** (and implausible ones — knowing a mechanism would need a
   10× larger value than physically possible is itself a verdict). Tabulate the signature each mechanism
   produces: its frequency, amplitude, scaling. **Only the mechanisms that reproduce the observed numbers
   survive.** Combinations count as candidates too.
5. **Falsify the survivor.** Find a limit where the surviving hypothesis makes a sharp, parameter-free
   prediction — a limiting case where the effect must vanish exactly, a scaling it must obey, a control
   measurement where candidates diverge — and check it (in the sim, and where cheap, on the instrument).
   An attribution that has survived a falsification attempt is CONFIRMED; one that merely fits is
   PROVISIONAL. Grade it and say so (`verify`'s ladder).

## Rules of evidence

- **Reasoning forward from "it looks like X" is inadmissible.** The test is always backward: does X,
  simulated at plausible strength, produce THIS signature with THESE numbers?
- **Arithmetic coincidences are not mechanisms.** Alias-folding, harmonic-matching, and
  order-of-magnitude numerology generate candidate mechanisms; they never confirm one. Every such
  argument must be re-derived by the numerical model before it counts.
- **The null candidate is always on the list**: the signature is an artifact of the extraction/analysis
  chain, not of the physics. Re-extract with an independent method before attributing anything subtle.
- **Negative results are verdicts.** "Mechanism X cannot produce this at any plausible strength" is often
  the most valuable output — record it (a ruled-out mechanism, dated, with the sweep that ruled it out)
  so the team never re-litigates it.
- **Validate the minimal model itself** with one known limit before trusting its verdicts (the hard-pulse
  / zero-coupling / static limit where the answer is known analytically). A minimal model with a bug
  attributes signatures to phantoms.

## Output

A short attribution record (in the journal, a findings note, or `record-decision` if a decision hangs on
it): the pinned signature, the candidate table (mechanism → simulated signature → verdict), the surviving
mechanism with its falsification test and grade, and what would revisit it. One figure — observed
signature overlaid with the surviving mechanism's simulation and, ideally, the runner-up that failed.

## Composition

`frame-problem` supplies the candidate inventory · `dimensional-analysis` bounds each mechanism's
plausible strength before anything is coded · `signal-extraction-pitfalls.md` guards step 1 ·
`debug` takes over if the survivor is "analysis artifact" · `verify` grades the final attribution and
an independent path recomputes it before promotion · `record-decision` when a calibration or hardware
change follows from it.

## Checklist

- [ ] Signature pinned as numbers (not adjectives)?
- [ ] Extraction chain checked — could the signature be fake?
- [ ] All candidates enumerated in writing, boring ones included?
- [ ] Minimal model, one explicit knob per mechanism, validated in a known limit?
- [ ] Every candidate swept through plausible strengths and tabulated?
- [ ] Survivor falsified in a sharp limit — and graded CONFIRMED only if it passed?
- [ ] Ruled-out mechanisms recorded with their sweeps?
- [ ] No conclusion resting on un-simulated arithmetic?
