#!/usr/bin/env python3
"""validate_campaign.py — gate a generated autoresearch CAMPAIGN tree, or a PROJECT tree.

The target is auto-detected:
  * a PROJECT root (has PROJECT.md + campaigns/)  -> project-tree validation, or
  * a campaign tree                               -> campaign validation.

EVERY campaign lives inside a project (<project>/campaigns/<name>/ with ../../PROJECT.md); there is
no standalone/bare-campaign mode. Two project layouts exist (ADR-0015) and both validate:
  * NEW (consolidated): PROJECT.md is THE overview - mission, "## Standing constraints" (what the
    campaign driver delivers into every spawned prompt), system knowledge, durable decisions, and
    "## Lineage" (the index of every campaign/session) - beside a short README.md and CLAUDE.md.
  * OLD (five-file): PROJECT.md + PROJECT_ORIENTATION.md (carrying the constraints section) +
    LINEAGE.md + DISCOVERIES.md + CLAUDE.md + shared/.
The layout is probed by where "## Standing constraints" lives; the project background is REFERENCED
by campaigns and never copied, under either layout.

Campaign validation fails (exit 1) on anything new-campaign left unresolved:
  * a literal {{PLACEHOLDER}} token, a dangling [[OPTIONAL … block, a stray [PROPOSED] tag,
  * an un-stripped .tmpl file,
  * a missing required file (campaign.md, the role files, README, the ledgers, config template, the
    code stubs),
  * an illegal campaign property in configs/loop.json "campaign" - an out-of-enum prediction_mode /
    noise_model, or prediction_mode 'none' with no recorded reason (mirrors the runner's preflight),
  * an existing prediction JSON whose `exp_name` does not exactly match its filename stem,
  * no project home above the campaign, or no "## Standing constraints" section in the project's
    PROJECT.md (new layout) or PROJECT_ORIENTATION.md (old layout) - the section the driver
    delivers (a pre-merge project - one still carrying shared/PHYSICS.md - is named as such, with
    the migration pointer),
  * a LOCAL copy of the project background in the campaign's docs/ (under the current name or a
    retired shared-doc name) - it must be referenced, never copied (design §4.1),
  * a hook whose interpreter does not RUN on this machine — a wired-but-dead gate is worse than an
    absent one, because it looks like coverage (bare `python` is the Store alias stub on stock Windows),
  * a dangling row in CLAUDE.md's §Where things live table — live skills route through it instead of
    naming a campaign path, and a wrong row misdirects them quietly (the agent guesses rather than
    erroring). A campaign with no such table predates it and is skipped, not failed.
Legacy trees using the retired multi-stage suffix (charter_<NAME>.md / configs_<NAME>/ / results_<NAME>/) still
validate — the required-file checks glob — but new stages are scaffolded as sibling campaigns, not suffixes.

Project-tree validation fails (exit 1) if the project home is malformed:
  * a missing required file/dir for its layout (new: README.md, PROJECT.md - with its "## Standing
    constraints" and "## Lineage" sections - CLAUDE.md, data/, campaigns/, sessions/, reports/;
    old: additionally PROJECT_ORIENTATION.md, LINEAGE.md, DISCOVERIES.md, shared/),
  * a NEW-layout project still carrying a retired root doc whose content PROJECT.md now owns
    (PROJECT_ORIENTATION.md, LINEAGE.md - two authorities for the same content is a fork) or a
    leftover shared/ (its artifacts belong in purpose-named project dirs). A legacy imported
    DISCOVERIES.md is tolerated: it is an append-only historical ledger, still hook-gated, that
    PROJECT.md does not duplicate,
  * a leftover {{PLACEHOLDER}}/[[OPTIONAL/[PROPOSED] in a project-root or shared/ doc,
  * a campaign in campaigns/ (or campaigns/_archive/) NOT indexed in the lineage (PROJECT.md
    "## Lineage" in the new layout; LINEAGE.md in the old),
  * a campaign carrying a LOCAL copy of the project background (docs/PROJECT_ORIENTATION.md, or a
    retired shared-doc name: docs/PHYSICS.md|CONVENTIONS.md|INSTRUMENT.md) — it must reference
    the project overview, never copy (design §4.1),
  * an ABSOLUTE path hard-coded in a config JSON (the portability breaker; prose docs are exempt because
    they legitimately carry example paths — the invariant is that the tree relocates as one unit, the only
    absolute path being the resolved data_path pointer in PROJECT.md / data/DATA_PATH.txt).

Usage:
    python validate_campaign.py <target_dir>
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

TEXT_EXT = {".md", ".py", ".json", ".tsv", ".txt", ".cfg", ".ini", ".yaml", ".yml"}
# Kit placeholders are UPPER_SNAKE (start with a letter/underscore). Matching only those avoids
# false positives on legitimate LaTeX (\frac{{a}}, x_{{ij}}) and Python f-string ({{...}}) braces.
PLACEHOLDER = re.compile(r"\{\{[A-Z_][A-Z0-9_]*\}\}")
LEAK_LITERALS = ("[[OPTIONAL", "[PROPOSED]")
DUAL_INSTRUCTION_MARKER = "<!-- physkit-dual-instructions:v1 -->"
# Windows drive-letter (C:\ or C:/) or UNC (\\server) absolute paths — the realistic portability breaker
# for this Windows/shared-drive project. Applied to CONFIG files only (not prose, which has legit examples).
ABS_PATH = re.compile(r"(?:[A-Za-z]:[\\/])|(?:\\\\[A-Za-z0-9_.$-]+\\)")

CAMPAIGN_REQUIRED_GLOBS = [
    ("campaign definition", "campaign.md"),
    ("worker role", "roles/worker.md"),
    ("verifier role", "roles/verifier.md"),
    ("capstone role", "roles/capstone.md"),
    ("role reference", "roles/REFERENCE.md"),
    ("front door + setup status", "README.md"),
    ("scoreboard ledger", "results*/scoreboard.tsv"),
    ("logbook", "results*/logbook.md"),
    ("journal", "results*/JOURNAL*.md"),
    ("config template", "configs*/_template.json"),
    ("metric scorer", "scripts/metric.py"),
    ("runner", "scripts/run_campaign.py"),
    ("frozen-core manifest", "scripts/frozen_core.py"),
    ("correctness suite", "tests/correctness_checks.py"),
    ("always-on doctrine", "CLAUDE.md"),
    ("promotion guard hook", "scripts/guard_promotion.py"),
    ("loop heartbeat hook", "scripts/loop_heartbeat.py"),
    ("hook settings", ".claude/settings.json"),
    ("loop knobs", "configs*/loop.json"),
    ("predictions dir", "predictions"),
    ("verdicts dir", "results*/verdicts"),
]

# Per-layout requirements (ADR-0015). The overview's constraints section is owned by
# check_orientation(), which also names a pre-merge layout instead of reporting generic damage.
PROJECT_REQUIRED_FILES = {
    "new": ["README.md", "PROJECT.md", "CLAUDE.md"],
    "old": ["PROJECT.md", "LINEAGE.md", "CLAUDE.md", "DISCOVERIES.md"],
}
PROJECT_REQUIRED_DIRS = {
    "new": ["data", "campaigns", "sessions", "reports"],
    "old": ["data", "shared", "campaigns", "sessions", "reports"],
}
# Root docs a NEW-layout project must NOT still carry: PROJECT.md owns their content now, so a
# surviving copy is two authorities for the same record - a fork. (DISCOVERIES.md is deliberately
# absent from this list: a legacy imported ledger is append-only history, still hook-gated, and
# PROJECT.md does not duplicate its entries.)
NEW_LAYOUT_FORK_DOCS = ("PROJECT_ORIENTATION.md", "LINEAGE.md")
# The project background lives ONCE in the project overview and is referenced; a campaign-local copy
# is a fork (design §4.1). The retired shared-doc names are checked too, because a copy under any
# layout's name forks the same content.
LOCAL_COPY_DOCS = ("PROJECT_ORIENTATION.md", "PHYSICS.md", "CONVENTIONS.md", "INSTRUMENT.md")
# The section the campaign driver delivers into every spawned prompt - in PROJECT.md (new layout) or
# PROJECT_ORIENTATION.md (old). Its absence is checked here AND by the driver's preflight, so it is
# caught at scaffold time, not at 3 a.m.
CONSTRAINTS_HEADING = "standing constraints"
LINEAGE_HEADING = "lineage"


def _read_text(path: Path) -> str | None:
    """Read a text file as UTF-8 (BOM-tolerant) or UTF-16; None if undecodable."""
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="utf-16")
        except (UnicodeError, OSError):
            return None
    except OSError:
        return None


def check_agent_instructions(root: Path, errors: list[str], *, chain: bool) -> None:
    """Use the shipped canonical checker without executing campaign-local Python."""
    checker_path = (Path(__file__).resolve().parents[3] / "templates" / "campaign"
                    / "scripts" / "sync_agent_instructions.py")
    try:
        namespace = {"__name__": "physkit_instruction_checker"}
        exec(compile(checker_path.read_bytes(), str(checker_path), "exec"), namespace)
        if chain:
            namespace["check_chain"](root)
        else:
            namespace["check_pair"](root, required=True)
    except Exception as exc:
        errors.append(f"Claude/Codex instruction consistency failed: {exc}")


def _md_has_section(path: Path, heading: str) -> bool:
    """True if the file has an H2 whose text contains `heading` (case-insensitive)."""
    text = _read_text(path) or ""
    return any(line.startswith("## ") and heading in line.lower() for line in text.splitlines())


def _md_section_text(path: Path, heading: str) -> str:
    """The body under the matching H2, through its H3s, up to the next H2; '' if absent."""
    out, on = [], False
    for line in (_read_text(path) or "").splitlines():
        if line.startswith("## ") and not line.startswith("### "):
            on = heading in line.lower()
            continue
        if on:
            out.append(line)
    return "\n".join(out)


def project_layout(root: Path) -> str:
    """'new' = the consolidated single-overview layout (ADR-0015: PROJECT.md carries the delivered
    constraints section); 'old' = the five-file layout. Probed by content, not by file census, so a
    half-migrated tree is judged by which file actually feeds the driver."""
    return "new" if _md_has_section(root / "PROJECT.md", CONSTRAINTS_HEADING) else "old"


def scan_leftovers(paths, base: Path, errors: list[str]) -> None:
    """Flag leftover placeholders / OPTIONAL blocks / PROPOSED tags / un-stripped .tmpl in `paths`."""
    for path in paths:
        if not path.is_file():
            continue
        if path.suffix == ".tmpl":
            errors.append(f"un-stripped template (.tmpl not removed): {path.relative_to(base)}")
            continue
        if path.suffix.lower() not in TEXT_EXT:
            continue
        text = _read_text(path)
        if text is None:
            errors.append(f"could not decode (not UTF-8/UTF-16), cannot scan for leftovers: {path.relative_to(base)}")
            continue
        rel = path.relative_to(base)
        for i, line in enumerate(text.splitlines(), 1):
            if PLACEHOLDER.search(line):
                errors.append(f"unresolved placeholder {rel}:{i}: {line.strip()[:100]}")
            for lit in LEAK_LITERALS:
                if lit in line:
                    errors.append(f"unresolved {lit} {rel}:{i}: {line.strip()[:100]}")


def _local_copy_error(rel: str, doc: str) -> str:
    """The right message for a campaign-level background doc: which one it is decides the fix.

    A campaign-level PROJECT_ORIENTATION.md is usually the pre-merge campaign file that DISSOLVED,
    not a copy - telling someone "never copy" invites deleting it, which loses the goal and task
    content the migration moves into campaign.md and the JOURNAL. Name the actual fix."""
    if doc == "PROJECT_ORIENTATION.md":
        return (f"campaign-level {rel} - this file dissolved in the one-background-document merge; "
                "migrate its content (goal -> campaign.md, tasks -> the JOURNAL's What to try next + NEXT, field "
                "positioning -> the project overview) per the kit's docs/MIGRATING.md, then "
                "delete it. Do not delete it unmigrated.")
    return (f"campaign carries a LOCAL copy of the project background (must reference the project "
            f"overview - ../../PROJECT.md, or ../../PROJECT_ORIENTATION.md in an old-layout "
            f"project - never copy): {rel}")


def check_orientation(proj_root: Path, errors: list[str]) -> None:
    """The project overview carries the section the driver delivers every spawn - in PROJECT.md
    (new layout) or PROJECT_ORIENTATION.md (old layout), the same resolution order the driver uses.

    A project still carrying the retired four-document layout (shared/PHYSICS.md et al.) is named as
    pre-merge with the migration pointer, not reported as generic damage: an agent told only "file
    missing" will fabricate one, and a fabricated background document is worse than a named gap.
    """
    if _md_has_section(proj_root / "PROJECT.md", CONSTRAINTS_HEADING):
        return                                    # new layout: PROJECT.md feeds the driver
    old = proj_root / "PROJECT_ORIENTATION.md"
    if old.is_file():
        if not _md_has_section(old, CONSTRAINTS_HEADING):
            errors.append(
                "PROJECT_ORIENTATION.md has no '## Standing constraints' section - that section is "
                "what the campaign driver delivers into every spawned prompt, so without it the "
                "delivery is silently empty. Add the section (see the project template)."
            )
        return
    if (proj_root / "shared" / "PHYSICS.md").is_file():
        errors.append(
            "the project home predates the one-background-document merge: it has shared/PHYSICS.md "
            "and no delivered-constraints doc. Migrate it with the kit's docs/MIGRATING.md; do not "
            "author a new background document from scratch."
        )
    else:
        errors.append(
            "no '## Standing constraints' anywhere the driver looks: PROJECT.md does not carry the "
            "section and there is no PROJECT_ORIENTATION.md. That section is delivered into every "
            "spawned prompt; author it in PROJECT.md (see the project template)."
        )


def project_root_of(campaign: Path) -> Path | None:
    """The project home above a campaign, or None if the campaign has no home.

    A campaign sits at <project>/campaigns/<slug>/, or <project>/campaigns/_archive/<slug>/ once forked.
    Matching on the parent directory NAME (not just depth) keeps a sessions/<date>_<slug>/ folder — which is
    also two levels under the project root — from being mistaken for a campaign.
    """
    if campaign.parent.name == "campaigns":
        cand = campaign.parent.parent
    elif campaign.parent.name == "_archive" and campaign.parent.parent.name == "campaigns":
        cand = campaign.parent.parent.parent
    else:
        return None
    # PROJECT.md alone marks the home: the old layout pairs it with LINEAGE.md, the consolidated
    # layout (ADR-0015) absorbed that index into PROJECT.md §Lineage.
    return cand if (cand / "PROJECT.md").is_file() else None


# The campaign-property enums. An intentional twin of run_campaign.py.tmpl's PREDICTION_MODES /
# NOISE_MODELS: the validator must run against a scaffolded tree without importing that campaign's
# runner, which would pull in numpy, metric and frozen_core just to read two strings. The twin is checked
# rather than trusted: tier0_static.py asserts the two lists
# agree, so a mode added on one side and not the other fails the suite instead of drifting.
PREDICTION_MODES = ("range", "direction", "none")
NOISE_MODELS = ("stochastic", "deterministic")
VERIFY_PRESETS = ("none", "minimal", "light", "heavy", "intensive")
VERIFY_ROWS = ("invariants", "machinery", "gates", "self_check", "self_verify", "independent", "capstone")
VERIFY_PRESET_RENAMED = {"moderate": "heavy"}
METRIC_REVISION_MODES = ("cautious", "autonomous")
AGENT_BACKENDS = ("auto", "claude", "codex", "custom")
VERIFY_STRATEGIES = ("auto", "legacy-nested", "driver-direct")
CLAUDE_EFFORTS = ("low", "medium", "high", "xhigh", "max")
CODEX_EFFORTS = ("minimal", "low", "medium", "high", "xhigh")


def check_loop_files(root: Path, errors: list[str]) -> None:
    """The driver's config/ledger must PARSE, not merely exist: a loop.json missing a hard-dereferenced
    key passes an existence glob and then crashes supervise() at launch (or worse, mid-night). Mirrors
    the runner's own preflight so the gap is caught at scaffold time too."""
    loop_files = list(root.glob("configs*/loop.json"))
    if loop_files:
        text = _read_text(loop_files[0])
        try:
            cfg = json.loads(text or "")
            for name, keys in (("worker.iteration_timeout_hours", ("worker", "iteration_timeout_hours")),
                               ):
                node = cfg
                try:
                    for k in keys:
                        node = node[k]
                    float(node)
                except Exception:
                    errors.append(f"loop.json is missing the numeric key the driver requires: {name}")
            camp = cfg.get("campaign") or {}
            mode = str(camp.get("prediction_mode") or "range").strip().lower()
            noise = str(camp.get("noise_model") or "stochastic").strip().lower()
            if mode not in PREDICTION_MODES:
                errors.append(f"loop.json campaign.prediction_mode is {mode!r}; expected one of "
                              + " | ".join(PREDICTION_MODES))
            if noise not in NOISE_MODELS:
                errors.append(f"loop.json campaign.noise_model is {noise!r}; expected one of "
                              + " | ".join(NOISE_MODELS))
            if mode == "none" and not str(camp.get("prediction_mode_reason") or "").strip():
                errors.append("loop.json sets campaign.prediction_mode='none' with an empty "
                              "campaign.prediction_mode_reason - record why this campaign cannot "
                              "honestly bound its answer. Running unbounded is a legitimate choice; "
                              "making it without a recorded reason leaves the control unowned.")
            verify_block = cfg.get("verify") if isinstance(cfg.get("verify"), dict) else {}
            preset = verify_block.get("preset")
            if preset is not None:
                p = str(preset).strip().lower()
                if p in VERIFY_PRESET_RENAMED:
                    errors.append(f"loop.json verify.preset {p!r} was renamed {VERIFY_PRESET_RENAMED[p]!r} "
                                  " - set the new name")
                elif p not in VERIFY_PRESETS:
                    errors.append(f"loop.json verify.preset is {p!r}; expected one of "
                                  + " | ".join(VERIFY_PRESETS) + " (docs/reference/verification-presets.md)")
            if camp.get("verification"):
                errors.append(f"loop.json campaign.verification={camp.get('verification')!r} is retired - set "
                              "verify.preset (" + " | ".join(VERIFY_PRESETS) + ") and delete the old key")
            rmode = str(camp.get("metric_revision") or "cautious").strip().lower()
            if rmode not in METRIC_REVISION_MODES:
                errors.append(f"loop.json campaign.metric_revision is {rmode!r}; expected one of "
                              + " | ".join(METRIC_REVISION_MODES)
                              + (" ('semi-autonomous' is reserved - its rules are not defined yet)"
                                 if rmode == "semi-autonomous" else ""))
            backend = str((cfg.get("driver") or {}).get("backend") or "auto").strip().lower()
            if backend not in AGENT_BACKENDS:
                errors.append(f"loop.json driver.backend is {backend!r}; expected one of "
                              + " | ".join(AGENT_BACKENDS))
            verify_cfg = cfg.get("verify") or {}
            verify_strategy = verify_cfg.get("strategy", "auto") if isinstance(verify_cfg, dict) else None
            if not isinstance(verify_strategy, str) or verify_strategy.strip().lower() not in VERIFY_STRATEGIES:
                errors.append("loop.json verify.strategy must be " + " | ".join(VERIFY_STRATEGIES))
            for role in ("worker", "verifier"):
                role_cfg = cfg.get(role) or {}
                if "codex_model" in role_cfg and not isinstance(role_cfg["codex_model"], str):
                    errors.append(f"loop.json {role}.codex_model must be a string")
                for field, allowed in (("claude_effort", CLAUDE_EFFORTS),
                                       ("codex_reasoning_effort", CODEX_EFFORTS)):
                    if field not in role_cfg:
                        continue
                    value = role_cfg[field]
                    if not isinstance(value, str):
                        errors.append(f"loop.json {role}.{field} must be a string")
                    elif value.strip() and value.strip().lower() not in allowed:
                        errors.append(f"loop.json {role}.{field} must be blank or one of: "
                                      + " | ".join(allowed))
        except Exception as exc:
            errors.append(f"loop.json does not parse as JSON ({exc})")
    if list(root.glob("results*/queue.json")):
        print("note: results/queue.json is the retired queue: the driver no longer reads it - run "
              "upgrade_campaign.py --retire-queue to archive it and move its open ideas into the JOURNAL")


