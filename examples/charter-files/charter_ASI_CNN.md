# Autonomous Research Loop — Magnetic Inverse Problem (V4)

The **slim core** of the v4 protocol — what the agent needs every iteration.
Rarely-fired procedures live in `docs/protocols/`.

## Mission

Iteratively improve a neural network that reconstructs M(x,y) from a single
NV projection B_NV(x,y), **maximizing the validated composite score on the
experimental ASI data**, with noisy-synthetic MSE as a secondary guardrail.

**Run continuously until manually stopped.**

## Why V4 Looks Different from V3

V3 forbade experimental metrics (v2 had churned 140 experiments on them).
V4 deliberately makes experimental performance primary again, but safely:
1. The metric is a **validated, frozen composite** (NCC × support × locality),
   not raw forward-residual (which prefers empty/out-of-ASI guesses).
2. It is scored over the **whole** experimental set with spread reported.
3. **Noisy-synthetic MSE remains a co-tracked guardrail** to catch overfitting
   to the small, correlated experimental set.
The may10 breakthroughs (native orientation, NV-angle jitter) made experimental
reconstruction good enough (R²≈0.80) that optimizing it is now productive.

## Startup Checklist

1. Read `CLAUDE.md` (auto-loaded) — v4 rules, physics, datasets.
2. Read `results/V3_HANDOFF.md` — warm-start recipe + settled context.
3. Read `results/DISCOVERIES.md`, `results/JOURNAL.md` (NEXT: pointer).
4. Read `results/results.tsv` — v4 history.
5. **Verify `configs/metric_v2.json` exists** (tilt-aware metric, signed off
   2026-06-01; loaded by default). If not, the composite is not yet trustworthy
   — see `metric_validation.md` and do NOT rank on it until the gate passes.
6. Decide what to try next. On a fresh dir: queue `v4_exp001_warmstart_native`.

## The Experiment Loop

```
Experiment 000 (ONCE, before the loop): METRIC-VALIDATION GATE
   run scripts/validate_metric.py; confirm synthetic Spearman + experimental
   ranking match the user's judgment; freeze configs/metric_v1.json. Until this
   passes, the composite is not a trusted decision input.

WHILE not interrupted:
   1. HYPOTHESIZE  — What change might raise the composite (and not hurt noisy_val_mse)?
   2. IMPLEMENT    — Modify model/training/preprocessing.
   3. TRAIN        — Run training (OBEY epoch caps).
   4. EVALUATE     — composite_mean/std on the experimental set (PRIMARY, via
                     run_experimental_inference.py) + noisy_val_mse/noisy_test_mse
                     (SECONDARY). Plus diagnostic clean val_mse.
   5. LOG          — Record all metrics in results.tsv (schema below).
   6. ANALYZE      — Did composite rise? Did the guardrail hold? Check spread
                     across images; a gain driven by 1-2 images is suspect.
   7. INFER ARTIFACTS — Save both bundles (experimental composite + synthetic-test
                     clean/noisy) via /save-inference for the user.
   8. UPDATE       — Write findings to JOURNAL.md / DISCOVERIES.md.
   9. CONSOLIDATE  — If JOURNAL needs trimming, see journal_consolidation.md.
  10. CHECKPOINT   — If exp_id % 25 == 0, run checkpoint_25.md.
  11. REPEAT
```

## Training Caps (HARD, never exceed)

| Type | Target | HARD MAX | When |
|------|--------|----------|------|
| **Scout** | 15 | **20** | Default for any new idea |
| **Confirmation** | 40 | **50** | Promising scouts, every 5–7 exps |
| **Extended** | 60 | **75** | Primary still improving at confirmation length |

Rules: never exceed the hard max; justify any run >50 epochs in JOURNAL; if your
last 3 runs were >50 epochs, the next must be a scout. Early-stop patience is on
`noisy_val_mse` (scouts 5, confirmation 15) — the experimental composite is only
computed end-of-run, so the in-training checkpoint/early-stop signal is the
secondary metric. **Then re-rank surviving checkpoints by the primary composite.**

