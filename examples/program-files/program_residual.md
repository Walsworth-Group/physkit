# Autonomous Residual-Minimization Campaign — THE LOOP

The slim core of a **targeted, continuously-running** campaign whose **sole goal is to drive the
experimental forward-vs-data residual as low as possible**, honestly. Read this every iteration.
Mirrors the V1 loop (`docs/program.md`) but with a different objective and a hard persistence rule.

## Mission
Maximize the single FROZEN metric **`EXP_RESIDUAL_R2`** (= 1 − mean experimental field residual;
`scripts/metrics_residual.py`) on the real hysteresis sweep, by optimizing **registration, forward
parameters, preprocessing, and the binary decoder/optimizer/loss**. Synthetic data is used ONLY for
the sanity guardrail and NEVER enters the primary metric. **Run continuously until manually stopped.**

## The ONE metric (FROZEN — never edited)
`EXP_RESIDUAL_R2` = mean over all ~25 frames of the scale-invariant amplitude-fit field-R² of the
**BINARY**-state forward prediction vs the preprocessed experimental input, over the **full** P×P
crop. Decoders may relax to continuous, but the score binarizes (`sign`). Higher = better.
**Baseline (exp 000) = pose-matched binary Tikhonov ≈ 0.639.** Co-tracked (NOT primary): continuous
σ-ceiling, binary-linear ceiling, per-frame spread, and the synthetic SANITY score.

## The Experiment Loop
```
Experiment 000 (ONCE): BASELINE GATE
   python run_residual_campaign.py --baseline   -> EXP_RESIDUAL_R2 ≈ 0.639 (the floor)

WHILE not interrupted:
  1. HYPOTHESIZE  — What change might LOWER the residual? Pick a lever (below).
  2. IMPLEMENT    — New method config: configs_residual/exp<NN>_<slug>.json (one per experiment).
  3. EVALUATE     — python run_residual_campaign.py --config ...   (frozen metric on ALL frames)
  4. SANITY       — auto-run synthetic guardrail (microstate_acc + overfit_flag); logged, NOT primary.
  5. LOG          — a row is appended to results_residual/scoreboard.tsv (schema below).
  6. ANALYZE      — Did EXP_RESIDUAL_R2 rise? Did the binary/continuous ceilings move (forward
                    quality) or only the gap-to-ceiling (decoder)? Did SANITY hold?
  7. ARTIFACTS    — EVERY run AUTOMATICALLY saves LIGHT artifacts (~1 s): per-frame data
                    `results_residual/data/<label>_recon_<G>.npz` (s_hat, input/recon/residual fields,
                    moments) + `results_residual/images/<label>_montage_domains.png`. IF this method
                    is the new CURRENT-BEST (and confirmed per "Rigor"), re-run with `--save-artifacts`
                    for the FULL set (~12 s): also `<label>_montage_fields.png`, `<label>_hysteresis.gif`,
                    and per-frame `<label>_recon_<G>.png`. ALL images land flat in
                    `results_residual/images/`, prefixed by the experiment label (the config filename
                    stem), for easy side-by-side browsing. (Recon = the method's own forward
                    D(theta)*s, i.e. what the metric scores.)  `--no-save` disables all saving.
  8. UPDATE       — write results_residual/JOURNAL_residual.md; graduate settled findings to
                    DISCOVERIES_residual.md.
  9. CONSOLIDATE  — if JOURNAL > ~150 lines, trim to recent + open threads (scoreboard is the ledger).
 10. REPEAT
```

## The levers (what the agent CAN change)
- **Registration** (`register_experimental.locate_asi` variants): per-frame translation; per-frame
  rotation/scale; smooth FOV warp; sub-pixel refine; alternative boundary objectives. Plug into
  `run_residual_campaign.register_frame`.
- **Forward params θ** (LOW-ORDER, physical; `scripts/forward_params.py` → `forward` config
  `{"type":"rebuild","params":{...}}`): GLOBAL NV θ/φ, PSF σ, scalar standoff, Ms, ASI rotation +
  low-order standoff **tilt** (`z0_tilt_x/y_nm_px`). `fit_scalar_params` fits these to the saturated
  anchors. NO free per-pixel offset/gain fields.
- **Preprocessing** (`run_residual_campaign.preprocess`): mean removal; low-order bias-gradient
  removal (`grad_remove`); normalization; denoising; NaN/outlier handling; the real `FWHM_np`/`a_np`
  channels; crop strategy.
