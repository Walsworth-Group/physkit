# PhysKit (`physkit`)

A Claude Code **plugin** for rigorous physical-science research. It has two layers:

- **General science toolkit** — skills for framing problems, verifying results, designing and validating
  simulations, dimensional analysis, deriving theory, debugging, and honest reporting. Useful in *any*
  session.
- **Campaign layer** — scaffolds and runs autonomous-research loops (hypothesize → run → evaluate → log
  → verify → repeat), with a frozen honesty/verification core.

Once installed, the skills appear as `/physkit:<name>` in every project.

## Install

**Quick test (no install, picks up edits live):**
```
claude --plugin-dir "<path-to-this-folder>"
```

**Persistent install from this repo (GitHub):**
```
/plugin marketplace add <OWNER>/<REPO>
/plugin install physkit@physkit
```

**Persistent install from a local/shared-drive copy:**
```
/plugin marketplace add "<path-to-this-folder>"
/plugin install physkit@physkit
```

Then run `/reload-plugins` and confirm with `/plugin list`.

See **[GETTING_STARTED.md](GETTING_STARTED.md)** for the full walkthrough, including how to stand up and
launch an autonomous campaign.

## Layout

```
.claude-plugin/   plugin.json + marketplace.json (the manifests)
skills/           the 17 skills (general + campaign), each a SKILL.md
docs/             always-on spine (CORE, PRINCIPLES) + on-demand reference docs
templates/        campaign scaffold materialized by /physkit:new-campaign
examples/         illustrative filled program charters
```
