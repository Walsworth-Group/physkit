# Installing PhysKit across agent harnesses

PhysKit's skills are authored to the open **Agent Skills** standard (`SKILL.md` with `name` +
`description` frontmatter and progressive disclosure). That standard is now read natively by several
agent CLIs, so the same skills that power PhysKit on Claude Code also run on Codex, OpenCode, and
Gemini CLI — with the same "auto-load the right skill when the task matches" behavior.

This document covers installing on each. **The Claude Code flow is unchanged** — everything here is
additive; no skill content and no Claude packaging was modified to enable the other harnesses.

> **Single source of truth.** `kit/skills/` is the one canonical copy of every skill. The Codex plugin
> wrapper points at it directly; the install script *projects* it into other tools' directories. After
> you update the kit (`git pull`), re-run the install script to refresh those copies (or install with
> `--link` / `-Link` to symlink instead of copy, so they never drift).

---

## Claude Code — unchanged

Nothing about the existing flow changed. Install exactly as before:

```
claude plugin marketplace add <path-to>/kit
claude plugin install physkit@physkit
```

Skills appear as `physkit:<name>` and auto-load on demand. This remains the reference experience.

---

## The one-location shortcut: `~/.agents/skills`

Codex, OpenCode, and Gemini CLI **all scan `~/.agents/skills` at user scope**, so a single install
covers all three. From the kit root:

```bash
# macOS / Linux
kit/scripts/install-skills.sh

# Windows (PowerShell)
kit\scripts\install-skills.ps1
```

Both scripts copy the 23 skills into `~/.agents/skills/` and are idempotent. Options:

| Option | Effect |
|---|---|
| `--target DIR` / `-Target DIR` | Install into a different skills directory |
| `--link` / `-Link` | Symlink instead of copy (live-linked, never drifts; Windows needs Developer Mode) |
| `--uninstall` / `-Uninstall` | Remove the PhysKit skills from the target |

Then start (or restart) your harness; it will discover the skills on launch.

---

## Codex

**Path A — skills directory (recommended, simplest).** Run the install script above; Codex reads
`~/.agents/skills` at user scope and auto-invokes a skill when your task matches its `description`
("implicit invocation"). You can also type `$` to invoke one explicitly.

**Path B — plugin marketplace (Claude-like UX).** A Codex plugin wrapper ships at
`kit/.codex-plugin/plugin.json` (points at the same `./skills/`), with a marketplace manifest at
`kit/.agents/plugins/marketplace.json`. Register and install:

```
codex plugin marketplace add <path-to>/kit
# then browse & install "physkit" via /plugins (TUI) or the Codex app
```

> ⚠️ **Validation status.** Codex was **not installed on the authoring machine**, so Path B's manifests
> were written to Codex's documented schema but not locally verified. Before relying on them, validate
> on a machine with Codex and adjust if the schema has moved. Path A (skills directory) uses only the
> documented user-scope location and is the safer default.

---

## OpenCode — verified

OpenCode implements the same `SKILL.md` standard and loads skills on demand via its native `skill`
tool. It scans several locations, including `~/.agents/skills`, project `.agents/skills` / `.opencode/skills`,
and — for compatibility — `~/.claude/skills` and project `.claude/skills`.

Install with the script above (target `~/.agents/skills`), or point it at OpenCode's own global dir:

```bash
kit/scripts/install-skills.sh --target ~/.config/opencode/skills
```

Verify discovery with **zero model cost**:

```bash
opencode debug skill        # lists every discovered skill and its file location
```

> ✅ **Verified**: on OpenCode v1.2.21 (Windows), `opencode debug skill` discovered all 23 PhysKit
> skills after the install script placed them, alongside the harness's other skills.

---

## Gemini CLI

Per its documentation, Gemini CLI is based on the same Agent Skills standard and reads
`~/.agents/skills` (and `.agents/skills` at project scope). The install script's default target
therefore covers it. *(Not locally validated — Gemini CLI was not installed on the authoring machine.)*

---

## Known limitation: skill-name collisions

Inside the Claude Code plugin, skills are namespaced (`physkit:verify`). When copied into a shared
skills directory like `~/.agents/skills`, they are **un-namespaced** (`verify`, `report`, `debug`, …).
If your harness already ships a built-in skill or another installed skill with the same name, they can
collide. If you hit this, install into a project-scoped `.agents/skills` for the repo where you want
PhysKit, or rename on copy. A namespacing convention for the portable build is a candidate for a later
phase.

---

## What this did and did not touch

- **Added** (new files only): `kit/.codex-plugin/plugin.json`, `kit/.agents/plugins/marketplace.json`,
  `kit/scripts/install-skills.{sh,ps1}`, and this doc.
- **Unchanged**: every file under `kit/skills/` and `kit/.claude-plugin/` is byte-for-byte identical to
  before (verified by content hash). No skill's scientific content was altered.
