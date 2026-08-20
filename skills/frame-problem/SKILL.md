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

Three classes of error in physical-science work are fixed before any code runs: an effect left out of the
model, a result with no planned check, and a long build whose second step was wrong and was caught at the
ninth. This skill spends a few minutes up front to prevent them. It turns a clear goal into an explicit
**frame**: which physics is in play, how the answer will be checked, and the order the work is built in.

It runs after the goal is clear. That clarification is the always-on CORE stance (state assumptions,
present interpretations, push back, stop when confused), not this skill's job. If the goal is still fuzzy,
resolve that first; framing a misunderstood goal produces a confident wrong plan. Once the goal is clear,
produce the three outputs below, then show them to the user to confirm or correct before executing. The
frame is a hypothesis about the problem, and the user is the cheapest check on it.

For a trivial single-step question, answer it directly. Frame every problem that has more than one moving
part or any way to be quietly wrong.

---

## 1 · Physics inventory — what's in, what's out, and *why*

List the physical effects that could matter to the answer, and tag each one. Every omission is then
deliberate and auditable rather than forgotten.

| tag | meaning |
|---|---|
| **accounted-for** | included in the model |
| **negligible-by-scale** | left out because an estimate shows it's small *here* — give the estimate (a ratio, an order of magnitude) |
| **out-of-scope** | real but outside what this work is answering — say so |
| **deferred** | will matter, but added in a later step — note where |
| **unknown** | might matter; you can't yet tell — flag it as a risk |

Rules that make the inventory honest:
- Justify every "not accounted-for." "Negligible" without a number is a guess. Use
  `dimensional-analysis` to estimate the size of an effect and to find the dimensionless groups that say
  which terms dominate; that is how a term is shown to be negligible in this regime.
- Bound the answer a priori. Before building anything, compute the ceiling, floor, and order of magnitude
  the result must fall within, from units, limits, and known system properties (`dimensional-analysis`). A
  later result outside this envelope is a bug or a discovery; decide which before acting on it.
- State the domain of validity and the key assumptions the model rests on.
- Anchor load-bearing facts, not only effects. A system parameter or convention taken from a paper,
  leftover code, or memory is a description of the system, not the system. Pin each one to the
  highest-authority artifact you can parse or run, and tag its provenance (`docs/PRINCIPLES.md` Ctx 4). An
  unpinned load-bearing fact is a risk, like an unjustified "negligible."
- Derive implied counts from a named structure; do not take the given number on its own. When the problem
  references a named structure class (a lattice, a symmetry group, a periodic or composite geometry), that
  name carries an implicit multiplicity or count. Derive it from the structure's definition and cross-check
  it against any count given in the framing. A mismatch is load-bearing: an implicit-count error changes
  handedness, degeneracy, or scale in everything downstream, and it throws no error, only a
  plausible-looking wrong answer.
- Keep the inventory living. A persistent gap between model and data, after the work checks out, points at
  a parked or missing effect here (model-form error), or at a bug in the FROZEN reference code or forward
  model, where a sign or convention error upstream presents as missing physics. Re-verify that
  infrastructure; do not only add terms. Update the inventory as understanding changes; in a campaign it
  graduates into the project's `PROJECT_ORIENTATION.md` §Standing constraints.

### The predictive framework — the model you predict *with* (and revise)
The inventory records which effects are in play. The **predictive framework** is the model that ties them
into predictions: the model an expert physicist reasons from. Name it explicitly.
- The mechanism, the key variables, and their relationships, at a complexity matched to the problem: the
  minimally-sufficient level, and why this level and not more. In a laser-cooling model that is photon
  versus atom momentum, the light-scattering conversion between them, and the scattering rate's dependence
  on light frequency and Doppler shift.
- The thought-experiments it licenses: if X changes, the framework predicts Y. These are the a-priori
  predictions and a source of candidate solutions. Run them before running code.
