---
name: attribute-mechanism
description: >-
  Establish which physical mechanism causes an observed signature before acting on it: one knob per
  candidate, keep what reproduces it, falsify the survivor. Use before saying "that's probably X"
  about a feature in data.
---

# attribute-mechanism — simulate before you attribute

An observed signature plus a plausible story is not an attribution. A wrong attribution is expensive
because it resembles understanding: the wrong quantity gets recalibrated, data gets corrected for an
effect that is not present, or later physics is built on a bug. The rule this skill enforces: never
state the cause of a non-trivial signature without a simulation, or an equivalent quantitative model,
that reproduces the signature and rules the alternatives out.

Two patterns motivate the discipline. Arithmetic that matches the data (alias folding, a harmonic
coincidence) can support an attribution that fails at every physically plausible parameter value, while
a mechanism nobody proposed reproduces the signature. A minimal exact model that sweeps the candidates
against each other separates the two, and converts "does this effect matter here?" from an open
question into a boundary with numbers and stated conditions.

## The method

1. **Pin the signature quantitatively.** Extract the numbers that any explanation must reproduce:
   frequency or period, amplitude (absolute or relative), phase, scaling with a control parameter, onset
   conditions. A mechanism that matches the kind of feature but not its numbers is not an explanation.
   Check the extraction chain first, per `signal-extraction-pitfalls.md`. A signature that is itself an
   artifact has no cause to attribute.
2. **Enumerate candidate mechanisms.** List all of them, including the boring ones (miscalibration,
   drift, analysis artifact) alongside the interesting ones. Write the list down: an unlisted mechanism
   is never tested. `frame-problem`'s effect inventory is the natural source.
3. **Build the minimal model with one knob per mechanism.** Not the production simulator: the smallest
   model that contains only the candidate mechanisms, each behind an explicit, user-controlled knob
   (a detuning, an amplitude error, a phase scheme, a drift rate). Minimality is what makes the sweep
   interpretable. In a model carrying unrelated ingredients the sweep cannot isolate which one produced
   the effect. Exactness over realism: a 2-component exact model beats a 20-component approximate one
   for attribution.
4. **Sweep each knob through plausible values**, and through implausible ones: a mechanism that would
   need a value 10× larger than physically possible is ruled out, which is itself a verdict. Tabulate
   the signature each mechanism produces: its frequency, amplitude, scaling. Only the mechanisms that
   reproduce the observed numbers survive. Combinations count as candidates too.
5. **Falsify the survivor.** Find a limit where the surviving hypothesis makes a sharp, parameter-free
   prediction: a limiting case where the effect must vanish exactly, a scaling it must obey, or a
   control measurement where candidates diverge. Check that prediction in the simulation, and on the
   instrument where that is cheap. An attribution that has survived a falsification attempt is
   CONFIRMED; one that merely fits is PROVISIONAL. Grade it and state the grade (`verify`'s ladder).

## Rules of evidence

- **Reasoning forward from "it looks like X" is inadmissible.** The test runs backward: does X,
  simulated at plausible strength, produce this signature with these numbers?
- **Arithmetic coincidences are not mechanisms.** Alias folding, harmonic matching, and
  order-of-magnitude numerology generate candidate mechanisms. They never confirm one. Every such
  argument must be re-derived by the numerical model before it counts.
- **The null candidate is always on the list**: the signature is an artifact of the extraction or
  analysis chain, not of the physics. Re-extract with an independent method before attributing anything
  subtle.
- **Negative results are verdicts.** "Mechanism X cannot produce this at any plausible strength" is a
  result. Record each ruled-out mechanism, dated, with the sweep that ruled it out, so it is not
  re-litigated.
- **Validate the minimal model itself** against one known limit before trusting its verdicts: the
  hard-pulse, zero-coupling, or static limit where the answer is known analytically. A minimal model
  with a bug attributes signatures to mechanisms that are not present.

## Output

A short attribution record, in the journal, a findings note, or `record-decision` if a decision hangs on
it. It carries the pinned signature, the candidate table (mechanism → simulated signature → verdict),
the surviving mechanism with its falsification test and grade, and what would revisit it. One figure:
the observed signature overlaid with the surviving mechanism's simulation and, ideally, the runner-up
that failed.

## Composition

`frame-problem` supplies the candidate inventory · `dimensional-analysis` bounds each mechanism's
plausible strength before anything is coded · `signal-extraction-pitfalls.md` guards step 1 ·
`debug` takes over if the survivor is "analysis artifact" · `verify` grades the final attribution and
an independent path recomputes it before promotion · `record-decision` when a calibration or hardware
change follows from it.

## Checklist

- [ ] Signature pinned as numbers, not adjectives?
- [ ] Extraction chain checked: could the signature be an artifact?
- [ ] All candidates enumerated in writing, boring ones included?
- [ ] Minimal model, one explicit knob per mechanism, validated in a known limit?
- [ ] Every candidate swept through plausible strengths and tabulated?
- [ ] Survivor falsified in a sharp limit, and graded CONFIRMED only if it passed?
- [ ] Ruled-out mechanisms recorded with their sweeps?
- [ ] No conclusion resting on un-simulated arithmetic?
