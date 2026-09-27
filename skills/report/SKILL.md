---
name: report
description: >-
  Write up finished work as a rigorous report or document: every number provenance-labeled, claims
  re-checked, citations verified. In a campaign, the end-of-campaign capstone.
---

# report — the general scientific-document engine

A report is the artifact that outlives the work. It is what a collaborator, or the author a year later,
reads to learn what was found, why, and on what evidence, and to reproduce it where that matters. This
skill produces that artifact for any task, from a one-off fit writeup to a methods paper to a campaign's
capstone. One engine, three modes; the campaign capstone is this skill plus the campaign-specific
instructions in [`references/campaign-capstone.md`](references/campaign-capstone.md), not a separate tool.

The work being reported is complete. Do not launch new experiments or change results to make the account
cleaner. The only new artifacts produced here are explanatory figures and the document itself. If the
report-time check finds a wrong number, correct the report and tell the user the underlying result needs
attention. Do not carry the wrong number forward.

## Set the mode first

Four dials decide the shape of the document. Settle them before writing; ask if unclear.

- **Audience.** *Internal* (rich: interpretation, open questions, dead ends, the verification ledger in
  full) or *shareable* (plain: data, method, comparison, results). Both carry the same facts and caveats.
  Only the register differs; audience never changes what is disclosed.
- **Stage.** *Draft* (fast, plain `article` or Markdown, structure and numbers right) · *progress* (a
  checkpoint snapshot: what is known, what is open) · *capstone* (the polished, reproducible, shareable
  deliverable). Verification (Standard 3) is mandatory before any shareable or capstone output. For an
  internal draft it can be lighter, but it is never skipped for the headline numbers.
- **Format.** LaTeX is the default for scientific reports (REVTeX/APS for a physics capstone; see
  *Assemble & compile*). Use Markdown for a quick internal draft or a doc that lives in the repo; use Word
  (the `docx` skill) when the recipient needs it. Do not re-implement rendering: compose the format skill
  that owns it (`docx`, `pdf`, `pptx`).
- **Where.** *In a campaign* (the capstone, or a progress note on a campaign): read
  [`references/campaign-capstone.md`](references/campaign-capstone.md) first. It says where each source
  lives, that the selected configuration is the campaign's gated record and never re-derived, that the
  claim audit runs before the evidence ledger, and which labels the report must print. *Outside a
  campaign*: skip it.

## The five standards (the rubric you grade your own draft against)

A report is finished only when it passes all five.

1. **Evidence-backed.** Every claim and number traces to a named source: an experiment id, a
   file/computation, or a citation. Quote the value or delta and where it came from. No free-floating
   assertions. If a choice has no evidence, state that plainly rather than rationalize it.
2. **Honest.** Label every number by provenance (see below). Report the honest band and the assumption
   that drives it, not the optimistic edge. Lead with the bad news. Surface limitations, the known
   ceiling, PROVISIONAL findings, and unresolved disputes. Give the road not taken its brief due.
3. **Verified.** Re-check key claims and values at report time (composes `verify` and `cite-check`; see
   *Verify before you finalize*). Never put a number in a report without reconfirming it from source.
4. **Traceable / reproducible.** Give the pointers so a reader can follow each result and regenerate the
   headline one: config, command, seed, data provenance, file/section. A report that cannot be regenerated
   from its stated pointers has failed its primary job.
5. **Polished.** Compiles clean (no `??`, no missing figures); units and math typeset; captions state the
   takeaway, not the subject ("Figure of the fit" fails); figures legible; notation consistent; citations
   clickable and real.

## Honest-provenance labels (Standard 2)

Label, do not blend. Pick the scheme that fits the artifact and keep it consistent:

- **Numbers:** *analytic* (closed form, exact within stated assumptions) · *computed* (simulated/measured
  and validated) · *scaffold* (depends on an unpinned input; flag it).
- **Prose findings:** *claim* (asserted, evidence given) · *assumption* (taken as given) · *open* (not yet
  resolved).
