---
name: record-decision
description: >-
  Capture the "why" behind a non-obvious engineering or modeling decision as a short, durable record —
  decision, the alternatives considered, why this one, the conditions it depends on, and what would make you
  revisit it. Use when you make a choice a future reader (or you, in six months) would otherwise have to
  reverse-engineer: picking one method/library/parameterization/approximation over another, adopting a
  non-obvious convention, accepting a trade-off, or making an assumption a result will rest on. Phrasings
  like "record this decision", "document why we chose...", "write an ADR", "note the reasoning here". It is
  distinct from conventions (the rules themselves) and the experiment journal (what happened) — this is the
  rationale and its expiry conditions. Pairs with verify/frame-problem (record the why of a non-obvious
  check or a parked physical effect).
---

# record-decision — capture the why, and when to revisit it

Research and modeling work is a chain of choices, and the reasoning behind them evaporates fast. Six months
on, nobody remembers why the timestep is what it is, why that approximation was deemed safe, or which
library was rejected and why — so the choice gets blindly kept or blindly reverted, both expensive. This
skill writes a **short, durable rationale** at the moment of decision, including the part that's almost
always lost: **the conditions the decision depends on, and the trigger that should make you reconsider it.**

It is deliberately lightweight — a few sentences, not a committee document. It is *not* the conventions file
(which states the rules) and *not* the experiment journal (which logs what happened); it is the **why**
behind a choice, and its expiry conditions.

## When it's worth a record
Record a decision when it is **non-obvious and consequential** and a future reader would otherwise have to
reverse-engineer it:
- choosing one method / library / model / parameterization / numerical scheme over a real alternative;
- an **approximation or assumption** a result will rest on (this links to the `frame-problem` inventory and
  to a `verify` QUESTIONABLE ASSUMPTION);
- a non-obvious **convention** (sign, frame, normalization) adopted to resolve an ambiguity;
- a **trade-off** accepted (accuracy vs cost, generality vs simplicity);
- the **why of a non-obvious verification check** (so a future editor doesn't delete a guard they don't
  understand).

Don't record the obvious or the trivial — that's noise. The test is: *would someone reasonably wonder "why
was this done this way?" and be unable to answer it from the code?*

## The fields (decision / alternatives / why / conditions / revisit-if)
Capture, briefly:
- **Decision** — what was chosen, concretely.
- **Alternatives considered** — the real options on the table (including "do nothing"), one line each. A
  decision with no alternatives recorded reads as the only option, which is rarely true.
- **Why this one** — the reasoning and the trade-off, tied to the actual constraints (compute, accuracy,
  fabrication, time, interpretability). Name the evidence if there is some.
- **Conditions it depends on** — the assumptions/regime that make this the right call (a parameter range,
  a data property, a compute budget, a deadline). These are what change underneath a decision.
- **Revisit-if** — the concrete trigger that should reopen it ("if we move beyond the dilute regime", "if
  the grid exceeds 10⁶ cells", "if validation data arrives"). This is the field that makes the record
  *living* rather than archival.

Keep notation and links consistent with the rest of the work; reference related decisions and the
`frame-problem` artifact where relevant.

## Where it lives
- **Campaign:** an append-only engineering-decisions record (e.g. `docs/ENGINEERING_NOTES.md`), separate
  from `CONVENTIONS.md` and the experiment `JOURNAL`. One entry per decision; never rewrite history —
  supersede an old entry with a new one and link them.
- **General session:** a short `DECISIONS.md` (or a section of the project doc); graduates into the campaign
  record if the work grows into one.
- Trivial/short-lived work needs none — just decide.

## Composition
- **`frame-problem`** — a parked physical effect or a key assumption gets a decision record so its
  rationale and revisit-trigger survive.
- **`verify`** — the *why* of a non-obvious check, and the premise behind a QUESTIONABLE ASSUMPTION verdict.
- **`simulation-design` / `correctness-suite`** — the rationale for a tool choice, a discretization, or a
  non-obvious regression gate.
- **`report`** — decision records feed the methods/limitations sections (why each choice, what it rests on).

## Bundled asset
- `assets/decision_template.md` — the five-field record (decision · alternatives · why · conditions ·
  revisit-if), with status and date.

## Checklist
- [ ] The decision is stated concretely, with the real alternatives (incl. "do nothing").
- [ ] The reasoning ties to actual constraints/evidence, not just preference.
- [ ] The **conditions it depends on** are written down.
- [ ] A concrete **revisit-if** trigger is set.
- [ ] It's in the right place (engineering record), not mixed into conventions or the journal.
