---
name: debug
description: >-
  Find and fix a bug in research or numerical code by ladder, not by guessing. Use on a crash, a stack
  trace, a NaN/inf, a result that's wrong or out of its expected range, "this worked before my change",
  "the simulation gives garbage", or any divergence between expected and actual behavior whose cause isn't
  obvious. It climbs a structured ladder — reproduce, reduce to the smallest failing case, check
  units/signs/conventions first, compare to a trusted reference, bisect one change at a time, inspect
  intermediate state, and ask whether you're even computing the right quantity — backed by a catalog of the
  silent bugs that bite physical-simulation code (sign/convention slips, unit mismatches, stale caches,
  non-converged solves, seeds, FFT/indexing conventions). Holds the stance "a crash is a bug, not a bad
  idea." Invokes dimensional-analysis for the units/sign check; hands off to pivoting only once a genuine
  implementation barrier is diagnosed.
---

# debug — climb the ladder, don't guess

A crash is **evidence about the code, not a verdict on the idea** — fix it and re-run before judging the
idea itself. Most research-code bugs are found fastest not by staring or by random edits, but by descending
a fixed ladder that narrows the failure until the cause is cornered. Work it in order; stop as soon as the
cause is found.

## The ladder
1. **Reproduce — deterministically.** Pin down expected vs actual, the exact inputs, and a command that
   triggers the failure every time. Seed every RNG and log the seed; an intermittent bug you can't reproduce
   on demand is a seed/environment lead, not a mystery. Note what changed recently (the top suspect).
   **Exhaust existing evidence first:** logs, recorded state, saved artifacts, OS/event logs often already
   contain the answer — read them before building a reproduction harness, *even when asked for a repro tool
   first* (a workstation crash was diagnosed straight from the event log before any stress test was needed).
2. **Reduce to the smallest failing case.** Shrink inputs, grid size, dimensions, number of steps until the
   failure is as small and fast as it can be. Small reproductions localize bugs; big ones hide them.
3. **Check units, signs, and conventions *first*.** The cheapest and most common class of numerical bug.
   Run a dimensional check (`dimensional-analysis`); confirm sign conventions, coordinate frames, angle
   units, and normalization match between the pieces that meet. Do this *before* anything deeper — it's
   minutes, and it's the #1 culprit.
4. **Compare to a trusted reference.** A known analytic limit, a textbook case, a previous working version,
   or an independent implementation. The first input where your code and the reference diverge points at
   the bug.
5. **Bisect — one change at a time.** Between a known-good and known-bad state (a past commit, a config, a
   code path), change exactly one thing per step and re-test. Don't change two things and guess which
   mattered. (If using git, `git bisect`; otherwise toggle one lever at a time.)
6. **Inspect intermediate state.** Print/plot the values *between* steps — array shapes, ranges, the first
   NaN/inf, matrix conditioning, the residual after each stage. The bug is at the first stage where an
   intermediate goes wrong, not necessarily where it surfaces.
7. **Ask whether you're computing the right quantity at all.** Sometimes the code is correct and the
   *formula, metric, or question* is wrong. Step back and confirm the thing being computed is the thing you
   want — a clean run of the wrong calculation is still wrong.

## The numerical / physics gotcha catalog
The silent bugs that produce a plausible-but-wrong number (worse than a crash, because nothing complains):
- **Sign / convention slip** — the single most common forward-model bug. Sign of a phase, an exponent, a
  Fourier kernel ($e^{+i}$ vs $e^{-i}$), a force; a flipped coordinate or handedness.
- **Units / scale mismatch** — SI vs Gaussian, missing $k_B$/$\hbar$/$4\pi$, nm vs m, a per-area vs total.
- **Angle units** — radians vs degrees into a trig function.
- **FFT / transform conventions** — normalization ($1/N$ placement), frequency ordering (fftshift), real
  vs complex packing.
- **Indexing / off-by-one / boundary conditions** — fence-post errors at grid edges; wrong ghost cells;
  row- vs column-major; 0- vs 1-based.
- **Broadcasting / shape bugs** — a silent shape mismatch that broadcasts into a wrong-but-finite array.
- **Stale cache** — a precomputed operator/dictionary reused after a core change; invalidate on the inputs
  that define it.
- **Non-converged solve reported as a result** — an optimizer/linear solve that didn't converge, or an
  ill-conditioned matrix inverted anyway; a number off a non-converged or non-finite solve is noise.
- **NaN / inf propagation** — a single bad value (a `0/0`, a `log(0)`, an overflow) silently poisoning the
  output; find the *first* one.
- **Seed / nondeterminism** — unset RNG state making results irreproducible across runs/machines.
- **Double-counting / missing factor** — a term added twice, or a Jacobian/volume element dropped.
- **Frozen-infrastructure bug (upstream)** — a persistent *unphysical* symptom (a reversed sign, a
  mirrored/flipped artifact, a structured residual that won't go away) can be a bug in the FROZEN forward
  model / data generator *upstream*, not in the model you're tuning. Re-verify the frozen reference code (a
  sign/convention round-trip against a trusted analytic reference; `correctness-suite`) **before** building
  corrective physics on top of it — chasing the symptom with new terms (tilts, detrending, extra capacity)
  buries the real bug. (A real campaign chased a training-data sign error as a physical "tilt" for ~50
  experiments.)

## Fail loudly so the next bug is cheap
After the fix, leave the code safer than you found it: assert physical invariants and array shapes/units at
boundaries; guard against NaN/inf; check matrix conditioning before solving; confirm optimizers actually
converged (report iterations / final residual). And **promote the bug to a regression check** — add the
minimal failing case to `correctness-suite` so this exact bug can never silently return.

**Tooling you install must be non-intrusive.** A monitor / watcher / auto-start process you add while
debugging must run windowless/headless with no per-iteration side effects (no console pop-ups, no resource
spikes) and be smoke-tested for that *before* you leave it running — debug infrastructure that itself
misbehaves is a new bug (a per-second `nvidia-smi` monitor flashed console windows for hours before anyone
noticed).

## When it isn't a bug
The ladder is for when behavior *diverges from what the code should do*. If you reach the bottom and the
code is correct but the *idea* is capped — it runs fine and simply doesn't work — that's not a debugging
problem; diagnose it and consult `docs/reference/pivoting.md` for the refine↔pivot decision. A genuine,
serious, documented implementation barrier can justify shelving — but only after the ladder rules out a bug.
Don't abandon an idea on the strength of a crash.

## Composition
- **`dimensional-analysis`** — rung 3 (units/signs) and localizing a scale bug.
- **`correctness-suite`** — where the fixed bug becomes a permanent regression gate; a green suite also
  bisects *for* you by telling you which invariant broke.
- **`verify`** — once fixed, re-verify the result; a crash never counts as a refutation of the idea.
- **`pivoting`** — only after the ladder proves it's a capped idea, not a bug.

## Debug report (when worth recording)
For a non-trivial bug, capture it briefly: **expected vs actual**, the **root cause** (the mechanism, not
the symptom), the **fix**, and the **regression check** added. In a campaign this goes in the logbook;
record the *why* of a subtle root cause with `record-decision`.

## Checklist
- [ ] Reproduced deterministically (seed logged); recent changes noted.
- [ ] Reduced to the smallest failing case.
- [ ] Units / signs / conventions checked first.
- [ ] Diverged from a trusted reference at an identified input.
- [ ] Bisected one change at a time to the root cause (mechanism, not symptom).
- [ ] Fix verified; a regression check added to `correctness-suite`; invariants now fail loudly.
