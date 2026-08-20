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

A crash is evidence about the code, not a verdict on the idea. Fix it and re-run before judging the idea
itself. Most research-code bugs are found fastest by descending a fixed ladder that narrows the failure
until the cause is cornered, rather than by inspection or trial edits. Work it in order; stop as soon as the
cause is found.

## The ladder
1. **Reproduce — deterministically.** Pin down expected vs actual, the exact inputs, and a command that
   triggers the failure every time. Seed every RNG and log the seed; an intermittent bug that will not
   reproduce on demand is a seed or environment lead, not a mystery. Note what changed recently (the top
   suspect). Exhaust existing evidence first: logs, recorded state, saved artifacts, and OS/event logs
   often already contain the answer. Read them before building a reproduction harness, including when
   the request was for a reproduction tool first.
2. **Reduce to the smallest failing case.** Shrink inputs, grid size, dimensions, number of steps until
   the failure is as small and fast as it can be. Small reproductions localize bugs; big ones hide them.
3. **Check units, signs, and conventions first.** The cheapest and most common class of numerical
   bug. Run a dimensional check (`dimensional-analysis`); confirm that sign conventions, coordinate frames,
   angle units, and normalization match between the pieces that meet. Do this before anything deeper: it
   takes minutes.
4. **Compare to a trusted reference.** A known analytic limit, a textbook case, a previous working version,
   or an independent implementation. The first input where the code and the reference diverge points at
   the bug.
   **When the reference is someone else's published result, a disagreement is a three-way fork, not proof
   your code is wrong** — diagnose *which* before fixing anything:
   (a) **your reproduction is wrong** — a real bug in the port or pipeline (units, channel order, a
   mis-wired layer): debug it and re-run;
   (b) **the published result has a quirk or bug your faithful reproduction correctly does NOT inherit** —
   here the discrepancy is a *finding*: investigate the mechanism against the authoritative artifact (run
   the released weights rather than trusting the printed table), record it, and decide deliberately whether
   to match the original's behaviour or keep the corrected one;
   (c) **the spec you were handed is wrong** — a load-bearing fact came from a low-authority source that
   the authoritative artifact contradicts: re-pin it and re-run.
   **Never tune the reproduction toward the target number blind, and never reverse-engineer the original's
   bug just to hit its printed value** — that is goalpost-matching, not reproduction. The honest move when a
   faithful repro disagrees with a paper is to find out *why*.
5. **Bisect — one change at a time.** Between a known-good and a known-bad state (a past commit, a config, a
   code path), change exactly one thing per step and re-test. Do not change two things and guess which
   mattered. With git, use `git bisect`; otherwise toggle one lever at a time.
6. **Inspect intermediate state.** Print or plot the values between steps: array shapes, ranges, the first
   NaN/inf, matrix conditioning, the residual after each stage. The bug is at the first stage where an
   intermediate goes wrong, not necessarily where it surfaces.
7. **Ask whether the right quantity is being computed at all.** Sometimes the code is correct and the
   formula, metric, or question is wrong. Step back and confirm the thing being computed is the thing
   required; a clean run of the wrong calculation is still wrong.

## The numerical / physics gotcha catalog
The silent bugs that produce a plausible-but-wrong number, worse than a crash because nothing complains:
- **Sign / convention slip** — the most common forward-model bug. Sign of a phase, an exponent, a
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
- **Non-converged solve reported as a result** — an optimizer or linear solve that did not converge, or an
  ill-conditioned matrix inverted anyway; a number off a non-converged or non-finite solve is noise.
- **A silent failure whose output imitates the effect being looked for** — the cousin of the
  above, and the one no generic check catches. The run returns exit 0, no NaNs, and an ordinary convergence
  metric, while its output has collapsed into something that reads like the sought signature (a
  solver that scrambles a stiff configuration to $|m| \approx 0$ looks like the moment reduction under
  study). Nothing is numerically wrong, so every health check passes. The gate has to be a **physical
  magnitude floor calibrated on a validated corpus**: the range the quantity actually takes on trusted runs,
  asserted on every run rather than the solver's own status. A result that is both dramatic and
  convenient is checked against this failure first.
- **NaN / inf propagation** — a single bad value (a `0/0`, a `log(0)`, an overflow) silently poisoning the
  output; find the first one.
- **Seed / nondeterminism** — unset RNG state making results irreproducible across runs/machines.
- **Double-counting / missing factor** — a term added twice, or a Jacobian/volume element dropped.
- **Self-referential nuisance-parameter anchoring** — a calibration/registration/background parameter meant to
  track independent ground truth instead gets re-solved against its own previous estimate (e.g. a per-step
  registration fit initialized from, and implicitly pulled toward, the prior step's answer rather than the raw
  data). The fit converges and looks stable, but around its own accumulated drift rather than the truth,
  and it walks slowly with no error signal to catch it. Check: does resetting the parameter's
  prior value between steps change the answer? If yes, it was anchoring to itself, not the data
  (`simulation-design` §assumptions).
