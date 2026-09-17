---
name: claim-audit
description: >-
  Campaign-scale audit of exported claims, at campaign end.
---

# claim-audit — the capstone: what no per-unit verifier can see

Per-unit verification checks a claim as stated, given the campaign's contract. It cannot see that the
contract's floor was never measured, that the best of forty configs is optimistically biased by
construction, that a kill was written up from an INCONCLUSIVE, or that the headline does not reproduce
from a clean checkout. Those are properties of the whole campaign, and they are what a researcher pays
for at the end. This skill is that payment, sized by the campaign's verification preset
(`configs/loop.json` `verify.preset`; the `capstone` row: `default` for every preset but `intensive`,
which asks for `panel`) and never a substitute for the setup audit that should have run before anything
was frozen.

You are reporting on completed work. Launch nothing new except the checks below; change no result, no
config, no ledger row. The audit's only writes are its artifact and, per settled claim, one
`--record <exp> --finding` line (the ledger's `finding` cell).

## Claim-directed, not unit-directed

Do not "run verify on everything". Enumerate the claims the campaign is about to export, rank them,
and spend top-down within the budget:

1. **Enumerate** from the record, never from memory: the current-best (`configs/RECOMMENDED.json`), every
   scoreboard row marked `NEW BEST` or `CONFIRMED`, every ledger `finding` cell (kills with their tier,
   negatives, discoveries), the project overview's updates from this campaign, and the
   assumptions every unit inherited (`campaign.md` §The ONE metric bounds, the baseline, the floor, the
   frozen lists). Read each claim's current label from its `results/checks_<NN>.json` (`label`,
   `verification`, `self_check`, `changes`).
2. **Rank** by load-bearing weight (the headline first; then what the report will quote; then what
   steered the search) times label weakness (`unverified` > `self-checked` > a review verdict > a
   re-executed verdict).
3. **Budget**: `default` ≈ 2 unit-equivalents of the campaign's measured unit cost, `panel` ≈ 8
   (`results/timing.tsv` gives the unit cost). State the budget and what it bought; a claim the budget
   did not reach keeps its label and is listed as unaudited, never silently promoted.

## The seven checks

1. **Inherited assumptions.** `assumption-audit`'s enumerate-and-rank step, applied to the whole
   campaign: every calibration, derived quantity, threshold, and classification the current-best
   carries; rank by would-being-wrong-reproduce-this-result crossed with provenance weakness; for the
   top suspects, is there a measurement in this tree, or only a citation? The contract checks in
   `tests/correctness_checks.py` (`baseline_reproduces`, `noise_floor_measured`, `metric_discriminates`,
   `synthetic_recovery`) say whether the setup audit ran; a `skip` there is a finding here.
2. **Selection bias.** The best of N tried configurations is optimistically biased. Re-evaluate the
   winner under fresh seeds or held-out data where the campaign is reproducible, compare its margin over
   the runner-up with the recorded noise floor, and account for how many contenders were tried. A
   margin inside the corrected noise is a working best, not a win.
3. **Ledger reconciliation** (a script, not a judgement). Every exported number has a producing artifact:
   scoreboard row ↔ `result_<NN>.json` ↔ `checks_<NN>.json` ↔ `results/verdicts/` ↔ `RECOMMENDED.json`
   ↔ `campaign.metric_epochs`. Recompute each exported number from its raw artifact. A number with no
   artifact, a verdict with no matching row, a promotion under a rolled-back epoch, a comparison across
   epochs — each is a defect to name.
4. **Narrative against evidence.** Read the JOURNAL's story against the numbers: a kill written from an
   INCONCLUSIVE, a "confirmed" that cites a review of a unit the preset said to re-execute, a finding
   that cites no verdict, a claimed effect with no change behind it in the unit's `changes` block.
5. **Search adequacy.** Was a serious attempt made to beat the current-best before calling it the answer:
   an orthogonal lever tried, or a reasoned argument that further gain is non-physical
   (`campaign-status` asks the same of a "done" claim). An unfalsified "we're done" is a flag.
6. **Physical plausibility and the literature gap.** Units, limits, and the a-priori range for the
   headline; a quantified comparison with published values, resolved (which is right, and why), never
   averaged. Does the metric measure the mission (`campaign.md` §Mission), or a proxy that drifted?
7. **The stranger test.** Reproduce the headline from a clean checkout using only the report's own
   instructions (the per-experiment snapshot, the config, the run command). The strongest single check
   and the one nothing else executes. Under `default`, the headline only; under `panel`, the
   Reproducer's whole job.

## Two levels, by what each member may see

