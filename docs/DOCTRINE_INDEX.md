---
id: doctrine-index
kind: metadata
layer: shared
load: on-demand
load_trigger: When deciding which doctrine file to read, auditing coverage, or adding a new artifact to the kit.
frozen: false
addresses: [7]
status: new
review: living
---

# Doctrine Index — the kit's map of itself

This is the maintained, machine-readable index of every doctrine artifact in the kit: what it is, when
it loads, which principle contexts it enforces, and its build status. It exists so the agent (and the
maintainer) can find the right file without loading everything — the substrate for **context economy**
(Principle Context 7) and for any future self-improving meta-loop.

**Two jobs:**
1. **Define the metadata schema** (below) that every doc and skill carries in YAML frontmatter.
2. **Hold the index table** mapping every artifact to its metadata + status. Update this table whenever an
   artifact is added, ported, extended, or retired.

> **Single sources of truth.** Principles live in [`PRINCIPLES.md`](PRINCIPLES.md) (canonical taxonomy).
> The always-loaded spine is [`CORE.md`](CORE.md). This index never restates principle content — it only
> points. Context numbers below (`addresses:`) refer to the **nine legacy contexts** in `PRINCIPLES.md`
> (not the nine *pillars* of the v2 taxonomy — the numbering differs; the X1 migration will reconcile).

---

## 1 · The metadata schema

Every doctrine **doc, protocol, and scaffold template** begins with a YAML frontmatter block using these
fields. **Skills are the exception:** a `SKILL.md` frontmatter stays loader-clean (only the `name` +
`description` the plugin loader requires, so `claude plugin validate` passes), and its metadata lives in
the index table below instead. The schema is therefore the contract for non-skill files in-file, and for
skills in this index.

```yaml
---
id: <short-kebab-slug>            # unique within the kit
kind: <see KIND below>            # the delivery mechanism
layer: general | campaign | shared
load: always | on-demand          # context-economy tier
load_trigger: <one line>          # WHEN this should be pulled into context
frozen: true | false             # part of the non-negotiable honesty/verification core?
addresses: [<context numbers>]    # which PRINCIPLES.md contexts it enforces (1–8)
status: <see STATUS below>        # build state
review: <flag | date | "living" | omit>
---
```

**`kind`** — the delivery mechanism (from the delivery-mechanism taxonomy):

| value | meaning |
|---|---|
| `core-doc` | always-loaded slim spine; the constitution + routing |
| `reference-doc` | on-demand depth; read when a situation calls for it |
| `skill` | an invokable `SKILL.md` (general or campaign) |
| `protocol` | a campaign procedure template (e.g. checkpoint, artifacts) |
| `scaffold-template` | a `*.tmpl` file materialized into a generated campaign tree |
| `metadata` | indexes/schemas about the kit itself (this file) |

**`layer`** — `general` (everyday science requests), `campaign` (autoresearch loops only), or `shared`
(both). The dual-use split: general sessions never pay the context cost of campaign material,
because campaign artifacts are `on-demand` and `layer: campaign`.

**`frozen`** — `true` for the honesty/verification constitution that must never be "optimized away" under
any self-improvement: scientific integrity (Ctx 1), independent verification (Ctx 2), metric integrity,
context economy. Everything else is `false`.

**`status`** — build state, so this index doubles as the live build tracker:

| value | meaning |
|---|---|
| `new` | authored fresh for this version |
| `ported` | carried over from v2 with reorganization |
| `shipped-v2` | exists in v2, not yet revised |
| `extend` | exists in v2; planned changes not yet applied |
| `planned` | designed (in `synthesis/`) but not yet built |
| `deferred` | intentionally postponed |

**`addresses`** — the list of `PRINCIPLES.md` context numbers the artifact primarily enforces. Lets the
maintainer audit that every principle context has a home, and that no orphan files exist.

---

## 2 · The index

Status reflects the **build backlog** (`synthesis/BUILD_BACKLOG.md`). "Path" is relative to the kit root.
Items not yet built are listed so the index is a complete map of the intended kit, not just what exists.

