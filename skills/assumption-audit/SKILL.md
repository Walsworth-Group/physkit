---
name: assumption-audit
description: >-
  Audit inherited values when an optimization plateaus.
---

# assumption-audit — when optimization stalls, audit what it inherits

A plateau has two species and the standard response fixes only one. If the levers are exhausted,
escalate or pivot (`docs/reference/pivoting.md`). If instead the stall is caused by a **wrong inherited
value** (a miscalibration, a mis-derived quantity, or a misread classification that every experiment
carries), every lever sits downstream of the error and escalation spends budget re-measuring the same
wall. The rule this skill enforces: a hard plateau is evidence about the campaign's assumptions as well
as its levers. Before committing more optimization experiments, audit what the current best inherits,
and buy one experiment that re-measures the top suspect from scratch.

The failure has a characteristic shape. A classification or a calibration is adopted without being
re-measured, a derived quantity is computed from it, and every downstream experiment inherits that
quantity. The effect under study can still appear in the data and still pass the loop's own control
experiments while one-lever optimization arms stay pinned at the same signal-to-noise floor, because
each arm searches at the inherited value. A loop can design the correct discriminating measurement and
still keep the wrong number, by framing that measurement as a confirmation of the incumbent and reading
the mismatch as an artifact. No lever fixes a value that is never re-opened.

## When to run it

Trigger on any of these, whichever comes first:

- **Cross-family floor:** one-lever experiments across ≥2 independent lever families land at the same
  performance floor. "Same" means indistinguishable within the metric's replicate spread, the noise
  floor `verify`'s campaign mode establishes. A floor shared across independent families is the
  signature of a binding constraint upstream of all of them.
- **A-priori gap:** the observed performance sits orders of magnitude from its own a-priori/CRB-style
  expectation and no lever moves the gap.
- **Unresponsive effect:** an effect already reported as present whose strength shows no response
  beyond that replicate spread across the swept range of the levers that should modulate it.
- **Scheduled:** `campaign-status` detects a plateau and lever coverage is already broad.

Do not reach for it when a single lever family is merely unfinished (keep mining), when the run crashed
(`debug`), or when the question is which lever to try next (`pivoting.md`). This skill asks a different
question: what does every experiment believe that nobody has re-measured?

Rule out the cheaper rival diagnosis first. The cross-family floor has a second explanation that does
not involve a wrong inherited value: the space may be **interaction-dominated**, so that no lever moves
the metric alone while a combination would. One-at-a-time search cannot escape such a space by
construction, and it reads the same as an upstream constraint. Before auditing the inheritance, spend
one small factorial or paired-lever run across the two families that floored. If the pair moves what
neither lever moved, the plateau is an interaction rather than a bad assumption, and this skill is the
wrong tool. That test is the cheaper one; running it second means re-measuring a calibration that was
fine.

## The method

1. **Enumerate the inheritance.** List every value the current-best configuration carries that was not
   measured in the current campaign phase: calibrations, derived quantities (anything computed from a
   measurement plus an assumption), adopted constants, and **classifications** (a peak identification, a
   mode assignment, a pattern read). Classifications are the entries most often omitted. A
   classification is an assumption no less than a number is: count what is actually there before naming
   what it is. Tag each entry with its provenance (the source-authority ladder: PINNED / REPORTED /
   INFERRED / RECALLED / REASONED — see `record-decision`). PINNED entries are near-immune; INFERRED and
   REASONED are the prime suspects.
2. **Interrogate each against the stall signature.** For each entry ask: if this were wrong, would the
   observed stall follow? A mechanism sketch is required. "Carrier wrong by a few kHz ⇒ real line
   present but outside the estimator window ⇒ per-experiment SNR pinned at noise floor while detection
   controls still pass" is a mechanism sketch; "maybe the calibration drifted" is not. Rank the entries
   by explanatory power × provenance weakness × cheapness of the discriminating test.
