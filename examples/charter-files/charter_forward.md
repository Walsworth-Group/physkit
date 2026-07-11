# Autonomous Forward-Model-Improvement Campaign — THE LOOP

The slim core of a **targeted, continuously-running** campaign whose **sole goal is to improve the
forward model** — to drive the residual between the **forward-projected field of a uniformly
saturated lattice** and the **measured data at 285 G and 300 G** as low as possible, honestly. Read
this every iteration. Sibling to `docs/charter_residual.md` / `docs/charter_residual_v2.md`: it
inherits their scientific-rigor scaffolding but **inverts what is mutable** — here the forward
*physics code itself* is the thing being improved.

> **Inherited from v2 + what's different.** This doc keeps the v2 best practices (a-priori bounding,
> uncertainty/error-type tracking, independent verification, parsimony, simulation-gap caution,
> provenance logging). The big change: the **forward method code is MUTABLE and is the target of the
> search** (it was FROZEN in the residual campaign). There is **no decoder** — the magnetization is
> KNOWN (uniform saturation), so this is a pure forward-fidelity problem. Items tagged **[PROPOSED]**
> are Claude's suggested additions awaiting your review — keep or cut each.

## Operating stance (applies to EVERY decision in the loop)
- **Critically evaluate every decision.** Every physics term, numerical choice, fitted nuisance
  parameter, and standoff assumption is a hypothesis, not a given. State why before you commit.
- **Assume you are wrong until independently proven right.** A forward change that lowers the residual
  is *suspect* until it survives the two-standoff check, physical-plausibility check, and independent
  verification. The burden of proof is on the improvement.
- **Prefer the minimally sufficient forward model.** Add a physics term, a free parameter, or a
  correction only when it earns its keep against the fit/replicate spread AT BOTH standoffs. A lower
  residual bought with extra free parameters that don't generalize is overfitting the anchors, not a
  better model. (Near-universal — apply by default.)
- **Use precise notation and units everywhere.** Name the quantity, its units, and its scale. Field
  R² is dimensionless in [−∞, 1]; B in Tesla; standoff/PSF σ in nm; Ms in A/m; angles in degrees.
  Ambiguous notation is how sign/convention bugs survive (see `docs/CONVENTIONS.md`).
- **Track uncertainty as a first-class output.** No bare point estimates — every residual you act on
  carries a spread (fit restarts, perturbed params, both standoffs). A result without an error bar is
  not yet a result.

## Mission
Improve the **forward model** so that the forward-projected field of the **uniformly saturated
lattice** (`s = +1` everywhere) matches the **measured saturated data at 285 G and 300 G** as closely
as possible. The forward code may be rewritten, extended with literature-grounded physics, and
optimized. **Every decision is made by minimizing the saturated-anchor residual** (below), checked at
two standoffs. **Run continuously until manually stopped.**

## The ONE metric (the SCORING FORMULA is FROZEN — the forward that feeds it is not)
**`FWD_SAT_RESIDUAL`** = `1 − mean over {285 G, 300 G} of the scale-invariant amplitude-fit field-R²`
of the candidate forward's **uniformly-saturated** prediction vs the preprocessed measured field, over
the full P×P crop. **Lower = better.** Equivalently report **`FWD_SAT_R2`** = the mean field-R²
(higher = better).
- The **saturated state is KNOWN**: `s = np.ones(n_islands)` (+saturation). No decoder, no inference —
  only the forward is under test.
- The **scoring formula is FROZEN** (`metrics_residual.field_r2_binary` / `score`, the scale-invariant
  amplitude fit `a = <b,rec>/<rec,rec>`). You change the *forward that produces `rec`*, never how the
  residual is computed. This is what keeps every experiment comparable.
- **Predicted field** = the candidate forward's saturated map. Prefer the EXACT path
  (`forward_accurate.forward_state(np.ones(...), cat, p)`); if you score the linear operator
  (`center_remove(build_D) @ s`) instead, **report the linearization error** (`validate_D`) alongside
  — never let it masquerade as a physics result.
- **Evaluated at TWO standoffs (650 nm and 900 nm).** A single-standoff number is not a result here
  (see "Two-standoff protocol"). `FWD_SAT_RESIDUAL` without a standoff label is meaningless.
- **Baseline (exp 000):** the current `forward_accurate.py` defaults, scored at BOTH standoffs. Run it
  first; that pair of numbers is the floor to beat. (Do not assume a value — measure it.)

