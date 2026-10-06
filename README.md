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
| **Focus** (context economy) | tiered doctrine — `docs/CORE.md` always loaded, the rest on demand via `docs/DOCTRINE_INDEX.md` | delegate bounded subtasks to sub-agents on the lightest capable model; keep context small |

**What's permanent, and what isn't.** Most of this doctrine is meant to evolve; that is the first pillar.
Only two things are fixed: the commitment to careful self-improvement itself, and a **frozen core** of kernels
the kit may never compromise — never fabricate or misreport, nothing is promoted without independent
verification, physical plausibility is a gate, and a few more. Seven of the nine pillars contribute such a
kernel. Communication and Focus do not, by design: they track what models are capable of, and are expected
to improve as models do.

The doctrine is stated in [`docs/CORE.md`](docs/CORE.md), which is always loaded; each skill and reference doc carries the depth for the work it covers.

## Install

PhysKit's skills follow the open **Agent Skills** standard (`SKILL.md`), so the same skills run on
Claude Code, Codex, and OpenCode. Per-harness detail (plus Gemini CLI) lives in
[docs/INSTALL_MULTI_HARNESS.md](docs/INSTALL_MULTI_HARNESS.md).

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

**Windows** — the `/plugin` slash command isn't recognized inside the REPL. Run the CLI form from a regular shell instead:
```
claude plugin marketplace add "<path>\physkit-internal\kit"
claude plugin install physkit@physkit
```
Then run `/reload-plugins` and confirm with `/plugin list`. Skills appear as `/physkit:<name>`.

### Codex — full campaign-capable package

Register the local PhysKit marketplace and install the plugin:

```
codex plugin marketplace add "<path-to-this-folder>"
codex plugin add physkit@physkit
```

Confirm with `codex plugin list`, then start a new Codex task so the refreshed plugin context is loaded.
This full-package route includes the templates, doctrine, validators, and scripts required by
`new-campaign`, `run-campaign`, and the closed loop.

After updating this local checkout, refresh the installed copy with
`codex plugin add physkit@physkit`, confirm it with
`codex plugin list --marketplace physkit`, and start a new task. You do not need to register the same
marketplace again.

### Skills-only projection — general use, not campaigns

Codex, OpenCode, and Gemini CLI can read standalone skills from `~/.agents/skills`. Project the skill
folders there with the bundled installer:
```
scripts/install-skills.sh                                            # macOS / Linux
powershell -ExecutionPolicy Bypass -File scripts\install-skills.ps1  # Windows
```

Restart the harness; it auto-discovers them (verify with `/skills` in Codex, or `opencode debug skill`
in OpenCode). This projection does not include package-level `templates/` or `docs/`; use it for the
general science toolkit only. A campaign skill discovered from this projection must not scaffold from a
source-tree fallback—install the full Codex plugin above instead.

See [GETTING_STARTED.md](GETTING_STARTED.md) for the full walkthrough, including how to stand up and
launch an autonomous campaign.

## Layout

```
.claude-plugin/   Claude Code plugin.json + marketplace.json (the manifests)
.codex-plugin/    Codex plugin.json (points at the same skills/)
.agents/          vendor-neutral Codex marketplace entry
skills/           the 26 skills (general + campaign + kit improvement), each a SKILL.md
scripts/          install-skills.{sh,ps1} — skills-only projection for general cross-harness use
docs/             always-on spine (CORE) + on-demand reference docs
templates/        project + campaign scaffolds materialized by /physkit:new-project + new-campaign
```
