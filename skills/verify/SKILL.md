---
name: verify
description: >-
  Adversarially check a result, number, derivation, fit, or claim, negative results too: recompute,
  falsify with code, graded verdict. Use before relying on or reporting a result, or when asked "is
  this right?".
---

# verify — assume you are wrong until independently proven right

The burden of proof is on the positive result. A result is not real until an independent check has tried to
refute it and failed. Convergence is not correctness, and a clean-looking number is not a verified one.
Warrant rides on the checker, not on the generator's reasoning. Verify by a mechanism-diverse independent
route, recompute every reported number from a fresh run, and falsify with code rather than prose: edge
cases, randomized inputs, counterexamples.

It works at two scales. General mode checks a standalone claim in any session. Campaign mode
(further down) is the full adversarial apparatus for promoting a campaign finding: it learns the metric,
scorer, and rules from the campaign's own charter and spawns an independent refuter. Use the depth the
stakes deserve.

**A campaign worker's self-verify** is general mode run on its own result, in its own session, without
§4's fresh-agent step: a worker never spawns an agent to check its work. Its output is not a
verdict and never INCONCLUSIVE for want of an agent; it goes in the unit's record as `self_verify`, and
its label (`self-verified` / `self-refuted`) says it is not independent. A **peer check** - the next
worker checking a surviving best - runs the same way, in that worker's session, and writes the verdict
artifact below with `"kind": "peer"`: independent of the reasoning that produced the result, because it
comes from a fresh context.

---

## General mode — check any result or claim

### 1 · Gather the claim, not the conclusion
Get the thing asserted and the inputs needed to reproduce it, without the author's narrative of why it is
right. Form an independent view: the reasoning under check is what might be wrong. Note the a-priori range
the answer should fall in, taken from `frame-problem` or computed now with `dimensional-analysis`. A result
outside its predicted envelope is a bug or a discovery, and this step decides which.

### 2 · Route by claim type to the decisive check
Different claims fail in different ways. Lead with the check that would catch the failure:

- **A new or derived equation / quantity → dimensional sanity-check first.** Do the units work? Invoke
  `dimensional-analysis`. Then test a limiting case: a known special case, a small- or large-parameter
  limit, or a symmetry the result must respect. An equation that fails units or a known limit is wrong.
  Stop there, before anything more expensive.
- **A computed number / result → recompute it from a fresh run.** Re-run the producing computation and
  confirm every reported number matches, not only the headline. A number that does not reproduce, or that
  was stated once and never recomputed, is REFUTED. Convergence is not correctness:
  re-derive the value rather than trusting that the solver converged. A number the model produced (mental
  arithmetic, an estimated or remembered value) rather than code is REFUTED on sight; there is nothing to
  reproduce, so regenerate it from code first. A pre-run a-priori estimate is exempt: it exists to be
  checked against the code, not reported as the result. Label each number's metric path: a relaxed or
  auxiliary score versus the frozen primary metric. An unlabelled number cannot be compared
  apples-to-apples and cannot drive a promotion.
- **A fit or a prediction → interrogate the nature of the error (§3), not just its magnitude**, in addition
  to recomputing it.
- **A claim that two quantities agree (or disagree) → test it in units of the combined uncertainty, do not
  eyeball it.** For *a ± σ_a* and *b ± σ_b* (independent errors), the tension is
  *t = |a − b| / √(σ_a² + σ_b²)*: *t ≲ 1* agree, *t ≈ 2* mild tension, *t ≳ 3* a real discrepancy, meaning
  a physical difference or an underestimated error bar and never "close enough." 141 ± 0.003 is not in
  agreement with 142 (*t ≈ 330*). Two values that agree only because both bars are large are a weak
  agreement, not a confirmation. No error bar on either side means the two are not comparable; get one
  first. For correlated errors, subtract the covariance (√(σ_a² + σ_b² − 2σ_ab)). Resolve a real tension,
  never average it (universalism). This is distinct from §4's noise-floor test of one delta against its
  own spread.
- **A comparison between candidates → check the scorer, the reference, and the starting point for
  entanglement, first.** Name all three and state what each shares with the things being compared. A
  reference that was fitted under one candidate, a scorer carrying a nuisance parameter inherited from the
  incumbent, or a sweep scored against its own starting point favours that candidate by construction, and
  the number it returns looks like evidence. Two tells: the comparison's argmin is the incumbent for every
  candidate (tautological), or the supposedly neutral arbiter reproduces one candidate's fitted parameter
  identically. Re-score under a reference that shares nothing with any candidate, or profile the shared
  component out. Never argue that the entanglement is small. Confirm too that all contenders were scored under the
  same metric and data version: if any changed, re-score the contenders under the current one. A
  comparison across versions is meaningless even when both numbers are individually real.
- **A result on a published or well-known benchmark → rule out memorization before crediting it.**
  Withhold the problem's identity where you can and re-test on synthetic instances that cannot be in
  training data (`discovery-loop` has the full gate).
