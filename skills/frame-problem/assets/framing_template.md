# Framing — <problem in one line>

> The durable frame for this problem, produced by `frame-problem` once the goal was clear. Update it as
> understanding changes. In a campaign its parts graduate: inventory → `PHYSICS.md`,
> goal + steps → `PROJECT_ORIENTATION.md`, verification plan → the verification gate.

**Date:** <YYYY-MM-DD> · **Status:** draft / confirmed-with-user / in-progress

## Goal & the decision it drives
- **Goal:** <what we're trying to find/predict/optimize, concretely>
- **Decision it serves:** <what this answer lets someone decide or do>
- **What is not claimed / out of scope:** <…>

## Physics inventory
A-priori bound on the answer (ceiling / floor / order of magnitude): **<… — how derived>**
Domain of validity: **<…>** · Key assumptions: **<…>**

| Effect | Tag | Why (number where "negligible") |
|---|---|---|
| <effect> | accounted-for | <how it's modeled> |
| <effect> | negligible-by-scale | <the estimate/ratio showing it's small here> |
| <effect> | out-of-scope | <why it's outside this work> |
| <effect> | deferred | <added in step N> |
| <effect> | unknown | <flagged risk — how we'll find out> |

## Verification plan — how we'll know the answer is right (decided up front)
Mark each as **V** (verification: solving the equations right) or **Val** (validation: solving the right
equations, on held-out/independent data). Verify before validate; calibration ≠ validation.

- [ ] (V) Dimensional / units sanity — run first.
- [ ] (V) Analytic / closed-form limit reproduced: <which limit>.
- [ ] (V) Conservation / symmetry invariant holds: <which>.
- [ ] (V) Numerical convergence demonstrated: <refine what until stable> (if discretized).
- [ ] (V) Independent-method parity: <second method that must agree>.
- [ ] (Val) Comparison to data / benchmark: <which, with uncertainty on both sides>.
- [ ] Application-specific checks / known gotchas: <field-standard checks for this problem>.

## Decomposition — steps, with checkpoints where it matters
Build the simplest sufficient version first; add deferred effects one at a time, naming what each
step changes. Adding several at once is legitimate; say which, and why.

| # | Step (what it produces) | Depends on | Check at this step? |
|---|---|---|---|
| 1 | <…> | — | <check, or "n/a — low risk"> |
| 2 | <…> | 1 | <check — step 3 builds on this> |
| 3 | <add deferred effect …> | 2 | <check> |

## Open questions / risks
- <unknowns from the inventory, decisions to revisit, things to confirm with the user>
