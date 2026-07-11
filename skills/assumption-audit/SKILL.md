---
name: assumption-audit
description: >-
  Convert a stalled optimizer into a diagnostician. Reach for it when an optimization — a campaign or any
  sustained tuning effort — has plateaued in a way that lever escalation does not fix: one-lever
  experiments across two or more lever families pinned at the same floor, or the current best sitting far
  from its own a-priori expectation. The discipline: stop
  tuning and audit what every experiment INHERITS — enumerate the calibrations, derived quantities, and
  classifications the current best carries, rank them by would-being-wrong-reproduce-this-stall crossed
  with provenance weakness, and spend ONE discriminating experiment that SOLVES for the top suspect's
  value from scratch (never one that merely confirms the incumbent). Distinct from pivoting (choosing the
  next lever), debug (broken code), and verify (checking a result): this hunts a wrong inherited value
  that sits upstream of every lever. A plateau caused by a bad assumption cannot be escaped by any lever
  downstream of it — only by re-opening the assumption.
---

# assumption-audit — when optimization stalls, audit what it inherits

A plateau has two species, and the standard response fixes only one of them. If the levers are genuinely
exhausted, escalate/pivot (`docs/reference/pivoting.md`). But if the stall is caused by a **wrong
inherited value** — a miscalibration, a mis-derived quantity, a misread classification that every
experiment silently carries — then every lever is downstream of the error, and escalation just spends
budget re-measuring the same wall. The rule this skill enforces: **a hard plateau is evidence about your
assumptions, not just your levers; before committing more optimization experiments, audit what the
current best inherits, and buy one experiment that re-measures the top suspect from scratch.**

A real, dated failure motivates the discipline: an autonomous hardware-commissioning loop miscounted the
lines of a resolved spectral pattern — reading it from memory of the canonical case rather than from the
data — anchored a frequency calibration off the true line center, and inherited from it a derived
detection frequency a few kHz off. Every downstream experiment carried that value. The real signal appeared in the
data and was even confirmed by the loop's own control experiments — yet dozens of one-lever optimization
arms stayed pinned at the same signal-to-noise floor, because each one searched at the inherited (wrong)
frequency. The loop then designed exactly the right discriminating measurement — and framed it as a
*confirmation* of the inherited value rather than a fresh estimate, read the mismatch as an artifact, and
went back to tuning. No lever it owned could have fixed a number it never re-opened.

## When to run it

Trigger on any of these, whichever comes first:

- **Cross-family floor:** one-lever experiments across ≥2 independent lever families land at the same
  performance floor — "same" meaning indistinguishable within the metric's replicate spread, the noise
  floor `verify`'s campaign mode establishes (the signature that the binding constraint is *shared* by
  all of them — i.e. upstream).
- **A-priori gap:** the observed performance sits orders of magnitude from its own a-priori/CRB-style
  expectation and no lever moves the gap.
- **Unresponsive effect:** a "found" effect whose strength shows no response beyond that replicate
  spread across the swept range of the levers that should modulate it.
- **Scheduled:** `campaign-status` detects a plateau and lever coverage is already broad.

Do NOT reach for it when a single lever family is merely unfinished (keep mining), when the run crashed
(`debug`), or when the question is which lever to try next (`pivoting.md`). This skill asks a different
question: *what does every experiment believe that nobody has re-measured?*

## The method

1. **Enumerate the inheritance.** List every value the current-best configuration carries that was not
   measured in the current campaign phase: calibrations, derived quantities (anything computed *from* a
   measurement plus an assumption), adopted constants, and — easy to miss — **classifications** (a peak
   identification, a mode assignment, a pattern read). A classification is an assumption exactly like a
   number; the wrongest one on record was a feature-count read from memory of the canonical case rather
   than from the data (count what is actually there before naming what it is). Tag each entry with its
   provenance (the source-authority ladder: PINNED / REPORTED / INFERRED / RECALLED / REASONED — see
   `record-decision`). PINNED entries are near-immune; INFERRED and REASONED are prime suspects.
2. **Interrogate each against the stall signature.** For each entry ask: *if this were wrong, would the
   observed stall follow?* Demand a mechanism sketch, not a vibe — "carrier wrong by a few kHz ⇒ real
   line present but outside the estimator window ⇒ per-experiment SNR pinned at noise floor while
   detection controls still pass" is an answer; "maybe the calibration drifted" is not. Rank the entries
   by explanatory power × provenance weakness × cheapness of the discriminating test.
