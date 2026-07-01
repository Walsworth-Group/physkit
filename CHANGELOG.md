# Changelog — physkit

All notable changes to the kit are recorded here. Format follows
[Keep a Changelog](https://keepachangelog.com/); the kit version lives in `.claude-plugin/plugin.json`.

Dates are UTC. Each entry cites the run/finding that motivated it (the kit's own
`campaign-review → improve-kit` loop) so a future reviewer can trace the "why".

## [Unreleased]

Second batch of keepers from the 2026-06-30 transcript review (`case-studies/transcript_review_2026-06-30.md`),
plus the first improvements harvested from the Wieman 29-decisions map (`synthesis/WIEMAN_DECISIONS_MAP.md`).
Each tightens the frozen honesty/verification core; none weakens it.

### Skills & framing (from the Wieman 29-decisions map)
- **New general skill `assess-idea`** (Wieman decision 9): honest feasibility/worth triage of a research idea
  *before* committing — bounds it a priori, locates the crux + cheapest de-risking check, weighs worth, and
  returns GO / DE-RISK-FIRST / NO-GO with confidence + assumptions. The anti-hype counterpart to `verify`
  (licensed to say "no"). Standalone, and an **advisory** (never-blocking) pre-check composable by
  `new-campaign`. Registered in `DOCTRINE_INDEX` / `CORE` routing / `GETTING_STARTED`. *(Front-end cluster
  piece 1 of 3.)*
- **New general skill `literature-review`** (Wieman decisions 1, 7): survey a field honestly — trajectory,
  closest prior art, and the methods that *transfer* to your problem — **self-contained** (no `deep-research`
  dependency, for frictionless adoption), arXiv-first, with a **mandatory `cite-check` gate** so no fabricated
  reference survives; campaign-aware (writes `LITERATURE.md`, seeds `PHYSICS.md`). *(Front-end cluster piece
  2 of 3; `research-direction` deferred — see `synthesis/FRONT_END_CLUSTER_DESIGN.md`.)*
- **Predictive framework (W-PF)** made a first-class output of `frame-problem` (the mechanism + discriminating
  thought-experiments at a justified complexity) with a `PHYSICS.md` "Predictive framework" section; its
  revision log = the existing "Updates from discoveries" (placement provisional). Unifies Wieman decisions
  5, 8, 19, 20, 23.
- **Confirmation-bias reflection ritual (W-reflect)** — Wieman's reflection decisions 23–26 ("most important
  and hardest"): a `verify` §5c ritual (state the hoped-for answer → argue it's wrong → name the refuting
  observation → hear the resisted alternative), echoed in `campaign-status` and `program.md`; plus a
  **non-count reflection trigger** (reflect on surprise / plateau / before a stop / on wall-clock, not only
  every N experiments).
- **Front-end / reflection refinements (Wieman 7, 8, 12, 14, 27)** — `frame-problem` flags the
  crux/highest-uncertainty sub-steps with an acceptable-uncertainty bar (W-12) and enumerates candidate
  approaches before committing (W-8); `campaign-status` re-plan prioritizes directions by importance ×
  tractability × cost (W-14); `final-report` gains a "Broader implications & significance" section and the
  `DISCOVERIES` entry template an Implications line (W-27); `program.md` "idea sources" now captures the
  transferable method/analogy from a related solved problem (W-analogy). Closes out the applyable-anytime
  Wieman keepers.

### Added
- **Machine-checkable `tier` field** (Scout/Confirmation/Extended) on every JOURNAL and scoreboard row, so
  run-length cap-compliance stays auditable and can't silently drop off later entries. *(D3)*
- **Wall-clock liveness self-check** for long runs in `expensive-evaluation.md.tmpl` — arm a monitor for any
  run >~30–60 min (verify process alive AND log advancing; a stalled log is a dead run), don't wait to be
  asked. *(E1)*