- **A claim / comparison → falsify it with code.** Write controls: verify against known examples (inputs
  whose answer you can derive or look up), test edge/degenerate/extreme inputs, randomize inputs, search
  for counterexamples. Beat the trivial baselines (all-zeros / constant / mean / a trivial physical state)
  and any prior known result; a result worse than a trivial answer is not a win. If a non-physical trivial
  answer scores better than a plausible result, that flags a metric or units problem rather than a target
  to beat.
- **A "we're done / at the ceiling / blocked / optimal" conclusion → treat it as a load-bearing positive
  claim and try to REFUTE it.** A stopping decision ends the work, so it earns the same adversarial
  scrutiny as a win. Require an explicit attempt to beat the supposed limit (an orthogonal lever, a freer
  model, a cheap what-if) and a reasoned argument for why any gain found is non-physical, before the "done"
  stands. "I've stopped finding gains" is not "no gains exist"; an unfalsified ceiling is INCONCLUSIVE, not
  CONFIRMED.

### 3 · Interrogate the nature of the error — and the statistic you read it with
For any fit, regression, calibrated model, or learned predictor, do not stop at the error magnitude:
examine the residuals for structure. The last bullet, on statistic choice, applies to any claim read off a
summary number, not only to a fit.
- **Structured residuals** — a trend, a dependence on an input variable, a spatial/temporal pattern,
  autocorrelation, a systematic over- or under-shoot in one regime — signal a bug or unaccounted-for
  physics (model-form error). They point back to a parked or missing effect in the physics inventory
  (`frame-problem`), and they are among the best sources of discovery. Investigate them.
- **Random, zero-mean residuals consistent with the noise model** are what "done" looks like.
- Plot residuals against each input and against the fitted value; check for autocorrelation. "The error is
  small" is not the same as "the error is unstructured." Do not write structure off as noise without proof.
- **Check that the statistic answers the question you asked.** Name the question, name the statistic, and
  state why they match, before reading anything off the number. Four cheap mismatches, each of which has
  produced a confident wrong conclusion:
  - A mean where a max belongs. Averaging a sign-changing quantity nearly cancels it, so a ceiling built
    that way can understate by an order of magnitude. Bound with the extreme, or with a per-region swing.
  - An unpaired spread applied to a paired comparison. Two models scored on the same data are paired, and a
    Δ far inside the across-realization scatter can be many σ once paired.
  - A central statistic where the hypothesis is "rare and large". A median over hundreds of units is blind
    to a sparse subpopulation by construction and cannot return anything but a clean negative. Use a tail
    statistic.
  - A fitter fed the wrong residual. Fitting a background to *(data − model)* when the intent was to fit it
    to the data lets the fit absorb the effect being tested for.

  Same check each time: state the question in words, then ask whether this number could come out small even
  if the true answer is "large."
- Be precise about overfitting. Claim it only from a specific signature: a gain that does not hold on
  held-out data, or a fit better than the known truth. Never claim it as a catch-all, and never when the
  change raised raw fit error, which cannot be overfitting. Separate statistical from systematic error.
- **A per-step/sequential fit's clean residuals can be manufactured, not earned.** When consecutive fits
  (frame-by-frame, step-by-step) share a drifting nuisance parameter, each step can co-adapt to absorb real
  signal: the residuals look random because the model moved to hide the structure, not because it is right
  (`simulation-design` §3). Before trusting clean per-step residuals as "done," check whether a joint or
  monotonicity-constrained refit across steps reproduces them. If the constrained fit's residuals show
  structure the per-step fit's did not, the per-step version was absorbing error rather than explaining it.

### 4 · Prefer an independent, mechanism-diverse check
The strongest verification comes from a different route reaching the same answer: a second method, an
independent re-derivation, a certifying solver, an analytic cross-check. For any substantial or
load-bearing claim, spawn a fresh agent (Agent tool, `subagent_type: general-purpose`) and give it the
adversarial prompt below, so it re-derives from scratch in its own context rather than inheriting prior
assumptions. Pass the why, never the reasoning: state what this claim gates (a promotion, a report, a
decision) and the stakes, because an agent told why the check matters verifies harder than one handed a
bare task. Never share the generating reasoning or the expected answer; either contaminates the check's
independence. Replicate across seeds and perturbations for anything stochastic, and use a
statistical test for close calls: a difference smaller than the spread is not automatically noise, since
real effects can be weak, and it is not automatically real either. If no such agent can be spawned, the
check is INCONCLUSIVE — say so. A control designed by the claimant is not mechanism-diverse; it tests the
confounds already thought of, which are the ones already handled.

### 4b · When the verdict is disputed — escalate to a blinded third party
A refuter's verdict can itself be wrong, and arguing it out with the refuter reproduces the original error:
by then both parties have read the same evidence and are defending positions. Neither defer nor
re-litigate. Spawn a third agent and blind it. Hand it both positions with provenance stripped
("Analysis 1" / "Analysis 2", never which one is yours), tell it explicitly not to weight by source, and
require it to run a check neither analysis ran rather than pick a side. Its verdicts include both wrong: a
conclusion can be right while every argument offered for it is not. Held-out data already on disk and a
method neither side tried are where it earns its cost. Record its verdict alongside the dispute,
append-only. A dispute closed by argument rather than by a new measurement is still open, and a rebuttal
written by the claimant is not independent of the reasoning that produced the claim.