### Metric integrity — don't move the goalposts, don't unfairly punish a valid model
The residual depends on the forward, so the failure modes are specific here:
- **Gaming risk = nuisance-parameter overfitting.** With only two anchor frames, a forward with enough
  free low-order parameters can drive the residual down by absorbing measurement artifacts (a bias
  gradient, a PSF mismatch, an amplitude offset) into "physics." Before trusting a drop, ask: *did the
  residual fall because the PHYSICS got more faithful, or because I added a knob that fit these two
  frames?* The two-standoff check, the physical-plausibility check, and parsimony exist to catch this.
- **Apples-to-apples.** Same crop, same preprocessing, same scoring path, same two anchor frames as
  exp 000. If the preprocessing changed, re-establish the baseline under the new preprocessing before
  claiming a delta — otherwise the delta is partly a measurement change, not a model improvement.
- **The opposite failure — don't let an incompatible check punish a valid model.** Just as a
  flattering setup must not bless a fake win, a structurally incompatible auxiliary check must not
  condemn a legitimate, in-scope change (the canonical residual-campaign example: a synthetic
  guardrail hard-wired to a fixed NV angle penalizing a run that legitimately changed the angle —
  fixed by re-centering the synthetic generation angles, `sanity_synthetic.py`, 2026-06-22). If you
  hit this, **FLAG it explicitly**, build a **fair** evaluation that reflects the run's actual settings
  (more faithful, never merely more lenient), and mark resulting findings **PROVISIONAL** until the
  fairness of the adjustment is reviewed. **Hard boundary:** you may adapt mutable diagnostics for
  fairness; you may NEVER edit the FROZEN scoring formula, the experimental data, or the known
  saturated microstate to make a number look better.
- **[PROPOSED] Null-control the metric.** Score a scrambled/shuffled measured field, or a random
  state, against the forward. The residual should jump to its no-skill level. If a "win" survives
  scrambling, you are scoring leakage, not field fidelity.

## The Experiment Loop
```
SETUP (ONCE): thin driver + baseline
   - If scripts/run_forward_campaign.py does not exist, create it (output-only; it loops a candidate
     forward over standoffs {650, 900}, fits the allowed low-order nuisance params at each FIXED
     standoff, ALSO runs one free-standoff diagnostic fit, scores FWD_SAT_RESIDUAL via the FROZEN
     metrics_residual formula on {285,300}, and writes a scoreboard row + result_<NN>.json). It must
     NOT touch the frozen scoring/data/geometry.
   - Experiment 000: run the current forward_accurate.py defaults at BOTH standoffs -> the floor.

WHILE not interrupted:
  1. HYPOTHESIZE & PREDICT — What forward change might LOWER the saturated-anchor residual? Pick a
                    lever (below); literature search is allowed and encouraged. BEFORE running, write
                    the EXPECTED FWD_SAT_RESIDUAL (point + range) at each standoff and WHY, grounded in
                    physics, units, and any source you cite (see "Bound expectations").
  2. IMPLEMENT    — Change the forward code and/or add a config configs_forward/exp<NN>_<slug>.json
                    capturing the params + which forward variant. Keep the change to ONE lever.
  3. EVALUATE     — Score at standoff = 650 nm AND standoff = 900 nm (fit allowed nuisance params at
                    each fixed standoff). Frozen metric on {285, 300 G}. ALSO run a FREE-standoff
                    diagnostic fit and record the best-fit standoff + its residual.
  4. CHECKS       — physical plausibility of fitted params; parsimony (free-parameter count); exact-vs-
                    linear (validate_D); --selftest still passes; output-preserving for speed-only edits.
  5. LOG          — append a row to results_forward/scoreboard.tsv (schema below), one per standoff
                    (or one row carrying both), with the spread.
  6. ANALYZE      — Did FWD_SAT_RESIDUAL fall at BOTH standoffs, by more than the fit/replicate spread?
                    Inside your predicted range (if not, STOP and explain)? Are fitted params physical?
                    Did the two standoffs AGREE on the model ranking? (If not -> standoff sweep.)
  7. ARTIFACTS    — Save the predicted vs measured saturated maps + residual map for each anchor and
                    standoff (montage/images), and the fitted params. Keep artifacts for each best.
  8. UPDATE       — write results_forward/JOURNAL_forward.md; graduate settled findings to
                    DISCOVERIES_forward.md (only after independent verification).
  9. CONSOLIDATE  — if JOURNAL > ~150 lines, trim to recent + open threads (scoreboard is the ledger).
 10. REPEAT
```

