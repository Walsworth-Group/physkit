---
name: new-project
description: >-
  Scaffold a PROJECT — the home for a whole investigation into one physical system, above individual campaigns.
  EVERY campaign lives in one, so this runs on the default path: `new-campaign` invokes it automatically
  whenever no project home exists. Use it directly when the user starts a new line of research, or when lifting
  a legacy bare campaign into a home: phrasings like "start a new project", "set up the ASI investigation",
  "make a home for this whole line of work", "we'll have several campaigns on this system".
  It interviews for the physical system, end goal, and the CANONICAL shared data + background knowledge, then
  generates the project tree (PROJECT.md charter, PROJECT_ORIENTATION.md — the ONE background document, whose
  §Standing constraints every campaign delivers into its spawned prompts — LINEAGE.md index, data/ or a data
  pointer, shared/, campaigns/, sessions/, reports/, and a project CLAUDE.md) so that every future campaign
  shares one data copy by relative path and every version/finding is indexed in one place. Composes
  new-campaign for the first campaign. NOT for
  a single campaign inside an existing project (that is new-campaign), nor for ad-hoc work (that is a session —
  see the project CLAUDE.md).
---

# new-project — the home for a whole investigation

A **Project** is one physical system investigated over many **Campaigns** (versioned attempts) and **Sessions**
(ad-hoc work). It exists so shared data and docs live once, referenced by relative path and never copied, and
so "what each version changed and found" lives in one index. Read `docs/PRINCIPLES.md` §1 for the interview
stance.

## Every campaign lives in a project — there is no bare-campaign mode
Two entry paths: directly, when the user starts a new line of research, or from `new-campaign`, whose
Step 0.1 found no project home. When called from `new-campaign`, the interview below is largely answered
already: carry those answers in, fill the tree, and return. Do not call back into `new-campaign`; it is
mid-run and resumes on its own.

A one-off project costs about five near-empty files; the physics, conventions, and instrument knowledge
lives once in `PROJECT_ORIENTATION.md` rather than multiplying. A sibling campaign, a fork, or an ad-hoc
session can be added later with no reorganization and no path rewrites.

## Interview (gather, don't assume)
1. **Physical system & end goal** — what system, what decision the investigation serves, what "done" looks like.
2. **Canonical data** — where the experimental/reference data lives. If it is large or already on disk, keep it
   out of the tree and record a `data_path` pointer; else place a read-only copy at `data/`. Data is never
   copied per-campaign; one copy referenced by relative path prevents duplication and broken paths.
3. **Shared physics / conventions / system params** — the facts every campaign inherits
   (→ `PROJECT_ORIENTATION.md`), and which of them are *standing constraints*: the hard rules a run must
   obey (inventory tags, a-priori bound, sign/unit/frame conventions, run-constraining rig parameters),
   which the campaign driver delivers into every spawned prompt.
4. **First campaign** — the initial attempt (its goal + frozen metric); scaffolded via `new-campaign` (below).

## Generate the project tree
Copy from `${CLAUDE_PLUGIN_ROOT}/templates/project/`, strip `.tmpl`, fill placeholders:
```
<project>/
├── PROJECT.md          # charter: what we are trying to achieve · project-wide invariants · data pointers
├── PROJECT_ORIENTATION.md # what we know about the system — the ONE background document (see below)
├── LINEAGE.md          # the index — what has been done: Campaigns + Sessions tables (schema inside)
├── DISCOVERIES.md      # project-wide VERIFIED findings (promoted from campaigns; survive fork-and-archive)
├── CLAUDE.md           # project always-on doctrine (structure + the shared-data/session rules)
├── data/               # canonical data (read-only) + README; OR a DATA_PATH.txt pointer — NEVER written by the loop
├── shared/             # promoted frozen artifacts a campaign froze for its siblings (starts empty)
├── campaigns/          # each campaign lives here (new-campaign generates into it)
├── sessions/           # ad-hoc / non-campaign sessions — each a <date>_<slug>/ with a NOTES.md
└── reports/            # one project-level outputs location (+ README)
```
- **Author `PROJECT_ORIENTATION.md`** from `${CLAUDE_PLUGIN_ROOT}/templates/project/`: the governing
  physics (with the target-of-study and physics-inventory sections), the units/signs/frames conventions,
  the measurement rig and its parameters, and the durable project-level decisions — one document, one
  section each. Fill its **§Standing constraints** with care and keep it lean: the campaign driver
  delivers that section into every spawned prompt, every cycle; depth belongs in the sections below it.
  Seed empty `DISCOVERIES.md` (project-wide verified findings, promoted from campaigns) from its template.
- **Data home (copy the README; decide copy vs pointer).** Copy `data/README.md` (the read-only,
  referenced-never-copied rule). Then, from interview topic 2: if the canonical data is on-tree, place the
  read-only files in `data/`. If it lives off-tree (large, or already on a lab store), do not copy it: write
  `data/DATA_PATH.txt` with one line, the absolute path, and record the same `data_path` in `PROJECT.md`.
  That pointer is the project's only absolute path.
- **Sessions & reports scaffolding.** `sessions/` starts empty. Each later ad-hoc session gets its own
  `sessions/<YYYY-MM-DD>_<slug>/NOTES.md` authored from `${CLAUDE_PLUGIN_ROOT}/templates/project/sessions/NOTES.md.tmpl`;
  do not pre-create empty session folders. Copy `reports/README.md` (the single outputs location).
- **Relative paths only.** Campaigns reference `../../data` and `../../shared`, so the whole tree relocates as
  one unit. The only absolute path allowed is the resolved `data_path` pointer, documented in `PROJECT.md`.
- **Strip `.tmpl` on write.** Fill every `{{PLACEHOLDER}}`; run the validator when done.

## Then the first campaign
If `new-campaign` called you, return to it; it scaffolds the campaign under `campaigns/` itself. If the user
came here directly, invoke `new-campaign` to scaffold the first campaign, wired to `../../data` and
`../../shared`, and append its opening row to `LINEAGE.md`. Either way, do not duplicate the interview: carry
over what was gathered here.

## Verify
Run the bundled validator on the project root (it auto-detects project vs campaign trees) and fix anything it flags:
```
python "${CLAUDE_PLUGIN_ROOT}/skills/new-campaign/scripts/validate_campaign.py" <project_root>
```
It checks the required project files/dirs, that `PROJECT_ORIENTATION.md` exists and carries its
`## Standing constraints` section (what the campaign driver delivers into every spawned prompt), no
leftover `{{…}}` in the project + `shared/` docs, that every campaign under `campaigns/` (incl.
`_archive/`) is indexed in `LINEAGE.md`, that no campaign carries a local copy of the background doc
(referenced-never-copied), and that no config hard-codes an absolute path (portability).
Then also confirm:
- `data/` is a read-only canonical copy or a `DATA_PATH.txt` pointer — not a per-campaign copy — and carries its README.
- `shared/`, `campaigns/`, `sessions/`, `reports/` exist (`reports/README.md` present).
- No stray reference to a retired doc the tree does not hold (`SYSTEM.md`, `shared/PHYSICS.md`,
  `shared/CONVENTIONS.md`, `shared/INSTRUMENT.md`, a project-root `ENGINEERING_NOTES.md`): all of it
  lives in `PROJECT_ORIENTATION.md` now, one section each.
- Report the project root, the data decision (copy vs pointer), and the first campaign created.

## Composition
Composes `new-campaign` (first and subsequent campaigns) and `fork-campaign` (invalidation forks).
