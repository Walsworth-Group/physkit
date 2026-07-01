---
name: literature-review
description: >-
  Survey a research field honestly and efficiently — its key results, where it is heading, and the closest
  prior art to your problem — with every citation verified against the real source. Use when someone wants to
  understand a field or find what's been done, with phrasings like "review the literature on X", "what's the
  state of the field", "where is X heading", "what's been done on Y", "find the closest prior work", "catch me
  up on Z", "has anyone tried ...". Self-contained (does not require any other research skill): it scopes the
  question with the user, searches broadly (arXiv-first, token-efficient), reads for the field's trajectory,
  the closest prior art, and the methods that TRANSFER to your problem, organizes an established/contested/open
  brief with a priority-ranked reading list, and — critically — verifies every reference with cite-check so no
  fabricated or misattributed citation survives. In a campaign it writes/refreshes LITERATURE.md and seeds
  PHYSICS.md. Distinct from cite-check (verifies references you already have), report (writes up finished
  work), and assess-idea (judges whether an idea is worth doing — this gathers the field it reasons over).
---

# literature-review — understand the field, honestly and efficiently

Before choosing a direction, pressure-testing an idea, or scoping a problem, you need an honest picture of what
is already known: the key results, where the field is heading, and — most valuable — the closest prior work to
*your* problem and what of its approach **transfers**. This skill produces that picture, cited and verified.

Its two non-negotiables are **honesty** and **verified citations**. A literature review that quietly inflates
consensus, hides disagreement, or — worst — invents a plausible-looking reference is worse than none: it
launches work on false ground. Every load-bearing claim traces to a real source you confirmed, and the review
says plainly what is established, what is contested, and what it could not find. *(This matters most for a
researcher new to AI tools, who will not catch a fabricated DOI — so the citation gate is not optional.)*

## When to use / not use
- **Use** to understand a field, find prior art for an idea or problem, or survey the standard methods — as the
  front-end of `assess-idea`, `frame-problem`, or `new-campaign`, or entirely on its own.
- **`cite-check`** instead when you already have a specific reference list to verify (this skill *composes*
  cite-check as its final gate). **`report`** instead to write up finished work. **`assess-idea`** judges
  whether an idea is worth pursuing — it *consumes* this skill's output rather than replacing it.
- **Self-contained.** It needs no other research skill. If a general `deep-research` skill is installed it can
  accelerate the heavy multi-source pass, but this skill runs standalone and the procedure below assumes nothing.

## Procedure

1. **Scope with the user — briefly.** Get the sub-area and, crucially, the **purpose**: grounding a campaign?
   prior art for a specific idea? learning a method? deciding a direction? The purpose sets the depth and *what
   to extract*. Ask one or two clarifying questions if the topic is broad — don't demand a perfect query, and
   don't over-interrogate; a physicist new to the tool should feel helped, not quizzed.

2. **Search broadly, arXiv-first, token-efficiently.** Run several queries (not one) covering the **core topic
   + the closest published analogues + recent advances / "since when"** for the moving parts. Prefer the
   **arXiv HTML** (`ar5iv.org/abs/<id>` or `arxiv.org/abs/<id>`) or LaTeX source over publisher PDFs (paywalls,
   heavy formatting); when only a PDF exists, convert it with a scientific-PDF→markdown tool and read only the
   relevant sections; **cache** what you fetch so you don't re-pull. For a large review, delegate parallel
   query threads to **sub-agents** (context economy) and synthesize centrally.

3. **Read for the right things** (not a generic summary):
   - **Key results & the field's trajectory** — what's settled, and *what just became possible* (a new method,
     a new regime, a new instrument) that opens directions (Wieman decision 1).
   - **The closest prior art to the user's problem** — has this been tried? If it was **abandoned, why?**
     (a dead end is as informative as a success) (Wieman decision 7).
   - **Standard methods + their trade-offs** — so the work doesn't reinvent or miss a known technique.
   - **What TRANSFERS** — the specific approaches, tricks, or results that carry over to the user's problem.
     This "what can I borrow" lens is the review's highest-value output, not the summary.

4. **Organize into a brief.** Structure it as **established / contested / open**: what the field agrees on,
   where it genuinely disagrees (name the disagreement — don't smooth it over), and the **open gaps** (which
   are the opportunities that feed `research-direction` / `assess-idea`, Wieman decision 2). Include a
   **methods table** (approach · what it's good/bad at) and a **priority-ranked reading list** (the few papers
   worth reading first, and why), with the transferable approaches flagged.

5. **Verify every citation — the mandatory gate (`cite-check`).** Before the brief is delivered, confirm each
   reference against the actual source: exact **title, full author list, year, venue, and DOI/arXiv id**, and
   that the paper **actually supports the claim** it's cited for. A reference that 404s, redirects, or points
   to a different paper is **not a citation** — drop or fix it; one you cannot confirm is **flagged as
   unconfirmed, never invented or approximated.** Prefer the arXiv version of the record.

6. **Deliver honestly.** Distinguish **what's established in the literature** from **your synthesis** from
   **what's uncertain or you couldn't find**; label each. State the field's open disagreements and the limits
   of the search (what you didn't cover). In a **campaign**, write or refresh **`LITERATURE.md`** (summaries +
   the ranked roadmap) and seed **`docs/PHYSICS.md`** (governing physics + references) — keep the two in sync.

## Output
A scannable, **cited** brief: established / contested / open · a methods table · the closest prior art (+ what
transfers) · a priority-ranked reading list · explicitly flagged uncertainties and search limits. Every
reference is clickable and **cite-check-verified**. Standalone: a message or a short doc. Campaign:
`LITERATURE.md` (+ `PHYSICS.md` references).

## Composition
- **`cite-check`** — the mandatory final gate; never deliver an unverified reference.
- **`assess-idea`** — consumes this skill's prior-art + closest-solved-problem output (its step 4).
- **`frame-problem`** — a field-informed physics inventory and predictive framework build on this.
- **`new-campaign`** — seeds `LITERATURE.md` / `PHYSICS.md` from a review at setup.
- **`report`** — if the review itself is a deliverable, `report` formats and re-verifies it.
- **sub-agents** (context economy) — parallel search/read threads for a large review, synthesized centrally;
  match the model to the task (light for fetch/scan, escalate for synthesis).

## The failure modes to guard against
- **Fabricated or misattributed citations** — the cardinal sin; the `cite-check` gate exists for exactly this.
- **Manufactured consensus** — smoothing over real disagreement to sound authoritative; name the conflict instead.
- **Recency/availability bias** — over-weighting what's easy to find or newest; seek the foundational work too.
- **"I don't recall seeing it" as evidence of novelty** — absence in your search is not proof the field hasn't
  done it; say "not found in this search," not "novel."

## Checklist
- [ ] Purpose scoped with the user (depth + what-to-extract set accordingly).
- [ ] Multiple queries run (core + analogues + recent); arXiv-first; fetches cached.
- [ ] Read for trajectory, closest prior art (+ why-abandoned), methods, and **what transfers** — not a generic summary.
- [ ] Brief organized established / contested / open, with a methods table + priority-ranked reading list.
- [ ] **Every citation cite-check-verified** (title/authors/year/venue/id + claim-support); unconfirmed ones flagged, none invented.
- [ ] Honesty labels applied (established vs synthesis vs uncertain); field disagreements and search limits stated.
- [ ] Campaign: `LITERATURE.md` written/refreshed and `PHYSICS.md` references seeded (kept in sync).
