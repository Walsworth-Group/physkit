---
id: pivoting
kind: reference-doc
layer: shared
load: on-demand
load_trigger: When an approach is failing or plateauing and you must decide whether to refine the current idea or pivot to a different one — the refine↔pivot diagnosis.
frozen: false
addresses: [3]
status: new
review: living
---

# Pivoting — diagnose the failure before you jump

When an approach stalls, the instinct is either to keep tweaking it forever or to abandon it for something
new. Both are usually wrong. The right move is to **diagnose *why* it's failing first**, then take the
**smallest jump** that the diagnosis justifies along the refine↔pivot spectrum. This is the depth behind
the CORE "when stuck" line, and `debug` hands off here once it has ruled out a bug.

**First, rule out a bug.** A crash or a garbage number is a `debug` problem, not a pivot problem — a crash
is evidence about the code, never about the idea. Only diagnose a *pivot* once the implementation runs
correctly and the idea still underperforms.

## Diagnose the failure type
Name which of these you're looking at — the diagnosis picks the move:

| Diagnosis | What it looks like | Smallest justified jump |
|---|---|---|
| **Idea-wrong** | The approach is sound-as-implemented but the *premise* doesn't hold — it can't work even done perfectly. | Pivot to a different idea/lever family. |
| **Implementation-capped** | The idea is fine but *this* implementation limits it (a weak solver, a coarse grid, a poor initialization, an under-tuned hyperparameter). | Refine in place — improve the implementation; don't abandon the idea. |
| **Fixed-choice-fought** | You're fighting a choice you've frozen (a parameterization, a representation, a constraint) that the idea needs to bend. | Change that one fixed choice — a medium jump, not a full pivot. |
| **Near-miss** | It almost works — a consistent small effect in the right direction, within the noise. | Gather more evidence / sharpen the test before deciding; don't pivot on a near-miss. |
| **Inherited-value-wrong** | One-lever experiments across ≥2 lever families pin at the *same* floor (within the metric's replicate spread), or the best result sits far from its own a-priori expectation and no lever moves the gap. | Not a pivot at all — the error is *upstream* of every lever: run `assumption-audit` (re-measure the top inherited suspect from scratch) before spending more experiments. |

A near-miss is the most-misread case: a consistent trend whose spread overlaps the comparison is a reason
to **gather more** (more seeds, more data, a sharper test) — not to declare failure *or* success. (This is
the INCONCLUSIVE verdict in `verify`.) Investigate anomalies and structured residuals before discarding
them — they're often the discovery, not the dead end.

## The refine↔pivot spectrum
Order the moves by how much they discard, and take the smallest the diagnosis warrants:
1. **Tune** — adjust hyperparameters/resolution within the current approach (implementation-capped).
2. **Re-implement a component** — swap a solver, initialization, or representation (implementation-capped /
   fixed-choice-fought).
3. **Change a fixed choice** — a different parameterization, constraint, or sub-method (fixed-choice-fought).
4. **Pivot the lever** — a different mechanism within the same goal (idea-wrong, current family).
5. **Pivot to an orthogonal lever** — a different family entirely (idea-wrong, family exhausted).

**Escalate to an orthogonal lever only once the current family is exhausted** — but escalate decisively when
it is, rather than tweaking the same knob indefinitely. The failure isn't "we should try harder on the same
thing"; it's "this lever class is spent."

## Don't lose the information
- **Record the diagnosis and the jump** (and the evidence for the diagnosis) — `record-decision` for a
  consequential pivot, the campaign journal otherwise. A pivot with no recorded reasoning gets re-tried
  later by accident.
- **After a discovery, re-open previously-shelved directions** the discovery may have unblocked —
  interactions matter, and a lever parked as "didn't work" may work now.
- A genuine, serious, *documented* implementation barrier can justify shelving an idea — but that's a
  diagnosis (idea blocked by a real constraint), not a shrug.

## Pointers
CORE "when stuck"; `debug` (rule out a bug first); `verify` (the INCONCLUSIVE / near-miss verdict);
`campaign-status` (pivot diagnosis at checkpoints); `record-decision` (capture the why).
