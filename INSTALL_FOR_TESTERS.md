# Testing PhysKit

PhysKit adds physics-research skills (`/physkit:verify`, `/physkit:frame-problem`, `/physkit:report`, …)
plus a rigor/honesty doctrine that stays loaded in every prompt. The install is one-time: after Step 1 the
skills are available in the terminal and in the Claude desktop app, in any project.

Before you start: `claude` runs in a terminal, and you have the kit either from the mounted shared Google
Drive or from a `physkit-kit.zip` file. Both paths are covered below. Either way you need a `<KIT_DIR>`:
the full path to the `kit` folder.

- **Google Drive:** `<KIT_DIR>` is
  `G:\Shared drives\PHYS - Walsworth Group\Experiment folders\Machine Learning\physkit-dev\physkit-internal\kit`
- **Zip file:** unzip `physkit-kit.zip` to a short local path with no spaces, e.g. `C:\physkit\kit`.
  Right-click the zip, choose Extract All…, and set the destination to `C:\physkit`. `<KIT_DIR>` is that
  extracted `kit` folder, e.g. `C:\physkit\kit`. Extract fully before running any command: running from
  inside the zip's own file-explorer preview makes Claude Code read a stale or partial copy.

---

## Step 1 — Install the plugin (one time, ~1 minute)

Open a terminal (any folder is fine) and run these three commands one at a time. Press Enter after each and
wait for it to finish before typing the next. Substitute your own `<KIT_DIR>` from above.

```
/plugin marketplace add "<KIT_DIR>"
```
> If a box titled "Enter marketplace source" appears instead, the quotes did not paste through. Type the
> path with no quotes, then press Enter: `<KIT_DIR>`

```
/plugin install physkit@physkit
```
```
/reload-plugins
```

physkit is now installed everywhere, including the desktop app. If an older `autoresearch`-named
version is installed, remove it first: `/plugin marketplace remove autoresearch`.

> Zip testers: the install is a snapshot of the zip's contents at extract time and does not update itself.
> To pick up a newer zip, extract it over the same `<KIT_DIR>` and run `/plugin marketplace update physkit`.

## Step 2 — Turn on the doctrine in your project

The plugin gives you the skills. Each project you test in needs one more file to keep the rigor/honesty
doctrine in context on every turn; it works like an always-on system prompt.

In your project folder, create a file named `CLAUDE.md` containing this one line (same `<KIT_DIR>` as
Step 1):
```
@<KIT_DIR>\docs\CORE.md
```
Claude Code re-reads `CLAUDE.md` every turn, so the doctrine never falls out of context. Check with
`/context`. If the `@import` line does not take, paste the contents of `CORE.md` directly into your
`CLAUDE.md` instead.

## Step 3 — Check it worked

- `/plugin list` → shows physkit
- Type `/physkit:` → lists the skills
- `/context` → shows your `CLAUDE.md` is loaded
- Ask "what's your frozen core?" → it recites the doctrine

## Step 4 — Use it (CLI or desktop app)

Work normally. Skills trigger on their own, or call them directly: `/physkit:verify`,
`/physkit:frame-problem`, `/physkit:report`. To start a full autonomous research campaign, run
`/physkit:new-campaign`; it creates a project home around the campaign (see `GETTING_STARTED.md`).

---

## Windows gotchas
- **"Filename too long"**: run `git config --global core.longpaths true`, and install big packages
  (TensorFlow/PyTorch) into a venv at a short path like `C:\venvs\physkit`, not the shared drive or the
  zip's extract folder.
- **Python**: use `py -3.x`, not `python3` (often a broken Windows Store stub).
- **No symlinks on Google Drive**: copy files instead of linking them.
- **Zip extracted to a long or nested path** (e.g. straight out of Downloads with a version-numbered
  subfolder): move it to something short like `C:\physkit\kit`. Long paths cause the same "filename too
  long" errors as the shared drive.

Report anything confusing or broken.
