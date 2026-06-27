---
id: context-economy
kind: reference-doc
layer: shared
load: on-demand
load_trigger: When deciding what to keep loaded vs stream on demand, how to tier docs (CORE vs REFERENCE), or how to keep a long-running agent's working context lean.
frozen: true
addresses: [7]
status: new
review: living
---

# Context economy — keep the loaded core tiny, stream depth on demand

An overloaded agent performs worse. Every token of standing context competes for attention with the task,
and a bloated working set degrades reasoning, hides the important among the routine, and slows everything
down. So the kit treats **what is loaded** as a resource to spend deliberately — this is part of the frozen
core (it must not be "optimized away" for short-term convenience). The principle is simple: **keep a tiny
always-loaded core; pull depth only when the situation calls for it.**

## The tiering rule
Three tiers, by how often they're needed:
- **CORE (always loaded):** the slim spine — identity, the frozen non-negotiables, the working loop, and a
  **routing table** to everything else. It must stay short on purpose; if it grows, something belongs in a
  lower tier. ([`CORE.md`](../CORE.md).)
- **REFERENCE (on-demand depth):** the full doctrine and the deep dives (this doc, `PRINCIPLES.md`,
  `SIMULATION_VALIDATION.md`, the skills). Loaded when a trigger fires — a situation, a skill invocation, a
  question that needs the depth — not by default.
- **METADATA (the map):** the `DOCTRINE_INDEX.md` and each artifact's `load_trigger`, so the agent can find
  the right file without reading everything. The index is how on-demand loading stays navigable.

The plugin mechanism makes this concrete: only a skill's `name` + `description` sit in context until it's
invoked; the body and assets load on demand. That is why the dual-use design works — a general session never
pays the context cost of campaign material (`layer: campaign`, `load: on-demand`).

## How to keep a working session lean
- **Lead with a routing table, not the content.** A one-line "when X → load Y" pointer costs almost
  nothing and defers the cost until X actually happens.
- **Append-only, rarely-read records.** Keep the full narrative in a logbook that is **never trimmed and
  never read in full** (so it can't bloat the loop), and a **lean working journal** (recent entries + open
  threads) you drop from freely — the logbook holds the history. The same discipline governs the scoreboard
  and diagnostics logs.
- **Summarize forward.** When a thread closes, replace its detail with a one-line outcome + a pointer to
  where the detail lives. Carry conclusions, not transcripts.
- **Distill in the background, cheaply.** On a long run, have a *lighter-model* sub-agent periodically
  extract decisions, corrections, and open threads into durable notes (the journal / a `notes/` file) so
  they survive a context reset without spending top-tier tokens on bookkeeping. At a context limit,
  **compound, don't just compact**: distill the durable *learnings* and resume clean, rather than lossily
  summarizing the raw transcript.
- **Stream, don't preload.** Read a reference doc, a paper, or a data file *when the step needs it*, and
  release it after — don't hold everything "just in case."
- **Tight skill descriptions.** A skill's description is always-loaded, so it must be specific enough to
  trigger correctly but no longer than it needs to be — every skill description is a standing context cost.

## Delegate to sub-agents (parallelize, and protect the main context)
A sub-agent runs a bounded subtask in its **own** context window and returns only its conclusion, so the
main thread never pays for the intermediate reasoning. Use them as both a speed lever and a context lever:
- **Parallelize independent work.** When steps don't depend on each other — searching multiple files,
  verifying a batch of citations, running independent checks, harvesting evidence for distinct lever
  groups — dispatch them concurrently (several Agent calls in one turn) instead of serially.
- **Delegate to keep the loop lean.** A search that would pull dozens of files into context, or a
  read-heavy survey, belongs in a sub-agent that returns the *answer*, not the raw material — the
  summarize-forward rule applied across agents: carry conclusions, not transcripts.
- **Independent verification is the prime use.** A fresh agent that never saw the generating reasoning is
  the ideal mechanism-diverse checker — warrant rides on the checker, not the generator (Context 2). The
  `verify` and `cite-check` skills already spawn refuters/checkers this way.
- **Scope tight, return small.** Give each sub-agent a precise task and ask for a compact, structured
  result; a sub-agent that hands back its whole transcript defeats the purpose.
- **Check independence before you fan out.** Parallelize only what is *provably* independent: before
  dispatching, analyze the **data, file-write, and shared-state dependencies** — two sub-agents must not
  write the same file, mutate shared state, or consume each other's output concurrently. If step B needs
  step A's output, chain them; if two tasks would touch the same artifact, sequence them or give each its
  own workspace (a git worktree / separate output dir). When unsure, sequence — a race corrupts the ledger
  silently and is hard to detect after the fact.

## Model tiering — spend reasoning where it counts
Sub-agents don't all need the strongest model. Match the model to the task, the same way you match
evaluation budget to the question (`spend evaluations well`, Principle Context 6):
- **Lighter tier (mechanical, checkable):** file/literature search and evidence harvest; citation
  *existence* + metadata checks; template/scaffold fills after the spec is frozen; the LaTeX compile-fix
  loop and figure generation from a fixed spec; journal/logbook summarize-forward; data loading and
  format conversion. Each returns a result a deterministic gate or the main agent can check.
- **Strong tier (judgment, physics, integrity):** the main hypothesize→evaluate→decide loop;
  `frame-problem`, `derive`, `simulation-design`, hard `debug`; metric design; the discovery /
  experiment-design / model-selection strategy.
- **The verification verdict is never downgraded.** `verify`'s refutation and CONFIRMED / PROVISIONAL /
  … grading must run on a model **at least as capable** as the one that produced the result — a verifier
  too weak to catch the error yields false CONFIRMs. Using a *different* capable model here is a feature:
  it adds mechanism diversity (different failure modes) on top of the independence.

Two guardrails keep tiering safe: **(1)** only hand a light model work whose output is checkable — by a
self-test, `validate_campaign.py`, a schema, or the main agent's own read — so a slip surfaces instead of
silently corrupting the ledger; **(2)** tier by *mechanical vs judgment*, not by how tedious the task
feels. The Agent / Workflow tools take a per-sub-agent `model` (and `effort`) override; don't hard-code
specific model names in durable docs — they age.

## The tension to manage
Context economy trades against completeness: too lean and the agent misses something it needed; too rich
and it drowns. Resolve it by tiering, not by cutting — move depth to REFERENCE and leave a pointer, rather
than deleting it. When in doubt, ask "does this need to be in *every* turn, or can a trigger pull it when
relevant?" Most things are the latter.

## Pointers
CORE (the spine it governs); `DOCTRINE_INDEX.md` (the metadata layer + `load`/`load_trigger` fields);
PRINCIPLES Context 7 (and Context 6 — the evaluation-budget analogue to model tiering); `verify` /
`cite-check` (the sub-agent verification/fan-out pattern); `handoff`
(cold-resume without reloading everything); the campaign logbook/journal split.