- **Decoder + optimizer + LOSS** (the loss MAY differ from the frozen metric;
  `run_residual_campaign.decode`): Tikhonov+threshold (λ); discrete polish (greedy/annealing/BP on
  the binary residual — reuse `_discrete_field_polish` / `physics_inverse._discrete_polish`);
  continuous-relax+round; self-supervised nets fit DIRECTLY on the real frames (no synthetic labels);
  multi-frame joint coupling; ice/coherence/sparsity regularizers in the loss.

## FROZEN / out of scope (NEVER change; NEVER ask for)
`metrics_residual.py` (the scoring formula); the forward PHYSICS equations (`M_to_B_linecuts.py`
`forward_B` — tune its PARAMETERS only); catalog geometry + island ordering (`island_dictionary.py`,
`catalog_index.py`); the experimental data (read-only). Do NOT pause to request more data, a
different metric, or a radically different objective.

## Decision / promotion
- **PRIMARY**: `EXP_RESIDUAL_R2` (higher = better). **A method becomes "best" only if it raises
  `EXP_RESIDUAL_R2` AND passes SANITY** (microstate_acc not materially worse than baseline AND
  `overfit_flag = False`). A high residual-R² with `overfit_flag = True` (fits the field BETTER than
  the true synthetic state) is NOT a real win — it is fitting noise/the null space (the discrete
  field-polish is the canonical example: real R² ≈ 0.85 but overfit_flag = True).
- Distinguish **ceiling moves** (forward/registration/preprocessing raised the binary/continuous
  ceiling — real, physical) from **gap-to-ceiling moves** (a freer decoder closed the gap — check
  SANITY, it is often overfitting).
- **On promotion to current-best, SAVE the reconstruction artifacts** (loop step 7,
  `--save-artifacts` -> `results_residual/<exp_id>/`): per-frame data (`recon_<G>.npz`) and images
  (`recon_<G>.png`, `montage_domains.png`, `montage_fields.png`, `hysteresis.gif`). Keep the
  artifacts for each successive best so the progression is inspectable.

## Rigor: experiments are CHEAP here — replicate before you conclude
Unlike the V1 GPU-training campaigns, these methods (a Tikhonov solve, a discrete polish, a short
self-supervised fit directly on the real frames) run **orders of magnitude faster** — seconds to a
few minutes each, not hours. **Exploit this: never judge an idea from a single run.**
- **Replicate with multiple seeds and slightly perturbed parameters** (λ, registration tolerance,
  standoff/PSF, sweep counts, init) to tell a *real, robust* effect from run-to-run noise. A change
  smaller than the seed-to-seed spread is not a result.
- **This is REQUIRED — not optional — before either:** (a) graduating a finding to
  `DISCOVERIES_residual.md`, or (b) permanently writing off an approach. One run never justifies
  either. Budget a small cluster of confirmatory runs for every candidate conclusion.

## Assessing results critically (every result is suspect until cross-checked)
The residual metric is *gameable* (the discrete-polish overfit is the canonical example) and
self-supervised fits can land on degenerate solutions, so treat every outcome — positive AND
negative — skeptically. Cheap experiments mean you can almost always run the discriminating control
instead of guessing.

**Before WRITING OFF an idea (a flat or negative result), ask:**
- *Could it be implemented differently?* — different parameterization, init, regularizer, optimizer,
  λ, or the ORDER of registration/preprocessing/forward steps. The idea may be right but the
  instantiation wrong.
- *Is there a bug or confound?* — a sign/convention slip, a pose/parameter mismatch, registration
  failing on a subset of frames, a degenerate λ, the scale-invariant amplitude fit masking the
  effect, or the full-crop folding in an unrelated confound. (E.g. exp 001's plane-removal looked
  negative because it ate *real* low-order ASI field, dropping the continuous ceiling too — diagnosed
  by watching the ceiling, not just the primary.)
- *Did it interact badly with a fixed choice that should co-vary?* — e.g. a forward-θ change often
  needs registration re-fit; test the pair, not the part.
- *Was the effect within seed noise?* — replicate before concluding.

**Before ACCEPTING a positive result, ask the SAME questions, plus:**
- *Is it a CEILING move (physical — the binary/continuous ceiling rose) or a gap-to-ceiling move
  (suspect — a freer decoder fitting the gap, usually overfitting)?* Gap moves must clear SANITY.
- *Does SANITY pass?* `overfit_flag = False` AND `microstate_acc` not materially worse than baseline.
- *Does it generalize?* Improvement across the whole sweep (not a few frames), no regression on the
  saturated anchors, holds under multiple seeds/params.
- **Confirm with ≥2–3 independent experiments** before calling a method "best" or writing a
  DISCOVERY. When uncertain, design an ablation / control / synthetic test with known truth rather
  than concluding from one number.

