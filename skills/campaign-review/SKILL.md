---
name: campaign-review
description: >-
  Retrospective of a finished or paused campaign from its artifacts and transcripts: failure
  signatures, root-caused to a kit locus; keepers feed improve-kit.
---

# campaign-review — retrospective on a loop, to improve the scaffolding

A finished or paused campaign is the richest evidence the kit has about itself: it shows exactly where the
scaffolding steered well and where it let the agent jump to a wrong conclusion, defer a cheap decisive check,
anchor on the wrong source, or burn compute. This skill turns one run into a **bucketed list of concrete kit
improvements**, each backed by evidence from the run. Its output is the input to `improve-kit`, which applies
the approved ones to your copy of the kit.

> **Stance.** *Assume the scaffolding is at fault before the model.* When the agent erred, ask first "what
> prompt/gate/doc would have prevented this?" — that is the improvable surface. But stay honest: distinguish a
> genuine scaffolding gap (fixable in the kit) from a one-off model slip (not). User corrections are a good
> place to look, not an automatic defect: ask whether the run should have caught it. A clarification of
> wording that was the user's own, or a detail the user simply added, is not a gap; a mistake the
> scaffolding should have caught is, and it gets a fix where it will fire next time. **Evidence every finding** —
> cite the transcript record or artifact; recompute every number from the ledger; never infer a failure you
> can't point to. **Freeze the honesty/verification core** — a "lesson" is never a reason to propose weaker
> integrity, looser verification, or a gameable metric (the constitution in `docs/CORE.md`).

## When to use / not use
- **Use** when a loop has stopped (done, paused, or abandoned) and you want to mine it for kit improvements.
- **`campaign-status`** instead — for a health check / checkpoint of a *running* loop (plateau, hygiene,
  next directions). That steers the campaign; this improves the *kit*.
- **`report`** instead — for the write-up of what the campaign found. This skill is about the scaffolding,
  not the science.
- **`improve-kit`** is the next step — it applies the keepers. This skill only *finds and proposes*.

## Inputs (gather first)
- **The campaign directory** — read everything in the layout the campaign actually carries. For a
  current campaign that means `CLAUDE.md` (always-on rules and routing), `campaign.md` (the signed-off
  contract, verification plan, landmines, and decision record), `roles/` (the per-spawn procedures),
  `README.md`, `configs/`, and `results/` — especially `JOURNAL.md`, `logbook.md`,
  `scoreboard.tsv`, `result_*.json`, `checks_*.json`, `verdicts/`, `snapshots/`, `diagnostics/`, and
  `guard_denials.log` and `driver_state.json` (direct evidence of what the scaffolding caught).
  Project-wide physics, conventions, instrument context, standing constraints, durable decisions, and
  lineage are in `../../PROJECT.md`. Follow the campaign's own `CLAUDE.md` routing table rather than
  assuming paths.
- **The raw session transcripts** — the archived `*.jsonl` (`campaign-status` snapshots them to the
  campaign's `transcripts/`; otherwise the harness's own session store, e.g. Claude Code's
  `~/.claude/projects/<slug>/`). The transcripts are where conclusion-jumping, premature certainty, and
  deferred checks are visible; the artifacts only show the settled story. Treat them as sensitive.
- **The kit version used** — campaigns stamp it in the `campaign.md` header and atop `results/logbook.md`.
  Compare it with the kit you would edit, so a proposed change targets current text rather than wording
  that has since moved.
- Any running notes, or the user's own sense of what went wrong — seed material, not a substitute for
  reading.

## Method (read-heavy — delegate to sub-agents)
The ingest is large; per the kit's delegation doctrine, **spawn sub-agents** to read slices and return only
their findings, keeping the main context lean. A good split: one agent reconstructs the decision chain from
the artifacts; one parses the transcripts for the failure signatures below; one recomputes the headline
numbers from the ledger. Synthesize their returns.

1. **Reconstruct the timeline & decision chain.** Order the experiments, the decisions and their reversals,
   the disputes, the user interventions, and the compute spent. For each decision, note in hindsight its
   **provenance/confidence at the time** (PINNED/REPORTED/INFERRED/RECALLED/REASONED, `verify` §5b) —
   reversals usually trace to a load-bearing fact acted on at INFERRED/RECALLED.
2. **Scan for failure signatures** (catalog below) AND for **what worked** — every place the scaffolding caught
   an error, forced a useful check, or enabled clean recovery. A balanced review keeps the keepers.