3. **Buy one discriminating experiment for the top suspect.** Two clauses are binding.
   - **Solve, do not confirm.** The experiment must estimate the suspect value from scratch and compare
     with the incumbent only afterwards. A consistency check framed as "verify the current value"
     invites reading any mismatch as an artifact, which is how a loop runs the right experiment and
     keeps the wrong number. Design the analysis so its output is a value, not a verdict on the
     incumbent.
   - **Operating-point validity.** Enumerate everything else that changes between this experiment and the
     ones it will be compared against, and re-derive any calibration that is valid only at the operating
     point where it was taken: a pulse calibration at a new frequency or amplitude, a gain at a new
     range, a response at a new temperature. A discriminating test run with an out-of-point calibration
     can refute a true hypothesis cleanly. Pre-registered falsification combined with an unmodeled
     confound produces a confident wrong conclusion.
4. **Close the loop on the verdict.**
   - Suspect **cleared**: record it (`record-decision`, with the discriminating evidence and a
     revisit-if trigger) so the audit never re-litigates it, then move to the next suspect or back to
     optimization.
   - Suspect **falls**: the revised value is an invalidation event, not a tweak. Re-baseline anything
     that inherited it, mark affected findings for re-verification, and if standing results are
     invalidated wholesale, use `fork-campaign`. Then return to optimization mode. The audit is a mode
     change, not a new home.

## Rules of evidence

- "The levers aren't exhausted yet" does not defer the audit. One audit round costs one experiment; a
  wrong inherited value costs every experiment until it is found. When the cross-family-floor signature
  is present, the audit is the cheaper option.
- An assumption absent from the list is never audited. Enumerate classifications, sign conventions, and
  analysis-chain constants alongside the obvious calibrations; `frame-problem`'s physics inventory is
  the seed.
- A confirmation is not an estimate. Evidence that the data is consistent with the incumbent value at
  low signal-to-noise is weak by construction. Design the discriminating experiment so that a wrong
  incumbent produces a different number, not a slightly worse fit.
- Provenance does the ranking; mechanism does the vetting. Weak provenance nominates a suspect. Only a
  sketch of how its being wrong produces the observed stall keeps it on the list. Both are required.
- Record the cleared suspects. An audit that leaves no `record-decision` trail is re-run from scratch at
  the next plateau, or skipped on the belief that it was already checked.

## Output

A short audit record (journal or findings note): the inheritance table (value → provenance → stall
mechanism → rank), the discriminating experiment with its solve-don't-confirm design and operating-point
check, the verdict, and the `record-decision` entries for cleared suspects. If a value fell, record the
invalidation scope: what re-baselines and what re-verifies.

## Composition

`campaign-status` triggers this at a resistant plateau (its §4 re-plan) · `roles/worker.md`'s *Getting
Unstuck* block names the trigger conditions · `frame-problem` seeds the inheritance enumeration ·
`record-decision` stores provenance tags, cleared suspects, and revisit-if triggers ·
`attribute-mechanism` takes over when the audit surfaces a signature needing a cause ·
`verify` grades the discriminating experiment's result before the revised value is adopted ·
`fork-campaign` if a fallen assumption invalidates standing findings · `docs/reference/pivoting.md`
remains the sibling path for the other species of plateau (exhausted levers).

`verify` §5b is the prospective form of this discipline: falsify an INFERRED or
RECALLED fact before it becomes load-bearing. This skill is the retrospective audit for when that gate
was missed and a plateau is the symptom.

## Checklist

- [ ] Trigger condition named (cross-family floor / a-priori gap / unresponsive effect / scheduled)?
- [ ] Inheritance enumerated in writing, including classifications and analysis constants?
- [ ] Every entry provenance-tagged (PINNED…REASONED)?
- [ ] Each suspect vetted with a stall mechanism sketch?
- [ ] Discriminating experiment solves for the value (output is a number, not a verdict)?
- [ ] Operating-point validity audited, every calibration valid where this test runs?
- [ ] Cleared suspects recorded with revisit-if triggers?
- [ ] Fallen value treated as an invalidation event (re-baseline / re-verify / fork if needed)?
