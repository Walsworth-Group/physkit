---
id: simulation-validation
kind: reference-doc
layer: shared
load: on-demand
load_trigger: When a simulation, forward model, surrogate, synthetic data, or simulator-scored search is involved — the full V&V&UQ depth behind simulation-design / correctness-suite / PRINCIPLES §5.
frozen: false
addresses: [2, 5]
status: ported+augmented
review: living
---

# Simulation Validation — kit doctrine (Verification, Validation & Uncertainty Quantification)

When work relies on a **simulation** — a forward model, a simulator inside the metric, synthetic training
data, a surrogate/emulator, or a generative search scored by a simulator — the results are only as
trustworthy as that simulation. This is the kit's reference for making a simulation **trustworthy**.
[`PRINCIPLES.md`](PRINCIPLES.md) §5 is the summary; `simulation-design` plans it and `correctness-suite`
executes it; this is the fuller doctrine behind all three.

> _Compiled from established simulation V&V / VVUQ practice and the framework in Wikipedia's
> ["Verification and validation of computer simulation models"](https://en.wikipedia.org/wiki/Verification_and_validation_of_computer_simulation_models)
> (Sargent; Naylor & Finger; Schlesinger et al.; Banks–Carson–Nelson–Nicol; ASME V&V — see References).
> Extend with project- or domain-specific sources as the work requires._

## The one distinction to internalize
- **Verification** — *"are we solving the equations right?"* The code and numerics implement the intended
  math correctly and have converged.
- **Validation** — *"are we solving the right equations?"* The model reproduces reality, within its
  intended range of use.
- **Uncertainty Quantification (UQ)** — *"how much should we trust a prediction?"* The prediction carries
  a quantified uncertainty.

Two rules follow: **verify before you validate** (a validation comparison on buggy or unconverged code is
meaningless), and **calibration is not validation** (you cannot validate a model on the same data you
tuned it to).

Formal definitions (Sargent / Schlesinger et al.): **verification** = confirming the model is *correctly
implemented with respect to the conceptual model*; **validation** = *substantiation that the model, within
its domain of applicability, possesses a satisfactory range of accuracy consistent with its intended
application.*

## Where V&V fits — the model lifecycle
V&V is **iterative throughout model development**, and a model is validated only **to the degree its
intended purpose requires** — it is built for a specific objective and its validity is judged *for that
purpose*. Three things get checked, against three artifacts:
- **Conceptual-model validation** — are the theories and **assumptions** behind the model correct and
  reasonable for the intended use? (validate the *assumptions* — see §2).
- **Computerized-model verification** — is the conceptual model **implemented correctly** in code? (§1).
- **Operational validity** — does the model's **output behaviour** have sufficient accuracy over its
  **domain of applicability** for the intended application? (§2).

A classic recipe (**Naylor & Finger, 1967**): (1) build a model with high **face validity**, (2)
**validate its assumptions**, (3) **compare its input–output behaviour** to the real system.

## 1. Verification — is the code/math right?
**Code verification** (the implementation matches the intended math):
- Unit-test the components; assert invariants — conservation laws, symmetry/reciprocity, known limiting
  cases.
- Compare to **analytic / closed-form solutions** where they exist (a uniform field, a point source, a
  symmetric configuration).
- **Method of Manufactured Solutions (MMS):** insert a chosen exact solution into the equations, derive
  the source term it implies, and confirm the code recovers it — the gold standard for PDE/ODE solvers.
- **Order-of-accuracy test:** refine the discretization and confirm the error shrinks at the method's
  theoretical rate; a wrong rate signals a bug, not just coarseness.
- Keep a frozen **regression self-test**: a known input must keep producing the known output across code
  changes (`--selftest`).
- Also apply the classic model-logic verification techniques: **expert review** of the model;
  **logic / flow diagrams** that enumerate every logically possible action; **output-reasonableness
  testing** (vary the inputs and confirm the outputs move sensibly); an **interactive debugger**; and
  standard **software-engineering** verification practices.

**Solution (numerical) verification** (this particular run is numerically converged):
- **Convergence study:** refine grid / time-step / mesh / tolerance / sample count until the answer stops
  changing; report the converged value and an estimate of the discretization error.
- Confirm solvers/optimizers actually **converged** (residuals, iteration count, final loss) — not just
  "it ran without error."
- Guard against numerical artifacts: NaN/inf, negative densities/probabilities, spurious oscillations,
  energy drift; check matrix conditioning before you invert or solve.
- **Separate numerical error from model error** — never attribute a discretization artifact to the physics
  (or vice versa).

## 2. Validation — is the model right for reality?
- Compare predictions to **experimental data with uncertainty on BOTH sides** — a prediction band against
  a measurement with its error bar, not point-to-point.
- Use a **quantitative validation metric** (a defined discrepancy measure), not visual "looks close."
- **Calibration ≠ validation.** If you tuned parameters to fit data, you cannot validate on that same
  data. Validate on **held-out** data, or on different conditions / a different observable than you
  calibrated on, and report clearly what was calibrated vs what was validated.
- **Validation hierarchy:** validate bottom-up — unit/benchmark problems → subsystem → full system. A
  full-system match can hide **compensating errors**; piecewise validation catches them.
- **Domain of applicability:** state the parameter ranges / regimes the model is validated for, and do
  not extrapolate beyond them without flagging it as unvalidated.
- A persistent model–data gap that survives verification is **model-form (structural) error** — the
  physics is incomplete or wrong, not a tuning problem; don't bury it under more free parameters.

**Named validation techniques** (use several — no single one is sufficient):
- **Face validity** — do knowledgeable users find the model and its outputs reasonable, including how it
  responds to input changes?
- **Validate the three kinds of assumption:** **structural** (how the system operates / is arranged —
  check against the real system), **data** (sources are reliable and distributions fit — test with
  goodness-of-fit; handle outliers), and **simplification** (deliberately-false approximations are still
  acceptable for this purpose).
- **Compare model output to system output**, quantitatively where possible: a **hypothesis test**
  (e.g. a t-test — is model output = system output at significance α?), **confidence intervals** (is the
  model within a tolerance ε of the system?), or **model-accuracy-as-a-range** (accept if the difference
  falls within pre-specified bounds). Use **graphical comparison** only as a fallback when the
  statistical assumptions can't be met.
- **Weigh both error risks** in any model-vs-system test: a **Type I error (the model builder's risk)** =
  rejecting a *valid* model; a **Type II error (the model user's risk)** = accepting an *invalid* one.
  Choose sample size and α with both in mind (operating-characteristic / risk curves trade them off);
  goodness-of-fit tests (Kolmogorov–Smirnov, chi-square) validate data distributions.
- **Lack of appropriate data is the most common reason validation fails** — plan for the validation data
  you'll need up front.

## 3. Uncertainty Quantification (UQ)
- Classify uncertainty: **aleatory** (irreducible randomness) vs **epistemic** (lack of knowledge —
  reducible with more data or refinement).
- Account for all sources: input/parameter uncertainty, numerical/discretization error, **model-form**
  uncertainty, and the **measurement uncertainty** in the validation data.
- **Propagate** input/parameter uncertainty to the outputs (Monte Carlo / sampling, surrogate-based, or
  polynomial chaos) and report predictions **with uncertainty bands** — never bare point values.
- **Sensitivity analysis:** identify which inputs/parameters dominate the output uncertainty (local
  derivatives; global / variance-based / Sobol indices). Spend measurement and modeling effort on the
  dominant ones.

## 4. Pitfalls & tips (especially inside an optimization / ML loop)
- **Verify before you validate;** never trust an unconverged or unverified simulation.
- **Calibration masquerading as validation** is the #1 self-deception — keep the two data sets strictly
  separate.
- **Reward-hacking the simulator:** any search or ML loop that optimizes *against* a simulator will
  exploit its inaccuracies — the "best" design may be best only in the simulator's errors. Cross-validate
  winners against a higher-fidelity model or experiment (cf. generative-design / surrogate archetypes).
- **Sim-to-real / domain gap:** synthetic data and in-loop simulations omit real noise, drift, calibration
  bias, and off-model physics; a guardrail resting on simulation is necessary-but-not-sufficient.
- **Test limiting cases** where the answer is known (zero / infinite limits, symmetric configurations,
  conserved quantities).
- **Pin everything:** simulator version + dependencies + config + seed; a result that won't reproduce on
  another machine is a verification problem.
- **Document assumptions + domain of validity** in `../../shared/PHYSICS.md`, and re-check them whenever a
  discovery changes the physics.

## 5. Simulation-scored search loops (when a search/ML loop is scored by the simulation)
When the simulator is not just a predictor but the **scorer of an optimization or discovery loop** (a
generative-design search, an LLM-in-the-loop designer, a surrogate-guided optimizer), the loop will find
and exploit every weakness in the scorer. Extra disciplines, drawn from recent physical-science practice:

- **In-loop convergence / feasibility gate.** Reject any candidate whose simulation does not converge
  *before* it is scored — otherwise the search optimizes numerical noise. The more design freedom the
  generator has (e.g. an LLM emitting arbitrary expressions), the more essential this gate. *(AutoTurb,
  Phys. Fluids 2025 — a hard CFD-convergence constraint on every generated closure expression.)*
- **Dual direct + downstream objective.** Score a candidate on **both** the quantity it directly fits
  **and** the downstream physical output that quantity feeds — not the direct fit alone. This blocks the
  loop from fitting the proxy in a way that wrecks the physics it should drive (and avoids numerical
  stiffness). *(AutoTurb: scoring a Reynolds-stress closure on the stress **and** the resulting velocity
  field.)* It is the concrete form of "don't reward-hack the simulator" for forward-model-scored search.
- **Generalize-across-regimes as the acceptance bar.** A win at one condition is not a win; require the
  discovered artifact to hold across geometries / parameters / regimes (e.g. multiple geometries ×
  Reynolds numbers) before promotion. *(See also `verify`'s generalization check.)*
- **Track the evaluation budget as a first-class metric.** When each evaluation is an expensive physics
  solve, the real win is **fewer simulator calls**, not just final quality. Report the number of expensive
  evaluations and **benchmark sample-efficiency against a strong classical optimizer** (e.g. NSGA-II), not
  only the end result. *(LLM-as-mechanical-designer with FEM in the loop, J. Eng. Design 2026 — faster
  convergence and fewer FEM evaluations than NSGA-II.)*
- **Diminishing-returns stopping criterion.** Detect convergence and **stop**, rather than burning a fixed
  budget regardless — a quality-based stop that complements the kit's run-cap tiers.
- **Don't default to the biggest/hottest model.** In at least one careful study a **smaller model and a
  lower temperature** gave higher constraint satisfaction and more consistent designs — test model size and
  temperature as configuration levers rather than assuming more is better.

## 6. Surrogates & synthetic data
When you train a surrogate/emulator or manufacture training data:
- **Validate the surrogate against the true evaluator** — surrogate errors mislead the search; re-check
  apparent winners on the real metric/simulator, never on the surrogate alone.
- **Synthetic-data-by-inversion.** When the **forward** map is cheap and the **inverse** is the hard
  problem, manufacture supervised data cheaply: generate random *solutions*, compute their (easy) forward
  outputs, and train the **inverse** map (solution-class → answer) on that data. *(Meta-designing quantum
  experiments, Nat. Mach. Intell. 2026 — random programs → their states → train the state→program map.)*
  **Caveats:** it needs a *cheap, exact* forward map (many physical problems have only expensive/noisy
  simulators, so it won't always transfer), and a model trained this way carries train/test-distribution
  risk — so its value is only realized if it **extrapolates**, which must be tested directly (run the
  discovered artifact on larger/unseen instances of the class, not just the training set).

## 7. Practical V&V&UQ checklist
- [ ] **Code verification:** analytic / MMS / order-of-accuracy / invariants pass; a frozen self-test exists.
- [ ] **Solution verification:** convergence study done; numerical error estimated; solver convergence confirmed.
- [ ] **Calibration ≠ validation:** the two data sets are separate; validation is on held-out / independent conditions.
- [ ] **Quantitative validation metric** reported, with uncertainty on prediction AND measurement.
- [ ] **Domain of applicability** stated; no silent extrapolation.
- [ ] **UQ:** dominant uncertainty sources identified (sensitivity); predictions carry uncertainty bands.
- [ ] **Anti reward-hacking:** if a loop optimizes against the simulator — feasibility/convergence gate on candidates; dual direct+downstream objective; winners cross-checked against higher fidelity / experiment.
- [ ] **Evaluation budget** tracked and benchmarked vs a classical optimizer; a diminishing-returns stop in place (for expensive-eval loops).
- [ ] **Surrogate/synthetic data:** surrogate validated against the true evaluator; any inversion-trained model passes an extrapolation test.
- [ ] **Provenance:** simulator version / config / seed pinned; assumptions documented in `../../shared/PHYSICS.md`.

## References & standards
Standard references for simulation V&V (per the Wikipedia article above):
- **R. G. Sargent**, *Verification and validation of simulation models* — the most-cited modern treatment.
- **Naylor & Finger (1967)** — the three-step validation approach (face validity → validate assumptions →
  compare input–output behaviour).
- **Schlesinger et al. (1979)**, *Terminology for model credibility*.
- **Banks, Carson, Nelson & Nicol**, *Discrete-Event System Simulation* — standard textbook reference.
- **ASME V&V** committee standards — consult the domain-appropriate one when it exists: **V&V 10 / 10.1**
  (computational solid mechanics), **V&V 20** (CFD & heat transfer), **V&V 40** (medical devices).

Loop-context practices in §5–6 are distilled from recent physical-science work — AutoTurb; an
LLM-as-mechanical-designer + FEM study; and meta-designing quantum experiments. The venue/year/arXiv
details for these are **unverified** (e.g. AutoTurb ≈ arXiv:2410.10657) and recorded only as leads.
Treat all of these as starting points; **before citing any of them in a report, verify the exact
details against the source itself** (`cite-check`).
