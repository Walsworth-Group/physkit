---
name: correctness-suite
description: >-
  Standing correctness and regression checks for simulation code.
---

# correctness-suite — the standing safety net for numerical code

`verify` asks whether a given result is right; this skill asks whether the machinery is still right, and
makes the answer a single command. It turns the verification plan (from `simulation-design` /
`frame-problem`) into an executable suite, keeps it green, and re-runs it after every core change so a
silent convention/sign/units slip is caught immediately instead of corrupting a ranking weeks later. A green
suite is not proof of a finding, but no finding built on a red suite is trustworthy.

Bring software-testing discipline, specialized to physical-simulation correctness: a layered suite, cheap
checks first, regression on every fixed bug.

**Where it lives (campaign).** The scaffold ships at `tests/correctness_checks.py`:
five skip-stubs (analytic-limit, invariants, parity, convergence, regression) filled from
`campaign.md` §Verification. `run_campaign.py` runs it on every experiment and records the status. Only an
affirmative GREEN green-lights a promotion. RED, EMPTY (zero active checks, the all-skip scaffold), ERROR,
and ABSENT each block it via `guard_promotion`. Deleting or never finishing the suite is not a way past
the gate. A campaign with no simulator records an explicit `tests/CORRECTNESS_NA.md` (a reviewable N/A
decision) to proceed. `verify` treats a non-green suite as a promotion blocker; re-run after any core/FROZEN
change (a stale green is rejected too; `campaign-status` §2). Run:
`python tests/correctness_checks.py` (exit 0 = green · 1 = failed · 2 = empty).

---

## 1 · Build the checks (encode the V&V plan)
Each item from the verification plan becomes one runnable, asserting check that fails loudly (a clear
message + the numbers), is deterministic (seed every RNG; log the seed), and is fast where possible.
Implement the ones that apply:

- **Analytic / closed-form limits** — assert the code reproduces a known special case or asymptotic limit
  to tolerance.
- **Method of Manufactured Solutions (MMS)** — inject an exact solution, derive its forcing term, assert the
  code recovers it. The strongest general code-verification check.
- **Order-of-accuracy** — refine grid/timestep over a few levels and assert the observed convergence rate
  matches the method's theoretical order (not merely that error decreases). A wrong order is a
  discretization bug even when the answer looks plausible.
- **Conservation / symmetry invariants** — assert energy/mass/charge conservation and the setup's symmetries
  hold to round-off (or the expected tolerance).
- **Independent-method parity** — assert a second, mechanism-diverse computation agrees on a case both can do.
- **Convergence** — assert the answer is stable under further refinement, with numerical error separated
  from model error.
- **Frozen self-test** — a fast `--selftest` asserting a known input→output for the metric/scorer and core
  physics, so a sign/convention slip, the most common silent bug, trips immediately.
- **Sign / convention round-trip** — for a **forward model or data generator**, feed a known simple input (a
  uniformly-poled dipole, a manufactured source) through the pipeline and assert the sign, units, and
  ordering conventions of the output match a trusted analytic reference (and, where invertible, that
  forward∘inverse returns the input). This is the cheapest guard against a convention or sign error that
  mirrors or negates everything downstream. Nothing complains, so it can persist in a FROZEN generator
  across a long series of experiments.
- **Application-specific checks** — the field-standard comparisons and known-artifact guards captured in the
  plan. Encode the checkable ones here.

Keep the **numerical core isolated** from I/O / hardware / RNG so each check can exercise it in isolation.
Fail loudly on NaN/inf, bad array shapes/units at boundaries, ill-conditioned solves, and non-converged
optimizers: a number off a non-finite or non-converged solve is noise, not data.

## 1b · Orthogonal sanity checks — catch a *fake-good* number
A metric can look good and be an artifact. Beyond the physics checks above, run a small panel of cheap,
orthogonal checks, each probing a different failure mode. A real result passes all of them; a number that
fails one is suspect regardless of its value:
- **Output / generation sanity** — the produced quantity is finite, in-range, and physically plausible (not
  saturated, clipped, or collapsed to a constant).
