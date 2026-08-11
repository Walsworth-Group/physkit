---
name: final-report
description: >-
  Generate a comprehensive, publication-quality LaTeX report (compiled to PDF) at the END of an
  autoresearch / fitting / optimization / model-improvement campaign. Use this whenever the user wants
  to wrap up a campaign and document its findings for the record or for reproduction — phrasings like
  "write the final report", "summarize the whole campaign", "document our results", "make a LaTeX
  writeup of the final fit", "explain all the parameters and why we chose them", or "create a document
  another researcher could use to reproduce this". The report explains the SELECTED best configuration
  in depth, briefly summarizes the promising runner-up contenders, tabulates every physical/model
  parameter with its value, governing equation, justification, and the in-campaign experimental evidence
  (metric deltas) for each choice, documents the full data pipeline and key derivations, embeds the best
  existing figures plus newly generated visualizations, and builds a verified bibliography in which every
  citation is confirmed to link to a real paper. Use it for end-of-campaign reporting and documentation —
  NOT for mid-campaign experiment verification (that is verify) or for one-off plots.
---

# final-report — the campaign's permanent, evidence-backed record

A final report is not a summary email. It is the document that outlives the campaign: the thing a
collaborator (or you, in a year) reads to understand *what was chosen, why, and on what evidence* — and,
crucially, to **reproduce the work from scratch**. Treat it that way. Every number traces to an
experiment, every parameter to a justification, every citation to a real paper, and the whole thing
compiles to a polished PDF — the campaign's one LaTeX/PDF deliverable (everything else stayed in markdown).

You are reporting on **completed** work. Do not launch new experiments or change campaign results. The
only new artifacts you create are explanatory visualizations and the report itself.

## This skill composes the general `report` engine
`final-report` is the **campaign specialization of the general `report` skill** — it is `report` run in
*capstone* stage, *shareable* audience, *LaTeX* format, with two campaign-specific additions: the
**campaign harvest** (discovering the campaign layout and pulling the selected config, evidence ledger,
discoveries, and disputes) and the **REVTeX/PDF packaging**. **Read
`${CLAUDE_PLUGIN_ROOT}/skills/report/SKILL.md` first** and apply its machinery — don't re-derive it here:
- the **five standards** (evidence-backed · honest · **verified** · traceable/reproducible · polished) are
  the rubric; this skill just supplies the campaign sources for each;
- the **report-time verification step** (Standard 3 — recompute load-bearing values from the frozen record,
  internal consistency, `cite-check` every reference, flag PROVISIONAL/QUESTIONABLE-ASSUMPTION claims, emit
  the verification ledger) is **mandatory before compiling**;
- the **honest-provenance labels**, the **master parameter table**, the **section arc**, and the
  **compile/Overleaf** handling all come from `report` (including the vendored REVTeX assets in
  `report/assets/` — use those, not a bespoke template).

The rest of this skill is the campaign-specific harvest that fills `report`'s structure. The standards
below are `report`'s five, expanded with where the campaign supplies each:

- **Evidence-backed.** No claim floats free. A feature is in the chosen configuration *because* the
  campaign's own data shows it helped — quote the metric delta (e.g. "adding canting lifted field-$R^2$
  in the coercive band from 0.54 → 0.82, exp 014") and point to the experiment. If you cannot find
  evidence for a choice, say so plainly rather than inventing a rationalization.
