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

A capability is trustworthy only when it is keyed to a real source. It is shippable only when what ships
is yours: the cited idea, re-expressed, not the source's expression copied. Ideas, methods, equations,
and algorithms are not copyrightable; their expression is — the prose, the code, the figures. One rule
follows:

> **Cite + adapt, never reproduce.** Learn the principle from the source, re-implement or re-express it
> yourself, and key the result to a real citation surfaced to the user.

This is a discipline doc, not legal advice. Where money or publication is at stake, a human confirms the
cite-and-adapt-only posture before the material ships.

## The three named risk patterns

Check every ingest and every build against all three.

- **Bootleg-source ingestion.** A scanned textbook or paper PDF of unclear provenance must not become
  knowledge-base raw material. Provenance is mandatory at ingest, and *how obtained* is part of that
  record. A source you cannot legitimately access is a source the kit does not ingest. Content already
  derived from one is quarantined, not shipped.
- **Port vs. re-implementation.** Translating a package's source line by line into another language
  produces a derivative work of that code: the language changed, the expression did not. The legitimate
  path is a **re-implementation from cited principles**. Work from the published equations, the documented
  algorithm, and the paper, not from the source code, and say so in the capability's provenance.
  Reading the source code forfeits that independence, so prefer building from the paper first and using
  the package only as an independent check of your output.
- **Scaffolding borrow.** Third-party agent scaffolding carries its own license: published plugin
  examples, another project's skills or prompt text. Check the license before adapting. Take the pattern
  and rewrite the prose. Never copy another plugin's text wholesale into shipped kit content.

## The provenance gate for capability work

Every capability built from external material (PDF ingests, reference-manager sync, the physics/math
capability library, user drop-ins) passes through the knowledge base's existing source-keying. No new
machinery, and no exceptions:

1. **Every capability skill is keyed to a real citation** — a resource `@key` in the knowledge-base
   registry, with full provenance (source, author, date, *how obtained*) recorded at ingest.
2. **The provenance is surfaced to the user**, not buried. A capability answers *"per `@key`"*, so the
   user knows whose method they are using and can go to the source.
3. **Verbatim material is minimal and attributed** — a brief quote with attribution where the exact
   wording matters, or nothing. Figures and long passages are never reproduced; they are cited.
4. **The citation is real** — it resolves to the actual paper claimed (`/physkit:cite-check`). A
   capability keyed to an unverifiable citation is not shippable.

## Pre-ship checklist

Before any capability, or the library, ships or is monetized, every box checks:

- [ ] Every capability keyed to a real, resolvable citation — `cite-check` passes on the set.
- [ ] No verbatim copyrighted text beyond brief, attributed quotes; no reproduced figures.
- [ ] No ported code: every implementation traceable to cited principles (paper or spec), and its
      provenance says which; any consulted package used only as an independent check, and named.
- [ ] Every borrowed scaffold, template, or prompt pattern license-checked, with attribution where
      required.
- [ ] No content derived from a source of unclear or illegitimate provenance: the *how obtained* field is
      filled and clean for every ingested source involved.
- [ ] The cite-and-adapt-only posture confirmed by a human before monetizing.

## Pointers

The knowledge base's own rules govern the ingest half: provenance mandatory at ingest, raw sources
immutable, *how obtained* recorded by the ingest procedure. `/physkit:cite-check` confirms every key
resolves to the paper claimed. The registry-to-bibliography export keeps `@keys` honest. A human confirms
the cite-and-adapt-only posture before anything built this way ships or is monetized.
