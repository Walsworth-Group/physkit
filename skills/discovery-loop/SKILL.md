---
name: discovery-loop
description: >-
  LLM discovery search over programs and rules (campaign archetype G).
---

# discovery-loop — evolve an interpretable artifact, then certify it

Most of the kit optimizes a fixed method's parameters (archetypes A–F). This skill discovers the method
itself: a program, a symbolic law, a heuristic, a design rule, or a control policy, evolved by an LLM
acting as the variation operator in a search loop (the FunSearch lineage: LLM-generate → evaluate →
select → reflect → repeat). This is **archetype G**. The deliverable is an **interpretable, generalizing
artifact**: human-readable code or symbolic form a physicist can check, extract a rule from, and edit.

Two framing points bound expectations:
- LLMs are weak at raw numerical optimization. Their value is flexibility, exploration, and intent:
  proposing structurally novel candidates and writing interpretable code, not sample-efficient
  number-crunching. To tune a fixed set of continuous knobs, use a classical optimizer, not this loop.
- On a mature, expert-tuned problem the realistic outcome is rediscovery of the state of the art plus a
  small advance. Bound expectations a priori; a clean rediscovery is a validation, not a failure.

---

## Step 0 — set the three design axes (and what you're evolving)
A discovery loop has three orthogonal choices plus the genome. Decide each deliberately; they matter more
than prompt wording.

1. **The object evolved (the genome).** The LLM is a domain-agnostic variation operator over any text
   genome: an equation, a code function, a parameter string, a design spec, a controller. Pick the
   representation that fits the physics; representation often dominates the optimizer, and code-space
   search can beat a binary-vector genetic algorithm on the same problem. Prefer one a trusted checker can
   verify and a human can read.
2. **The search engine**, by landscape:
   - **population / island** (diversity, the EoH/ReEvo family) — a general default; islands resist
     premature convergence.
   - **tree / MCTS / PUCT** — preserves early-poor-but-promising candidates that population methods cull;
     use on deceptive landscapes.
   - **neighborhood / local** — for refining a strong incumbent.

   Rank-normalize scores before any exploration rule, so one exploration constant transfers across tasks
   and metric scales.
3. **The feedback memory** — how accumulated insight conditions generation, a capability/cost gradient:
   - **prompt only**: cheapest, and brittle because generation degrades in long ever-growing prompts. Keep
     it consolidated.
   - **reflections**, or verbal gradients (ReEvo-style): separate generator and reflector roles. The
     reflector analyzes why A beat B before the generator mutates, and accumulates long-term hints.
   - **an evolving concept library** (LaSR-style): abstract elite patterns into named concepts (in physics,
     often literal physical principles) that condition future generation. Curatable and inspectable.

   Heavier memory buys capability at more cost and contamination risk. Default to reflections; use a
   concept library when reusable structure is the point.
4. *(Advanced)* **generator self-improvement** — a frozen generator (the default), or fine-tuning it on
   its own successful traces. Fine-tuning is heavyweight and carries a contamination and
   overfitting hazard: do not use it until the frozen loop works and its cost is justified.

**Scope generation to the lever functions ("function-only").** The LLM writes only the mutable lever
functions. The harness, evaluator, and data acquisition stay **FROZEN and READ-ONLY**.
Function-only generation outperforms whole-pipeline generation, and is the discovery-loop instance of the
kit's FROZEN/READ-ONLY/MUTABLE tiering.

---

## The loop
```
SEED (a trivial or expert heuristic as in-context init) → then repeat:
  1. GENERATE   — LLM proposes/mutates the genome (function-only), conditioned on the feedback memory.
                  Operators: mutate (bounded — change x% of code), recombine (compare two parents,
                  articulate the difference, merge), or reflect-then-edit.
  2. PARSE/GATE — parse into a canonical structure (e.g. an expression tree); reject unparseable,
                  degenerate, or infeasible candidates BEFORE scoring. For simulator-scored search, a
                  hard convergence/feasibility gate (a non-converging solve scored anyway just
                  optimizes noise). Enforce a parsimony/complexity constraint DURING search, not after.
  3. EVALUATE   — score with the FROZEN evaluator on a representative benchmark; count the evaluation
                  (budget is a first-class metric).
  4. REFLECT    — update the feedback memory: the reflector says why recent candidates scored as they did
                  (verbal gradient), or distills a new named concept. Carry it forward in CONSOLIDATED form.
  5. SELECT     — population/island/tree update; preserve diversity (don't collapse to one lineage early).
  6. STOP?      — on diminishing returns (convergence detected), not a fixed budget burned blindly.
```
**Alternate explore and exploit:** a global evolutionary/reflective mode for breadth, a local refine mode
for depth. Prove the synergy by ablation. For numeric-heavy physics use **explore-with-LLM,
exploit-with-classical**: the LLM scopes an unfamiliar space and yields interpretable structure, then lift
that structure into a faster specialized optimizer (typed GP or a classical method). Alternatively the LLM
writes the program skeleton and a classical optimizer tunes its numeric constants.

---

## Spend the evaluation budget well
Discovery loops are evaluation-hungry. When evaluations are expensive, follow
`docs/reference/expensive-evaluation.md`:
- Track and report the number of evaluations, and benchmark sample-efficiency against a classical baseline
  (BO, RL, NSGA-II, GP). "LLM as optimizer" is a hypothesis: make it beat a real baseline; do not credit
  the apparatus by assumption.