### Shared spine (always loaded)

| id | path | kind | frozen | addresses | status |
|---|---|---|---|---|---|
| core | `docs/CORE.md` | core-doc | true | 1,2,7,8,9 | new |
| principles | `docs/PRINCIPLES.md` | reference-doc | true | 1–9 | new |
| doctrine-index | `docs/DOCTRINE_INDEX.md` | metadata | false | 7 | new |

### General reference docs (on-demand)

| id | path | kind | addresses | status |
|---|---|---|---|---|
| simulation-validation | `docs/SIMULATION_VALIDATION.md` | reference-doc | 2,5 | ported+augmented |
| dimensional-analysis-ref | `docs/reference/dimensional-analysis.md` | reference-doc | 4,5 | new |
| pivoting | `docs/reference/pivoting.md` | reference-doc | 3 | new |
| version-control | `docs/reference/version-control.md` | reference-doc | 7 | new |
| context-economy | `docs/reference/context-economy.md` | reference-doc | 7 | new |
| coordinate-frames | `docs/reference/coordinate-frames.md` | reference-doc | 5 | new |
| hardware-in-the-loop | `docs/reference/hardware-in-the-loop.md` | reference-doc | 4,8,9 | new |
| signal-extraction-pitfalls | `docs/reference/signal-extraction-pitfalls.md` | reference-doc | 2,4,5 | new |
| uncertainty-and-error-budgets | `docs/reference/uncertainty-and-error-budgets.md` | reference-doc | 2,5,1 | new |
| systematic-errors | `docs/reference/systematic-errors.md` | reference-doc | 2,4,1 | new |
| noise-and-sensitivity | `docs/reference/noise-and-sensitivity.md` | reference-doc | 5,4,2 | new |
| calibration-and-drift | `docs/reference/calibration-and-drift.md` | reference-doc | 4,5,7 | new |
| ip-and-attribution | `docs/reference/ip-and-attribution.md` | reference-doc | 1,7 | new |
| prompt-surface-audit | `docs/reference/prompt-surface-audit.md` | reference-doc | 9,1 | new |
| reporting-standards | — | reference-doc | 1 | absorbed into `report` skill (§standards) |
| latex-toolchain | — | reference-doc | 1 | absorbed into `report` assets README |

### General skills (on-demand; `layer: general`)