## Two-standoff protocol (the central discipline of THIS campaign)
The NV standoff is an uncertain experimental parameter; **a forward-model conclusion must not be an
artifact of one assumed standoff.** Therefore every candidate is judged at **two fixed standoffs,
650 nm and 900 nm** (the standoff is HELD at each value during comparison; the other allowed low-order
nuisance params may be fit to the anchors at each standoff).
- **Promotion requires agreement:** a forward becomes "better" only if it lowers `FWD_SAT_RESIDUAL`
  (beyond the spread) at **BOTH** 650 nm and 900 nm, with physical fitted params.
- **Diagnostic: free-standoff fit (run EVERY experiment).** In addition to the two fixed-standoff
  scores, run a fit with standoff FREE (alongside the other low-order nuisance params) to find each
  candidate forward's residual-minimizing standoff and the residual there. This is **diagnostic
  context, NOT the decision metric** — promotion still rides on the two fixed standoffs. Read the
  free-fit for: (a) does the best-fit standoff land inside the physical ~650–900 nm window? (b) does it
  shift markedly between candidate forwards, or between the 285 and 300 G anchors — a large shift flags
  a **standoff↔physics degeneracy** (thickness / demag / PSF / k-space falloff absorbing standoff);
  (c) a candidate that only "wins" by driving the best-fit standoff out of range is compensating for
  missing physics, not improving it (treat as overfitting). Log the free-fit standoff + its residual.
- **Disagreement triggers a detailed standoff sweep.** If model A wins at 650 nm but model B wins at
  900 nm (the ranking flips), DO NOT pick a winner. Run a **fine standoff sweep** (e.g. ~600–950 nm in
  small steps) for both models, plot residual-vs-standoff for each, find where and why the curves
  cross, and report it. The crossing usually reveals which physics term is standoff-dependent (e.g.
  finite-thickness, demag, PSF, k-space falloff). **Do not conclude until the crossover is understood.**
- The sweep is also the natural way to localize the true standoff: the residual-minimizing standoff,
  and how sharply it is determined, are themselves results worth logging.

## Bound expectations BEFORE you run (a-priori prediction)
Predicting the residual first turns each run into a real test and is the fastest way to catch
sign/convention bugs and overfit "wins."
- **Hard bounds:** `FWD_SAT_R2 ≤ 1`, `FWD_SAT_RESIDUAL ≥ 0`. The exact forward and its linearization
  agree only to within `validate_D` (~few %); a "win" smaller than that error is inside the noise.
- **Physical parameter ranges — flag any fit that escapes them:** standoff bracketed by the test
  values (~650–900 nm is the plausible NV regime); Ms near the literature permalloy value (the code
  default is `6e5 A/m`; compare to the established bulk value and flag large deviations rather than
  accepting a free-running Ms); NV axis near the measured `θ≈69°, φ≈115°`; PSF σ set by the optical/NV
  readout resolution; ASI rotation near the measured `−2.87°`. A parameter that runs to a non-physical
  value to win is a result *about the model being wrong*, not a free win.
- **Calibrate disagreement with the literature by its weight.** If your fitted value conflicts with a
  few high-uncertainty papers, your data may win; if it conflicts with a well-established, tightly
  measured constant (e.g. permalloy Ms, μ0), assume the error is yours until proven otherwise, and
  quantify the magnitude of the disagreement (how many σ / what fractional difference), not just its
  sign.
- **A result outside your predicted range is a red flag, not a triumph** — do not move on until you
  understand the surprise. Update the bounds as understanding improves.
- **[PROPOSED] Pre-register the prediction** in the JOURNAL entry (a `**Predicted**:` line written
  before EVALUATE), and track predicted-vs-actual to see whether your own forecasting is calibrated.

## The levers (what the agent CAN change — the forward CODE is in scope)
You may edit the forward model code itself. Make ONE lever-change per experiment so effects are
attributable. Levers, roughly orthogonal:
- **Forward physics core** (`forward_accurate.forward_B_core` and its callers): finite-thickness
  factor (`(e^{-kz} − e^{-k(z+t)})` vs thin `kt`), k-space propagation kernel, prefactor/DC
  conventions, demagnetizing/shape effects, edge/corner treatment, higher-order or
  micromagnetic-informed corrections, dipole-vs-extended-source modeling.
