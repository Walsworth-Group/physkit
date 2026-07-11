# Autonomous Research Loop — Per-Island ASI Classifier

The **slim core** of the campaign protocol — what the agent needs every iteration.
Rarely-fired procedures live in `docs/protocols/`. Modeled on the v4
image-reconstruction campaign (`E:\Magnetic inverse loop - v4\docs\charter.md`).

## Mission

Iteratively improve a neural network that classifies the Ising state of all 2178
pinwheel-ASI islands from a single NV map `B_NV`, **maximizing balanced per-island
accuracy on a held-out synthetic test set drawn from the realistic-config
mixture**, with the sim-to-real field-reconstruction R² on the real frustrated
maps as a co-tracked guardrail.

**Run continuously until manually stopped.**

## Why this is shaped differently from v4

v4 reconstructs an *image* and had **no** ground-truth M for the real data, so its
primary metric was an experimental composite. Here every island has a known
position + easy axis, so the problem is **binary classification** with a known
linear forward map `B = D s`, and synthetic states come with **exact labels**.
That inverts the metric roles: synthetic per-island accuracy is PRIMARY (we can
measure correctness directly), and the real frustrated maps — for which we have
no microstate truth — are a **guardrail** scored by field residual + ice-rule
plausibility (necessary-but-not-sufficient; the field is blind to the null space).

The SVD recoverability analysis (`DISCOVERIES.md`) sets expectations: at 650 nm
standoff ~72% of island DOF are above noise; edges are resolvable, interior
~0.6–0.7. The network's value is lifting the interior via the learned prior.

## Startup Checklist

1. Read this file (`docs/charter.md`).
2. Read `docs/DESIGN_island_classifier.md` (the why) + `docs/CONVENTIONS.md`
   (sign/ordering — the bug-prevention reference).
3. Read `results/DISCOVERIES.md` (settled), `results/JOURNAL.md` (NEXT: pointer).
4. Read `results/results.tsv` — campaign history.
5. **Verify the dataset exists** (`data/trainset/ISLcls_*`); if not, generate it
   (`protocols/dataset.md`) — this is the first action on a fresh tree.
6. Decide what to try next. On a fresh tree: queue Experiment 000 (baselines),
   then Experiment 0 (`backproj_cnn`).

## The Experiment Loop

```
Experiment 000 (ONCE, before the loop): BASELINE GATE
   run scripts/baselines.py --config configs/exp000_baselines.json
   -> matched-filter + Tikhonov-LS balanced accuracy = the FLOOR. Also validates
   the D / data / sign-convention chain. Record in results.tsv + JOURNAL.

WHILE not interrupted:
   1. HYPOTHESIZE  — What change might raise balanced per-island accuracy
                     (without hurting the noisy-val guardrail)?
   2. IMPLEMENT    — Modify model/loss/preprocessing (new config per exp).
   3. TRAIN        — scripts/train.py --config ... (OBEY epoch caps).
   4. EVALUATE     — test balanced_acc (PRIMARY) + edge/interior split + field R²
                     (run_synthetic_eval.py writes summary.json); the in-training
                     guardrail is noisy-val balanced_acc.
   5. LOG          — append a row to results.tsv (schema below).
   6. ANALYZE      — Did balanced_acc rise vs the baseline floor + prior best? Did
                     the interior improve (where the prior matters), or only edges?
                     Did the guardrail hold? A gain only at edges is cheap.
   7. ARTIFACTS    — summary.json (synthetic) + the per-island inference plot
                     (plot_inference.py --config ... --mode both) saved under
                     experiments/<exp>/ {.,inference_plots/}. See
                     protocols/inference_artifacts.md.
   8. UPDATE       — write JOURNAL.md / DISCOVERIES.md entries.
   9. CONSOLIDATE  — if JOURNAL > ~150 lines, see journal_consolidation.md.
  10. CHECKPOINT   — if exp_id % 25 == 0, run checkpoint_25.md.
  11. REPEAT
```

