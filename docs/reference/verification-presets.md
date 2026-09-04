# Verification presets — how much checking a campaign buys, and of what kind

One choice sets it: `configs/loop.json` `verify.preset`, one of **`minimal` · `light` · `moderate` ·
`intensive`**. `new-campaign` presents the four descriptions below verbatim when a campaign is set up;
the driver prints the table each preset resolves to at preflight and stamps the preset into every
`results/checks_<NN>.json`. There are no knobs to combine. This file is the single description of what
each preset means; `campaign-status` and the claim audit read the same words.

## What every preset does, whatever the choice

- **The runner floor always runs**: the FROZEN scorer's self-test, the mechanical checks artifact
  (prediction, noise floor, comparability, hard bounds, save-set, epoch), and the ledger and epoch gates.
  A campaign cannot grow it and a preset cannot turn it off.
- **Cheap authored invariants run every unit** (`@check(row="invariants")` in
  `tests/correctness_checks.py`), metered against a budget of one tenth of the campaign's measured unit
  cost (never below thirty seconds): an over-budget set is refused at preflight by name, and a check
  that grows slow mid-campaign is demoted to promotion-time, loudly, never silently skipped.
- **The worker records its own checks** (`--self-check`), directed at what the unit changed; that gives a
  result the label `self-checked`. A self-check is never independent verification.
- **Verification starts from what changed.** The runner records, per experiment, what moved since the
  last verified unit (code compared as code, config keys, version tags); an independent verifier
  verifies that delta and its interaction with the unchanged parts.
- **Re-execution depth is decided per unit, by the driver, not by the preset alone**: the preset says
  whether an independent check is owed; the driver re-executes the unit only when its measured solve
  time is within a quarter of `worker.iteration_timeout_hours` and `campaign.reproducible` is true
  (`configs/loop.json`), and otherwise has it reviewed from the frozen record; the verdict says which.
- **Every exported claim carries an honest label**: `unverified` · `self-checked` · `<VERDICT>/review` ·
  `<VERDICT>/re-execution` (in `results/checks_<NN>.json` `label`), and, from the claim audit's own
  artifact, `<VERDICT>/audit`. The first two are *non-independent*; the rest are *independent* labels.
  `unverified` is a legitimate label; a softened one is not — a recorded verdict is never replaced by a
  weaker label, and a self-check never counts as independent.
- **The claim audit** at the end of the campaign (`claim-audit`; composed by `final-report`) checks what
  no per-unit verifier can: inherited assumptions, selection bias, ledger reconciliation, narrative
  against evidence, search adequacy, physical plausibility against the literature, and a stranger's
  reproduction of the headline. A shareable report waits for it while any exported claim lacks an
  independent label.

## The four presets

Each entry has the same seven fields: summary · what runs each unit · what a promotion needs · what the
label says · the end-of-campaign audit · when to choose it · rough cost.

### `minimal` — exploration only

- **Summary.** The floor and the cheap invariants; nothing independent. For finding out whether a
  direction is worth a campaign at all.
- **Each unit.** The runner floor; the authored invariants; the worker's self-check.
- **A promotion needs.** Nothing beyond a correctness suite that is not RED (no failing check) — and
  the promotion must say `unverified` (in `RECOMMENDED.json` as `"verification_label": "unverified"`; on
  the scoreboard row as UNVERIFIED). The guard refuses a promotion that does not carry the word. A
  self-checked unit still promotes as `unverified`: a self-check is not independent.
- **The label.** `unverified`, or `self-checked` where the worker recorded one. Findings and a
  shareable report wait for the claim audit; its artifact is the citation a Finding needs.
- **End of campaign.** The default claim audit: a reconciliation script plus one fresh-context agent
  over the exported claims, with a stranger's reproduction of the headline.
- **Choose it when** the problem is one the agent will likely get right first time, a wrong answer costs
  little, and you will read the record yourself before anything leaves the campaign.
