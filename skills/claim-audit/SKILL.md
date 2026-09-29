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
for at the end. This skill is that payment: the driver runs it at the end of the loop under every
verification preset but `none` (`configs/loop.json` `verify.preset`, the `capstone` row;
`docs/reference/verification-presets.md`), and you may run it at any time. It re-checks the final best
once more, whatever that best was checked with in the loop - the one exception to "one check per result".
It is never a substitute for the setup audit that should have run before anything was frozen.

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
   `verification`, `self_check`, `changes`). The final best named in your VALUES is always on the list,
   with its delta since the last independent check.
2. **Rank** by load-bearing weight (the headline first; then what the report will quote; then what
   steered the search) times label weakness (`unverified` > `self-checked` > `self-verified` >
   `<VERDICT>/peer` > `<VERDICT>/verifier`; an old `/review` or `/re-execution` reads as `/verifier`).
3. **Budget**: ≈ 2 unit-equivalents of the campaign's measured unit cost (`results/timing.tsv` gives
   it). State the budget and what it bought; a claim the budget did not reach keeps its label and is
   listed as unaudited, never silently promoted - except the final best, which is re-checked first.

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
   INCONCLUSIVE, a "confirmed" that cites a check weaker than its label (a self-verify written up as
   independent), a finding that cites no verdict, a claimed effect with no change behind it in the unit's
   `changes` block. A gate outcome set aside by judgement — a result that met every written promotion
   condition and was written up as "refused" with no `results/contests/` entry and no decision-record
   amendment — is a defect to name (the V_B⁻ test campaign's exp017 / exp019), as is a contest filed
   and never resolved.
5. **Search adequacy.** Was a serious attempt made to beat the current-best before calling it the answer:
   an orthogonal lever tried, or a reasoned argument that further gain is non-physical
   (`campaign-status` asks the same of a "done" claim). An unfalsified "we're done" is a flag.
6. **Physical plausibility and the literature gap.** Units, limits, and the a-priori range for the
   headline; a quantified comparison with published values, resolved (which is right, and why), never
   averaged. Does the metric measure the mission (`campaign.md` §Mission), or a proxy that drifted?
7. **The stranger test.** Reproduce the headline from a clean checkout using only the report's own
   instructions (the per-experiment snapshot, the config, the run command). The strongest single check
   and the one nothing else executes; it runs on the headline.

## Who does what

Independence comes from information partition, not from headcount: same-model agents with the same
context mostly agree with each other. So the audit is the reconciliation script (check 3, and the
recomputation of every exported number), then ONE fresh-context agent that sees everything except the
session that wrote the story: checks 1, 2, 4, 5, 6 over the ranked claims, and 7 on the headline. One
spawn buys the one independence boundary that matters most. Start the final best's re-check from its
delta since the last independent check (the VALUES carry it by value; `--diff <exp>` prints it).

## The artifact, the labels, and the finding cell

Write `results/verdicts/audit_<NN>.json` (zero-padded sequence, append-only; the promotion guard's
per-experiment lookup never matches it):

```json
{"kind": "claim-audit", "level": "default", "utc": "<stamp>", "preset": "<verify.preset>",
 "budget_units": 2, "spent_units": 1.6,
 "claims": [{"id": "<exp id or finding>", "kind": "headline | promoted | kill | negative | discovery | assumption",
             "label_before": "<label>", "label_after": "<label>", "verdict": "CONFIRMED | ... ",
             "role": "<who checked it>", "evidence": ["<paths>"]}],
 "checks": {"inherited_assumptions": {"status": "pass | fail | skip | not_run", "detail": "", "evidence": []},
            "selection_bias": {}, "ledger_reconciliation": {}, "narrative_vs_evidence": {},
            "search_adequacy": {}, "plausibility_literature": {}, "stranger_test": {}},
 "headline": {"exp_id": "<id>", "label_before": "", "label_after": "", "downgraded": false, "reason": ""},
 "metric_version": "<current>", "unaudited": ["<claim ids>"]}
```

A claim's label may go UP (an `unverified` headline the stranger reproduced and the audit failed to
break gets `CONFIRMED/audit`) or DOWN (a `CONFIRMED/peer` headline that did not reproduce becomes
`REFUTED/audit`). A label is never softened: a REFUTED stays REFUTED. The audit never edits
`configs/RECOMMENDED.json` or a scoreboard row — the label lives in the artifact, and `report` (campaign mode)
prints it. Record each settled claim on its own ledger row:
`python scripts/run_campaign.py --record <exp> --finding "Claim audit (<level>): <label_after> —
results/verdicts/audit_<NN>.json"` (add `--replace` where the row already carries a finding; the
earlier text stays in the logbook and `results/journal_archive/`).

## Composition

- **`report`, in campaign mode,** runs this before it builds its evidence ledger, and refuses a shareable report
  while any exported claim's label is non-independent (`unverified`, `self-checked`, `self-verified`)
  and no audit covers it; an internal draft may proceed with the labels printed. The report's
  verification ledger prints `label_after` per claim and says "downgraded by audit" where true.
- **The driver** spawns the audit at STOP or convergence when the preset's `capstone` row is not `off`
  (every preset but `none`); the user may run it at any time, and must before a shareable report of a
  `none` campaign.
- **`assumption-audit`** supplies check 1's method; the reconciliation script is the same reading
  `campaign-status` does of the ledger, executed rather than narrated.

## Before you call it done — checklist
- [ ] Every exported claim was enumerated from the record, ranked, and either audited or listed unaudited.
- [ ] The final best was re-checked once, from its delta since the last independent check.
- [ ] The seven checks each carry a status and evidence paths; the stranger test ran on the headline.
- [ ] The budget and what it bought are stated; nothing ran beyond it without saying so.
- [ ] Labels moved only on evidence, never softened; `RECOMMENDED.json` and the scoreboard untouched.
- [ ] The artifact is `results/verdicts/audit_<NN>.json` and each settled claim carries a `finding` cell citing it.