### 5 · Bounds & physicality
Confirm the result is physically possible: within hard bounds (probabilities in [0,1], known ranges), no
fitted parameter outside its physical range (wrong sign, out of bounds), nothing above its own ceiling.
Anything impossible means a bug or a leak. It is REFUTED until explained, and never carried into a reported
"best" config while it stands. Three traps specific to physically-motivated fits:
- A physically-shaped template with a fitted amplitude or sign is not a physical prediction. If the
  first-principles value (the physical amplitude, scale = +1, …) is not what the fit chose, or if that value
  hurts the metric, the lever is an empirical corrector in physical clothing: grade it QUESTIONABLE
  ASSUMPTION and do not credit it as first-principles.
- A known physical input that hurts the fit is an anomaly to explain, not to override with a fitted fudge
  factor. Cross-fit agreement on the same unphysical value is not validation: two fits agreeing on the same
  wrong number are both wrong.
- Frame consistency (geometry-heavy claims). For any result that crosses coordinate frames, run the
  frame-consistency check in [`docs/reference/coordinate-frames.md`](../../docs/reference/coordinate-frames.md):
  every quantity's frame declared, no symbol overloaded across frames, orientation/handedness resolved from
  an independent reference, not the fit. Correct code with undeclared frames is still unverifiable.

### 5b · Provenance, authority, and irreversible actions
A result is only as trustworthy as the facts it rests on and the source those facts came from.
- When sources conflict, resolve a load-bearing fact to the highest-authority artifact: parse the saved
  model, probe the released data, run the shipped weights. Do not resolve it to a lower-authority proxy
  (paper text, leftover code) or to a statistic you derived from the data: a correlation you computed is
  weaker than the source it came from. Rank the sources describing the same system: a shipped artifact
  or an empirical probe outranks text that states the fact (paper, figure, docs), which outranks code you
  cannot trust as the source (leftover or modified code), which outranks recollection. Tag each
  load-bearing fact by where it came from: PINNED (authoritative artifact or probe) · REPORTED (stated in
  text) · INFERRED (from an untrusted proxy) · RECALLED (from memory) · REASONED (your own engineering or
  design judgment, resting on no external claim about the system). A load-bearing fact still at INFERRED
  or RECALLED is a blocker to resolve: ask, do not default.
- Weigh a claim by its evidence, not its source. A value the user supplies enters as REPORTED or
  RECALLED, never PINNED, until a probe confirms it; a published value enters as REPORTED, with its
  uncertainty; your own earlier conclusions re-enter at the confidence they were tagged with. Deference
  that lets an error through is a verification failure, not courtesy: push back with the evidence.
- A fact acted on at INFERRED or RECALLED is itself a claim to verify. Attempt to falsify it before it
  becomes load-bearing, and run any cheaper discriminating check that is already available. An unfalsified
  inference can otherwise carry a long series of experiments before it is caught.
- Before any irreversible action (overwrite/delete/regenerate inputs, a hardware move), require the
  justifying diagnosis to reach CONFIRMED via the highest-authority artifact: read the actual pipeline
  source rather than acting on a derived statistic. Gating a destructive step to the user on a
  below-CONFIRMED diagnosis makes the human the only backstop. Confirm first.

### 5c · Reflect against your own confirmation bias (before you grade)
Once an answer has been decided, the pull is to suppress alternatives and read every new datum as
confirmation. Generating failure modes is a learnable skill, so run the ritual explicitly rather than
intending to be objective:
- State the result that was expected or hoped for, so the bias is visible.
- Make the strongest case that it is wrong. Argue the other side as hard as the original case, and list the
  concrete ways it could fail.
- Name the single observation or control that would refute it, then check whether it was actually run. If
  not, run it before concluding.
- Consider the alternative conclusion being resisted, especially an unwelcome one (the effect is noise; a
  rival model fits too; the win is an artifact), and give it a fair hearing.

This reflection complements the independent refuter (§4), which never shared the hope, and the blinded
adjudicator (§4b) owed when the refuter is disputed. It replaces neither.

### 6 · Grade the verdict and surface the premise
Return one of the five verdicts (defined below), state what is certified versus conjectured and over what
range, and name any load-bearing assumption the result hinges on. Record the reason for a non-obvious check
(`record-decision`) so it is not lost.

---

## The verdicts

- **CONFIRMED** — survived an independent attempt to refute it; reproduced, bounded, and unstructured where
  it should be. May proceed.
- **PROVISIONAL** — stands, but rests on an adapted evaluation: a guardrail or auxiliary check changed to
  accommodate a legitimate lever. Usable, but flagged until the adaptation's fairness is reviewed. The
  judgment is faithful (removed a real artifact) versus lenient (relaxed the bar).
- **QUESTIONABLE ASSUMPTION** — may well be correct, but hinges on a dubious or unverified premise: an
  assumed parameter value, an approximation or physical model, or a property of the data. State the
  assumption and how to test it. PROVISIONAL is about an adapted evaluation; QUESTIONABLE ASSUMPTION is
  about a shaky premise.
