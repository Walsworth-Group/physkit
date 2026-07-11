---
name: discovery-loop
description: >-
  Run an LLM-in-the-loop discovery search — the FunSearch-lineage loop that evolves an interpretable
  artifact (a program, a symbolic equation, a heuristic, a design rule, a controller) against a frozen
  evaluator, rather than tuning parameters. Use when the goal is to DISCOVER a method/expression/algorithm,
  not optimize a fixed one: phrasings like "evolve a heuristic for...", "symbolic regression with an LLM",
  "discover an algorithm/closure/acquisition function for...", "search program space for...", or setting up
  the discovery archetype (G). It sets the three design axes (search engine; feedback memory —
  prompt/reflections/concept-library; generator self-improvement), scopes generation to the lever functions
  (harness/data frozen), spends the evaluation budget deliberately, certifies discoveries independently, and
  delivers a human-readable artifact with its design rule extracted. Composes new-campaign (archetype G),
  verify (certification), and the expensive-evaluation protocol. The most exploratory skill — read it before
  building any LLM-driven search.
---

# discovery-loop — evolve an interpretable artifact, then certify it

Most of the kit optimizes a *fixed* method's parameters (archetypes A–F). This skill is for the other kind
of goal: **discovering the method itself** — a program, a symbolic law, a heuristic, a design rule, a
control policy — by using an LLM as a variation operator inside a search loop (the FunSearch lineage:
LLM-generate → evaluate → select → reflect → repeat). It is **archetype G**. The deliverable that makes it
worth the trouble is an **interpretable, generalizing artifact**: human-readable code or symbolic form a
physicist can check, extract a rule from, and edit.

Two honest framing points up front, because they set realistic expectations:
- **LLMs are weak at raw numerical optimization.** Their value here is *flexibility, exploration, and
  intent* — proposing structurally novel candidates and writing interpretable code — not sample-efficient
  number-crunching. If the task is "tune these 8 continuous knobs," use a classical optimizer, not this.
- **On a mature, expert-tuned problem, the realistic outcome is "rediscover SOTA + a small advance,"** not a
  miracle. Bound expectations a priori and call a clean rediscovery what it is: a validation, not a failure.

---

## Step 0 — set the three design axes (and what you're evolving)
A discovery loop has three orthogonal choices plus the genome. Decide them deliberately — they matter more
than prompt-fiddling.

1. **The object evolved (the genome).** The LLM is a domain-agnostic variation operator over *any* text
   genome — an equation, a code function, a parameter-string, a design spec, a controller. **Pick the
   representation that fits the physics; representation often dominates the optimizer** (code-space search
   can crush a binary-vector GA on the same problem). Prefer a representation a trusted checker can verify
   and a human can read.
2. **The search engine** (selectable by landscape):
   - **population / island** (diversity, the EoH/ReEvo family) — good general default; islands resist
     premature convergence.
   - **tree / MCTS / PUCT** — preserves early-poor-but-promising candidates that population methods cull;
     good for deceptive landscapes.
   - **neighborhood / local** — when you have a strong incumbent to refine.
   **Rank-normalize scores before any exploration rule** so one exploration constant transfers across tasks
   and metric scales.
3. **The feedback memory** — how accumulated insight conditions generation (a capability/cost gradient):
   - **prompt only** (cheapest, but brittle — LLMs "get lost" in long ever-growing prompts; keep it
     consolidated);
   - **reflections / "verbal gradients"** (ReEvo-style: a *separate generator and reflector role*; the
     reflector analyzes *why* A beat B before the generator mutates — reflection-before-mutation, plus
     accumulated long-term hints);
   - **an evolving concept library** (LaSR-style: abstract elite patterns into *named concepts* — which in
     physics are often literal physical principles — that condition future generation; curatable, inspectable).
   Heavier memory = more capability **and** more cost and contamination risk. Default to reflections; reach
   for a concept library when reusable structure is the point.
4. *(Advanced)* **generator self-improvement** — frozen generator (default) vs fine-tuning the generator on
   its own successful traces (heavyweight; a real contamination/overfitting hazard). Don't reach for this
   until the frozen loop is working and you've justified the cost.

**Scope generation to the lever functions ("function-only").** Let the LLM write **only** the mutable
functions that are the actual levers; keep the harness, the evaluator, and data acquisition **FROZEN and
READ-ONLY**. Function-only generation beats whole-pipeline generation and is the discovery-loop instance of
the kit's FROZEN/READ-ONLY/MUTABLE tiering.

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
**Alternate explore and exploit:** a global evolutionary/reflective mode for breadth and a local refine
mode for depth — and prove the synergy by ablation. A strong pattern for numeric-heavy physics is
**explore-with-LLM, exploit-with-classical**: use the LLM to scope an unfamiliar space and yield
interpretable structure, then lift that structure into a faster specialized optimizer (typed GP / a
classical method), or have the LLM write the program *skeleton* and a classical optimizer tune its numeric
constants.

---

## Spend the evaluation budget well
Discovery loops are evaluation-hungry; when each evaluation is expensive, follow
`docs/protocols/expensive-evaluation.md`:
- **Track and report the number of evaluations**, and **benchmark sample-efficiency against a classical
  baseline** (BO / RL / NSGA-II / GP). "LLM as optimizer" is a *hypothesis* — make it beat a real baseline,
  don't credit the apparatus by assumption.
- **Discover on small instances, benchmark on large** (scale generalization doubles as an acceptance test).
- **Diminishing-returns stop**; pre-screen with a cheap proxy before a full-fidelity evaluation; validate
  any surrogate against the true evaluator (surrogate errors mislead the search).

