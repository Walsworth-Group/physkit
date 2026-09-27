# The campaign capstone — campaign-specific instructions for `report`

Read this when the *Where* dial of `report` says *in a campaign*. Everything in `SKILL.md` still applies:
the five standards, the provenance labels, the procedure, the report-time verification, the section arc,
the assets, the checklist. This file says only what a campaign adds: where the sources live, which
record is authoritative, what runs first, and which labels the report must print. The capstone is the
campaign's one LaTeX/PDF deliverable; every other campaign artifact stays in markdown.

## Where things live — discover the layout, don't assume it

Campaigns differ in how they store things, so read the campaign's own structure rather than assuming
filenames. Campaigns scaffolded by this kit answer that from one place: the campaign's `CLAUDE.md` and
its **§Where things live** table, which names the campaign definition, `results/scoreboard.tsv`,
`results/JOURNAL.md` (working memory; the ledger's `finding` cells are the settled record), the project
background doc, and the verdict artifacts. The per-experiment configs (`configs/`, `configs*/exp*.json`)
and the figures (`results*/images/`) are not table rows; read them from the tree. A campaign scaffolded
before that table existed has none: fall back to `docs/charter*.md`. So do non-kit campaigns. The roles to find:

- **The campaign definition** (`campaign.md`): the goal, the primary metric, what is FROZEN (physics,
  geometry, data, the metric itself and, if it was revised, its epochs), which levers were explored. The
  thesis follows from it: given the frozen setup and the goal, here is the best lever combination and
  the evidence for it.
- **The experiment ledger** (`results/scoreboard.tsv`; elsewhere a results table or `result_*.json`): the
  per-experiment record of what was tried and what it scored, sub-metrics, ceilings, sanity/overfit
  flags, notes. The spine of the evidence section; each row is an ablation.
- **The journal / narrative** (`results/logbook.md`; often a `JOURNAL*.md` elsewhere): the reasoning
  behind each experiment. Mine it for why a lever was tried and how a choice was reached, and for the
  `Disputes & responses` lines (verifier and user challenges) and how they were resolved.
- **The verified findings** (the ledger's `finding` cells; often a `DISCOVERIES*.md` in older or non-kit
  campaigns): the results that survived verification. Cite their verification status and metric epoch.
- **The configs** (`configs*/exp*.json`): the exact knob settings per experiment.
- **The literature file** (`LITERATURE.md`, optional): the curated references, usually mapped to levers.
  The bibliography seed; every entry still goes through `cite-check`.
- **The figures** (`results*/images/` or per-experiment output dirs), optional.
- **The project overview** (`../../PROJECT.md`): the governing physics, conventions, rig and sample
  parameters. Pull definitions and derivations from it rather than reconstructing them.

If a role has no obvious home, search for it (grep for the metric name, for "best", for citation URLs)
before concluding it does not exist.

## The selected configuration is the campaign's gated record

The report centers on one configuration, and it is **`configs/RECOMMENDED.json`**, the campaign's own
current-best. Read it; do not re-derive it. That file is a gated artifact: a write to it is a promotion,
and the PreToolUse hook refuses one that does not carry the result's honest label (`verification_label`),
or a result a check refuted. Inferring a winner from
the scoreboard re-decides, by a different rule and with no gate, something the campaign already decided
under one; a report that names a configuration the campaign never promoted asserts a result nobody
verified. Route to it via `CLAUDE.md` §Where things live, not by assuming the path.

- If the user names a specific config, use theirs, and if it differs from `RECOMMENDED.json` say so in the
  report with both.
- If `RECOMMENDED.json` is absent, empty, or stale (its `exp_id` has no scoreboard row), that is a finding
  to report, not a gap to paper over: the campaign has no current-best. Say so, then infer a candidate
  from the ledger and label it *inferred*, with its basis and its label. Never present an inferred winner
  as the selected configuration.
- The pointer follows the true best at once, so a current-best labelled `unverified`, `self-checked` or
  `self-verified` is not a defect: its label is printed as such. A `verification_label` that differs from
  its `results/checks_<NN>.json` `label` is the defect `campaign-status` flags.
- A higher raw score that fails the overfit flag is not the winner, and saying so is part of an honest
  report.

**The contenders** are 2–4 runner-ups: a lever that nearly matched, an approach that won on one axis and
lost on another, a physically interesting near-miss. A paragraph or a row each. Keep the asymmetry: the
selected configuration in depth, the contenders summarized.

## Run the claim audit first

Before the evidence ledger, read the latest `results/verdicts/audit_<NN>.json` or run `claim-audit` (the
driver runs it at the end of the loop under every preset but `none`; a `none` campaign that will share
its report runs it here). It is claim-directed: it enumerates what this report will export, ranks by
load-bearing weight and label weakness, spends its budget top-down, and re-checks the final best once.
Its inherited-assumptions check seeds the assumptions register.

## The labels the report prints

Every exported claim carries its label (`results/checks_<NN>.json` `label`: `unverified` ·
`self-checked` · `self-verified` · `self-refuted` · `<VERDICT>/peer` · `<VERDICT>/verifier`, an old
`/review` or `/re-execution` read as `/verifier`; and, from the audit's artifact, `label_after`, which
may be `<VERDICT>/audit`), and the report prints it. A shareable report needs the current-best's label
to be independent: a CONFIRMED peer or verifier verdict, or the claim audit's label. A headline the
audit downgraded is reported as downgraded, never as the best; it stays in `RECOMMENDED.json` with its
downgraded label printed beside it (promote-and-label, never a silent swap). Every other exported claim
prints its label too, `unaudited` included. While the current-best's label is non-independent and no
audit covers it, the report may be an internal draft only, never shareable.

Name the metric epoch the headline rests on: its `metric_version`, kind, direction, and standing
(`configs/loop.json` `campaign.metric_epochs`; the first epoch is implicit and ratified). A headline under
a `pending` epoch says so; a number from a rolled-back epoch is not a headline; no two numbers are
compared across epochs without saying the ruler changed.

## The evidence ledger, campaign form

For the selected configuration and for each feature or lever it includes, assemble the record before
writing prose: **the number** (the in-campaign delta attributable to the feature, preferably an ablation:
the metric with the feature against the metric without it, everything else fixed; quote both values, the
delta, and the experiment ids), **the reasoning** (why it was tried and why this value, from the
journal), **the status** (independently verified, or provisional). Where a parameter was set by a sweep,
the evidence is the sweep curve and its optimum; by a fit, the anchors and the fitted value with its
spread; locked, the reason it is frozen with the source of truth cited. Render this as the results /
ablation table and narrate the important rows. A reader must be able to point at any feature and see
what it bought.

Every ledger row and every verdict artifact appears in that table or in a short list of exclusions with a
reason. A row left out silently is the cherry-pick the audit exists to catch.

## Figures

Two sources. Existing campaign figures: the most informative outputs of the most refined runs, found via
the ledger (the highest-metric experiments, the selected config's output dir, the figures the journal
references); prefer final over early; copy them into the report's figure dir. New explanatory figures: a
geometry / parameter schematic, a pipeline diagram, an evidence/ablation chart (metric delta per feature),
a metric-progression chart across the campaign (annotated with the lever added at each step), and the
headline result figure (best reconstruction or fit against the measurement). Captions state the takeaway.

## Output

Write into a fresh `final_report/` directory in the campaign root so existing work is not clobbered; note
it if a prior report exists. Use `report`'s bundled assets, not a bespoke template; compile per
*Assemble & compile*.

## The campaign checklist (in addition to `report`'s)

- [ ] The selected configuration came from `configs/RECOMMENDED.json`, not from re-deriving a winner; or,
      if that record was absent or stale, the report says so and labels its candidate as inferred.
- [ ] The claim audit ran (or its latest artifact was read) before the evidence ledger; every exported
      claim prints its label, `label_after` where the audit covered it, "downgraded by audit" where true.
- [ ] The metric epoch the headline rests on is named; no cross-epoch comparison goes unlabeled.
- [ ] Every ledger row and verdict artifact is in the evidence table or the exclusions list with a reason.
- [ ] The selected configuration is explained in depth; the contenders are summarized.
- [ ] Every parameter in the selected config has a "how set" and an "evidence" entry.
- [ ] Unresolved disputes from the logbook are surfaced with how they were resolved.
- [ ] A figure shows the evidence/ablation; a figure shows the headline result.
- [ ] The reproducibility section gives exact commands and configs a stranger could run.
