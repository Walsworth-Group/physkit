---
name: model-selection
description: >-
  Decide which of several competing physical models or hypotheses best explains the data — and, when needed,
  design the experiments that best discriminate them. Use when the goal is to choose or rank explanations
  rather than optimize within one: comparing candidate mechanisms/theories, "which model fits best without
  overfitting", Bayesian model comparison, hypothesis discrimination, or designing a decisive
  discriminating experiment. Static mode compares models on fixed data via marginal likelihood / Bayes
  factors / cross-validated predictive performance / information criteria, penalizing complexity (Occam) and
  reporting uncertainty and priors. Active mode (for expensive sequential experiments) composes
  experiment-design / archetype H with a utility that rewards experiments where the models DISAGREE most.
  Throughout it guards against the true model lying outside the candidate set (model-form error) and credits
  the recovered mechanism, not just the fit. This is the operational doctrine for campaign archetype I.
---

# model-selection — choose the explanation, honestly

Some campaigns aren't trying to optimize a number — they're trying to decide **which mechanism is true**.
Given competing models or hypotheses, this skill ranks them on the evidence, says how strongly, designs the
experiment that would settle it when one is needed, and stays honest about the possibility that none of the
candidates is right. It is **archetype I**, and it pairs naturally with `frame-problem` (which enumerated
the physics that the competing models embody) and `verify` (which certifies the verdict).

The deliverable is a **decision between explanations plus its strength and scope** — not a single best-fit
curve. A model that wins by a hair, or wins only because its rivals were misspecified, is not a confident
answer, and saying so is the point.

## Two modes

### Static — compare models on fixed data
When the data are in hand and you just need to rank the models:
- **Score by evidence, penalizing complexity.** Use the **marginal likelihood / Bayes factor**,
  **cross-validated predictive performance**, or an **information criterion** (AIC/BIC/WAIC) — each
  embodies **Occam**: a simpler model that fits comparably should win, because extra flexibility buys fit
  without buying truth. (A change that *raises* raw fit error cannot be overfitting — be precise about
  which is which.)
- **State the priors and assumptions.** Bayes factors depend on the priors over each model's parameters;
  report them, and check sensitivity to reasonable alternatives — a conclusion that flips under a defensible
  prior change is not robust.
- **Report the comparison with uncertainty**, not a bare "model B wins": the posterior odds / the
  cross-validation spread / how decisive the margin is.
- **Interrogate the residuals of the front-runner** (`verify`): structured residuals mean even the best
  candidate has unaccounted-for physics — a reason to expand the set, not to crown it.

### Active — design experiments to discriminate (expensive/sequential)
When discriminating requires new, costly experiments, **compose `experiment-design` (archetype H)** with a
discrimination utility:
- **Measure where the models disagree most.** The informative experiment is where the candidates predict
  *different* outcomes (T-optimality / maximize the expected change in the model posterior / mutual
  information between outcome and model identity) — not where they already agree.
- Maintain a **calibrated posterior over models** (and over each model's parameters); update it as each
  experiment lands; **stop when one model is decisively favored** or returns diminish.
- Inherit H's disciplines (surrogate/posterior calibration is cardinal; budget tracking; benchmark vs
  naive sampling) and, for hardware, archetype E's safety/drift rules.

## The honest-set discipline (the failure mode that matters most)
**The true model may lie outside your candidate set** — this is model-form error, and it is how model
selection most often misleads.
- **Include a flexible "none-of-the-above" alternative** (a more expressive or non-parametric model) so the
  set can register "none of these is adequate."
- A **best-but-still-poor** fit is a signal to **expand the set**, not a winner — judge absolute adequacy
  (does the front-runner actually explain the data, within its uncertainty?), not just relative ranking.
- **Don't let one model's misspecification masquerade as discrimination** — a rival can lose because it was
  implemented badly, not because it's wrong. Rule out the implementation (a `debug`/`verify` pass on each
  candidate) before declaring a mechanism refuted.
- **Test where the models are actually DISTINGUISHABLE, not in a degenerate regime.** A negative result
  measured where the candidates predict the *same* outcome proves nothing (e.g. comparing a stiff vs soft
  magnet only in saturation, where both predict zero canting). Before writing off a hypothesis, confirm the
  experiment sat in the regime where the models diverge — that is exactly what active mode's
  "measure where they disagree most" buys you.

## Credit the mechanism, not just the metric
A model-selection result is **explanatory**: the win is a recovered understanding of *why* the system
behaves as it does, which updates `PHYSICS.md`. Credit that — the mechanism, the parameter values it
implies, the predictions it newly makes — not merely that it scored highest. A descriptive "B fits better"
is weaker than an explanatory "B fits better *and* implies effect X, which we then observed."

## Composition
- **`frame-problem`** supplies the candidate models (the competing physics inventories) and the a-priori
  expectations each implies.
- **`experiment-design` (archetype H)** is the active-mode engine for choosing discriminating experiments.
- **`verify`** certifies the verdict: confirm the margin is real (not a prior artifact), recompute the
  evidence, run the anti-overfitting and residual-structure checks, and state **what is decided vs still
  open** and over what experimental range.
- **`record-decision`** captures *why* a model was selected and the conditions/priors it rests on;
  **`report`** documents the comparison, the evidence, and the recovered mechanism with its uncertainty.
- **`new-campaign`** scaffolds archetype I; a campaign may pull H **and** I (actively discriminate) or
  either alone.

## Before you trust the verdict — checklist
- [ ] Models scored by an evidence/predictive criterion that **penalizes complexity** (Occam), not raw fit.
- [ ] Priors and assumptions stated; the conclusion is robust to reasonable prior/criterion changes.
- [ ] The front-runner is **absolutely adequate** (residuals unstructured), not just relatively best.
- [ ] Any hypothesis written off was tested in a regime where the models are **distinguishable** (not a degenerate regime where both predict the same).
- [ ] A flexible "none-of-the-above" was in the set; model-form error considered.
- [ ] Each candidate's implementation was checked, so a loss reflects the *model*, not a bug.
- [ ] (Active mode) experiments targeted maximum model disagreement; the model posterior is calibrated; a decisive stop was used.
- [ ] The result is reported as a decision **with its strength, scope, and the recovered mechanism** — and independently verified.