- Enumerate candidate approaches before committing to one. The thought-experiments usually suggest several
  possible levers or solutions. Write a short divergent list with a one-line pro and con for each, and
  choose among them deliberately rather than taking the first idea that came to mind.
- Keep it revisable, and log the revisions. When data disagrees with the framework's prediction (a
  structured residual, an out-of-envelope result), decide whether the anomaly fits the framework's stated
  domain or the framework itself must change, then record what changed and why. The revised laser-cooling
  model adds the AC Stark shift and its spatial variation across the beam. In a campaign this revision log
  lives in `PROJECT_ORIENTATION.md`, in its "Updates from discoveries" section.

## 2 · Verification plan — how you'll know the answer is right (decided up front)

Decide how the answer will be checked before computing it, not after. A check designed before the result
exists is independent of the result; a check chosen once a number is in hand is selected by that number.
Draft the plan as a short list of concrete checks, each one committed to being run.

Draw from the following. Not all apply to every problem.
- **Analytic / closed-form limits** the result must reproduce (a known special case, a small/large-parameter
  limit, a symmetry).
- **Conservation and symmetry invariants** that must hold (energy/mass/charge; the symmetries of the setup).
- **Dimensional / units sanity.** Run it first; it is the cheapest check available (`dimensional-analysis`).
- **Numerical convergence.** If anything is discretized, state the plan to refine timestep, grid, or
  tolerance until the answer stops moving, and to separate numerical error from model error.
- **Independent, mechanism-diverse parity.** A second method, an independent computation, or a certifying
  solver that must agree. Warrant rests on an independent checker, not on a prose argument.
- **Validation against data.** Comparison to measurement or an established benchmark, with uncertainty on
  both sides, on held-out or independent data. Mark it as validation ("solving the right equations"),
  distinct from verification ("solving the equations right"). Verify before you validate, and calibration
  is not validation.
- **Application-specific checks and known gotchas.** The field-standard comparisons, known artifacts, and
  the checks everyone in the subfield runs on this class of problem. Record them at framing time; they are
  easy to omit later and expensive to miss. In a campaign they land in `campaign.md` §Verification
  and feed `correctness-suite`, which promotes each check to a standing
  regression gate.

For each check, name the arbiter: a coded gate, or the model's judgment. Prefer a coded gate that emits the
verdict; the model explains and acts on that verdict but does not decide it. Reserve model judgment for
what cannot be coded, such as a physical-plausibility call, and state why.

The plan is the input to the rest of the pipeline: `correctness-suite` executes the checkable ones, `verify`
adversarially checks the resulting claims, and `simulation-design` turns this into a sim's full V&V&UQ plan.
Record the reason for any non-obvious check (`record-decision`).

## 3 · Decomposition — small steps, verified where it matters

Break the work into small sub-steps that can be done one at a time. For each step, note what it produces,
what it depends on, and, for the steps that matter, its check.

- Verify between steps in proportion to risk, not after every trivial step. Put a checkpoint where a later
  step depends on this one, or where an error would compound. A wrong foundation found at step two is
  cheap; found at step nine it is a rebuild.
- Flag the crux sub-steps and set an acceptable-uncertainty bar. Name the sub-steps that are hardest or
  most uncertain, where the plan is most likely wrong, and decide how certain the result must be to proceed
  past each one. That threshold is the acceptable-uncertainty bar for that stage. Risk concentrates at
  those steps; put the checkpoints and the early de-risking effort there.
- Build the simplest sufficient version first, then add the deferred effects from the inventory one at a
  time. Each addition is a step, and ideally each is independently checkable. Validating a simpler subcase
  first usually yields a stronger, better-validated final result.
- Name what each step changes, so its effect stays attributable. Moving several together is legitimate
  when the cost is justified (coupled levers, a screen, an interaction test); state which moved, and expect `verify`
  to grade the attribution spent.

