---
name: frame-problem
description: >-
  Frame a physical-science problem before doing the work — the "think before you act" step. Use once the
  goal is clear (after any goal-clarifying back-and-forth) and BEFORE building a model, writing a
  simulation, deriving a result, or starting a fit: phrasings like "how should I approach...", "frame
  this problem", "what physics matters here", "set up the model for...", "before I simulate/derive/fit...",
  "I want to compute/estimate <quantity>". It produces three things and surfaces them for confirmation:
  (1) a physics inventory — every relevant effect tagged accounted-for or not, and WHY; (2) a verification
  plan — how you will know the answer is right, decided up front; (3) a decomposition into small steps with
  verification between the ones that matter. Skip only for trivial one-step questions. Composed by
  new-campaign and simulation-design; pairs with dimensional-analysis for a-priori bounds.
---

# frame-problem — scope the physics before you do the work

The most expensive mistakes in physical-science work are decided *before any code runs*: the effect you
silently left out, the answer you never planned to check, the ten-step build where step two was wrong and
you found out at step nine. This skill spends a few minutes up front to prevent them. It turns a clear
goal into an explicit **frame**: what physics is in play, how you will know the answer is right, and the
order you will build it in.

It runs **after the goal is clear** — that clarification is the always-on CORE stance (state assumptions,
present interpretations, push back, stop when confused), not this skill's job. If the goal is still fuzzy,
resolve that first; framing a misunderstood goal just produces a confident wrong plan. If the goal is
clear, produce the three things below, **then show them to the user to confirm or correct before
executing.** The frame is a hypothesis about the problem, and the user is the cheapest check on it.

For a genuinely trivial, single-step question, don't ceremonialize — answer it. Framing earns its keep
the moment a problem has more than one moving part or any way to be quietly wrong.

---

## 1 · Physics inventory — what's in, what's out, and *why*

List the physical effects that could matter to the answer, and tag each one. The point is that **every
omission is deliberate and auditable**, not forgotten.

| tag | meaning |
|---|---|
| **accounted-for** | included in the model |
| **negligible-by-scale** | left out because an estimate shows it's small *here* — give the estimate (a ratio, an order of magnitude) |
| **out-of-scope** | real but outside what this work is answering — say so |
| **deferred** | will matter, but added in a later step — note where |
| **unknown** | might matter; you can't yet tell — flag it as a risk |

Rules that make the inventory honest:
- **Justify every "not accounted-for."** "Negligible" without a number is a guess. Reach for
  `dimensional-analysis` to estimate the size of an effect and to find the **dimensionless groups** that
  say which terms dominate — that is exactly how you decide what's negligible *here*.
- **Bound the answer a priori.** Before building anything, compute the **ceiling, floor, and order of
  magnitude** the result must fall within (units, limits, known system properties). A later result outside
  this envelope is a bug or a discovery — and you decide which *before* celebrating. (`dimensional-analysis`.)
- **State the domain of validity and the key assumptions** the model rests on.
- **Anchor load-bearing facts, not just effects.** A system parameter or convention taken from a paper,
  leftover code, or memory is a *description* of the system, not the system — pin each to the
  highest-authority artifact you can parse/run and tag its provenance (`docs/PRINCIPLES.md` Ctx 4). An
  unpinned load-bearing fact is a risk, like an unjustified "negligible."
- **Keep it living.** A persistent gap between model and data, after the work checks out, points straight
  at a **parked or missing effect** here (model-form error) — the inventory is where you look — **or at a bug
  in the FROZEN reference code / forward model itself** (a sign/convention error upstream masquerades as
  missing physics); re-verify that infrastructure too, don't only add terms. Update it as understanding
  changes; in a campaign it graduates into `PHYSICS.md`.

### The predictive framework — the model you predict *with* (and revise)
The inventory says *which effects are in play*; the **predictive framework** is the model that ties them into
**predictions** — the mental model expert physicists actually reason from (Wieman's decisions 5, 8, 19, 20,
23). Name it explicitly:
- **The mechanism + the key variables and their relationships**, at a **complexity chosen to match the
  problem** — the minimally-sufficient level, and *why this level and not more* (decision 5). (Laser-cooling
  example: photon vs atom momentum, the light-scattering conversion between them, and the scattering rate's
  dependence on light frequency and the Doppler shift.)