3. **Buy ONE discriminating experiment for the top suspect — with two hard clauses.**
   - **Solve, don't confirm.** The experiment must *estimate the suspect value from scratch* and only
     afterwards compare with the incumbent. A consistency check framed as "verify the current value"
     invites reading any mismatch as an artifact (that is precisely how the motivating loop ran the right
     experiment and kept the wrong number). Design the analysis so its output is a value, not a verdict
     on the incumbent.
   - **Operating-point validity.** Enumerate everything else that changes between this experiment and the
     ones it will be compared against, and re-derive any calibration that is only valid at the operating
     point where it was taken (a pulse calibration at a new frequency or amplitude, a gain at a new
     range, a response at a new temperature). A discriminating test run with an out-of-point calibration
     can cleanly refute a *true* hypothesis — pre-registered falsification plus an unmodeled confound is
     discipline amplifying error, the most expensive failure this skill knows about.
4. **Close the loop on the verdict.**
   - Suspect **cleared**: record it (`record-decision`, with the discriminating evidence and a
     *revisit-if* trigger) so the audit never re-litigates it, and move to the next suspect or back to
     optimization.
   - Suspect **falls**: the revised value is an invalidation event, not a tweak — re-baseline anything
     that inherited it, mark affected findings for re-verification, and if standing results are
     invalidated wholesale, that is `fork-campaign` territory. Then return to optimization mode: the
     audit is a mode change, not a new home.

## Rules of evidence

- **"The levers aren't exhausted yet" does not defer the audit.** One audit round costs one experiment;
  a wrong inherited value costs every experiment until it is found. When the cross-family-floor signature
  is present, the audit is the *cheap* option.
- **Absence from the list is the failure mode.** The assumption you did not enumerate is the one that
  survives. Include classifications, sign conventions, and analysis-chain constants alongside the obvious
  calibrations; `frame-problem`'s physics inventory is the natural seed.
- **A confirmation is not an estimate.** Evidence that the data is "consistent with" the incumbent value
  at low signal-to-noise is weak by construction — the discriminating experiment must be designed so a
  wrong incumbent produces a *different number*, not a slightly worse fit.
- **Provenance does the ranking, mechanism does the vetting.** Weak provenance nominates a suspect; only
  a sketch of *how* its being wrong produces the observed stall keeps it on the list. Both are required.
- **Record the cleared ones.** An audit that leaves no `record-decision` trail will be re-run from
  scratch at the next plateau — or worse, skipped because "we already checked that."

## Output

A short audit record (journal or findings note): the inheritance table (value → provenance → stall
mechanism → rank), the discriminating experiment with its solve-don't-confirm design and operating-point
check, the verdict, and the `record-decision` entries for cleared suspects. If a value fell: the
invalidation scope (what re-baselines, what re-verifies).

## Composition

`campaign-status` triggers this at a resistant plateau (its §4 re-plan) · the charter's *Getting
Unstuck* block names the trigger conditions · `frame-problem` seeds the inheritance enumeration ·
`record-decision` stores provenance tags, cleared suspects, and revisit-if triggers ·
`attribute-mechanism` takes over when the audit surfaces a signature needing a cause ·
`verify` grades the discriminating experiment's result before the revised value is adopted — and
`verify` §5b / PRINCIPLES Ctx 4 are the *prospective* twin of this whole skill (falsify an
INFERRED/RECALLED fact before it becomes load-bearing); this is the retrospective audit for when that
gate was missed and a plateau is the symptom ·
`fork-campaign` if a fallen assumption invalidates standing findings · `docs/reference/pivoting.md`
remains the sibling path for the *other* species of plateau (exhausted levers).

## Checklist

- [ ] Trigger condition named (cross-family floor / a-priori gap / unresponsive effect / scheduled)?
- [ ] Inheritance enumerated in writing — including classifications and analysis constants?
- [ ] Every entry provenance-tagged (PINNED…REASONED)?
- [ ] Each suspect vetted with a stall mechanism sketch, not a vibe?
- [ ] Discriminating experiment SOLVES for the value (output is a number, not a verdict)?
- [ ] Operating-point validity audited — every calibration valid where this test runs?
- [ ] Cleared suspects recorded with revisit-if triggers?
- [ ] Fallen value treated as an invalidation event (re-baseline / re-verify / fork if needed)?