- **REFUTED** — failed: did not reproduce, lost to a trivial baseline, violated a bound, or a control broke
  it. Do not promote; log why; treat the refuting control as its own result.
- **INCONCLUSIVE** — a consistent-but-weak signal whose spread still overlaps the comparison. Gather more
  (replicates, data, a sharper test). Do not dismiss it as noise or claim the effect. Name the one control
  that would decide it.

A crash is a code bug to fix and re-run, not by itself a refutation of the idea.

---

## Depth scales with cost (re-solving is tiered, re-scoring never is)
The expensive step is the forward computation (the solve or the training run). The derivation chain — the
scorer and every derived number, recomputed from the stored raw artifact — is cheap regardless. So:
- **Always, at any cost tier:** recompute every derived number from the raw artifacts, because a
  transcribed value is never trusted; check that the config actually ran, log consistency, and
  prediction-vs-result.
- **Cheap to recompute** (seconds to minutes, seeded, re-runnable from its inputs; in a campaign, the
  result's `solve_wall_clock_s` and `configs/loop.json` `campaign.reproducible`): re-run it where the
  claim depends on the computation - a search's reach, a stochastic spread - with multiple seeds or
  perturbations and a statistical test; a cheap computation has no excuse for a single-seed conclusion.
  Deterministic code re-derives the same bytes: re-scoring the saved artifact in a fresh process is the
  check there, not re-running the solve.
- **Expensive / long**: do not force a full re-run, but never zero re-execution. Scrutinize the code (the change, its logic, its conventions) and
  the conclusions (do they follow from the logged numbers? are saved metrics internally consistent and
  recomputable from saved outputs?), re-check the saved artifacts, and run the cheapest discriminating
  spot-check: one config of the sweep, a coarse-mesh replica, or the selftest. That is the minimum
  re-execution that could catch the error class at issue.

Start from what changed. The delta is delivered in your spawn's VALUES — the `changes` summary (code,
compared as code; config keys; version tags) and the full snapshot diff, by value — so you read it there,
not from disk; `python scripts/run_campaign.py --diff <exp>` reprints it on demand. Verify that delta and
its interaction with the unchanged parts; what did not change since the last independent check inherits
that check's coverage and is spot-checked, not re-derived. A change with no declared effect on the result, or a
claimed effect with no change behind it, is a red flag in its own right.

Say in the verdict's summary what you re-ran and what you re-derived. Tiering applies to re-solving only;
it never licenses skipping the recomputation of derived numbers from raw artifacts. If a tiered
verification later proves to have missed an error in the part not re-run, say so in the verdict.

---

## Campaign mode — promoting a finding (the full adversarial apparatus)

When the claim is a candidate result in an autoresearch campaign, verification is the gate between "looks
like a win" and recording it as settled — a ledger `finding` cell, an independent label on the
current-best, a scoreboard verdict token. A finding is not settled until this returns CONFIRMED; the
current-best pointer carries its honest label meanwhile. In supervised loops this mode runs
on the driver's schedule, not the worker's judgment: when the preset owes a result an independent check,
the driver spawns a verification agent that invokes this skill per experiment (the entry is not cleared
until every verdict artifact exists, and the driver stamps the label from it). Attended sessions invoke
it directly.

**Step 0 — learn the campaign (parametrize the check).** Read the campaign's `CLAUDE.md` and follow its
**§Where things live** table to the campaign definition and each document below — it is that campaign's own
map, so route through it rather than assuming a path. *A campaign scaffolded before the table existed has
none; read `docs/charter*.md` (or `docs/program.md` in the oldest trees — lint-ok: a fallback must name
the retired spelling) directly.* Note: the FROZEN
primary metric and direction, and the FROZEN scorer path; the current metric epoch (`configs/loop.json`
`campaign.metric_version`, its `campaign.metric_epochs` entry if any, and its standing — a result is
judged within its epoch); the run command and the baseline (exp 000); the
guardrail, the diagnostics, and any ceilings; the levers and the FROZEN / READ-ONLY / MUTABLE lists, in
particular whether code is a lever, since forward-model campaigns mutate the code under test; and the
campaign-specific extra checks its *Independent verification* section already names (the
`{{VERIFY_EXTRA_CHECKS}}` slot — honor them). These fill the `<…>` slots below.

**Inputs.** Identify the candidate by experiment id / config path; resolve it to the config and the claimed
numbers from `results/scoreboard.tsv` and `results/result_<NN>.json`. Read only the claim: the config, the
scoreboard row, the result JSON. Do not pre-read the JOURNAL narrative; the verifier must form an
independent view.

