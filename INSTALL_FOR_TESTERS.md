# Testing PhysKit (Claude Code plugin)

*A copy-paste install guide to share with colleagues testing the kit.*

PhysKit adds physics-research skills — framing, verification, simulation V&V, debugging, honest reporting —
as `/physkit:<name>` commands, plus a `CLAUDE.md` you drop into a project to keep the rigor/honesty doctrine
always in context.

**Before you start:** make sure `claude` runs in your terminal and the PHYS shared drive is mounted. The kit
lives at:

`G:\Shared drives\PHYS - Walsworth Group\Experiment folders\Machine Learning\physkit-dev\physkit-internal\kit`

*(If your shared drive isn't `G:`, change the drive letter.)*

---

## Step 1 — Put the doctrine in your project
1. Pick the project folder you'll work in.
2. Copy this file from the kit:
   `…\physkit-internal\kit\templates\CLAUDE.general.md`
3. Paste it into your project folder and **rename the copy to `CLAUDE.md`**.

## Step 2 — Start Claude with the plugin (easiest — do this one)
1. Open a terminal and `cd` into your project folder.
2. Launch Claude with the kit attached — copy this **whole line, quotes included**:
   ```
   claude --plugin-dir "G:\Shared drives\PHYS - Walsworth Group\Experiment folders\Machine Learning\physkit-dev\physkit-internal\kit"
   ```
   That loads the skills for the session **and** auto-loads your project `CLAUDE.md`. Skip to Step 4.

*(This avoids the install dialog. Only do Step 3 if you'd rather install it permanently so you don't pass
`--plugin-dir` each time.)*

## Step 3 — (optional) Install permanently
Run these as **three separate commands, one at a time**, at the normal chat prompt — do **not** paste them
together:

1. Add the marketplace (type the whole line, including quotes):
   ```
   /plugin marketplace add "G:\Shared drives\PHYS - Walsworth Group\Experiment folders\Machine Learning\physkit-dev\physkit-internal\kit"
   ```
   ⚠️ If a box pops up titled **"Enter marketplace source:"**, type **only the path — no quotes, nothing
   after it** — then Enter:
   `G:\Shared drives\PHYS - Walsworth Group\Experiment folders\Machine Learning\physkit-dev\physkit-internal\kit`
2. Install the plugin:
   ```
   /plugin install physkit@physkit
   ```
3. Activate it:
   ```
   /reload-plugins
   ```
*(If you tested the earlier version named `autoresearch`, remove it first: `/plugin marketplace remove autoresearch`.)*

## Step 4 — Check it worked
- `/plugin list` shows **physkit**.
- Typing `/physkit:` lists the skills (verify, frame-problem, report, …).
- `/context` shows `CLAUDE.md` loaded (the always-on doctrine).
- Sanity check: ask *"what's your frozen core?"* — it should recite it.

## Step 5 — Use it
Work normally — skills trigger on their own, or call them explicitly: `/physkit:verify`,
`/physkit:frame-problem`, `/physkit:report`. To stand up an autonomous research campaign, run
`/physkit:new-campaign` (see `GETTING_STARTED.md`).

## Windows gotchas (save yourself some time)
- **Long paths:** the shared-drive path is long, so pip installs of big wheels (TensorFlow/PyTorch) and some
  git operations can fail with "Filename too long". Fixes: `git config --global core.longpaths true`, and
  install heavyweight packages into a venv at a SHORT path (e.g. `C:\venvs\physkit`).
- **Use `py -3.x`**, not `python3` (which is often a non-functional Windows Store stub).
- **Symlinks:** Google Drive File Stream doesn't support them — copy files instead of linking.

Please flag anything confusing or broken — thanks for testing!