- Discover on small instances, benchmark on large. Scale generalization doubles as an acceptance test.
- Stop on diminishing returns. Pre-screen with a cheap proxy before a full-fidelity evaluation. Validate
  any surrogate against the true evaluator; surrogate error misleads the search.

## Certify discoveries — discover-then-certify
The search is an untrusted stochastic proposer: warrant comes from an **independent** check, not the
generator. Compose `verify` and add the discovery-specific gates:
- **Discover-then-certify.** Where an independent exact or certifying method exists, prefer a certificate
  over a re-run. State explicitly what is certified and what is conjectured, and over what range. An interpretable
  artifact often enables a formal check, such as a Lyapunov stability proof on a discovered control law:
  pick representations a trusted checker can verify.
- **Re-discover the known SOTA or ground truth as a validation gate** before trusting a novel improvement:
  the loop must recover the known-good answer first.
- **Generalize-across-regimes / extrapolation test.** Run the discovered artifact on larger and unseen
  instances and across regimes (geometries, parameters), not just the training set.
- **Anti-memorization.** An LLM can reproduce material from its training data. Use black-box prompting,
  withholding the problem's identity and name, and re-test on synthetic, un-memorizable instances when the
  benchmark may be in training data.
- **Novelty / equivalence check.** Confirm a discovery is new at the component level, not a restatement of
  a known method.
- **Ablate the machinery and test multi-LLM robustness.** Prove the search and reflection beat a direct-LLM
  baseline and attribute gains to components. Test across more than one model backbone. Report run
  variance, and the outcome distribution and stability over repeats, not the best run alone.
- **Credit explanatory over descriptive discovery.** A recovered mechanism (project-overview-level
  understanding) counts for more than a metric move. Evaluate the process, not only the outcome.
- **State the limit of the warrant.** Physical-science claims rarely have a proof-checker, so warrant is
  bounded by the strength of the independent re-derivation, higher-fidelity simulation, or experiment. Name
  that bound; never claim certification you do not have.

## The deliverable is interpretable — extract the rule
An LLM is used instead of a black-box optimizer because its artifact is human-readable. Realize that
value:
- **Move the black box to design-time.** Use the LLM to synthesize an interpretable program, then deploy
  and verify the artifact, not the model.
- **Extract the design rule** into `PROJECT.md` / the report: the recovered principle, not only the code.
- **Human-in-the-loop edit-and-re-evolve.** An interpretable artifact can be read, improved by a domain
  expert, and fed back. A/B the human edit; support this as a first-class flow, not a fallback.

## Cautions (discovery-specific failure modes)
- **Reward-hacking the evaluator.** The loop exploits any evaluator inaccuracy. Cross-check winners against
  higher fidelity (`SIMULATION_VALIDATION.md` §5: feasibility gate + dual direct-and-downstream objective).
- **Over-prompting on rugged landscapes.** Physics priors help on structured landscapes and over-constrain
  exploration on noisy ones. Treat domain-prompt richness as a lever to test, not a free win.
- **Complexity creep.** Repeated LLM prompting adds needless complexity. Monitor the complexity trajectory
  (AST size or parameter count over generations) and enforce parsimony actively. Complexity rising while
  performance stays flat requires intervention.
- **Brittle long feedback prompts.** Keep reflection memory structured and consolidated, not an
  ever-growing transcript. The kit's slim-core and consolidation discipline applies here.
- **Bigger and hotter is not always better.** Test model size and temperature; a smaller, cooler model can
  win on constraint satisfaction and consistency.
- **Reward shaping is load-bearing.** The metric dominates success and is not automatic. Design it with
  frozen-metric care so the loop cannot win by gaming a degenerate optimum; an evaluator found wrong
  mid-campaign is revised as a declared metric epoch (`campaign.md` §The ONE metric), never quietly.

## Audit artifacts
- A **breakthrough plot** (best score vs number of evaluations) and the **saved search tree / lineage** of
  the elite artifact: the discovery-loop analogue of the scoreboard + figures.
- The **complexity trajectory**, a `campaign-status` health metric (over-engineering detector).
- Every elite artifact saved by label with its evaluation, reflection trace, and snapshot
  (reproducibility).

## Composition
- `new-campaign` scaffolds archetype G, the loop its campaign definition runs; its FROZEN evaluator and
  benchmark are the campaign's frozen metric.
- `verify` certifies each promoted discovery (discover-then-certify; anti-memorization; novelty).
- `correctness-suite` guards the FROZEN evaluator and harness.
- `docs/reference/expensive-evaluation.md` governs the budget; `SIMULATION_VALIDATION.md` §5 governs
  simulator-scored search.
- `report` documents the discovered artifact, its design rule, and its
  certified-vs-conjectured scope; `record-decision` captures why the genome, search engine, and memory
  were chosen.

## Before you trust a discovery — checklist
- [ ] The three axes (engine · memory · generator) and the genome were chosen deliberately and recorded.
- [ ] Generation is function-only; harness/evaluator/data are FROZEN.
- [ ] A parse/feasibility gate and a parsimony constraint run during search.
- [ ] Evaluation budget tracked; sample-efficiency benchmarked vs a classical optimizer; diminishing-returns stop.
- [ ] The discovery was certified independently (certificate where possible; certified-vs-conjectured stated).
- [ ] Re-discovers known SOTA; generalizes/extrapolates across regimes; passes anti-memorization + novelty checks.
- [ ] Machinery ablated vs a direct-LLM baseline; tested across ≥2 model backbones; stability reported.
- [ ] The artifact is interpretable; its design rule is extracted into `PROJECT.md` / the report.