- **NV signal model:** projection convention (`physical` n_z=+cosθ vs `flip_nz`; see the convention
  warning — they differ ~0.9%), ensemble/orientation averaging over the NV axis distribution, PSF
  model (Gaussian σ vs measured/anisotropic PSF), standoff distribution / multi-plane averaging.
- **Geometry treatment in the forward** (NOT the geometry truth itself): sub-pixel island placement,
  integration over island volume/shape (rounded corners), thickness profile. The catalog of island
  centers/sizes/ordering stays FROZEN — you change how the forward *uses* it, not what it is.
- **Low-order nuisance params fit to the anchors** (LOW-ORDER, physical; `ForwardParams`): Ms, PSF σ,
  NV θ/φ, ASI rotation, low-order standoff tilt (`z0_tilt_x/y_nm_px`). Standoff is held at 650/900 for
  the decision metric, and ADDITIONALLY free-fit as a diagnostic (see protocol). NO free per-pixel
  offset/gain fields.
- **Numerical & computational optimization:** caching, FFT grid / padding, precision (fp32/fp64),
  vectorization. Split these in two: **(a) speed-only refactors MUST be output-preserving** — prove it
  with an equivalence test (bit-for-bit or within fp tolerance), they do NOT change the metric;
  **(b) accuracy-improving numerics** (finer grid, exact thickness, sub-pixel) DO change the output and
  are scored by the metric like any physics change.
- **Literature & physics search:** use WebSearch to find better forward models / corrections
  (finite-thickness micromagnetics, demag factors for thin elements, NV ensemble PSF, k-space field
  propagation above a magnetized sheet, magnetic-charge formulations). Ground every change in
  `docs/MAGNETIZATION_RECONSTRUCTION_REFERENCE.md`, `docs/CONVENTIONS.md`, and the cited source;
  record the citation in the JOURNAL.

### Choosing among forward models (parsimony + tie-breaking)
- **Could a simpler model fit equally well?** If two forwards match the anchors comparably at both
  standoffs, they are degenerate on this metric — prefer the simpler (fewer free parameters, clearer
  physics) and design a discriminating test (different standoff, the residual *spatial structure*,
  the −sat data if you later trust it) rather than declaring a winner by a coin-flip margin.
- **When two options tie within the spread, break the tie deliberately:** fewer free parameters,
  robustness across the standoff sweep, physical plausibility of fitted params, interpretability, and
  (secondarily) compute cost. Don't add a knob you can't justify physically.
- **A correction that only helps at one standoff is suspect** — it may be absorbing a
  standoff-dependent artifact rather than fixing physics. Resolve via the sweep.

## FROZEN / out of scope (NEVER change; NEVER ask for)
- **The scoring formula** (`metrics_residual.field_r2_binary` / `score` — the scale-invariant
  amplitude-fit field-R²). You optimize the forward against it; you never edit it.
- **The experimental data** (read-only) and **the two anchor frames** used as the metric (285, 300 G).
  (155/160 G are excluded — not reliable.)
- **The known saturated microstate** (`s = +1`) — it is ground truth, not a fit parameter.
- **The catalog GEOMETRY + island ordering** (`island_dictionary.py`, `catalog_index.py`): island
  centers, sizes, count, and index order. You change how the forward *models* this geometry, not the
  geometry itself.
- Do NOT pause to request more data, a different metric, or a radically different objective.

## Decision / promotion
- **PRIMARY**: `FWD_SAT_RESIDUAL` (lower = better), on {285, 300 G}. **A forward becomes "best" only
  if it lowers `FWD_SAT_RESIDUAL` (by more than the fit/replicate spread) at BOTH standoffs
  (650 & 900 nm) AND its fitted params stay physical AND it is no less parsimonious without
  justification AND it survives independent verification.**
- **Distinguish a real physics improvement from anchor-overfitting.** A drop that (i) holds at both
  standoffs, (ii) keeps params physical, and (iii) does not require new free knobs is a real
  improvement. A drop that appears at one standoff, pushes a parameter out of range, or needs added
  flexibility is overfitting the two anchors — investigate, don't promote.