**Spawn the independent refuter** (Agent tool, one call per candidate; verify several in parallel in one
message) with the prompt below, `<…>` filled from Step 0, starting from the delta in your VALUES (in an
attended session, the experiment's checks artifact `changes_independent`, or `--diff <exp>`). Run it on a
model at least as capable as the one that produced the result. A different capable model is preferable: it
adds mechanism diversity. Never use a weaker model, which yields false CONFIRMs.

**On return — write the verdict ARTIFACT, then record it append-only.** First write
`results/verdicts/<exp_id_or_slug>.json`, the machine-checkable artifact consumed by the promotion gate
(the current-best/scoreboard surface and the project-ledger surface) and by the loop driver. Copy this
stub and fill every `<…>`; all fields are REQUIRED. Do not hand-improvise a subset:
```json
{"claim": "<one line>", "exp_id": "<id>", "verdict": "CONFIRMED", "kind": "verifier",
 "kill_tier": null, "refuter": "<the spawned agent's id — never this session>",
 "confounded_levers": [], "disentangler": null, "resolves_confounded": [],
 "utc": "<current UTC stamp>", "summary": "<2-3 sentences>"}
```
`refuter` is the id of the independent agent you spawned above (§4). Capture it from that agent and paste
it here; it is never this session's id. The gate rejects a verdict with an empty or absent `refuter` on
BOTH promotion paths, so a refuterless CONFIRMED does not graduate and a dropped field blocks your own
promotion. Fill the stub literally rather than reconstructing the schema from memory. `kill_tier` is set
only for a negative or kill-claim, per *Verifying a kill-claim* below. `confounded_levers` and
`disentangler` are set whenever more than one lever moved, per *Confounded attribution* below. A ledger
`finding` cell must cite this file by name (the rule `campaign-status` audits), and a project-ledger
entry must cite it by path or the hook denies the write.

Then put the verdict on the experiment's `**Verification**:` line (in a supervised run the driver
stamps it from the verdict artifact; a line you write by hand is never overwritten). Log every concern the verifier raised,
including on a CONFIRMED, under `**Disputes & responses**:`, each with your response. Never delete a raised
issue; if you disagree, add a counter-argument. If the disagreement is load-bearing, escalate it per §4b
rather than settling it yourself, because your rebuttal of the checker inherits the reasoning the checker
was called to test. Do the same for any concern the user raises.

Then gate. CONFIRMED → may promote. PROVISIONAL / QUESTIONABLE ASSUMPTION → working result only: it must
not be written into a `finding` cell, and must not be reported as "current-best" or "best" without its caveat
carried inline, until the adaptation or assumption is reviewed. REFUTED → do not promote; the refuting
control is its own experiment. INCONCLUSIVE → the named control runs before anything is decided.
**In campaign mode, a REFUTED or INCONCLUSIVE verdict names that control or fix-and-rerun in the verdict
artifact's `follow_up` field** — one line, concrete, citing `results/verdicts/<id>.json`. You propose no
config and start no unit: the driver relays the field to the next worker as a note, and the worker
decides (there is no queue). No claim-splitting: a
headline number is inseparable from the config that produced it, so you may not promote "the number" while
grading its config's physics QUESTIONABLE, nor let a promoted config keep a fitted parameter outside its
physical range. This is about the config's validity, not about attribution among its levers. "Which lever
earned the win" is a separate claim, graded separately, and a shaky answer to it does not block the
empirical one (see *Confounded attribution*).

**A contest.** In a supervised loop the driver's verifier VALUES may carry a `CONTEST` line: the worker
disputed the gate outcome recorded for its own result and filed the objection as a charge, with the
artifacts it rests on. The claim under test is then the recorded outcome (the pass, or the refusal), and
the charge is the first attack to run against it, judged on the artifacts it names and the ledger — not on
the campaign's landmine rows or the worker's narrative, which are the frame the contest exists to test.
The gate reads the other way round from a finding: the outcome **stands** unless REFUTED. CONFIRMED, the
charge failed; REFUTED, the charge holds and the outcome is overturned; PROVISIONAL / QUESTIONABLE /
INCONCLUSIVE, the charge is not established and the outcome stands with that verdict as its label. Write
`"contest": true` in the artifact and name in `follow_up` the unit that would settle what the charge
raised; the driver promotes a contested pass that stands, and never the verifier.

**Clear the noise floor before promoting.** A delta only counts if it exceeds measurement jitter. Establish
the noise floor: repeat the evaluation across seeds or perturbations (or re-runs of a stochastic pipeline)
and take the spread (SD or MAD) of the primary metric. Require the improvement over the incumbent to be
several times that spread, not within it. Report the win as `Δ = <value> ± <spread> (n=<reps>)`. An
improvement inside the noise floor is INCONCLUSIVE, not a win, however good the single number looks. For an
expensive eval where many reps are not affordable, estimate the floor once on a representative case and
reuse it. This is the statistical backing for the spread column in the scoreboard. **Record the number where the machinery can read it** — `configs/loop.json` `campaign.noise_floor` — or it stays an estimate in someone's head and every later run reports its noise check `unavailable`. A **deterministic** campaign (`campaign.noise_model`) has no spread to estimate: set `campaign.tolerance` instead and skip this section.

### Confounded attribution (fires whenever more than one lever moved)

Always ask first: how many levers changed versus the comparison? A single-lever comparison needs no
further work here. When two or more moved, deliberately (coupled levers, a screen, an interaction test) or
by accident, record the entangled set and the experiment that would separate it:

```json
"confounded_levers": ["preproc_norm", "decoder_loss"],
"disentangler": "exp 042: decoder_loss alone vs current best"
```

