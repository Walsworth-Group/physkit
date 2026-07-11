---
name: verify
description: >-
  Independently and adversarially check whether a result, number, equation, derivation, fit, or claim is
  actually right — for any task, not only research campaigns. The stance is "assume you are wrong until
  independently proven right": recompute every reported number from a fresh run, falsify with code rather
  than prose, and prefer a mechanism-diverse independent check over an argument. Use before you rely on or
  report a result, when a number beats its expected range or "looks too good", before promoting a campaign
  finding to current-best or writing a DISCOVERY, or whenever someone asks "is this right / double-check
  this". For a new or derived equation it runs a dimensional sanity-check first (dimensional-analysis);
  for a fit or prediction it interrogates the NATURE of the residuals (systematic structure vs random
  noise), not just their size. Returns CONFIRMED / PROVISIONAL / QUESTIONABLE ASSUMPTION / REFUTED /
  INCONCLUSIVE with evidence. Not for checking citations (cite-check) or building a standing check suite
  (correctness-suite).
---

# verify — assume you are wrong until independently proven right

The burden of proof is on the positive result. This skill operationalizes the core verification stance:
a result is not real until an *independent* check has tried to refute it and failed. **Convergence is not
correctness; a clean-looking number is not a verified one.** Warrant rides on the checker, not on the
generator's reasoning — so verify by a mechanism-diverse independent route, recompute every reported
number from a fresh run, and **falsify with code, not prose** (edge cases, randomized inputs,
counterexamples).

It works at two scales. **General mode** checks a standalone claim in any session. **Campaign mode**
(further down) is the full adversarial apparatus for promoting a campaign finding — it learns the metric,
scorer, and rules from the campaign's own charter and spawns an independent refuter. Use the depth the
stakes deserve.

---

## General mode — check any result or claim

### 1 · Gather the claim, not the conclusion
Get the thing asserted and the inputs needed to reproduce it — **without** anchoring on the author's
narrative of why it's right. Form an independent view; the reasoning you're checking is exactly what might
be wrong. Note the **a-priori range** the answer should fall in (from `frame-problem`, or compute one now
with `dimensional-analysis`): a result outside its predicted envelope is a bug or a discovery, and you
decide which here.

### 2 · Route by claim type to the decisive check
Different claims fail in different ways. Lead with the check that would actually catch the failure:

- **A new or derived equation / quantity → dimensional sanity-check *first*.** The cheapest check there is:
  do the units even work? Invoke `dimensional-analysis`. Then test a **limiting case** (a known special
  case, a small/large-parameter limit, a symmetry the result must respect). An equation that fails units
  or a known limit is wrong — stop before anything more expensive.
- **A computed number / result → recompute it from a fresh run.** Re-run the producing computation and
  confirm the value matches — **every reported number, not just the headline**. A number that doesn't
  reproduce, or that was only ever stated once and never recomputed, is REFUTED. Convergence ≠ correctness:
  re-derive the value, don't trust that the solver converged. A number the *model* produced (mental
  arithmetic, an "estimated" or remembered value) rather than code is REFUTED on sight — there is nothing to
  reproduce; regenerate it from code first. (A pre-run a-priori estimate is exempt — it exists to be checked
  against the code, not reported as the result.) **Label which metric path each number is** (a
  relaxed/auxiliary score vs the frozen primary metric); an unlabelled number can't be compared
  apples-to-apples or drive a promotion.
- **A fit or a prediction → interrogate the *nature* of the error (see below), not just its magnitude**,
  in addition to recomputing it.
