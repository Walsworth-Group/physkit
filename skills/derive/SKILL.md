---
name: derive
description: >-
  Analytical or symbolic derivation, verified before use: derivation before code, then dimensional,
  limiting-case, computer-algebra, and numerical checks.
---

# derive — work the analytics out, then prove you didn't fool yourself

A derivation is a claim, and it carries no warrant until it is checked. A single dropped factor, sign flip,
or out-of-regime approximation propagates silently into everything built on it. This skill does the
analytical work with discipline, then applies to symbols the stance the rest of the kit applies to numbers:
assume you are wrong until independently proven right.

Two habits set the frame (the mathematical layer of the agentic-research commandments, Zimmer et al.):
- **Derivations before code.** Work the analytics out first. The derivation is the specification the code
  must satisfy, not the other way around. Code is then an independent check on the derivation (below), not
  a substitute for it.
- **Precise notation.** Define every symbol, its meaning, and its units the first time it appears, and fix
  conventions (signs, frames, branch choices) explicitly. Most derivation bugs hide in ambiguous notation.

## The process
1. **State it precisely.** What is given, what is sought, and in what regime or domain. List the
   assumptions and approximations before making them. Each one is an entry in the physics inventory
   (`frame-problem`) and a condition on the result's validity. Define all symbols + units.
2. **Derive — show the steps.** Derive what is specific to this problem, and cite standard textbook
   results rather than re-deriving them. Keep each step dimensionally consistent; do not wait until the end.
   Record where each approximation is valid: the small parameter, the neglected term, and why it is small
   (quantify with `dimensional-analysis`).
3. **Verify the result — independently, by several routes.** No single check suffices.
   - **Dimensional check** every nontrivial line and the final result. Units must balance, and arguments
     of transcendental functions must be dimensionless (`dimensional-analysis`).
   - **Limiting & special cases** — the result must reduce to known results in the obvious limits (a
     parameter → 0 or ∞, a symmetry, a previously-solved case). This catches sign and O(1) errors that
     dimensions miss.
   - **Computer-algebra cross-check (step-by-step).** Mechanize the algebra (SymPy or another CAS) to
     redo the expansion, integral, or simplification, and check it step by step rather than only the final
     form: re-derive each nontrivial line and assert the CAS expression equals the hand result
     (`sympy.simplify(lhs - rhs) == 0`), test the key limits with `series` / `limit`, and verify the
     boundary and special cases symbolically. This catches the hand-algebra slips (dropped terms, sign
     errors, bad interchange of sum/integral) that are the most common derivation failure, and it localizes
     which line broke instead of only showing that the final answer is wrong.
   - **Independent re-derivation** — a second, mechanism-diverse route to the same result (a different
     method, a different variable choice). Agreement by two routes is strong warrant. Warrant rides on the
     independent check, not on re-reading the original steps.
   - **Numerical spot-check** — evaluate the analytic result and an independent numerical solution of the
     original problem at a few representative points. They must agree within the expansion order.
     Disagreement localizes the bug.
   - **Conservation / symmetry** — the result must respect the conservation laws and symmetries of the
     setup. Check them explicitly.
4. **Grade the claim** (`verify`'s verdicts): **verified** (CAS + independent route + numerical
   agreement), **partially verified** (some checks pass, e.g. limits + units only), or **conjectured**
   (plausible, not yet checked). State what is proven and what is conjectured, and the assumptions and
   domain under which it holds. Never present an assumption-dependent or single-route-only result as a
   general, settled fact.
5. **Record & report.** Capture the reason for a non-obvious approximation (`record-decision`). In a report,
   show the specific derivation at a level a reader can follow and reproduce, cite the standard results, and
   carry the assumptions + domain of validity into the limitations.

## Common derivation bugs (the catalog)
- **Sign / factor errors** — a dropped $2$, $\pi$, $i$, or minus; a missed Jacobian / volume element /
  metric factor.
- **Index & summation slips** — a free index that should be summed, a repeated dummy, a transposed pair.
- **Illegal interchange** — swapping limits ↔ integrals ↔ sums without justification; differentiating under
  an integral where it is not allowed.
- **Boundary terms** — dropped surface/boundary terms in integration by parts or the divergence theorem.
- **Out-of-regime approximation** — a Taylor/asymptotic expansion used where its small parameter is not
  small; keeping inconsistent orders.
- **Branch & domain** — wrong branch of a root/log, ignoring a pole or branch cut, a step valid only for
  one sign of a variable.
- **Non-commutation** — treating non-commuting operators/matrices as commuting.
- **Units / convention** — a hidden $\hbar$/$c$/$k_B$, a Gaussian-vs-SI factor, an angle in the wrong unit.

## Honest limit on warrant
A symbolic result that a CAS confirms and a numerical solution reproduces is strongly verified. A hand
derivation with only a dimensional + limiting-case sanity check is weakly verified. Grade it as partial and
say so. Physical mathematics rarely affords a full proof-checker. Name the strength of the checks that were
actually run rather than implying more certainty than those checks support.

## Composition
- **`dimensional-analysis`** — the per-line units check, the dimensionless-group structure, and the
  limiting-case bounds.
- **`frame-problem`** — the assumptions and approximations tracked here are the physics inventory, and a
  derivation's domain of validity feeds it.
- **`verify`** — treats the derived result as a claim to certify (independent route, numerical falsification).
  This skill is verify specialized to a symbolic result.
- **`record-decision`** (why an approximation) · **`report`** (present the derivation, cite standard / derive
  specific) · **`correctness-suite`** (a derived formula that becomes code gets an analytic-limit/MMS test).

## Before you rely on a derivation — checklist
- [ ] Every symbol defined with units; conventions (sign/frame/branch) fixed.
- [ ] Assumptions/approximations listed with the regime each is valid in.
- [ ] Final result is dimensionally consistent and reduces correctly in known limits.
- [ ] Cross-checked by a CAS, an independent re-derivation, or both.
- [ ] Numerically spot-checked against an independent solution of the original problem.
- [ ] Conservation laws / symmetries respected.
- [ ] Claim graded (verified / partial / conjectured); assumptions + domain of validity stated.
