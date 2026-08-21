# Migrating a campaign to a newer kit layout

Campaigns are **frozen with their doctrine**: a finished campaign wants the exact rules it ran under, so
nothing here runs automatically and nothing rewrites a campaign in place without being asked. Migrate only
a campaign you intend to keep working in.

Each section is a short procedure an agent can follow end to end. Newest layout first. If you are several
versions behind, work upward from the oldest section that matches your tree.

---

> **Reading the commands below on Windows:** `python` is the Microsoft Store alias stub on a stock
> install. It prints "Python was not found" and exits 49 without running the script. Use `py -3` there;
> `python` is correct on macOS and Linux. Every command in this file works either way with that
> substitution.

## To the consolidated project root — README + one overview + rules (kit ≥ v0.10.1, 2026-08-20, ADR-0015)

**Symptom.** The validator reports *"consolidated project still carries LINEAGE.md /
PROJECT_ORIENTATION.md"* or *"still has shared/"* on a half-migrated tree; or you want a five-file
project root (`PROJECT.md` · `PROJECT_ORIENTATION.md` · `LINEAGE.md` · `DISCOVERIES.md` ·
`CLAUDE.md` · `shared/`) brought down to the consolidated three (`README.md` · `PROJECT.md` ·
`CLAUDE.md`).

**What changed.** The project root consolidated (ADR-0015): `PROJECT.md` is THE overview — §Mission
(the old charter), §Standing constraints and the system/instrument/equations depth (the old
`PROJECT_ORIENTATION.md`, section names unchanged), §Updates from discoveries, §Durable decisions,
and §Lineage (the old `LINEAGE.md` tables) — edited by tier (OPEN vs GUARDED; project `CLAUDE.md`
rule 7). A short `README.md` front door carries the directory map, and nothing else does. The
project `DISCOVERIES.md` ledger is **retired**: verified findings live in the campaign that produced
them (journal §Findings + `results/verdicts/`), and the project layer is pointers — the §Lineage
verified-findings column and §Updates-from-discoveries entries citing the verdict by path. `shared/`
is retired for flat purpose-named dirs (`scripts/`, `models/`, …) created at first promotion; the
promotion mark is the §Lineage promotion line. **Era tolerance:** the current driver reads
`## Standing constraints` from `PROJECT.md` and falls back to `PROJECT_ORIENTATION.md`, and the
guard still gates any legacy `DISCOVERIES.md`, so an un-migrated project keeps working and a new
campaign scaffolds into it fine. Migrate for the reading surface, not out of necessity.

**What breaks.** Nothing in an un-migrated project. Do NOT migrate a project whose ACTIVE campaigns
were scaffolded before this change if you cannot re-verify them: their stamped drivers read
`../../PROJECT_ORIENTATION.md` directly, so deleting it breaks *their* preflight. Migrate projects
whose campaigns are done/archived, or whose campaigns are new-era.