## PERSISTENCE (the defining rule of this campaign)
- **Never stop.** Keep generating diverse hypotheses even after long plateaus with no improvement.
- **After a plateau, escalate to an ORTHOGONAL lever** (registration ↔ forward-θ ↔ preprocessing ↔
  decoder). Do not keep tweaking one knob.
- **Log negative results too** (a flat or worse row is information). Be broad and creative —
  exhaustively probe what residual minimization can do on this data.
- **Do not ask for out-of-scope things.** Work strictly within the levers above.

## Logging
### `results_residual/scoreboard.tsv` (schema)
`exp_id · timestamp · description · registration · forward_params · preprocessing · decoder · loss
· exp_residual_r2 (PRIMARY) · per_frame_r2_min · per_frame_r2_median · continuous_ceiling ·
binary_ceiling · sanity_microstate_acc · sanity_overfit_flag · notes`
### `results_residual/JOURNAL_residual.md` entry
```
## Experiment XXX — [date]
**Hypothesis**: [why this lowers the residual]
**Change**: [the one lever changed vs the current best]
**Result**: EXP_RESIDUAL_R2=... (min/median ...), bin_ceil=..., cont_ceil=...; SANITY acc=..., overfit=...
**Analysis**: [ceiling move vs gap move? sanity hold? real win or overfit?]
**NEXT**: [orthogonal lever to try]
```
### `results_residual/DISCOVERIES_residual.md`
Write only after multiple experiments confirm a finding on `EXP_RESIDUAL_R2` (with SANITY noted).

## Where everything is saved (canonical map — verify each is written every run)
Everything for THIS campaign lives under `E:\ASI sims V2`. It does NOT use `experiments/` (that was
the V1 net-training campaign; safe to ignore). Per experiment, ALL of these must exist:
- `configs_residual/exp<NN>_<slug>.json` — the method spec (one per experiment; the reproducible record).
- `results_residual/scoreboard.tsv` — the ledger (one row per experiment; the PRIMARY metric + ceilings).
- `results_residual/result_<NN>.json` — the full per-experiment metric breakdown.
- `results_residual/data/<label>_recon_<G>.npz` (+ `images/<label>_*.png|gif`) — per-frame artifacts.
- `results_residual/JOURNAL_residual.md` / `DISCOVERIES_residual.md` — narrative + settled findings.
- `data/D_cache/` — cached forward dictionaries (regenerable).
**A result is not "saved" until it has BOTH a scoreboard row AND a `result_<NN>.json`.** Verify after
each run; if a run died before writing both, treat it as not-done and re-run.

## Diagnostics & raw-output persistence (NO result may live only in the console)
Quick probes (`scripts/diag_*.py`, parameter scans via `run_method`) are first-class — their numbers
often decide the next config — but by default they only `print()`, so they are LOST on interruption or
console close and are not reproducible without re-running. This is the one real persistence hole; obey:
- **Tee every run's stdout to a file.** Launch campaign experiments AND diagnostics as
  `python <script> ... > results_residual/diagnostics/<script-stem>_<UTCstamp>.log 2>&1`
  (or pipe through `tee`). Never rely on console scrollback surviving.
- **Any diagnostic that yields an actionable number MUST persist it** in the SAME turn you read it:
  append a structured line to `results_residual/diagnostics/<name>.jsonl` (or `np.save` its arrays),
  AND record the number + the script that produced it in `JOURNAL_residual.md`. A console print alone
  does not count as saved.
- **Keep the diagnostic scripts.** Do not overwrite `diag_x.py` in place — version it (`diag_x2.py`)
  or keep the prior; the script is the only record of HOW a number was produced.
- If a probe informs a promotion, it must additionally become a real `configs_residual/` experiment
  with a scoreboard row — the scan log is evidence, the config+row is the result of record.

> **NEXT VERSION (deferred — implement in the next campaign iteration):** put the project under
> version control (`git init`) so the *code* behind each result is pinned, not just the params. Today
> `run_residual_campaign.py`/`forward_params.py` are mutable with no history, so a `result_<NN>.json`
> + config records the metrics/params but a later code change to a named decoder/forward can make an
> old experiment non-reproducible. Until then, snapshot `scripts/` + `configs_residual/` (e.g. a dated
> zip) whenever a method is promoted to current-best.

## Code rules
- **Mutable**: `run_residual_campaign.py` (add forwards/registrations/preprocessors/decoders),
  `forward_params.py`, `configs_residual/*.json`, the `results_residual/` docs.
- **FROZEN**: `metrics_residual.py`, `M_to_B_linecuts.py` physics, `island_dictionary.py`/
  `catalog_index.py` geometry, `data/D_experimental.npy` build convention. Never edit the data.