## Training Caps (HARD, never exceed)

| Type | Target | HARD MAX | When |
|------|--------|----------|------|
| **Scout** | 15 | **20** | Default for any new idea |
| **Confirmation** | 40 | **50** | Promising scouts, every 5–7 exps |
| **Extended** | 60 | **75** | Primary still improving at confirmation length |

Early-stop patience is on the guardrail `noisy_val_balanced_acc` (scouts 5,
confirmation 12). The best checkpoint is selected by that guardrail; report the
PRIMARY (test balanced_acc) at the best checkpoint.

## Decision Metrics

- **PRIMARY** (cross-experiment ranking, "current best"): **test balanced per-island
  accuracy** on the held-out realistic-config shards, higher better. Always report
  the **edge vs interior split** — interior accuracy is the real signal (edges are
  near-trivially recoverable; see DISCOVERIES). A mean propped up by edges is not a
  real win.
- **SECONDARY guardrail** (checkpoint selection, early stop, overfit watch):
  `noisy_val_balanced_acc` (eval noise from config), higher better.
- **SIM-TO-REAL guardrail** (co-tracked, NOT primary, DEFERRED until wired):
  field-reconstruction R² + ice-rule plausibility on the real frustrated maps
  (`run_experimental_inference.py`). A primary gain that does NOT transfer to the
  real field residual is a sim-to-real-overfit red flag.
- **Diagnostic**: overall (unbalanced) accuracy, synthetic field R², BCE, ice frac.

**Promotion rule**: a config becomes "current best" only if it raises test
balanced_acc (driven at least partly by the INTERIOR) AND the noisy-val guardrail
is not materially worse (> ~2% absolute). Confirm single-seed wins with a second
seed before promoting.

## Logging Protocol

### `results/results.tsv` (schema)
```
exp_id  timestamp  description  model  preprocessing  loss  lambda_field
train_noise  eval_noise  lr  batch  epochs  train_loss
val_balanced_acc  val_acc  acc_edge  acc_interior  noisy_val_balanced_acc
field_r2  real_field_r2  notes
```
Primary = `val_balanced_acc` (test split, best ckpt). `real_field_r2` blank until
the experimental guardrail is wired.

### `results/JOURNAL.md` entry
```
## Experiment XXX -- [date]
**Type**: Scout (15ep) | Confirmation (40ep) | Extended (60ep)
**Hypothesis**: [why this raises balanced per-island accuracy]
**Change**: ...
**Result**: bal_acc=... (edge=... interior=...), noisy_val=..., field_r2=...
**Analysis**: [did the INTERIOR move? guardrail hold? vs baseline floor?]
**Artifacts**: experiments/<exp>/summary.json
**NEXT**: [what to try next]
```

### `results/DISCOVERIES.md`
Write only after multiple consistent experiments confirm a finding on the PRIMARY
(and note the guardrail behavior).

## Decision-Making Guidelines

- **Interior accuracy up, guardrail holds** → log, queue a confirmation/seed-repeat.
- **Only edge accuracy up** → cheap/near-trivial; not a real win, keep exploring.
- **Primary up, guardrail degraded** → suspect sim-to-real / val overfit; second seed.
- **Flat/ambiguous** → after 2–3 inconclusive scouts, move on.
- **Realistic-config mixture is a *data* choice** — changing the sampler mixture
  changes the test distribution; hold it fixed unless deliberately studying it
  (log the change loudly), at most a couple of early experiments.

## What to Vary

Architecture (CNN width/depth/attention; a **GNN on the vertex graph**; unrolled /
learned-ISTA decoders); the backprojection front-end (colnorm vs none; mean-removed
D; multi-axis / multi-standoff stacked D to raise rank); loss (`lambda_field`,
the **ice-rule term** once built, focal/weighted BCE for the imbalanced interior);
training (lr/schedule, optimizer, batch, noise curriculum, NV-angle/pose-jitter
robustness — the dataset already jitters pose). Sampler mixture is a *data* choice.

