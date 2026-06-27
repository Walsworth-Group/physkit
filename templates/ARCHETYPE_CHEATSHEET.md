# Campaign Archetype Cheat-Sheet

A reference for the `new-campaign` setup skill (and the researcher) when filling
`campaign/docs/program.md.tmpl`. Most physical-science autoresearch campaigns fall into a small set of
recurring archetypes (catalogued below as A–I). A campaign may match **none, one, or several** — determine which **apply**, and **inherit and merge** the
metric/lever/FROZEN/failure-mode guidance from each relevant one (don't force a single best fit). If
several apply *in sequence* rather than at once, that's a multi-stage campaign (see the note at the
end). Then specialize the placeholders. Four of the archetypes are exemplified by real campaigns in
`examples/program-files/`; the generic `program.md` template is the union of their rigor disciplines. The
hardware-in-the-loop archetype (**E**) is fundamentally different from the compute-only ones and needs
special treatment — see its section.

This cheat-sheet is the *selection guide*; the deeper doctrine lives in [`docs/PRINCIPLES.md`](../docs/PRINCIPLES.md)
(§5 Simulation rigor & tooling, §6 Experiment & hardware, §9 Coding). Expand it freely as new
archetypes and patterns appear.

> This file is **guidance for the setup skill** — it is NOT copied into a generated campaign (though
> the skill may copy a tailored extract into `docs/` if the user wants it retained).

---

## A. Iterative fit / decoder optimization
*Real example: `examples/program-files/program_residual.md` (NV residual minimization).*

- **PRIMARY metric:** a scale-invariant goodness-of-fit on REAL data (R² / residual / log-likelihood /
  χ²), FROZEN. The model may relax to a continuous form, but the score evaluates the final
  (often quantized) answer.
