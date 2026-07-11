---
name: cite-check
description: >-
  Verify that every citation is real and correctly used before it goes into a document — the anti-
  hallucination gate for references. Use when finalizing a report/paper bibliography, when asked to "check
  these references / citations", when you've drafted citations an LLM might have invented, or whenever a
  claim leans on a source. For each reference it confirms, against the actual source, the exact title, the
  full author list, year, venue, and identifier (DOI / arXiv id) — and that the paper actually supports the
  claim it's cited for. A reference that 404s, redirects, or points to a different paper is not a citation;
  one that can't be confirmed is flagged, never invented or approximated. Prefers the arXiv version and
  reads token-efficiently; parallelizes across subagents for a large bibliography. Composed by report and
  final-report; also runs standalone. Distinct from verify (checks results, not references).
---

# cite-check — real papers only, used for what they actually say

Hallucinated or mis-attributed references are the classic failure mode of LLM-written scientific documents,
and they destroy trust instantly — one fake DOI taints the whole paper. This skill is the gate that
prevents it: **no citation enters a document until it has been confirmed against the real source.** The
default is suspicion; a reference earns its place only by being found and matched.

## The discipline
For **every** citation:
1. **Fetch the actual source** and confirm it exists. Prefer the **arXiv** version — the abstract page or
   `ar5iv` HTML, or the LaTeX source — over a publisher PDF (no paywall, clean metadata, token-efficient).
   Convert a PDF only if needed (a scientific-PDF→markdown tool) and read only the parts you need. For
   anything not confirmable from one authoritative hit, **cross-check independent indexes** — CrossRef,
   Semantic Scholar, and OpenAlex are open and need no API key: agreement across **≥2** is strong
   existence evidence, a hit in only **one** is *suspicious* (verify harder), **zero** is unconfirmable.
2. **Match the metadata exactly:** the **title**, the **full author list** (not "et al." — the actual
   authors, in order), the **year**, the **venue**, and the **identifier** (DOI or arXiv id) must all match
   what you are citing. A link that 404s, redirects to a homepage, or resolves to a *different* paper is
   **not** a citation. **Watch for *chimeric* references** — a real, correct-sounding title stitched onto
   the wrong authors, year, or venue (or two papers fused into one entry). These survive a naive title
   search and are the signature of an LLM-invented citation; catch them by confirming the title **and**
   the full author list resolve to the *same* record.
3. **Match the claim to the content — from the section that would contain it, not the abstract.** Confirm the
   paper actually says what you cite it for. An abstract *screens* a citation (is this even the right paper?);
   it does not *confirm* a claim — abstracts overstate, drop caveats, and reuse a claim's keywords in a
   different scope. Read the relevant full-text section (results / method / the stated limitation). If only the
   abstract is reachable (paywall / bot-wall), the claim-support verdict is **PROVISIONAL**, never CONFIRMED,
   and the reference records its read-depth as `abstract-only`. A real paper attached to a claim it doesn't
   support — or one whose support you inferred from the abstract — is still a bad citation.
4. **Grade each reference** (each grade records its read-depth — `full` / `abstract-only` / `partial:<section>`):
   - **CONFIRMED** — found, metadata matches, and claim-support confirmed **from the relevant full-text
     section**. Keep it (with corrected metadata if it was slightly off).
   - **PROVISIONAL** — found and metadata matches, but claim-support rests on the **abstract only** (full text
     unreachable). Usable as *provisional* support, flagged `read: abstract-only`; it **cannot alone** carry a
     claim to a settled / "well-evidenced" status. Upgrade to CONFIRMED on a full read, or soften the claim.
   - **MISMATCH** — exists but the metadata or the claim-support is wrong. Fix the entry, or move the claim
     to the right source.
   - **UNCONFIRMABLE** — cannot find it, or cannot confirm the claim at all. **Flag it** — do not ship it.
     Either find a real supporting source or drop/soften the claim.
5. **Never invent or approximate** a reference, DOI, or arXiv id. If a statement has no real supporting
   source, that's fine — label the underlying choice honestly (e.g. a parameter as "empirical / lab-internal"
   in the parameter table) rather than manufacturing a citation for it.

## Filling genuine gaps
When a claim needs a citation it doesn't have, search for a real supporting source, then verify it by the
same discipline before using it. Seed from any curated literature the project already has (a campaign's
`LITERATURE.md` maps references to topics) — those are pre-vetted anchors, but re-confirm anything you're
unsure of.

## Scaling to a large bibliography
Verification parallelizes cleanly: fan the references out across subagents (Agent tool), one batch each,
and assemble the verdicts centrally. These existence/metadata checks are mechanical — run the fan-out
sub-agents on a **lighter model**; reserve the stronger model for judging whether a source actually
*supports the claim* it's cited for. Keep the final compiled bibliography and its `.bib` in one place so
keys stay consistent. For a campaign capstone this is exactly how `final-report` checks a long reference
list.

## Output
Return a short per-reference ledger — **key · CONFIRMED / PROVISIONAL / MISMATCH / UNCONFIRMABLE ·
read-depth (full / abstract-only) · the verified (or corrected) metadata · the source URL/id checked** —
plus a corrected `refs.bib` (or inline bibliography) containing only confirmed entries (PROVISIONAL ones
kept only where the claim they back is softened to match), with flagged ones called out separately so
nothing unverified slips into the document silently.

## Composition
- **`report` / `final-report`** compose this as the citations half of their report-time verification
  (Standard 3); it's the `{{cite-check}}` step before a document is declared done.
- Runs **standalone** too — "are these references real?" on any bibliography or reference list.
- Pairs with **`verify`** (which checks *results*); together they are "is the science right *and* are the
  sources real."

## Checklist
- [ ] Every reference was fetched from its actual source (arXiv preferred).
- [ ] Title, full author list, year, venue, and DOI/arXiv id each match what's cited.
- [ ] Cross-checked against ≥2 independent indexes where possible (CrossRef · Semantic Scholar · OpenAlex); single-index or chimeric (title ≠ authors) hits treated as suspicious, not confirmed.
- [ ] Each paper actually supports the claim it's attached to — **confirmed from the full-text section, not the abstract**; abstract-only support is graded PROVISIONAL and flagged, never CONFIRMED.
- [ ] Unconfirmable references are flagged and removed/replaced — none invented or approximated.
- [ ] The output ledger states each reference's status + the source checked; the final bib has only confirmed entries.