## Getting Unstuck

If 5+ experiments without an interior-accuracy gain: re-read `DESIGN_island_classifier.md`
(null-space / learned-prior argument) and `DISCOVERIES.md`; check whether the
guardrail is also stuck (capacity/data-limited) or still moving
(generalization-limited); build the **ice-rule prior** (the biggest unexploited
constraint); try **multi-axis D** (raises the recoverable rank — the hard ceiling);
try a GNN that respects the vertex topology; revisit a smaller/larger model.

## Safety & Code Modification Rules

- Never delete data/models without confirmation; never modify on-disk datasets.
  Monitor GPU memory (OOM → smaller batch/model, log, move on).
- **FROZEN** (do not edit without re-validation + user sign-off): `metrics.py`
  scoring math, the forward model `mb` (`M_to_B_linecuts.py`), `island_dictionary.py`
  (D construction), `catalog_index.py` (ordering).
- **READ-ONLY**: `generate_training_islands.py` (regenerate datasets via it, don't
  edit its physics).
- **Mutable**: `model.py`, `train.py`, `losses.py`, `data.py` preprocessing,
  `configs/` (new file per experiment).

  ### Literature Search Rule

Whenever you feel stuck perform a **web literature
search** to find new techniques and update `docs/LITERATURE.md`.
Note that literature ideas are merely suggestions, and you do not have to 
prioritize them over your own ideas unless you feel stuck

#### How to perform a literature search

1. **Review current state**: Read `results/DISCOVERIES.md` and
   `results/JOURNAL.md` to identify what's working, what's failing, and
   where the current bottleneck is (e.g., overfitting, amplitude recovery,
   frequency content, domain gap).

2. **Search for relevant papers** using web search. Target 6-10 queries
   covering:
   - The specific bottleneck you're facing (e.g., "reducing train/val gap
     UNet inverse problem 2025")
   - The closest published analogues (e.g., "magnetization reconstruction
     NV magnetometry neural network")
   - Architectural innovations for your resolution/problem size
   - Loss functions and regularization for ill-posed inverse problems
   - Domain adaptation techniques (synthetic -> experimental)
   - Any new techniques in the general area that may have appeared since
     the last search

3. **Update `docs/LITERATURE.md`**:
   - Add new sections for genuinely new techniques not already covered
   - Update existing sections if newer/better papers supersede old ones
   - **Update the Priority Roadmap** table: mark items that have been
     tried (with outcome), add new items, re-rank by expected impact
     given current experiment results
   - Update the "Last updated" date at the top of the file
   - Add a recommended next-experiment sequence at the bottom based on
     the updated roadmap and current best results

4. **Log the search** in `results/JOURNAL.md` with a brief note:
   `"Literature search at exp XXX: added sections on [topics]. Top new
   priorities: [list]."`

#### When to search 

- You have tried all "Low effort" items in the Priority Roadmap and need
  fresh ideas
- A new category of experiment (e.g., first time trying physics-informed
  losses) could benefit from more targeted references
- The current best MSE has plateaued for 25+ experiments with diminishing
  returns (<1% improvement per experiment)
- You are about to attempt a "High effort" item and want to confirm it's
  still the best use of time given recent literature

## Protocol Index

| Protocol | Fires when | File |
|----------|-----------|------|
| Dataset generation & splits | Fresh tree / new data | `protocols/dataset.md` |
| Metric spec | Reasoning about the primary | `protocols/metric.md` |
| Baseline gate | Experiment 000 | `protocols/baselines.md` |
| Experimental (sim-to-real) scoring | When wiring the real-data guardrail | `protocols/experimental_scoring.md` |
| Save inference artifacts | Every experiment, step 7 | `protocols/inference_artifacts.md` |
| Journal consolidation | Every 10 exp or >150 lines | `protocols/journal_consolidation.md` |
| 25-experiment checkpoint | Every 25 exp | `protocols/checkpoint_25.md` |