An empty list asserts attribution is clean. A non-empty list requires `disentangler`: the cheapest ablation
that would isolate the suspected contributor. The field names a debt rather than discharging one, so
stamping it settles nothing and instead names the run that will. When you later run that disentangler,
name the levers it separated in the new verdict's `resolves_confounded`. That is what closes the debt and
releases the levers.

Confounding is a property of the design, orthogonal to the verdict, as `kill_tier` is. It grades the claims
separately:

- The empirical claim ("this config scores X") is unaffected: the number was measured, and a current-best
  is an empirical fact, not a causal one. It may be CONFIRMED and promoted with the set recorded. Holding
  the best configuration available without yet knowing why it wins is allowed.
- The causal claim ("lever L is why") cannot be CONFIRMED while the set is non-empty. It is
  QUESTIONABLE ASSUMPTION, with the confounded set as the named premise. Report the win without
  attributing it, or run the disentangler.
- A kill claim gets the strict treatment described below. This is the asymmetric case.

The apparatus above — refuter, verdict artifact, promotion gate — is aimed at positives. A multi-lever win
runs into all of it, while a multi-lever loss only updates the journal, so a confounded negative routes
around the machinery that would have caught it. The mechanism to hunt is masking: lever A helps, lever B
hurts more, the combination scores below baseline, and both get retired. A good direction dies silently,
and negatives are rarely re-litigated.

So a multi-lever negative refutes the combination, not its members.
- The combination as a unit may earn `EVIDENCE_AGAINST` if the implementation is verified sound.
- Every lever in `confounded_levers` is INCONCLUSIVE individually, because cause is not attributed. By the
  tier rules below that does not steer and never graduates. No lever in that set may be recorded as ruled
  out.
- Each such lever remains untried for planning and exhaustion purposes. A lever tried only inside a
  confounded unit has not been tried. `loop_heartbeat` refuses an `exhausted` stop while any lever sits in
  that state, so a single bad combined experiment cannot end a campaign.