- **On promotion, SAVE artifacts:** predicted vs measured saturated maps + residual maps for each
  anchor at each standoff, the fitted params, and the `validate_D` linearization error. Keep the
  artifacts for each successive best so the progression is inspectable. If the promoted change touched
  the forward CODE, snapshot the code too (see provenance logging).

## Independent verification — assume the improvement is wrong and try to REFUTE it
A lower residual is not a better model until it is independently re-derived. Convergence of a fit is
not correctness; an apparent win can be a sign flip, a standoff-artifact, or anchor-overfitting.
- **Re-derive from scratch:** re-run the candidate forward at both standoffs, recompute
  `FWD_SAT_RESIDUAL` from the frozen scorer, and confirm it reproduces within tolerance.
- **Spawn an independent agent to refute it.** The `verify-finding` skill
  (`.claude/skills/verify-finding/SKILL.md`) is the pattern: a fresh agent that *assumes the result is
  wrong*. For THIS campaign it must additionally: (1) confirm the win holds at BOTH standoffs; (2)
  check fitted params are physical and the model isn't just freer; (3) check the forward CODE change is
  sound (no convention/sign slip; `--selftest` and `validate_D` still pass); (4) confirm apples-to-
  apples preprocessing/crop vs exp 000. Verdict: CONFIRMED / PROVISIONAL / REFUTED / INCONCLUSIVE.
  > **Note:** the current `verify-finding` skill is written for the residual (decoder) campaign and
  > references its metric/ceilings. Adapt its prompt to this campaign's metric, or spin up a
  > `verify-forward-finding` variant. (Ask if you want it built.)
- **[PROPOSED] Spatial-residual check.** Beyond the scalar R², inspect WHERE the residual lives. A
  faithful forward leaves structureless, noise-like residual; a residual that still traces island
  edges or a low-order gradient points to a remaining physics/PSF/standoff error — and is a lead, not
  a stopping point.

## Rigor: experiments are CHEAP here — replicate before you conclude
A saturated-anchor score is a forward solve + a closed-form amplitude fit — **seconds**, not hours.
Exploit it: never judge a forward change from a single run.
- **Replicate** with restarted fits and slightly perturbed nuisance params / grids; for any stochastic
  step, multiple seeds. Report the spread. A change smaller than the spread is not a result.