- **A claim that two quantities agree (or disagree) → test it in units of the combined uncertainty, don't
  eyeball it.** For *a ± σ_a* and *b ± σ_b* (independent errors), the tension is
  *t = |a − b| / √(σ_a² + σ_b²)*: *t ≲ 1* agree, *t ≈ 2* mild tension, *t ≳ 3* a real discrepancy — a
  physical difference or an underestimated error bar, never "close enough." **141 ± 0.003 is not in
  agreement with 142** (*t ≈ 330*), yet two values agreeing only because both bars are huge is a weak
  agreement, not a confirmation. No error bar on either side → not comparable; get one first. Correlated
  errors → subtract the covariance (√(σ_a² + σ_b² − 2σ_ab)). Resolve a real tension, never average it
  (universalism; distinct from §4's noise-floor test of one delta against its own spread).
- **A claim / comparison → falsify it with code.** Write controls: verify against known examples (inputs
  whose answer you can derive or look up), test edge/degenerate/extreme inputs, randomize inputs, search
  for counterexamples. Beat the **trivial baselines** (all-zeros / constant / mean / a trivial physical
  state) and any prior known result — a result worse than a trivial answer is no win. *(Nuance: if a
  **non-physical** trivial answer scores better than a plausible result, that flags a metric/units problem,
  not a target to beat.)*
- **A "we're done / at the ceiling / blocked / optimal" conclusion → treat it as a load-bearing positive
  claim and try to REFUTE it.** A stopping decision is high-stakes — it ends the work — so it earns the same
  adversarial scrutiny as a win: require an explicit attempt to beat the supposed limit (an orthogonal lever,
  a freer model, a cheap what-if) and a reasoned argument for why any gain found is non-physical, before the
  "done" stands. "I've stopped finding gains" is not "no gains exist"; an unfalsified ceiling is INCONCLUSIVE,
  not CONFIRMED.

### 3 · Interrogate the nature of the error (fits & predictions)
For any fit, regression, calibrated model, or learned predictor, **don't stop at the error magnitude —
examine the residuals for structure.**
- **Structured residuals** — a trend, a dependence on an input variable, a spatial/temporal pattern,
  autocorrelation, a systematic over/under-shoot in one regime — signal a **bug or unaccounted-for physics
  (model-form error)**. They point back to a parked or missing effect in the physics inventory
  (`frame-problem`), and they are **one of the best sources of genuine discovery** — investigate them.
- **Random, zero-mean residuals consistent with the noise model** are what "done" looks like.
- Plot residuals against each input and against the fitted value; check for autocorrelation. "The error is
  small" is not the same as "the error is unstructured." Don't write structure off as noise without proof.
- Be precise about overfitting: claim it only from a *specific signature* (a gain that doesn't hold on
  held-out data; a fit better than the known truth), **never** as a catch-all, and **never** when the
  change *raised* raw fit error (that cannot be overfitting). Separate statistical from systematic error.
- **A per-step/sequential fit's clean residuals can be manufactured, not earned.** When consecutive fits
  (frame-by-frame, step-by-step) share a drifting nuisance parameter, each step can silently co-adapt to
  absorb real signal — residuals look random precisely because the model quietly moved to hide the
  structure, not because it's right (`simulation-design` §3). Before trusting clean per-step residuals as
  "done," check whether a joint or monotonicity-constrained refit across steps reproduces them — if the
  constrained fit's residuals show structure the per-step fit's didn't, the per-step version was absorbing
  error, not explaining it.

### 4 · Prefer an independent, mechanism-diverse check
The strongest verification comes from a *different route* reaching the same answer: a second method, an
independent re-derivation, a certifying solver, an analytic cross-check. For any substantial or
load-bearing claim, **spawn a fresh agent** (Agent tool, `subagent_type: general-purpose`) and give it the
adversarial prompt below, so it re-derives from scratch in its own context rather than inheriting your
assumptions. **Pass the why, never the reasoning:** tell the spawned agent what this claim *gates* (a
promotion, a report, a decision) and the stakes — an agent that knows why the check matters verifies
harder than one handed a bare task — but never share your generating reasoning or expected answer, which
would contaminate its independence. Replicate across seeds/perturbations for anything stochastic, and use
a **statistical test** for close calls — a difference smaller than the spread is not automatically noise
(real effects can be weak), but it's not automatically real either.

### 5 · Bounds & physicality
Confirm the result is physically possible: within hard bounds (probabilities in [0,1], known ranges), **no
fitted parameter outside its physical range** (wrong sign, out of bounds), nothing above its own ceiling.
Anything impossible means a bug or a leak — **REFUTED until explained, and never carried into a reported
"best" config while it stands.** Three traps specific to physically-motivated fits:
- **A physically-*shaped* template with a *fitted* amplitude/sign is not a physical prediction.** If the
  first-principles value (the physical amplitude, scale = +1, …) is *not* what the fit chose — worse, if it
  *hurts* the metric — the lever is an empirical corrector in physical clothing: grade it QUESTIONABLE
  ASSUMPTION, don't credit it as first-principles.
- **A known physical input that *hurts* the fit is an anomaly to explain, not to override with a fitted fudge
  factor.** And **cross-fit agreement on the *same unphysical value* is not validation** — two fits agreeing
  on the same wrong number are both wrong.
- **Frame consistency (geometry-heavy claims).** For any result that crosses coordinate frames, run the
  frame-consistency check in [`docs/reference/coordinate-frames.md`](../../docs/reference/coordinate-frames.md):
  every quantity's frame declared, no symbol overloaded across frames, orientation/handedness resolved from an
  independent reference (not the fit). Correct code with undeclared frames is still unverifiable.

### 5b · Provenance, authority, and irreversible actions
A result is only as trustworthy as the facts it rests on and the source those facts came from.
- **When sources conflict, resolve a load-bearing fact to the highest-authority artifact** — parse the saved
  model, probe the released data, run the shipped weights — not a lower-authority proxy (paper text, leftover
  code) and *not a statistic you derived from the data* (a correlation you computed is weaker than the source
  it came from). The authority ladder and the PINNED/REPORTED/INFERRED/RECALLED/REASONED tags are in
  `docs/PRINCIPLES.md` Ctx 4.
- **A fact acted on at INFERRED/RECALLED is itself a claim to verify.** Try to *falsify* it before it becomes
  load-bearing — especially when a cheaper discriminator is already in hand. (A campaign that pins an
  inferred quantity and builds on it, skipping an available refuting check, is the classic expensive error.)
- **Before any irreversible action** (overwrite/delete/regenerate inputs, a hardware move), require the
  justifying diagnosis to reach **CONFIRMED via the highest-authority artifact** — read the actual pipeline
  source, don't act on a derived statistic. Gating a destructive step to the user on a below-CONFIRMED
  diagnosis makes the human your only backstop; confirm first.

### 5c · Reflect against your own confirmation bias (before you grade)
The hardest error to catch is the one you are motivated not to see: once you have decided an answer is right,
the pull is to suppress alternatives and read every new datum as confirmation. This is the chief threat to the
reflective decisions, and generating failure modes is a *learnable* skill experts have and novices lack — so
run the ritual explicitly, don't just intend to be objective:
- **State the result you expected or hoped for** — name it, so the bias is visible.
- **Make the strongest case that it is WRONG** — argue the other side as hard as you argued yours; list the
  concrete ways it could fail.
- **Name the single observation or control that would refute it** — then check whether you actually ran it.
  If not, run it before concluding.
- **Consider the alternative conclusion you are resisting**, especially an unwelcome one (the effect is noise;
  a rival model fits too; the "win" is an artifact) — and give it a fair hearing.
This is *your own* reflection; it complements — does not replace — the independent refuter (§4), whose value
is precisely that it never shared your hope.

### 6 · Grade the verdict and surface the premise
Return one of the five verdicts (defined below), state what is **certified vs conjectured** and over what
range, and **name any load-bearing assumption** the result hinges on. Record the *why* of a non-obvious
check (`record-decision`) so it isn't lost.

---

## The verdicts

- **CONFIRMED** — survived an independent attempt to refute it; reproduced, bounded, and unstructured where
  it should be. May proceed.
- **PROVISIONAL** — stands, but rests on an *adapted evaluation* (a guardrail/auxiliary check changed to
  accommodate a legitimate lever). Usable, but flagged until the adaptation's fairness is reviewed. Faithful
  (removed a real artifact) vs lenient (relaxed the bar) is the judgment.
- **QUESTIONABLE ASSUMPTION** — may well be correct, but **hinges on a dubious or unverified premise**: an
  assumed parameter value, an approximation/physical model, or a property of the data. State the assumption
  and how to test it. (PROVISIONAL is about an adapted *evaluation*; QUESTIONABLE ASSUMPTION is about a shaky
  *premise*.)
- **REFUTED** — failed: didn't reproduce, lost to a trivial baseline, violated a bound, or a control broke
  it. Don't promote; log why; treat the refuting control as its own result.
- **INCONCLUSIVE** — a consistent-but-weak signal whose spread still overlaps the comparison. **Gather more**
  (replicates, data, a sharper test) — do not dismiss as noise *or* claim the effect. Name the one control
  that would decide it.

A crash is a code bug to fix and re-run, not by itself a refutation of the idea.

---

## Depth scales with cost
- **Cheap to recompute (seconds–minutes):** full reproduction PLUS extra rigor — multiple seeds/perturbations
  and a statistical test. A cheap computation has no excuse for a single-seed conclusion.
- **Expensive / long:** don't force a full re-run, but **don't skip verification.** Scrutinize the *code*
  (the change, its logic, conventions), the *conclusions* (do they follow from the logged numbers? are saved
  metrics internally consistent and recomputable from saved outputs?), and re-check the *saved artifacts*,
  re-running only the cheapest decisive control. State which mode you used in the verdict.

---

## Campaign mode — promoting a finding (the full adversarial apparatus)

When the claim is a candidate result in an autoresearch campaign, verification is the **gate** between
"looks like a win" and writing it into `results/DISCOVERIES.md`. A promotion is not real until this returns
CONFIRMED.

**Step 0 — learn the campaign (parametrize the check).** Read `docs/charter.md` (or `charter_<NAME>.md`)
and note: the **FROZEN primary metric** + direction and the **FROZEN scorer** path; the **run command** and
**baseline (exp 000)**; the **guardrail**, diagnostics, and any **ceilings**; the **levers** and the
**FROZEN / READ-ONLY / MUTABLE** lists (in particular, *is code a lever?* — forward-model campaigns mutate
the code under test); and the campaign-specific extra checks the charter's *Independent verification*
section already names (the `{{VERIFY_EXTRA_CHECKS}}` slot — honor them). These fill the `<…>` slots below.

**Inputs.** Identify the candidate by experiment id / config path; resolve it to the config + claimed
numbers from `results/scoreboard.tsv` and `results/result_<NN>.json`. **Read only the claim** — config,
scoreboard row, result JSON. **Do not pre-read the JOURNAL narrative**; the verifier must form an
independent view.

**Spawn the independent refuter** (Agent tool, one call per candidate; verify several in parallel in one
message) with the prompt below, `<…>` filled from Step 0, reproduce-mode chosen by run cost. Run it on a
model **at least as capable** as the one that produced the result — a *different* capable model is ideal
(it adds mechanism diversity); **never a weaker model**, which yields false CONFIRMs.

**On return — record verdict AND every issue raised, append-only.** Put the verdict on the experiment's
`**Verification**:` line; log every concern the verifier raised — *even on CONFIRMED* — under
`**Disputes & responses**:`, each with your response. **Never delete a raised issue; if you disagree, add a
counter-argument.** Do the same for any concern the **user** raises. Then gate: CONFIRMED → may promote;
PROVISIONAL / QUESTIONABLE ASSUMPTION → **working result only** — must NOT graduate to DISCOVERIES, **nor be
reported as "current-best" / "best" without its caveat carried inline**, until the adaptation/assumption is
reviewed; REFUTED → don't promote, add the refuting control as its own experiment; INCONCLUSIVE → run the
named control before deciding. **No claim-splitting:** a headline number is inseparable from the config that
produced it — you may not promote "the number" while grading its config's physics QUESTIONABLE, nor let a
promoted config keep a fitted parameter outside its physical range.

**Clear the noise floor before promoting.** A delta only counts if it exceeds measurement jitter.
Establish the **noise floor** — repeat the evaluation across seeds/perturbations (or re-runs of a
stochastic pipeline) and take the spread (SD or MAD) of the primary metric — and require the improvement
over the incumbent to be **several times that spread**, not within it. Report the win as
`Δ = <value> ± <spread> (n=<reps>)`; an improvement *inside* the noise floor is **INCONCLUSIVE**, not a
win, however good the single number looks. For an expensive eval where many reps aren't affordable,
estimate the floor once on a representative case and reuse it. (This is the statistical backing for the
spread column in the scoreboard.)

### Adversarial prompt to give the spawned agent
Fill every `<…>` from Step 0. Omit the bracketed CODE/FORWARD block if code is not a lever. Choose the
reproduce mode by run cost.

> You are an independent verifier for the campaign at `<campaign dir>`. Read its `docs/charter.md` for the
> metric and rules. **Assume the following result is WRONG and try to refute it.** Your default verdict is
> REFUTED unless the evidence forces CONFIRMED.
>
> Candidate: `<config path>`. Claimed: `<METRIC> = <value>` (`<direction>` = better; baseline exp 000 =
> `<baseline>`), guardrail `<GUARDRAIL> = <value>`, plus `<any ceilings / diagnostics claimed>`.
>
> **Why this check matters:** `<what the claim gates — promotion to current-best / a report figure / a
> go-no-go decision>`. Your verdict is that gate; the work will be published, so the result must be
> defensible. *(You are told the stakes, not the original reasoning — that is deliberate.)*
>
> Report what you actually observe (numbers, not vibes). **Falsify with code, not prose** — verify against
> known examples, test edge/degenerate/extreme inputs, randomize inputs, search for counterexamples. A
> crash is a code bug to fix/report, not a refutation of the idea. Surface load-bearing assumptions — if the
> result stands only under a dubious/unverified premise, that's a QUESTIONABLE ASSUMPTION.
> 1. **Reproduce (mode by run cost).** FAST: re-run `<RUN COMMAND> --config <config path>` (tee to
>    `results/diagnostics/verify_<exp_id>_<UTCstamp>.log 2>&1`), recompute `<METRIC>` from scratch with the
>    FROZEN scorer `<scorer path>`; doesn't reproduce → REFUTED. LONG/EXPENSIVE: recompute `<METRIC>` from
>    the **saved artifacts** and confirm internal consistency, lean on the code + conclusions checks.
>    Either way recompute **every reported number** from a fresh evaluation; *convergence is not
>    correctness*. A number that doesn't match → REFUTED.
> 2. **Replicate — test, don't assume noise.** Re-run with perturbed params and, for stochastic steps,
>    different seeds; report spread; apply a paired statistical test. No consistent effect → noise (REFUTED);
>    consistent trend whose spread overlaps the comparison → INCONCLUSIVE (gather more); clear test-significant
>    effect → passes. Best-of-many-configs → higher bar (look-elsewhere), still resolved by a test.
> 3. **Beat trivial baselines and prior bests.** Compare `<METRIC>` to the recorded baseline/prior best and
>    to trivial/degenerate solutions (all-zeros / constant / mean / trivial physical state). A trivial
>    solution beating the candidate → not a win. A *non-physical* trivial winner → flags a metric/units
>    problem; scrutinize scaling/normalization/definition.
> 4. **Metric integrity / no goalpost-moving.** Did this experiment change anything the metric/guardrail
>    *consumes* (`<metric inputs>`) in a way that flatters the number without improving true performance? Is
>    the comparison to exp 000 apples-to-apples? Null-control: feed the scorer a scrambled input and confirm
>    it collapses to the no-skill floor.
> 5. **Ceiling vs gap, and the nature of the residuals.** Is the win a CEILING move (physical bound rose —
>    real) or a gap-to-ceiling move (a freer model closed the gap — suspect overfitting; must clear the
>    guardrail)? Examine the residuals for **systematic structure vs random noise** — structure means a bug
>    or unaccounted-for physics, not just error to report. Claim overfitting only from a specific signature,
>    never when the change *raised* raw fit error.
> 6. **Guardrail — confirm it can fail, not just that it passed.** A guardrail that would read the *same*
>    regardless of the lever under test is not exercising the code path it's meant to guard — it gives false
>    confidence, worse than no guardrail. Check: does `<GUARDRAIL>` actually depend on this experiment's
>    change (perturb the lever and confirm the guardrail value moves), or does it pass identically either way?
>    If it can't be shown to fail on a deliberately bad input, flag it as untested, don't credit the pass.
>    Only once that's established, confirm `<GUARDRAIL>` passes (not materially worse than baseline; overfit
>    flag False).
> 7. **Bounds & units.** Physically possible? Every fitted parameter inside its range; nothing above its
>    ceiling. Impossible → bug/leak → REFUTED until explained.
> 8. **Generalization.** Improvement holds across the whole evaluation (`<all conditions / held-out split>`),
>    not a lucky subset, no regression on anchors.
> 9. **Fairness of any adapted evaluation.** FAITHFUL (removed a real artifact → may be CONFIRMED, flag
>    PROVISIONAL) vs LENIENT (relaxed the bar → REFUTED). The FROZEN metric, data, and known ground truth must
>    NOT have been touched — if they were, REFUTED outright.
> [CODE / FORWARD-MUTATING ONLY:
> 10. **Code soundness.** Sign/convention slip (the #1 forward bug — see `docs/CONVENTIONS.md`), units error,
>    geometry mismatch. `--selftest` still passes; no stale cache reused after a core change; no silently-added
>    free parameters (must be no freer). **Upstream preprocessing:** the load-bearing transform feeding the
>    metric (registration / pose / normalization) is non-degenerate on the data it's applied to — a degenerate
>    step can pass the score while silently mis-handling specific inputs.
> 11. **Multi-condition agreement.** Win holds at EVERY evaluated condition, not one. A one-condition win is an
>    artifact. ]
>
> Return a structured verdict: `verdict`; `questionable_assumption`; `verification_mode`; `adapted_eval`;
> `reproduced_metric` (+ spread); `beats_trivial` (note if a non-physical trivial wins); `ceiling_or_gap`;
> `residual_structure` (structured→lead/bug | random); `guardrail`; `contamination_check`; `code_check`;
> `failure_modes_found`; `additional_control_needed` (if INCONCLUSIVE); `summary` (2–3 sentences).

---

## Notes & composition
- **Verification only.** Never promotes, never edits a FROZEN metric/physics, never edits data. It
  re-runs, re-derives, and reports.
- **Composes:** `dimensional-analysis` (the units/bounds first check), `frame-problem` (the a-priori range
  and the physics inventory a structured residual points back to), `correctness-suite` (which turns a
  hard-won check here into a standing regression gate), `record-decision` (the *why* of a non-obvious
  check). `report`'s report-time verification step composes this skill.
- The campaign `charter.md` names this skill in its *Independent verification* section — honor the extra
  checks it lists.

## Before you call it verified — checklist
- [ ] Checked the claim independently, without anchoring on the author's reasoning.
- [ ] New/derived equation → dimensional check + a limiting case, first.
- [ ] Every reported number recomputed from a fresh run (not transcribed).
- [ ] Fit/prediction → residuals examined for structure vs random noise.
- [ ] Any "these agree/disagree" claim tested via the combined-uncertainty tension (*t = |a−b|/√(σ_a²+σ_b²)*), not eyeballed; error bars on both sides; a real tension resolved, not averaged.
- [ ] Falsified with code (known examples, edge cases, counterexamples); beats trivial baselines.
- [ ] Result within physical bounds and its a-priori range; **every fitted parameter inside its physical range** (a physically-shaped free-amplitude lever not credited as a physical prediction; a known input that *hurts* treated as an anomaly, not overridden with a fudge factor).
- [ ] Every reported number **labelled with its metric path**; a cross-frame result passed the **frame-consistency check** (`docs/reference/coordinate-frames.md`).
- [ ] QUESTIONABLE/PROVISIONAL **not promoted or reported as "best" without its caveat inline**; no claim-splitting (the number is inseparable from its config).
- [ ] Load-bearing facts resolved to the highest-authority source (not a derived statistic); any INFERRED/RECALLED fact falsification-tested before it's relied on.
- [ ] Any irreversible action was gated on a CONFIRMED diagnosis (highest-authority artifact read), not a derived statistic.
- [ ] Substantial claim → an independent / mechanism-diverse route (often a fresh agent) agreed.
- [ ] Campaign mode: the correctness suite (`tests/correctness_checks.py`) is green, or explicitly N/A — a red suite blocks promotion.
- [ ] Verdict graded; load-bearing assumption named; disputes recorded append-only (campaign mode).