### Verifying a kill-claim (steering-negatives and invalidations)
A negative finding that will steer the campaign — it kills a lever or topology branch, declares a ceiling
or plateau, shelves a direction, or invalidates prior results — is recorded as a `finding` cell on its
ledger row (through `--record <exp> --finding`, citing the verdict) and verified exactly like a win.
The failed-experiment population is more bug-contaminated than the winning one: most
implementation errors degrade performance, so bugs masquerade as "this approach doesn't work," and an
unexamined negative kills a branch permanently. A claimed invalidation ("the scoreboard is tainted", "the
metric is broken") gets this check before the campaign reprioritizes or forks on it; the false alarm is the
symmetric failure mode. **A verified kill of the metric itself is what opens a metric epoch**
(`roles/REFERENCE.md` §Metric epochs): a `semantics` revision needs a REFUTED or EVIDENCE_AGAINST tier
against the old metric, and an `easier` revision — one under which the current best would score better,
the goalpost-moving shape — needs REFUTED. The verdict artifact is what the epoch entry cites;
INCONCLUSIVE never opens one.

The refuter's checklist differs from the positive case. Hunt the false-negative sources:
- **Implementation error** — signs/units/ports/conventions; run the selftest and the correctness suite on
  the exact code that produced the negative. A crash, or an envelope breach (a result below the a-priori
  floor), is itself evidence of a bug rather than of a dead idea.
- **Strawman comparison** — did the killed alternative get materially less tuning budget than the
  incumbent? A fair kill requires comparable effort.
- **Insufficient search** — dead after 2 configs in a large design space is a sampling statement, not a
  death certificate.
- **Non-discriminating regime** — was the negative measured where the competing hypotheses predict the
  same outcome? A null where the effect must vanish under either is no evidence against it; re-test where
  they disagree.
- **Mechanism** — a promoted negative carries why it fails, not just that it scored low. Never name a cause
  of death from resemblance (`attribute-mechanism`).

**Grade the kill on three tiers** (recorded as `kill_tier` in the verdict artifact; the verdict field
itself still grades whether the *claim as stated* is CONFIRMED):
- **REFUTED** — mechanism understood; the idea cannot work (a reasoning- or proof-level kill, such as an
  exact symmetry cancellation). Prunes the branch.
- **EVIDENCE_AGAINST** — a clean negative experiment with the implementation verified sound, but a single
  instantiation cannot establish that no implementation works. Deprioritizes: the branch is shelved with
  its evidence and is revivable. Independent EVIDENCE_AGAINST entries may accumulate toward
  a prune, recorded with the entries cited.
- **INCONCLUSIVE** — cause not attributed; the implementation, not the idea, may be at fault. Does not
  steer and never graduates. Name a fix-and-rerun in the verdict's `follow_up` instead; the promotion
  hook denies an INCONCLUSIVE kill.

### Adversarial prompt to give the spawned agent
Fill every `<…>` from Step 0. Omit the bracketed CODE/FORWARD block if code is not a lever. Choose the
reproduce mode by run cost.

> You are an independent verifier for the campaign at `<campaign dir>`. Read its `CLAUDE.md` and follow the
> **§Where things live** table to the metric and the rules; if it has no such table, read `docs/charter*.md`
> directly. Assume the following result is wrong and try to refute it. Your default verdict is REFUTED
> unless the evidence forces CONFIRMED.
>
> Candidate: `<config path>`. Claimed: `<METRIC> = <value>` (`<direction>` = better; baseline exp 000 =
> `<baseline>`), guardrail `<GUARDRAIL> = <value>`, plus `<any ceilings / diagnostics claimed>`.
>
> Why this check matters: `<what the claim gates — promotion to current-best / a report figure / a
> go-no-go decision>`. Your verdict is that gate; the work will be published, so the result must be
> defensible. You are given the stakes, not the original reasoning; that is deliberate.
>
> Report what you actually observe, as numbers. Falsify with code, not prose: verify against known
> examples, test edge/degenerate/extreme inputs, randomize inputs, search for counterexamples. A crash is a
> code bug to fix and report, not a refutation of the idea. Surface load-bearing assumptions; if the result
> stands only under a dubious or unverified premise, that is a QUESTIONABLE ASSUMPTION.
> 1. **Reproduce.** Recompute `<METRIC>` from the saved artifacts with the FROZEN scorer `<scorer path>` in
>    a fresh process and confirm internal consistency; re-run `<RUN COMMAND> --config <config path>` (tee to
>    `results/diagnostics/verify_<exp_id>_<UTCstamp>.log 2>&1`) where the claim depends on the computation
>    itself - a search's reach, a stochastic spread. Either way recompute every reported number from a fresh
>    evaluation; convergence is not correctness. A number that doesn't match → REFUTED. Never background the
>    reproduction: if it cannot finish in the foreground, write INCONCLUSIVE with the reason rather than
>    no artifact. Say in the summary what you re-ran.
> 2. **Replicate — test, don't assume noise.** Re-run with perturbed params and, for stochastic steps,
>    different seeds; report spread; apply a paired statistical test. No consistent effect → noise (REFUTED);
>    consistent trend whose spread overlaps the comparison → INCONCLUSIVE (gather more); clear
>    test-significant effect → passes. Best-of-many-configs → higher bar (look-elsewhere), still resolved by
>    a test.
> 3. **Beat trivial baselines and prior bests.** Compare `<METRIC>` to the recorded baseline/prior best and
>    to trivial/degenerate solutions (all-zeros / constant / mean / trivial physical state). A trivial
>    solution beating the candidate → not a win. A non-physical trivial winner → flags a metric/units
>    problem; scrutinize scaling/normalization/definition.
> 4. **Metric integrity / no goalpost-moving.** Did this experiment change anything the metric/guardrail
>    consumes (`<metric inputs>`) in a way that flatters the number without improving true performance? Is
>    the comparison to exp 000 apples-to-apples? Null-control: feed the scorer a scrambled input and confirm
>    it collapses to the no-skill floor. Entanglement: does the scorer, the reference, or the comparison's
>    starting point share a fitted component with the candidate (a reference fitted under it, an inherited
>    nuisance parameter, a sweep scored from its own start)? Then it favours that candidate by construction:
>    re-score under something that shares nothing, or profile the shared component out. A change to the
>    FROZEN metric that is declared as a metric epoch is judged by its direction: a harder ruler (the
>    current best scores worse) is presumptively honest; an easier one is the goalpost-moving shape and
>    needs the strongest evidence.
> 5. **Ceiling vs gap, and the nature of the residuals.** Is the win a CEILING move (physical bound rose —
>    real) or a gap-to-ceiling move (a freer model closed the gap — suspect overfitting; must clear the
>    guardrail)? Examine the residuals for systematic structure vs random noise: structure means a bug or
>    unaccounted-for physics, not just error to report. Claim overfitting only from a specific signature,
>    never when the change raised raw fit error.
> 6. **Guardrail — confirm it can fail, not just that it passed.** A guardrail that would read the same
>    regardless of the lever under test is not exercising the code path it is meant to guard; it gives false
>    confidence, worse than no guardrail. Check: does `<GUARDRAIL>` depend on this experiment's
>    change (perturb the lever and confirm the guardrail value moves), or does it pass identically either way?
>    If it can't be shown to fail on a deliberately bad input, flag it as untested and do not credit the pass.
>    Only once that's established, confirm `<GUARDRAIL>` passes (not materially worse than baseline; overfit
>    flag False).
> 7. **Bounds & units.** Physically possible? Every fitted parameter inside its range; nothing above its
>    ceiling. Impossible → bug/leak → REFUTED until explained.
> 8. **Generalization.** Improvement holds across the whole evaluation (`<all conditions / held-out split>`),
>    not a lucky subset, no regression on anchors.
> 9. **Fairness of any adapted evaluation.** FAITHFUL (removed a real artifact → may be CONFIRMED, flag
>    PROVISIONAL) vs LENIENT (relaxed the bar → REFUTED). The data and known ground truth must not have been
>    touched — if they were, REFUTED outright. The FROZEN metric may have changed ONLY as a declared metric
>    epoch (a new `metric_version` with its `campaign.metric_epochs` entry and evidence): undeclared →
>    REFUTED outright; declared → judge the epoch by its direction and evidence, and never rank this result
>    against rows from the previous epoch.
> [CODE / FORWARD-MUTATING ONLY:
> 10. **Code soundness.** Sign/convention slip (check this first — see `../../PROJECT.md` §Standing constraints), units
>    error, geometry mismatch. `--selftest` still passes; no stale cache reused after a core change; no
>    silently-added free parameters (must be no freer). Upstream preprocessing: the load-bearing transform
>    feeding the metric (registration / pose / normalization) is non-degenerate on the data it is applied
>    to — a degenerate step can pass the score while silently mis-handling specific inputs.
> 11. **Multi-condition agreement.** Win holds at every evaluated condition, not one. A one-condition win is
>    an artifact. ]
>
> Return a structured verdict: `verdict`; `questionable_assumption`; `verification_mode`; `adapted_eval`;
> `reproduced_metric` (+ spread); `beats_trivial` (note if a non-physical trivial wins); `ceiling_or_gap`;
> `residual_structure` (structured→lead/bug | random); `guardrail`; `contamination_check`; `code_check`;
> `failure_modes_found`; `additional_control_needed` (if INCONCLUSIVE); `summary` (2–3 sentences).