- **Parameters (in the table):** *user-given · fitted · swept · first-principles · simulation · locked ·
  assumed · literature*. A parameter with no supporting source is labeled "empirical / lab-internal"; that
  is a valid provenance, stated rather than concealed.

## Procedure

0. **Set the dials and gather sources.** Collect the material: for a general task, the analysis,
   computations, and data the user points to; in a campaign, the sources the reference names (the
   ledger, logbook, findings, configs, the project overview `PROJECT.md`, the `frame-problem` artifact).
   Build an accurate map of what plays each role first; downstream quality depends on it.
1. **Map material to roles:** the thesis/result · supporting evidence (numbers + their sources) ·
   parameters · the physics model + assumptions · methods/pipeline · figures · references.
2. **Problem framing & scope** (from `frame-problem` if it ran). State the goal, the decomposition and
   steps taken, and how it was verified (the verification plan). Then two tables that state the domain
   of validity up front:
   - **The physics inventory** — one row per physical effect that could matter: effect · *included /
     excluded / parked* · why (the bound or estimate that justifies excluding it, or the reason it is in)
     · where it enters (equation or pipeline stage) · evidence pointer. An excluded effect with no number
     behind "negligible" is a guess; say so.
   - **The assumptions register** — one row per assumption the result rests on: assumption · where it
     enters · what rests on it (which claims or parameters) · status (*verified · provisional · open ·
     superseded*) · the check or evidence that set the status. Every assumption that was never checked is
     *open*, listed, not hidden. A superseded assumption stays in the register with its successor named
     and nothing load-bearing on it.
3. **Build the evidence ledger.** For each headline claim or feature: the value/delta, its source
   (experiment id or computation), and its verification status. Where a value came from a sweep, the
   evidence is the curve and its optimum; from a fit, the anchors and the fitted value with uncertainty;
   from a lock, the reason it is frozen.
4. **Master parameter table.** One row for every parameter that entered the final product: symbol ·
   meaning · value (+units) · role (which equation or pipeline stage it enters) · how set (fitted, to
   which anchors, by what procedure · swept, range → optimum · locked, why · assumed, source · literature,
   citation key) · uncertainty · evidence pointer (the in-campaign number or computation, with its id) ·
   source (citation key, else "empirical / lab-internal"). Then, for the handful that matter most,
   including any whose values were contested, a paragraph each: the physics, the governing equation, how
   the value was pinned (derivation / fit result / simulation), and the evidence. The long tail of
   locked/standard parameters can live in the table alone. Do not omit a parameter because it is obvious;
   unstated parameters are where reproducibility leaks.
5. **Methods, pipeline & derivations** — end-to-end so it can be re-run (raw input → each step → result).
   Derive what is specific to this work; cite standard textbook results rather than re-deriving them.
   Define the metric / figure of merit precisely, including its known degeneracies or ceiling. Keep
   symbols consistent with the parameter table.
6. **Figures.** Curate the most informative existing figures (prefer final over early) and generate the
   explanatory ones: a geometry/schematic, a pipeline diagram, an evidence/ablation chart, and the
   headline-result figure. Every caption states the takeaway; axes are labeled with units; text is
   legible. Copy used figures into the report's figure dir so it is self-contained.
7. **Verify (Standard 3).** Run the report-time check below.
8. **Assemble & compile.** Build into a fresh in-tree output directory: in a campaign, the campaign's
   `final_report/`; for a project-level or cross-campaign writeup, the project's single `reports/` home;
   outside any project (a one-off memo), a fresh local dir. Keep LaTeX build artifacts
   (`.aux/.log/.out/.fls`) out of source control via `.gitignore`. The compiled PDF lives in-tree beside
   its source. Apply the right register and the provenance labels; compile and self-correct until clean,
   or emit the Overleaf folder if there is no local compiler (see *Assemble & compile*).
9. **Grade against the five standards + the checklist** before declaring done.

## Verify before you finalize (Standard 3 — the mandatory step)

Composes `verify` (for values/claims) and `cite-check` (for references), proportional to importance:
re-check what a reader will act on, not every digit.

