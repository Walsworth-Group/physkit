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

The deliverable of an experiment is not a value but a value **and its uncertainty** — the uncertainty is
what makes the number comparable, falsifiable, and honest. Most wrong conclusions from careful experiments
come not from a wrong central value but from an **underestimated or mis-typed uncertainty**: a statistical
error quoted where a systematic dominates, or error bars that don't include the thing that actually moved
between sessions. This is the discipline of getting the uncertainty right.

## 1. Statistical vs systematic — the split that governs everything

- **Statistical (random):** scatter that averages down as 1/√N — shot/spin-projection noise, thermal and
  readout noise. Estimated from the spread of repeated measurements (or from the noise model).
- **Systematic:** a bias that does **not** average down — a calibration offset, a drift, a misalignment,
  cross-talk. Measuring faster or longer does not help; it must be *bounded by other means* (see
  `systematic-errors.md`).
- The cardinal rule: **√N buys down statistics, never systematics.** A measurement becomes
  *systematics-limited* the moment its systematic budget exceeds its statistical error — past that point
  more averaging is wasted (§5, the drift wall).
- **Quote them separately:** `value ± stat ± sys`. Collapsing the two hides which one you could improve by
  running longer, and which one needs a redesign.

## 2. The error budget — the artifact that makes uncertainty auditable

The central deliverable is a **table with one row per uncertainty source**: the source, its magnitude *in
the units of the result*, whether it is stat or sys, **how it was estimated** (measured / propagated /
bounded / assumed), and any correlation to other rows. Building it forces enumeration — the source you
didn't list is the one that bites — and the total is the *correct* combination of the rows (§4), not a
single hand-waved ±.

| source | value ± | stat/sys | how estimated | correlated with |
|---|---|---|---|---|
| photon shot noise | … | stat | noise model / measured | — |
| bias-field drift | … | sys | monitored + bounded | calibration |
| calibration scale | … | sys | traced to standard | field drift |

A number quoted without an error budget is an *opinion* about its uncertainty.

## 3. Propagation of uncertainty

For `y = f(x₁,…,xₙ)`, to first order
`σ_y² = Σᵢ (∂f/∂xᵢ)² σ_xᵢ² + 2 Σᵢ<ⱼ (∂f/∂xᵢ)(∂f/∂xⱼ) cov(xᵢ,xⱼ)`.

- The partials **are** the sensitivity analysis: the term with the largest `(∂f/∂xᵢ)·σ_xᵢ` dominates — put
  your effort there, not on the smallest.
- **Linear propagation fails** when `f` is strongly nonlinear across ±σ, when σ is large, or near a
  physical boundary — then **Monte-Carlo propagate**: sample the inputs from their distributions and
  histogram the output.
- Check the propagated σ **dimensionally** (`dimensional-analysis`) — it must carry the units of `y`.

## 4. Combining — quadrature, and its two traps

Independent sources add in quadrature: `σ_tot = √Σ σᵢ²`. Two traps:

- **Correlated sources do NOT add in quadrature.** A single calibration feeding two terms is *fully
  correlated* and adds linearly; ignoring the correlation can badly under- or over-state the total.
- **Don't double-count.** A fluctuation already inside the statistical scatter is not *also* a separate
  systematic line. Decide where each source lives once.
- **State the coverage.** Is a bar k=1 (1σ, ~68 %) or k=2 (~95 %)? Never combine or compare a 1σ with a
  2σ number.

## 5. Averaging, and where it stops helping — the Allan deviation

White noise averages as `σ(τ) ∝ 1/√τ`, but real instruments don't stay white: 1/f (flicker) noise flattens
the curve, and **drift makes it rise again** past some integration time. The **Allan deviation** `σ_A(τ)`
diagnoses exactly this — computed vs averaging time τ it shows the white-noise slope, the flicker floor,
and the **drift wall**: the optimal integration time `τ_opt` beyond which averaging *worsens* the result.
This is the quantitative form of "instrument time is the scarce resource": integrate to `τ_opt`, not
forever, and re-zero / re-calibrate on the drift timescale (see `calibration-and-drift.md`).

## 6. Goodness of fit — what reduced χ² tells you (and doesn't)

For a fit weighted by *proper* uncertainties, reduced chi-square `χ²/dof` should be ≈ 1.
- `χ²/dof ≫ 1` → the model is wrong **or** the uncertainties are underestimated (often a missing
  systematic).
- `χ²/dof ≪ 1` → the uncertainties are overestimated, or correlated points were counted as independent.

It is a **consistency check between your model and your error bars** — *not* a substitute for interrogating
residual structure (`verify` — the *nature* of the error). A perfect χ² with structured residuals is still
a bad fit; a good fit needs both.

## 7. Reporting the uncertainty honestly

- **Never a bare number** — quote `value ± uncertainty` with the coverage (1σ / 95 %) and the stat/sys
  split.
- **Significant figures:** the uncertainty sets the precision — usually 1–2 sig figs on the uncertainty,
  with the value's last digit matched to it. Round at the *end*, never mid-propagation.
- An **asymmetric or bounded** quantity (near zero, near a physical limit) gets an interval or a limit, not
  a symmetric ±.
- Ties to `report`'s *honest band* and *label every number by kind* — an uncertainty is part of the number.

## The two-question reflex (before you quote an uncertainty)

1. **What dominates the budget — and is it stat or sys?** If systematic, running longer will not help.
2. **Did I include the thing that actually moved** between repeats/sessions? Session-to-session "scatter"
   is often a drift or a recalibration — a systematic wearing a statistical disguise.

## Checklist

- [ ] Every source enumerated in an error-budget table (stat/sys tagged, estimation method noted)?
- [ ] Dominant source identified from the sensitivity (partials × σ)?
- [ ] Correlations handled (not blind quadrature); nothing double-counted; coverage stated?
- [ ] Averaging taken to `τ_opt`, not past the drift wall (Allan deviation)?
- [ ] reduced-χ² ≈ 1 **and** residuals unstructured?
- [ ] Reported as `value ± stat ± sys` with stated coverage — not a bare number?

## Composition

`verify` grades whether the uncertainty is defensible and interrogates residual structure ·
`report` / `final-report` consume the budget as the "honest band" · `signal-extraction-pitfalls.md`
guards the raw statistics feeding it · `systematic-errors.md` bounds the systematic rows ·
`dimensional-analysis` checks the propagated units · `noise-and-sensitivity.md` supplies the
a-priori statistical floor.

## Sources *(cite-checked 2026-07-03; confirm final formatting/DOIs at paper time)*

Standard measurement-science methodology — nothing here is novel; the value is codifying it into the
kit's workflow. Verified canonical references: the **GUM** (JCGM 100:2008, *Guide to the Expression of
Uncertainty in Measurement*); **Taylor**, *An Introduction to Error Analysis* (2nd ed., University Science
Books, 1997); **Bevington & Robinson**, *Data Reduction and Error Analysis for the Physical Sciences* (3rd
ed., McGraw-Hill, 2003); **Allan**, "Statistics of Atomic Frequency Standards" (*Proc. IEEE* **54**, 1966,
221–230) for the Allan deviation.
