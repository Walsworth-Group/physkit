---
name: correctness-suite
description: >-
  Build and run a standing suite of correctness checks for a simulation, solver, forward model, or
  numerical pipeline — and keep it green. Use when you have a V&V plan to execute (from simulation-design or
  frame-problem), when about to edit FROZEN/core physics or scoring code and need a safety net, after fixing
  a numerical bug (add the check that would have caught it), or phrasings like "set up tests for the
  solver", "add validation checks", "make sure my changes didn't break the physics". It encodes the plan as
  executable checks — analytic limits, Method of Manufactured Solutions, order-of-accuracy, conservation/
  symmetry invariants, independent-method parity, convergence, and the application-specific checks — plus a
  fast frozen self-test, and promotes each hard-won check to a standing regression gate that re-runs after
  any core change. The suite must be GREEN before a result built on the code is trusted. Distinct from
  verify (adversarial check of one claim) and cite-check (citations).
---

# correctness-suite — the standing safety net for numerical code

`verify` asks "is *this result* right?"; this skill asks "is *the machinery* still right?" — and makes the
answer a button you can press. It turns the verification plan (from `simulation-design` / `frame-problem`)
into an executable suite, keeps it **green**, and re-runs it after every core change so a silent
convention/sign/units slip is caught immediately instead of corrupting a ranking weeks later. A green suite
is not proof of a finding, but **no finding built on a red suite is trustworthy.**

Bring software-testing discipline (a layered suite, cheap checks first, regression on every fixed bug),
specialized to physical-simulation correctness.

---

## 1 · Build the checks (encode the V&V plan)
Each item from the verification plan becomes one runnable, asserting check that **fails loudly** (a clear
message + the numbers), is **deterministic** (seed every RNG; log the seed), and is **fast** where possible.
Implement the ones that apply:

- **Analytic / closed-form limits** — assert the code reproduces a known special case or asymptotic limit
  to tolerance.
- **Method of Manufactured Solutions (MMS)** — inject an exact solution, derive its forcing term, assert the
  code recovers it. The strongest general code-verification check.
- **Order-of-accuracy** — refine grid/timestep over a few levels and assert the observed convergence rate
  matches the method's *theoretical* order (not merely "error decreases"). A wrong order is a discretization
  bug even when the answer looks plausible.
- **Conservation / symmetry invariants** — assert energy/mass/charge conservation and the setup's symmetries
  hold to round-off (or the expected tolerance).
- **Independent-method parity** — assert a second, mechanism-diverse computation agrees on a case both can do.
- **Convergence** — assert the answer is stable under further refinement (and that numerical error is
  separated from model error).
- **Frozen self-test** — a fast `--selftest` asserting a known input→output for the metric/scorer and core
  physics, so a sign/convention slip (the most common silent bug) trips immediately.
- **Sign / convention round-trip** — for a **forward model or data generator**, feed a known simple input (a
  uniformly-poled dipole, a manufactured source) through the pipeline and assert the **sign, units, and
  ordering conventions** of the output match a trusted analytic reference (and, where invertible, that
  forward∘inverse returns the input). This is the cheapest guard against the convention/sign bug that
  silently mirrors or negates everything downstream — the kind that has sat in a *frozen* generator for tens
  of experiments before a human caught it.
- **Application-specific checks** — the field-standard comparisons and known-artifact guards captured in the
  plan. Encode the checkable ones here.

Keep the **numerical core isolated** from I/O / hardware / RNG so each check can exercise it in isolation;
**fail loudly** on NaN/inf, bad array shapes/units at boundaries, ill-conditioned solves, and non-converged
optimizers (a number off a non-finite or non-converged solve is noise, not data).

## 1b · Orthogonal sanity checks — catch a *fake-good* number
A metric can look great and be an artifact. Beyond the physics checks above, run a small panel of **cheap,
orthogonal** checks that each probe a *different* failure mode — a real result passes **all** of them; a
number that fails one is suspect no matter how good it looks:
- **Output / generation sanity** — the produced quantity is finite, in-range, and physically plausible (not
  saturated, clipped, or collapsed to a constant).
- **No-skill floor** — a scrambled / random / predict-the-mean input collapses to the no-skill score; a
  "win" that survives scrambling is leakage, not signal (the metric self-test's null control).
- **Train ↔ eval tracking** — the held-out metric moves *with* the fit/training metric; eval improving while
  train doesn't (or vice-versa) signals a leak or a bug, not a result.
- **Data consumption / leakage** — the evaluation saw the data it should and *not* the data it shouldn't (no
  test-in-train, no target leak; the expected number of samples were actually scored).
