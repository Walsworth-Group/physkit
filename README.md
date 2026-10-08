# PhysKit (`physkit`)

A cross-harness plugin for rigorous physical-science research, packaged for Claude Code and Codex. It
has two layers:

- **General science toolkit** — skills for framing problems, verifying results, designing and validating
  simulations, dimensional analysis, deriving theory, debugging, and honest reporting. Useful in any
  session.
- **Campaign layer** — scaffolds and runs autonomous-research loops (hypothesize → run → evaluate → log
  → verify → repeat), with a frozen honesty/verification core.

Once installed, the skills appear as `/physkit:<name>` in Claude Code and `$physkit:<name>` in Codex;
both harnesses may also select a matching skill automatically.

> **Pre-release.** PhysKit is in active development (every version so far is 0.x), and its skills, templates,
> and doctrine still change between versions. Use the latest version; earlier versions remain tagged only
> so that work which cites them can be traced, and are not maintained.

## Start here — the five skills to know

The agent routes to the right skill on its own, and suggests the non-obvious one when the work calls for
it. These five are the workflow front doors worth invoking by name:

| To… | Invoke |
|---|---|
| start any physics problem (before modeling, simulating, or deriving) | `frame-problem` |
| check a result, number, or derivation before relying on it | `verify` |
| write up work — every number provenance-labeled, every citation verified | `report` |
| stand up an autonomous research campaign (it creates the project home if none exists) | `new-campaign` |
| health-check or checkpoint a running campaign | `campaign-status` |

## Principles

PhysKit is built for rigorous research in the physical sciences: autonomous enough to do substantial work
unattended, and trustworthy enough that a domain expert can build on the results. Those goals are in
tension. The more an agent does on its own, the more ways it can be wrong, confidently and plausibly, in
ways that surface only under checking. The kit's response is to build rigor into the system the agent works
in, rather than ask the agent for it at run time.

Each principle has two faces:

- a **design face** — the tools, gates, and templates that make it hold, especially during long unattended runs;
- an **operating face** — the `/physkit:` skills the agent uses on a specific task.

They group into nine pillars, led by the one that improves all the others. The table names the machinery behind each.

| Pillar | Design face — built into the kit | Operating face — skills on a task |
|---|---|---|
| **Adaptability & self-improvement** | PhysKit is a living document — improved from real-run retrospectives, with the frozen core off-limits, so it adapts over time | `campaign-review` → `improve-kit` turn a finished campaign into reviewed changes to your copy of the kit; `discovery-loop` / `experiment-design` evolve the artifact; fix a crash and re-run before judging the idea; diagnose a failure before pivoting |
| **Integrity & honest reporting** | the frozen honesty core in `docs/CORE.md`, applied through the campaign's promotion discipline | `report` labels every number by provenance + give the honest band; `cite-check` blocks fabricated references |
| **Verification & correctness** | `correctness-suite` stands up analytic-limit, convergence, and regression checks, re-run after every core change | `verify` checks independently and recomputes with graded verdicts; `dimensional-analysis`; `debug` |
| **Physics-aware reasoning** | `frame-problem` requires a physics-effect inventory + verification plan; `docs/SIMULATION_VALIDATION.md` codifies V&V&UQ | `dimensional-analysis`, `derive`, `simulation-design`, `correctness-suite` (manufactured solutions, order-of-accuracy) |
| **Rigor** | the campaign loop runs hypothesize → run → evaluate → verify, recording what each step changed | `frame-problem` bounds the answer first; `experiment-design` picks the next run; `model-selection` discriminates hypotheses |
| **Traceability** | per-experiment snapshots + append-only results ledger in the scaffold; a provenance-tag convention | tag every fact (PINNED / REPORTED / INFERRED …); `cite-check` verifies each reference against its source |
| **Autonomy & supervision** | `new-campaign` front-loads clarification; `run-campaign` launches, watches, and steers the supervised loop; `campaign-status` runs periodic health checks | clarify first; continue past the first plateau; escalate genuine forks; confirm before irreversible actions |
| **Communication & specification** | each skill is written *why*-first; the campaign definition (`campaign.md`) streams goal + context to the agent | `record-decision`, `handoff`, `report` carry the reasoning, not just the result |
| **Focus** (context economy) | tiered doctrine — `docs/CORE.md` always loaded, the rest on demand via its routing table | delegate bounded subtasks to sub-agents on the lightest capable model; keep context small |

**What's permanent, and what isn't.** Most of this doctrine is meant to evolve; that is the first pillar.
Only two things are fixed: the commitment to careful self-improvement itself, and a **frozen core** of kernels
the kit may never compromise — never fabricate or misreport, nothing is promoted without independent
verification, physical plausibility is a gate, and a few more. Seven of the nine pillars contribute such a
kernel. Communication and Focus do not, by design: they track what models are capable of, and are expected
to improve as models do.

The doctrine is stated in [`docs/CORE.md`](docs/CORE.md), which is always loaded; each skill and reference doc carries the depth for the work it covers.

## Install