## Certify discoveries — discover-then-certify
The search is an *untrusted stochastic proposer*; warrant comes from an **independent** check, not from the
generator. Compose **`verify`** and add the discovery-specific gates:
- **Discover-then-certify.** Where an independent exact/certifying method exists, prefer a *certificate*
  over a re-run, and **state explicitly what is certified vs conjectured**, and over what range. (An
  interpretable artifact often *enables* a formal check — e.g. a Lyapunov stability proof on a discovered
  control law: pick representations a trusted checker can verify.)
- **Re-discover the known SOTA / ground truth as a validation gate** before trusting a novel improvement —
  "can the loop recover the known-good answer?"
- **Generalize-across-regimes / extrapolation test** — run the discovered artifact on larger/unseen
  instances and across regimes (geometries, parameters), not just the training set.
- **Anti-memorization (LLMs regurgitate their training data).** Use **black-box prompting** (withhold the
  problem's identity/name) and **re-test on synthetic, un-memorizable instances** when the benchmark may be
  in training data.
- **Novelty / equivalence check** — confirm a "discovery" is genuinely new at the component level, not a
  cosmetic restatement of a known method.
- **Ablate the machinery + multi-LLM robustness** — prove the search/reflection actually beats a simple
  direct-LLM baseline and attribute gains to components; test across more than one model backbone and report
  run variance. Report the **outcome distribution and stability** over repeats, not just the best run.
- **Credit explanatory over descriptive discovery** — a recovered *mechanism* (a `PHYSICS.md`-level
  understanding) counts for more than a metric move; evaluate the process, not only the outcome.
- **Honest limit:** physical-science claims rarely have a proof-checker, so warrant is bounded by the
  strength of the independent re-derivation / higher-fidelity simulation / experiment — name that bound;
  don't overclaim certification you don't have.

## The deliverable is interpretable — extract the rule
The point of using an LLM (vs a black-box optimizer) is that the discovered artifact is **human-readable**.
Realize that value:
- **Move the black box to design-time:** use the LLM to *synthesize* an interpretable program, then deploy
  and verify the *artifact*, not the model.
- **Extract the design rule** into `PHYSICS.md` / the report — the recovered principle, not just the code.
- **Human-in-the-loop edit-and-re-evolve:** an interpretable artifact can be read, improved by a domain
  expert, and fed back — A/B the human edit. Support this as a first-class flow, not a fallback.

## Cautions (discovery-specific failure modes)
- **Reward-hacking the evaluator** — the loop will exploit any evaluator inaccuracy; cross-check winners
  against higher fidelity (`SIMULATION_VALIDATION.md` §5: feasibility gate + dual direct+downstream objective).
- **Over-prompting hurts on rugged landscapes** — injecting physics priors helps on structured landscapes
  but *over-constrains exploration* on noisy ones. Treat domain-prompt richness as a lever to **test**, not
  a free win.
- **Complexity creep** — repeated LLM prompting adds needless complexity; **monitor the complexity
  trajectory** (AST size / parameter count over generations) and enforce parsimony actively. Complexity-up +
  performance-flat ⇒ intervene.
- **Brittle long feedback prompts** — keep reflection memory structured and consolidated, not an
  ever-growing transcript (this is why the kit's slim-core / consolidation discipline applies here too).
- **Bigger/hotter isn't always better** — test model size and temperature; a smaller, cooler model
  sometimes wins on constraint satisfaction and consistency.
- **Reward shaping is load-bearing** — the metric dominates success and is not automatic; design it
  deliberately (frozen-metric care) so the loop can't win by gaming a degenerate optimum.

## Audit artifacts
- A **breakthrough plot** (best score vs number of evaluations) and the **saved search tree / lineage** of
  the elite artifact — the discovery-loop analogue of the scoreboard + figures.
- The **complexity trajectory** (a `campaign-status` health metric — over-engineering detector).
- Every elite artifact saved by label with its evaluation, reflection trace, and snapshot (reproducibility).

## Composition
- **`new-campaign`** scaffolds archetype G (this is the loop its `charter.md` runs); the FROZEN evaluator +
  benchmark are the campaign's frozen metric.
- **`verify`** certifies each promoted discovery (discover-then-certify; anti-memorization; novelty).
- **`correctness-suite`** guards the FROZEN evaluator/harness itself.
- **`docs/protocols/expensive-evaluation.md`** governs the budget; **`SIMULATION_VALIDATION.md` §5** governs
  simulator-scored search.
- **`report` / `final-report`** documents the discovered artifact, its design rule, and its certified-vs-
  conjectured scope; **`record-decision`** captures the *why* of the genome/search-engine/memory choices.

## Before you trust a discovery — checklist
- [ ] The three axes (engine · memory · generator) and the genome were chosen deliberately and recorded.
- [ ] Generation is function-only; harness/evaluator/data are FROZEN.
- [ ] A parse/feasibility gate + a parsimony constraint run *during* search.
- [ ] Evaluation budget tracked; sample-efficiency benchmarked vs a classical optimizer; diminishing-returns stop.
- [ ] The discovery was **certified independently** (certificate where possible; certified-vs-conjectured stated).
- [ ] Re-discovers known SOTA; generalizes/extrapolates across regimes; passes anti-memorization + novelty checks.
- [ ] Machinery ablated vs a direct-LLM baseline; tested across ≥2 model backbones; stability reported.
- [ ] The artifact is interpretable; its design rule is extracted into `PHYSICS.md` / the report.
