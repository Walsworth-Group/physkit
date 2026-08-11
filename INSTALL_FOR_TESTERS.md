# Testing PhysKit

PhysKit adds physics-research skills (`/physkit:verify`, `/physkit:frame-problem`, `/physkit:report`, …)
plus a rigor/honesty doctrine that stays loaded in every prompt. This is a one-time install — after Step 1
it works in the terminal **and** the Claude desktop app, in any project, from then on.

**Before you start:** `claude` runs in a terminal, and you have the kit available one of two ways —
either your G: drive (Google Drive) is mounted, **or** you were handed a `physkit-kit.zip` file. Both
paths are covered below; use whichever matches how you got the kit. Either way, you need a `<KIT_DIR>`:
the full path to the `kit` folder.

- **Google Drive:** `<KIT_DIR>` is
  `G:\Shared drives\PHYS - Walsworth Group\Experiment folders\Machine Learning\physkit-dev\physkit-internal\kit`
- **Zip file:** unzip `physkit-kit.zip` to a short local path with no spaces, e.g. `C:\physkit\kit` —
  right-click the zip → **Extract All…** → set the destination to `C:\physkit`. `<KIT_DIR>` is that
  extracted `kit` folder, e.g. `C:\physkit\kit`. (Don't run commands from inside the zip's own file-explorer
  preview — extract fully first, or Claude Code will read a stale/partial copy.)

---

## Step 1 — Install the plugin (one time, ~1 minute)

Open a terminal (any folder is fine) and run these **three commands, one at a time** — press Enter after
each and wait for it to finish before typing the next. Substitute your own `<KIT_DIR>` from above:

```
/plugin marketplace add "<KIT_DIR>"
```
> If a box titled **"Enter marketplace source"** pops up instead, that means the quotes didn't paste through.
> Type just the path with no quotes, then Enter: `<KIT_DIR>`

```
/plugin install physkit@physkit
```
```
/reload-plugins
```

Done — physkit is now installed for you everywhere, including the desktop app. (Testing an older
`autoresearch`-named version? Remove it first: `/plugin marketplace remove autoresearch`.)

> **Zip testers:** the install is a snapshot of the zip's contents at extract time — it does **not**
> update itself. If you're given a newer zip later, extract it over the same `<KIT_DIR>` and run
> `/plugin marketplace update physkit` to pick up the changes.

## Step 2 — Turn on the doctrine in your project

The plugin gives you the *skills*. To also keep the rigor/honesty doctrine in context on every turn (it
works like an always-on system prompt), each project you test in needs one file.

In your project folder, create a file named `CLAUDE.md` containing this one line (same `<KIT_DIR>` as
Step 1):
```
@<KIT_DIR>\docs\CORE.md
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
`/physkit:new-campaign` — it creates a project home around the campaign (see `GETTING_STARTED.md`).

---

## Windows gotchas
- **"Filename too long"**: run `git config --global core.longpaths true`, and install big packages
  (TensorFlow/PyTorch) into a venv at a short path like `C:\venvs\physkit`, not the shared drive or the
  zip's extract folder.
- **Python**: use `py -3.x`, not `python3` (often a broken Windows Store stub).
- **No symlinks on Google Drive**: copy files instead of linking them.
- **Zip extracted to a long/nested path** (e.g. straight out of Downloads with a version-numbered subfolder):
  move it to something short like `C:\physkit\kit` — long paths cause the same "filename too long" errors
  as the shared drive.

Please flag anything confusing or broken — thanks for testing!
