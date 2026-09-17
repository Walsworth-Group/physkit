---
name: model-selection
description: >-
  Compare and discriminate competing physical models (campaign archetype I).
---

# model-selection — choose the explanation, honestly

Some campaigns decide which mechanism is true rather than optimize a number. Given competing models or
hypotheses, this skill ranks them on the evidence, states the strength of the ranking, designs the
experiment that would settle it when one is needed, and states when no candidate is adequate. It is
archetype I. It pairs with `frame-problem`, which enumerates the physics the competing models embody, and
`verify`, which certifies the verdict.

The deliverable is a decision between explanations, with its strength and scope, not a single best-fit
curve. A model that wins by a narrow margin, or wins only because its rivals were misspecified, is not a
confident answer. Report the margin and its cause.

## Two modes

### Static — compare models on fixed data
When the data are in hand and the task is to rank the models:
- Score by evidence, penalizing complexity. Use the marginal likelihood / Bayes factor, cross-validated
  predictive performance, or an information criterion (AIC/BIC/WAIC). Each embodies Occam: a simpler model
  that fits comparably wins, because extra flexibility buys fit without buying truth. A change that raises
  raw fit error cannot be overfitting; distinguish the two.
- State the priors and assumptions. Bayes factors depend on the priors over each model's parameters. Report
  them, and check sensitivity to reasonable alternatives. A conclusion that flips under a defensible prior
  change is not robust.
- Report the comparison with uncertainty, not a bare "model B wins": the posterior odds, the
  cross-validation spread, and how decisive the margin is.
- Interrogate the residuals of the front-runner (`verify`). Structured residuals mean even the best
  candidate has unaccounted-for physics: expand the set rather than crown it.

### Active — design experiments to discriminate (expensive/sequential)
When discriminating requires new, costly experiments, compose `experiment-design` (archetype H) with a
discrimination utility:
- Measure where the models disagree most. The informative experiment is where the candidates predict
  different outcomes, not where they already agree: T-optimality, maximum expected change in the model
  posterior, or mutual information between outcome and model identity.
- Maintain a calibrated posterior over models and over each model's parameters. Update it as each
  experiment lands. Stop when one model is decisively favored or returns diminish.
- Inherit H's disciplines: surrogate and posterior calibration is cardinal, budget tracking, benchmarking
  against naive sampling. For hardware, inherit archetype E's safety and drift rules.

## The honest-set discipline (the failure mode that matters most)
The true model may lie outside the candidate set. This is model-form error, and it is how model selection
most often misleads.
- Include a flexible "none-of-the-above" alternative in the set: a more expressive or non-parametric model.
  The set must be able to register that no candidate is adequate.
- A best-but-still-poor fit is a signal to expand the set, not a winner. Judge absolute adequacy, not only
  relative ranking: does the front-runner explain the data, within its uncertainty?
- Do not let one model's misspecification masquerade as discrimination. A rival can lose because it was
  implemented badly rather than because it is wrong. Rule out the implementation with a `debug` or `verify`
  pass on each candidate before declaring a mechanism refuted.
- Test where the models are distinguishable, not in a degenerate regime. A negative result measured where
  the candidates predict the same outcome proves nothing: comparing a stiff and a soft magnet only in
  saturation, where both predict zero canting, cannot separate them. Before writing off a hypothesis,
  confirm the experiment sat in the regime where the models diverge. Active mode's "measure where they
  disagree most" selects that regime.

## Credit the mechanism, not just the metric
A model-selection result is explanatory: the win is a recovered understanding of why the system behaves as
it does, and it updates the project overview (`PROJECT.md`). Credit the mechanism, the parameter values it implies, and the
predictions it newly makes, not the fact that it scored highest. A descriptive "B fits better" is weaker
than an explanatory "B fits better and implies effect X, which was then observed."

## Composition
- `frame-problem` supplies the candidate models (the competing physics inventories) and the a-priori
  expectations each implies.
- `experiment-design` (archetype H) is the active-mode engine for choosing discriminating experiments.
- `verify` certifies the verdict: confirm the margin is real, not a prior artifact, recompute the evidence,
  run the anti-overfitting and residual-structure checks, and state what is decided, what is still open,
  and over what experimental range.
- `record-decision` captures why a model was selected and the conditions and priors it rests on. `report`
  documents the comparison, the evidence, and the recovered mechanism with its uncertainty.
- `new-campaign` scaffolds archetype I. A campaign may pull H and I together (actively discriminate), or
  either alone.

## Before you trust the verdict — checklist
- [ ] Models scored by an evidence or predictive criterion that penalizes complexity (Occam), not by raw fit.
- [ ] Priors and assumptions stated; the conclusion is robust to reasonable prior and criterion changes.
- [ ] The front-runner is absolutely adequate (residuals unstructured), not only relatively best.
- [ ] Any hypothesis written off was tested in a regime where the models are distinguishable, not a degenerate regime where both predict the same outcome.
- [ ] A flexible "none-of-the-above" was in the set; model-form error considered.
- [ ] Each candidate's implementation was checked, so a loss reflects the model, not a bug.
- [ ] (Active mode) experiments targeted maximum model disagreement; the model posterior is calibrated; a decisive stop was used.
- [ ] The result is reported as a decision with its strength, scope, and the recovered mechanism, and independently verified.