- **Identify the load-bearing claims/values:** the headline result, the key deltas, anything a decision
  rests on.
- **Recompute/confirm each from source** rather than transcribing: re-run or re-read the producing
  computation and confirm it matches the stated value. A number the model produced by mental arithmetic
  (a delta, a ratio, a "which is larger") is not a source; regenerate it from code and point at the code.
  In a campaign, reconcile against the frozen record and print each claim's verification label; a
  shareable report needs the headline's to be independent (the reference says how).
- **Internal consistency:** totals/sums, units, cross-references, and figures all agree with the numbers
  in the text, and the abstract matches the body. A number restated in several places agrees at all of
  them.
- **Citations:** every reference resolves to the real source via `cite-check`: exact title, full author
  list, year, venue, identifier. Claim support is confirmed from the full text, not the abstract;
  abstract-only support is carried as PROVISIONAL and the claim is softened to match. A link that 404s,
  redirects, or points to a different paper is not a citation. Flag any reference that cannot be found;
  never invent or approximate one.
- **Flag premises:** any claim resting on a QUESTIONABLE ASSUMPTION, or a PROVISIONAL/unverified
  result, is marked as such and never presented as settled.
- **Emit a claim→evidence manifest** (the verification ledger): a table mapping each load-bearing claim to
  the evidence that backs it (experiment id / `result_<NN>.json` / figure / ledger row), how it was
  checked, the result, its verification label, and any planned-vs-executed delta (what was intended to run
  vs what ran). Every headline claim must trace to a real artifact; a claim with no entry does not go in
  the document. Keep it in full for an internal audience, or as an appendix for a shareable one, so the
  report's own trustworthiness is auditable.

## Normalization pass (standard form — distinct from correctness)

A final read for notation and standard form, kept separate from the correctness re-check above:
consistent symbols / units / sign conventions, field-standard nomenclature, idiomatic over idiosyncratic
phrasing. This pass may never change a result, a number, or its meaning; that is a correctness edit,
routed back through *Verify before you finalize*. Where the standard form is ambiguous, flag it; do not
silently rewrite.

## Section arc (physics-report default — adapt or omit per report type)

A lit review has no parameter table; a short memo collapses several sections. This is the default for a
results/methods report; the items marked *(campaign)* belong to the capstone:

1. **Title / authors / date / abstract** — the headline result with its number + the one or two key
   evidence deltas; honest (lead with what is shown, state the band).
2. **Introduction & objective** — the problem, the goal and the decision it drives, what is claimed,
   position vs the literature (what gap it fills, what not to claim); *(campaign)* what is frozen, and any
   metric epochs.
3. **Problem framing & scope** (from `frame-problem`) — the physics inventory and the assumptions register
   (the two tables of step 2); the decomposition.
4. *(campaign)* **The selected configuration, in depth** — what it is, every component, and why.
5. **Physical & model parameters** — the master parameter table + prose for the key few.
6. **Methods, pipeline & derivations** — end-to-end; the metric defined, with its degeneracies or ceiling.
7. **Verification & validation** — the verification plan executed + the verification ledger.
8. **Results & evidence** — the evidence ledger; the headline figure; per-lever deltas; uncertainty bands
   on every reported quantity.
9. *(optional)* **Promising alternatives** — the road not taken, brief.
10. **Reproducibility** — exact configs, commands, seeds, data provenance, environment, file pointers.
11. *(optional)* **Broader implications** — over what range the result applies; what it newly enables or
    predicts; which open problems it bears on. Stated honestly, with no overclaiming.
12. **Limitations & open questions** — the known ceiling, unresolved disputes, every provisional and
    assumption-dependent claim marked as such.
13. **References** — verified.

## Assemble & compile

- **LaTeX capstone (default for shareable physics reports).** Start from the bundled `assets/`:
  `report_skeleton.tex` (REVTeX `revtex4-2`, APS/PRX substyle, the arc above pre-stubbed with a
  `ruledtabular` parameter table) and `report-macros.sty` (portable, free of siunitx/physics/braket, so it
  compiles on a base TeX install; non-base classes/styles are vendored alongside, so no package install
  is needed). Copy the asset folder into a fresh report dir, set `\graphicspath` to the figure
  dir, fill it in, generate `refs.bib` from the verified citations, and compile with
  `latexmk -pdf -interaction=nonstopmode -halt-on-error report_skeleton.tex`.