def check_prediction_subjects(root: Path, errors: list[str]) -> None:
    """Existing pre-run evidence must name the subject its filename assigns to it.

    Predictions are created incrementally, so absence is valid here and remains the runner's spend-gate
    decision. Any prediction that does exist must already satisfy the verifier's immutable subject rule.
    """
    for path in sorted((root / "predictions").glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            errors.append(f"{path.relative_to(root)} does not parse as JSON ({exc})")
            continue
        actual = str(payload.get("exp_name", "")) if isinstance(payload, dict) else ""
        if actual != path.stem:
            errors.append(f"{path.relative_to(root)} has exp_name={actual!r}; expected {path.stem!r}")


def check_routing_table(root: Path, errors: list[str]) -> None:
    """Every row of CLAUDE.md's §Where things live table must resolve in THIS campaign.

    Live skills route through that table instead of naming a campaign path, so a dangling row misdirects
    the whole skills layer — and it misdirects QUIETLY, because a wrong path degrades (the agent guesses
    and moves on) rather than erroring. The template says "Keep it true", which is an exhortation; the
    kit's own rule is enforce, don't exhort.

    A campaign with no table is NOT an error: it was scaffolded before the table existed and is frozen
    that way by design. Its skills fall back to `docs/charter*.md`, which is a required glob above.
    """
    text = _read_text(root / "CLAUDE.md")
    if text is None:
        return                                   # absence is already reported by the required-files scan
    rows, in_table = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            in_table = "Where things live" in line
            continue
        if not in_table or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or set(cells[-1]) <= set("- ") or cells[0].lower().startswith("what you need"):
            continue                             # separator or header row
        m = re.search(r"`([^`]+)`", cells[-1])
        if m:
            section = cells[-1].split("§", 1)[1].strip().strip("`") if "§" in cells[-1] else ""
            rows.append((cells[0], m.group(1), section))
    if not rows:
        return                                   # pre-table campaign; the charter glob still gates it

    for label, rel, section in rows:
        target = root / rel
        if not target.exists():
            errors.append(f"CLAUDE.md routing table points at a path that does not exist: "
                          f"'{label}' -> {rel}. Correct the row to match this campaign's tree.")
            continue
        if section and target.is_file():
            headings = [L.lstrip("#").strip()
                        for L in (_read_text(target) or "").splitlines() if L.startswith("#")]
            if not any(section.lower() in h.lower() for h in headings):
                errors.append(f"CLAUDE.md routing table names a section that does not exist: "
                              f"'{label}' -> {rel} §{section}.")


def check_hook_wiring(root: Path, errors: list[str]) -> None:
    """The gates must be INVOKABLE, not merely present. A hook whose interpreter does not resolve is a
    campaign with no promotion gate and no loop persistence -- silently, because Claude Code reports a
    non-zero, non-2 hook exit as a non-blocking error and allows the action.

    The live failure: on stock Windows, bare `python` is the Microsoft Store App Execution Alias stub. It
    prints "Python was not found" and exits 49 without running the script. The Store aliases are on by
    default and the Python installer's "Add python.exe to PATH" box is off by default, so this is the
    DEFAULT state of a fresh Windows box, not an exotic one. Existence checks cannot see it, and neither
    can a test suite that invokes the hook scripts directly with sys.executable.
    """
    settings = root / ".claude" / "settings.json"
    text = _read_text(settings)
    if text is None:
        return                                   # absence is already reported by the required-files scan
    try:
        cfg = json.loads(text)
    except Exception as exc:
        errors.append(f".claude/settings.json does not parse as JSON ({exc})")
        return
    cmds = [h.get("command", "") for group in (cfg.get("hooks") or {}).values()
            for entry in group for h in (entry.get("hooks") or []) if h.get("type") == "command"]
    if not cmds:
        errors.append(".claude/settings.json declares no command hooks — the gates are not wired")
        return
    for cmd in cmds:
        interp = cmd.split('"')[0].strip()
        if not interp:
            continue
        script = (cmd.split('"')[1].rsplit("/", 1)[-1] if '"' in cmd else cmd)
        try:
            r = subprocess.run(f'{interp} -c "print(1)"', shell=True,
                               capture_output=True, text=True, timeout=30)
            ok = r.returncode == 0 and r.stdout.strip() == "1"
        except Exception as exc:
            ok, r = False, None
            errors.append(f"hook interpreter {interp!r} (for {script}) could not be run ({exc})")
            continue
        if not ok:
            detail = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()
            errors.append(
                f"hook interpreter {interp!r} (for {script}) does not run: exit {r.returncode}"
                + (f" — {detail[0][:100]}" if detail else "")
                + ". The gate is silently DEAD. Use an invocation that resolves on this machine"
                  " (`py -3` on Windows, `python3` on macOS/Linux) in .claude/settings.json.")


def check_codex_hook_wiring(root: Path, errors: list[str]) -> None:
    """New managed campaigns must expose the shared promotion policy to canonical apply_patch."""
    settings = root / ".codex" / "hooks.json"
    text = _read_text(settings)
    if text is None:
        errors.append("missing Codex promotion-hook settings: .codex/hooks.json")
        return
    try:
        cfg = json.loads(text)
    except Exception as exc:
        errors.append(f".codex/hooks.json does not parse as JSON ({exc})")
        return
    hook_map = cfg.get("hooks") if isinstance(cfg, dict) else None
    entries = hook_map.get("PreToolUse") if isinstance(hook_map, dict) else None
    if not isinstance(entries, list):
        errors.append(".codex/hooks.json must declare hooks.PreToolUse as a list")
        return
    matched = [entry for entry in entries
               if isinstance(entry, dict) and entry.get("matcher") == "^apply_patch$"]
    if not matched:
        errors.append(".codex/hooks.json has no exact canonical apply_patch PreToolUse matcher")
        return
    hooks = [hook for entry in matched
             for hook in (entry.get("hooks") if isinstance(entry.get("hooks"), list) else [])
             if isinstance(hook, dict)]
    wired = [hook for hook in hooks
             if hook.get("type") == "command"
             and "guard_promotion_codex.py" in str(hook.get("command", ""))
             and "guard_promotion_codex.py" in str(hook.get("commandWindows", hook.get("command", "")))]
    if not wired:
        errors.append(".codex/hooks.json does not invoke scripts/guard_promotion_codex.py")
    elif any(hook.get("async") not in (None, False) for hook in wired):
        errors.append("Codex promotion PreToolUse hook must be synchronous (async must be absent or false)")


EPOCH_KINDS = ("mechanics", "semantics")
EPOCH_STATUSES = ("pending", "ratified", "rolled-back")


CONTRACT_CHECKS = ("baseline_reproduces", "noise_floor_measured", "metric_discriminates", "synthetic_recovery")


def check_contract_checks(root: Path, errors: list[str]) -> None:
    """The setup audit's four contract checks must exist in the suite (new-campaign Step 3.7) unless
    tests/CORRECTNESS_NA.md records why the campaign has no machinery to check. Presence only: their
    outcome is the runner's to record (a skip-stub is allowed to ship; a missing name is a scaffold that
    skipped the audit)."""
    suite = root / "tests" / "correctness_checks.py"
    if not suite.is_file():
        return                      # the required-file check already reports an absent suite
    if (root / "tests" / "CORRECTNESS_NA.md").is_file():
        return
    try:
        text = suite.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    missing = [name for name in CONTRACT_CHECKS if f"def {name}(" not in text]
    if missing:
        errors.append("tests/correctness_checks.py lacks the setup audit's contract check(s): "
                      + ", ".join(missing) + " - fill them (new-campaign Step 3.7; the suite template "
                      "ships them as stubs), or record tests/CORRECTNESS_NA.md with the reason")


def check_metric_epochs(root: Path, errors: list[str]) -> None:
    """loop.json campaign.metric_epochs (the metric-epoch record) - absent while the campaign is on its
    co-designed first metric; once present, an object keyed by metric_version whose entries carry a legal
    kind and status, naming the current metric_version, and not pointing it at a rolled-back epoch."""
    loop_files = list(root.glob("configs*/loop.json"))
    if not loop_files:
        return
    try:
        camp = (json.loads(_read_text(loop_files[0]) or "") or {}).get("campaign") or {}
    except Exception:
        return   # check_loop_files already reports an unparseable loop.json
    block = camp.get("metric_epochs")
    if block is None:
        return
    if not isinstance(block, dict):
        errors.append("loop.json campaign.metric_epochs must be a JSON object keyed by metric_version")
        return
    for vid, e in block.items():
        if not str(vid).strip() or not isinstance(e, dict):
            errors.append("loop.json campaign.metric_epochs: every entry is keyed by a metric_version and is an object")
            return
        if str(e.get("kind", "")) not in EPOCH_KINDS:
            errors.append(f"loop.json campaign.metric_epochs[{vid!r}]: kind must be " + " | ".join(EPOCH_KINDS))
        if str(e.get("status", "")) not in EPOCH_STATUSES:
            errors.append(f"loop.json campaign.metric_epochs[{vid!r}]: status must be " + " | ".join(EPOCH_STATUSES))
    mv = str(camp.get("metric_version") or "").strip()
    bound = {}
    for state in root.glob("results*/correctness_state.json"):
        try:
            bound = (json.loads(_read_text(state) or "") or {}).get("scorer_hash_by_version") or {}
        except Exception:
            bound = {}
        break
    if block and mv and mv not in block and mv not in bound:   # the first (bound) epoch needs no entry
        errors.append(f"loop.json campaign.metric_version {mv!r} has no entry in campaign.metric_epochs "
                      f"(declared: {', '.join(str(k) for k in block)}) - a metric_version bump is an epoch; declare it")
    elif block and mv and mv in block and str(block[mv].get("status")) == "rolled-back":
        errors.append(f"loop.json campaign.metric_version {mv!r} points at a ROLLED-BACK epoch")


LANDMINE_HEADING = "known landmines"


def check_landmine_sources(root: Path, errors: list[str]) -> None:
    """Every row of campaign.md §Known landmines names its source in the fourth column (the user, a
    ledger id, a sibling campaign's verdict). A landmine nobody can source is a guess, and a guessed
    landmine steers a campaign away from a path nobody tested - the failure that motivated the rule
    (the brief trim; MIGRATING has the story). A campaign scaffolded before the source column (a three-column table) is frozen that
    way by design and is not checked."""
    text = _md_section_text(root / "campaign.md", LANDMINE_HEADING)
    rows = [L for L in (text or "").splitlines() if L.startswith("|")]
    if len(rows) < 2:
        return
    header = [c.strip().lower() for c in rows[0].strip().strip("|").split("|")]
    if len(header) < 4 or "source" not in header[-1]:
        return                                   # pre-source-column campaign
    for line in rows[2:]:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not any(cells) or cells[0].startswith("<"):
            continue                             # the template's example row
        if len(cells) < 4 or not cells[3] or cells[3].startswith("<"):
            errors.append(f"campaign.md §Known landmines: the row '{cells[0][:60]}' names no source. A "
                          "landmine without a source is a guess: source it (the user, a ledger id, a "
                          "verdict) or move it to the JOURNAL marked [setup inference].")


def validate_campaign(root: Path) -> list[str]:
    errors: list[str] = []

    # Every campaign lives inside a project, so the background is SHARED in the project overview
    # (../../PROJECT.md; old layout: ../../PROJECT_ORIENTATION.md) — referenced, never copied
    # (design §4.1). There is no standalone mode to detect.
    proj_root = project_root_of(root)

    # 1. Required files present (glob-based; tolerates the retired _<NAME> suffix in legacy trees).
    for label, pattern in CAMPAIGN_REQUIRED_GLOBS:
        if not list(root.glob(pattern)):
            errors.append(f"missing {label}: no file matches '{pattern}'")

    # New runners import this helper; legacy Claude runners predate it and remain valid.
    runner = root / "scripts" / "run_campaign.py"
    runner_text = _read_text(runner) or ""
    # The campaign's code is scripts/experiment.py (kit >= v0.11.1); a pre-split runner that still
    # defines the hooks itself is a legacy campaign, valid until it is upgraded.
    if runner.is_file() and "def run_experiment(" not in runner_text \
            and not (root / "scripts" / "experiment.py").is_file():
        errors.append("missing campaign code: scripts/experiment.py (the runner calls its hooks; "
                      "upgrade_campaign.py extracts them from a pre-split runner)")
    managed_instructions = DUAL_INSTRUCTION_MARKER in (
        (_read_text(root / "CLAUDE.md") or "") + (_read_text(root / "AGENTS.md") or ""))
    if (runner.is_file()
            and "import supervisor_lock as _supervisor_lock"
            in runner_text
            and not (root / "scripts" / "supervisor_lock.py").is_file()):
        errors.append("missing supervisor ownership lock: scripts/supervisor_lock.py")
    instruction_import = "import sync_agent_instructions as _agent_instructions" in runner_text
    codex_backend_import = "import codex_backend as _codex_backend" in runner_text
    if managed_instructions and not instruction_import:
        errors.append("managed Claude/Codex instructions require runner checker wiring")
    if instruction_import or managed_instructions:
        if not (root / "scripts" / "sync_agent_instructions.py").is_file():
            errors.append("missing Claude/Codex instruction checker: scripts/sync_agent_instructions.py")
        check_agent_instructions(root, errors, chain=True)
    if codex_backend_import and not (root / "scripts" / "codex_backend.py").is_file():
        errors.append("missing Codex launch adapter: scripts/codex_backend.py")
    if "import codex_verifier" in runner_text and not (root / "scripts" / "codex_verifier.py").is_file():
        errors.append("missing Codex verifier policy: scripts/codex_verifier.py")
    if managed_instructions:
        if not (root / "scripts" / "guard_promotion_codex.py").is_file():
            errors.append("missing Codex promotion adapter: scripts/guard_promotion_codex.py")
        check_codex_hook_wiring(root, errors)
        check_prediction_subjects(root, errors)

    # 1b. The project home + its background doc. A campaign with no home is a legacy bare tree — lift it
    #     into a project (new-campaign Step 0.1) rather than authoring campaign-local physics/conventions.
    if proj_root is None:
        errors.append(
            "no project home: expected <project>/campaigns/<slug>/ with ../../PROJECT.md — "
            "every campaign lives in a project; lift this tree in via new-campaign Step 0.1"
        )
    else:
        check_orientation(proj_root, errors)

    # 1c. No campaign-local copy of the project background (validate_project runs the same check tree-wide).
    for doc in LOCAL_COPY_DOCS:
        if (root / "docs" / doc).is_file():
            errors.append(_local_copy_error(f"docs/{doc}", doc))

    # (README's §Setup status is a static pointer to --preflight, the authoritative setup check; the
    # CLAUDE.md routing-table check below already verifies the section exists for the row that names it.)

    # 1d. The loop driver's config parses and carries the keys the driver dereferences.
    check_loop_files(root, errors)
    check_metric_epochs(root, errors)
    check_contract_checks(root, errors)
    check_hook_wiring(root, errors)
    check_routing_table(root, errors)
    check_landmine_sources(root, errors)

    # 2. No leftover tokens / un-stripped templates anywhere in the tree.
    scan_leftovers(sorted(root.rglob("*")), root, errors)
    return errors


def validate_project(root: Path) -> list[str]:
    errors: list[str] = []
    layout = project_layout(root)

    # 1. Required project files + dirs for this layout, and the delivered-constraints section.
    for rel in PROJECT_REQUIRED_FILES[layout]:
        if not (root / rel).is_file():
            errors.append(f"missing required project file ({layout} layout): {rel}")
    for rel in PROJECT_REQUIRED_DIRS[layout]:
        if not (root / rel).is_dir():
            errors.append(f"missing required project dir ({layout} layout): {rel}/")
    check_orientation(root, errors)
    if DUAL_INSTRUCTION_MARKER in ((_read_text(root / "CLAUDE.md") or "")
                                   + (_read_text(root / "AGENTS.md") or "")):
        check_agent_instructions(root, errors, chain=False)

    # 1b. New layout: PROJECT.md must carry the §Lineage index, and the retired root docs whose
    #     content it now owns must be GONE - a surviving LINEAGE.md or PROJECT_ORIENTATION.md is a
    #     second authority for the same record, the fork the single-source rule names. shared/ is
    #     retired too: promoted artifacts live in purpose-named project dirs (ADR-0015). A legacy
    #     imported DISCOVERIES.md is tolerated (append-only history, still hook-gated).
    if layout == "new":
        if not _md_has_section(root / "PROJECT.md", LINEAGE_HEADING):
            errors.append("PROJECT.md has no '## Lineage' section - the consolidated layout keeps "
                          "the campaign/session index there (see the project template).")
        for rel in NEW_LAYOUT_FORK_DOCS:
            if (root / rel).is_file():
                errors.append(f"consolidated project still carries {rel} - PROJECT.md owns that "
                              "content now; two authorities fork. Merge any unabsorbed content into "
                              "PROJECT.md and delete the file (docs/MIGRATING.md).")
        if (root / "shared").is_dir():
            errors.append("consolidated project still has shared/ - promoted artifacts live in "
                          "purpose-named project dirs (scripts/, models/, ...) with a PROJECT.md "
                          "§Lineage promotion line. Move them and delete shared/ (docs/MIGRATING.md).")

    # 2. No leftover tokens in the project-root docs + shared/ (campaigns validate separately; skip data/).
    root_docs = [p for p in root.glob("*.md")]
    shared_docs = list((root / "shared").glob("*.md")) if (root / "shared").is_dir() else []
    scan_leftovers(sorted(root_docs + shared_docs), root, errors)

    # 3. Every campaign (incl. archived) is indexed in the lineage - PROJECT.md §Lineage (new) or
    #    LINEAGE.md (old); no campaign carries a LOCAL shared-doc copy.
    if layout == "new":
        lineage, lineage_name = _md_section_text(root / "PROJECT.md", LINEAGE_HEADING), "PROJECT.md §Lineage"
    else:
        lineage, lineage_name = _read_text(root / "LINEAGE.md") or "", "LINEAGE.md"
    campaigns_dir = root / "campaigns"
    if campaigns_dir.is_dir():
        camp_dirs = [d for d in campaigns_dir.iterdir() if d.is_dir() and not d.name.startswith(".") and d.name != "_archive"]
        archive = campaigns_dir / "_archive"
        if archive.is_dir():
            camp_dirs += [d for d in archive.iterdir() if d.is_dir() and not d.name.startswith(".")]
        for d in camp_dirs:
            slug = d.name
            slug_noidx = re.sub(r"^\d+[_-]", "", slug)   # 01_cnn-inverse -> cnn-inverse
            if slug not in lineage and slug_noidx not in lineage:
                errors.append(f"campaign not indexed in {lineage_name}: campaigns/{('_archive/' if d.parent.name=='_archive' else '')}{slug}")
            for local_doc in LOCAL_COPY_DOCS:
                if (d / "docs" / local_doc).is_file():
                    errors.append(_local_copy_error(f"campaigns/{slug}/docs/{local_doc}", local_doc))

    # 4. Portability: no absolute path hard-coded in a config JSON (prose docs are exempt — legit examples).
    for cfg in root.glob("campaigns/**/configs*/*.json"):
        text = _read_text(cfg) or ""
        for i, line in enumerate(text.splitlines(), 1):
            if ABS_PATH.search(line):
                errors.append(f"absolute path in config (breaks portability) {cfg.relative_to(root)}:{i}: {line.strip()[:100]}")
    for cfg in root.glob("sessions/**/*.json"):
        text = _read_text(cfg) or ""
        for i, line in enumerate(text.splitlines(), 1):
            if ABS_PATH.search(line):
                errors.append(f"absolute path in session config (breaks portability) {cfg.relative_to(root)}:{i}: {line.strip()[:100]}")
    return errors


def legacy_layout(root: Path) -> str | None:
    """Name the pre-restructure file if this is a pre-PR-9 campaign, else None.

    PR-9 replaced `docs/charter.md` with `campaign.md` + `roles/`. A campaign scaffolded before that
    is not broken; it is an older layout. Run the normal checks against it and EVERY required-path
    rule fires at once, which reads as damage rather than as a version difference -- and an agent
    that believes the damage will "repair" a frozen tree to make the validator happy. That is a named
    risk in the plan ("An agent mutates a frozen campaign to satisfy the new validator"), so the
    probe has to come BEFORE the first per-path error, not be inferred from a wall of them.
    """
    if (root / "campaign.md").is_file():
        return None                                     # post-restructure (or mid-migration): proceed
    for old in ("docs/charter.md", "docs/program.md"):  # program.md is the oldest naming
        if (root / old).is_file():
            return old
    hits = sorted(root.glob("docs/charter*.md"))        # the retired multi-stage suffix
    return hits[0].relative_to(root).as_posix() if hits else None


def _say(line: str) -> None:
    """Print a line that may carry non-ASCII, on a console that may not accept it.

    A Windows console defaults to cp1252, so a single U+2192 lifted from a campaign's own prose into
    an error message raised UnicodeEncodeError and killed the report MID-LIST -- the validator failed
    while telling you why it failed, and truncated at whatever line held the first arrow. The tool
    that reports problems must not be the tool that dies on them.
    """
    try:
        print(line)
    except UnicodeEncodeError:
        enc = sys.stdout.encoding or "ascii"
        print(line.encode(enc, "backslashreplace").decode(enc, "replace"))


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python validate_campaign.py <target_dir>", file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).resolve()
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 2

    # PROJECT.md + campaigns/ marks a project root in both layouts (the old one also has LINEAGE.md,
    # but keying on it would misread a consolidated project as a campaign - ADR-0015).
    is_project = (root / "PROJECT.md").is_file() and (root / "campaigns").is_dir()
    kind = "PROJECT" if is_project else "CAMPAIGN"

    if not is_project:
        old = legacy_layout(root)
        if old:
            print(f"REFUSING TO VALIDATE - {root}\n")
            print(f"  This campaign predates the PR-9 restructure: it has {old} and no campaign.md.")
            print("  That is a layout difference, not a defect, and this validator only knows the")
            print("  current one (campaign.md + roles/worker.md). Checking it")
            print("  anyway would report every required path as missing and read as damage.\n")
            print("  Migrate with kit/docs/MIGRATING.md, or validate it with the kit version that")
            print("  scaffolded it. Do NOT edit this tree to satisfy this check.")
            return 3

    errors = validate_project(root) if is_project else validate_campaign(root)

    if errors:
        _say(f"{kind} VALIDATION FAILED - {len(errors)} issue(s):\n")
        for e in errors:
            _say(f"  - {e}")
        _say(f"\nResolve every item above; a {kind.lower()} with an unresolved issue is not done.")
        return 1

    print(f"{kind} VALIDATION PASSED - {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
