---
name: dimensional-analysis
description: >-
  The cheapest check, run first: units consistency, a-priori bounds and scaling, dimensionless
  groups. Use on any new equation or suspected units bug.
---

# dimensional-analysis — the cheapest check, run first

Dimensional reasoning costs no code and no data. Run it before trusting a new equation, chasing a bug, or
running a simulation. It gives a correctness test (do the units balance) and an order-of-magnitude
forecast from the scales already in the problem.

This skill does three things. Use whichever the situation calls for; they share the same machinery.

---

## 1 · Units consistency — the bug filter
Catch the dimensionally-impossible before anything expensive.
- Assign base dimensions to every quantity: mass **M**, length **L**, time **T**, temperature **Θ**,
  current **I**, amount **N**, luminous intensity **J** (or the field's convention). Carry them through.
- Every additive term must share the same dimensions, and both sides of an equation must match. A term
  that does not fit is a wrong equation. Find the missing factor (a length, a density, a rate) before
  going further.
- Arguments of transcendental functions must be dimensionless: exponentials, logs, sines, anything in a
  power series. An `exp(t)` with `t` in seconds is a bug; it should be `exp(t/τ)`. Same for a log's
  argument or a fractional power. Angles are dimensionless (radians); track them anyway.
- Watch unit systems and hidden constants: Gaussian vs SI electromagnetism, factors of $c$, $4\pi$,
  $k_B$, $\hbar$, and "natural units" where constants are set to 1. A missing $k_B$ between energy and
  temperature is a common case.

Limit: units cannot catch a sign error, a factor-of-2 or O(1) prefactor, or a swapped pair of
same-dimension quantities. Those need a limiting case (below) or `verify`. Dimensional consistency is
necessary, not sufficient.

## 2 · A-priori bounds — what the answer must be
Before computing, build the ceiling, floor, and order of magnitude the result has to fall within.
- Combine the relevant scales into a quantity with the target dimensions. The answer is usually that
  combination times an O(1) number (current at a microelectrode $\sim nFDc\,r$; thermal velocity
  $\sim\sqrt{k_BT/m}$; diffusion time $\sim L^2/D$). That combination is the order-of-magnitude bound.
- Bracket it: the trivial floor (zero or a degenerate limit) and the hard ceiling (a conservation bound,
  a saturation, the speed of light, unit probability). The result lies between them.
- A computed result outside this envelope is a bug or a discovery. Decide which before reporting or
  building on it. This is the bound `frame-problem` records and `verify` checks a result against.

## 3 · Dimensionless groups — the real parameters
The number of true parameters is almost always smaller than the number of variables.
- Form the dimensionless groups (Buckingham π): by the π-theorem, a relation among $n$ variables built
  from $k$ independent dimensions reduces to $n-k$ dimensionless groups. Those groups (a Reynolds number,
  a ratio of timescales, a coupling strength) are the problem's real parameters; the physics depends only
  on them.
- Their magnitude says which terms dominate. A group $\ll 1$ or $\gg 1$ marks a term as negligible or
  controlling in the regime at hand, which is how `frame-problem` justifies a "negligible-by-scale" tag
  with a number instead of a guess. A group near 1 means competing effects: keep both.
- Nondimensionalize the governing equations by scaling each variable by its characteristic value. This
  reduces the parameter count, exposes the scaling laws (how the result grows with each input), and
  identifies the small and large parameters for an asymptotic expansion.

---

## Signs, conventions, and what it can't do
Dimensional analysis screens form, not sign or coefficient. Always pair it with at least one limiting
case: a known special case, a small- or large-parameter limit, or a symmetry the result must respect.
That catches the sign flips and O(1) errors units miss. The dimensionless prefactor requires the actual
derivation, a fit, or a reference value. Treat a dimensionally-consistent result as not yet falsified,
not as correct.

## Composition
- `frame-problem` uses jobs 2–3 to bound the answer and to decide what is negligible-by-scale.
- `verify` runs job 1 as the first check on any new or derived equation, before recomputing.
- `debug` uses job 1 to localize a units or sign bug.
- `attribute-mechanism` uses job 2 to bound each candidate mechanism's plausible strength before the sweep is coded.
- For deeper theory (the π-theorem proof, scaling laws, asymptotics, similarity solutions) see
  `docs/reference/dimensional-analysis.md`.

## Worked micro-example
*Claim: a damped oscillator's amplitude decays as $A(t)=A_0\,e^{-\gamma t}$ with $\gamma = b/m$ ($b$ =
drag coefficient $[\mathrm{M\,T^{-1}}]$, $m$ = mass $[\mathrm{M}]$).*
- Units (job 1): $[\gamma] = [b]/[m] = \mathrm{M\,T^{-1}}/\mathrm{M} = \mathrm{T^{-1}}$, so $\gamma t$ is
  dimensionless and $e^{-\gamma t}$ is legal. The form passes.
- Bound (job 2): the decay time is $\tau = 1/\gamma = m/b$, an order of magnitude set by mass over drag.
- Groups (job 3): with a restoring force $k$, the real parameter is the damping ratio
  $\zeta = b/(2\sqrt{mk})$ (dimensionless): $\zeta \ll 1$ underdamped, $\zeta \gg 1$ overdamped. That
  ratio, not $b$, $m$, $k$ separately, governs the behavior.
- Limit (the part units miss): as $b\to 0$, $\gamma\to 0$ and $A\to A_0$ (undamped), and the sign is right
  (decay, not growth). Units alone could not have caught a wrong sign here.

## Checklist
- [ ] Every additive term and both sides of each equation are dimensionally equal.
- [ ] Every transcendental-function argument is dimensionless.
- [ ] An order-of-magnitude bound (ceiling / floor) is in hand before computing.
- [ ] The dimensionless groups are identified; small/large ones flag negligible/dominant terms.
- [ ] At least one limiting case checked (catches the sign / O(1) errors units cannot).
