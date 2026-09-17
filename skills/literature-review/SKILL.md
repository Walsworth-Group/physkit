---
name: literature-review
description: >-
  Survey a field: key results, trajectory, closest prior art, a ranked reading list, every reference
  verified.
---

# literature-review — understand the field, honestly and efficiently

Choosing a direction, pressure-testing an idea, or scoping a problem requires an honest picture of what is
already known: the key results, where the field is heading, and the closest prior work to the problem at hand
with the part of its approach that transfers. This skill produces that picture, cited and verified.

Two requirements are absolute: honesty, and verified citations. A review that inflates consensus, hides
disagreement, or invents a plausible-looking reference is worse than none: it launches work on false ground.
Every load-bearing claim traces to a real source you confirmed, and the review states what is established,
what is contested, and what it could not find. The citation gate is not optional: a fabricated identifier is
not detectable by the reader.

## When to use / not use
- **Use** to understand a field, find prior art for an idea or problem, or survey the standard methods, as the
  front-end of `assess-idea`, `frame-problem`, or `new-campaign`, or on its own.
- **`cite-check`** instead when you already have a specific reference list to verify; this skill composes
  cite-check as its final gate. **`report`** instead to write up finished work. **`assess-idea`** judges
  whether an idea is worth pursuing; it consumes this skill's output rather than replacing it.
- **Self-contained.** It needs no other research skill. If a general `deep-research` skill is installed it can
  accelerate the heavy multi-source pass; the procedure below assumes nothing beyond this skill.

## Procedure

1. **Scope with the user.** Get the sub-area and the **purpose**: grounding a campaign, prior art for a
   specific idea, learning a method, or deciding a direction. The purpose sets the depth and *what to
   extract*. Ask one or two clarifying questions when the topic is broad. Do not require a fully specified
   query, and do not extend the scoping past those questions.

2. **Search broadly, arXiv-first, token-efficiently.** Run several queries, not one, covering the core topic,
   the closest published analogues, and recent advances for the moving parts, including since when each
   became possible. Prefer the arXiv HTML
   (`ar5iv.org/abs/<id>` or `arxiv.org/abs/<id>`) or LaTeX source over publisher PDFs (paywalls, heavy
   formatting). When only a PDF exists, convert it with a scientific-PDF→markdown tool and read only the
   relevant sections. Cache what you fetch so it is not re-pulled. For a large review, delegate parallel
   query threads to sub-agents (context economy) and synthesize centrally.

3. **Read for the right things**, not a generic summary. Screen on abstracts; conclude on full text. A
   load-bearing judgment (this transfers, this supports the claim, this is the closest prior art) comes from
   the relevant full-text section. An abstract triages which papers earn a deep read; a conclusion still
   resting on one is provisional. Read for:
   - **Key results and the field's trajectory** — what is settled, and what has newly become possible (a new
     method, a new regime, a new instrument) that opens directions.
   - **The closest prior art to the user's problem** — has this been tried, and if it was abandoned, why? An
     abandoned approach is as informative as a successful one.
   - **Standard methods and their trade-offs**, so the work does not reinvent or miss a known technique.
   - **What transfers** — the specific approaches, tricks, or results that carry over to the user's problem.
     This is the review's highest-value output, not the summary.

4. **Organize into a brief.** Structure it as established / contested / open: what the field agrees on, where
   it disagrees, and the open gaps. Name each disagreement rather than smoothing it over. The open gaps are
   the opportunities that feed `research-direction` and `assess-idea`. Include a methods table (approach ·
   what it is good and bad at) and a priority-ranked reading list (the few papers worth reading first, and
   why), with the transferable approaches flagged.

5. **Verify every citation — the mandatory gate (`cite-check`).** Before the brief is delivered, confirm each
   reference against the actual source: exact title, full author list, year, venue, and DOI/arXiv id, and that
   the paper supports the claim it is cited for. Read the claim support from the full-text section, not the
   abstract. Support found only in an abstract is carried as provisional (cite-check PROVISIONAL) and the
   brief says so; it is never presented as established. A reference that 404s, redirects, or points to a
   different paper is not a citation: drop or fix it. A reference that cannot be confirmed is flagged as
   unconfirmed, never invented or approximated. Prefer the arXiv version of the record.

6. **Deliver honestly.** Label each part of the brief as established in the literature, your synthesis, or
   uncertain / not found. State the field's open disagreements and the limits of the search, including what
   was not covered. In a campaign, write or refresh `LITERATURE.md` (summaries + the ranked roadmap) and seed
   `../../PROJECT.md` (governing physics + references), and keep the two in sync.

## Output
A scannable, cited brief: established / contested / open · a methods table · the closest prior art and what
transfers · a priority-ranked reading list · explicitly flagged uncertainties and search limits. Every
reference is clickable and cite-check-verified. Standalone: a message or a short doc. Campaign:
`LITERATURE.md` (+ `PROJECT.md` references).

## Composition
- **`cite-check`** — the mandatory final gate. Never deliver an unverified reference.
- **`assess-idea`** — consumes this skill's prior-art + closest-solved-problem output (its step 4).
- **`frame-problem`** — a field-informed physics inventory and predictive framework build on this.
- **`new-campaign`** — seeds `LITERATURE.md` / `PROJECT.md` from a review at setup.
- **`report`** — if the review itself is a deliverable, `report` formats and re-verifies it.
- **sub-agents** (context economy) — parallel search and read threads for a large review, synthesized
  centrally; match the model to the task (light for fetch and scan, escalate for synthesis).

## The failure modes to guard against
- **Fabricated or misattributed citations** — the `cite-check` gate exists for this failure.
- **Abstract-driven conclusions** — grading a paper's support, or its subject, from its abstract. An abstract
  is written to sound broader and cleaner than the paper delivers. Screen on it, conclude on the full text; a
  claim supportable only from an abstract is provisional, not established.
- **Confirmation-seeking search** — a search for papers that *support* X returns keyword-matching abstracts
  and misses those that complicate it. Query what the literature says about X instead. A well-evidenced
  paper that complicates or refutes X is a successful result, not a failed row.
- **Manufactured consensus** — smoothing over real disagreement to sound authoritative; name the conflict instead.
- **Recency and availability bias** — over-weighting what is easiest to find or newest; search the foundational
  work as well.
- **Absence of evidence reported as novelty** — absence from this search is not proof the field has not done
  it; write "not found in this search," not "novel."

## Checklist
- [ ] Purpose scoped with the user (depth + what-to-extract set accordingly).
- [ ] Multiple queries run (core + analogues + recent); arXiv-first; fetches cached.
- [ ] Read for trajectory, closest prior art (+ why abandoned), methods, and what transfers (load-bearing judgments from full text, not the abstract) — not a generic summary.
- [ ] Brief organized established / contested / open, with a methods table + priority-ranked reading list.
- [ ] Every citation cite-check-verified (title/authors/year/venue/id + claim-support from full text, not the abstract); abstract-only support carried as provisional, unconfirmed ones flagged, none invented.
- [ ] Honesty labels applied (established vs synthesis vs uncertain); field disagreements and search limits stated.
- [ ] Campaign: `LITERATURE.md` written/refreshed and `PROJECT.md` references seeded (kept in sync).