## Decision Metrics

> **METRIC v2 (2026-06-01): `configs/metric_v2.json`** — the experimental
> composite is PRIMARY (rank on `composite_mean`). v2 is TILT-AWARE: the forward
> model used for R2_swept + the NCC gate now includes the experimental standoff
> tilt (~1.73° z0 gradient along +y), reflecting current physics. Composite
> structure unchanged from v1. Rankings preserved vs v1 (re-score:
> `results/metric_v2_rescore.tsv`). Keep collecting labels (`metric_labels.md`);
> re-version only with user sign-off.

- **PRIMARY** (cross-experiment ranking, "current best"): `composite_mean` over
  the experimental set (frozen `metric_v2`), higher better; watch `composite_std`
  / `composite_min` / worst image (the spread guardrail — a mean propped up by
  1–2 of the correlated bias-field images is not a real win).
- **SECONDARY guardrail** (checkpoint selection, early stop, overfit watch):
  `noisy_val_mse_tilt` / `noisy_test_mse_tilt` (std 0.05, seed 42), lower better.
  **As of 2026-05-31 the canonical guardrail is computed on TILTED val/test**
  (the experimental regime — fixed 1.73° standoff tilt; see "Tilted eval change"
  below and `protocols/evaluation.md`). When you train on a `*_tiltc` dataset,
  train.py's in-training `noisy_val_mse` and end test eval are ALREADY tilted —
  log them into the `_tilt` columns.
- **Diagnostic only**: clean `val_mse`, `test_mse`, `train_loss`, train/val ratio.
  The legacy `noisy_val_mse` / `noisy_test_mse` columns (clean val/test) are kept
  for the pre-2026-05-31 runs as a REFERENCE ONLY — they are NOT on the same scale
  as the `_tilt` columns (per-sample-max normalization shifts when the tilt raises
  |B|; tilted MSE runs ~2-3× lower for the same net). **Never compare a `_tilt`
  number to a non-`_tilt` number — only tilted-to-tilted.**

> **Tilted eval change (2026-05-31).** Clean val/test unfairly penalized
> tilt-trained nets (harder problem). Val/test moved to the experimental tilt
> regime; all prior checkpointed nets were re-scored on the same tilted set
> (`scripts/rescore_tilted.py` → `results/tilted_rescore.tsv`, backfilled into
> the `_tilt` columns). Old clean numbers retained for reference.

**Promotion rule**: a config becomes "current best" only if it raises the
primary composite AND its `noisy_val_mse_tilt` is not materially worse (> ~5%)
than the prior best (tilted-to-tilted). A primary gain with a degraded guardrail
is a red flag for experimental-set overfitting — confirm with a second seed.

## Logging Protocol

### `results/results.tsv` (v4 schema)
```
exp_id  timestamp  description  architecture  preprocessing  loss_fn
standoff_set  nv_theta_mean  nv_phi_mean  nv_theta_std  nv_phi_std
train_noise_std  eval_noise_std  lr  batch_size  epochs  train_loss
exp_score_mean  exp_score_std  exp_ncc  exp_support  exp_edge_frac
noisy_val_mse  noisy_test_mse  val_mse  test_mse
noisy_val_mse_tilt  noisy_test_mse_tilt  val_mse_tilt  test_mse_tilt  notes
```
Primary = `exp_score_mean`; secondary (canonical) = `noisy_val_mse_tilt` /
`noisy_test_mse_tilt` (TILTED val/test). The non-`_tilt` columns are the legacy
CLEAN val/test numbers, kept for reference only (different normalization scale —
do not compare across the two). New `*_tiltc`-trained runs: copy train.py's
(already-tilted) `noisy_val_mse`/`noisy_test_mse` into the `_tilt` columns and
leave the clean columns blank (or "-").