- **No-skill floor** — a scrambled / random / predict-the-mean input collapses to the no-skill score. A win
  that survives scrambling is leakage, not signal (the metric self-test's null control).
- **Train ↔ eval tracking** — the held-out metric moves with the fit/training metric; eval improving while
  train does not (or the reverse) indicates a leak or a bug, not a result.
- **Data consumption / leakage** — the evaluation saw the data it should and not the data it should not (no
  test-in-train, no target leak; the expected number of samples were actually scored).
- **Stream scan** — search the run's stderr/log for NaN/inf, silent fallbacks, dtype downcasts, and
  convergence warnings; a buried warning is often the result.
- **Shape / parameter drift** — array shapes, units, and free-parameter count match what was intended; a
  silent broadcast or one extra fitted parameter accounts for many apparent improvements.
- **Guardrail scope** — a closure/sanity guardrail must exercise the lever/code path it is meant to guard.
  Perturb the lever, including to a known-bad value, and confirm the guardrail's output changes. A guardrail
  that reads identically regardless of the lever is worse than no guardrail: it looks like coverage. Flag
  any guardrail that cannot be shown to fail as untested, not passing. (`verify` §4 item 6 runs this same
  check per-claim; encode it once here as a standing test.)

A short watchlist of **statistical fallacies** that manufacture false wins: *Simpson's paradox* (an
aggregate trend that reverses by subgroup), *survivorship / selection* (concluding from only the runs that
finished), *multiple comparisons* (selecting the best of many seeds or configs without correction), and
*regression to the mean* (a re-test of an extreme run drifting back). When a result could be one of these,
run the splitting or correction control before believing it.

## 2 · Make it a suite the runner can schedule
- Organize the checks into one entry point — in a campaign, `tests/correctness_checks.py`'s `CHECKS`
  list: the runner hosts the run, prints a per-check pass/fail summary, and records each check's cost and
  the files it executed (`results/correctness_state.json`). Outside a campaign, a `tests/` suite or a
  `--selftest` flag that prints a clear summary and tees a log.
- **Declare each check's row** with `@check(row=...)`. The campaign's verification preset
  (`configs/loop.json` `verify.preset`; `docs/reference/verification-presets.md`) decides when each row
  runs, and the runner meters everything that fires every unit:

  | row | what it may test | its inputs |
  |---|---|---|
  | `invariants` (the default when undeclared) | a cheap property of this run's OUTPUT: conservation, ranges, no NaN/inf, shapes, sum rules | the result |
  | `machinery` | the code's own fixed-input checks: a known answer, an analytic limit, parity between two methods, a convergence study, synthetic recovery | its own fixtures — never this run's config or result |
  | `gates` | an expensive per-result gate: a leave-one-out refit, a bootstrap, a held-out score | the experiment (the check takes one argument) |

  | preset | `invariants` | `machinery` | `gates` |
  |---|---|---|---|
  | `none` | off | off | off |
  | `minimal` | every unit | off | off |
  | `light` | every unit | once, at setup | a new best (`promotion`) |
  | `heavy` | every unit | when the code it executed changes | a new best |
  | `intensive` | every unit | every unit | every unit |

  Whatever the preset, a FROZEN-core change makes every check due. Every-unit checks share a budget of a
  tenth of the unit's measured cost (never below thirty seconds); a `promotion` gate runs after the solve
  of a result that is a new best.

  Authoring is where a check is judged too slow or too numerous, not cycle forty. An `invariants` check
  runs in seconds and names the failure the runner's own floor would miss. A `machinery` check that reads
  this run's config is a result check wearing the wrong row. A check that shells out declares
  `depends_on=("path", ...)` so what it depends on is seen. `every="<reason>"` pins a check to every unit
  whatever the preset (still metered). An over-budget every-set is refused at preflight by name; one
  that grows slow mid-campaign is demoted to promotion-time, loudly, never silently skipped. Never
  conclude correctness from the every-set alone for a load-bearing result: that is what the machinery
  and gates rows, and the result's independent check, are for.
- **The contract checks** are the setup audit's (`new-campaign` Step 3.7), shipped as four `machinery`
  stubs: `baseline_reproduces`, `noise_floor_measured`, `metric_discriminates`, `synthetic_recovery`.
  Green before anything is frozen; the validator refuses a suite without them unless
  `tests/CORRECTNESS_NA.md` records why. A contract error is paid on every unit afterwards, and no
  per-unit preset reaches it.