- **Vendor, don't install.** Non-base classes/styles (`revtex4-2.cls`, `apsrev4-2.bst`) ship inside the
  asset folder, so no package-install approval is needed. If a class is missing and cannot be vendored,
  fall back to the plain-`article` draft template.
- **Read the `.log` and fix until clean.** Compile errors are in scope: fix a bad ref or citation key;
  correct the path or regenerate a missing figure. Loop until the PDF builds with no errors and no
  unresolved `??` / "missing figure" warnings.
- **No local compiler? Emit an Overleaf folder.** Zip the self-contained report dir (`.tex`, vendored
  `.cls`/`.bst`/`.sty`, `refs.bib`, `figs/`) and tell the user to upload it to Overleaf. The report is not
  done until it either compiled locally or was packaged this way.
- **Draft / Markdown / Word.** For a draft, the plain-`article` template or Markdown is sufficient. For
  Word, hand the assembled content to the `docx` skill rather than rendering by hand.

## Before you call it done — checklist

- [ ] Every parameter that entered the result is in the table, each with role, how set, uncertainty, evidence, and source.
- [ ] The physics inventory lists every effect that could matter as included, excluded, or parked, with the number or reason behind each exclusion.
- [ ] The assumptions register lists every assumption the result rests on with its status; none is silently open; nothing load-bearing rests on a superseded one.
- [ ] Every load-bearing claim/value was recomputed or reconfirmed from source, not transcribed; no number is the model's arithmetic.
- [ ] Every number is provenance-labeled; the honest band, not the optimistic edge, is reported.
- [ ] Every citation was verified to a real source (`cite-check`); unconfirmable ones are flagged, not invented.
- [ ] Provisional / assumption-dependent claims are marked as such.
- [ ] Internal consistency holds: totals, units, cross-references, restatements, abstract ↔ body.
- [ ] Reproducibility pointers (configs/commands/seeds/data) are present for the headline result.
- [ ] It compiles clean, or the Overleaf folder is emitted: no `??`, no missing figures, no TODOs.
- [ ] Normalization pass done: notation/units/nomenclature consistent and in standard form; no result or meaning changed.
- [ ] *(campaign)* The reference's own checklist passed.

Then tell the user where the `.tex` / `.pdf` (or the doc) and the generated figures live, and give a 3–4
line summary of the headline result and its strongest evidence.

## Composition & scaling

- **In a campaign** this skill is the capstone: the *Where* dial routes to
  [`references/campaign-capstone.md`](references/campaign-capstone.md), which adds the campaign harvest
  (the gated selected configuration, the claim audit, the evidence ledger's campaign forms, the labels)
  to the procedure above. Periodic campaign progress is this skill in *progress* mode. There is no
  separate campaign report skill.
- For a large report (many results, long bibliography), fan the gathering out to subagents: harvest
  evidence for distinct groups, verify citations in parallel, generate figure sets. Then assemble and
  compile in one place so voice, symbols, and cross-references stay consistent. The harvest, citation
  checks, and figure/compile mechanics run well on a lighter model; keep the writing, the provenance
  labeling, and the load-bearing-claim re-checks on the strong model.

## Bundled assets
- `references/campaign-capstone.md` — the campaign-specific instructions, read in campaign mode only.
- `assets/report_skeleton.tex` — REVTeX capstone skeleton (the arc above, pre-stubbed).
- `assets/report-macros.sty` — portable physics macros (no siunitx/physics/braket). Smoke-tested on base TeX Live.
- `assets/refs.bib` — empty bibliography stub to fill from verified citations.
- `assets/draft_article.tex` — plain `article` one-column draft template (no REVTeX needed).
- `assets/README.md` — asset notes + the vendoring step (`revtex4-2.cls`, `apsrev4-2.bst`).
