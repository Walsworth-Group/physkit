# Installing PhysKit on other agents

PhysKit's skills follow the open **Agent Skills** standard (`SKILL.md` with `name` and `description`
frontmatter, loaded on demand), so the same skills run in several agent CLIs. There are two ways to
install:

- **The full plugin** (Claude Code, Codex) — the skills plus the templates, docs, scripts, and validators
  they read. This is the only install that can scaffold and run campaigns. Commands are in the README's
  [Install](../README.md#install) section.
- **A skills-only copy** (OpenCode, Gemini CLI, or Codex without the plugin) — the skill folders alone,
  for the general science toolkit.

## Skills-only copy: `~/.agents/skills`

OpenCode, Gemini CLI, and Codex scan `~/.agents/skills` at user scope. From a clone of this repository:

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
| `--link` / `-Link` | Symlink instead of copy, so a `git pull` updates it (Windows needs Developer Mode) |
| `--uninstall` / `-Uninstall` | Remove the PhysKit skills from the target |

Then start or restart the agent. After updating your clone, re-run the script (unless you used
`--link`).

This copy omits `templates/` and `docs/`, so it covers the general science toolkit, not campaign
scaffolding or the closed loop. The campaign skills are still copied; without their package resources
they stop and point you to the full plugin.

### OpenCode

OpenCode loads `SKILL.md` skills on demand through its `skill` tool and scans `~/.agents/skills`, project
`.agents/skills` and `.opencode/skills`, and, for compatibility, `~/.claude/skills` and project
`.claude/skills`. The default target above works, or install into OpenCode's own directory:

```bash
./scripts/install-skills.sh --target ~/.config/opencode/skills
```

List what it discovered, without spending model tokens:

```bash
opencode debug skill
```

### Gemini CLI

Gemini CLI follows the same standard and reads `~/.agents/skills` (and `.agents/skills` in a project),
so the default target covers it. This path has not been tested against a running Gemini CLI.

## Skill-name collisions

In the Claude Code and Codex plugins, skills are namespaced (`/physkit:verify`, `$physkit:verify`). In a
shared skills directory they are not: `verify`, `report`, `debug`, and so on. A built-in skill or another
installed skill with the same name collides with them. The scripts replace same-named folders in the
target, and `--uninstall` removes those names, so check the target first and avoid this route where a
collision exists. The namespaced plugins have no such problem.
