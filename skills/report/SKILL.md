---
name: report
description: >-
  Produce a rigorous, evidence-backed scientific report or technical document from work that is already
  done — for any task, not only research campaigns. Use whenever the user wants to write up results,
  document a method, or turn analysis into a shareable artifact: phrasings like "write a report",
  "write this up", "document these results", "make a writeup of the fit/derivation/analysis", "turn this
  into a paper/memo", "explain the parameters and why we chose them", or "create something a colleague
  could read and reproduce". Handles audience (internal vs shareable), stage (draft / progress / capstone),
  and format (LaTeX by default for scientific reports; Markdown or Word where lighter is better). Every
  number is labeled by provenance, every load-bearing claim is re-checked from source before finalizing,
  every citation is verified, and a master parameter table records each parameter with its provenance,
  justification, and uncertainty. For an end-of-CAMPAIGN capstone use final-report (it composes this
  skill); for mid-campaign result checking use verify.
---

# report — the general scientific-document engine

A report is the artifact that outlives the work: what a collaborator (or you, in a year) reads to
understand *what was found, why, and on what evidence* — and, where it matters, to **reproduce it**. This
skill produces that artifact for any task, from a one-off fit writeup to a methods paper. It is the
general engine; the campaign capstone (`final-report`) and periodic campaign progress notes are this same
engine in different *modes*, not separate tools.

