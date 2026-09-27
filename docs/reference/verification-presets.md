# Verification presets — how much checking a campaign buys, and of what kind

One choice sets it: `configs/loop.json` `verify.preset`, one of **`none` · `minimal` · `light` · `heavy` ·
`intensive`**. `new-campaign` presents the five descriptions below verbatim when a campaign is set up;
the driver prints the table each preset resolves to at preflight and stamps the preset into every
`results/checks_<NN>.json`, and the worker's brief carries only its own preset's instructions. There are
no knobs to combine. This file is the single description of what each preset means; `campaign-status`
and the claim audit read the same words.

## What every preset does, whatever the choice

- **The runner floor always runs**: the FROZEN scorer's self-test, the mechanical checks artifact
  (prediction, noise floor, comparability, hard bounds, save-set, epoch), and the ledger and epoch gates.
  It is what keeps the ledger honest, not verification; a preset cannot turn it off.
- **One check per result.** Each result gets at most ONE check, the strongest its preset owes it,
  decided by the runner when the result is recorded (`verification.owed` in its checks artifact, and on
  the card). A result owed an independent check is never also self-verified. The one exception is the
  end of the campaign: the claim audit re-checks the final best once more.
- **The kinds of check.** A *self-check* is the directed checks the worker records every unit
  (`self_check`), only those the runner does not already run. A *self-verify* is the `verify` protocol
  (predict, then refute: beat it, enumerate its class, seek a counterexample) run by the worker on its
  own result, in its own session - never independent. An *independent check* comes from a context other
  than the one that produced the result: a **peer** (the next worker - a fresh context that reads the
  previous worker's narrative) or a **verifier** (spawned by the driver with the change record and the
  metric by value; **blinded** under `intensive`, when it may not read the JOURNAL or the logbook). A
  worker never spawns an agent to check anything.
- **A new best's check waits for survival.** A result is a *new best* when it beats the incumbent by
  more than the campaign's resolution (the tolerance, deterministic; the noise floor, stochastic) under
  the same metric version. Where a preset checks new bests independently, the check runs once the next
  unit has not beaten it. A best beaten first gets no check of its own: its successor's check covers what
  it changed.
- **Every check starts from what changed** since the last check of its kind (the runner records it;
  `--diff <exp>` prints it), and every new agent gets that delta by value. An independent check starts
  from the last *independent* check, so an independent label never rests on code only a self-verify saw.
- **The pointer follows the true best at once**, carrying its current label (`RECOMMENDED.json`
  `verification_label`); a check upgrades the label, and a refutation rolls the pointer back to the best
  result not refuted. The promotion guard enforces the label, not the existence of a verdict.
- **Every exported claim carries an honest label**: `unverified` · `self-checked` · `self-verified` ·
  `self-refuted` (non-independent) · `<VERDICT>/peer` · `<VERDICT>/verifier` · `<VERDICT>/audit`
  (independent). `unverified` is a legitimate label; a softened one is not - a recorded verdict is never
  replaced by a weaker label. A shareable report waits for the claim audit while any exported claim lacks
  an independent label.

## The five presets

Each entry has the same six fields: summary · what each unit gets · what a new best gets · the end of
the campaign · when to choose it · rough cost.

### `none`

- **Summary.** No mandatory verification. The worker investigates what it judges worth investigating,
  when it judges it, in its own session and outside any formal procedure.
- **Each unit.** The runner floor. No correctness-suite rows fire; no self-check is owed.
- **A new best.** Promoted `unverified`, like every result.
- **End of campaign.** No claim audit runs; a shareable report still waits for one (run
  `/physkit:claim-audit` yourself).
- **Choose it when** you are sketching: the question is whether a direction exists at all, and you will
  read everything yourself.
- **Cost.** Nothing beyond the units.

### `minimal` — the default

- **Summary.** Unit tests, and a self-verify when a result surprises.
- **Each unit.** The runner floor; the authored invariants; the worker's self-check. A result outside
  its predicted range - better or worse - is self-verified by its worker (`prediction_mode: range` only;
  without a range there is no such trigger).
- **A new best.** The same rule: self-verified if it fell outside its range, otherwise `self-checked`.
- **End of campaign.** The default claim audit, which re-checks the final best.
- **Choose it when** a wrong answer costs little and you will read the record yourself before anything
  leaves the campaign: the common case, and the default, since the claim audit still stands between the
  loop and a shareable report.
- **Cost.** A self-verify per surprising result (a few turns of the worker's own unit); the audit at the
  end.

### `light`

- **Summary.** As `minimal`, and an independent check of every best that survives, by the next worker.
- **Each unit.** The runner floor; the authored invariants, with the machinery checks once at setup;
  the self-check. A result outside its predicted range that is not a new best is self-verified.
- **A new best.** No self-verify: once the next unit has not beaten it, the NEXT worker checks it first
  thing (a peer check - its VALUES carry the result and its delta), writing a verdict labelled
  `<VERDICT>/peer`. The per-result gates run for it at record time.
- **End of campaign.** The default claim audit, which re-checks the final best.
- **Choose it when** a best is worth an independent look before the next units build on it, at little
  cost: the peer check needs no extra spawn and no orientation - the next worker is already oriented.
- **Cost.** A few turns of the next worker's unit per surviving best; the audit at the end.

### `heavy`

- **Summary.** Every result checked once: a self-verify for ordinary results, a dedicated verifier for
  every best that survives.
- **Each unit.** The runner floor; the authored invariants, with the machinery checks re-run whenever the
  code they cover changes; the self-check; a self-verify of every result that is not a new best.
- **A new best.** No self-verify: once the next unit has not beaten it, the driver spawns a verifier
  (the change record and the metric delivered by value, not the worker's narrative): `<VERDICT>/verifier`.
- **End of campaign.** The default claim audit, which re-checks the final best.
- **Choose it when** the model code changes often, or a promotion is expensive to get wrong.
- **Cost.** A self-verify in most units; one verifier spawn per surviving best.

### `intensive` — every result, independently

- **Summary.** A blinded verifier on every result.
- **Each unit.** Every authored check (metered); the self-check; no self-verify - the driver spawns a
  blinded verifier for every result, which may not read the JOURNAL or the logbook narrative.
- **A new best.** Checked at once, like every result.
- **End of campaign.** The default claim audit, which re-checks the final best.
- **Choose it when** the model is new, the fit is fragile, or the number will be published: when a
  plausible-looking wrong answer is both likely and expensive.
- **Cost.** One verifier spawn per unit; checking can cost as much as the search.

## Changing the preset

Edit `verify.preset` in `configs/loop.json` at any time. The driver logs the change at its next loop top
and the next spawn's brief carries the new preset's instructions; every result records the preset it ran
under, so a campaign that changed presets reads as two regimes, not one. Lowering the preset never
relabels a result already checked; raising it does not check results retroactively - run the verify skill
for those you now want covered. `moderate` was renamed `heavy`; a loop.json still naming it is
refused at preflight.

## Presets and the metric-revision dial

Two independent choices, asked together at setup: the preset says how much verification the campaign
buys; `campaign.metric_revision` (`cautious` | `autonomous`) says whether the loop may revise the FROZEN
metric on its own. A campaign can be `autonomous` and `light`, or `cautious` and `intensive`.
