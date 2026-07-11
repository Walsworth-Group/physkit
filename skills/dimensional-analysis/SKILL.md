---
name: dimensional-analysis
description: >-
  The cheapest correctness and bounding tool in physics — use it first. Reach for it whenever there is a
  new or derived equation or quantity to sanity-check ("do the units even work?"), a suspected units-or-sign
  bug, or a need to bound what an answer should be before computing it (ceiling / floor / order of
  magnitude). It does three jobs: (1) units/dimensional consistency as a bug filter; (2) a-priori bounds and
  scaling from combining the relevant scales; (3) the dimensionless groups (Buckingham pi) and
  nondimensionalization that reveal the problem's *real* parameters and which terms dominate or are
  negligible. Invoked by verify, debug, and frame-problem as the first cheap check, and usable standalone.
  Note it cannot catch a sign error or an O(1) prefactor — pair it with a limiting case for those.
---

# dimensional-analysis — the cheapest check, run first

Dimensions are free information. Before you trust a new equation, chase a bug, or run a simulation, a few
minutes of dimensional reasoning catches the most common errors and tells you what the answer should be —
no code, no data. The discipline is small and high-yield: **the cheapest correctness test is "do the units
work?"**, and the cheapest forecast is the order of magnitude you can build from the scales in the problem.

This skill does three things. Use whichever the situation calls for; they share the same machinery.

---

## 1 · Units consistency — the bug filter
Catch the dimensionally-impossible before anything expensive.
- **Assign base dimensions** to every quantity: mass **M**, length **L**, time **T**, temperature **Θ**,
  current **I**, amount **N**, luminous intensity **J** (or your field's convention). Carry them through.
- **Every additive term must share the same dimensions**, and **both sides of an equation must match.** A
  term that doesn't fit is a wrong equation — find the missing factor (a length, a density, a rate) before
  going further.
- **Arguments of transcendental functions must be dimensionless** — exponentials, logs, sines, anything in
  a power series. A `exp(t)` with `t` in seconds is a bug; it should be `exp(t/τ)`. Same for the argument of
  a log or a fractional power. Angles are dimensionless (radians) but track them anyway.
- **Watch unit systems and hidden constants** — Gaussian vs SI electromagnetism, factors of $c$, $4\pi$,
  $k_B$, $\hbar$; "natural units" where constants are set to 1. A missing $k_B$ between energy and
  temperature is a classic.

**Limit:** units cannot catch a **sign error**, a **factor-of-2 / O(1) prefactor**, or a swapped pair of
same-dimension quantities. Those need a limiting case (below) or `verify`. Dimensional consistency is
necessary, not sufficient.

## 2 · A-priori bounds — what the answer must be
Before computing, build the **ceiling, floor, and order of magnitude** the result has to fall within.
- **Combine the relevant scales** into something with the target dimensions: the answer is usually that
  combination times an O(1) number. (Current at a microelectrode $\sim nFDc\,r$; thermal velocity
  $\sim\sqrt{k_BT/m}$; diffusion time $\sim L^2/D$.) That estimate *is* your order-of-magnitude bound.
- **Bracket it:** the trivial floor (zero / a degenerate limit) and the hard ceiling (a conservation bound,
  a saturation, the speed of light, unit probability). The real answer lives between.
- **A computed result outside this envelope is a bug or a discovery** — and you decide which *before*
  celebrating. This is the bound `frame-problem` records and `verify` checks a result against.

## 3 · Dimensionless groups — the real parameters
The number of true parameters is almost always smaller than the number of variables.
- **Form the dimensionless groups** (Buckingham π): by the π-theorem, a relation among $n$ variables built
  from $k$ independent dimensions reduces to $n-k$ dimensionless groups. Those groups — Reynolds number,
  a ratio of timescales, a coupling strength — are the problem's **real parameters**; the physics depends
  only on them.
- **Their magnitude tells you which terms dominate.** A group $\ll 1$ or $\gg 1$ says a term is negligible
  or controlling *here* — this is exactly how `frame-problem` justifies a "negligible-by-scale" tag with a
  number instead of a guess. A group near 1 means competing effects — keep both.
- **Nondimensionalize** the governing equations (scale each variable by its characteristic value). This
  reduces the parameter count, exposes the **scaling laws** (how the answer grows with each input), and
  makes the small/large parameters for an asymptotic expansion obvious.

---

## Signs, conventions, and what it can't do
Dimensional analysis screens *form*, not *sign or coefficient*. Always pair it with at least one
**limiting case** — a known special case, a small/large-parameter limit, a symmetry the result must respect
— which catches sign flips and O(1) errors that units miss. For the dimensionless **prefactor** you need
the actual derivation, a fit, or a reference value. Treat a dimensionally-consistent result as "not yet
falsified," not "correct."

## Composition
- **`frame-problem`** uses jobs 2–3 to bound the answer and to decide what's negligible-by-scale.
- **`verify`** runs job 1 as the first check on any new/derived equation, before recomputing.
- **`debug`** uses job 1 to localize a units/sign bug.
- **`attribute-mechanism`** uses job 2 to bound each candidate mechanism's plausible strength before the sweep is coded.
- For deeper theory (the π-theorem proof, scaling laws, asymptotics, similarity solutions) see
  `docs/reference/dimensional-analysis.md`.

## Worked micro-example
*Claim: a damped oscillator's amplitude decays as $A(t)=A_0\,e^{-\gamma t}$ with $\gamma = b/m$ ($b$ =
drag coefficient $[\mathrm{M\,T^{-1}}]$, $m$ = mass $[\mathrm{M}]$).*
- **Units (job 1):** $[\gamma] = [b]/[m] = \mathrm{M\,T^{-1}}/\mathrm{M} = \mathrm{T^{-1}}$ ✓ — so $\gamma t$
  is dimensionless and $e^{-\gamma t}$ is legal. The form passes.
- **Bound (job 2):** the decay time is $\tau = 1/\gamma = m/b$ — order of magnitude set by mass over drag.
- **Groups (job 3):** with a restoring force $k$, the real parameter is the damping ratio
  $\zeta = b/(2\sqrt{mk})$ (dimensionless) — $\zeta \ll 1$ underdamped, $\zeta \gg 1$ overdamped. *That*,
  not $b$, $m$, $k$ separately, governs the behavior.
- **Limit (the part units miss):** as $b\to 0$, $\gamma\to 0$ and $A\to A_0$ (undamped) ✓ — and the sign is
  right (decay, not growth). Units alone couldn't have caught a wrong sign here.

## Checklist
- [ ] Every additive term and both sides of each equation are dimensionally equal.
- [ ] Every transcendental-function argument is dimensionless.
- [ ] An order-of-magnitude bound (ceiling / floor) is in hand before computing.
- [ ] The dimensionless groups are identified; small/large ones flag negligible/dominant terms.
- [ ] At least one limiting case checked (catches the sign / O(1) errors units cannot).
