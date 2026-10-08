---
name: improve-kit
description: >-
  Apply vetted kit changes to your own copy of the kit with bucketed sign-off (AUTO / SIGN-OFF /
  MORE-CONTEXT), threaded across every locus and logged; the integrity core is frozen.
---

# improve-kit — apply scaffolding changes, augmented not autonomous

The kit improves by feeding real-run lessons back into its skills, templates, and doctrine. Full automation of
that loop causes drift — like a trainer that only ever works your chest: it *feels* like improvement while it
quietly breaks you. So this skill keeps the human on the high-stakes calls via **three buckets**, and
**freezes the integrity core** so speed never erodes rigor (the constitution in `docs/CORE.md`).

> **Stance.** *You are editing the thing that steers every future campaign.* Change the **kit source**
> (`templates/…`, `skills/…`, `docs/…`), never a generated campaign's copy (that is a historical record),
> and write it the way `docs/reference/kit-development.md` describes: altitude and voice, one statement
> per rule, every place a concept appears threaded, outside material cited and adapted, never reproduced.
> Every change **cites the run/finding that motivated it** — close the loop back to the review.

## Find the copy you will edit (first)
Paths in this skill are relative to the **kit root**: the folder holding `.claude-plugin/`, `skills/`,
`templates/`, and `docs/` (in a development monorepo it may be a subdirectory, e.g. `kit/`).
- **Edit a copy you own, not an installed one.** A plugin installed from a marketplace is a cached copy in
  the harness's plugin store (for Claude Code, under `~/.claude/plugins/cache/`), replaced on every update,
  and the skills-only projection (`~/.agents/skills`, from `scripts/install-skills.sh` or `.ps1`) is a copy
  without the templates or docs. An edit to either is silently lost. If that is all there is, stop and help the user make
  their own: clone or fork the PhysKit repository and load its kit root instead.
- **Make the edits reach the harness.** `claude --plugin-dir <kit root>` reads the checkout live. A
  persistent install is itself a cached copy: after editing, refresh it (`/plugin marketplace update physkit`
  in Claude Code; `codex plugin add physkit@physkit` in Codex, then a new task). The README's Install section
  has both routes.
- **Prefer a git checkout on a branch.** Keeping local changes on their own branch lets the user merge a
  newer upstream release without losing them, and gives every change a commit to cite.
- **Know what campaigns inherit.** A change reaches new campaigns at scaffold time. An existing campaign keeps
  the kit version stamped in its `campaign.md` header until it is upgraded deliberately
  (`skills/new-campaign/scripts/upgrade_campaign.py`).

## Inputs
- **The proposed changes** — ideally the keeper table from a `campaign-review` report (`kit_review.md` in the
  campaign directory, §4), or an ad-hoc request ("improve this skill based on this conversation"). Each
  should carry: what, where (target kit file), why, and the **evidence** behind it.
- **The kit source** — templates, skills, docs — and its change log (below).

## The three buckets (triage every proposed change)
1. **AUTO — apply, then log.** Cosmetic or clarifying only, *cannot change behavior or doctrine*: a typo, a
   dead/stale link, a formatting fix, a clarifying sentence, a missing cross-reference. Apply it and log it;
   no sign-off needed.
2. **SIGN-OFF — propose, get explicit approval, then apply.** The default for anything that changes behavior:
   editing a skill's instructions, changing a template / gate / hook / default value, adding or removing a
   skill, altering a principle. Present a concise **change proposal** (below) and wait for an explicit
   *approve* before editing. Offer three responses: **Approve / Reject / Approve and don't ask again for this
   class.**
3. **MORE-CONTEXT — surface the question.** Analyzed but undecidable alone (a genuine fork, a missing fact, a
   trade-off only the user can weigh). Ask; don't guess.

**Change proposal (sign-off bucket) — keep it tight:**
> **Change:** <what> · **Where:** <exact kit file(s) + section> · **Why:** <the lesson> ·
> **Evidence:** <the run/finding it traces to> · **Generality:** <what future failure, *different from the
> motivating one*, this would catch> · **Risk / blast-radius:** <what it could affect; which campaigns
> inherit it> · **Bucket rationale:** <why sign-off not auto>.

