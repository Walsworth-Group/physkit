# Testing PhysKit

PhysKit adds physics-research skills (`/physkit:verify`, `/physkit:frame-problem`, `/physkit:report`, …)
plus a rigor/honesty doctrine that stays loaded in every prompt. This is a one-time install — after Step 1
it works in the terminal **and** the Claude desktop app, in any project, from then on.

**Before you start:** your G: drive (Google Drive) is mounted, and `claude` runs in a terminal.

---

## Step 1 — Install the plugin (one time, ~1 minute)

Open a terminal (any folder is fine) and run these **three commands, one at a time** — press Enter after
each and wait for it to finish before typing the next:

```
/plugin marketplace add "G:\Shared drives\PHYS - Walsworth Group\Experiment folders\Machine Learning\physkit-dev\physkit-internal\kit"
```
> If a box titled **"Enter marketplace source"** pops up instead, that means the quotes didn't paste through.
> Type just the path with no quotes, then Enter:
> `G:\Shared drives\PHYS - Walsworth Group\Experiment folders\Machine Learning\physkit-dev\physkit-internal\kit`

```
/plugin install physkit@physkit
```
```
/reload-plugins
```

Done — physkit is now installed for you everywhere, including the desktop app. (Testing an older
`autoresearch`-named version? Remove it first: `/plugin marketplace remove autoresearch`.)

## Step 2 — Turn on the doctrine in your project

The plugin gives you the *skills*. To also keep the rigor/honesty doctrine in context on every turn (it
works like an always-on system prompt), each project you test in needs one file.

In your project folder, create a file named `CLAUDE.md` containing this one line:
```
@G:\Shared drives\PHYS - Walsworth Group\Experiment folders\Machine Learning\physkit-dev\physkit-internal\kit\docs\CORE.md
```
Claude Code re-reads `CLAUDE.md` every turn, so the doctrine never falls out of context. (If that `@import`
line doesn't seem to take — check with `/context` — paste the contents of `CORE.md` directly into your
`CLAUDE.md` instead.)

## Step 3 — Check it worked

- `/plugin list` → shows **physkit**
- Type `/physkit:` → lists the skills
- `/context` → shows your `CLAUDE.md` is loaded
- Ask *"what's your frozen core?"* → it should recite the doctrine

## Step 4 — Use it (CLI or desktop app)

Just work normally — skills trigger on their own, or call them directly: `/physkit:verify`,
`/physkit:frame-problem`, `/physkit:report`. To start a full autonomous research campaign, run
`/physkit:new-campaign` (see `GETTING_STARTED.md`).

---

## Windows gotchas
- **"Filename too long"**: run `git config --global core.longpaths true`, and install big packages
  (TensorFlow/PyTorch) into a venv at a short path like `C:\venvs\physkit`, not the shared drive.
- **Python**: use `py -3.x`, not `python3` (often a broken Windows Store stub).
- **No symlinks on Google Drive**: copy files instead of linking them.

Please flag anything confusing or broken — thanks for testing!
