# PhysKit (`physkit`)

A Claude Code **plugin** for rigorous physical-science research. It has two layers:

- **General science toolkit** — skills for framing problems, verifying results, designing and validating
  simulations, dimensional analysis, deriving theory, debugging, and honest reporting. Useful in *any*
  session.
- **Campaign layer** — scaffolds and runs autonomous-research loops (hypothesize → run → evaluate → log
  → verify → repeat), with a frozen honesty/verification core.

Once installed, the skills appear as `/physkit:<name>` in every project.

## Start here — the five skills to know

You don't need to learn the full catalog: the agent routes to the right skill on its own and suggests the
non-obvious one when your work calls for it. These five are the **workflow front doors** worth invoking by
name:

| When you… | Invoke |
|---|---|
| start any physics problem (before modeling, simulating, or deriving) | `/physkit:frame-problem` |
| need a result, number, or derivation checked before relying on it | `/physkit:verify` |
| write up work — every number provenance-labeled, every citation verified | `/physkit:report` |
| stand up an autonomous research campaign (it creates the project home if you don't have one) | `/physkit:new-campaign` |
| want a running campaign health-checked / checkpointed | `/physkit:campaign-status` |

## Principles

PhysKit is built for **rigorous** research in the physical sciences: autonomous enough to do substantial work unattended, and trustworthy enough that a domain expert can build on the results. Those goals are in tension — the more an agent does on its own, the more ways it can be wrong, often confidently and plausibly, in ways that surface only under checking. The kit's response is to treat rigor as something to **build into the system the agent works in**, not something to ask the agent for at run time.

So each principle has two faces:

- a **design face** — the tools, gates, and templates that make it hold, especially during long unattended runs;
- an **operating face** — the `/physkit:` skills the agent uses on a specific task.

They group into nine pillars, led by the one that improves all the others. The table names the machinery behind each.

| Pillar | Design face — built into the kit | Operating face — skills on a task |
|---|---|---|
| **Adaptability & self-improvement** | PhysKit is a living document — improved from real-run retrospectives, with the frozen core off-limits, so it adapts over time | `discovery-loop` / `experiment-design` evolve the artifact; a crash is a bug, not a bad idea; diagnose before pivoting |
| **Integrity & honest reporting** | the frozen honesty core in `docs/CORE.md`, applied through the campaign's promotion discipline | `report` / `final-report` label every number by provenance + give the honest band; `cite-check` blocks fabricated references |
| **Verification & correctness** | `correctness-suite` stands up analytic-limit, convergence, and regression checks, re-run after every core change | `verify` checks independently and recomputes with graded verdicts; `dimensional-analysis`; `debug` |
| **Physics-aware reasoning** | `frame-problem` requires a physics-effect inventory + verification plan; `docs/SIMULATION_VALIDATION.md` codifies V&V&UQ | `dimensional-analysis`, `derive`, `simulation-design`, `correctness-suite` (manufactured solutions, order-of-accuracy) |
| **Rigor** | the campaign loop runs hypothesize → run → evaluate → verify, one change at a time by default | `frame-problem` bounds the answer first; `experiment-design` picks the next run; `model-selection` discriminates hypotheses |
| **Traceability** | per-experiment snapshots + append-only results ledger in the scaffold; a provenance-tag convention | tag every fact (PINNED / REPORTED / INFERRED …); `cite-check` verifies each reference against its source |
| **Autonomy & supervision** | `new-campaign` front-loads clarification; `run-campaign` launches, watches, and steers the supervised loop; `campaign-status` runs periodic health checks | clarify first; don't stop at the first plateau; escalate genuine forks; confirm before irreversible actions |
| **Communication & specification** | each skill is written *why*-first; the campaign charter (`docs/charter.md`) streams goal + context to the agent | `record-decision`, `handoff`, `report` carry the reasoning, not just the result |
| **Focus** (context economy) | tiered doctrine — `docs/CORE.md` always loaded, the rest on demand via `docs/DOCTRINE_INDEX.md` | delegate bounded subtasks to sub-agents on the lightest capable model; keep context small |

**What's permanent, and what isn't.** Most of this doctrine is meant to *evolve* — that's the first pillar. Only two things are fixed: the commitment to careful self-improvement itself, and a **frozen core** of non-negotiable kernels it may never compromise — *never fabricate or misreport*, *nothing is promoted without independent verification*, *physical plausibility is a gate*, and a few more. Seven of the nine pillars contribute such a kernel. Two — **Communication** and **Focus** — deliberately don't: they track what models are capable of, and should improve as models do.

The full per-pillar doctrine, with rationale and provenance, is in [`docs/PRINCIPLES.md`](docs/PRINCIPLES.md); the always-loaded essence is in [`docs/CORE.md`](docs/CORE.md).

## Install

PhysKit's skills follow the open **Agent Skills** standard (`SKILL.md`), so the same skills run on
Claude Code, Codex, and OpenCode. Per-harness detail (plus Gemini CLI) lives in
**[docs/INSTALL_MULTI_HARNESS.md](docs/INSTALL_MULTI_HARNESS.md)**.

### Claude Code

**Quick test** (no install, picks up edits live):
```
claude --plugin-dir "<path-to-this-folder>"
```

**Persistent install** (from GitHub, or a local/shared-drive copy):

**macOS/Linux** — inside the Claude Code REPL:
```
/plugin marketplace add <OWNER>/<REPO>          # or  "<path-to-this-folder>"
/plugin install physkit@physkit
```

**Windows** — the `/plugin` slash command isn't recognized inside the REPL. Run the CLI form from your regular shell instead:
```
claude plugin marketplace add "<path>\physkit-internal\kit"
claude plugin install physkit@physkit
```
Then run `/reload-plugins` and confirm with `/plugin list`. Skills appear as `/physkit:<name>`.

### Codex, OpenCode, and Gemini CLI

These read skills from `~/.agents/skills`. Project this kit's skills there with the bundled installer:
```
scripts/install-skills.sh                                            # macOS / Linux
powershell -ExecutionPolicy Bypass -File scripts\install-skills.ps1  # Windows
```

Restart the harness; it auto-discovers them (verify with `/skills` in Codex, or `opencode debug skill`
in OpenCode). Codex users who prefer a marketplace flow can instead
`codex plugin marketplace add "<path-to-this-folder>"`.

See **[GETTING_STARTED.md](GETTING_STARTED.md)** for the full walkthrough, including how to stand up and
launch an autonomous campaign.

## Layout

```
.claude-plugin/   Claude Code plugin.json + marketplace.json (the manifests)
.codex-plugin/    Codex plugin.json (points at the same skills/)
.agents/          vendor-neutral Codex marketplace entry
skills/           the 24 skills (general + campaign), each a SKILL.md
scripts/          install-skills.{sh,ps1} — project skills into ~/.agents/skills (Codex/OpenCode/Gemini)
docs/             always-on spine (CORE, PRINCIPLES) + on-demand reference docs
templates/        project + campaign scaffolds materialized by /physkit:new-project + new-campaign
```