- **Honest.** Mark fitted vs. swept vs. locked vs. assumed parameters for what they are. Give the
  promising-but-not-selected contenders their due in brief. State limitations and the known ceiling. An
  honest report that says "this lever didn't pan out and here's why" is more useful and more credible
  than one that launders every decision into a triumph. Surface the **unresolved disputes** the campaign
  recorded (the JOURNAL's append-only verifier/user challenges) and how they were resolved, and mark
  **PROVISIONAL** findings as provisional — a report that hides a live disagreement is not honest.
- **Verified.** Run `report`'s report-time check: recompute the headline result and key deltas from the
  **frozen record** (scoreboard/logbook) — require the current-best's `verify` status is **CONFIRMED**,
  not just high — confirm internal consistency (abstract ↔ body, totals, units), `cite-check` every
  reference (claim-support from full text, not the abstract; abstract-only support is PROVISIONAL), and flag
  anything PROVISIONAL or resting on a QUESTIONABLE ASSUMPTION.
- **Reproducible.** A stranger with the repo should be able to rerun the headline result: exact configs,
  commands, data provenance, environment, and the file pointers to find everything (the per-experiment
  snapshot). If they can't, the report has failed its primary job.
- **Polished.** It compiles. Units are typeset, tables are clean, equations are numbered, figures have
  captions that state their takeaway (not just "Figure of the fit"), and citations are clickable and
  real.

## The campaigns vary — discover the layout, don't assume it

Campaigns differ in how they store things, so **start by reading the campaign's own structure** rather
than assuming filenames. You are looking for a handful of *roles*; find whatever file plays each role.
(Campaigns scaffolded by this kit use standard homes — `docs/charter.md`, `results/scoreboard.tsv`,
`results/JOURNAL.md`, `results/DISCOVERIES.md`, the governing physics/conventions/instrument docs at
`../../shared/PHYSICS.md` · `../../shared/CONVENTIONS.md` · `../../shared/INSTRUMENT.md`, optional
`LITERATURE.md`, `configs/`, `results/images/` — confirm they exist, and fall back to discovery for
non-kit campaigns.)

- **The charter / program doc** — defines the goal, the **primary metric**, what is **FROZEN** (physics,
  geometry, data, the metric itself), and which **levers** were explored. This is your north star: the
  report's thesis is "given the frozen setup and the goal, here is the best lever combination and the
  evidence for it." (Often a `charter*.md` / `README` / a docs folder.)
- **The experiment ledger** — the per-experiment record of what was tried and what it scored: the primary
  metric plus sub-metrics, ceilings, sanity/overfit flags, and notes. This is the spine of your evidence
  section — each row is an ablation. (Often a `scoreboard.tsv/csv`, a results table, or a set of
  `result_*.json`.)
- **The journal / narrative** — the reasoning behind each experiment: hypotheses, what was expected,
  what happened. Mine it for *why* a lever was tried and how a choice was reached. (Often a `JOURNAL*.md`.)
- **The discoveries / verified findings** — results that survived verification and graduated to
  "established". These are your selected, high-confidence claims; cite their verification status.
  (Often a `DISCOVERIES*.md`.)
- **The configs** — the exact knob settings per experiment, including the **selected** configuration.
  (Often `configs*/exp*.json` or similar.)
- **The literature / citations file** — the campaign's curated references, usually already mapped to
  levers. This is your bibliography seed and your anti-hallucination anchor. (Often a `LITERATURE.md`.)
- **The figures** — outputs from the runs, especially the most refined ones. (Often a `results*/images/`
  or per-experiment output dirs.)
- **Reference docs** — the governing physics (`PHYSICS.md` — equations, methods, system behavior),
  conventions (`CONVENTIONS.md`), and the measurement rig / apparatus + sample parameters (`INSTRUMENT.md`),
  shared at `../../shared/` and **referenced, never copied**. Pull definitions and derivations from these
  rather than reconstructing them.

If a role has no obvious home, search for it (grep for the metric name, for "best", for citation URLs)
before concluding it doesn't exist. Spend your first chunk of effort building an accurate map; the
quality of everything downstream depends on it.

## Identify the selected configuration and the contenders

The report has a clear protagonist. From the ledger + discoveries, determine:

- **The selected/best configuration** — the one the campaign converged on. Usually it maximizes (or
  minimizes) the primary metric *while passing the sanity/overfit guards* — a higher raw score that
  fails the overfit flag is **not** the winner, and saying so is part of an honest report. If the user
  named a specific config, use theirs; otherwise infer it and state your inference and its basis.
- **The contenders** — 2–4 runner-ups that were genuinely promising: a different lever that nearly
  matched, an approach that won on one axis but lost on another, or a physically interesting near-miss.
  These get a *brief* treatment (a paragraph or a row each) — enough that a reader knows the road not
  taken and why.

The asymmetry is deliberate and is what the user wants: the selected configuration is explained in
**great detail**; the contenders are **summarized**.

## Build the evidence ledger (the heart of the report)

For the selected configuration and for **each feature/lever** it includes, assemble a small evidence
record before you write prose:

- **The number.** The in-campaign delta attributable to the feature — ideally an ablation: metric *with*
  vs. *without* the feature, holding everything else fixed (this is exactly what the ledger's rows give
  you). Quote both values and the delta, and name the experiment id(s).
- **The reasoning.** Why it was tried and why this value (from the journal).
- **The status.** Whether it was independently verified / graduated to discoveries, or is provisional.

Where a parameter was set by a **sweep**, the evidence is the sweep curve and its optimum; by a **fit**,
it's the anchor(s) fitted to and the fitted value with its uncertainty/spread; by a **lock**, it's the
reason it's frozen (cite the source of truth). Render this as a results/ablation table in the report and
narrate the important rows. A reader should be able to point at any feature and immediately see what it
bought.

## Enumerate every parameter — the master table

Physicists reading this will look for the parameter table first. Build one row per parameter in the
selected configuration. Include geometry, the forward-model physics, instrument/measurement parameters,
preprocessing settings, and decoder/fit hyperparameters — *all* of them, not just the interesting ones.
Each row:

| field | what goes here |
|---|---|
| Symbol | the LaTeX math symbol used consistently elsewhere in the report |
| Meaning | one phrase |
| Value (units) | typeset with units |
| Role | which equation / pipeline stage it enters |
| How set | fitted (to which anchors, by what procedure) · swept (range → optimum) · locked/frozen (why) · assumed (source) |
| Evidence | the in-campaign number: ablation delta, sweep optimum, or fitted value + spread, with exp id |
| Source | citation key if literature-backed, else "empirical / lab-internal" — stated honestly |

Then, for the **handful of parameters that matter most** (the ones the campaign actually fought over),
write a paragraph each: the physics, the governing equation, how the value was pinned, and the evidence.
The long tail of locked/standard parameters can live in the table alone.

## Document the pipeline and derive what's specific

Describe the **full data pipeline end-to-end** so it can be re-run: raw data in → each preprocessing
step → the forward model → the fit/decoder → the metric out. Make the flow concrete (what transforms
what, in what order, with which parameters).

Include the **governing equations**, pulling them (and any campaign-specific derivations) from
`../../shared/PHYSICS.md` where it exists rather than reconstructing them. Derive the relations that are
*specific to this campaign* (the forward map, the metric definition, any effective-parameter or
correction derivations the campaign relied on) at a level that lets a reader follow and reproduce them.
Cite standard textbook results rather than re-deriving them — derive what's novel, reference what's
known. Keep symbols consistent with the parameter table.

## Figures: curate the best, generate the rest

Use **two** sources of figures.

1. **Existing campaign figures.** Pull the most informative outputs from the **most refined runs** —
   identify them via the ledger (highest-metric experiments, the selected config's output dir, the
   figures the journal/discoveries actually reference). Prefer final over early. Copy the ones you use
   into the report's figure dir (or set `\graphicspath`) so the report is self-contained.
2. **New explanatory visualizations** you generate with matplotlib. A strong report typically wants:
   a **geometry/parameter schematic** (so the angles and shapes in the parameter table are visual), a
   **pipeline diagram** (the data flow), an **evidence/ablation chart** (metric delta per feature — this
   makes your evidence section land at a glance), a **metric-progression chart** across the campaign
   (how the headline number climbed, annotated with the lever added at each step), and the **headline
   result** figure (best reconstruction/fit vs. measured). Save generated figures next to the report.

Every figure needs a caption that states the **takeaway**, axis labels with units, and legible text.
A figure a reader has to decode is a figure that failed.

## Citations: real papers only

Hallucinated references are the classic failure mode of LLM-written reports and they destroy trust
instantly. The discipline:

- **Seed from the campaign's literature file.** It already maps references to levers; reuse those.
- **Verify every citation against the source.** Fetch it and confirm the exact title, the **full author
  list**, year, venue, and identifier (DOI / arXiv id) all match what you're citing it for. A link that
  404s, redirects to a homepage, or points to a different paper is not a citation. **If you cannot find
  the paper, flag the citation** — never invent or approximate one. (Verification parallelizes well — you
  can fan it out across subagents for a large bibliography.)
- **Prefer arXiv; be token-efficient.** When verifying or fetching a paper, use its arXiv version (the
  abstract/HTML on `ar5iv.org`, or the LaTeX source) rather than a publisher PDF; convert any PDF with a
  scientific-PDF→markdown tool and read only what you need (`docs/PRINCIPLES.md` §2).
- **Fill genuine gaps with a web search**, then verify those the same way before using them.
- **Never invent a reference, DOI, or arXiv id.** If a choice has no real supporting source, either find
  one or label the choice "empirical / lab-internal" in the parameter table — that is an honest and
  perfectly respectable provenance.

## Assemble, compile, and self-correct

Write the report into a fresh directory in the campaign root (e.g. `final_report/`), so you don't
clobber any existing `report/` work — note it if a prior report exists. Start from the bundled template
(see below), then:

- Generate `references.bib` (or an inline bibliography) from your verified citations.
- Compile with `latexmk` so the multi-pass + bibliography runs happen automatically, e.g.
  `latexmk -pdf -interaction=nonstopmode -halt-on-error report.tex` (run from the report dir). On
  Windows the MiKTeX `latexmk`/`pdflatex` are on PATH.
- **Read the `.log` and fix until it builds clean.** Treat compile errors as your problem to solve:
  missing package → install or swap for a standard one; bad reference/citation → fix the key; missing
  figure → correct the path or regenerate it. Loop until the PDF builds with no errors and no unresolved
  `??` references or "Missing figure" warnings.

## Report structure

Adapt section names to the campaign, but cover this arc (it mirrors a methods paper, which is what a
reproducible report effectively is):

1. **Title, authors/lab, date, abstract** — the abstract states the headline result *with its number*
   and the one or two key evidence deltas, the way the campaign's best work would be summarized.
2. **Introduction & objective** — the problem, the goal, what's frozen, the headline finding.
3. **The selected configuration (in depth)** — the protagonist. What it is, every component, and why.
4. **Physical & model parameters** — the master table + per-parameter prose for the important ones.
5. **Methods: data pipeline & forward model** — end-to-end pipeline + campaign-specific derivations.
6. **Fitting / decoding & the metric** — how the configuration is fit and how success is measured
   (define the primary metric precisely; note its known degeneracies/ceiling).
7. **Results & evidence** — the ablation/evidence table, the metric-progression and result figures, the
   narration of what each lever bought.
8. **Promising alternatives** — the contenders, brief.
9. **Reproducibility** — exact configs, commands, data provenance, environment, file pointers.
10. **Broader implications & significance** — over what range the solution applies; what it *newly enables or
    predicts*; which open problems in the field it might bear on; why it's interesting beyond this campaign —
    the honest version, no overclaiming *(Wieman decision 27)*.
11. **Limitations & open questions** — honest accounting of what's unresolved and the ceiling,
    including any unresolved disputes from the JOURNAL record.
12. **References** — verified, clickable.

## Before you call it done — checklist

- [ ] The PDF compiled with no errors and no `??` / missing-figure warnings.
- [ ] The selected configuration is explained in depth; contenders are summarized (the right asymmetry).
- [ ] Every parameter in the selected config appears in the table with a "how set" and an "evidence" entry.
- [ ] Every notable claim cites an experiment id or a reference — no free-floating assertions.
- [ ] Every citation was fetched and confirmed to be a real paper matching its use.
- [ ] A figure shows the evidence/ablation; a figure shows the headline result; figures have takeaway captions.
- [ ] The reproducibility section gives exact commands + configs a stranger could run.
- [ ] Broader implications stated honestly — applicability range, what it newly enables/predicts, open problems it bears on — with no overclaiming.
- [ ] A claim→evidence manifest maps every headline claim to its backing artifact (experiment id / `result_<NN>.json` / figure), with planned-vs-executed deltas noted.
- [ ] No placeholder text, no "TODO", no invented numbers.

Then tell the user where the `.tex`, the `.pdf`, and the generated figures live, and give a 3–4 line
summary of the headline result and the strongest evidence for it.

## Assets — use the shared `report` assets
Use the **general `report` skill's vendored assets** (`${CLAUDE_PLUGIN_ROOT}/skills/report/assets/`), not a
bespoke template: `report_skeleton.tex` (REVTeX `revtex4-2`, APS/PRX — the capstone form, verified to
compile), `report-macros.sty` (portable, siunitx/physics/braket-free), the **vendored `revtex4-2.cls` +
`apsrev4-2.bst` + size configs** (so no package-install approval is ever needed), `refs.bib`, and the
plain-`article` `draft_article.tex` fallback. Copy that asset folder into a fresh `final_report/` dir, set
`\graphicspath` to your figure dir, fill it in, and compile per `report`'s *Assemble & compile* (read the
`.log`, self-correct until clean; emit the Overleaf folder if there's no local compiler).

## Scaling to large campaigns

For a campaign with many experiments and a long bibliography, fan the gathering out: spawn subagents to
(a) harvest the evidence ledger for distinct lever groups, (b) verify citations in parallel, and (c)
generate figure sets — then assemble centrally. Keep the **writing and the final compile in one place**
so voice, symbols, and cross-references stay consistent. Those fan-out jobs (harvest, citation checks,
figure sets) suit a **lighter model**; keep the synthesis, the claim/number re-checks, and the final
compile on the strong model.