- **Track error and separate its kinds.** Distinguish *statistical* error (fit restarts, finite
  pixels — shrinks with more samples) from *systematic* error (a convention, standoff, or calibration
  bias — more samples won't help; find the cause). A standoff-dependent residual is the signature of a
  systematic error in the forward.
- **Use a statistical test, not eyeballing, for close calls** — compare per-pixel/per-anchor residual
  distributions, not two point means; "better" must clear the spread at both standoffs.
- **[PROPOSED] Define the minimum meaningful Δ** (e.g. ≥ 2× the fit spread AND larger than the
  `validate_D` linearization error) up front, and report deltas as `Δ ± spread`.
- **This is REQUIRED** before either graduating a finding to `DISCOVERIES_forward.md` or permanently
  writing off a forward idea. One run never justifies either.

## Assessing results critically (every result is suspect until cross-checked)
Cheap experiments mean you can almost always run the discriminating control instead of guessing.

**Before WRITING OFF a forward idea (a flat or negative result), ask:**
- *Could it be implemented differently?* — different parameterization, a different convention, the
  ORDER of operations (PSF before/after thickness, mean-removal timing), or paired with a nuisance
  re-fit. The physics may be right but the instantiation wrong, or another error may be capping it.
- *Is there a bug or confound?* — a sign/convention slip (the #1 forward bug; check `CONVENTIONS.md`),
  a units error (nm vs m, A/m vs emu/cc), a stale cached `D` (delete `data/D_cache/Dacc_*.npy` after a
  core change), a `flip_nz`-vs-`physical` mismatch, or the amplitude fit masking the effect.
- *Did it interact with a fixed choice that should co-vary?* — e.g. a core change often needs the PSF
  or standoff re-fit; test the pair. Standoff and thickness/demag are partially degenerate — vary them
  together, watch the sweep.
- *Was the effect within fit/replicate noise, or one-standoff-only?* — replicate and check both
  standoffs before concluding.

**Before ACCEPTING a positive result, ask the SAME questions, plus:**
- *Did it win at BOTH standoffs?* If not, run the sweep — do not promote a one-standoff win.
- *Did it land inside your predicted range?* Beating your a-priori physical bound is a flag to
  investigate, not a victory to bank.
- *Are the fitted params physical and the model parsimonious?* A win bought with out-of-range params
  or new free knobs is anchor-overfitting.
- *Is the residual structurally better (whiter), not just lower in scalar R²?* (Spatial-residual
  check.)
- **Confirm with ≥2–3 independent experiments AND an independent-agent verification** before calling a
  forward "best" or writing a DISCOVERY. When uncertain, design an ablation / control rather than
  concluding from one number.

### Mind the model-vs-reality gap (here, the model IS the thing you're tuning)
You are improving a *model* of a real magnet/NV system against only two anchor frames. The danger is
fitting the *measurement* (a bias gradient, a PSF quirk, a calibration offset, drift) as if it were
physics.
- Prefer changes justified by physics/literature that ALSO lower the residual, over changes that only
  lower the residual. A correction with a mechanism is far more trustworthy than a free knob.
- A genuine forward improvement should generalize: hold at both standoffs, leave whiter residuals, and
  — once you trust them — help on other frames too. Improvements that only touch the two +sat anchors
  are suspect.
- When a conclusion depends on a modeling assumption (thickness, demag, PSF shape, NV ensemble), say
  so explicitly and test sensitivity to it where cheap.

### After a major discovery — re-open shelved directions
A real forward improvement changes what else is possible. After confirming one, ask which previously-
negative or untried levers might now behave differently (a PSF model that failed under the old core, a
standoff that was capped by the old thickness factor). Budget a short re-exploration pass after every
genuine breakthrough.

## PERSISTENCE (the defining rule of this campaign)
- **Never stop.** Keep generating diverse forward hypotheses (physics, numerics, literature) even
  after long plateaus.
- **After a plateau, escalate to an ORTHOGONAL lever** (physics core ↔ NV signal model ↔ geometry
  treatment ↔ nuisance params ↔ literature). Do not keep tweaking one knob.
- **Form testable hypotheses and design experiments to FALSIFY them.** When a new theory of the
  residual emerges (e.g. "the edge residual is finite-thickness"), design the run that would disprove
  it and the run that isolates exactly which term helps — not just another confirmation.
- **Log negative results too** (a flat or worse row is information). Be broad and creative.
- **Do not ask for out-of-scope things.** Work within the levers above.

## Logging
### `results_forward/scoreboard.tsv` (schema)
`exp_id · timestamp · description · forward_variant · changed_lever · standoff_nm ·
fitted_params · fwd_sat_residual (PRIMARY) · fwd_sat_r2 · r2_285 · r2_300 · residual_spread ·
freefit_standoff_nm · freefit_residual · validate_d_pct · n_free_params · params_physical ·
verified · notes`
(One row per standoff, or one row carrying the 650 & 900 pair — be consistent. `validate_d_pct` =
linearization error; `params_physical` = did fitted params stay in range.)
### `results_forward/JOURNAL_forward.md` entry
```
## Experiment XXX — [date]
**Hypothesis**: [which forward change lowers the saturated-anchor residual, and the physics/citation]
**Predicted**: FWD_SAT_RESIDUAL ≈ [pt] in [lo,hi] @650; [pt] in [lo,hi] @900; basis = [physics/source]
**Change**: [the ONE lever changed vs current best; file(s) touched]
**Result**: @650 resid=[v]±[s] (r2_285/300=.../...);  @900 resid=[v]±[s] (.../...);
            free-fit standoff=[nm] -> resid=[v]; validate_D=[%]; fitted params=[...]; n_free=[...]
**Analysis**: [won at BOTH standoffs? params physical & parsimonious? residual whiter? real vs overfit?
              free-fit standoff in 650–900 & stable across forwards/anchors (degeneracy?)?
              standoffs agree on ranking — if not, sweep result]
**Verification**: [verdict: CONFIRMED / PROVISIONAL / REFUTED / INCONCLUSIVE + key evidence]
**Status**: [confirmed | PROVISIONAL — rests on an adapted eval (say which, and why it's fair)]
**NEXT**: [orthogonal lever to try]
```
### `results_forward/DISCOVERIES_forward.md`
Write only after multiple experiments confirm a finding at BOTH standoffs (with params physical) AND an
independent verification returns CONFIRMED.

### Provenance & configuration logging — log EVERYTHING that could move the number
The "thermostat in the box" principle: record the conditions you weren't varying, because they explain
surprises later. For each run capture:
- The exact config / `ForwardParams` (the reproducible record) and which forward variant/commit.
- The exact command line, both standoff results, wall-clock, and which baseline/best it was compared to.
- **[PROPOSED] Code snapshot is MANDATORY here** (not deferred as in the residual campaign): because the
  forward CODE is mutable and is the result, a config alone does NOT reproduce a number. Snapshot
  `scripts/forward_accurate.py` (+ any edited forward file) per promoted result — ideally `git init`
  and record the commit hash; until then, a dated zip / hash of the forward sources.
- **[PROPOSED] Environment provenance:** Python + numpy/scipy/torch versions, host, threads/BLAS, any
  seed, and the `ASI_MB_PATH` in effect. A score that won't reproduce elsewhere is a systematic-error
  lead — findable only if the environment was logged.

## Where everything is saved (canonical map — verify each is written every run)
Everything for THIS campaign lives under `E:\ASI sims V2`. Per experiment, ALL of these must exist:
- `configs_forward/exp<NN>_<slug>.json` — the method/param spec (one per experiment).
- `results_forward/scoreboard.tsv` — the ledger (the PRIMARY metric at both standoffs).
- `results_forward/result_<NN>.json` — the full per-experiment breakdown (per-anchor, per-standoff).
- `results_forward/images/<label>_*.png` — predicted/measured/residual maps per anchor & standoff.
- `results_forward/JOURNAL_forward.md` / `DISCOVERIES_forward.md` — narrative + settled findings.
- `results_forward/code_snapshots/<label>/` (or a commit hash) — the forward source behind the result.
- `data/D_cache/` — cached forward dictionaries (regenerable; DELETE stale `Dacc_*.npy` after a core change).
**A result is not "saved" until it has BOTH a scoreboard row AND a `result_<NN>.json`.** Verify after
each run; if a run died before writing both, treat it as not-done and re-run.

## Diagnostics & raw-output persistence (NO result may live only in the console)
Quick probes (selftests, parameter scans, standoff sweeps) are first-class — their numbers decide the
next change — but by default they only `print()`, so they are LOST on interruption. Obey:
- **Tee every run's stdout to a file:** `python <script> ... >
  results_forward/diagnostics/<script-stem>_<UTCstamp>.log 2>&1` (or pipe through `tee`).
- **Any diagnostic that yields an actionable number MUST persist it** in the SAME turn you read it:
  append a structured line to `results_forward/diagnostics/<name>.jsonl` (or `np.save` arrays), AND
  record the number + the script that produced it in `JOURNAL_forward.md`. A console print is not saved.
- **Persist standoff sweeps as data**, not just a plot: save `(standoff, residual)` arrays per model so
  the crossover is re-analyzable.
- **[PROPOSED] Numerical hygiene on every probe:** guard against silent NaN/inf, check FFT/grid
  conditioning, confirm fits converged (iterations / final residual). A score from a non-finite or
  non-converged solve is noise. Always run `--selftest` and `validate_D` after a core change.
- **Keep diagnostic scripts** (version, don't overwrite) — the script is the only record of HOW a
  number was produced.
- If a probe informs a promotion, it must additionally become a real `configs_forward/` experiment with
  a scoreboard row — the scan log is evidence, the config+row is the result of record.

## Code rules
- **MUTABLE (the target)**: the forward model code — `scripts/forward_accurate.py` (the owned core
  `forward_B_core`, `forward_state`, `build_D`, conventions, params), any forward variant you add,
  `configs_forward/*.json`, the `results_forward/` docs. You MAY rewrite the forward physics, add
  literature-grounded corrections, and optimize numerics — with the validation above.
- **FROZEN**: `metrics_residual.py` (the scoring formula), the experimental data + the 285/300 G anchor
  frames + the known saturated microstate, and the catalog GEOMETRY/ordering (`island_dictionary.py`,
  `catalog_index.py`). Never edit the data; never edit the score; never invent geometry.
- **After ANY forward-core change:** delete stale `data/D_cache/Dacc_*.npy`, re-run `--selftest` and
  `validate_D`, and re-establish exp 000 if preprocessing changed.