- Record, next to the suite, what each non-obvious check is for (`record-decision`), so a later editor does
  not delete a guard whose purpose is not evident.

## 3 · Keep it green (the gate)
- **Validate before freezing** (frozen ≠ validated). Run the suite, especially the sign/convention
  round-trip and the symmetry self-tests, on a forward model / data generator / scorer before it is declared
  FROZEN and a campaign builds on it. FROZEN means locked, not correct: a frozen but unvalidated model bakes
  its bug into every downstream experiment, and matching a published number can drive reproduction of that
  publication's bug. Validate first, then freeze.
- **A change to core/FROZEN code re-runs the suite** — the scoring math, the physics/geometry, the
  forward model. In a campaign the runner does this: a FROZEN-core change makes every check due, and a
  `machinery` check re-runs whenever the code it executed last time moves (compared as code, so a
  comment is not a change). Do not edit FROZEN code and skip the suite; a change to the scorer is a
  declared metric epoch (`roles/REFERENCE.md` §Metric epochs) — the runner binds the scorer's code to its
  epoch and refuses an undeclared change — and the epoch stays pending until the user ratifies it.
- **A red suite blocks trust.** Do not promote a result, write a DISCOVERY, or report a number while a
  relevant check is failing. Fix the code or fix the check, and state which.
- **Stale caches.** Invalidate any cached invariant (a precomputed operator/dictionary) on the inputs that
  define it. A stale cache reused after a core change is a silent failure the frozen self-test must catch.

## 4 · Promote every check to a regression gate
When a bug is found and fixed, add to the standing suite the check that would have caught it: a minimal
reproducing case asserting the now-correct behavior. When the verification plan turns up a new
application-specific check, add it. The suite then only grows stronger, and the same bug cannot silently
return. New checks are appended as the work uncovers them. A regression check joins the row matching
what it tests: an output property → `invariants` (most of them); a bug reproduced on fixed inputs →
`machinery`; a per-result statistical guard → `gates`. A refuted finding that becomes a check costs one
check once and milliseconds every unit after — the reuse a light preset rests on.

When the bug was a **silent failure whose output imitated the effect under study** (`debug`'s gotcha
catalog: exit 0, no NaNs, an ordinary convergence metric, and a result that reads like the sought
signature), the regression check is a **physical magnitude floor calibrated on a validated corpus**, not a
tighter tolerance on the solver's own status. Assert it on every run that writes the artifact, not only on
the case that failed.

## Composition
- **Upstream:** `simulation-design` / `frame-problem` hand over the V&V plan and the application-specific
  checks this skill encodes; `dimensional-analysis` supplies cheap invariants (units, scaling).
- **Downstream / alongside:** `verify` uses a green suite as evidence when adjudicating a claim (evidence,
  not proof); a campaign's independent-verification gate and `campaign-status` check
  suite-green; `report` cites the executed checks in its verification section.
- **Doctrine:** `docs/SIMULATION_VALIDATION.md` (MMS, order-of-accuracy, validation hierarchy, compensating
  errors, domain of applicability).

## Before you rely on the suite — checklist
- [ ] Every applicable plan check is encoded as an asserting, deterministic, loud-failing test.
- [ ] MMS and an order-of-accuracy test exist for any discretized solver (not just "error is small").
- [ ] Conservation/symmetry invariants are declared `invariants`; the frozen self-test is the runner's own floor.
- [ ] The four contract checks exist and are green (or `tests/CORRECTNESS_NA.md` records why not).
- [ ] A sign/convention round-trip + symmetry self-tests ran and passed before any forward model / data generator was frozen (frozen ≠ validated).
- [ ] Application-specific checks from the plan are included.
- [ ] The orthogonal sanity panel (no-skill floor, train↔eval tracking, leakage, stderr scan, shape/param drift) passes for any load-bearing number.
- [ ] Every check declares its row; preflight shows the every-set's measured cost within budget.
- [ ] It was re-run after the latest core change and is GREEN (or failures are openly flagged).
- [ ] Every previously-fixed bug has a regression check guarding it.
