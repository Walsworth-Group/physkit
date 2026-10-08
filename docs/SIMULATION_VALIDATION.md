---
id: simulation-validation
kind: reference-doc
layer: shared
load: on-demand
load_trigger: When a simulation, forward model, surrogate, synthetic data, or simulator-scored search is involved — the full V&V&UQ depth behind simulation-design / correctness-suite.
frozen: false
review: living
---

# Simulation Validation — kit doctrine (Verification, Validation & Uncertainty Quantification)

A result that relies on a simulation (a forward model, a simulator inside the metric, synthetic training
data, a surrogate or emulator, or a generative search scored by a simulator) is only as trustworthy as that
simulation. `simulation-design` plans this work and
`correctness-suite` executes it. This document is the fuller doctrine behind all three.

> Compiled from established simulation V&V / VVUQ practice and the framework in Wikipedia's
> ["Verification and validation of computer simulation models"](https://en.wikipedia.org/wiki/Verification_and_validation_of_computer_simulation_models):
> Sargent; Naylor & Finger; Schlesinger et al.; Banks–Carson–Nelson–Nicol; ASME V&V. See References.
> Extend with project- or domain-specific sources as the work requires.

## The one distinction to internalize
- **Verification**: are we solving the equations right? The code and numerics implement the intended math
  correctly and have converged.
- **Validation**: are we solving the right equations? The model reproduces reality, within its intended
  range of use.
- **Uncertainty Quantification (UQ)**: how much should we trust a prediction? The prediction carries a
  quantified uncertainty.

Two rules follow. Verify before you validate: a validation comparison against buggy or unconverged code is
meaningless. Calibration is not validation: a model cannot be validated on the data it was tuned to.

Formal definitions (Sargent; Schlesinger et al.): verification confirms the model is correctly implemented
with respect to the conceptual model. Validation substantiates that the model, within its domain of
applicability, possesses a satisfactory range of accuracy consistent with its intended application.

## Where V&V fits — the model lifecycle
V&V is iterative throughout model development. A model is validated only to the degree its intended purpose
requires: it is built for a specific objective and judged valid for that objective. Three things get
checked, against three artifacts:
- **Conceptual-model validation**: are the theories and assumptions behind the model correct and reasonable
  for the intended use? Validate the assumptions (§2).
- **Computerized-model verification**: is the conceptual model implemented correctly in code? (§1)
- **Operational validity**: does the model's output behaviour have sufficient accuracy over its domain of
  applicability for the intended application? (§2)

A classic recipe (Naylor & Finger, 1967): build a model with high face validity, validate its assumptions,
then compare its input–output behaviour to the real system.

## 1. Verification — is the code/math right?
**Code verification** (the implementation matches the intended math):
- Unit-test the components. Assert invariants: conservation laws, symmetry and reciprocity, known limiting
  cases.
- Compare to analytic or closed-form solutions where they exist: a uniform field, a point source, a
  symmetric configuration.
- **Method of Manufactured Solutions (MMS):** insert a chosen exact solution into the equations, derive the
  source term it implies, and confirm the code recovers it. It is the strongest code-verification check for
  PDE and ODE solvers.
- **Order-of-accuracy test:** refine the discretization and confirm the error shrinks at the method's
  theoretical rate. A wrong rate indicates a bug, not coarseness.
- Keep a frozen **regression self-test**: a known input must keep producing the known output across code
  changes (`--selftest`).
- Apply the classic model-logic verification techniques: expert review of the model; logic and flow
  diagrams that enumerate every logically possible action; output-reasonableness testing (vary the inputs
  and confirm the outputs move sensibly); an interactive debugger; and standard software-engineering
  verification practices.

**Solution (numerical) verification** (this particular run is numerically converged):
- **Convergence study:** refine grid, time-step, mesh, tolerance, or sample count until the answer stops
  changing. Report the converged value and an estimate of the discretization error.
- Confirm that solvers and optimizers converged: residuals, iteration count, final loss. Running without
  error is not convergence.
- Guard against numerical artifacts: NaN or inf, negative densities or probabilities, spurious
  oscillations, energy drift. Check matrix conditioning before inverting or solving.
- Separate numerical error from model error. Never attribute a discretization artifact to the physics, or a
  physics error to the discretization.

## 2. Validation — is the model right for reality?
- Compare predictions to experimental data with uncertainty on both sides: a prediction band against a
  measurement with its error bar, not point-to-point.
- Use a quantitative validation metric: a defined discrepancy measure, not visual agreement.
- Calibration is not validation. Parameters tuned to fit data cannot be validated on that same data.
  Validate on held-out data, or on different conditions or a different observable than you calibrated on,
  and report what was calibrated and what was validated.
- **Validation hierarchy:** validate bottom-up, from unit and benchmark problems to subsystem to full
  system. A full-system match can hide compensating errors; piecewise validation catches them.
- **Domain of applicability:** state the parameter ranges and regimes the model is validated for. Do not
  extrapolate beyond them without flagging the extrapolation as unvalidated.
- A persistent model–data gap that survives verification is model-form (structural) error: the physics is
  incomplete or wrong, not a tuning problem. Do not absorb it into more free parameters.

**Named validation techniques.** Use several; no single one is sufficient.
- **Face validity:** do knowledgeable users find the model and its outputs reasonable, including how it
  responds to input changes?
- Validate the three kinds of assumption: **structural** (how the system operates and is arranged, checked
  against the real system), **data** (sources are reliable and distributions fit; test with goodness-of-fit
  and handle outliers), and **simplification** (approximations known to be false are still acceptable for
  this purpose).
- Compare model output to system output, quantitatively where possible: a hypothesis test (a t-test, asking
  whether model output equals system output at significance α), confidence intervals (is the model within a
  tolerance ε of the system?), or model-accuracy-as-a-range (accept if the difference falls within
  pre-specified bounds). Use graphical comparison only as a fallback when the statistical assumptions
  cannot be met.
- Weigh both error risks in any model-vs-system test. A **Type I error (the model builder's risk)** is
  rejecting a valid model. A **Type II error (the model user's risk)** is accepting an invalid one. Choose
  sample size and α with both in mind; operating-characteristic and risk curves trade them off.
  Goodness-of-fit tests (Kolmogorov–Smirnov, chi-square) validate data distributions.
- Lack of appropriate data is the most common reason validation fails. Plan for the validation data up
  front.

## 3. Uncertainty Quantification (UQ)
- Classify uncertainty: **aleatory** (irreducible randomness) or **epistemic** (lack of knowledge,
  reducible with more data or refinement).
- Account for all sources: input and parameter uncertainty, numerical and discretization error,
  **model-form** uncertainty, and the measurement uncertainty in the validation data.
- Propagate input and parameter uncertainty to the outputs (Monte Carlo / sampling, surrogate-based, or
  polynomial chaos). Report predictions with uncertainty bands, never as bare point values.
- **Sensitivity analysis:** identify which inputs and parameters dominate the output uncertainty, using
  local derivatives or global variance-based (Sobol) indices. Spend measurement and modeling effort on the
  dominant ones.

## 4. Pitfalls & tips (especially inside an optimization / ML loop)
- Verify before you validate. Never trust an unconverged or unverified simulation.
- Calibration masquerading as validation is the most common self-deception here. Keep the two data sets
  strictly separate.
- **Reward-hacking the simulator.** Any search or ML loop that optimizes against a simulator will exploit
  its inaccuracies; the best-scoring design may be best only in the simulator's errors. Cross-validate
  winners against a higher-fidelity model or an experiment (generative-design and surrogate archetypes).
- **Sim-to-real / domain gap.** Synthetic data and in-loop simulations omit real noise, drift, calibration
  bias, and off-model physics. A guardrail resting on simulation is necessary but not sufficient.
- Test limiting cases where the answer is known: zero and infinite limits, symmetric configurations,
  conserved quantities.
- Pin the simulator version, its dependencies, the config, and the seed. A result that will not reproduce
  on another machine is a verification problem.
- Document assumptions and the domain of validity in `../../PROJECT.md` (§Equations and
  methods; the domain of validity is a standing constraint), and re-check them whenever
  a discovery changes the physics.

## 5. Simulation-scored search loops (when a search/ML loop is scored by the simulation)
When the simulator is not only a predictor but the scorer of an optimization or discovery loop (a
generative-design search, an LLM-in-the-loop designer, a surrogate-guided optimizer), the loop will find
and exploit every weakness in the scorer. Extra disciplines apply, with source leads under References:

- **In-loop convergence / feasibility gate.** Reject any candidate whose simulation does not converge,
  before it is scored. Otherwise the search optimizes numerical noise. The more design freedom the
  generator has (an LLM emitting arbitrary expressions, for example), the more essential this gate is.
- **Dual direct + downstream objective.** Score a candidate on both the quantity it directly fits and the
  downstream physical output that quantity feeds, not on the direct fit alone. This blocks the loop from
  fitting the proxy in a way that wrecks the physics the proxy should drive, and it avoids numerical
  stiffness. Example: a Reynolds-stress closure scored on the stress and on the resulting velocity field.
  It is the concrete form of "do not reward-hack the simulator" for forward-model-scored search.
- **Generalize-across-regimes as the acceptance bar.** A win at one condition is not a win. Require the
  discovered artifact to hold across geometries, parameters, and regimes (for example, multiple geometries
  crossed with Reynolds numbers) before promotion. `verify` applies the same generalization check.
- **Track the evaluation budget as a first-class metric.** When each evaluation is an expensive physics
  solve, the win is fewer simulator calls, not only final quality. Report the number of expensive
  evaluations, and benchmark sample-efficiency against a strong classical optimizer such as NSGA-II, not
  the end result alone.
- **Diminishing-returns stopping criterion.** Detect convergence and stop, rather than burning a fixed
  budget regardless. A quality-based stop complements the kit's run-cap tiers.
- **Do not default to the biggest or hottest model.** Test model size and temperature as configuration
  levers rather than assuming more is better: a smaller model at a lower temperature can give higher
  constraint satisfaction and more consistent designs.

## 6. Surrogates & synthetic data
When you train a surrogate or emulator, or manufacture training data:
- **Validate the surrogate against the true evaluator.** Surrogate errors mislead the search. Re-check
  apparent winners on the real metric or simulator, never on the surrogate alone.
- **Synthetic-data-by-inversion.** When the forward map is cheap and the inverse is the hard problem,
  manufacture supervised data cheaply: generate random *solutions*, compute their (easy) forward outputs,
  and train the **inverse** map (solution-class → answer) on that data. **Caveats:** it needs a cheap,
  exact forward map, and many physical problems have only expensive or noisy simulators, so it will not
  always transfer. A model trained this way also carries train/test-distribution risk, so its value is
  realized only if it extrapolates. Test extrapolation directly, on larger and unseen instances of the
  class, not on the training set alone.

## 7. Practical V&V&UQ checklist
- [ ] **Code verification:** analytic / MMS / order-of-accuracy / invariants pass; a frozen self-test exists.
- [ ] **Solution verification:** convergence study done; numerical error estimated; solver convergence confirmed.
- [ ] **Calibration is not validation:** the two data sets are separate; validation is on held-out / independent conditions.
- [ ] **Quantitative validation metric** reported, with uncertainty on prediction and measurement.
- [ ] **Domain of applicability** stated; no silent extrapolation.
- [ ] **UQ:** dominant uncertainty sources identified (sensitivity); predictions carry uncertainty bands.
- [ ] **Anti reward-hacking:** if a loop optimizes against the simulator — feasibility/convergence gate on candidates; dual direct+downstream objective; winners cross-checked against higher fidelity / experiment.
- [ ] **Evaluation budget** tracked and benchmarked vs a classical optimizer; a diminishing-returns stop in place (for expensive-eval loops).
- [ ] **Surrogate/synthetic data:** surrogate validated against the true evaluator; any inversion-trained model passes an extrapolation test.
- [ ] **Provenance:** simulator version / config / seed pinned; assumptions documented in `../../PROJECT.md`.

## References & standards
Standard references for simulation V&V (per the Wikipedia article above):
- **R. G. Sargent**, *Verification and validation of simulation models* — the most-cited modern treatment.
- **Naylor & Finger (1967)** — the three-step validation approach (face validity → validate assumptions →
  compare input–output behaviour).
- **Schlesinger et al. (1979)**, *Terminology for model credibility*.
- **Banks, Carson, Nelson & Nicol**, *Discrete-Event System Simulation* — standard textbook reference.
- **ASME V&V** committee standards — consult the domain-appropriate one when it exists: **V&V 10 / 10.1**
  (computational solid mechanics), **V&V 20** (CFD & heat transfer), **V&V 40** (medical devices).

The loop-context practices in §5–6 are distilled from recent physical-science work: AutoTurb (Phys. Fluids
2025, arXiv ≈ 2410.10657); an LLM-as-mechanical-designer with FEM in the loop (J. Eng. Design 2026); and
meta-designing quantum experiments (Nat. Mach. Intell. 2026). These venue, year, and arXiv details are
**unverified** and recorded only as leads. Treat them as starting points; before citing any of them in a
report, verify the exact details against the source itself (`cite-check`).
