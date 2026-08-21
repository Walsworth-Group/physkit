---
name: new-project
description: >-
  Scaffold a PROJECT — the home for a whole investigation into one physical system, above individual campaigns.
  EVERY campaign lives in one, so this runs on the default path: `new-campaign` invokes it automatically
  whenever no project home exists. Use it directly when the user starts a new line of research, or when lifting
  a legacy bare campaign into a home: phrasings like "start a new project", "set up the ASI investigation",
  "make a home for this whole line of work", "we'll have several campaigns on this system".
  It interviews for the physical system, end goal, and the CANONICAL shared data + background knowledge, then
  generates the project tree: a short README.md front door, PROJECT.md — THE overview (mission, the
  §Standing constraints every campaign delivers into its spawned prompts, system knowledge, durable
  decisions, and §Lineage, the index of every attempt), a project CLAUDE.md, data/ or a data pointer, and
  campaigns/, sessions/, reports/ — so that every future campaign shares one data copy by relative path and
  every version/finding is indexed in one place. Composes new-campaign for the first campaign. NOT for
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

A one-off project costs three near-empty documents; the physics, conventions, and instrument knowledge
lives once in `PROJECT.md` rather than multiplying. A sibling campaign, a fork, or an ad-hoc session can
be added later with no reorganization and no path rewrites.

## Interview (gather, don't assume)
1. **Physical system & end goal** — what system, what decision the investigation serves, what "done" looks like.
2. **Canonical data** — where the experimental/reference data lives. If it is large or already on disk, keep it
   out of the tree and record a `data_path` pointer; else place a read-only copy at `data/`. Data is never
   copied per-campaign; one copy referenced by relative path prevents duplication and broken paths.
3. **Shared physics / conventions / system params** — the facts every campaign inherits
   (→ `PROJECT.md`'s knowledge sections), and which of them are *standing constraints*: the hard rules a run
   must obey (inventory tags, a-priori bound, sign/unit/frame conventions, run-constraining rig parameters),
   which the campaign driver delivers into every spawned prompt.
4. **First campaign** — the initial attempt (its goal + frozen metric); scaffolded via `new-campaign` (below).

## Generate the project tree
Copy from `${CLAUDE_PLUGIN_ROOT}/templates/project/`, strip `.tmpl`, fill placeholders:
```
<project>/
├── README.md           # the front door: a very short "where to find things" map — nothing deeper
├── PROJECT.md          # THE overview: §Mission · §Standing constraints (driver-delivered) · system
│                       #   knowledge · §Updates from discoveries · §Durable decisions · §Lineage (the
│                       #   index of every campaign & session; schema inside)
├── CLAUDE.md           # project always-on rules (structure · reference-never-copy · the edit tiers)
├── data/               # canonical data (read-only) + README; OR a DATA_PATH.txt pointer — NEVER written by the loop
├── campaigns/          # each campaign lives here (new-campaign generates into it)
├── sessions/           # ad-hoc / non-campaign sessions — each a <date>_<slug>/ with a NOTES.md
└── reports/            # one project-level outputs location (+ README)
```
Promoted shared artifacts get flat, purpose-named project-level dirs (`scripts/`, `models/`,
`datasets/`, …) **created on demand at the first promotion, never pre-created empty**. A promoted
artifact is versioned and carries a `PROJECT.md` §Lineage promotion line — that line, not a
directory name, is what marks it promoted-frozen (project `CLAUDE.md` rule 6).

- **Author `PROJECT.md`** — the one overview, ordered for a first read. Fill §Mission (goal, decision
  served, done-criteria, project-wide invariants, the data location/pointer) and the knowledge sections
  (target of study, predictive framework, instrument, equations and methods) from the interview. Fill its
  **§Standing constraints** with care and keep it lean: the campaign driver delivers that section into
  every spawned prompt, every cycle; depth belongs in the sections below it. Leave §Updates from
  discoveries and §Lineage as their seeded empty forms. **Preserve the edit-tier comment banners** — the
  OPEN/GUARDED split (mirrored as project `CLAUDE.md` rule 7) is what lets future agents update the
  overview without eroding the signed-off core.
- **Keep `README.md` short.** It is the map for someone unfamiliar — what campaigns and sessions are,
  where the data and promoted artifacts live — pointing at `PROJECT.md` for everything deeper. The map
  lives there ONLY; do not restate it in `PROJECT.md`.
- **Data home (copy the README; decide copy vs pointer).** Copy `data/README.md` (the read-only,
  referenced-never-copied rule). Then, from interview topic 2: if the canonical data is on-tree, place the
  read-only files in `data/`. If it lives off-tree (large, or already on a lab store), do not copy it: write
  `data/DATA_PATH.txt` with one line, the absolute path, and record the same `data_path` in `PROJECT.md`
  §Mission. That pointer is the project's only absolute path.
- **Sessions & reports scaffolding.** `sessions/` starts empty. Each later ad-hoc session gets its own
  `sessions/<YYYY-MM-DD>_<slug>/NOTES.md` authored from `${CLAUDE_PLUGIN_ROOT}/templates/project/sessions/NOTES.md.tmpl`;
  do not pre-create empty session folders. Copy `reports/README.md` (the single outputs location).
- **Relative paths only.** Campaigns reference `../../data` and the promoted dirs (`../../scripts`, …), so
  the whole tree relocates as one unit. The only absolute path allowed is the resolved `data_path` pointer,
  documented in `PROJECT.md` §Mission.
- **Strip `.tmpl` on write.** Fill every `{{PLACEHOLDER}}`; run the validator when done.

## Then the first campaign
If `new-campaign` called you, return to it; it scaffolds the campaign under `campaigns/` itself. If the user
came here directly, invoke `new-campaign` to scaffold the first campaign, wired to `../../data`, and append
its opening row to `PROJECT.md` §Lineage. Either way, do not duplicate the interview: carry over what was
gathered here.

## Verify
Run the bundled validator on the project root (it auto-detects project vs campaign trees, and old- vs
new-layout projects) and fix anything it flags:
```
python "${CLAUDE_PLUGIN_ROOT}/skills/new-campaign/scripts/validate_campaign.py" <project_root>
```
It checks the required project files/dirs, that `PROJECT.md` carries its `## Standing constraints`
section (what the campaign driver delivers into every spawned prompt) and its `## Lineage` tables, no
leftover `{{…}}` in the project docs, that every campaign under `campaigns/` (incl. `_archive/`) is
indexed in §Lineage, that no campaign carries a local copy of the overview (referenced-never-copied),
and that no config hard-codes an absolute path (portability).
Then also confirm:
- `data/` is a read-only canonical copy or a `DATA_PATH.txt` pointer — not a per-campaign copy — and carries its README.
- `campaigns/`, `sessions/`, `reports/` exist (`reports/README.md` present); no empty pre-created
  purpose dirs.
- No stray reference to a retired doc the tree does not hold (`PROJECT_ORIENTATION.md`, `LINEAGE.md`,
  `DISCOVERIES.md`, `shared/`, `SYSTEM.md`, a project-root `ENGINEERING_NOTES.md`): all of it lives in
  `PROJECT.md` now, one section each — except verified findings, which live in the campaigns that
  produced them, pointed at from §Lineage and §Updates from discoveries (ADR-0015).
- Report the project root, the data decision (copy vs pointer), and the first campaign created.

## Composition
Composes `new-campaign` (first and subsequent campaigns) and `fork-campaign` (invalidation forks).
