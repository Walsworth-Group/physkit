---
id: uncertainty-and-error-budgets
kind: reference
layer: operating
load: on-demand
frozen: false
addresses: [2, 5, 1]
status: active
---

# Uncertainty & error budgets — a number without an uncertainty is not a measurement

The deliverable of an experiment is a value and its uncertainty. The uncertainty is what makes the number
comparable, falsifiable, and honest. Most wrong conclusions from careful experiments come from an
underestimated or mis-typed uncertainty, not from a wrong central value: a statistical error quoted where a
systematic dominates, or error bars that exclude whatever moved between sessions. This is the discipline of
getting the uncertainty right.

## 1. Statistical vs systematic — the split that governs everything

- **Statistical (random):** scatter that averages down as 1/√N: shot and spin-projection noise, thermal and
  readout noise. Estimate it from the spread of repeated measurements, or from the noise model.
- **Systematic:** a bias that does not average down: a calibration offset, a drift, a misalignment,
  cross-talk. Measuring faster or longer does not reduce it. Bound it by other means (see
  `systematic-errors.md`).
- √N buys down statistics, never systematics. A measurement is systematics-limited once its systematic
  budget exceeds its statistical error; past that point more averaging is wasted (§5, the drift wall).
- Quote them separately: `value ± stat ± sys`. Collapsing the two hides which one running longer would
  improve and which one needs a redesign.

## 2. The error budget — the artifact that makes uncertainty auditable

The central deliverable is a table with one row per uncertainty source: the source, its magnitude in the
units of the result, whether it is stat or sys, how it was estimated (measured / propagated / bounded /
assumed), and any correlation to other rows. Building the table forces enumeration, and an unlisted source
is an unbounded one. The total is the combination of the rows required by §4, not a single unsupported ±.

| source | value ± | stat/sys | how estimated | correlated with |
|---|---|---|---|---|
| photon shot noise | … | stat | noise model / measured | — |
| bias-field drift | … | sys | monitored + bounded | calibration |
| calibration scale | … | sys | traced to standard | field drift |

A number quoted without an error budget carries no defensible uncertainty.

## 3. Propagation of uncertainty

For `y = f(x₁,…,xₙ)`, to first order
`σ_y² = Σᵢ (∂f/∂xᵢ)² σ_xᵢ² + 2 Σᵢ<ⱼ (∂f/∂xᵢ)(∂f/∂xⱼ) cov(xᵢ,xⱼ)`.

- The partials are the sensitivity analysis. The term with the largest `(∂f/∂xᵢ)·σ_xᵢ` dominates; spend the
  effort there, not on the smallest.
- Linear propagation fails when `f` is strongly nonlinear across ±σ, when σ is large, or near a physical
  boundary. In those cases, Monte-Carlo propagate: sample the inputs from their distributions and histogram
  the output.
- Check the propagated σ dimensionally (`dimensional-analysis`). It must carry the units of `y`.

## 4. Combining — quadrature, and its two traps

Independent sources add in quadrature: `σ_tot = √Σ σᵢ²`. Two traps:

- **Correlation.** Correlated sources do not add in quadrature. A single calibration feeding two terms is
  fully correlated and adds linearly; ignoring the correlation can under- or over-state the total by a
  large factor.
- **Double-counting.** A fluctuation already inside the statistical scatter is not also a separate
  systematic line. Decide where each source lives once.
- **Coverage.** State whether a bar is k=1 (1σ, ~68 %) or k=2 (~95 %). Never combine or compare a 1σ with a
  2σ number.

## 5. Averaging, and where it stops helping — the Allan deviation

White noise averages as `σ(τ) ∝ 1/√τ`, but real instruments do not stay white: 1/f (flicker) noise flattens
the curve, and drift makes the curve rise again past some integration time. The Allan deviation `σ_A(τ)`,
computed against averaging time τ, shows the white-noise slope, the flicker floor, and the drift wall: the
optimal integration time `τ_opt` beyond which averaging worsens the result. Integrate to `τ_opt`, not
further, and re-zero or re-calibrate on the drift timescale (see `calibration-and-drift.md`).

## 6. Goodness of fit — what reduced χ² tells you (and doesn't)

For a fit weighted by proper uncertainties, reduced chi-square `χ²/dof` should be ≈ 1.
- `χ²/dof ≫ 1` → the model is wrong, or the uncertainties are underestimated (often a missing systematic).
- `χ²/dof ≪ 1` → the uncertainties are overestimated, or correlated points were counted as independent.

`χ²/dof` is a consistency check between the model and the error bars. It does not replace interrogating
residual structure (`verify` — the nature of the error). A perfect χ² with structured residuals is still a
bad fit; a good fit needs both.

## 7. Reporting the uncertainty honestly

- **Never a bare number.** Quote `value ± uncertainty` with the coverage (1σ / 95 %) and the stat/sys
  split.
- **Significant figures.** The uncertainty sets the precision: 1–2 sig figs on the uncertainty, with the
  value's last digit matched to it. Round at the end, never mid-propagation.
- **Bounded or asymmetric quantities.** A quantity near zero or near a physical limit gets an interval or a
  limit, not a symmetric ±.
- An uncertainty is part of the number, so it falls under `report`'s *honest band* and *label every number
  by kind* rules.

## The two-question reflex (before you quote an uncertainty)

1. **What dominates the budget, and is it stat or sys?** If systematic, running longer will not help.
2. **Was the thing that actually moved between repeats or sessions included?** Session-to-session scatter
   is often a drift or a recalibration, which is a systematic and must be budgeted as one.

## Checklist

- [ ] Every source enumerated in an error-budget table (stat/sys tagged, estimation method noted)?
- [ ] Dominant source identified from the sensitivity (partials × σ)?
- [ ] Correlations handled (not blind quadrature); nothing double-counted; coverage stated?
- [ ] Averaging taken to `τ_opt`, not past the drift wall (Allan deviation)?
- [ ] reduced-χ² ≈ 1 and residuals unstructured?
- [ ] Reported as `value ± stat ± sys` with stated coverage, not a bare number?

## Composition

`verify` grades whether the uncertainty is defensible and interrogates residual structure ·
`report` consumes the budget as the "honest band" · `signal-extraction-pitfalls.md`
guards the raw statistics feeding it · `systematic-errors.md` bounds the systematic rows ·
`dimensional-analysis` checks the propagated units · `noise-and-sensitivity.md` supplies the
a-priori statistical floor.

## Sources

Standard measurement-science methodology; nothing here is novel. The contribution is codifying it into the
kit's workflow. Canonical references: the GUM (JCGM 100:2008, *Guide to the Expression of Uncertainty in
Measurement*); Taylor, *An Introduction to Error Analysis* (2nd ed., University Science Books, 1997);
Bevington & Robinson, *Data Reduction and Error Analysis for the Physical Sciences* (3rd ed., McGraw-Hill,
2003); Allan, "Statistics of Atomic Frequency Standards" (*Proc. IEEE* **54**, 1966, 221–230) for the Allan
deviation.