- **The thought-experiments it licenses** — "if I change X, the framework predicts Y." These *are* your
  a-priori predictions (decision 19) and a source of candidate solutions (decision 8); run them before you
  run code.
- **Enumerate candidate approaches before committing to one** (decision 8). The thought-experiments usually
  suggest *several* possible levers or solutions — jot a short **divergent** list with a one-line pro/con
  each, and *choose among them deliberately*, rather than running with the first idea that came to mind.
- **Keep it revisable, and log the revisions.** When data disagrees with the framework's prediction (a
  structured residual, an out-of-envelope result), decide whether the anomaly fits the framework's stated
  domain or **the framework itself must change** (decisions 20 → 23) — then record what changed and why (the
  laser-cooling example adds the AC Stark shift and its spatial variation across the beam). In a campaign this
  revision log lives in `PHYSICS.md` (its "Updates from discoveries" section). *(Placement of the revision log
  is provisional — reassess after a couple of campaigns whether it belongs in `PHYSICS.md` or the append-only
  `ENGINEERING_NOTES.md`.)*

## 2 · Verification plan — how you'll know the answer is right (decided up front)

Decide *how the answer will be checked before you compute it*, not after. This is the single highest-leverage
habit in the skill: a check you design up front is honest; a check you reach for once you already have a
number you like is not. Draft the plan as a short list of concrete checks, each one you commit to running.

Draw from (pick what fits — not all apply):
- **Analytic / closed-form limits** the result must reproduce (a known special case, a small/large-parameter
  limit, a symmetry).
- **Conservation and symmetry invariants** that must hold (energy/mass/charge; the symmetries of the setup).
- **Dimensional / units sanity** — the cheapest check there is; run it first (`dimensional-analysis`).
- **Numerical convergence** — if anything is discretized, the plan to refine timestep/grid/tolerance until
  the answer stops moving, and to separate numerical error from model error.
- **Independent, mechanism-diverse parity** — a second method, an independent computation, or a certifying
  solver that should agree. Warrant rides on an independent checker, not a prose argument.
