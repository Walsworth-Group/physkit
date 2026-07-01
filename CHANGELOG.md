# Changelog — physkit

All notable changes to the kit are recorded here. Format follows
[Keep a Changelog](https://keepachangelog.com/); the kit version lives in `.claude-plugin/plugin.json`.

Dates are UTC. Each entry cites the run/finding that motivated it (the kit's own
`campaign-review → improve-kit` loop) so a future reviewer can trace the "why".

## [Unreleased]

_Nothing yet._

## [0.5.0] — 2026-06-30

### Added
- **`CHANGELOG.md`** (this file) — a running, human-readable kit change log.
- **Scoreboard comparability columns** — `metric_version` and `data_version` added to
  `templates/campaign/results/scoreboard.tsv.tmpl`, with a comparability rule (a "current best" is valid only
  *within* one `(metric_version, data_version)` pair; re-score across versions). Threaded into
  `program.md.tmpl` (Logging Protocol + promotion rule), `new-campaign` (column list), and a
  `campaign-status` hygiene check. *(keeper C2)*
- **DISCOVERIES retraction/supersession convention** — `templates/campaign/results/DISCOVERIES.md.tmpl` now
  carries an append-only `REVISES Dn` convention so a reversed finding is corrected *in the same file*, never
  only in a side note. *(keeper C1)*
- **Frozen-≠-validated gate** — `correctness-suite` and `simulation-design` now require a **sign/convention
  round-trip vs a trusted analytic reference + symmetry self-tests** to pass *before* a forward model / data
  generator / scorer is frozen; `program.md.tmpl` FROZEN section states "frozen means locked, not correct"
  and makes an unphysical symptom a trigger to re-verify the frozen infra first. *(keeper B1)*
- **Verify-gate enforcement** — `program.md.tmpl` makes independent verification a named, enforced promotion
  step that also covers scoreboard *current-best* promotion (not only DISCOVERIES writes); `campaign-status`
  now asserts the `guard_discoveries` hook is actually wired and flags a current-best/DISCOVERY row with a
  blank `verified` column; `new-campaign` + the guard hook's docstring document that imported/relocated trees
  lose the gate and must be re-wired. *(keepers A1+A2)*
- **Ledger-hygiene gates** — a "no orphaned result (every row has a written narrative AND a graded verdict)"
  check in `campaign-status` + the checkpoint protocol + `handoff`; and `handoff` must scan recent session
  transcript(s) for artifacts written *outside* the campaign root before asserting a deliverable "wasn't
  done". *(keepers D1+D2)*

### Changed
- **Closed the review→improve loop** — `campaign-review` now mirrors its keepers into a tracked intake table
  in `synthesis/BUILD_BACKLOG.md`, and `improve-kit` marks each keeper `applied`/`rejected` with a commit.
  This fixes the leak where a prior review's keepers were never folded in and the same bugs recurred.
  *(keeper G1; campaign-review + improve-kit are dev-only skills in the workspace `.claude/skills/`)*

### Provenance
- All of the above were harvested by the kit's own `campaign-review` run over the archived transcript corpus
  (Magnetic inverse loop v3/v4, ASI sims v1/V2, ASI fit 3, + misc), 2026-06-30. Full evidence-cited report:
  `case-studies/transcript_review_2026-06-30.md`. Remaining keepers are queued in the
  `synthesis/BUILD_BACKLOG.md` intake table (C3, B2–B4, E1–E2, F1–F5, G2–G3).
- Honesty/verification/metric-integrity core unchanged except to **tighten** enforcement — the one direction
  self-improvement is permitted to move it.

---

## [0.4.0] and earlier
Tracked in the per-file `## Changelog` sections (`docs/PRINCIPLES.md`, `docs/DOCTRINE_INDEX.md`) and the git
history of this repo (e.g. `physkit` rename, always-on `CLAUDE.md` + verify-before-DISCOVERIES gate,
model-tiering guidance). This top-level CHANGELOG begins at the Unreleased entry above.