- **LEVERS:** registration/alignment of model to data · forward **parameters** (low-order, physical:
  standoff, PSF, angles, amplitude) · preprocessing (bias/mean removal, normalization, crop, denoise)
  · the decoder/optimizer/**loss** (the loss MAY differ from the frozen metric).
- **Usually FROZEN:** the scoring formula; the forward **physics equations** (tune their parameters
  only); geometry/ordering; the experimental data.
- **Failure modes / guardrails:** metric gamed by preprocessing that removes *real* signal (watch a
  ceiling, not just the primary); gap-to-ceiling overfitting where a freer decoder fits the null space
  → synthetic SANITY guardrail + theoretical ceilings; sim-to-experiment gap (SANITY is
  necessary-not-sufficient); levers that must co-vary (a forward-angle change needs a registration
  re-fit — test the pair).

## B. Forward-model / simulation improvement
*Real example: `examples/program-files/program_forward.md` (NV forward model).*

- **PRIMARY metric:** residual between the forward-projected prediction of a KNOWN configuration and
  measured anchors, FROZEN scorer. Here the **forward CODE is the mutable target** — this inverts what
  is frozen in archetype A.
- **LEVERS:** the forward physics core (finite thickness, k-space kernel, demag, edge treatment) · the
  observation/signal model (projection convention, PSF, ensemble averaging) · geometry treatment
  (sub-pixel, volume integration) · low-order nuisance params fit to anchors · numerics. **Split
  numerics:** a speed-only refactor MUST be output-preserving; accuracy-changing numerics are scored
  like physics.
- **Usually FROZEN:** the scoring formula; the data + anchor measurements; the KNOWN ground-truth
  configuration; catalog geometry/ordering.
- **Failure modes / guardrails:** nuisance-overfitting of a few anchors → require agreement across
  **multiple independent conditions** (e.g. two standoffs — a win at one condition only is suspect) +
  parsimony + physical-range checks on every fitted param; convention/sign slips (the #1 forward bug)
  → self-tests + a linearization/validation check that must still pass; **code snapshot MANDATORY**
  because the code itself changes.
- **Why this archetype is more powerful than it looks (note for future agents):** building a forward
  model that reproduces experimental data forces you to *characterize every significant physical effect
  and experimental artifact* in the data — it is one of the best ways to genuinely understand a dataset,
  not just fit it. It is also a natural **first stage** for an ML or targeted-search campaign, because
  those score candidates *through* the forward problem. In that case, run **two sequential loops**: loop
  1 optimizes the forward model/metric until it is trustworthy; loop 2 (archetype A / C / D) optimizes
  the decoder, design, or ML architecture against that now-frozen forward. See the multi-stage note below.

## C. Generative design
*No real example in the kit yet — e.g. pulse-sequence design, permanent-magnet lattices, metamaterials,
photonic structures.*

- **PRIMARY metric:** a figure of merit on the DESIGNED object via a FROZEN evaluator/simulator (field
  uniformity/gradient, sequence fidelity/robustness, transmission, etc.). Bound it a priori with a
  physical or theoretical limit.
- **LEVERS:** the design parameterization (geometry/placement/materials, or pulse timings/phases/
  amplitudes) · the search strategy (gradient / evolutionary / Bayesian / RL) · constraints & penalty
  weights · objective trade-off weights.
- **Usually FROZEN:** the evaluator/simulator and its scoring; physical & fabrication constraints; the
  independent validation forward model.
- **Failure modes / guardrails:** designs that exploit simulator inaccuracy (**reward hacking**) →
  independent high-fidelity re-evaluation + manufacturability/feasibility checks; overfit to a single
  operating point → require **robustness across conditions** (temperature, detuning, tolerances);
  constraint violations masked by soft penalties → a HARD feasibility gate separate from the soft
  objective.
- **Simulation rigor & tooling (the make-or-break of this archetype):** the entire campaign rests on the
  evaluator/simulator, so it must be *rigorous and reliable before any design is trusted* — validate it
  against analytic limits, conservation laws, symmetries, and published benchmarks, and demonstrate
  numerical convergence (refine grid/timestep/tolerance until the answer stops moving). Before writing a
  simulator from scratch, **survey existing packages/libraries** — prefer a mature, well-tested, ideally
  free/open-source tool, and explore the options carefully before committing; reinventing a solver is
  slow and a fresh source of bugs. Record what you chose and why. (Full checklist: `docs/PRINCIPLES.md` §5.)

## D. ML-model training / classifier
*Real example: `examples/program-files/program.md` (per-island ASI classifier).*

- **PRIMARY metric:** a held-out test metric with EXACT labels (balanced accuracy / F1 / MSE), FROZEN.
  Report the **hard-subgroup split** — a mean propped up by an easy subgroup is not a win.
- **LEVERS:** architecture (width/depth/attention/graph) · the input front-end/featurization · the
  loss (auxiliary physics terms, class weighting, focal) · training (lr/schedule/optimizer/batch/noise
  curriculum/augmentation). The data-distribution / sampler mixture is a **DATA choice** — hold fixed.
- **Usually FROZEN:** the scoring math; the forward map / label-generation physics; geometry/ordering;
  the fixed train/val/test split.
- **Failure modes / guardrails:** train/val overfit → a noisy-val guardrail + select the best
  checkpoint on it; sim-to-real overfit → a co-tracked real-data guardrail; easy-subgroup inflation →
  the subgroup split; capacity-vs-data confusion → ablations; hard epoch/compute caps.
- *Variant — surrogate / emulator building:* training a fast model to replace an expensive simulator is
  this archetype with the simulator's outputs as the labels; the key extra risk is that the surrogate's
  errors mislead whatever search later consumes it, so validate it against the true simulator on held-out
  points (cf. archetype C reward-hacking).

## E. Hardware-in-the-loop / experimental control
*No real example in the kit yet — e.g. closed-loop tuning of an instrument: pulse calibration, field or
voltage setpoints, sample conditions, alignment, readout optimization. **This archetype needs special
treatment** — the "experiment" is a real measurement on real hardware, not a compute job.*

- **PRIMARY metric:** a figure of merit read directly off the instrument (signal contrast, coherence
  time, gate/readout fidelity, SNR, count rate, yield), FROZEN. It carries BOTH statistical and
  systematic error — never act on a single read; average and track the spread.
- **LEVERS:** the control parameters (timings, amplitudes/phases, field/voltage setpoints, flow/temp,
  alignment) · the measurement protocol (averaging, integration time, sequencing) · calibration routines.
- **Usually FROZEN:** the safety limits (hard constraints, NOT levers); the scoring definition; the
  measured reference/ground truth; the apparatus itself (tune settings, don't rebuild the rig
  mid-campaign without sign-off).
- **Special treatment — what makes this different from the compute archetypes:**
  - **Runs are EXPENSIVE and often IRREVERSIBLE** (the opposite of the cheap-compute archetypes). You
    cannot replicate for free, so design experiments deliberately (a design-of-experiments mindset) and
    **pre-screen candidates with a forward model / digital twin** where one exists (a great use of
    archetype B as a first stage).
  - **Respect hardware limits as hard constraints, and confirm before any hard-to-reverse or destructive
    action** (sample/instrument damage, consuming a limited resource). A setpoint outside the safe range
    is out of scope, never a lever.
  - **Drift is the default enemy:** interleave/randomize comparisons (A-B-A) so calibration drift isn't
    read as an effect; keep key parameters fixed and fair between compared runs.
  - **Rule out measurement artifacts before claiming a real effect;** re-check calibration/baseline first.
  - **Log the full instrument + environment state every run** ("thermostat in the box").
- **Failure modes / guardrails:** artifacts masquerading as signal → null/control measurements + repeats;
  drift between comparisons → interleaving + re-measuring the reference; overfitting to one session's
  conditions → confirm across sessions; unsafe excursions → a hard safety gate + human confirmation.
  (The generic `program.md` carries an optional "Hardware safety & irreversibility" block for this
  archetype; full doctrine in `docs/PRINCIPLES.md` §6.)

## F. Inverse problem / parameter estimation (with uncertainty)
*Real example: `examples/program-files/program_ASI_CNN.md` (reconstruct the magnetization M from a single
NV field projection).*

- **PRIMARY metric:** fidelity of the **recovered quantity** (a parameter, field, or distribution) to
  truth. Truth is usually unknown, so use a FROZEN **validated composite** score on real data that is
  robust to the problem's ill-posedness — **not raw forward-residual**, which rewards degenerate/empty
  solutions that fit the data through the null space. **Report uncertainty** on the recovered quantity
  (error bars / posterior spread), not just a point score.
- **LEVERS:** the **regularization / prior** that makes the ill-posed problem well-posed (Tikhonov,
  sparsity, total-variation, or a learned prior) · the reconstruction method (least-squares,
  MAP/Bayesian/posterior sampling, unrolled or learned decoders) · conditioning of the forward operator
  (e.g. multi-angle / multi-standoff stacking to raise the recoverable rank) · preprocessing.
- **Usually FROZEN:** the scoring/validation metric; the forward operator's physics (its *parameters* may
  be a lever — see A/B); the data and any known ground truth.
- **Failure modes / guardrails:** the **null space** — many solutions fit the data equally well, so a low
  residual is NOT a correct reconstruction → score with a metric that penalizes implausible structure
  (support / locality / physical plausibility) + a synthetic guardrail with KNOWN truth; over-
  regularization that erases real signal → watch a recoverability/rank ceiling; overfitting to a small,
  correlated real set → a co-tracked noisy-synthetic guardrail; and **always report uncertainty** — a
  recovered value without an error bar is half a result.

## G. Program / equation / heuristic discovery (LLM-in-the-loop search)
*No real example in the kit yet — e.g. discovering a turbulence closure, a symbolic law, a heuristic, an
acquisition function, or a control policy. **This archetype is fundamentally different from A–F:** the
object optimized is an **interpretable artifact the LLM generates** (a program / equation / design rule),
not a parameter set; the "experiment" is a generate→evaluate→reflect step in a search loop. The operational
doctrine lives in the **`discovery-loop` skill** — this is the selection-guide summary.*

- **PRIMARY metric:** a figure of merit on the **discovered artifact** via a FROZEN evaluator, on a
  **representative, heterogeneous benchmark** (never solely self-chosen functions). Track **best score vs
  number of evaluations** (budget is a first-class metric), and the outcome distribution/stability over
  repeats — not just the best run.
- **LEVERS (the discovery design axes):** the **object evolved** (the genome — equation/code/heuristic/
  design/controller; representation often dominates the optimizer) · the **search engine** (population/
  island · tree/MCTS/PUCT · neighborhood — pick by landscape) · the **feedback memory** (prompt →
  reflections/"verbal gradients" → an evolving concept library; heavier = more capable + more cost/
  contamination) · the **reflection mode** · **domain-prompt richness** (a lever to *test*, not a free win) ·
  *(advanced)* generator self-improvement. **Generation is function-only** — the LLM writes only the mutable
  lever functions.
- **Usually FROZEN:** the evaluator/scoring and the benchmark/data; the **harness + data acquisition**
  (function-only generation keeps these READ-ONLY); known ground truth.
- **Failure modes / guardrails:** reward-hacking the evaluator → independent higher-fidelity re-eval +
  feasibility/convergence gate + dual direct+downstream objective; **memorization/contamination** (LLMs
  regurgitate) → black-box prompting + synthetic un-memorizable re-tests; **cosmetic novelty** → a
  novelty/equivalence check; **complexity creep** → monitor the complexity trajectory + parsimony *during*
  search; **over-prompting** hurts on rugged landscapes; crediting the apparatus → ablate vs a direct-LLM
  baseline + a classical optimizer (BO/RL/NSGA-II) + multi-LLM robustness. **LLMs are weak at raw numerical
  optimization** — use them for flexibility/exploration/interpretable structure, and consider
  explore-with-LLM-then-exploit-with-classical.
- **Discovery-specific rigor (the make-or-break):** **discover-then-certify** — the search proposes, an
  *independent* method certifies; **state certified vs conjectured** scope. Re-discover the known SOTA as a
  validation gate; require **generalization/extrapolation across regimes**; **credit explanatory (mechanism)
  over descriptive (metric) discovery**; deliver an **interpretable artifact** and extract its design rule
  into `PHYSICS.md`. (Full loop, memory modes, and checklist: the `discovery-loop` skill;
  simulator-scored search: `docs/SIMULATION_VALIDATION.md` §5; budget: `docs/protocols/expensive-evaluation.md`.)

## H. Active / optimal experimental design (sequential experiment selection)
*No real example in the kit yet — e.g. Bayesian optimization of a material/process, active learning, an
autonomous/self-driving lab, design-of-experiments. The "experiment" is a costly evaluation, and the loop's
core decision is **which experiment to run next**, not how to improve a fixed model. Operational doctrine:
the **`experiment-design`** skill.*

- **PRIMARY metric:** the **objective being optimized** (figure of merit) or the **target parameter
  precision** (posterior uncertainty), via a FROZEN evaluator/measurement. Track the **evaluation budget**
  as a first-class number and benchmark sample-efficiency vs random/grid/a classical optimizer.
- **LEVERS:** the **next experiment(s) to run** (the point/batch chosen by the acquisition/information
  utility — EI/UCB/Thompson/knowledge-gradient for an optimum; D-/A-optimality / expected information gain
  for parameters) · the surrogate/posterior model choice · the explore–exploit / batch strategy.
- **Usually FROZEN:** the evaluator/measurement and its scoring; the design space and feasibility/safety
  constraints; the data already collected.
- **Failure modes / guardrails:** **surrogate miscalibration** (the cardinal failure — a miscalibrated
  belief misallocates every later experiment; check predictive coverage, recalibrate) → validate the
  surrogate's uncertainty, not just its mean; **reward-hacking the surrogate** → cross-check apparent optima
  on the true evaluator; **greedy myopia** and **premature collapse** → lookahead / diversity-aware
  acquisition; **noise** → replicate near the noise floor. For a hardware loop inherit archetype E; for a
  simulation evaluator inherit `SIMULATION_VALIDATION.md`. *(LLMs are weak at the numerical acquisition
  optimization — use established BO/OED tooling for the inner loop.)*

## I. Model selection / hypothesis discrimination
*No real example in the kit yet — e.g. deciding which of several mechanisms/theories explains the data. The
deliverable is a **decision between explanations + its strength and scope**, not a best-fit curve.
Operational doctrine: the **`model-selection`** skill.*

- **PRIMARY metric:** model **evidence / posterior odds** — marginal likelihood / Bayes factor,
  cross-validated predictive performance, or an information criterion (AIC/BIC/WAIC) — each **penalizing
  complexity (Occam)**. Report the comparison **with uncertainty and the priors**, not a bare winner.
- **LEVERS:** the **candidate model set** (and each model's parameterization) · the comparison criterion +
  priors · in the **active** case, the **discriminating experiments** chosen (compose archetype H with a
  utility that rewards where the models DISAGREE most — T-optimality / expected change in the model
  posterior).
- **Usually FROZEN:** the scoring/evidence criterion; the data (and, in active mode, the frozen evaluator);
  known ground truth.
- **Failure modes / guardrails:** **the true model outside the candidate set** (model-form error — the
  failure that matters most) → include a flexible "none-of-the-above" alternative and judge **absolute
  adequacy** (front-runner residuals unstructured), not just relative ranking; **one model's
  misspecification masquerading as discrimination** → `debug`/`verify` each candidate's implementation
  before declaring a mechanism refuted; **prior sensitivity** → confirm the verdict survives reasonable
  prior changes; **descriptive-not-explanatory** → credit the recovered *mechanism* (update `PHYSICS.md`),
  not just the fit. A campaign can pull **H and I together** (actively design experiments to discriminate)
  or either alone.

---

## Cross-archetype constants (fill these the same way for ANY archetype)
These are settled doctrine in the generic `program.md` and apply regardless of archetype:
- ONE **frozen metric**; scoring math never changes mid-campaign.
- **Exp 000 baseline gate** = the floor + an end-to-end pipeline/convention validation.
- The **FROZEN / READ-ONLY / Mutable** code tripartition.
- **A-priori metric bounding** (predict before you run; an out-of-range result is a flag, not a win).
- **Statistical vs systematic** error separation; **replicate with seeds/perturbations**.
- **Independent adversarial verification** before any promotion or DISCOVERY.
- **Minimally-sufficient** model/design; add a parameter only if it generalizes + is motivated +
  beats the spread.
- **Markdown-primary** documentation; **save visualizations** of notable results; full reproducibility
  (config + scoreboard row + result JSON + figures + per-experiment code snapshot + input-data hash; tee
  stdout; never lose a number).
- **Simulation Verification & Validation** — most archetypes have a simulation component (forward models,
  synthetic data, evaluators, surrogates), so apply the V&V&UQ doctrine in `docs/SIMULATION_VALIDATION.md`;
  and **hardware safety / irreversibility** for hardware-in-the-loop campaigns (`docs/PRINCIPLES.md` §6).

## Multi-objective / multi-stage campaigns
Many complex goals are best done as **several sequential loops**, not one tangled campaign — optimizing
two things at once makes a win un-attributable, and **validating/improving on a simpler subcase first
usually yields a more powerful, better-validated final result.** Common patterns:
- **Forward model as the scoring backbone:** a forward model scores a downstream decoder, design search,
  or ML model — optimize the forward first (archetype B) until it is trustworthy, then optimize the
  thing built on it (A / C / D) against that now-frozen forward.
- **Idealized → real:** optimize on simpler/idealized physics first (a baseline + a solid procedure
  while the physics is simple), then carry it to the real system.
- **A characterization stage the user executes:** a stage can output an **experimental protocol the
  user carries out** (e.g. a gauss-meter measurement), whose results feed the next stage.

*Example — design a permanent-magnet array from measured surface fields (3 loops):* (1) optimize the
arrangement with *idealized* magnets — a baseline for (3) plus a solid optimizer while the physics is
simple; (2) design a protocol the user runs to measure their real magnets' imperfections; (3) optimize
the arrangement of the *imperfect* magnets, building on (1) and the data from (2).

The setup skill plans and proposes the staging, and gives each loop its own `program_<NAME>.md`,
`configs_<NAME>/`, `results_<NAME>/`.
