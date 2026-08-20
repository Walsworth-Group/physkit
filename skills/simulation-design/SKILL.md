---
name: simulation-design
description: >-
  Design a simulation BEFORE writing its code — the simulation-specialized form of frame-problem. Use when
  about to build or commission a simulation, solver, forward model, surrogate, or synthetic-data generator,
  or phrasings like "I need to simulate...", "let's model... numerically", "build a forward model for...",
  "should I write this solver or use a package?". It produces, up front: a survey and choice of mature tools
  vs from-scratch code; the model's assumptions and domain of validity (starting from the physics
  inventory); and the simulation's Verification, Validation & UQ PLAN — which analytic limits / manufactured
  solutions / convergence studies will establish the code is right, which independent data will validate it
  (on held-out data — calibration is not validation), and how uncertainty will be quantified. Think the
  simulation and its checks through before implementing, not code-then-debug. Feeds correctness-suite (which
  executes the plan); draws on docs/SIMULATION_VALIDATION.md.
---

# simulation-design — plan the simulation and its verification before you code

A simulation written first and checked later bakes silent bugs and unvalidated models into the result. Decide
what to build, what it assumes, and how its correctness will be established, before the first line of solver
code. This skill is `frame-problem` specialized to simulations: it starts from that skill's physics inventory
and a-priori bounds and turns the verification plan into a concrete V&V&UQ plan for a numerical model. Full
doctrine: [`docs/SIMULATION_VALIDATION.md`](../../docs/SIMULATION_VALIDATION.md); this skill applies it at
design time.

Verify before you validate. **Verification** is solving the equations right: correct code, converged numerics.
**Validation** is solving the right equations: the model matches reality within its domain. **UQ** is how much
to trust the prediction. Calibration is not validation.

---

## 1 · Survey tools before building one
Reinventing a solver is slow and a fresh source of bugs.
- **Survey mature, validated packages first** (open-source especially) and choose an established one where it
  fits: less code under test, fewer places for a bug to hide. Record what you surveyed and why you chose.
- **Build from scratch only when** nothing fits, the physics is novel, or a transparent reference
  implementation is needed. When building, keep the numerical core small and testable (isolate I/O, RNG,
  hardware) so `correctness-suite` can unit-test it.
- **Pin versions** of whatever you use, so results reproduce.

## 2 · State the model: assumptions and domain of validity
Carry the **physics inventory** from `frame-problem` into the simulation:
- The governing equations, with the effects included vs excluded and why (the inventory). Prefer the
  **minimally sufficient model**: add a term only when it earns its keep; do not bury a structural gap under
  free parameters.
- The **assumptions** the model rests on, and the **domain of validity** (parameter ranges, regimes). Never
  extrapolate beyond that domain unflagged.
