---
name: record-decision
description: >-
  Record the why of a non-obvious decision: alternatives, reasons, dependencies, what would trigger
  a revisit.
---

# record-decision — capture the why, and when to revisit it

The reasoning behind a modeling or engineering choice is lost quickly. Within months, why the timestep
has its value, why an approximation was judged safe, or which library was rejected is no longer
recoverable, and the choice is kept or reverted without evidence. This skill writes a short, durable
rationale at the moment of decision, including the two parts most often lost: the conditions the decision
depends on, and the trigger that reopens it.

The record is short: a few sentences, not a committee document. It is not the conventions file (which
states the rules) and not the experiment journal (which logs what happened). It is the rationale behind a
choice and its expiry conditions.

## When it's worth a record
Record a decision when it is non-obvious and consequential and a future reader would otherwise have to
reverse-engineer it:
- choosing one method / library / model / parameterization / numerical scheme over a real alternative;
- an approximation or assumption a result will rest on (this links to the `frame-problem` inventory and
  to a `verify` QUESTIONABLE ASSUMPTION);
- a non-obvious convention (sign, frame, normalization) adopted to resolve an ambiguity;
- a trade-off accepted (accuracy vs cost, generality vs simplicity);
- the reason for a non-obvious verification check, so a later editor does not delete a guard whose
  purpose is not in the code.

Do not record obvious or trivial choices; they are noise. The test: would someone reasonably ask why this
was done this way and be unable to answer from the code?

## The fields (decision / alternatives / why / [provenance] / conditions / revisit-if)
Capture, briefly:
- **Decision** — what was chosen, concretely.
- **Alternatives considered** — the real options on the table (including "do nothing"), one line each. A
  decision with no alternatives recorded reads as the only option, which is rarely true.
- **Why this one** — the reasoning and the trade-off, tied to the actual constraints (compute, accuracy,
  fabrication, time, interpretability). Name the evidence if there is some.
- **Provenance** *(mandatory; every record states it)* — the authoritative source the decision is pinned
  to, and its confidence: *PINNED* (read from a shipped artifact / saved model / released data / empirical
  probe) · *REPORTED* (stated in a paper/doc) · *INFERRED* (from an untrusted proxy, such as leftover or
  modified code) · *RECALLED* (from memory) · *REASONED* (engineering judgment resting on no external
  claim about the system; use for a pure trade-off choice). When the decision rests on a fact from a
  source, rank sources by authority: an artifact that can be parsed or run outranks text, which outranks
  modified code, which outranks recollection. Resolve the fact to the highest authority available, and
  note lower-authority sources that disagree and were quarantined. A load-bearing fact that can only
  be marked INFERRED or RECALLED is not yet settled. Flag it; never build on it silently.
- **Conditions it depends on** — the assumptions/regime that make this the right call (a parameter range,
  a data property, a compute budget, a deadline). These are what change underneath a decision.
- **Revisit-if** — the concrete trigger that should reopen it ("if we move beyond the dilute regime", "if
  the grid exceeds 10⁶ cells", "if validation data arrives"). This field makes the record living rather
  than archival.

Keep notation and links consistent with the rest of the work; reference related decisions and the
`frame-problem` artifact where relevant.

## Where it lives
Pick the tier by what the decision outlives. Every tier is an append-only record: one entry per decision,
never rewrite history, and supersede an old entry with a new one that links to it.
- **Campaign:** `campaign.md` §Decision record — the append-only tail below the signed-off contract;
  separate from the project overview's §Standing constraints (the rules) and the
  experiment `JOURNAL` (what happened).
- **Project:** the project overview's (`PROJECT.md`) §Durable decisions — a decision that outlives
  one campaign (a project-wide convention, a shared-physics or instrument choice) and that sibling
  campaigns inherit.
- **Ad-hoc session:** the session's `sessions/<date>_<slug>/NOTES.md`; graduates to the project record once
  a campaign comes to depend on it.
- Trivial or short-lived work needs none.

## Composition
- `frame-problem` — a parked physical effect or a key assumption gets a decision record so its rationale
  and revisit-trigger survive.
- Sign-off tracking — a timed-out or unanswered approval request is recorded
  as "no sign-off obtained" at the time, never inferred later from an unrelated go-ahead. Resurface the
  gap proactively, as a request probably missed rather than a refusal, and assume neither answer meanwhile.
- `verify` — the reason for a non-obvious check, and the premise behind a QUESTIONABLE ASSUMPTION verdict.
- `simulation-design` / `correctness-suite` — the rationale for a tool choice, a discretization, or a
  non-obvious regression gate.
- `report` — decision records feed the methods and limitations sections: why each choice, what it rests
  on.

## Bundled asset
- `assets/decision_template.md` — the record (decision · alternatives · why · [provenance] · conditions ·
  revisit-if), with status and date.

## Checklist
- [ ] The decision is stated concretely, with the real alternatives (incl. "do nothing").
- [ ] The reasoning ties to actual constraints/evidence, not just preference.
- [ ] **Provenance** is recorded (mandatory) — the source the decision is pinned to + confidence
      (PINNED/REPORTED/INFERRED/RECALLED, or REASONED for a pure-judgment call); an INFERRED/RECALLED
      load-bearing fact is flagged unsettled.
- [ ] The **conditions it depends on** are written down.
- [ ] A concrete **revisit-if** trigger is set.
- [ ] It's in the right place (engineering record), not mixed into conventions or the journal.
