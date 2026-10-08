---
id: pivoting
kind: reference-doc
layer: shared
load: on-demand
load_trigger: When an approach is failing or plateauing and you must decide whether to refine the current idea or pivot to a different one — the refine↔pivot diagnosis.
frozen: false
review: living
---

# Pivoting — diagnose the failure before you jump

When an approach stalls, neither continued tweaking nor immediate abandonment is justified on its own.
Diagnose why it is failing first, then take the smallest jump along the refine↔pivot spectrum that the
diagnosis justifies. This is the depth behind the CORE "when stuck" line, and `debug` hands off here once
it has ruled out a bug.

Rule out a bug first. A crash or a garbage number is a `debug` problem, not a pivot problem: a crash is
evidence about the code, never about the idea. Diagnose a pivot only once the implementation runs
correctly and the idea still underperforms.

## Diagnose the failure type
Name which case applies. The diagnosis selects the move:

| Diagnosis | What it looks like | Smallest justified jump |
|---|---|---|
| **Idea-wrong** | The approach is sound as implemented but the premise does not hold: it cannot work even done perfectly. | Pivot to a different idea/lever family. |
| **Implementation-capped** | The idea is sound but this implementation limits it (a weak solver, a coarse grid, a poor initialization, an under-tuned hyperparameter). | Refine in place: improve the implementation, do not abandon the idea. |
| **Fixed-choice-fought** | A frozen choice (a parameterization, a representation, a constraint) is being fought by an idea that needs it to bend. | Change that one fixed choice. A medium jump, not a full pivot. |
| **Near-miss** | It almost works: a consistent small effect in the right direction, within the noise. | Gather more evidence or sharpen the test before deciding. Do not pivot on a near-miss. |
| **Inherited-value-wrong** | One-lever experiments across ≥2 lever families pin at the same floor (within the metric's replicate spread), or the best result sits far from its own a-priori expectation and no lever moves the gap. | Not a pivot at all: the error is upstream of every lever. Run `assumption-audit` (re-measure the top inherited suspect from scratch) before spending more experiments. |

The near-miss is the case most often misread. A consistent trend whose spread overlaps the
comparison is a reason to gather more evidence: more seeds, more data, a sharper test. It establishes
neither failure nor success. This is the INCONCLUSIVE verdict in `verify`. Investigate anomalies and
structured residuals before discarding them; a structured residual is a frequent source of discovery.

## The refine↔pivot spectrum
Order the moves by how much they discard, and take the smallest the diagnosis warrants:
1. **Tune** — adjust hyperparameters/resolution within the current approach (implementation-capped).
2. **Re-implement a component** — swap a solver, initialization, or representation (implementation-capped /
   fixed-choice-fought).
3. **Change a fixed choice** — a different parameterization, constraint, or sub-method (fixed-choice-fought).
4. **Pivot the lever** — a different mechanism within the same goal (idea-wrong, current family).
5. **Pivot to an orthogonal lever** — a different family entirely (idea-wrong, family exhausted).

Escalate to an orthogonal lever only once the current family is exhausted. Once it is, escalate rather
than continuing to adjust the same knob.

## Don't lose the information
- Record the diagnosis, the jump, and the evidence for the diagnosis: `record-decision` for a
  consequential pivot, the campaign journal otherwise. A pivot with no recorded reasoning is re-tried
  later by accident.
- After a discovery, re-open previously-shelved directions the discovery may have unblocked. Levers
  interact; a lever shelved as ineffective can work after a change elsewhere.
- A documented implementation barrier that is serious enough to block the idea can justify shelving it.
  Record it as a diagnosis: name the constraint that blocks the idea and the evidence that the
  constraint is real.

## Pointers
CORE "when stuck"; `debug` (rule out a bug first); `verify` (the INCONCLUSIVE / near-miss verdict);
`campaign-status` (pivot diagnosis at checkpoints); `record-decision` (capture the why).