- **Stream scan** — grep the run's stderr/log for NaN/inf, silent fallbacks, dtype downcasts, and
  convergence warnings; a buried warning often *is* the result.
- **Shape / parameter drift** — array shapes, units, and free-parameter count are what you intended (a silent
  broadcast or one extra fitted parameter explains many "improvements").

And a short watchlist of **statistical fallacies** that manufacture fake wins: *Simpson's paradox* (an
aggregate trend that reverses by subgroup), *survivorship / selection* (concluding from only the runs that
finished), *multiple comparisons* (cherry-picking the best of many seeds/configs without correction), and
*regression to the mean* (a re-test of an extreme run drifting back). When a result could be one of these,
run the splitting / correction control before believing it.

## 2 · Make it a suite you can run
- Organize the checks into a single runnable entry point (a `tests/` suite, a `make check`, or a
  `--selftest` flag) that prints a clear pass/fail summary and **tees output to a log**.
- **Tier by cost:** a *cheap* tier (limits, invariants, self-test, a coarse MMS) that runs after every change
  and in CI; an *expensive* tier (full order-of-accuracy sweeps, large convergence studies, validation runs)
  run on demand and before a result is promoted. Never conclude correctness from the cheap tier alone for a
  load-bearing result.
- Record, next to the suite, **what each non-obvious check is for** (`record-decision`) so a future editor
  doesn't delete a guard they don't understand.

## 3 · Keep it green (the gate)
- **Validate BEFORE you freeze (frozen ≠ validated).** Run the suite — especially the sign/convention
  round-trip and the symmetry self-tests — on a forward model / data generator / scorer *before* it is
  declared FROZEN and a campaign builds on it. "Frozen" means *locked*, not *correct*: a frozen-but-unvalidated
  model bakes its bug into every downstream experiment, and "match the published number" can quietly drive you
  to reproduce the original's bug. Validate first, then freeze.
- **Re-run the suite after any change to core/FROZEN code** — the scoring math, the physics/geometry, the
  forward model. Do **not** edit FROZEN code without re-running and (in a campaign) user sign-off.
- A **red suite blocks trust**: don't promote a result, write a DISCOVERY, or report a number while a
  relevant check is failing. Fix the code or fix the check (and say which).
- **Beware stale caches** — invalidate any cached invariant (a precomputed operator/dictionary) on the inputs
  that define it; a stale cache reused after a core change is a classic silent failure the self-test should
  catch.

## 4 · Promote every hard-won check to a regression gate
This is the compounding payoff. **When a bug is found and fixed, add the check that would have caught it** —
a minimal reproducing case asserting the now-correct behavior — to the standing suite. When the verification
plan turns up a new application-specific check, add it. The suite then only grows stronger, and the same bug
can never silently return. New checks are appended as the work uncovers them.

## Composition
- **Upstream:** `simulation-design` / `frame-problem` hand over the V&V plan and the application-specific
  checks this skill encodes; `dimensional-analysis` supplies cheap invariants (units, scaling).
- **Downstream / alongside:** `verify` uses a green suite as evidence when adjudicating a claim (evidence,
  not proof); a campaign's `program.md` independent-verification gate and `campaign-status` check
  suite-green; `report` cites the executed checks in its verification section.
- **Doctrine:** `docs/SIMULATION_VALIDATION.md` (MMS, order-of-accuracy, validation hierarchy, compensating
  errors, domain of applicability).

## Before you rely on the suite — checklist
- [ ] Every applicable plan check is encoded as an asserting, deterministic, loud-failing test.
- [ ] MMS and an order-of-accuracy test exist for any discretized solver (not just "error is small").
- [ ] Conservation/symmetry invariants and a fast frozen self-test are in the cheap tier.
- [ ] A sign/convention round-trip + symmetry self-tests ran and passed **before** any forward model / data generator was frozen (frozen ≠ validated).
- [ ] Application-specific checks from the plan are included.
- [ ] The orthogonal sanity panel (no-skill floor, train↔eval tracking, leakage, stderr scan, shape/param drift) passes for any load-bearing number.
- [ ] The suite runs from one entry point, tiered by cost, and tees a pass/fail log.
- [ ] It was re-run after the latest core change and is GREEN (or failures are openly flagged).
- [ ] Every previously-fixed bug has a regression check guarding it.
