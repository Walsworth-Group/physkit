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
> points. Context numbers below (`addresses:`) refer to the eight contexts in `PRINCIPLES.md`.

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
| core | `docs/CORE.md` | core-doc | true | 1,2,7,8 | new |
| principles | `docs/PRINCIPLES.md` | reference-doc | true | 1–8 | new |
| doctrine-index | `docs/DOCTRINE_INDEX.md` | metadata | false | 7 | new |

### General reference docs (on-demand)

| id | path | kind | addresses | status |
|---|---|---|---|---|
| simulation-validation | `docs/SIMULATION_VALIDATION.md` | reference-doc | 2,5 | ported+augmented |
| dimensional-analysis-ref | `docs/reference/dimensional-analysis.md` | reference-doc | 4,5 | new |
| pivoting | `docs/reference/pivoting.md` | reference-doc | 3 | new |
| version-control | `docs/reference/version-control.md` | reference-doc | 7 | new |
| context-economy | `docs/reference/context-economy.md` | reference-doc | 7 | new |
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

### Campaign skills (on-demand; `layer: campaign`)

| id | path | addresses | status |
|---|---|---|---|
| new-campaign | `skills/new-campaign/SKILL.md` | 4,8 | ported+extended |
| campaign-status | `skills/campaign-status/SKILL.md` | 3,4 | ported+extended |
| final-report | `skills/final-report/SKILL.md` | 1 | ported+extended (composes `report`) |
| handoff | `skills/handoff/SKILL.md` | 7 | new |
| discovery-loop | `skills/discovery-loop/SKILL.md` | 6 | new (archetype G) |
| experiment-design | `skills/experiment-design/SKILL.md` | 4 | new (archetype H) |
| model-selection | `skills/model-selection/SKILL.md` | 2,4 | new (archetype I) |

### Campaign scaffold (`layer: campaign`; materialized per campaign)

| id | path | kind | addresses | status |
|---|---|---|---|---|
| program | `templates/campaign/docs/program.md.tmpl` | scaffold-template | 3,4 | ported+refined |
| physics | `templates/campaign/docs/PHYSICS.md.tmpl` | scaffold-template | 5 | ported+refined (inventory) |
| intake | `templates/campaign/INTAKE.md.tmpl` | scaffold-template | 8 | new |
| project-orientation | `templates/campaign/docs/PROJECT_ORIENTATION.md.tmpl` | scaffold-template | 7,8 | new |
| engineering-notes | `templates/campaign/docs/ENGINEERING_NOTES.md.tmpl` | scaffold-template | 7 | new |
| verification-plan | `templates/campaign/docs/VERIFICATION_PLAN.md.tmpl` | scaffold-template | 2 | new |
| expensive-evaluation | `templates/campaign/docs/protocols/expensive-evaluation.md.tmpl` | protocol | 4,6 | new |
| artifacts-protocol | `templates/campaign/docs/protocols/artifacts.md.tmpl` | protocol | 7 | ported+refined |

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
| 1 Integrity | CORE + PRINCIPLES (frozen); `report`, `cite-check`, reporting-standards |
| 2 Verification | CORE + PRINCIPLES (frozen); `verify`, `correctness-suite`, SIMULATION_VALIDATION |
| 3 Problem-solving | PRINCIPLES; `debug`, `pivoting`, program.md, campaign-status |
| 4 Experimental design | PRINCIPLES; program.md, `new-campaign`, archetypes |
| 5 Physics & simulation | PRINCIPLES; `frame-problem`, `simulation-design`, SIMULATION_VALIDATION, PHYSICS |
| 6 Discovery-loop | PRINCIPLES; `discovery-loop`, archetype G (cheatsheet), expensive-evaluation |
| 7 Records & reproducibility | CORE (frozen: context economy); this index, `handoff`, `record-decision`, scaffold |
| 8 Autonomy & collaboration | CORE (frozen-adjacent: clarify-the-goal); `new-campaign`, frame-problem |

**Open gaps:** none of the backlog tiers remain — Tiers 0–5 and the deferred discovery-loop/archetype G are
all built. Remaining work is testing/iteration, not net-new artifacts.

## Changelog
- **v0.1** — initial index + metadata schema. Enumerates the full intended kit (built + planned) from
  `synthesis/BUILD_BACKLOG.md` and `SKILLS_AND_DOCS_OUTLINE.md`.
