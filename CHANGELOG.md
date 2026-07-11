# Changelog — physkit

All notable changes to the kit are recorded here. Format follows
[Keep a Changelog](https://keepachangelog.com/); the kit version lives in `.claude-plugin/plugin.json`.

Dates are UTC. Each entry cites the run/finding that motivated it (the kit's own
`campaign-review → improve-kit` loop) so a future reviewer can trace the "why".

## [0.6.0] - 2026-07-11

### Added — assumption-audit skill + prompt-surface-audit doctrine (lab-loop keepers, 2026-07-07)

- **`skills/assumption-audit` (new).** The plateau mode-change from optimizer to diagnostician: when
  one-lever experiments across ≥2 lever families pin at the same floor (or the best result sits far from
  its own a-priori expectation), the stall may live *upstream* of every lever in a wrong **inherited**
  value — a calibration, a derived quantity, or a classification that every experiment silently carries.
  The skill enumerates the inheritance with provenance tags, ranks suspects by
  would-being-wrong-reproduce-this-stall, and buys ONE discriminating experiment under two hard clauses:
  **solve, don't confirm** (the test estimates the suspect value from scratch; a consistency check invites
  reading a mismatch as an artifact) and **operating-point validity** (re-derive any calibration crossing
  an operating-point boundary — a falsification run with an out-of-point calibration can refute a *true*
  hypothesis). Wired into the charter's *Getting Unstuck* block (third bullet) and `campaign-status` §4
  re-plan as the response to a plateau that *resists* lever escalation — the gap being that all previously
  prescribed plateau responses were pivot-escalation (change lever), none a change of *mode* (question
  assumptions) — `pivoting.md` gains the fifth diagnosis row (**Inherited-value-wrong**) and CORE's
  "plateau is a pivot signal" line gains the second species (frozen-doc sign-off = this PR's review).
  Motivation: a hardware-commissioning loop (2026-07) miscounted the lines of a resolved spectral pattern
  (read from memory of the canonical case rather than from the data), inherited a detection frequency a
  few kHz off from it, and pinned dozens of one-lever arms at the same SNR floor while its own signal sat
  in the data — it even ran the right discriminating measurement, framed as *confirmation* of the
  incumbent value, and read the mismatch as an artifact.
- **`docs/reference/prompt-surface-audit.md` (new) + a Ctx9 PRINCIPLES bullet (tightening; frozen-core
  sign-off = this PR's review).** Doctrine only governs an agent whose RENDERED context contains it:
  subagent prompts *replace* the doctrine stack (inherit nothing from CLAUDE.md), SDK-spawned loop roles
  may load no always-on files, and **dynamically rendered** surfaces (observation digests) are part of
  the prompt surface — auditable both for missing doctrine and for stowaway contamination. The audit:
  enumerate roles → list relied-upon rules per role → capture each context *as rendered* → grep for every
  rule → gate the launch on it, re-running after any prompt change. `new-campaign` Step 5 gains the
  launch-checklist bullet and `campaign-status` §2 the matching hygiene check. The Ctx9 principle is
  recorded as PRINCIPLES v1.9; **propagation to the content master (taxonomy) is pending** per the
  derivation note. Motivation (2026-07, same program): two disciplines the designers relied on
  were simply absent from an SDK loop's rendered prompts (each hole cost real instrument time), and a
  static-file leak audit stayed green for two full campaign arms while a dynamically rendered digest
  carried a stale false fact into every round.

### Changed — abstract-only reading discipline: conclude on full text, not the abstract (B5, 2026-07-05)

- **`skills/cite-check` now separates *existence* from *claim-support*.** Confirming a paper exists and its
  metadata may use the abstract page; confirming it **supports the claim** must read the relevant full-text
  section. Support established only from an abstract is a new **PROVISIONAL** grade (flagged
  `read: abstract-only`) that cannot alone carry a claim to "well-evidenced," and every verdict records its
  read-depth. **`skills/literature-review`** gains *screen on abstracts, conclude on full text* plus two
  failure-mode guards — **abstract-driven conclusions** and **confirmation-seeking search** (a paper that
  complicates or refutes the sought claim is a successful result, not a failed row). **`report`/`final-report`**
  thread the PROVISIONAL grade so abstract-only support is carried provisionally, never laundered into
  "established." Motivation: a testing session where the agent gave a ~90%-right reading of an arXiv *abstract*
  then reversed once the full paper loaded (`@meeting_agentic_2026-07-02a` 01:22:01→01:22:28), corroborated by
  three papers ingested as pillar support that a full read showed *complicate* the claim
  (`LIT_SEARCH_BACKLOG.md` item 14). Maintainer-side (KB) companions: a `Read status` field in the resource
  registry + `add-new-resource` / `ingest-transcript`. (User-approved, 2026-07-05.)

### Changed — unified always-on spine: CORE.md is now the single source; CLAUDE.general.md retired (2026-07-03)

- **`templates/CLAUDE.general.md` deleted; `docs/CORE.md` is the one spine.** Motivation: in plugin-only
  mode a doc read once falls out of context over a long session, while CLAUDE.md content is re-injected
  every turn — and maintaining the template as a separate copy had already let the two drift apart. Users
  now make the spine always-on with a one-line import in their project `CLAUDE.md`
  (`@<kit>/docs/CORE.md`), or by copying CORE's body (fallback). `GETTING_STARTED.md` §1,
  `INSTALL_FOR_TESTERS.md` Step 1, and the `DOCTRINE_INDEX` row updated. (User finding + decision,
  2026-07-03.) CORE also gained: the **universalism** constitution bullet extended with the concise
  **literature-disagreement weighing rule**; a **traceability** constitution bullet (a result isn't real
  until recorded and reproducible; provenance never fabricated); **pass-the-why** in the loop's delegation
  step; and the restored **register-vs-facts** line in Honest reporting.
- **CORE working-loop additions (2026-07-04, user-approved):** Frame step += **check what already exists**
  (prior runs, repo artifacts, literature) and **settle statically-answerable questions before an
  expensive run** — an environment check (is there actually a GPU, and is the job using it?) beats hours
  of misplaced compute (recurring failure observed in testing); loop closes with an **iterate coda** (a
  surprise updates the frame, not just the log); step 4 + Honest reporting += **uncertainty-first**: every
  newly derived number carries a propagated uncertainty estimate, PROVISIONAL (value *and* band) until
  systematics are investigated — mirrored into `PRINCIPLES.md` §5 (v1.8) and the taxonomy (v3.7). Also
  2026-07-04 (user edit): the **A3 narration line removed** from the spine ("name the skill as you go") —
  the behavior appears to occur by default; kept under observation during testing. The A1 proactive-
  suggestion line stays.
- **Spine content updated to taxonomy v3.4/v3.5** (`synthesis/PRINCIPLE_TAXONOMY_v2.md`): new
  **Universalism** section (weigh every claim by its evidence, never its source — the researcher's, the
  literature's, your own; includes the literature-disagreement weighing rule, elevated from the campaign
  charter); constitution's reporting kernel extended with Feynman's **report-what-might-invalidate**
  standard; working loop gains **work-the-procedure-step-by-step** (pillar 5, renamed **Methodical
  inquiry**), the **winner's curse** re-verification clause, and **reproducible ≠ correct**; "When stuck"
  gains **never name a cause from resemblance** (→ `attribute-mechanism`); "Running unattended" upgrades
  the liveness check to **monitor progress, not liveness**. Trailing nine-context list replaced by the
  **nine pillars**; `PRINCIPLES.md` depth-pointers now cite sections by name (renumbering-safe until X1).
- **Decision #10 reconciled across the spine:** context economy is doctrine but **no longer in the frozen
  constitution** (it tracks model capability) — updated in the CORE body, `PRINCIPLES.md`
  frozen-core note, `DOCTRINE_INDEX.md` coverage row 7, and `reference/context-economy.md` frontmatter.

### Added — experimental measurement-science reference cluster (2026-07-03)

- `docs/reference/uncertainty-and-error-budgets.md` — statistical vs systematic, the error-budget table,
  propagation (+ Monte-Carlo where linear fails), quadrature/correlation traps, the Allan deviation & drift
  wall, reduced-χ², honest reporting. (Meeting-2026-07-02 item **B2**, scoped.)
- `docs/reference/systematic-errors.md` — hunting the biases that don't average down: reversal/null tests,
  vary-the-suspect bounding, auxiliary monitors, blind analysis, a usual-suspects catalog. (Item **B4**, scoped.)
- `docs/reference/noise-and-sensitivity.md` — a-priori noise floor / PSD, fundamental vs technical noise,
  sensitivity, the √N/√T law and where it breaks. (Net-new.)
- `docs/reference/calibration-and-drift.md` — trace-to-a-standard, drift characterization, staleness
  windows, A-B-A interleaving, judge-by-own-output, calibration versioning. (Net-new; lifts
  `hardware-in-the-loop.md` §4 into standalone measurement science.)

The four form a DRY cross-linked cluster (the Allan deviation lives once, in the uncertainty doc) and, with
the merged trio, cover the measurement lifecycle end-to-end (a-priori floor → acquire → extract → number +
uncertainty → hunt systematics → attribute). Field-standard methodology codified into the kit; canonical
sources named but flagged for `cite-check` (nothing fabricated).

### Added — mechanism attribution + extraction hygiene (lab-loop keepers, 2026-07-02)

- **New skill `attribute-mechanism`** — "simulate before you attribute": enumerate candidate mechanisms,
  build a minimal one-knob-per-mechanism model, sweep, keep only mechanisms that reproduce the observed
  numbers, falsify the survivor in a sharp limit. Fills the gap between `frame-problem`, `debug`, and
  `verify` for the "which physics caused this real signature?" question. Grounded in two dated cases from
  a live lab loop (a modulation mis-attributed to detuning that a 5-minute sim pinned on a 3% amplitude
  miscalibration; a pulse-phase-coherence question settled with a hard-pulse limiting case to 1e-7).
- `docs/reference/signal-extraction-pitfalls.md` — five extraction failure modes that manufactured fake
  signatures (or buried real ones) in real data: detrend-before-FFT, fixed-bin peaks tracking the noise
  floor, tuned-pipeline-vs-naive-re-extraction, incoherent averaging, low-SNR peak-picking; plus the
  two-question reflex (null control + independent path).
- `debug` gotcha catalog +3 (from the same loop's live bugs): latent geometry assumptions armed by
  calibration changes; success inferred from ambient state; path-dependent state resets.

### Added — archetype E gets its example + reference (from a real qualified loop)

- `docs/reference/hardware-in-the-loop.md` — eight operational patterns for hardware-in-the-loop
  campaigns (readiness gate; file-based agent–instrument handshake; pause-sentinel sharing;
  calibration-vs-science starvation guard; progress-not-liveness monitoring; ingest quarantine;
  deterministic emission-gate + mid-flight abort; irreversibility/caps/persistence). Every pattern
  answers a failure that occurred while qualifying a real autonomous loop on a low-field (~1 MHz 1H Larmor) NV-diamond-detected NMR
  spectrometer probing microscale sample volumes; thresholds
  are deliberately placeholders to be set from the instrument's own tolerances.
- `examples/charter-files/charter_hardware_loop.md` — the first archetype-E example charter
  (the cheatsheet's "no real example in the kit yet" gap), exercising those patterns end-to-end,
  including the known-answer readiness gate G-0 and comparability tags on the scoreboard.

Second batch of keepers from the 2026-06-30 transcript review (`case-studies/transcript_review_2026-06-30.md`),
plus the first improvements harvested from the Wieman 29-decisions map (`synthesis/WIEMAN_DECISIONS_MAP.md`).
Each tightens the frozen honesty/verification core; none weakens it.

### Project-structure redesign — housing a whole investigation (2026-07-01)
A **Project** layer now sits above campaigns (`synthesis/PROJECT_STRUCTURE_DESIGN.md`, decisions LOCKED). One
investigation, many campaigns + ad-hoc sessions, sharing `data/` + `shared/` by relative path (**referenced,
never copied**) under a single `LINEAGE.md` index — killing the data-duplication + broken-path problems that
bloated prior multi-version investigations (~422 GB across 8 sibling dirs, in the motivating case).
- **New skill `new-project`** — scaffolds the Project home (`PROJECT.md` · `LINEAGE.md` · `DISCOVERIES.md` ·
  `ENGINEERING_NOTES.md` · `shared/{PHYSICS,CONVENTIONS,INSTRUMENT}.md` · `data/` + a `DATA_PATH.txt` pointer ·
  `campaigns/` · `sessions/` · `reports/`), then composes `new-campaign` for the first campaign.
- **New skill `fork-campaign`** — the honest invalidation clean break (§4.4b): when a bug/correction invalidates
  a campaign's findings, archive it (frozen, still in `LINEAGE`), scaffold a fresh-ledger sibling, and carry
  forward ONLY findings that survive independent RE-verification (with provenance) — never a quiet version bump
  that lets a tainted ledger steer the next effort.
- **`new-campaign` is project-aware** — in a Project it references `../../shared` docs (no campaign-local copies),
  wires `../../data`, appends a `LINEAGE.md` row, and resolves the charter *Relationship to sibling campaigns*
  block (§5); tracks collapse into sibling campaigns, not `_<NAME>` suffixes. Standalone mode unchanged.
  `SYSTEM.md` retired → the PHYSICS "target of study" § + `INSTRUMENT.md` (each name unambiguous across subfields).
- **`campaign-status` gains a Project mode** — at a project root it reads `LINEAGE` across campaigns and checks
  cross-campaign FROZEN/MUTABLE (sibling-coupling) consistency; **`handoff`** resumes from `LINEAGE` and checks
  whole-tree portability; **`validate_campaign.py`** auto-detects and validates a whole Project tree
  (structure, every campaign indexed, no local shared-doc copies, no absolute paths in configs).
- **Knowledge base aligned** (§8) — registry gains optional `Project`/`Campaign`/`Session` provenance + `result`
  and `report` resource types; `ingest-transcript` records Project/Campaign/Session; the rigor-honesty
  (true-tier) rule carries across ingest. A per-project scoped KB (§9) is reserved but **not** built this pass.
- **Campaign charter renamed** `program.md` → `charter.md` (threaded across skills/templates). *Note:* older
  changelog entries above/below that reference `program.md(.tmpl)` predate this rename and are left as-written
  (the file was `program.md` when those changes shipped); the live template is `docs/charter.md.tmpl`.

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