How much to persist (do not create a document for a small job):
- **Trivial / short:** keep the steps in your head or a scratch list and do them.
- **General session, non-trivial:** a maintained checklist (steps, status, which were checked). It
  graduates into a campaign if the work grows into one.
- **Campaign:** the decomposition becomes the opening units in `results/queue.json` (each with its
  rationale — how it serves the goal) and the JOURNAL NEXT pointer. `new-campaign` owns that seeding;
  `frame-problem` feeds it.

---

## Surface the frame, then execute

Show the user the three outputs together (inventory, verification plan, step plan) and invite correction.
This is the cheapest point at which to catch a missing effect, a check that will not discriminate, or a
step order that buries risk. Then execute the steps, running each planned check at its checkpoint.

## Persist a framing artifact (when the work is non-trivial)

For anything beyond a quick question, write the frame to a durable **framing artifact** (template:
`assets/framing_template.md`) so it survives the session and seeds what comes next. Its content graduates:
the inventory to `PROJECT_ORIENTATION.md` §Standing constraints, the goal to `campaign.md` and the steps
to the queue + JOURNAL NEXT in a campaign, the
verification plan to the verification gate. Keep one artifact, and update it as the frame changes.

## Composition & boundaries

- `new-campaign` composes this skill and confirms rather than re-asking: `frame-problem` owns the physics
  scoping and writes the artifact; `new-campaign` reads it back and adds campaign-only topics (metric,
  levers, data, compute, archetype). Within a session this is shared context; across sessions the persisted
  artifact carries it. Do not run a second interview.
- `simulation-design` starts from this skill's inventory and turns the verification plan into a full V&V&UQ
  plan before any simulation code is written.
- `dimensional-analysis` does the bounding and dominant-term work in steps 1–2.
- `docs/reference/coordinate-frames.md` — for a geometry-heavy problem, declare each coordinate frame
  (name, origin, axes, handedness) in the inventory, and pin how every transpose, handedness, and sign
  ambiguity is broken, using an independent reference. `verify` runs the frame-consistency checklist
  downstream.
- `verify` and `correctness-suite` consume the verification plan downstream.
- `attribute-mechanism` consumes this skill's effect inventory as its candidate-mechanism list when an
  observed signature later needs its physical cause established.

## Worked mini-example (estimate, then frame)

*Goal (already clarified): predict the diffusion-limited current at a microelectrode for a redox couple.*
- **Inventory:** bulk diffusion **accounted-for**; spherical/edge geometry **accounted-for**; migration
  **negligible-by-scale** (excess supporting electrolyte → transference number ≪ 1, give the ratio);
  natural convection **out-of-scope** (quiescent, short timescale; state the timescale); double-layer
  charging **deferred** (matters only at early times; added in step 3); adsorption **unknown** (flag).
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
- [ ] Every effect that could matter is listed and tagged; each "not accounted-for" has a reason (a number where it's "negligible").
- [ ] The answer is bounded a priori (ceiling / floor / order of magnitude).
- [ ] The **predictive framework** is named (mechanism, variables, and relationships, at a complexity justified for the problem), the thought-experiments it licenses are stated, and it is set up to be revised, with a logged reason, when data disagrees.
- [ ] Candidate approaches enumerated (divergent, pro/con) before committing; the crux/highest-uncertainty sub-steps flagged with an acceptable-uncertainty bar.
- [ ] Key assumptions and the domain of validity are stated.
- [ ] The verification plan is concrete and decided before computing; verification vs validation marked; calibration ≠ validation noted where relevant.
- [ ] Application-specific checks / known gotchas captured.
- [ ] The work is decomposed into steps with checkpoints where risk compounds (not everywhere).
- [ ] The three outputs were shown to the user for confirmation.
- [ ] A framing artifact is written if the work is non-trivial (else intentionally skipped).

## Bundled assets
- `assets/framing_template.md` — the durable framing artifact: goal recap · physics inventory table ·
  verification plan · decomposition with checkpoints.
