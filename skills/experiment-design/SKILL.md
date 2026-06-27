---
name: experiment-design
description: >-
  Choose which experiment, measurement, or simulation to run NEXT to learn the most per costly evaluation —
  active / optimal / sequential experimental design. Use when the campaign's core loop is deciding what to
  sample next rather than improving a fixed model: Bayesian optimization, active learning, adaptive
  sampling, a self-driving/autonomous lab, design-of-experiments, or "which experiment is most informative
  now". It serves two objectives with the same machinery — (a) find an optimum, and (b) estimate parameters
  to a target precision — by maintaining a calibrated surrogate or posterior, picking the next experiment
  (or batch) via an acquisition/information utility, tracking the evaluation budget, and stopping when the
  posterior is decisive. (To DISCRIMINATE between competing models/hypotheses, see model-selection /
  archetype I, which composes this skill's active machinery with a discrimination utility.) This is the
  operational doctrine for campaign archetype H; composes verify, correctness-suite, and the
  expensive-evaluation protocol.
---

# experiment-design — spend each costly experiment on the most informative question

When evaluations are expensive (a long simulation, an instrument run, a synthesis-and-characterize cycle),
the highest-leverage decision is not *how* you model the system but *what you measure next*. This skill runs
that loop: keep a probabilistic belief about the system, and at each step choose the experiment that most
reduces what you don't yet know — toward an **optimum** or toward **precise parameters**. It is
**archetype H**, the natural home for the autonomous-lab / Bayesian-optimization style of campaign.
(Choosing experiments to **decide between competing models** is the closely-related archetype I,
`model-selection`, which reuses this loop with a discrimination utility.)

Two objectives share one engine and differ only in the utility you maximize. (A third — discriminating
between models — is **archetype I / `model-selection`**, which reuses this same machinery with a
disagreement utility; a campaign can pull both H and I.)
| Objective | Utility to maximize | Classic form |
|---|---|---|
| **Find an optimum** | expected improvement toward the optimum | EI · UCB · Thompson sampling · knowledge-gradient |
| **Estimate parameters** | expected reduction in parameter posterior uncertainty | D-/A-optimality · expected information gain |

---

## The loop
```
Build a calibrated belief → then repeat:
  1. MODEL     — maintain a surrogate over the objective (GP / Bayesian NN / ensemble) and/or a posterior
                 over parameters and over the competing models. Calibration is everything (see below).
  2. UTILITY   — pick the objective (optimum / parameters) and its acquisition/information utility.
                 (Discriminating models instead? compose `model-selection` / archetype I.)
  3. SELECT    — choose the next experiment (or a BATCH, for parallel runs) maximizing the utility, subject
                 to feasibility/cost/safety constraints. Use established BO/OED tooling for the inner
                 optimization — don't hand it to an LLM (LLMs are weak at numerical acquisition optimization).
  4. RUN       — execute the (expensive) experiment; record the outcome with its uncertainty.
  5. UPDATE    — condition the surrogate/posterior on the new datum; recompute the model posterior.
  6. STOP?     — when the posterior is decisive (parameter CI tight enough, or one model dominates), the
                 optimum has converged, or returns diminish — not at a fixed budget burned blindly.
```

## Calibration is the cardinal discipline
**A miscalibrated belief misallocates every subsequent experiment** — this is the central failure mode of
the whole archetype, more than the choice of acquisition function.
- **Validate the surrogate/posterior's predictive uncertainty**, not just its mean: check coverage (do
  ~68% of held-out points fall in the 1σ band?), and recalibrate if not. An overconfident surrogate stops
  exploring; an underconfident one never exploits.
- **Account for noise** (and heteroscedasticity): separate observation noise from model uncertainty;
  replicate where the signal is near the noise floor before trusting a point.
- **Don't reward-hack the surrogate.** The selection will exploit surrogate error — periodically
  cross-check apparent optima against the true evaluator / higher fidelity, exactly as in archetypes C/D/G.

## Discriminating between models? → archetype I
If the goal is to decide *which competing model/hypothesis is true* (not to optimize or estimate within one
model), that is **`model-selection` / archetype I**. When the discriminating experiments are themselves
expensive and must be chosen sequentially, archetype I **composes this skill** — same surrogate/posterior
loop, but the utility rewards experiments where the candidate models **disagree most** (T-optimality /
expected change in the model posterior). A campaign can run H and I together (actively design experiments to
discriminate) or either alone.

## Spend the budget well
Follow `docs/protocols/expensive-evaluation.md`: count evaluations as a first-class metric and
**benchmark sample-efficiency against random / grid / a classical optimizer** — active design has to *earn*
its complexity by beating space-filling. Pre-screen with a cheap proxy where one exists (validate the proxy
against the true evaluator first). Use a diminishing-returns / decision-theoretic stop.

## Cautions
- **Surrogate miscalibration** (above) — the dominant failure.
- **Greedy myopia.** One-step acquisition can be short-sighted; use a lookahead / batch-aware utility where
  the cost of a wasted experiment is high.
- **Premature exploitation / collapse** — the loop hammering one region and missing the global structure;
  diversity-aware or explicitly explorative acquisition guards against it.
- **Constraint and safety handling** — for a hardware loop, inherit archetype E (hard safety limits as
  constraints, confirm irreversible actions, interleave against drift). For simulation, inherit the V&V
  doctrine for the evaluator.
- **The acquisition function itself can be a lever to discover** (archetype G / FunBO-style) — but treat
  "this learned acquisition beats a standard one" as a hypothesis to verify, not assume.

## Composition
- **`new-campaign`** scaffolds archetype H; the FROZEN evaluator/measurement + the objective are the
  campaign's metric; the candidate model set + parameterization come from `frame-problem` / `PHYSICS.md`.
- **`verify`** certifies the recommended optimum / parameter estimate / winning model — re-evaluate at the
  recommendation, confirm it generalizes, and (for discrimination) confirm the margin is real, not a prior
  artifact.
- **`correctness-suite`** guards the surrogate/evaluator and the acquisition implementation.
- **`docs/protocols/expensive-evaluation.md`** governs the budget; hardware → archetype E; sim evaluator →
  `SIMULATION_VALIDATION.md`.
- **`report`** documents the recommended design/parameters/model with uncertainty and the experiment trail.

## Before you trust the recommendation — checklist
- [ ] The objective (optimum / parameters / discrimination) and its utility are stated explicitly.
- [ ] The surrogate/posterior is **calibrated** (predictive coverage checked); noise handled.
- [ ] Sample-efficiency benchmarked vs random/grid/classical — active design beat space-filling.
- [ ] Apparent optima cross-checked against the true evaluator (no surrogate reward-hacking).
- [ ] A principled stop (decisive posterior / converged optimum / diminishing returns), not a blind budget burn.
- [ ] The recommendation is independently verified (`verify`); uncertainty reported, never a bare point.