PhysKit installs as a plugin in **Claude Code** or **Codex**. The repository is its own plugin
marketplace, so you add it once and install from it. Campaigns need the full plugin, not a copy of the
`skills/` folder, because scaffolding reads the bundled templates, docs, scripts, and validators.

### Claude Code

In a Claude Code session:
```
/plugin marketplace add Walsworth-Group/physkit
/plugin install physkit@physkit
```
`/plugin install` opens the plugin's details; choose a scope there: you (every project on this machine),
everyone working in this repository, or this repository only. Or, from your shell:
```
claude plugin marketplace add Walsworth-Group/physkit
claude plugin install physkit@physkit                    # add --scope project to share with collaborators
```
Type `/physkit:` to see the skills, or run `claude plugin list`. In the desktop app's Code tab, use
**+ → Plugins → Add plugin**; in VS Code, type `/plugins`. An install at user scope is shared by the
terminal, the desktop app, and VS Code on the same computer.

- **Update.** This marketplace does not auto-update unless you turn it on (`/plugin` → **Marketplaces** →
  **Enable auto-update**). To update now: `claude plugin update physkit@physkit`, then `/reload-plugins` in
  an open session.
- **Pin a version.** Add the release tag to the marketplace source:
  `/plugin marketplace add Walsworth-Group/physkit#v0.12.3`.
- **Share with a team.** Install at project scope and commit the `.claude/settings.json` it writes. Each
  collaborator then adds the marketplace and runs `claude plugin install physkit@physkit --scope project`
  once.
- **Remove.** `claude plugin uninstall physkit@physkit` (or `disable` to keep it installed but off).

### Codex

From your shell:
```
codex plugin marketplace add Walsworth-Group/physkit
codex plugin add physkit@physkit
```
Or run `/plugins` in the Codex CLI to browse and install. Start a new session afterwards; skills load at
session start and appear as `$physkit:<name>`. Check with `codex plugin list`.

- **Update.** `codex plugin marketplace upgrade physkit`, then `codex plugin add physkit@physkit` to refresh
  the installed copy, and start a new session.
- **Pin a version.** `codex plugin marketplace add Walsworth-Group/physkit --ref v0.12.3`.
- **Remove.** `codex plugin remove physkit@physkit`.

### Keep the doctrine loaded

The plugin makes the skills available. To keep PhysKit's rules (`docs/CORE.md`) in context on every turn
of ordinary work, copy the body of `docs/CORE.md` into your project's `CLAUDE.md` (Claude Code) or
`AGENTS.md` (Codex), and refresh it when you update the plugin. A campaign scaffolded by
`/physkit:new-campaign` writes its own and needs nothing from you.

### Modifying the kit

To change PhysKit for your own work, clone or fork this repository and load your copy directly:
```
claude --plugin-dir ./physkit        # one session, reads the files live; /reload-plugins after edits
```
For Codex, add your clone as a local marketplace (`codex plugin marketplace add ./physkit`, then
`codex plugin add physkit@physkit`) and re-run the add after each edit. `/physkit:campaign-review` and
`/physkit:improve-kit` turn a finished campaign into reviewed changes to your copy.

### Other agents (general skills only)

OpenCode and Gemini CLI read the same `SKILL.md` format from `~/.agents/skills`. The bundled installer
copies the skills there:
```
scripts/install-skills.sh                                            # macOS / Linux
powershell -ExecutionPolicy Bypass -File scripts\install-skills.ps1  # Windows
```
This copy has no templates or docs, so it covers the general science toolkit, not campaigns. Details and
caveats (skill-name collisions): [docs/INSTALL_MULTI_HARNESS.md](docs/INSTALL_MULTI_HARNESS.md).

See [GETTING_STARTED.md](GETTING_STARTED.md) for the full walkthrough, including how to stand up and
launch an autonomous campaign.

## Sources and acknowledgments

PhysKit's doctrine draws on the verification, validation and uncertainty-quantification literature (cited
in `docs/SIMULATION_VALIDATION.md`), the agentic-research literature, and the authors' experience running
research agents. Its rules are written as behaviors tied to the failures they prevent, after Zimmer et
al., *The Agentic Researcher* (arXiv:2603.15914); `docs/CORE.md`'s Stage 0 ("clarify the goal") adapts
"Think Before Coding" from the Karpathy skills collection. The bundled REVTeX 4.2 files in
`skills/report/assets/` keep their own license (LPPL); the MIT license covers the rest.

## Layout

```
.claude-plugin/   Claude Code plugin.json + marketplace.json (the manifests)
.codex-plugin/    Codex plugin.json (points at the same skills/)
.agents/          vendor-neutral Codex marketplace entry
skills/           the 26 skills (general + campaign + kit improvement), each a SKILL.md
scripts/          install-skills.{sh,ps1} (skills-only copy for other agents); hardware/ and audits/ helpers
docs/             always-on spine (CORE) + on-demand reference docs
templates/        project + campaign scaffolds materialized by /physkit:new-project + new-campaign
```