| id | path | addresses | status |
|---|---|---|---|
| frame-problem | `skills/frame-problem/SKILL.md` | 5,4,3 | new |
| verify | `skills/verify/SKILL.md` | 2 | new (generalizes v2 verify-finding) |
| simulation-design | `skills/simulation-design/SKILL.md` | 5 | new |
| correctness-suite | `skills/correctness-suite/SKILL.md` | 2,5 | new |
| debug | `skills/debug/SKILL.md` | 3 | new |
| dimensional-analysis | `skills/dimensional-analysis/SKILL.md` | 5,3 | new |
| record-decision | `skills/record-decision/SKILL.md` | 7 | new |
| cite-check | `skills/cite-check/SKILL.md` | 1 | new (lifted from final-report) |
| report | `skills/report/SKILL.md` | 1 | new |
| derive | `skills/derive/SKILL.md` | 2,5 | new (analytical/symbolic theory) |
| assess-idea | `skills/assess-idea/SKILL.md` | 8,4,9 | new (feasibility/worth triage — Wieman decision 9; front-end cluster) |
| literature-review | `skills/literature-review/SKILL.md` | 1,8 | new (understand the field, cited — Wieman decisions 1,7; front-end cluster) |
| attribute-mechanism | `skills/attribute-mechanism/SKILL.md` | 2,5,3 | new (mechanism attribution — "simulate before you attribute"; composes frame-problem/dimensional-analysis/signal-extraction-pitfalls/debug/verify) |
| assumption-audit | `skills/assumption-audit/SKILL.md` | 3,4 | new (plateau → diagnosis mode-change; solve-don't-confirm + operating-point validity; lab-loop keeper) |

### Project skills (`layer: campaign`)

| id | path | addresses | status |
|---|---|---|---|
| new-project | `skills/new-project/SKILL.md` | 7,8 | new — **default path, not on-demand**: every campaign lives in a project, so `new-campaign` Step 0.1 runs this whenever no project home exists (and it composes new-campaign for the first campaign) |
| fork-campaign | `skills/fork-campaign/SKILL.md` | 2,1 | on-demand; new (invalidation clean break §4.4b; composes new-campaign + verify) |

### Campaign skills (on-demand; `layer: campaign`)

| id | path | addresses | status |
|---|---|---|---|
| new-campaign | `skills/new-campaign/SKILL.md` | 4,8 | ported+extended (project-aware: reference shared, LINEAGE row, §5 relationship) |
| campaign-status | `skills/campaign-status/SKILL.md` | 3,4 | ported+extended (+ project mode: cross-campaign, FROZEN/MUTABLE) |
| final-report | `skills/final-report/SKILL.md` | 1 | ported+extended (composes `report`) |
| handoff | `skills/handoff/SKILL.md` | 7 | new (project-aware: resume from LINEAGE, whole-tree portability) |
| discovery-loop | `skills/discovery-loop/SKILL.md` | 6 | new (archetype G) |
| experiment-design | `skills/experiment-design/SKILL.md` | 4 | new (archetype H) |
| model-selection | `skills/model-selection/SKILL.md` | 2,4 | new (archetype I) |

### Project scaffold (`layer: campaign`; materialized by `new-project` for the project every campaign lives in)

| id | path | kind | addresses | status |
|---|---|---|---|---|
| project-charter | `templates/project/PROJECT.md.tmpl` | scaffold-template | 7 | new (system · goal · data/shared pointers) |
| lineage | `templates/project/LINEAGE.md.tmpl` | scaffold-template | 7 | new (the campaign + session index) |
| project-claude | `templates/project/CLAUDE.md.tmpl` | scaffold-template | 1,7 | new (project always-on rules) |
| project-discoveries | `templates/project/DISCOVERIES.md.tmpl` | scaffold-template | 2,7 | new (promoted verified findings; survive fork-and-archive) |
| project-engineering-notes | `templates/project/ENGINEERING_NOTES.md.tmpl` | scaffold-template | 7 | new (durable project-wide decisions) |
| shared-physics | `templates/project/shared/PHYSICS.md.tmpl` | scaffold-template | 5 | new (governing physics + target-of-study §; shared) |
| shared-conventions | `templates/project/shared/CONVENTIONS.md.tmpl` | scaffold-template | 5 | new (units/signs/frames; shared) |
| shared-instrument | `templates/project/shared/INSTRUMENT.md.tmpl` | scaffold-template | 5 | new (measurement rig; retires SYSTEM.md) |
| data-readme | `templates/project/data/README.md.tmpl` | scaffold-template | 7 | new (read-only + DATA_PATH pointer convention) |
| reports-readme | `templates/project/reports/README.md.tmpl` | scaffold-template | 1 | new (single project outputs location) |
| session-notes | `templates/project/sessions/NOTES.md.tmpl` | scaffold-template | 7,8 | new (ad-hoc session record at true tier) |

### Campaign scaffold (`layer: campaign`; materialized per campaign)

| id | path | kind | addresses | status |
|---|---|---|---|---|
| program | `templates/campaign/docs/charter.md.tmpl` | scaffold-template | 3,4 | ported+refined |
| physics | `templates/project/shared/PHYSICS.md.tmpl` | scaffold-template | 5 | ported+refined (inventory); shared per project — the campaign-local copy was retired with standalone mode |
| intake | `templates/campaign/INTAKE.md.tmpl` | scaffold-template | 8 | new |
| project-orientation | `templates/campaign/docs/PROJECT_ORIENTATION.md.tmpl` | scaffold-template | 7,8 | new |
| engineering-notes | `templates/campaign/docs/ENGINEERING_NOTES.md.tmpl` | scaffold-template | 7 | new |
| verification-plan | `templates/campaign/docs/VERIFICATION_PLAN.md.tmpl` | scaffold-template | 2 | new |
| expensive-evaluation | `templates/campaign/docs/protocols/expensive-evaluation.md.tmpl` | protocol | 4,6 | new |
| artifacts-protocol | `templates/campaign/docs/protocols/artifacts.md.tmpl` | protocol | 7 | ported+refined |
| campaign-claude | `templates/campaign/CLAUDE.md.tmpl` | scaffold-template | 1,2,7 | always-on per-campaign doctrine: a FROZEN, provenance-stamped snapshot of `CORE.md` rendered by `new-campaign` (Step 3) into `{{PHYSKIT_SPINE}}` + the campaign hard gates. Freeze-and-stamp, NOT `@`-imported or hash-checked (kit-dev `CLAUDE.md` §single-source) |
| discoveries-guard | `templates/campaign/scripts/guard_discoveries.py.tmpl` | scaffold-template | 2 | new (PreToolUse hook: blocks unverified DISCOVERIES write) |
| loop-heartbeat | `templates/campaign/scripts/loop_heartbeat.py.tmpl` | scaffold-template | 9 | new (Stop hook: refuses an unearned end-of-turn; stop via `results/STOP` or a recorded `stop_request.json`) |
| hook-settings | `templates/campaign/.claude/settings.json.tmpl` | scaffold-template | 2,9 | new (wires the guard + heartbeat hooks; uses `{{PYTHON_CMD}}`) |
| claude-general | ~~`templates/CLAUDE.general.md`~~ | scaffold-template | 1,2,7 | **retired 2026-07-03** — was a duplicate of the spine and drifted; `docs/CORE.md` is the single source. Users import it from their project `CLAUDE.md` (`@<kit>/docs/CORE.md`) or copy its body (see `GETTING_STARTED.md` §1) |

### Report assets

| id | path | kind | addresses | status |
|---|---|---|---|---|
| report-skeleton | `skills/report/assets/report_skeleton.tex` | scaffold-template | 1 | new (compiles) |
| report-macros | `skills/report/assets/report-macros.sty` | scaffold-template | 1 | new |
| draft-article | `skills/report/assets/draft_article.tex` | scaffold-template | 1 | new |
| revtex-vendored | `skills/report/assets/{revtex4-2.cls, aps*.rtx, revsymb4-2.sty, ltxgrid.sty, ltxutil.sty, apsrev4-2.bst}` | scaffold-template | 1 | vendored (compiles) |

### Archetypes (campaign reference)

| id | path | addresses | status |
|---|---|---|---|
| archetype-cheatsheet | `templates/ARCHETYPE_CHEATSHEET.md` | 4,6 | extended (added G,H,I) |
| archetype-G-discovery | (cheatsheet + `discovery-loop` skill) | 6 | new |
| archetype-H-active-design | (cheatsheet + `experiment-design` skill) | 4 | new |
| archetype-I-model-selection | (cheatsheet + `model-selection` skill) | 2,4 | new |

---

## 3 · Coverage audit

Every principle context should have at least one `frozen` or always-loaded home plus on-demand depth:

| Ctx | Home(s) |
|---|---|
| 1 Integrity | CORE + PRINCIPLES (frozen); `report`, `cite-check`, reporting-standards, `ip-and-attribution`, `prompt-surface-audit` |
| 2 Verification | CORE + PRINCIPLES (frozen); `verify`, `correctness-suite`, SIMULATION_VALIDATION, `signal-extraction-pitfalls`, `attribute-mechanism`, `uncertainty-and-error-budgets`, `systematic-errors`, `noise-and-sensitivity` |
| 3 Problem-solving | PRINCIPLES; `debug`, `pivoting`, `assumption-audit`, charter.md, campaign-status |
| 4 Experimental design | PRINCIPLES; charter.md, `new-campaign`, archetypes, `hardware-in-the-loop`, `systematic-errors`, `noise-and-sensitivity`, `calibration-and-drift`, `assumption-audit` |
| 5 Physics & simulation | PRINCIPLES; `frame-problem`, `simulation-design`, SIMULATION_VALIDATION, PHYSICS, `attribute-mechanism`, `uncertainty-and-error-budgets`, `noise-and-sensitivity`, `calibration-and-drift` |
| 6 Discovery-loop | PRINCIPLES; `discovery-loop`, archetype G (cheatsheet), expensive-evaluation |
| 7 Records & reproducibility | CORE (context economy — doctrine, unfrozen per dec #10 2026-07-03); this index, `handoff`, `record-decision`, scaffold |
| 8 Autonomy & collaboration | CORE (frozen-adjacent: clarify-the-goal); `new-campaign`, frame-problem |
| 9 Operating unattended | CORE (Running unattended) + PRINCIPLES §9; `charter.md` (Getting Unstuck + Ending the loop + promotion), `campaign-status`, `expensive-evaluation`, `hardware-in-the-loop` (archetype E), ENGINEERING_NOTES (landmines), the CLAUDE.md gates + the DISCOVERIES and loop-heartbeat hooks, `prompt-surface-audit` |

**Open gaps:** none of the backlog tiers remain — Tiers 0–5 and the deferred discovery-loop/archetype G are
all built. Remaining work is testing/iteration, not net-new artifacts. *(Context 9 overlaps 7–8 by design;
its organization vs those contexts is flagged for revisit.)*

## Changelog
- **v0.7 (unreleased)** — re-classed `new-project` from an on-demand Project skill to the **default path**, and the project
  scaffold as the home every campaign has: the standalone / bare-campaign mode is retired, so `new-campaign`
  Step 0.1 finds the project home or runs `new-project` to create it. Sign-off: approved in-session 2026-07-18.
- **v0.6** — added the 2026-07 lab-loop keepers: `assumption-audit` (skills-table row + Ctx 3/4 coverage —
  the plateau → diagnosis mode-change; solve-don't-confirm + operating-point validity) and
  `prompt-surface-audit` (reference-doc row + Ctx 9/1 coverage — rendered-context auditing for multi-agent
  loops; PRINCIPLES Ctx 9 gained the twin bullet, v1.9; CORE's plateau line gained the second species).
  Sign-off route: PR review, 2026-07-07.
- **v0.5** — added `ip-and-attribution` (the cite-and-adapt-never-reproduce guardrail for capability work,
  meeting item X3/LHF-2): reference-doc row + Ctx 1 coverage. Constraint doc for the C1–C4 capability
  library; posture pending formal confirmation by open decision #8. Sign-off approved 2026-07-04.
- **v0.4** — indexed the experimental **measurement-science reference cluster**
  (`uncertainty-and-error-budgets`, `systematic-errors`, `noise-and-sensitivity`, `calibration-and-drift`):
  added their rows + Ctx 2/4/5 coverage. Meeting-2026-07-02 items **B2** (uncertainty) and **B4**
  (systematics) plus two net-new (noise, calibration). *(Context-numbered `addresses` remap with the X1
  9-pillar migration.)*
- **v0.3** — indexed the mechanism-attribution + hardware-loop additions (PRs #6/#7, merged 2026-07-03):
  added the `attribute-mechanism` skills-table row (its SKILL.md shipped but was left unindexed), and wired
  `attribute-mechanism` / `signal-extraction-pitfalls` / `hardware-in-the-loop` into the §3 coverage audit
  (Ctx 2/4/5/9). The two reference docs were already row-indexed in-PR; no principle content changed —
  provenance in `synthesis/PR6_PR7_INTEGRATION_REVIEW.md`.
- **v0.2** — added **Context 9 · Operating unattended** to the coverage audit (home: CORE "Running
  unattended" + PRINCIPLES §9; enforced via `charter.md` / `campaign-status` / `expensive-evaluation` /
  ENGINEERING_NOTES landmines / the CLAUDE.md gates). Bumped CORE `addresses` to `1,2,7,8,9` and PRINCIPLES
  to `1–9`. From the 2026-06-30 review.
- **v0.1** — initial index + metadata schema. Enumerates the full intended kit (built + planned) from
  `synthesis/BUILD_BACKLOG.md` and `SKILLS_AND_DOCS_OUTLINE.md`.