- **Nuisance and calibration parameters must track independent ground truth, not their own history.** A
  registration, background, or drift-correction parameter re-solved with its own previous estimate as the
  effective prior converges to a stable-looking value that is its own accumulated drift: a silent walk with no
  error signal (`debug`'s silent-bug catalog: self-referential nuisance-parameter anchoring). State explicitly
  what ground truth each nuisance parameter is anchored to, and confirm the fit cannot be satisfied by chasing
  itself.
- The **discretization choices** (mesh/timestep/basis/tolerance) and what controls their error.
- Where the **dimensionless groups** (`dimensional-analysis`) put the problem. They decide which terms
  dominate and what resolution the stiff/dominant scales demand.

## 3 · Write the V&V&UQ plan (the heart of this skill)
Decide every check now, as a concrete plan `correctness-suite` will later execute.

**Verification — is the code/math right?** Choose the checks that apply:
- **Analytic / closed-form limits** the solver must reproduce (known special cases, asymptotic limits).
- **Method of Manufactured Solutions (MMS)** — pick an exact solution, plug it in to derive the forcing
  term, and confirm the code recovers it. The strongest general code-verification tool.
- **Order-of-accuracy test** — refine the grid/timestep and confirm the error shrinks at the method's
  *theoretical* rate, not merely that it shrinks. A wrong observed order is a discretization bug.
- **Conservation / symmetry invariants** that must hold exactly or to round-off (energy, mass, charge; the
  symmetries of the setup); a frozen **self-test** asserting a known input→output.
- **Sign / convention round-trip** — for a forward model or data generator, a check that a known simple input
  (a uniformly-poled dipole, a manufactured source) produces output whose sign, units, and ordering match
  a trusted analytic reference. Plan this as a **gate that must pass before the model is FROZEN** as a
  campaign input. Frozen is not validated: a sign or convention bug locked into a frozen generator corrupts
  every downstream experiment and is expensive to catch late.
- **Convergence study** — refine until the answer stops moving, and separate numerical error from model
  error so a data gap is not attributed to the wrong one.
- **Joint constraints across sequential fits.** A fit run frame-by-frame or step-by-step (a time series, a
  hysteresis sweep, a sequential update) can look reasonable at every step while collectively absorbing real
  signal into drifting per-step nuisance parameters (state co-adaptation). The residuals look clean because
  the model adapted, not because it is right. Whenever consecutive fits share a nuisance parameter, plan a
  **joint or monotonicity constraint across steps** (shared parameters, an enforced monotone trend, a global
  refit) as part of the verification plan. That restores the residuals as a trustworthy diagnostic
  (`verify`'s residual-nature interrogation).

**Validation — is it right for reality?** Plan this *before* you fit anything:
- **Identify the validation data up front** and hold it out. Compare to measurement or an established
  benchmark with uncertainty on both sides, via a quantitative metric. Validate unit → subsystem →
  full system; a full-system match can hide **compensating errors**.
- Keep calibration data separate from validation data. Tuning to data then reporting agreement with the
  same data is calibration, not validation.
- If a search/ML loop will score against the simulator, plan to cross-check apparent winners against
  higher fidelity, because reward-hacking a flawed simulator is the default failure. Mind the
  **sim-to-real gap**: synthetic guardrails are necessary, not sufficient.

**UQ — how much to trust it?**
- Distinguish **aleatory** (irreducible) from **epistemic** (reducible) uncertainty, and plan to propagate
  both to uncertainty bands on every reported prediction.
- Plan a **sensitivity analysis** to find which inputs and assumptions dominate the output uncertainty. That
  is where to spend effort.

## 4 · Capture application-specific checks
Record the field-standard comparisons, known numerical artifacts, and checks that are standard practice in
the subfield for *this* simulation. They go into `campaign.md` §Verification (the V&V&UQ method itself is
the physkit plugin's `docs/SIMULATION_VALIDATION.md`, never restated per campaign) and become standing
regression gates in `correctness-suite`. Record the reason for a non-obvious one (`record-decision`).

## 5 · Surface the design, then build
Show the user the tool choice, the model + domain of validity, and the V&V&UQ plan before implementing. That
is the cheapest point to catch a missing validation, an over-complex model, or a check that will not
discriminate. Then implement, with `correctness-suite` executing the plan as the code is written. Do not leave
the checks to the end: an order-of-accuracy test on day one catches bugs while they are cheap.

## Composition
- **Upstream:** `frame-problem` (physics inventory + a-priori bounds), `dimensional-analysis` (dominant
  terms, resolution scales).
- **Downstream:** `correctness-suite` executes the V&V plan and promotes checks to regression
  gates; `verify` adversarially checks a resulting claim; `report` documents the model, domain, and
  V&V evidence.
- **Doctrine:** `docs/SIMULATION_VALIDATION.md` (the full V&V&UQ reference + standards: Sargent;
  Schlesinger et al.; ASME V&V 10/20/40).

## Before you write solver code — checklist
- [ ] Surveyed mature tools; chose build-vs-reuse deliberately and recorded why; versions pinned.
- [ ] Model stated: equations, effects in/out (inventory), assumptions, domain of validity, discretization.
- [ ] Verification plan: analytic limits + MMS + order-of-accuracy + invariants + convergence (those that apply).
- [ ] Validation plan: validation data identified and held out; calibration ≠ validation; unit→system hierarchy.
- [ ] UQ plan: aleatory vs epistemic; propagation to bands; sensitivity analysis.
- [ ] Application-specific checks / known artifacts captured.
- [ ] Design surfaced to the user before implementing.