### `results/JOURNAL.md` entry
```
## Experiment XXX -- [date]
**Type**: Scout (15ep) | Confirmation (40ep) | Extended (60ep)
**Hypothesis**: [why this raises the composite]
**Change**: ...
**Result**: exp_score=MEAN±STD (best mode=...), noisy_val_mse=..., (clean val_mse=...)
**Analysis**: [composite-grounded; did the guardrail hold? spread across images?]
**Inference artifacts**: experimental + synthetic-test saved to experiments/v4_expXXX_*/.
**NEXT**: [what to try next]
```

### `results/DISCOVERIES.md`
Write only after multiple consistent experiments confirm a finding on the
**primary composite** (and note the guardrail behavior).

## Decision-Making Guidelines

- **Composite up, guardrail holds** → log, queue a confirmation/seed-repeat,
  keep exploring (don't immediately full-train).
- **Composite up, guardrail degraded** → suspect experimental-set overfit;
  re-run with a second seed; if it doesn't replicate, reject.
- **Composite flat/ambiguous** → after 2–3 inconclusive scouts, move on.
- **Standoff-treatment A/B is a distraction risk** — at most 2–3 early
  experiments comparing the three datasets, then commit to the primary
  (uniform) unless an alternate clearly and reproducibly wins.

## What to Vary

Architecture (UNet depth/width, attention, residual/multi-scale heads,
activations); Training (lr + schedule, optimizer, batch size, loss family —
MSE/MAE/Huber/spectral/physics-informed, NV-angle jitter std, gradient
clipping, augmentation — but mixup OFF with jitter); Preprocessing (Wiener
prefilter standoff(s), FFT features, per-sample norm). Standoff treatment is a
*data* choice (swap the dataset), capped per above.

## Getting Unstuck

If 5+ experiments without composite improvement: re-read `DISCOVERIES.md` /
`V3_HANDOFF.md`; re-read `LITERATURE.md` (noise-robustness, denoising,
regularization) and run a literature search (`literature.md`); re-read
`PHYSICS.md` for an unexploited constraint; check whether the guardrail
(noisy_val_mse) is also stuck (capacity/data-limited) or still improving
(experimental-generalization-limited); try a different loss family or
preprocessing; try a smaller model; revisit scout-only ideas at longer length.

## Safety & Code Modification Rules

- Never delete data or models without confirmation; never modify on-disk
  datasets. Monitor GPU memory (OOM → smaller batch/model, log, move on).
- FROZEN: `forward_model.py`, `evaluate.py`, and `metric_v2.json` (current metric).
- READ-ONLY: `data_generator.py`.
- Mutable: `model.py`, `train.py`, `preprocess.py`, `configs/` (new file per exp).
- `run_experimental_inference.py` / `experimental_metric.py`: the metric LOGIC
  is frozen via `metric_v2.json`; you may edit plotting/IO but not the scoring
  math without re-running the validation gate + user sign-off.

## Protocol Index

| Protocol | Fires when | File |
|----------|-----------|------|
| Dataset paths & splits | Read once | `protocols/dataset.md` |
| Composite metric spec | When reasoning about the primary | `protocols/experimental_metric.md` |
| Metric validation gate | Experiment 000 / any metric change | `protocols/metric_validation.md` |
| Evaluation detail | When changing eval code | `protocols/evaluation.md` |
| Save inference artifacts | Every experiment, step 7 | `protocols/inference_artifacts.md` (`/save-inference`) |
| Data regeneration | To make/alter a standoff dataset | `protocols/data_regeneration.md` |
| Literature consult/search | Every 10 / 25 exp | `protocols/literature.md` |
| Journal consolidation | Every 10 exp or >150 lines | `protocols/journal_consolidation.md` |
| 25-experiment checkpoint | Every 25 exp | `protocols/checkpoint_25.md` |
```