**The generality test (progressive vs. degenerating changes).** Before proposing any keeper, ask: *does this
change cover a failure class, or only re-describe the one incident that motivated it?* A change earns a place
in doctrine when it would catch future failures **different from** the motivating one (progressive); a patch
whose content is exhausted by the single observed case is a bandage (degenerating) — record it as a
campaign-specific landmine or a debug-catalog entry instead, or generalize it first. This is Lakatos's
progressive/degenerating problem-shift test (1970) applied to the scaffold: a research programme advances
when a revision predicts novel cases, and degenerates when revisions only absorb known anomalies ad hoc. Grow
the doctrine with rules that reach forward, not scar tissue that only points backward.

## Frozen core — never auto, never weakened
The **honesty / verification / integrity doctrine is frozen** (the CORE constitution; the `verify` gate and
`report`'s honesty standard; the frozen-metric and no-fabrication rules; the promotion guard). A proposed
change that would relax integrity, loosen verification, make a metric gameable, or remove a guard is
**rejected outright** — not bucketed, not applied even with sign-off — unless the user is explicitly and
deliberately re-deciding doctrine (then it is a SIGN-OFF with a loud flag and a `record-decision` entry).
Outside CORE, the frozen core's working text lives in `verify` (§2, §5b, the verdicts, campaign-mode
promotion) and `report` (Standard 2, Honest); those passages may only be tightened. Context economy is
doctrine but not frozen: how much context helps tracks model capability. When self-improving the
doctrine, **evaluate the change on held-out tasks**, not only on the incident that motivated it, so a gain
on one case can't silently regress rigor elsewhere.

## Apply discipline
- **Write it per the guide.** Read `docs/reference/kit-development.md` before the first edit: where a rule
  lives (the kit source, one statement per rule, CORE's routing table as the map), how kit text is written
  (rules as behaviors, why first, altitude, readable by someone outside the work), threading every place a
  concept appears, and bringing in outside material (cite and adapt, never reproduce).
- **Record the why** for any non-obvious change to doctrine or a default — the reason, its provenance (the
  motivating run), and a revisit-if trigger, in the `record-decision` format — in that change's
  `LOCAL_CHANGES.md` entry.

## Record & validate (close the loop)
- **Log every change** (auto and approved) in `LOCAL_CHANGES.md` at the kit root (create it on first use):
  date, what changed, the file(s), the motivating run/finding, and the bucket. It is your copy's change log,
  and the record of how it differs from upstream. If the project's `CLAUDE.md` names a different log, use
  that.
- **Close out the keeper.** When a change came from a `campaign-review` keeper, **mark that keeper's row in
  the review's keeper table `applied`** (or `rejected`, with the reason) and note the commit or date. A keeper
  left `pending` after you acted on it — or a change applied without being recorded against its keeper — is
  the leak this skill exists to prevent: an unfolded keeper lets the same bug recur in the next campaign. The
  loop is closed only when every consumed keeper reads applied/rejected.
- **Check it** as the guide's *Checking a change* section says: templates through the campaign validator,
  doctrine on held-out tasks with a fresh-agent review, prompts and roles through the prompt-surface audit.
- **Note the kit version** (commit) the change landed in, so a future `campaign-review` targets current text.
  A new campaign stamps the plugin version and the checkout's commit, so edits left uncommitted are invisible
  in that stamp: offer to commit them on the user's branch before the next scaffold, or note in
  `LOCAL_CHANGES.md` which campaigns were scaffolded over uncommitted edits.
- **Don't commit or push** unless asked; if asked, branch first.

## Composition
- Consumes **`campaign-review`** output (the keeper table).
- Uses the **`record-decision`** format for the change rationale + provenance (kept in `LOCAL_CHANGES.md`).
- Follows **`docs/reference/kit-development.md`** for how the change is written, sourced, and checked.
- Pairs with version control (`docs/reference/version-control.md`) — the change log is the baseline even
  without a commit.

## Checklist
- [ ] Editing a **copy you own** (a checkout, ideally on a branch), not an installed copy; edits reach the harness.
- [ ] Every change **triaged** into auto / sign-off / more-context; sign-off changes **approved before** editing.
- [ ] Every keeper passed the **generality test** — it covers a failure class beyond its motivating incident (progressive), not an ad hoc patch (degenerating).
- [ ] **No change weakens** the honesty/verification/integrity core (rejected, not bucketed).
- [ ] Edited the **kit source**, not a generated campaign copy, written per `kit-development.md`.
- [ ] **Threaded** — grepped for the old wording; no stale references left behind.
- [ ] **Logged** with motivating evidence; consumed keepers marked applied/rejected; the change **checked**.
- [ ] Non-obvious doctrine/default changes carry their **why, provenance, and revisit-if** in the log.
