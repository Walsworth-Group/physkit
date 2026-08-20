---
id: dimensional-analysis-ref
kind: reference-doc
layer: shared
load: on-demand
load_trigger: When the `dimensional-analysis` skill needs depth — the π-theorem, nondimensionalization procedure, scaling laws, asymptotics, and similarity solutions.
frozen: false
addresses: [4, 5]
status: new
review: living
---

# Dimensional analysis — reference depth

The depth behind the [`dimensional-analysis`](../../skills/dimensional-analysis/SKILL.md) skill. The skill
is the actionable checklist (units filter, bounds, dimensionless groups); this is the theory for deriving
the groups, building a scaling law, or setting up an asymptotic expansion.

## The Buckingham π-theorem
A physically meaningful equation among $n$ variables, built from $k$ independent base dimensions, can be
rewritten as a relation among $n-k$ independent **dimensionless groups** ($\pi$-groups):
$$ f(q_1,\dots,q_n)=0 \;\;\Longleftrightarrow\;\; F(\pi_1,\dots,\pi_{n-k})=0. $$
The physics depends on the $\pi$-groups alone, and they are fewer than the raw variables. That reduction
is what nondimensionalization buys.

**Constructing the groups.**
1. List every relevant variable and its dimensions in the base set (M, L, T, Θ, I, N, J).
2. Determine $k$ = the rank of the dimension matrix: the number of independent dimensions present, often
   fewer than the count of base dimensions.
3. Choose $k$ **repeating variables** that together span all the dimensions and are dimensionally
   independent. Do not pick two that differ only by a dimensionless factor.
4. Form $n-k$ groups, each a repeating-variable product times one remaining variable, with exponents fixed
   by requiring the product be dimensionless.

The chosen groups are not unique: any independent combination works. Pick the set whose members carry
physical meaning (a Reynolds number, a ratio of timescales, a coupling constant).

## Nondimensionalization procedure
1. Pick a **characteristic scale** for each variable (a length $L$, a time $\tau$, a field strength) from
   the problem's data.
2. Substitute $x = L\,\tilde x$, $t = \tau\,\tilde t$, … into the governing equations.
3. Collect the dimensionless prefactors; each is a $\pi$-group. Choosing the scales well makes one term
   $O(1)$ and exposes the others' relative size.

The payoff: the parameter count drops, the dominant balance becomes visible, and the expansion's small or
large parameter is now explicit.

## Scaling laws & dominant balance
- A $\pi$-group $\gg 1$ or $\ll 1$ means the term it multiplies dominates or is negligible in that regime,
  the rigorous form of `frame-problem`'s "negligible-by-scale" tag. The classification can flip between
  regimes (boundary layers, stiff systems), so state the regime with the conclusion.
- **Power-law scaling:** when the answer must be a product of powers of the inputs (by dimensions), the
  exponents follow from the dimensions alone; only the dimensionless prefactor needs a derivation, fit, or
  reference value.
- **Dominant balance:** keep the two largest terms, solve, then check the dropped terms are consistent
  with being small (self-consistency). This is the backbone of boundary-layer theory and matched
  asymptotics.

## Limiting cases, similarity & self-similarity
- **Limiting cases** (a parameter → 0 or ∞, a symmetry) give checks units can't: they catch sign errors
  and O(1) coefficients. Always test at least one.
- **Self-similar solutions:** when a problem has no intrinsic length/time scale, the solution often depends
  only on a similarity variable (e.g. $x/\sqrt{Dt}$ for diffusion). Dimensional reasoning finds that
  variable, collapsing a PDE to an ODE.

## What dimensional analysis cannot give you
- The **dimensionless prefactor** (the $4\pi$, the factor of 2). It needs the derivation or a measurement.
- **Sign**, and the form of the dimensionless function $F$: physically different laws can share dimensions,
  so pin the form with theory, a limiting case, or data.
- Anything hidden in a quantity omitted from the variable list. The method is only as complete as that
  list, which is why it pairs with the `frame-problem` physics inventory.

## Pointers
Skill: [`dimensional-analysis`](../../skills/dimensional-analysis/SKILL.md). Used by `frame-problem`
(bounds + dominant terms), `verify` (units-first check), `debug` (units/scale bugs). Classic references:
Barenblatt, *Scaling, Self-similarity, and Intermediate Asymptotics*; Bridgman, *Dimensional Analysis*.
