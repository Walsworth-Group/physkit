# Installing PhysKit across agent harnesses

PhysKit's skills are authored to the open **Agent Skills** standard (`SKILL.md` with `name` +
`description` frontmatter and progressive disclosure). Several agent CLIs read that standard natively,
so the same skills that power PhysKit on Claude Code also run on Codex, OpenCode, and Gemini CLI, with
the same behavior: the skill whose `description` matches the task loads automatically.

This document covers installing on each. The Claude Code flow is unaffected. Support for the other
harnesses consists of additional files only; no skill content and no Claude packaging changes to enable
it.

> **Single source of truth.** `kit/skills/` is the one canonical copy of every skill. The Codex plugin
> wrapper points at it directly; the install script projects it into other tools' directories. After
> updating the kit (`git pull`), re-run the install script to refresh those copies, or install with
> `--link` / `-Link` to symlink instead of copy so the copies never drift.

---

## Claude Code — unchanged

The Claude Code flow is the same as it has always been. Install with:

```
claude plugin marketplace add <path-to>/kit
claude plugin install physkit@physkit
```

Skills appear as `physkit:<name>` and load on demand. This is the reference installation.

---

## The one-location shortcut: `~/.agents/skills`

Codex, OpenCode, and Gemini CLI all scan `~/.agents/skills` at user scope, so a single install covers
all three. From the kit root:

```bash
# macOS / Linux
kit/scripts/install-skills.sh

# Windows (PowerShell)
kit\scripts\install-skills.ps1
```

Both scripts copy every PhysKit skill into `~/.agents/skills/` and are idempotent. Options:

| Option | Effect |
|---|---|
| `--target DIR` / `-Target DIR` | Install into a different skills directory |
| `--link` / `-Link` | Symlink instead of copy (live-linked, never drifts; Windows needs Developer Mode) |
| `--uninstall` / `-Uninstall` | Remove the PhysKit skills from the target |

Then start (or restart) your harness; it will discover the skills on launch.

---

## Codex

**Path A — skills directory (recommended, simplest).** Run the install script above. Codex reads
`~/.agents/skills` at user scope and invokes a skill when the task matches its `description`; Codex
calls this implicit invocation. Typing `$` invokes a skill explicitly.

**Path B — plugin marketplace (Claude-like UX).** A Codex plugin wrapper ships at
`kit/.codex-plugin/plugin.json` and points at the same `./skills/`, with a marketplace manifest at
`kit/.agents/plugins/marketplace.json`. Register and install:

```
codex plugin marketplace add <path-to>/kit
# then browse & install "physkit" via /plugins (TUI) or the Codex app
```

> **Validation status.** Path B's manifests follow Codex's documented schema and have not been validated
> against a running Codex. Validate them on a machine with Codex before relying on them, and adjust if
> the schema has moved. Path A uses only the documented user-scope location and is the safer default.

---

## OpenCode — verified

OpenCode implements the same `SKILL.md` standard and loads skills on demand via its native `skill`
tool. It scans several locations: `~/.agents/skills`, project `.agents/skills` and `.opencode/skills`,
and, for compatibility, `~/.claude/skills` and project `.claude/skills`.

Install with the script above (target `~/.agents/skills`), or point it at OpenCode's own global dir:

```bash
kit/scripts/install-skills.sh --target ~/.config/opencode/skills
```

Verify discovery without spending model tokens:

```bash
opencode debug skill        # lists every discovered skill and its file location
```

> **Verified.** This path has been validated against a running OpenCode: `opencode debug skill` lists
> every PhysKit skill after the install script places them, alongside the harness's other skills.

---

## Gemini CLI

Per its documentation, Gemini CLI is based on the same Agent Skills standard and reads
`~/.agents/skills`, and `.agents/skills` at project scope. The install script's default target therefore
covers it. This path has not been validated against a running Gemini CLI.

---

## Known limitation: skill-name collisions

Inside the Claude Code plugin, skills are namespaced (`physkit:verify`). When copied into a shared
skills directory such as `~/.agents/skills`, they are un-namespaced: `verify`, `report`, `debug`, and so
on. A built-in skill of the harness, or another installed skill of the same name, collides with them. On
a collision, install into a project-scoped `.agents/skills` for the repository that needs PhysKit, or
rename on copy.

---

## What this did and did not touch

- **Added** (new files only): `kit/.codex-plugin/plugin.json`, `kit/.agents/plugins/marketplace.json`,
  `kit/scripts/install-skills.{sh,ps1}`, and this doc.
- **Unchanged**: every file under `kit/skills/` and `kit/.claude-plugin/` is byte-for-byte identical
  to before, verified by content hash. No skill's scientific content was altered.
