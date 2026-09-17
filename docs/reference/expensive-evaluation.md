---
id: expensive-evaluation
kind: reference
layer: operating
load: on-demand
frozen: false
addresses: [5, 7, 9]
status: active
---

# Expensive evaluations — spending the evaluation budget well

Fires when each evaluation is costly: a long simulation, an FEM/CFD solve, a hardware run, a large
training job. When evaluations are cheap, ignore this document and exploit the speed; replicate freely.
When they are expensive, the real figure of merit is spending the evaluation budget well, not just the
final quality, so track and economize it deliberately. Draws on `docs/SIMULATION_VALIDATION.md` §5.
The campaign-specific stop criterion is a campaign fact and stays in the campaign definition.

## Track the evaluation budget as a first-class metric
- Count expensive evaluations (simulation calls, hardware runs, training jobs) and report the count
  alongside the quality metric. "Reached quality Q in N evaluations": N is half the result.
- Benchmark sample-efficiency against a strong classical baseline such as NSGA-II, Bayesian optimization,
  or a random or grid search, on both final quality and evaluation count. Fewer expensive evaluations than
  the classical baseline is the physics-relevant result. Quality reported without the budget hides the cost.
- Log per-evaluation cost (wall-clock, currency, or samples) so the budget is auditable.

## Spend the budget well
- **Tier by fidelity** (scout → confirm → extended). Screen candidates with the cheapest evaluation that
  discriminates, and spend full-fidelity evaluations only on survivors. Never conclude from toy scale
  alone. Never spend a full run where a cheap one would have filtered the candidate.
- **Scout tiers are per cost axis.** Levers differ in re-check cost, so do not blend them into one scout
  tier. A lever that is cheap to re-screen, such as a per-item or per-frame reprocessing pass, and one that
  is not, such as a global refit across the whole dataset, do not belong in the same scout bucket when the
  cheap one can be screened far more often for the same budget. Where a campaign has both kinds, split or
  tag the scout tier by the cost axis each lever touches, so the budget plan reflects the real cost
  structure rather than assuming uniform scout cost.
- **Pre-screen with a cheaper proxy** where one exists: a surrogate, a reduced-order model, a coarser grid,
  a digital twin. Confirm winners at full fidelity. Validate the proxy against the true evaluator, because
  surrogate error misdirects the search (`SIMULATION_VALIDATION.md` §6).
- **Diminishing-returns stopping.** Detect convergence and stop, rather than spending a fixed budget
  regardless. Define the stop up front, using the stop criterion the campaign recorded: for example,
  improvement below a stated threshold over a stated number of evaluations. A quality-based stop
  complements the hard run caps.
- **Configuration size is a lever, not a default.** Test model size, temperature, and resolution as levers.
  A smaller, cheaper setting sometimes wins on constraint satisfaction and consistency.

## Don't waste an expensive evaluation
- **Predict before you run.** State the a-priori bound first, so the evaluation is a test rather than an
  exploration, and so a surprising result is flagged immediately.
- **In-loop feasibility gate.** Reject a candidate that will not converge, or is infeasible, before paying
  for a full evaluation of it. A non-converging solve that is scored anyway optimizes noise.
- **Save the expensive output** (the campaign's quicker-check artifacts) so a result can be re-checked
  without re-running, and so the verifier can work from saved artifacts on a long run.
- **Hardware and irreversible evaluations.** Confirm before any destructive action. Interleave or randomize
  A/B comparisons against drift. Pre-screen with a forward model. Full operational doctrine: the campaign
  definition's hardware section and `docs/reference/hardware-in-the-loop.md`.

## Monitor a long run — don't wait to be asked
For any run expected to exceed ~30–60 min (a long simulation, a large training job, a detached or
background process):
- **Arm a liveness self-check** on a cadence proportional to the expected duration, rather than relying on
  the user to ask whether it has finished. Verify both that the process is alive and that its log is
  advancing (new lines, or a moving step counter). A live PID is not evidence of progress.
- **Treat a stalled log as a dead run.** Silent deaths are common: out-of-memory, a GPU or driver hang, a
  killed job. A log that has stopped advancing is a failure to investigate, not a run still in progress.
- **Report status without being asked** at each check: started, progressing, stalled, or done.
- Tee stdout to a file so liveness is inspectable: `... > results/diagnostics/<stem>_<UTCstamp>.log 2>&1`.

## Record
Log the running evaluation count, the budget, and the sample-efficiency comparison in the JOURNAL and
the ledger's `note` cell (`--record <exp> --ledger-note`). When you stop a direction, note the stopping
decision and its trigger.