- **Frozen-infrastructure bug (upstream)** — a persistent unphysical symptom (a reversed sign, a
  mirrored or flipped artifact, a structured residual that will not go away) can be a bug in the FROZEN
  forward model or data generator upstream, not in the model being tuned. Re-verify the frozen reference
  code before building corrective physics on top of it: run a sign/convention round-trip against a trusted
  analytic reference (`correctness-suite`). Chasing the symptom with new terms (tilts, detrending, extra
  capacity) buries the real bug and can absorb a long series of experiments before the upstream cause is
  found.

- **Latent geometry assumption armed by a calibration change** — a shared buffer/window/grid sized to
  one consumer silently truncates or clips another the day a calibration changes the first (e.g. a shared
  pulse window sized to pulse A clips the longer pulse B after A is shortened, while metadata keeps
  recording B's intended length). Size shared structures to the max of their consumers, and regression-test
  extents (what actually got written or played), not just parameters.
- **Success inferred from ambient state** — judging a step's success by state it should have changed
  (a cache is fresh, a file exists, a flag is set) instead of by the step's own explicit output or exit
  signal. A previous success, or an unrelated writer, leaves the ambient check green while the step fails
  every time, and disables the retry/latch logic built on it.
- **Path-dependent state reset** — a counter/breaker/flag reset on the common code path but not on the
  alternate path that reaches the same outcome (manual stop vs normal completion; error path vs success
  path). Bites during operator interventions. Reset state where the condition becomes true, not
  where control usually flows.

## Fail loudly so the next bug is cheap
After the fix, leave the code safer than it was: assert physical invariants and array shapes/units at
boundaries; guard against NaN/inf; check matrix conditioning before solving; confirm optimizers converged
(report iterations and final residual). Promote the bug two ways so it cannot cost twice. Add the minimal
failing case to `correctness-suite` as a regression check, so it can never silently return. Append a
one-line **`symptom → check`** entry to `CONVENTIONS.md` → *Known gotchas*, so the failure is recognized at
a glance instead of re-debugged.

**Never regenerate or overwrite the campaign's INPUTS on a diagnosis you have not confirmed.** CORE already
says to confirm before an irreversible action; inputs are where that rule most often has to fire, because
"the data must be wrong" is a natural conclusion partway down this ladder and acting on it destroys the
thing you would need to check. Reach CONFIRMED against the highest-authority artifact first — read the
actual data-prep or pipeline source, not a derived statistic or a plausible correlation. Handing the
destructive action to the user on a below-CONFIRMED diagnosis makes them your only backstop.

**Tooling installed while debugging must be non-intrusive.** A monitor, watcher, or auto-start process added
during debugging must run windowless and headless with no per-iteration side effects (no console pop-ups, no
resource spikes), and must be smoke-tested for that before it is left running. Debug infrastructure that
itself misbehaves is a new bug, and one that can run unnoticed for a long time.

## When it isn't a bug
The ladder is for behavior that diverges from what the code should do. If the ladder bottoms out with the
code correct and the idea capped (it runs and does not work), that is not a debugging problem.
Diagnose it and consult `docs/reference/pivoting.md` for the refine-versus-pivot decision. A genuine,
serious, documented implementation barrier can justify shelving, but only after the ladder rules out a bug. Do not
abandon an idea on the strength of a crash.

## Composition
- **`dimensional-analysis`** — rung 3 (units/signs) and localizing a scale bug.
- **`correctness-suite`** — where the fixed bug becomes a permanent regression gate; a green suite also
  narrows the bisection by identifying which invariant broke.
- **`verify`** — once fixed, re-verify the result; a crash never counts as a refutation of the idea.
- **`pivoting`** — only after the ladder proves it is a capped idea, not a bug.
- **`attribute-mechanism`** — once the ladder clears the code and a real signature persists (rung 7 /
  "When it isn't a bug"), the question shifts from "is the code right" to "what physical cause produces
  this"; hand off to `attribute-mechanism`.

## Debug report (when worth recording)
For a non-trivial bug, capture it briefly: expected vs actual, the root cause (the mechanism, not
the symptom), the fix, and the regression check added. In a campaign this goes in the logbook;
record the why of a subtle root cause with `record-decision`.

## Checklist
- [ ] Reproduced deterministically (seed logged); recent changes noted.
- [ ] Reduced to the smallest failing case.
- [ ] Units / signs / conventions checked first.
- [ ] Diverged from a trusted reference at an identified input.
- [ ] Bisected one change at a time to the root cause (mechanism, not symptom).
- [ ] Fix verified; a regression check added to `correctness-suite`; invariants now fail loudly.
