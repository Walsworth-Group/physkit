---
id: version-control
kind: reference-doc
layer: shared
load: on-demand
load_trigger: When a project uses (or should consider) git — branch/commit etiquette, .gitignore, archive-don't-delete. Conditional, not day-one mandatory.
frozen: false
review: living
---

# Version control — *if* this project uses git

Git is recommended, not mandatory. Full reproducibility is mandatory: for every experiment, the
documentation of what was done and the exact code plus data to redo it, preserved and self-contained. The
kit meets that baseline with per-experiment snapshots. A `results/snapshots/<label>/` directory holds the
config and the mutable code for each run; snapshots work with or without git and preserve superseded code.
Git is a good addition when it earns its keep. This doc covers how to use it well when you do, and how to
meet the reproducibility bar when you don't.

## When git earns its keep (and when it doesn't)
- **Use it** for shared or collaborative projects, anything large or long-lived, code with a meaningful
  change history, or when you want cheap branching to explore.
- **Skip it** (snapshots suffice) for a small solo analysis, a one-off computation, or throwaway
  exploration. The reproducibility invariant holds either way; the mechanism is the project's choice.
- Either way, the per-experiment snapshot is the primary reproducibility record. Git complements it and
  does not replace it.

## If you use git — etiquette
- **Commit code and configs together** so every result is pinned to the exact code that produced it, not
  just to its parameters. Without this, a later edit to a shared decoder or forward model makes an old
  result silently non-reproducible.
- **`.gitignore` the right things:** large data, generated artifacts (trained models, datasets, figures),
  caches, secrets, and environment dirs. Pin large or external data by source, checksum, generation
  command, and seed instead of committing it (see reproducibility below).
- **Branch for exploratory directions** and keep `main` in a working state. Small, frequent, descriptive
  commits beat giant ones; the history is part of the record.
- **Tag or record the commit hash** alongside each promoted result, so the result points to its exact code
  state.
- **Archive, don't delete.** Superseded code and approaches are part of the scientific record. Move them to
  a branch, an `archive/` dir, or a snapshot rather than erasing them. The same archive-don't-delete
  discipline governs handoffs and disputes.

## Reproducibility without git (the snapshot baseline)
Met by every experiment, not just promoted ones:
- **Per-experiment snapshot:** copy the config and the mutable code that produced the result into
  `results/snapshots/<label>/`. It must be self-contained: a reader can rerun from it alone.
- **Pin input data:** record its source and a checksum. For generated data, pin the exact generation
  command and seed.
- **Log the environment:** library versions, host, RNG seeds, command line, wall-clock; tee stdout to a log.
- **Separate config from code:** one config file per experiment, as data rather than edited source lines.

A result is not saved until both the how-to-redo (code, config, data provenance) and the what-happened
(documentation and the quicker-check artifacts) exist, with or without git.

## Pointers
CORE constitution and working-loop step 6 (reproducibility is mandatory; git optional); the campaign `roles/worker.md` save-set
(snapshot convention); `handoff` (archive-don't-delete); `record-decision` (why a non-obvious VC choice).