Independence comes from information partition, not from headcount: same-model agents with the same
context mostly agree with each other.

- **`default`.** The reconciliation script (check 3, and the recomputation of every exported number),
  then ONE fresh-context agent that sees everything except the session that wrote the story: checks 1,
  2, 4, 5, 6 over the ranked claims, and 7 on the headline only. One spawn buys the one independence
  boundary that matters most.
- **`panel`.** Four roles, each with a distinct information diet, then an adjudicator only on
  disagreement:
  - **Reproducer** — sees the export instructions and the repo only (no JOURNAL, no scoreboard
    narrative): check 7. Mechanism-diverse by construction.
  - **Auditor** — sees the records, not the narrative: check 3 (mostly the script; the agent reads the
    exceptions).
  - **Skeptic** — sees the claims and the narrative, tasked to break each: checks 1, 2, 4, 5. Where the
    campaign's `verify` block names a different model family, the Skeptic runs on it — the cheapest
    real independence gain available.
  - **Referee** — sees the physics and the literature, and is told the campaign's preferences are not
    evidence: check 6.
  - **Adjudicator** — spawned only when two members disagree; blinded, both positions with provenance
    stripped, required to run a check neither ran (`verify` §4b, unchanged).
  Say the limit plainly: a panel can cost as much as a short campaign, and same-model members share
  blind spots; the partition and the cross-model Skeptic are the mitigations, more seats are not.

## The artifact, the labels, and the finding cell

Write `results/verdicts/audit_<NN>.json` (zero-padded sequence, append-only; the promotion guard's
per-experiment lookup never matches it):

```json
{"kind": "claim-audit", "level": "default | panel", "utc": "<stamp>", "preset": "<verify.preset>",
 "budget_units": 2, "spent_units": 1.6,
 "claims": [{"id": "<exp id or finding>", "kind": "headline | promoted | kill | negative | discovery | assumption",
             "label_before": "<label>", "label_after": "<label>", "verdict": "CONFIRMED | ... ",
             "role": "<who checked it>", "evidence": ["<paths>"]}],
 "checks": {"inherited_assumptions": {"status": "pass | fail | skip | not_run", "detail": "", "evidence": []},
            "selection_bias": {}, "ledger_reconciliation": {}, "narrative_vs_evidence": {},
            "search_adequacy": {}, "plausibility_literature": {}, "stranger_test": {}},
 "headline": {"exp_id": "<id>", "label_before": "", "label_after": "", "downgraded": false, "reason": ""},
 "disagreements": [], "adjudication": null, "metric_version": "<current>", "unaudited": ["<claim ids>"]}
```

A claim's label may go UP (an `unverified` headline the stranger reproduced and the Skeptic failed to
break gets `CONFIRMED/audit`) or DOWN (a `CONFIRMED/review` headline that did not reproduce becomes
`REFUTED/audit`). A label is never softened: a REFUTED stays REFUTED. The audit never edits
`configs/RECOMMENDED.json` or a scoreboard row — the label lives in the artifact, and `report` (campaign mode)
prints it. Record each settled claim on its own ledger row:
`python scripts/run_campaign.py --record <exp> --finding "Claim audit (<level>): <label_after> —
results/verdicts/audit_<NN>.json"` (add `--replace` where the row already carries a finding; the
earlier text stays in the logbook and `results/journal_archive/`).

## Composition

- **`report`, in campaign mode,** runs this before it builds its evidence ledger, and refuses a shareable report
  while any exported claim's label is non-independent (`unverified`, `self-checked`) and no audit covers
  it; an internal draft may proceed with the labels printed. The report's verification ledger prints
  `label_after` per claim and says "downgraded by audit" where true.
- **The driver** spawns the audit at STOP or convergence when the preset's `capstone` row is not `off`
  (the `intensive` preset asks for `panel`); the user may run it at any time.
- **`assumption-audit`** supplies check 1's method; **`verify`** §4b supplies the adjudicator; the
  reconciliation script is the same reading `campaign-status` does of the ledger, executed rather than
  narrated.

## Before you call it done — checklist
- [ ] Every exported claim was enumerated from the record, ranked, and either audited or listed unaudited.
- [ ] The seven checks each carry a status and evidence paths; the stranger test ran on the headline.
- [ ] The budget and what it bought are stated; nothing ran beyond it without saying so.
- [ ] Labels moved only on evidence, never softened; `RECOMMENDED.json` and the scoreboard untouched.
- [ ] The artifact is `results/verdicts/audit_<NN>.json` and each settled claim carries a `finding` cell citing it.
- [ ] Under `panel`, each member saw only its partition, and any disagreement went to the blinded adjudicator.
