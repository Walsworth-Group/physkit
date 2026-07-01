# Testing PhysKit (Claude Code plugin)

*A copy-paste install guide to share with colleagues testing the kit.*

PhysKit adds physics-research skills — framing, verification, simulation V&V, debugging, honest reporting —
as `/physkit:<name>` commands, plus a `CLAUDE.md` you drop into a project to keep the rigor/honesty doctrine
always in context.

**Before you start:** make sure `claude` runs in your terminal and the PHYS shared drive is mounted. The kit
lives at:

`G:\Shared drives\PHYS - Walsworth Group\Experiment folders\Machine Learning\Autoresearch paper\Auto Research Paper\kit`

*(If your shared drive isn't `G:`, change the drive letter.)*

---

## Step 1 — Put the doctrine in your project
1. Pick the project folder you'll work in.
2. Copy this file from the kit:
   `…\Auto Research Paper\kit\templates\CLAUDE.general.md`
3. Paste it into your project folder and **rename the copy to `CLAUDE.md`**.

## Step 2 — Start Claude with the plugin (easiest — do this one)
1. Open a terminal and `cd` into your project folder.
2. Launch Claude with the kit attached — copy this **whole line, quotes included**:
   ```
   claude --plugin-dir "G:\Shared drives\PHYS - Walsworth Group\Experiment folders\Machine Learning\Autoresearch paper\Auto Research Paper\kit"
   ```
   That loads the skills for the session **and** auto-loads your project `CLAUDE.md`. Skip to Step 4.

*(This avoids the install dialog. Only do Step 3 if you'd rather install it permanently so you don't pass
`--plugin-dir` each time.)*

## Step 3 — (optional) Install permanently
Run these as **three separate commands, one at a time**, at the normal chat prompt — do **not** paste them
together:

1. Add the marketplace (type the whole line, including quotes):
   ```
   /plugin marketplace add "G:\Shared drives\PHYS - Walsworth Group\Experiment folders\Machine Learning\Autoresearch paper\Auto Research Paper\kit"
   ```
   ⚠️ If a box pops up titled **"Enter marketplace source:"**, type **only the path — no quotes, nothing
   after it** — then Enter:
   `G:\Shared drives\PHYS - Walsworth Group\Experiment folders\Machine Learning\Autoresearch paper\Auto Research Paper\kit`
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

Please flag anything confusing or broken — thanks for testing!
