---
id: ip-and-attribution
kind: reference-doc
layer: shared
load: on-demand
load_trigger: Building or ingesting a capability from an external source — a paper's method, a package's
  algorithm, a textbook derivation, someone else's scaffolding — into a skill, the KB, or shipped kit
  content; read before shipping or monetizing anything containing adapted material. The standing constraint
  on all capability-library work.
frozen: false
addresses: [1, 7]
status: new
review: living
---

# IP & attribution — cite and adapt, never reproduce

The kit's provenance ethic and copyright discipline point the same direction: **a capability is trustworthy
only when it is keyed to a real source, and shippable only when what shipped is *yours* — the cited idea,
re-expressed, never the source's expression, copied.** Ideas, methods, equations, and algorithms are not
copyrightable; their *expression* — the prose, the code, the figures — is. So the rule is one line:

> **Cite + adapt, never reproduce.** Learn the principle from the source, re-implement or re-express it
> yourself, and key the result to a real citation surfaced to the user.

This is a discipline doc, not legal advice — where real money or publication is at stake, the posture is
confirmed by a human (open decision #8: cite-and-adapt-only for the capability library).

## The three named risk patterns

Each of these was called out explicitly before any capability work began — check every ingest and every
build against all three:

- **Bootleg-source ingestion.** A scanned textbook or paper PDF of unclear provenance (the canonical
  example: a bootleg Levitt) must not become KB raw material. The KB already makes provenance mandatory at
  ingest — *how obtained* is part of the provenance record, not a nicety. A source you cannot legitimately
  access is a source the kit does not ingest; content already derived from one is quarantined, not shipped.
- **Port vs. re-implementation.** Translating a package's source line-by-line into another language (e.g. a
  `SpinDynamica` → Python *port*) produces a derivative work of that code — the language changed, the
  expression didn't. The legitimate path is a **re-implementation from cited principles**: work from the
  published equations, the documented algorithm, the paper — not from the source code — and say so in the
  capability's provenance. If you have read the source code, you are no longer clean; prefer building from
  the paper first and using the package only as an independent *check* of your output.
- **Scaffolding borrow.** Third-party agent scaffolding — Anthropic's plugin examples, another project's
  skills or prompt text — carries its own license. Check it before adapting; take the *pattern*, rewrite
  the prose; never wholesale-copy another plugin's text into shipped kit content.

## The provenance gate for capability work

Every capability built from external material (the C1–C4 cluster: PDF ingests, Zotero sync, the
physics/math capability library, user drop-ins) passes through the KB's existing source-keying — no new
machinery, just no exceptions:

1. **Every capability skill is keyed to a real citation** — a resource `@key` in the KB registry
   (`wiki/registry.md`), with full provenance (source, author, date, **how obtained**) recorded at ingest.
2. **The provenance is surfaced to the user**, not buried: a capability answers *"per `@key`"*, so the user
   always knows whose method they are using and can go to the source.
3. **Verbatim material is minimal and attributed** — a brief quote with attribution where the exact wording
   matters, or nothing; figures and long passages are never reproduced, they are cited.
4. **The citation is real** — it resolves to the actual paper claimed (`/physkit:cite-check`); a capability
   keyed to an unverifiable citation is not shippable.

## Pre-ship checklist

Before any capability (or the library) ships or is monetized, every box checks:

- [ ] Every capability keyed to a real, resolvable citation — `cite-check` passes on the set.
- [ ] No verbatim copyrighted text beyond brief, attributed quotes; no reproduced figures.
- [ ] No ported code: every implementation traceable to cited principles (paper/spec), and its provenance
      says which; any consulted package used only as an independent check, and named.
- [ ] Every borrowed scaffold/template/prompt pattern license-checked, with attribution where required.
- [ ] No content derived from a source of unclear or illegitimate provenance (the *how obtained* field is
      filled and clean for every ingested source involved).
- [ ] The posture (cite-and-adapt-only) confirmed by decision #8 before monetizing.

## Pointers

`knowledge-base/CLAUDE.md` (provenance mandatory at ingest; `raw/` immutable); the `add-new-resource` /
`ingest-transcript` skills (the ingest procedure that records *how obtained*); `/physkit:cite-check` (every
key resolves to the real paper); `export-bibtex` (the registry→bibliography path that keeps `@keys`
honest); open decision #8 (the human confirmation of this posture before shipping/monetizing).
