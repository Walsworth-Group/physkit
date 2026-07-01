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

Most wasted research effort is decided at the very start: a problem pursued because it sounded exciting, not
because anyone checked whether it was *solvable* or *worth it*. This skill is the honest triage for that
moment. It is the counterpart to `verify`: where `verify` assumes a *result* is wrong until independently
proven right, `assess-idea` assumes an *idea* is not worth doing until the case is made — and it is **licensed
to disappoint.** "Truth over excitement" applies to idea selection too: a well-evidenced "this won't clear the
ceiling" or "this is already solved" is a success, not a failure of nerve.

> **Creativity is not the enemy of rigor.** This is not a filter for timidity — bold, unusual ideas are
> exactly what good research needs. The job is not to talk the user out of ambition; it is to find the *cheapest
> path to the truth* about whether the idea works, and to name the one thing most likely to sink it. Kill the
> idea as hard as you would build it — then, if it survives, pursue it with both feet.

## When to use / not use
- **Use** on a raw idea or direction, *before* investing: "what do you think of this?", "is this worth it?",
  "is this feasible?", "should we work on X?" — and as an optional **advisory pre-check before `new-campaign`**
  scaffolds a loop around an unvetted idea.
- **`frame-problem`** instead once the idea is a *go* — that skill plans *how* to do a problem you've decided
  to do (physics inventory, verification plan, decomposition). `assess-idea` is **upstream** of it and lighter:
  it decides *whether* to do it at all. Hand off to `frame-problem` on a `go`.
- **`verify`** instead when you already have a *result* to check. **`new-campaign`** to scaffold a decided loop.
- **Collaboration first.** Problem selection is a **shared** decision — surface the assessment and its reasoning
  and let the researcher choose; don't unilaterally kill or greenlight someone's idea. The verdict is a
  recommendation with its evidence, not a verdict on the researcher.

## The assessment
Work these in order; stop early on a decisive result (a hard physical no in step 2 ends it). Keep it
proportional — a quick idea gets a quick pass; a big commitment earns the full battery.

1. **Restate the idea and what success would look like.** In your own words: the claim or goal, and the
   concrete criterion by which it would count as *working* (decision 3). If the idea is fuzzy or you're filling
   in intent, **clarify with the user first** (the always-on Stage-0 stance) — you cannot assess a moving target.
2. **Bound it a priori** (compose `dimensional-analysis`, or a light `frame-problem` pass). Compute the
   **ceiling / floor / order of magnitude**: *is the hoped-for effect even physically available?* An idea that
   cannot clear a known threshold — or that needs a quantity to exceed a hard bound — is a fast, well-evidenced
   **no-go**. State the number, not a vibe.
3. **Locate the crux.** Name the **single hardest or most-uncertain part** — the thing most likely to sink it
   (a required assumption, an unproven mechanism, a measurement at the edge of feasibility) — and the
   **cheapest check that would de-risk it**: the killer experiment, static probe, or back-of-envelope that,
   done first, would settle the biggest doubt. This is usually the highest-value output of the whole assessment.
4. **Prior art & analogy** (compose `literature-review`, or a quick targeted search). Has this been tried —
   and if it was abandoned, *why*? What is the closest **solved** problem, and does its *approach* transfer?
   Cite real sources (`cite-check` anything load-bearing); "I don't recall seeing it" is not evidence it's novel.
5. **Weigh worth.** Payoff *if it works* (what it would **enable** — a capability, a decision, a new prediction)
   × **tractability** × **cost / risk / time**. Is there a **cheaper decisive experiment** that should come
   first? Weigh *compute and effort*, not (mis-estimated) coding time. A high-payoff long-shot with a cheap
   de-risking check can beat a safe, low-value grind.
6. **Alternatives & push-back.** Is there a **stronger version** of the idea, or a **simpler route** to the same
   goal? Offer it. Sometimes the best assessment is "yes, but do this adjacent thing instead."
7. **Verdict — grade it, with the premise exposed.** Return one of:
   - **GO** — plausibly solvable and worth it; the crux is acceptable. Hand to `frame-problem`.
   - **DE-RISK-FIRST** — promising, but gated on the crux: do the cheap check in step 3 *before* committing.
     (The most common honest verdict.)
   - **NO-GO** — not worth it as posed: it can't clear the ceiling, the crux is a wall, it's already solved, or
     a cheaper alternative dominates. Say so plainly, with the evidence.
   State the verdict's **confidence** and the **load-bearing assumptions** it rests on (an assumed parameter, a
   feasibility guess) — a different assumption may flip it, and the user should see the hinge.

## In a campaign — advisory only
When invoked inside a running or forming campaign (or by `new-campaign` as a pre-scaffold check), `assess-idea`
is **advisory**: it records its verdict as a `record-decision` (with a *revisit-if* trigger), and it **never
blocks** scaffolding or a run. The human decides; the skill informs. This keeps problem-selection collaborative
even when the loop is otherwise autonomous.

## Output
A short, structured take — **crux + the cheapest de-risking check** (the headline), the a-priori bound,
the worth weighing, any stronger alternative, and the **graded verdict with confidence + assumptions**.
Standalone: a message. In a campaign: a `record-decision` entry.

## Composition
- **`dimensional-analysis`** — the a-priori bound (step 2), the cheapest correctness/feasibility filter.
- **`frame-problem`** — the hand-off on a `GO` (it plans the how); `assess-idea` decides the whether.
- **`literature-review`** / a targeted search + **`cite-check`** — prior art and analogy (step 4).
- **`verify`** — if a *factual claim* underlies the idea, check that claim before trusting the case for it.
- **`record-decision`** — log the verdict + revisit-if (campaign/advisory mode).
- **`new-campaign`** — may compose this as an optional advisory pre-check before scaffolding.

## The failure mode to guard against
**Motivated optimism** — the pull to encourage an idea because it's the user's, or because "it might work."
Guard it the way `verify` guards convergence-≠-correctness: make the case *against* explicitly, name the crux,
and give the number. A cheerful "sounds great!" that skips step 2 is the anti-pattern this skill exists to replace.

## Checklist
- [ ] The idea and a concrete success criterion are restated (clarified with the user if fuzzy).
- [ ] Bounded a priori — the ceiling/floor/order is a number, and physical availability is checked.
- [ ] The crux (hardest/most-uncertain part) is named, with the cheapest check that would de-risk it.
- [ ] Prior art / closest solved problem considered; load-bearing claims cited (`cite-check`).
- [ ] Worth weighed (payoff × tractability × cost/risk); a cheaper decisive test surfaced if one exists.
- [ ] A stronger or simpler alternative offered where there is one.
- [ ] A graded verdict (GO / DE-RISK-FIRST / NO-GO) with **confidence + load-bearing assumptions** stated.
- [ ] In a campaign: recorded as advisory (`record-decision`), not a block.