You are reporting on **completed** work. Do not launch new experiments or change results to make the story
cleaner. The only new artifacts you create are explanatory figures and the document itself. (If the
report-time check uncovers a wrong number, fix the *report*, and tell the user the underlying result needs
attention — don't quietly paper over it.)

## Set the mode first

Three dials decide the shape of the document. Settle them before writing — ask if unclear.

- **Audience.** *Internal* (rich: interpretation, open questions, dead ends, the verification ledger in
  full) vs *shareable* (plain: data, method, comparison, results). The two carry the **same facts and
  caveats** — only the register differs. Honesty is not a function of audience.
- **Stage.** *Draft* (fast, plain `article` or Markdown, get the structure and numbers right) ·
  *progress* (a checkpoint snapshot — what's known, what's open) · *capstone* (the polished, reproducible,
  shareable deliverable). Verification (Standard 3) is **mandatory before any shareable or capstone
  output**; for an internal draft it can be lighter, but never skipped for the headline numbers.
- **Format.** **LaTeX is the default for scientific reports** (REVTeX/APS for a physics capstone — see
  *Assemble & compile*). Use **Markdown** for a quick internal draft or a doc that lives in the repo; use
  **Word** (the `docx` skill) when the recipient needs it. Don't re-implement rendering — compose the
  format skill that owns it (`docx`, `pdf`, `pptx`).

## The five standards (the rubric you grade your own draft against)

A report is *finished* only when it passes all five.

1. **Evidence-backed.** Every claim and number traces to a named source — an experiment id, a
   file/computation, or a citation. Quote the actual value/delta and where it came from. No free-floating
   assertions; if a choice has no evidence, **say so plainly** rather than rationalize it.
2. **Honest.** Label every number by provenance (see below). Report the **honest band and the assumption
   that drives it**, not the optimistic edge. Lead with the bad news; surface limitations, the known
   ceiling, PROVISIONAL findings, and unresolved disputes. Give the road not taken its brief due.
3. **Verified — re-check key claims and values at report time** (composes `verify` and `cite-check`; see
   *Verify before you finalize*). Never put a number in a report you have not reconfirmed from source.
4. **Traceable / reproducible.** Give the pointers — config, command, seed, data provenance, file/section
   — so a reader can follow each result and regenerate the headline one. A polished PDF nobody can
   reproduce has failed its primary job.
5. **Polished.** Compiles clean (no `??`, no missing figures); units and math typeset; captions state the
   **takeaway** (not "Figure of the fit"); figures legible; notation consistent; citations clickable and
   real.

## Honest-provenance labels (Standard 2)

Label, don't blend. Pick the scheme that fits the artifact and keep it consistent:

- **Numbers:** *analytic* (closed form, exact within stated assumptions) · *computed* (simulated/measured
  and validated) · *scaffold* (depends on an unpinned input — flag it).
- **Prose findings:** *claim* (asserted, evidence given) · *assumption* (taken as given) · *open* (not yet
  resolved).
- **Parameters (in the table):** *user-given · fitted · first-principles · simulation · assumed ·
  literature*. (A parameter with no real supporting source is honestly labeled "empirical / lab-internal"
  — that is a respectable provenance, not a gap to hide.)

## Procedure

0. **Set parameters and gather sources.** Fix the three mode dials. Collect the material: for a general
   task, the analysis/computations/data the user points to; for a campaign (via `final-report`), harvest
   the ledger / logbook / discoveries / configs + `PHYSICS.md` + the **`frame-problem` artifact**. Spend
   the first effort building an accurate map of what plays each role — quality downstream depends on it.
1. **Map material to roles:** the thesis/result · supporting evidence (numbers + their sources) ·
   parameters · the physics model + assumptions · methods/pipeline · figures · references.
2. **Problem framing & scope** *(from `frame-problem` if it ran).* State the goal, **what physics was
   included vs excluded and why** (the inventory), the **decomposition / steps** taken, and **how it was
   verified** (the verification plan). This is the model-and-scope section — it tells the reader the domain
   of validity up front.
3. **Build the evidence ledger** *(the spine of the results section).* For each headline claim/feature:
   the value/delta, its source (experiment id or computation), and its **verification status**. Where a
   value came from a *sweep*, the evidence is the curve and its optimum; from a *fit*, the anchors and the
   fitted value with uncertainty; from a *lock*, the reason it's frozen.
4. **Master parameter table — *every* parameter that entered the final product.** One row each:
   **symbol · meaning · value (+units) · provenance · justification appropriate to its type · uncertainty ·
   evidence pointer.** Then, for the handful that matter most (the ones actually fought over), a paragraph
   each: the physics, the governing equation, how the value was pinned (derivation / fit result /
   simulation), and the evidence. The long tail of locked/standard parameters can live in the table alone.
   *Do not omit a parameter because it is "obvious" — obvious-but-unstated parameters are where
   reproducibility leaks.*
5. **Methods, pipeline & derivations** — end-to-end so it can be re-run (raw input → each step → result).
   Derive what is *specific* to this work; **cite** standard textbook results rather than re-deriving them.
   Define the metric / figure of merit precisely, including its known degeneracies or ceiling.
6. **Figures** — curate the most informative existing figures (prefer final over early) and generate the
   explanatory ones a good report wants: a **geometry/schematic**, a **pipeline diagram**, an
   **evidence/ablation chart**, and the **headline-result** figure. Every caption states the takeaway;
   axes are labeled with units; text is legible. Copy used figures into the report's figure dir so it is
   self-contained.
7. **Verify (Standard 3).** Run the report-time check below.
8. **Assemble & compile.** Build into a fresh **in-tree** output directory — in a campaign, the campaign's
   `final_report/`; for a project-level or cross-campaign writeup, the project's single `reports/` home;
   standalone, a fresh local dir. Keep LaTeX build artifacts (`.aux/.log/.out/.fls`) out of source control
   via `.gitignore`, but the compiled PDF lives **in-tree beside its source** (the outputs shelf is in the
   tree — see `final-report` and the project `reports/`). Apply the right register and the provenance labels;
   compile and **self-correct until clean** — or emit the Overleaf folder if there is no local compiler
   (see *Assemble & compile*).
9. **Grade against the five standards + the checklist** before declaring done.

## Verify before you finalize (Standard 3 — the mandatory step)

Composes `verify` (for values/claims) and `cite-check` (for references). Proportional to importance —
re-check what a reader will *act on*, not every digit.

- **Identify the load-bearing claims/values:** the headline result, the key deltas, anything a decision
  rests on.
- **Recompute/confirm each from source** rather than transcribing: re-run or re-read the producing
  computation and confirm it matches the stated value. For a campaign, reconcile against the **frozen
  record** (scoreboard/logbook) and require the verification status is **CONFIRMED** — a higher raw score
  that failed an overfit/sanity guard is not the headline.
- **Internal consistency:** totals/sums, units, cross-references, and figures all agree with the numbers
  in the text, and the **abstract matches the body**.
- **Citations:** every reference resolves to the real source — exact title, full author list, year, venue,
  identifier — via `cite-check`, its **claim-support confirmed from the full text, not the abstract**
  (abstract-only support is carried as PROVISIONAL and the claim softened to match). A link that 404s,
  redirects, or points to a different paper is not a citation. If you cannot find it, **flag it**; never
  invent or approximate one.
- **Flag premises:** any claim resting on a **QUESTIONABLE ASSUMPTION**, or a PROVISIONAL/unverified
  result, is marked as such — never presented as settled.
- **Emit a claim→evidence manifest** (the verification ledger): a table mapping **each load-bearing claim →
  the exact evidence that backs it** (experiment id / `result_<NN>.json` / figure / scoreboard row), **how
  it was checked**, the result, and any **planned-vs-executed delta** (what you intended to run vs what
  actually ran). Every headline claim must trace to a real artifact; a claim with no entry doesn't go in
  the document. Keep it in full for an internal audience, or as an appendix for a shareable one — so the
  report's own trustworthiness is auditable.

## Normalization pass (standard form — distinct from correctness)

A final read for **notation and standard form**, kept separate from the correctness re-check above:
consistent symbols / units / sign conventions, field-standard nomenclature, idiomatic over idiosyncratic
phrasing. This is a *more-standard-way* pass — it may **never change a result, a number, or its meaning**
(that is a correctness edit, routed back through *Verify before you finalize*). Where the standard form is
ambiguous, flag it — don't silently rewrite.

## Section arc (physics-report default — adapt or omit per report type)

A lit review has no parameter table; a short memo collapses several sections. This is the default for a
results/methods report:

1. **Title / authors / date / abstract** — the headline result *with its number* + the one or two key
   evidence deltas; honest (lead with what is shown, state the band).
2. **Introduction & objective** — the problem, the goal and the decision it drives, what is claimed,
   position vs the literature (what gap it fills, what *not* to claim).
3. **Problem framing & scope** *(from `frame-problem`)* — physics included vs excluded + why; assumptions;
   domain of validity; the decomposition.
4. **Physical & model parameters** — the master parameter table + prose for the key few.
5. **Methods, pipeline & derivations** — end-to-end; the metric defined.
6. **Verification & validation** — the verification plan executed + the verification ledger.
7. **Results & evidence** — the evidence ledger; the headline figure; per-lever deltas; uncertainty bands
   on every reported quantity.
8. *(optional)* **Promising alternatives** — the road not taken, brief.
9. **Reproducibility** — exact configs, commands, seeds, data provenance, environment, file pointers.
10. **Limitations & open questions** — the known ceiling, unresolved disputes, every provisional /
    assumption-dependent claim marked as such.
11. **References** — verified.

## Assemble & compile

- **LaTeX capstone (default for shareable physics reports).** Start from the bundled `assets/`:
  `report_skeleton.tex` (REVTeX `revtex4-2`, APS/PRX substyle, the arc above pre-stubbed with a
  `ruledtabular` parameter table) and `report-macros.sty` (portable, siunitx/physics/braket-**free** so it
  compiles on a base TeX install — the non-base classes/styles are vendored alongside, so no package
  install is ever needed). Copy the asset folder into a fresh report dir, set
  `\graphicspath` to your figure dir, fill it in, generate `refs.bib` from the verified citations, and
  compile with `latexmk -pdf -interaction=nonstopmode -halt-on-error report_skeleton.tex`.
- **Vendor, don't install.** Non-base classes/styles (`revtex4-2.cls`, `apsrev4-2.bst`) ship **inside the
  asset folder** so no package-install approval is ever needed. If a class is genuinely missing and cannot
  be vendored, fall back to the plain-`article` draft template.
- **Read the `.log` and fix until clean.** Treat compile errors as yours to solve: bad ref/citation key →
  fix it; missing figure → correct the path or regenerate; loop until the PDF builds with no errors and no
  unresolved `??` / "missing figure" warnings.
- **No local compiler? Emit an Overleaf folder.** Zip the self-contained report dir (`.tex`, vendored
  `.cls`/`.bst`/`.sty`, `refs.bib`, `figs/`) and tell the user to upload it to Overleaf — full TeX, zero
  installs. The report is *not* done until it either compiled locally or was packaged this way.
- **Draft / Markdown / Word.** For a draft, the plain-`article` template or Markdown is fine. For Word,
  hand the assembled content to the `docx` skill rather than rendering by hand.

## Before you call it done — checklist

- [ ] Every parameter that entered the result is in the table, each with provenance + justification + uncertainty.
- [ ] Every load-bearing claim/value was recomputed or reconfirmed from source (not transcribed).
- [ ] Every number is provenance-labeled; the honest band (not the optimistic edge) is reported.
- [ ] Every citation was verified to a real source (`cite-check`); unconfirmable ones are flagged, not invented.
- [ ] Provisional / assumption-dependent claims are marked as such.
- [ ] Physics included/excluded + the steps + how it was verified are stated (from `frame-problem`).
- [ ] Internal consistency holds: totals, units, cross-references, abstract ↔ body.
- [ ] Reproducibility pointers (configs/commands/seeds/data) are present for the headline result.
- [ ] It compiles clean (or the Overleaf folder is emitted) — no `??`, no missing figures, no TODOs.
- [ ] Normalization pass done: notation/units/nomenclature consistent and in standard form; no result or meaning changed.

Then tell the user where the `.tex` / `.pdf` (or the doc) and the generated figures live, and give a 3–4
line summary of the headline result and its strongest evidence.

## Composition & scaling

- **`final-report`** (campaign capstone) composes this skill, then adds the campaign harvest (selected
  config, full evidence ledger, discoveries, disputes) and the REVTeX capstone packaging.
- **Periodic campaign progress** is this skill in *progress* mode — no separate skill.
- For a large report (many results, long bibliography), fan the gathering out to subagents — harvest
  evidence for distinct groups, verify citations in parallel, generate figure sets — then **assemble and
  compile in one place** so voice, symbols, and cross-references stay consistent. The harvest, citation
  checks, and figure/compile mechanics run well on a **lighter model**; keep the writing, the provenance
  labeling, and the load-bearing-claim re-checks on the strong model.

## Bundled assets
- `assets/report_skeleton.tex` — REVTeX capstone skeleton (the arc above, pre-stubbed).
- `assets/report-macros.sty` — portable physics macros (no siunitx/physics/braket). Smoke-tested on base TeX Live.
- `assets/refs.bib` — empty bibliography stub to fill from verified citations.
- `assets/draft_article.tex` — plain `article` one-column draft template (no REVTeX needed).
- `assets/README.md` — asset notes + the vendoring step (`revtex4-2.cls`, `apsrev4-2.bst`).