---

## Notes & composition
- **Verification only.** Never promotes, never edits a FROZEN metric or physics, never edits data. It
  re-runs, re-derives, and reports. It never opens a metric epoch either; it adjudicates the kill-claim
  that would justify one.
- **Composes:** `dimensional-analysis` (the units/bounds first check), `frame-problem` (the a-priori range
  and the physics inventory a structured residual points back to), `correctness-suite` (which turns a
  check produced here into a standing regression gate), `record-decision` (the reason for a non-obvious
  check). `report`'s report-time verification step composes this skill.
- The campaign definition (via `CLAUDE.md` §Where things live) names this skill in its *Independent
  verification* section — honor the extra checks it lists.

## Before you call it verified — checklist
- [ ] Checked the claim independently, without anchoring on the author's reasoning.
- [ ] New/derived equation → dimensional check + a limiting case, first.
- [ ] Every reported number recomputed from a fresh run (not transcribed).
- [ ] Fit/prediction → residuals examined for structure vs random noise; the statistic checked against the question it is meant to answer (mean-vs-max, paired-vs-unpaired, a central statistic where the hypothesis is "rare and large", a fitter fed the wrong residual).
- [ ] Any comparison between candidates → scorer, reference, and starting point checked for entanglement with the things being compared (a reference fitted under one candidate favours it by construction).
- [ ] Any "these agree/disagree" claim tested via the combined-uncertainty tension (*t = |a−b|/√(σ_a²+σ_b²)*), not eyeballed; error bars on both sides; a real tension resolved, not averaged.
- [ ] Falsified with code (known examples, edge cases, counterexamples); beats trivial baselines.
- [ ] Result within physical bounds and its a-priori range; every fitted parameter inside its physical range (a physically-shaped free-amplitude lever not credited as a physical prediction; a known input that hurts treated as an anomaly, not overridden with a fudge factor).
- [ ] Every reported number labelled with its metric path; a cross-frame result passed the frame-consistency check (`docs/reference/coordinate-frames.md`).
- [ ] QUESTIONABLE/PROVISIONAL not promoted or reported as "best" without its caveat inline; no claim-splitting (the number is inseparable from its config).
- [ ] Load-bearing facts resolved to the highest-authority source (not a derived statistic); any INFERRED/RECALLED fact falsification-tested before it's relied on.
- [ ] Any irreversible action was gated on a CONFIRMED diagnosis (highest-authority artifact read), not a derived statistic.
- [ ] Substantial claim → an independent / mechanism-diverse route (often a fresh agent) agreed.
- [ ] Any disputed verdict escalated to a blinded third party required to run a check neither side ran (§4b), not settled by argument between the claimant and the refuter.
- [ ] Campaign mode: the correctness suite (`tests/correctness_checks.py`) is green, or explicitly N/A — a red suite blocks promotion.
- [ ] Campaign mode: the verdict artifact `results/verdicts/<id>.json` written (with a named refuter) — the promotion hook and the loop driver consume it, and the finding cell must cite it.
- [ ] A kill-claim got the negative-refuter checklist (implementation error / strawman / insufficient search / mechanism) and a `kill_tier` — INCONCLUSIVE kills name a fix-and-rerun in `follow_up`, never graduate.
- [ ] A kill-claim against the METRIC itself carries the tier a metric epoch needs (REFUTED or EVIDENCE_AGAINST; REFUTED for an easier ruler), and its verdict artifact is what the epoch entry will cite.
- [ ] Counted the levers that moved. More than one → `confounded_levers` + a `disentangler` recorded; the causal claim graded QUESTIONABLE ASSUMPTION (the empirical one may still promote); a negative kills only the combination — every member INCONCLUSIVE, still untried, checked for masking (one lever helping while another hurts more).
- [ ] Re-ran what the claim depends on, per the cost tier; an expensive unit still got the cheapest discriminating spot-check — never zero re-execution.
- [ ] Verdict graded; load-bearing assumption named; disputes recorded append-only (campaign mode).