- **"Known landmines / Do-not-repeat" block** in `ENGINEERING_NOTES.md.tmpl` — a pre-flight checklist
  re-checked before any matching action (GPU/detached/irreversible) and surfaced to the user before
  complying. *(E2)*
- **Environment-pitfalls guidance** (Windows MAX_PATH → short venv paths + `core.longpaths`, `py -3.x` not
  `python3`, shared-drive symlink limits) in `CONVENTIONS.md.tmpl` and `INSTALL_FOR_TESTERS.md`. *(F5/env)*
- **`verify` §5b — provenance, authority, and irreversible actions**: resolve conflicting facts to the
  highest-authority artifact (a derived statistic is weaker than its source); a fact acted on at
  INFERRED/RECALLED is a claim to falsify; an irreversible action needs a CONFIRMED diagnosis. *(F1, F2, B4)*

### Changed
- **Degenerate-regime check** before writing off an idea (`program.md.tmpl`, `model-selection`): a null
  measured where competing hypotheses are indistinguishable proves nothing. *(C3)*
- **Frozen-infrastructure debugging**: an unphysical symptom (sign flip, mirrored artifact, structured
  residual) now triggers re-verifying the FROZEN forward model/generator *first* — threaded into the `debug`
  gotcha catalog and `frame-problem`'s "keep it living" (a persistent gap can be a bug in reference code, not
  only model-form error). *(B2)*
- **Promotion validates upstream preprocessing** (registration/pose/normalization must be non-degenerate on
  the data it's applied to) in the checkpoint promotion checks and `verify`'s code-soundness step. *(B3)*
- **No INFERRED→PINNED without a falsification attempt** (especially when a cheaper discriminator exists) in
  `program.md.tmpl`'s operating stance and `verify`. *(B4)*
- **Static-check-before-expensive-run** worked example (φ-scan artifact) added to `program.md.tmpl`'s
  a-priori section. *(E3)*
- **`debug`**: exhaust existing evidence (logs/recorded state) before building a reproduction harness; and
  installed tooling must be verified non-intrusive. *(F4)*
- **`handoff` + `GETTING_STARTED`**: flush converged designs/plans to a file at decision-lock points, not
  session end. *(F3)*

### Principles (doctrine)
- **New Context 9 · "Operating unattended"** in `docs/PRINCIPLES.md` (+ always-on essence in `docs/CORE.md`
  "Running unattended", coverage in `docs/DOCTRINE_INDEX.md`, and the paper master
  `synthesis/PRINCIPLE_TAXONOMY.md`): **don't stop prematurely** (a "done/ceiling/blocked" conclusion is a
  load-bearing claim, refuted like a positive result), autonomous-but-safe escalation, CONFIRMED-diagnosis
  before an irreversible action, monitor-long-runs (a stalled log is a dead run), persist hazards/decisions
  when they lock, enforce-don't-exhort, and every-human-correction-is-a-scaffolding-gap.
- **Enforcement of "don't stop prematurely"** threaded into `program.md.tmpl` (Getting Unstuck), `verify`
  (a ceiling/blocked claim is a load-bearing claim to refute; unfalsified ⇒ INCONCLUSIVE), and
  `campaign-status` (flags a premature "done/blocked" as a resume signal).
- **Additions to existing contexts** (all from the 2026-06-30 review): comparability-is-honesty +
  record-carries-its-own-corrections (Ctx 1); validate-before-you-freeze + unphysical-symptom-implicates-
  infrastructure (Ctx 2); exhaust-existing-evidence-before-a-repro-harness (Ctx 3); discriminate-where-
  hypotheses-diverge + sharpened anchoring (Ctx 4); result-not-saved-until-verdict + reconstruct-from-full-
  trail (Ctx 7).

_Deferred / deliberate:_ multi-track campaign support (G2 branching + G3 cross-linked FROZEN/MUTABLE) is
scoped as one workstream in `synthesis/BUILD_BACKLOG.md`; the stale-archive-digest flag (archive) stays queued.
Ctx 9's overlap with Contexts 7–8 (organization) is flagged for a later editorial pass.

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