**The procedure** (per project; the validator's errors double as the checklist):

1. Scaffold-fresh the two new files from the kit templates (`templates/project/README.md.tmpl`,
   `PROJECT.md.tmpl`), then **move** — do not rewrite — the content: the old `PROJECT.md` charter
   into §Mission; `PROJECT_ORIENTATION.md` wholesale into the matching sections (they kept their
   names); `LINEAGE.md`'s tables into §Lineage.
2. For each `DISCOVERIES.md` entry, add a §Updates-from-discoveries entry citing the same verdict
   artifact path, and make sure the finding's §Lineage row points at its campaign. Then either
   delete the ledger or keep it as read-only history — the guard gates it either way; the validator
   tolerates it.
3. Move each `shared/` artifact to a purpose-named project dir (`models/`, `scripts/`, …), keep its
   version tag, and add its §Lineage promotion line. Update consuming campaigns' `campaign.md`
   §Relationship paths. Delete `shared/`.
4. Delete `PROJECT_ORIENTATION.md` and `LINEAGE.md` (their content now lives in `PROJECT.md`; a
   surviving copy is a fork and the validator flags it). Update the project `CLAUDE.md` from its
   template (new paths + the edit-tier rule).
5. Run the validator on the project root; it detects the new layout and checks §Standing
   constraints, §Lineage indexing, and the retired-file flags:
   `python "<kit>/skills/new-campaign/scripts/validate_campaign.py" <project_root>`

---

## To the consolidated layout — one background document, seven campaign docs, one promotion gate (kit ≥ v0.10.0, 2026-08-20)

**Symptom.** The validator reports *"the project home predates the one-background-document merge: it
has shared/PHYSICS.md and no PROJECT_ORIENTATION.md"*, flags a campaign-level
`docs/PROJECT_ORIENTATION.md`, or reports *"README.md has no 'Setup status' section"*; a newly
scaffolded driver's `--preflight` refuses with *"../../PROJECT_ORIENTATION.md is missing or has no
'## Standing constraints' section"*.

**What changed — project level.** The background became ONE document: `shared/PHYSICS.md`,
`shared/CONVENTIONS.md`, `shared/INSTRUMENT.md`, and the project-root `ENGINEERING_NOTES.md` merged
into `<project>/PROJECT_ORIENTATION.md`, one section each; `shared/` now holds only promoted frozen
artifacts. The driver delivers the doc's `## Standing constraints` into every spawned prompt **by
value** and stamps the spawn prompt's hash into each experiment snapshot's manifest.

**What changed — campaign level.** `campaign.md` is now the whole signed-off contract, absorbing what
were separate files: the goal block and expectations (from the dissolved `docs/PROJECT_ORIENTATION.md`;
tasks go to the queue + JOURNAL NEXT), the campaign-specific verification checks (§Verification, from
`docs/VERIFICATION_PLAN.md` — the generic checklist was the `verify`/`correctness-suite` procedure
restated), and the landmines table + append-only decision record (§Known landmines + §Decision record,
from `docs/ENGINEERING_NOTES.md`). `README.md` is the cold-reader front door; `SETUP_TODO.md` is
retired without a replacement table — setup state is computed live by `--preflight` and the gates,
and README's §Setup status just points there. `DOCTRINE_SNAPSHOT.md` is retired for a kit-**version stamp** in
`campaign.md`'s header and atop `results/logbook.md` — the snapshot recorded only the doctrine spine
while skills, reference docs, and the driver also govern behavior; the version pin recovers the whole
tagged kit (ADR-0012). `INTAKE.md` and `tests/README.md` are retired outright; `docs/` no longer
exists. **`results/DISCOVERIES.md` dissolved into the journal's append-only `## Findings` section**
(V6): settled findings — positive, negative, disputes, REVISES retractions — live there, each citing
its verdict artifact, and consolidation never trims that section. The promotion hook narrowed to the
mechanical surfaces and was renamed `guard_promotion.py`: it gates `configs/RECOMMENDED.json` writes,
scoreboard `CONFIRMED`/`NEW BEST` tokens, and — newly, fail-closed — the **project** ledger
`<project>/DISCOVERIES.md`, whose entries must cite the source campaign's verdict by path
(`campaigns/<slug>/results/verdicts/<id>.json`) with that campaign's suite green. The journal's
Findings section is deliberately not hook-gated (it is working memory); `campaign-status` audits that
every entry's citation resolves.

**What breaks.** Nothing in an un-migrated tree that keeps its own driver — the old campaign's files
still point at paths it still has. The costs are the scattered reading surface and pointer-only
constraint delivery. Migrate a project you are still working in; leave finished campaigns frozen.

**The procedure** (per project; the validator's errors double as the checklist):

1. Create `<project>/PROJECT_ORIENTATION.md` from the kit template
   (`templates/project/PROJECT_ORIENTATION.md.tmpl`) and **move** — do not rewrite — the content:
   the physics inventory, a-priori bound, domain of validity, all unit/sign/frame/ordering
   conventions, known gotchas, and run-constraining rig parameters into `## Standing constraints`
   (keep it lean; it is delivered every cycle); target-of-study, predictive framework, system
   behavior into `## The system under study`; the rig characterization into `## The instrument`;
   equations, simulation methods, common techniques into `## Equations and methods`; the project
   `ENGINEERING_NOTES.md` ED entries into `## Durable decisions`; references into `## References`.
   Then delete the four merged project files.
2. For each **active** campaign, fold into `campaign.md`: the goal / decision-served / done-criteria /
   out-of-scope from `docs/PROJECT_ORIENTATION.md` (§Mission + §FROZEN), its expectations as a
   `## Loosely-held expectations` section, live tasks into `results/queue.json` "next" (with
   rationales) + the JOURNAL NEXT, field-positioning into the project document; the
   campaign-specific checks from `docs/VERIFICATION_PLAN.md` as a `## Verification` section (drop
   the generic checklist rows — they are the skills' procedure — and the bounds rows, which
   §The ONE metric already carries); the landmines table and ED entries from
   `docs/ENGINEERING_NOTES.md` as `## Known landmines` and a `## Decision record` tail. Delete the
   three files and the now-empty `docs/`.
3. Delete `SETUP_TODO.md` — its content is computed live by `--preflight` and the gates — and add a
   short `## Setup status` section to `README.md` pointing there (copy it from the current template);
   move any campaign-specific rows still open into the JOURNAL NEXT list. Delete `tests/README.md`
   too. Stamp the version: copy the kit version from
   `DOCTRINE_SNAPSHOT.md`'s banner (`generated: physkit vX.Y.Z …`) into a
   `> **Scaffolded by physkit vX.Y.Z (…)**` line in `campaign.md`'s header and at the top of
   `results/logbook.md`, then delete `DOCTRINE_SNAPSHOT.md`. Delete `INTAKE.md` after checking it
   holds no proposal the signed-off spec never resolved.
4. Move `results/DISCOVERIES.md`'s entries — D/N findings, REVISES retractions, dispute notes — into a
   `## Findings (settled — positive and negative; append-only, never trimmed)` section of
   `results/JOURNAL.md`, keeping every verdict citation verbatim, then delete the file. Swap the hook:
   copy the new `guard_promotion.py` template into `scripts/`, delete `guard_discoveries.py`, and
   repoint the command in `.claude/settings.json`. The guard is not in the frozen-core file set
   (`CORE_FILES_DEFAULT` is the scorer + the correctness suite), so the swap does not invalidate a
   recorded correctness green.
5. Fix the campaign `CLAUDE.md`: hard gate 1's promotion definition (current-best · scoreboard tokens ·
   the project ledger; findings recorded in the journal), the project-context block, and the §Where
   things live rows — the background doc row points at `../../PROJECT_ORIENTATION.md`, the verification
   / landmines / decision-record rows at their `campaign.md` sections, the settled-findings row at
   `results/JOURNAL.md` §Findings, the setup row at `README.md` §Setup status (the validator enforces
   that table; compare against a freshly scaffolded `CLAUDE.md`).
6. Decide the driver per campaign. By-value constraint delivery, the snapshot prompt-hash, and
   **per-block verification** (the driver spawns an independent verification agent after every
   completed unit or block, stamps the scoreboard's `verified` column from the verdict, and will not
   clear the block without it — `configs/loop.json` `campaign.verification`, default `per-block`)
   all live in `scripts/run_campaign.py`; a migrated campaign keeps the old behavior until you
   re-copy the new driver template and add the `verification` keys to its `campaign` block. Check
   `frozen_core` before swapping mid-campaign: if the driver is in the core file set, the swap
   changes the core hash and the recorded correctness green no longer applies.
7. Re-run the validator on the project root; it must PASS with zero issues.

---

## To the `campaign` block in `configs/loop.json` (kit ≥ V0/V1, 2026-08-18)

**Symptom.** Every experiment ends with `checks: N not runnable for this campaign`, and each
`results/checks_<NN>.json` lists `comparability`, and the change-vs-incumbent check keyed `noise_floor`,
as `unavailable`, run after run. `campaign-status` reports them as a standing blind spot rather than as
failures.

**What breaks.** Nothing, and the defaults exist to keep it that way. A `configs/loop.json` with no
`campaign` block reads as `prediction_mode` `range` and `noise_model` `stochastic`, which is the behaviour
every campaign already ran under. Blank comparability tags are missing coverage, not a failed check.
Grading them `fail` would raise a permanent red flag on every experiment of every campaign scaffolded
before the block existed, and a red flag no experiment can clear stops being read. An un-migrated campaign
is therefore degraded, never broken, and **this migration is not urgent**. What it costs:

- **Comparability certifies nothing.** A ranking claim is valid only within one (`metric_version`,
  `data_version`) pair. With no tags the check reports `unavailable` and names them, so no ordering of
  two rows in this campaign is machine-certified.
- **The change against the incumbent has no numeric threshold.** "Larger than noise" has no meaning
  until `noise_floor` (stochastic) or `tolerance` (deterministic) carries a number, so that check
  reports the delta as `unavailable` instead of pass or fail.

**What is new.** One top-level `"campaign"` key in `configs/loop.json`, beside `unit_cost`:

| key | legal values | left unset |
|---|---|---|
| `prediction_mode` | `range` · `direction` · `none` | reads `range` |
| `prediction_mode_reason` | free text; required when the mode is `none` | empty — a `none` with no reason is refused at launch |
| `noise_model` | `stochastic` · `deterministic` | reads `stochastic` |
| `noise_floor` | a JSON number ≥ 0, or `null` | `null` — the change-vs-incumbent check stays `unavailable` |
| `tolerance` | a JSON number ≥ 0, or `null` | `null` — the same, for a deterministic campaign |
| `metric_version` · `data_version` | free strings, conventionally `v1` | blank — comparability stays `unavailable` |

A value that is present but out of enum is refused, never defaulted: a typo'd `"determinstic"` falling
back to `stochastic` would hold a deterministic campaign to a spread test it can never satisfy. A quoted
`"0.05"` is a string, not a number, and is refused rather than coerced. Write the number, or `null`, and
never a TODO string. Copy the block's `_doc` field across with the keys; it is the authority on what each
one means.

**The minimal edit.** The two comparability tags:

```json
"campaign": { "metric_version": "v1", "data_version": "v1" }
```

That single change converts the most common `unavailable` into a real check. From then on the runner
stamps both tags onto every `results/scoreboard.tsv` row and into every `results/result_<NN>.json`, which
is what the scoreboard schema always said those columns were for. One wrinkle to expect: the check
compares this run against the incumbent, and a pre-migration incumbent carries no tags of its own, so
comparability keeps reporting `unavailable` (its `needs` says to re-score that experiment under the
current version) until the incumbent is either re-scored or overtaken by a result recorded after the
migration. The tag describes the state the campaign is in now, and is stamped only on rows written from
here on. If the FROZEN scorer or the evaluation data changed at some point in this campaign's history, do
not retro-fit one version onto the older rows: their blank tag is the honest record that nobody certified
them.

**The decision you cannot default.** `prediction_mode` and `noise_model` are setup-time declarations
about what kind of campaign this is. They are not per-experiment knobs, and the defaults do not answer
them:

- *Can this campaign honestly bound its answer before it runs?* `range` if a defensible numeric
  `[low, high]` exists, which is the strongest control. `direction` if the honest claim is only which way
  the metric should move versus a named prior experiment. `none` only if neither is honest, and then with
  a recorded `prediction_mode_reason`. A fabricated range is a fake control, and is worse than none. The
  prediction file stays mandatory in every mode: what relaxes is the bound, never the requirement to write
  an expectation down before spending. The shape the gate demands changes with the mode, so a switch
  applies from the next experiment on.
- *Does re-running one experiment reproduce the metric exactly?* Answer that by running one thing twice,
  not from intuition: re-run a recorded experiment from its own config and compare the metric to the
  number in its `results/result_<NN>.json`. Identical means `deterministic`, and the knob that matters is
  `tolerance` (numerical equality). Anything else means `stochastic`, and the spread over a few repeats is
  the `noise_floor` (`verify`, "Clear the noise floor"). Either may stay `null`, in which case the check
  reports `unavailable` and names the knob. That is honest; a guessed number is not.

Getting either wrong is silent. A stochastic campaign mislabelled `deterministic` promotes
noise as a win. A deterministic one mislabelled `stochastic` is held to a spread test it can never
satisfy, and it fails in the direction that looks like rigor, which is the direction nobody
investigates.

**Migration.** Nothing is re-scaffolded. `configs/loop.json` is user-owned and re-read as the loop runs,
so a live campaign picks the block up at its next unit, and every later
`results/snapshots/<exp>/manifest.txt` records the properties that experiment ran under. A change made
mid-campaign therefore lands in the frozen record, not only in a mutable file.

1. Copy the whole `campaign` block, `_doc` and all, from
   `kit/templates/campaign/configs/loop.json.tmpl` into your `configs/loop.json`.
2. Set `metric_version` / `data_version` (`v1` / `v1` unless this campaign's scorer or data has already
   moved). This alone is a complete and useful migration; the remaining steps can be done later.
3. Answer the two questions above and write the answers into `prediction_mode` and `noise_model`, plus
   `prediction_mode_reason` if the mode is `none`.
4. Set `noise_floor` or `tolerance`, or leave it `null` as recorded debt.

**Done when.** The validator has the last word on whether the block is legal. It rejects an out-of-enum
`prediction_mode` or `noise_model`, and a `none` with an empty `prediction_mode_reason`:

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/new-campaign/scripts/validate_campaign.py" <campaign>
```

It does not fail a campaign with blank tags or an unset resolution, and should not, because that is debt
rather than damage. So it cannot tell you the migration is done. This can, run from the campaign root:

```bash
py -3 - <<'PY'
import json, pathlib
c = json.loads(pathlib.Path("configs/loop.json").read_text(encoding="utf-8-sig")).get("campaign") or {}
def state(key, default):
    v = str(c.get(key) or "").strip().lower()
    return f"{v or default}  ({'declared' if v else 'DEFAULTED - nobody chose this'})"
noise = str(c.get("noise_model") or "stochastic").strip().lower()
knob = "tolerance" if noise == "deterministic" else "noise_floor"
tags = [t for t in ("metric_version", "data_version") if str(c.get(t) or "").strip()]
print("prediction_mode :", state("prediction_mode", "range"))
print("noise_model     :", state("noise_model", "stochastic"))
print(f"{knob:<16}: {c.get(knob)!r}"
      + ("" if c.get(knob) is not None else "  <- change-vs-incumbent check stays unavailable"))
print(f"comparability   : {len(tags)}/2 tags set"
      + ("" if len(tags) == 2 else "  <- comparability stays unavailable"))
PY
```

Migrated reads: both properties `declared` rather than `DEFAULTED`, `2/2 tags set`, and either a number on
the resolution knob or a `null` whose `unavailable` report on every run you accept.

---

## To the split campaign definition (kit ≥ the 2026-08 restructure)

**Symptom.** The validator prints `REFUSING TO VALIDATE` and exit 3, saying the campaign has
`docs/charter.md` and no `campaign.md`. Or a skill sends you to `campaign.md` §The ONE metric and the
file does not exist.

**What breaks.** Nothing, until you try to validate. The campaign runs: its own `CLAUDE.md` describes its
own tree, which is why the routing table was added first. The validator refuses rather than reporting
every required path as missing, because a wall of missing-path errors reads as damage and invites an agent
to repair a frozen campaign. **A finished campaign should not be migrated at all.** Freeze it and read it
where it stands.

**What moved.** One `docs/charter.md` fused three audiences; it is now three files:

| was | is |
|---|---|
| `docs/charter.md` — mission, metric, levers, FROZEN, caps, promotion, scoreboard schema | `campaign.md` |
| `docs/charter.md` — the experiment loop, verification, the save-set, the iteration contract | `roles/worker.md` |
| `docs/charter.md` — getting unstuck, reopening shelved directions, the literature rule | `roles/planner.md` |
| `docs/charter.md` §Ending the loop | deleted — `CLAUDE.md` HARD GATE 5 is the whole contract |
| `docs/protocols/checkpoint.md` §0 · `docs/protocols/artifacts.md` | `roles/worker.md` |
| `docs/protocols/checkpoint.md` (the rest) | the `campaign-status` skill |
| `docs/protocols/metric.md` | deleted — `campaign.md` §The ONE metric said it already |
| `docs/protocols/expensive-evaluation.md` | the kit's `docs/reference/expensive-evaluation.md` |
| `docs/baselines.md` · `docs/dataset.md` | `campaign.md` sections |
| `results/INDEX.md` | deleted — the scoreboard and JOURNAL carry what it indexed |
| the `CORE.md` snapshot inlined in `CLAUDE.md` | `DOCTRINE_SNAPSHOT.md`, referenced not auto-loaded |

**Migration.** For a campaign you intend to keep working in:

1. Scaffold a throwaway campaign with the current kit (`new-campaign`, any answers) and use its tree as
   the shape to copy. That is cheaper and more accurate than transcribing the table above.
2. Split your `docs/charter.md` into `campaign.md` + `roles/worker.md` + `roles/planner.md` by the rows
   above. Keep your own campaign's facts verbatim. Take the generic doctrine from the fresh scaffold
   rather than carrying yours across, so you pick up the corrections.
3. Move the `CORE.md` snapshot out of `CLAUDE.md` into `DOCTRINE_SNAPSHOT.md` **unchanged**. It records
   the doctrine your campaign ran under and must not be re-synced to the current kit.
4. Rewrite `CLAUDE.md` §Where things live from the fresh scaffold's, then **correct every row against your
   tree**. Both the validator and Tier 0 check that each row's file exists and each `§` names a real
   heading, so a copied row that does not match your campaign fails loudly by design.
5. Delete `docs/protocols/`, `results/INDEX.md`, `docs/baselines.md`, `docs/dataset.md` only after
   confirming their content landed somewhere.
6. Run `python "${CLAUDE_PLUGIN_ROOT}/skills/new-campaign/scripts/validate_campaign.py" <campaign>`
   until it passes. Exit 3 means step 2 has not been done yet; exit 1 lists what is still missing.

**Do not** migrate `results/`. The ledger is the record, and its format did not change.

---

## To the `CLAUDE.md` routing table (kit ≥ PR-6)

**Symptom.** A skill tells you to follow the campaign's `CLAUDE.md` §Where things live table and the
campaign has no such section. The campaign was scaffolded before the table existed.

**What breaks.** Nothing hard-fails. A capable agent recovers by reading `docs/charter.md` directly and
reports the named table as missing. The cost is wasted turns, and an agent that believes its
instructions are wrong, which is corrosive over a long loop.

**Migration.** Add the table to the campaign's own `CLAUDE.md`, above `## Standing authorization`. Copy it
from `kit/templates/campaign/CLAUDE.md.tmpl` §Where things live, then **correct every row against the tree
you are in**. That is what the table is for, and a copied row naming a file this campaign does not have is
worse than no table.

Check each row resolves before you finish:

```bash
py -3 - <<'PY'
import re, pathlib
c = pathlib.Path("CLAUDE.md")
rows, on = [], False
for line in c.read_text(encoding="utf-8").splitlines():
    if line.startswith("## "):
        on = "Where things live" in line
    elif on and line.startswith("|"):
        m = re.search(r"`([^`]+)`", line.split("|")[-2])
        if m:
            rows.append(m.group(1))
missing = [r for r in rows if not pathlib.Path(r).exists()]
print(f"{len(rows)} rows, {len(missing)} dangling")
for r in missing:
    print("  MISSING:", r)
PY
```

A campaign with a suffixed charter (`docs/charter_<NAME>.md`, the retired multi-stage layout) names that
file in the table's first rows. That is the case the indirection exists for: one row changes, and no skill
does.

**If you would rather not migrate**, tell the agent so. Reading `docs/charter.md` directly is still
correct in this layout; you are only giving up the indirection.