- **Validation against data** — comparison to measurement or an established benchmark, with uncertainty on
  *both* sides, on **held-out / independent** data. Mark this clearly as *validation* ("solving the right
  equations"), distinct from *verification* ("solving the equations right"): **verify before you validate,
  and calibration is not validation.**
- **Application-specific checks and known gotchas** — the field-standard comparisons, known artifacts, and
  "everyone in this subfield checks X" practices for *this* problem. Capture these now; they're easy to
  forget and expensive to miss. (In a campaign these land in the verification plan / `VERIFICATION_PLAN.md`
  and feed `correctness-suite`, which promotes each hard-won check to a standing regression gate.)

The plan is the input to the rest of the pipeline: `correctness-suite` *executes* the checkable ones,
`verify` adversarially checks the resulting claims, and `simulation-design` turns this into a sim's full
V&V&UQ plan. Record the *why* of any non-obvious check (`record-decision`).

## 3 · Decomposition — small steps, verified where it matters

Break the work into small, agile sub-steps you can do one at a time. For each step note **what it produces**,
**what it depends on**, and — for the steps that matter — **its check**.

- **Verify between steps proportional to risk, not after every trivial step.** Put a checkpoint where a
  later step *depends* on this one, or where an error would *compound*. A wrong foundation found at step two
  is cheap; found at step nine it's a rebuild.
- **Flag the crux sub-steps and set an acceptable-uncertainty bar** (Wieman decision 12). Name the sub-steps
  that are *hardest or most uncertain* — where the plan is most likely wrong — and decide *how sure you must
  be* to proceed past each (the acceptable-uncertainty threshold at that stage). Risk concentrates there;
  that's where the checkpoints and the early de-risking effort belong.
- **Build the simplest sufficient version first**, then add the deferred effects from the inventory one at a
  time — each addition is a step, and ideally each is independently checkable. Validating a simpler subcase
  first usually yields a stronger, better-validated final result.
- **One lever at a time** so each step's effect is attributable (co-vary only deliberately, and say so).

How much to persist (don't invent a doc for a small job):
- **Trivial / short:** keep the steps in your head or a scratch list — just do them.
- **General session, non-trivial:** a lightweight checklist you maintain (steps + status + which were
  checked). It graduates into a campaign's orientation doc if the work grows into one.
- **Campaign:** the numbered, goal-linked task hierarchy in `PROJECT_ORIENTATION.md` (status + per-step
  verification). `new-campaign` owns that; `frame-problem` feeds it.

---

## Surface the frame, then execute

Show the user the three outputs together — inventory, verification plan, step plan — and **invite
correction**. Cheap moment to catch a missing effect, a check that won't actually discriminate, or a step
order that buries risk. Then execute the steps, running each planned check at its checkpoint.

## Persist a framing artifact (when the work is non-trivial)

For anything beyond a quick question, write the frame to a durable **framing artifact** (template:
`assets/framing_template.md`) so it survives the session and seeds what comes next. Its content graduates:
the **inventory → `PHYSICS.md`**, the **goal + steps → `PROJECT_ORIENTATION.md`** (campaigns), the
**verification plan → the verification gate**. Keep one artifact; update it as the frame changes.

## Composition & boundaries

- **`new-campaign` composes this** and *confirms, does not re-ask*: `frame-problem` owns the physics scoping
  and writes the artifact; `new-campaign` reads it back and adds campaign-only topics (metric, levers,
  data, compute, archetype). Within a session this is shared context; across sessions the persisted
  artifact carries it. No double-interview.
- **`simulation-design` starts from this skill's inventory** and turns the verification plan into a full
  V&V&UQ plan *before any simulation code is written*.
- **`dimensional-analysis`** does the bounding and dominant-term work in steps 1–2.
- **`docs/reference/coordinate-frames.md`** — for a geometry-heavy problem, declare each coordinate frame
  (name, origin, axes, handedness) in the inventory and pin how every transpose/handedness/sign ambiguity is
  broken from an **independent** reference; `verify` runs the frame-consistency checklist downstream.
- **`verify` / `correctness-suite`** consume the verification plan downstream.

## Worked mini-example (estimate, then frame)

*Goal (already clarified): predict the diffusion-limited current at a microelectrode for a redox couple.*
- **Inventory:** bulk diffusion **accounted-for**; spherical/edge geometry **accounted-for**; migration
  **negligible-by-scale** (excess supporting electrolyte → transference number ≪ 1, give the ratio);
  natural convection **out-of-scope** (quiescent, short timescale — state the timescale); double-layer
  charging **deferred** (matters only at early times — added in step 3); adsorption **unknown** (flag).
- **A-priori bound:** steady-state $i \sim n F D c\, r$ (with an $O(1)$ geometry-dependent prefactor — 4
  for a microdisk of radius $r$) sets the order of magnitude; the answer must land within a small factor
  of it (`dimensional-analysis`).
- **Verification plan:** recover the planar Cottrell limit as $r\to\infty$ (analytic limit); check the
  steady-state scaling with $r$ and $c$; converge the mesh near the electrode edge; compare to the
  published microdisk result (validation, independent data).
- **Decomposition:** (1) steady-state analytic estimate [check: units + the bound]; (2) numerical
  steady-state solve [check: matches (1) within mesh error, convergence demonstrated]; (3) add transient +
  double-layer [check: recovers Cottrell at short time]. Verify after (2) — step (3) builds on it.

## Before you call the frame done — checklist
- [ ] Every effect that could matter is listed and tagged; each "not accounted-for" has a *reason* (a number where it's "negligible").
- [ ] The answer is bounded a priori (ceiling / floor / order of magnitude).
- [ ] The **predictive framework** is named (mechanism + variables + relationships, at a complexity justified for the problem) and the thought-experiments it licenses are stated — and it's set up to be *revised* (with a logged reason) when data disagrees.
- [ ] Candidate approaches enumerated (divergent, pro/con) before committing; the crux/highest-uncertainty sub-steps flagged with an acceptable-uncertainty bar.
- [ ] Key assumptions and the domain of validity are stated.
- [ ] The verification plan is concrete and decided *before* computing — verification vs validation marked; calibration ≠ validation noted where relevant.
- [ ] Application-specific checks / known gotchas captured.
- [ ] The work is decomposed into steps with checkpoints where risk compounds (not everywhere).
- [ ] The three outputs were shown to the user for confirmation.
- [ ] A framing artifact is written if the work is non-trivial (else intentionally skipped).

## Bundled assets
- `assets/framing_template.md` — the durable framing artifact: goal recap · physics inventory table ·
  verification plan · decomposition with checkpoints.
