---
id: version-control
kind: reference-doc
layer: shared
load: on-demand
load_trigger: When a project uses (or should consider) git — branch/commit etiquette, .gitignore, archive-don't-delete. Conditional, not day-one mandatory.
frozen: false
addresses: [7]
status: new
review: living
---

# Version control — *if* this project uses git

Git is **recommended, not mandatory.** What is mandatory is **full reproducibility** — for every
experiment, the documentation of what was done *and* the exact code + data to redo it, preserved and
self-contained. The kit achieves that baseline with **per-experiment snapshots** (a `results/snapshots/
<label>/` holding the config + mutable code for each run), which work with or without git and also preserve
superseded code for free. Git is a good *addition* when it earns its keep; this doc is how to use it well
when you do — and how to meet the reproducibility bar when you don't.

## When git earns its keep (and when it doesn't)
- **Use it** for shared/collaborative projects, anything large or long-lived, code with a meaningful change
  history, or when you want cheap branching to explore. The cost is low and the safety net is real.
- **Skip it (snapshots suffice)** for a small solo analysis, a one-off computation, or throwaway
  exploration — don't impose ceremony that adds work without payoff. This is a deliberate downgrade from
  "git from day one": the reproducibility *invariant* stays; the *mechanism* is the project's choice.
- Either way, **the per-experiment snapshot is the primary reproducibility record** — git complements it,
  it doesn't replace it.

## If you use git — etiquette
- **Commit code *and* configs together** so every result is pinned to the exact code that produced it — not
  just its parameters. A later edit to a shared decoder/forward model otherwise makes an old result
  silently non-reproducible.
- **`.gitignore` the right things:** large data, generated artifacts (trained models, datasets, figures),
  caches, secrets, and environment dirs. Pin large/external data by **source + checksum + generation
  command + seed** instead of committing it (see reproducibility below).
- **Branch for exploratory directions**; keep `main` in a working state. Small, frequent, descriptive
  commits beat giant ones — the history is part of the record.
- **Tag or record the commit hash** alongside each promoted result, so the result points to its exact code
  state.
- **Archive, don't delete.** Superseded code/approaches are part of the scientific record — move them aside
  (a branch, an `archive/` dir, or a snapshot) rather than erasing them. The same archive-don't-delete
  discipline governs handoffs and disputes.

## Reproducibility without git (the snapshot baseline)
Met by **every** experiment, not just promoted ones:
- **Per-experiment snapshot:** copy the config + the mutable code that produced the result into
  `results/snapshots/<label>/`. Self-contained — a reader can rerun from it alone.
- **Pin input data:** record its source and a **checksum**; for generated data, pin the exact generation
  command + seed.
- **Log the environment:** library versions, host, RNG seeds, command line, wall-clock; tee stdout to a log.
- **Separate config from code:** one config file per experiment (data, not edited source lines).

A result is not "saved" until both the *how-to-redo* (code + config + data provenance) and the
*what-happened* (documentation + the quicker-check artifacts) exist — git or no git.

## Pointers
PRINCIPLES Context 7 (reproducibility is mandatory; git optional); the campaign `artifacts.md` protocol
(snapshot convention); `handoff` (archive-don't-delete); `record-decision` (why a non-obvious VC choice).
