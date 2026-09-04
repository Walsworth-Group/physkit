# Installing PhysKit across agent harnesses

PhysKit's skills are authored to the open **Agent Skills** standard (`SKILL.md` with `name` +
`description` frontmatter and progressive disclosure). Several agent CLIs read that standard natively,
so the same general skills can load on Claude Code, Codex, OpenCode, and Gemini CLI. Campaign skills also
need PhysKit's package-level templates, doctrine, scripts, and validators; install a full supported plugin
for those rather than projecting `skills/` alone.

This document covers installing on each. The Claude Code packaging and install flow remain separate and
unchanged; shared skill instructions use package-relative resource links so either full plugin can load
the same docs, templates, scripts, and validators.

> **Single source of truth.** `kit/skills/` is the one canonical copy of every skill. The Codex plugin
> wrapper points at it directly; the skills-only installer projects skill folders into other tools'
> directories. After updating the kit (`git pull`), reinstall the plugin or refresh those copies.

---

## Claude Code — unchanged

The Claude Code flow is the same as it has always been. Install with:

```
claude plugin marketplace add <path-to>/kit
claude plugin install physkit@physkit
```

Skills appear as `physkit:<name>` and load on demand. This is the supported Claude installation.

---

## Codex — full campaign-capable plugin (recommended)

A Codex manifest at `kit/.codex-plugin/plugin.json` points at the canonical `./skills/`, and the local
marketplace lives at `kit/.agents/plugins/marketplace.json`. Register and install:

```
codex plugin marketplace add <path-to>/kit
codex plugin add physkit@physkit
```

Confirm with `codex plugin list`, then start a new Codex task so it loads the refreshed plugin context.
Skills appear as `$physkit:<name>` and can also be selected implicitly from their descriptions.

For an update from the same local checkout, do not register the marketplace again. Refresh the cached
package with `codex plugin add physkit@physkit`, verify it with
`codex plugin list --marketplace physkit`, and start a new task.

This is the supported Codex path for campaigns. The installed package includes `templates/`, `docs/`,
validators, and generated-loop scripts alongside `skills/`; `new-campaign` refuses to use an unrelated
source checkout when that dependency closure is absent.

---

## Skills-only projection: `~/.agents/skills` (general work only)

Codex, OpenCode, and Gemini CLI scan `~/.agents/skills` at user scope. From the kit root:

```bash
# macOS / Linux
./scripts/install-skills.sh

# Windows (PowerShell)
powershell -ExecutionPolicy Bypass -File .\scripts\install-skills.ps1
```

Both scripts copy the PhysKit skill folders into `~/.agents/skills/`. Options:

| Option | Effect |
|---|---|
| `--target DIR` / `-Target DIR` | Install into a different skills directory |
| `--link` / `-Link` | Symlink instead of copy (live-linked, never drifts; Windows needs Developer Mode) |
| `--uninstall` / `-Uninstall` | Remove the PhysKit skills from the target |

Then start or restart the harness. This projection omits package-level `templates/` and `docs/`, so its
supported scope is the general science toolkit—not campaign scaffolding or closed-loop operation. Some
campaign skill names may still be discovered because the scripts copy skill folders; when their package
resources are absent, they must stop and direct the user to the full plugin rather than fall back to a
source tree.

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
on. A built-in skill of the harness, or another installed skill of the same name, collides with them.
The current projection scripts replace same-named destination folders and their uninstall mode removes
those names; inspect the target first and do not use this path where a collision exists. Collision-safe
ownership tracking is deferred for cross-harness maintainer review. Prefer the namespaced full Codex or
Claude plugin.

---

## Package boundaries

- The Claude manifests and install commands are independent of the Codex wrapper and remain unchanged.
- The two full plugins ship the same canonical skills and package resources. Cross-harness edits are
  limited to resource lookup and loader-valid routing metadata; scientific policy is shared.
- The skills-only projection is not a second package authority and is not campaign-capable.
