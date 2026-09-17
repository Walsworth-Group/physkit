---
name: cite-check
description: >-
  Confirm every citation against the real source and that it supports the claim; unconfirmable ones
  flagged, never invented.
---

# cite-check — real papers only, used for what they actually say

Hallucinated or mis-attributed references are the characteristic failure mode of LLM-written scientific
documents. One fabricated DOI discredits the whole document. This skill is the gate: no citation enters a
document until it has been confirmed against the real source. Treat every reference as unconfirmed until it
has been found and matched.

## The discipline
For every citation:
1. Fetch the actual source and confirm it exists. Prefer the arXiv version (the abstract page, the `ar5iv`
   HTML, or the LaTeX source) over a publisher PDF: no paywall, clean metadata, fewer tokens. Convert a PDF
   only when needed, with a scientific-PDF→markdown tool, and read only the parts required. When one
   authoritative hit does not settle it, cross-check independent indexes. CrossRef, Semantic Scholar, and
   OpenAlex are open and need no API key. Agreement across ≥2 is strong existence evidence; a hit in only
   one is suspicious and must be verified further; zero is unconfirmable.
2. Match the metadata exactly: the title, the full author list (the actual authors, in order, not "et
   al."), the year, the venue, and the identifier (DOI or arXiv id) must all match what is being cited. A
   link that 404s, redirects to a homepage, or resolves to a different paper is not a citation. Check for
   chimeric references: a real, correct-sounding title stitched onto the wrong authors, year, or venue, or
   two papers fused into one entry. These survive a naive title search and are the signature of an invented
   citation. Catch them by confirming that the title and the full author list resolve to the same record.
3. Match the claim to the content, from the section that would contain it rather than the abstract. Confirm
   the paper says what it is cited for. An abstract screens a citation (is this the right paper?); it does
   not confirm a claim, because abstracts overstate, drop caveats, and reuse a claim's keywords in a
   different scope. Read the relevant full-text section: results, method, or the stated limitation. If only
   the abstract is reachable (paywall or bot-wall), the claim-support verdict is PROVISIONAL, never
   CONFIRMED, and the reference records its read-depth as `abstract-only`. A real paper attached to a claim
   it does not support, or one whose support was inferred from the abstract, is a bad citation.
4. Grade each reference. Each grade records its read-depth (`full` / `abstract-only` / `partial:<section>`):
   - CONFIRMED — found, metadata matches, and claim-support confirmed from the relevant full-text section.
     Keep it, with corrected metadata if it was slightly off.
   - PROVISIONAL — found and metadata matches, but claim-support rests on the abstract only (full text
     unreachable). Usable as provisional support, flagged `read: abstract-only`. It cannot alone carry a
     claim to settled or well-evidenced status. Upgrade to CONFIRMED on a full read, or soften the claim.
   - MISMATCH — exists but the metadata or the claim-support is wrong. Fix the entry, or move the claim
     to the right source.
   - UNCONFIRMABLE — cannot find it, or cannot confirm the claim at all. Flag it; do not ship it.
     Either find a real supporting source or drop/soften the claim.
5. Never invent or approximate a reference, DOI, or arXiv id. A statement with no real supporting source is
   acceptable: label the underlying choice honestly (a parameter as "empirical / lab-internal" in the
   parameter table, for example) rather than manufacturing a citation for it.

## Filling genuine gaps
When a claim needs a citation it does not have, search for a real supporting source, then verify it by the
same discipline before using it. Seed from any curated literature the project already has; a campaign's
`LITERATURE.md` maps references to topics. Those anchors are pre-vetted, but re-confirm any that is
uncertain.

## Scaling to a large bibliography
Verification parallelizes. Fan the references out across subagents (Agent tool), one batch each, and
assemble the verdicts centrally. The existence and metadata checks are mechanical: run the fan-out
sub-agents on a lighter model, and reserve the stronger model for judging whether a source supports the
claim it is cited for. Keep the final compiled bibliography and its `.bib` in one place so keys stay
consistent. `report` uses this fan-out for a campaign capstone's reference list.

## Output
Return a short per-reference ledger: key · CONFIRMED / PROVISIONAL / MISMATCH / UNCONFIRMABLE · read-depth
(full / abstract-only) · the verified (or corrected) metadata · the source URL/id checked. Return with it
a corrected `refs.bib` (or inline bibliography) containing only confirmed entries; keep a PROVISIONAL entry
only where the claim it backs is softened to match. Call out flagged references separately so nothing
unverified enters the document silently.

## Composition
- `report` composes this as the citations half of their report-time verification
  (Standard 3). It is the `{{cite-check}}` step before a document is declared done.
- Runs standalone: "are these references real?" on any bibliography or reference list.
- Pairs with `verify`, which checks results. Together they establish that the science is right and the
  sources are real.

## Checklist
- [ ] Every reference was fetched from its actual source (arXiv preferred).
- [ ] Title, full author list, year, venue, and DOI/arXiv id each match what is cited.
- [ ] Cross-checked against ≥2 independent indexes where possible (CrossRef · Semantic Scholar · OpenAlex); single-index or chimeric (title ≠ authors) hits treated as suspicious, not confirmed.
- [ ] Each paper supports the claim it is attached to, confirmed from the full-text section and not the abstract; abstract-only support is graded PROVISIONAL and flagged, never CONFIRMED.
- [ ] Unconfirmable references are flagged and removed or replaced; none invented or approximated.
- [ ] The output ledger states each reference's status and the source checked; the final bib has only confirmed entries.