- **Cost.** No verifier spawns; the audit at the end (about two units' worth).

### `light` — the default

- **Summary.** Cheap checks every unit, the authored machinery checks once at setup, and an independent
  review before each promotion.
- **Each unit.** The runner floor; the authored invariants; the worker's self-check. The machinery checks
  (analytic limits, known answers, parity, convergence) run at setup and again whenever a FROZEN-core
  change makes everything due.
- **A promotion needs.** A CONFIRMED verdict from an independent fresh-context reviewer, who recomputes
  from the frozen record and verifies the delta; the per-result gates (the suite's `gates` row) run for
  the candidate first.
- **The label.** `self-checked` for most units; `<VERDICT>/review` for promotion candidates.
- **End of campaign.** The default claim audit.
- **Choose it when** the pipeline is understood, solves are cheap, and few assumptions are inherited:
  the common case. It is the default because most units are not promotion candidates, and a review of
  each candidate catches most of what re-executing everything would, at a fraction of the spend.
- **Cost.** About one verifier spawn per promotion candidate; roughly a tenth of the campaign's spend on
  checking.

### `moderate`

- **Summary.** As `light`, plus the machinery checks re-run whenever the code they cover changes, and the
  independent check before a promotion re-executes the unit when it is cheap and reproducible.
- **Each unit.** The runner floor; the authored invariants; the worker's self-check; any machinery check
  whose traced code moved since it last ran.
- **A promotion needs.** A CONFIRMED verdict — from a re-execution when the unit is eligible, from a
  review when it is not; the guard refuses a review-mode verdict on a unit the preset said to re-run.
- **The label.** `self-checked` for most units; `<VERDICT>/re-execution` or `<VERDICT>/review` for
  promotion candidates.
- **End of campaign.** The default claim audit.
- **Choose it when** the model code changes often (a model-improvement campaign), or a promotion is
  expensive to get wrong, but the solve is cheap enough that re-running a candidate is affordable.
- **Cost.** One verifier spawn plus one solve per promotion candidate; machinery re-runs when code moves.

### `intensive` — every unit, every check

- **Summary.** Every authored check and an independent check on every unit, batched per block; a
  different-model refuter where an adapter is configured; the verifier blinded from the narrative; a
  panel claim audit at the end.
- **Each unit.** Everything: the floor, every authored check (metered), the self-check, and an
  independent re-execution (review where the unit is not eligible) of every unit, one spawn per
  completed block of related units.
- **A promotion needs.** A CONFIRMED verdict of the depth the unit was eligible for.
- **The label.** `<VERDICT>/re-execution` or `<VERDICT>/review` on every unit.
- **End of campaign.** The panel claim audit: four information-partitioned roles (a reproducer who sees
  only the export instructions, an auditor who sees only the records, a skeptic who sees the claims and
  the narrative, a referee who sees the physics and the literature) and a blinded adjudicator on
  disagreement.
- **Choose it when** the model is new, the fit is fragile, or the number will be published: when a
  plausible-looking wrong answer is both likely and expensive.
- **Cost.** One verifier spawn per block plus a solve per eligible unit; checking can cost as much as
  the search. This is what the kit did for every campaign before presets existed.

## Changing the preset

Edit `verify.preset` in `configs/loop.json` at any time. The driver logs the change at its next loop top,
and every result records the preset it ran under, so a campaign that changed presets reads as two
regimes, not one. Lowering the preset never relabels a result already verified; raising it does not
verify results retroactively — run `--run-suite due --for <exp>` and the verify skill for those you
now want covered.

## Presets and the metric-revision dial

Two independent choices, asked together at setup: the preset says how much verification the campaign
buys; `campaign.metric_revision` (`cautious` | `autonomous`) says whether the loop may revise the FROZEN
metric on its own. A campaign can be `autonomous` and `light`, or `cautious` and `intensive`.
