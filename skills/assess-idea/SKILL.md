---
name: assess-idea
description: >-
  Honestly pressure-test a research idea or direction BEFORE committing to it — is it plausibly solvable, and
  is it worth the cost, risk, and time? The anti-hype counterpart to verify: it may (and should) conclude
  "no", "not yet", or "not worth it". Use when someone floats an idea and wants a candid take, or before
  scaffolding a campaign around an unvetted idea — phrasings like "what do you think of this idea?", "is this
  worth pursuing?", "is this feasible?", "should I work on X?", "pressure-test this proposal", "is this a good
  research direction?". It bounds the idea a priori (is the hoped-for effect even physically available?),
  locates the crux (the hardest/most-uncertain part and the cheapest check that would de-risk it), weighs
  prior art and cheaper alternatives, and returns a graded go / no-go / de-risk-first verdict with its
  reasoning, confidence, and load-bearing assumptions. In a campaign it is ADVISORY — it records a judgment,
  never blocks. Distinct from frame-problem (which plans HOW to do a problem you have already decided to do)
  and verify (which checks a result you already have).
---

# assess-idea — pressure-test the idea before you commit

Most wasted research effort is committed at the start, on a problem chosen because it sounded interesting
rather than checked for solvability or worth. This skill is the triage for that moment, and the counterpart
to `verify`: where `verify` treats a result as wrong until independently proven right, `assess-idea` treats
an idea as not worth doing until its case is made. Truth over excitement applies to idea selection: a
well-evidenced "this cannot clear the ceiling" or "this is already solved" is a successful assessment.

Novelty and rigor are compatible: unconventional and ambitious ideas are in scope, and this skill is not a
filter against them. The job is to find the cheapest path to the truth about whether the idea works, and to
name the one thing most likely to sink it. Attempt to falsify the idea as hard as the case for it was built;
an idea that survives is pursued without reservation.

## When to use / not use
- **Use** on a raw idea or direction, before investing: "what do you think of this?", "is this worth it?",
  "is this feasible?", "should we work on X?". Also an optional advisory pre-check before `new-campaign`
  scaffolds a loop around an unvetted idea.
- **`frame-problem`** instead once the idea is a `go`. That skill plans how to do a problem already decided
  on: physics inventory, verification plan, decomposition. `assess-idea` is upstream of it and lighter; it
  decides whether to do the work at all. Hand off to `frame-problem` on a `go`.
- **`verify`** instead when there is already a result to check. **`new-campaign`** to scaffold a decided loop.
- **Collaboration first.** Problem selection is a shared decision: surface the assessment and its reasoning
  and let the researcher choose. Do not unilaterally kill or greenlight someone's idea. The verdict is a
  recommendation with its evidence, not a verdict on the researcher.

## The assessment
Work these in order. Stop early on a decisive result: a hard physical no in step 2 ends it. Keep the effort
proportional — a quick idea gets a quick pass, a large commitment the full battery.

1. **Restate the idea and what success would look like.** In your own words: the claim or goal, and the
   concrete criterion by which it would count as working. If the idea is fuzzy, or intent is being filled
   in, clarify with the user first. A moving target cannot be assessed.
2. **Bound it a priori** (compose `dimensional-analysis`, or a light `frame-problem` pass). Compute the
   ceiling, floor, and order of magnitude: is the hoped-for effect physically available at all? An idea that
   cannot clear a known threshold, or that needs a quantity to exceed a hard bound, is a fast,
   well-evidenced NO-GO. State the number.
3. **Locate the crux.** Name the single hardest or most-uncertain part, the thing most likely to sink the
   idea: a required assumption, an unproven mechanism, a measurement at the edge of feasibility. Name the
   cheapest check that would de-risk it, the killer experiment, static probe, or back-of-envelope that,
   done first, settles the biggest doubt. This is usually the highest-value output of the assessment.
4. **Prior art & analogy** (compose `literature-review`, or a quick targeted search). Has this been tried,
   and if it was abandoned, why? What is the closest solved problem, and does its approach transfer? Cite
   real sources, and run `cite-check` on anything load-bearing. "I don't recall seeing it" is not evidence
   that an idea is novel.
5. **Weigh worth.** Payoff if it works (the capability, decision, or new prediction it would enable) ×
   tractability × cost / risk / time. Is there a cheaper decisive experiment that should come first? Weigh
   compute and effort, not coding time, which is routinely mis-estimated. A high-payoff long shot with a
   cheap de-risking check can beat a safe, low-value grind.
6. **Alternatives & push-back.** Is there a stronger version of the idea, or a simpler route to the same
   goal? Offer it. The best assessment is sometimes "yes, but do this adjacent thing instead."
7. **Verdict — grade it, with the premise exposed.** Return one of:
   - **GO** — plausibly solvable and worth it; the crux is acceptable. Hand to `frame-problem`.
   - **DE-RISK-FIRST** — promising, but gated on the crux: do the cheap check from step 3 before
     committing. This is the most common honest verdict.
   - **NO-GO** — not worth it as posed: it cannot clear the ceiling, the crux is a wall, it is already
     solved, or a cheaper alternative dominates. Say so plainly, with the evidence.
   State the verdict's confidence and the load-bearing assumptions it rests on (an assumed parameter, a
   feasibility estimate). A different assumption may flip the verdict, so the user sees the hinge.

## In a campaign — advisory only
When invoked inside a running or forming campaign, or by `new-campaign` as a pre-scaffold check,
`assess-idea` is advisory. It records its verdict as a `record-decision` entry with a revisit-if trigger,
and it never blocks scaffolding or a run. The human decides; the skill informs. Problem selection stays
collaborative even when the loop is otherwise autonomous.

## Output
A short, structured take. The headline is the crux and the cheapest de-risking check. Then the a-priori
bound, the worth weighing, any stronger alternative, and the graded verdict with its confidence and
assumptions. Standalone: a message. In a campaign: a `record-decision` entry.

## Composition
- `dimensional-analysis` — the a-priori bound (step 2), the cheapest correctness and feasibility filter.
- `frame-problem` — the hand-off on a `GO`; it plans the how, `assess-idea` decides the whether.
- `literature-review` / a targeted search + `cite-check` — prior art and analogy (step 4).
- `verify` — when a factual claim underlies the idea, check that claim before trusting the case for it.
- `record-decision` — log the verdict and its revisit-if trigger (campaign/advisory mode).
- `new-campaign` — may compose this as an optional advisory pre-check before scaffolding.

## The failure mode to guard against
**Motivated optimism**: the pull to encourage an idea because it is the user's, or because it might work.
Guard it as `verify` guards against treating convergence as correctness. Make the case against the idea
explicitly, name the crux, and give the number. An encouraging answer that skips step 2 is the failure this
skill replaces.

## Checklist
- [ ] The idea and a concrete success criterion are restated (clarified with the user if fuzzy).
- [ ] Bounded a priori: the ceiling/floor/order is a number, and physical availability is checked.
- [ ] The crux (hardest or most-uncertain part) is named, with the cheapest check that would de-risk it.
- [ ] Prior art / closest solved problem considered; load-bearing claims cited (`cite-check`).
- [ ] Worth weighed (payoff × tractability × cost/risk); a cheaper decisive test surfaced if one exists.
- [ ] A stronger or simpler alternative offered where there is one.
- [ ] A graded verdict (GO / DE-RISK-FIRST / NO-GO) with confidence and load-bearing assumptions stated.
- [ ] In a campaign: recorded as advisory (`record-decision`), not a block.