3. **Root-cause each finding.** Symptom → mechanism → **the specific kit locus** that should change (name the
   file: a `SKILL.md`, a `*.tmpl`, a `roles/*.md`, a `CORE.md` section or reference doc, a gate/hook). A
   finding with no kit locus is an observation, not an improvement — mark it so.
4. **Bucket each proposed change by risk** (the buckets `improve-kit` consumes): **auto** (cosmetic/clarifying,
   no behavior change) · **sign-off** (any change to a skill's instructions, a template, a gate, a default, a
   principle) · **more-context** (can't decide without the user). Anything touching the honesty/verification
   core is **always sign-off**, never auto.
5. **Write the report** from `assets/review_template.md` to `kit_review.md` in the campaign directory, beside
   the evidence it cites (`kit_review_<date>.md` if one exists). Its §4 keeper table, every row `pending`, is
   what `improve-kit` consumes and marks `applied` or `rejected`. The campaign validator scans every `.md` in
   the tree for leftover template markers, so when a finding quotes one, break it up (`{ {NAME} }`,
   `[ [OPTIONAL`) rather than reproducing it. Keepers that live only in prose get lost:
   the same scaffolding gap then recurs in the next campaign. If the project's `CLAUDE.md` names a different
   home for reviews or keepers, use that. Then hand the keepers to `improve-kit`.

## Failure signatures to scan for (not exhaustive — add as you find new ones)
- **Conclusion-jumping** — a claim asserted with confidence, then reversed, sometimes more than once. Look
  for "decided X" followed later by "actually not-X."
- **Deferred cheap decisive check** — an expensive run spent to answer a question a seconds-long static check
  (parse an artifact, probe the data) would have settled; or a check punted to "the loop's job."
- **Wrong-authority anchoring** — a load-bearing fact taken from a low-authority source (leftover/modified
  code, recollection) when a higher-authority artifact (trained weights, released data) was available.
- **Gate-induced bug reproduction** — a "match the published number" gate driving the agent to
  reverse-engineer the original's quirk or bug instead of diagnosing the discrepancy.
- **Scope / spec drift** — the agent silently redefining the baseline, the metric inputs, or the lever set
  away from the signed-off spec.
- **Wasted / mis-spent compute** — long runs launched before the spec was pinned; re-runs forced by an
  avoidable error; no early health check on a multi-hour run.
- **Unverified promotion** — a current best or finding promoted without the label of the check that
  actually ran, or past the verification its preset requires.
- **Lost context on resume** — a handoff that didn't carry the in-flight reasoning, forcing rediscovery.
- **Silent infrastructure** — a lever that was dropped by one build path and not honored end-to-end.
- **Positives (keep!)** — append-only records that enabled clean recovery, an empirical pin that prevented a
  bug, a refused metric-gaming win, an a-priori bound that caught a surprise.

## Output
`kit_review.md` in the campaign directory (from the asset template): the reconstructed timeline, a
**what-worked** list, a **findings table** — each row: `observation → evidence (cite transcript record /
artifact) → root cause → proposed kit change → target file → risk bucket` — and the bucketed **keeper table**
for `improve-kit`.

## Composition
- Feeds **`improve-kit`** through the report's keeper table, so each keeper is tracked to applied/rejected
  and can't silently evaporate; `docs/reference/kit-development.md` is how a keeper's change is then made.
- Uses the **`verify` §5b** provenance vocabulary (PINNED/REPORTED/INFERRED/RECALLED/REASONED) to grade past
  decisions, and **`record-decision`** for any non-obvious judgment the review itself makes.
- Pairs with **`handoff`** / **`campaign-status`** (state & health) — this is the post-hoc improvement lens,
  distinct from both.

## Checklist
- [ ] Read the **transcripts**, not only the artifacts — the failures live in the conversation.
- [ ] Every finding **cites** a transcript record or artifact; every number **recomputed** from the ledger.
- [ ] Each finding **root-caused to a named kit locus**, or explicitly marked "observation, no kit change."
- [ ] **What-worked** captured, not only failures.
- [ ] Each proposed change **risk-bucketed**; anything touching the integrity/verification core → sign-off.
- [ ] **Keeper table** written with every row `pending`, so `improve-kit` can close each one.
- [ ] No proposed change weakens the honesty/verification core.
