---
id: context-economy
kind: reference-doc
layer: shared
load: on-demand
load_trigger: When deciding what to keep loaded vs stream on demand, how to tier docs (CORE vs REFERENCE), or how to keep a long-running agent's working context lean.
frozen: false  # unfrozen by a recorded decision — stays doctrine, but how much context helps tracks model capability
addresses: [7]
status: new
review: living
---

# Context economy — keep the loaded core tiny, stream depth on demand

An overloaded agent performs worse. Every token of standing context competes for attention with the task.
A bloated working set degrades reasoning, hides the important among the routine, and slows everything down.
The kit therefore treats what is loaded as a resource to spend deliberately. This is part of the frozen
core and must not be traded away for short-term convenience. The rule: keep a tiny always-loaded core, and
pull depth only when the situation calls for it.

## The tiering rule
Three tiers, by how often each is needed:
- CORE (always loaded): the slim spine — identity, the frozen non-negotiables, the working loop, and a
  routing table to everything else. It must stay short by design; if it grows, something in it belongs in
  a lower tier. ([`CORE.md`](../CORE.md).)
- REFERENCE (on-demand depth): the deep dives (this doc,
  `SIMULATION_VALIDATION.md`, the skills). Loaded when a trigger fires, never by default: a situation, a
  skill invocation, or a question that needs the depth.
- METADATA (the map): the `DOCTRINE_INDEX.md` and each artifact's `load_trigger`, so the agent can find
  the right file without reading everything. The index is what keeps on-demand loading navigable.

The plugin mechanism makes this concrete: only a skill's `name` and `description` sit in context until it
is invoked, and the body and assets load on demand. That is why the dual-use design works. A general
session never pays the context cost of campaign material (`layer: campaign`, `load: on-demand`).

## How to keep a working session lean
- Lead with a routing table, not the content. A one-line "when X → load Y" pointer costs almost nothing
  and defers the cost until X happens.
- Split records into append-only and working. Keep the full narrative in a logbook that is never trimmed
  and never read in full, so it cannot bloat the loop, and a bounded working journal — where things
  stand, live hypotheses, what to try next, open questions — that you bring up to date rather than
  append to. The logbook holds the history. The same discipline governs the scoreboard and the
  diagnostics logs.
- Summarize forward. When a thread closes, replace its detail with a one-line outcome and a pointer to
  where the detail lives. Carry conclusions, not transcripts.
- Distill in the background. On a long run, have a lighter-model sub-agent periodically extract decisions,
  corrections, and open threads into durable notes (the journal, or a `notes/` file) so they survive a
  context reset without spending top-tier tokens on bookkeeping. At a context limit, compound rather than
  compact: distill the durable learnings and resume clean instead of lossily summarizing the raw
  transcript.
- Stream, don't preload. Read a reference doc, a paper, or a data file when the step needs it, and release
  it afterward. Do not hold material against possible future need.
- Keep skill descriptions tight. A skill's description is always loaded, so it must be specific enough to
  trigger correctly and no longer than that. Every skill description is a standing context cost.

## Delegate to sub-agents (parallelize, and protect the main context)
A sub-agent runs a bounded subtask in its own context window and returns only its conclusion, so the main
thread never pays for the intermediate reasoning. Use sub-agents as both a speed lever and a context lever:
- Parallelize independent work. When steps do not depend on each other, dispatch them concurrently,
  several Agent calls in one turn, instead of serially: searching multiple files, verifying a batch of
  citations, running independent checks, harvesting evidence for distinct lever groups.
- Delegate to keep the loop lean. A search that would pull many files into context, or a read-heavy
  survey, belongs in a sub-agent that returns the answer rather than the raw material. Summarize forward
  across agents: carry conclusions, not transcripts.
- Independent verification is the prime use. A fresh agent that never saw the generating reasoning is the
  mechanism-diverse checker: warrant rides on the checker, not the generator (CORE constitution). The `verify` and
  `cite-check` skills already spawn refuters and checkers this way.
- Scope tight, return small. Give each sub-agent a precise task and require a compact, structured result.
  A sub-agent that hands back its whole transcript defeats the purpose.
- Pass the why, not just the instruction. Every delegation prompt carries the goal, the context, and what
  the result is for: what it gates, who reads it, the stakes. Motivation shifts behavior more reliably
  than bare commands (pillar 8). One exception: an independent verifier gets the stakes but never the
  generating reasoning or the expected answer (see `verify` §4).
- Check independence before you fan out. Parallelize only what is provably independent. Before
  dispatching, analyze the data, file-write, and shared-state dependencies: two sub-agents must not write
  the same file, mutate shared state, or consume each other's output concurrently. If step B needs step
  A's output, chain them; if two tasks would touch the same artifact, sequence them or give each its own
  workspace (a git worktree, or a separate output directory). When unsure, sequence. A race corrupts the
  ledger silently and is hard to detect after the fact.

## Model tiering — spend reasoning where it counts
Sub-agents do not all need the strongest model. Match the model to the task, the same way evaluation
budget is matched to the question (`spend evaluations well`, `discovery-loop`):
- Lighter tier (mechanical, checkable): file and literature search and evidence harvest; citation
  existence and metadata checks; template and scaffold fills after the spec is frozen; the LaTeX
  compile-fix loop and figure generation from a fixed spec; journal and logbook summarize-forward; data
  loading and format conversion. Each returns a result a deterministic gate or the main agent can check.
- Strong tier (judgment, physics, integrity): the main hypothesize→evaluate→decide loop; `frame-problem`,
  `derive`, `simulation-design`, hard `debug`; metric design; the discovery, experiment-design, and
  model-selection strategy.
- The verification verdict is never downgraded. `verify`'s refutation and CONFIRMED / PROVISIONAL / …
  grading must run on a model at least as capable as the one that produced the result. A verifier too
  weak to catch the error yields false CONFIRMs. Using a different capable model adds mechanism diversity,
  a second set of failure modes, on top of the independence.

Two guardrails keep tiering safe. First, hand a light model only work whose output is checkable by a
self-test, `validate_campaign.py`, a schema, or the main agent's own read, so that a slip surfaces
instead of silently corrupting the ledger. Second, tier by mechanical versus judgment, not by how tedious
the task feels. Sub-agent dispatch tools take a per-sub-agent `model` (and `effort`) override. Do not
hard-code specific model names in durable docs; they age.

## The tension to manage
Context economy trades against completeness: too lean and the agent misses something it needed, too rich
and it drowns. Resolve the trade by tiering, not by cutting. Move depth to REFERENCE and leave a pointer
rather than deleting it. When in doubt, ask whether the material must be present in every turn or whether
a trigger can pull it when relevant. Most material is the latter.

## Pointers
CORE (the spine it governs); `DOCTRINE_INDEX.md` (the metadata layer and the `load` / `load_trigger`
fields); CORE working-loop step 3 (sub-agents and model tiering) and `discovery-loop` for the
evaluation-budget analogue; `verify`
and `cite-check` (the sub-agent verification and fan-out pattern); `handoff`
(cold-resume without reloading everything); the campaign logbook/journal split.
