#!/usr/bin/env python3
"""validate_campaign.py — gate a generated autoresearch CAMPAIGN tree, or a PROJECT tree.

The target is auto-detected:
  * a PROJECT root (has PROJECT.md + campaigns/)  -> project-tree validation, or
  * a campaign tree                               -> campaign validation.

EVERY campaign lives inside a project (<project>/campaigns/<name>/ with ../../PROJECT.md); there is
no standalone/bare-campaign mode. PROJECT.md is THE project overview - mission, "## Standing
constraints" (what the campaign driver delivers into every spawned prompt), system knowledge, durable
decisions, and "## Lineage" (the index of every campaign/session) - beside a short README.md and
CLAUDE.md. Campaigns REFERENCE the project background and never copy it.

Campaign validation fails (exit 1) on anything new-campaign left unresolved:
  * a literal {{PLACEHOLDER}} token, a dangling [[OPTIONAL … block, a stray [PROPOSED] or [[KEEP tag,
  * an un-stripped .tmpl file,
  * a missing required file (campaign.md, the role files, README, the ledgers, config template, the
    code: scripts/experiment.py, the runner and its helper scripts),
  * a CLAUDE.md/AGENTS.md pair (campaign or project) that is unmarked, missing a twin, or drifted, a
    runner not wired to the instruction checker, or a .codex/hooks.json that does not route Codex's
    apply_patch through scripts/guard_promotion_codex.py,
  * an illegal campaign property in configs/loop.json "campaign" - an out-of-enum noise_model (mirrors
    the runner's preflight),
  * no project home above the campaign, or no "## Standing constraints" section in the project's
    PROJECT.md - the section the driver delivers,
  * a campaign-local docs/PHYSICS.md - the project background is referenced, never copied,
  * a hook whose interpreter does not RUN on this machine — a wired-but-dead gate is worse than an
    absent one, because it looks like coverage (bare `python` is the Store alias stub on stock Windows),
  * a missing or dangling row in CLAUDE.md's §Where things live table — live skills route through it
    instead of naming a campaign path, and a wrong row misdirects them quietly (the agent guesses rather
    than erroring),
  * a campaign.md §Known landmines row that names no source.

Project-tree validation fails (exit 1) if the project home is malformed:
  * a missing required file/dir (README.md, PROJECT.md - with its "## Standing constraints" and
    "## Lineage" sections - CLAUDE.md, data/, campaigns/, sessions/, reports/), or a managed
    CLAUDE.md/AGENTS.md pair that is unmarked, missing a twin, or drifted,
  * a leftover {{PLACEHOLDER}}/[[OPTIONAL/[PROPOSED]/[[KEEP in a project-root doc,
  * a campaign in campaigns/ (or campaigns/_archive/) NOT indexed in PROJECT.md "## Lineage",
  * a campaign carrying a local docs/PHYSICS.md (see above),
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

# The kit-version stamp and the oldest supported kit have one definition, in the upgrade script.
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from upgrade_campaign import OLDEST_SOURCE, STAMP_RE, UPGRADE_STAMP_RE, _version_tuple
except ImportError:                                   # a copy of this file without its sibling
    OLDEST_SOURCE = None

TEXT_EXT = {".md", ".py", ".json", ".tsv", ".txt", ".cfg", ".ini", ".yaml", ".yml"}
# Kit placeholders are UPPER_SNAKE (start with a letter/underscore). Matching only those avoids
# false positives on legitimate LaTeX (\frac{{a}}, x_{{ij}}) and Python f-string ({{...}}) braces.
PLACEHOLDER = re.compile(r"\{\{[A-Z_][A-Z0-9_]*\}\}")
LEAK_LITERALS = ("[[OPTIONAL", "[PROPOSED]", "[[KEEP")
# Windows drive-letter (C:\ or C:/) or UNC (\\server) absolute paths — the realistic portability breaker
# for this Windows/shared-drive project. Applied to CONFIG files only (not prose, which has legit examples).
ABS_PATH = re.compile(r"(?:[A-Za-z]:[\\/])|(?:\\\\[A-Za-z0-9_.$-]+\\)")

CAMPAIGN_REQUIRED = [
    ("campaign definition", "campaign.md"),
    ("worker role", "roles/worker.md"),
    ("verifier role", "roles/verifier.md"),
    ("capstone role", "roles/capstone.md"),
    ("role reference", "roles/REFERENCE.md"),
    ("front door + setup status", "README.md"),
    ("scoreboard ledger", "results/scoreboard.tsv"),
    ("logbook", "results/logbook.md"),
    ("journal", "results/JOURNAL.md"),
    ("config template", "configs/_template.json"),
    ("metric scorer", "scripts/metric.py"),
    ("runner", "scripts/run_campaign.py"),
    ("campaign code", "scripts/experiment.py"),
    ("frozen-core manifest", "scripts/frozen_core.py"),
    ("correctness suite", "tests/correctness_checks.py"),
    ("always-on doctrine", "CLAUDE.md"),
    ("promotion guard hook", "scripts/guard_promotion.py"),
    ("loop heartbeat hook", "scripts/loop_heartbeat.py"),
    ("hook settings", ".claude/settings.json"),
    ("supervisor ownership lock", "scripts/supervisor_lock.py"),
    ("Claude/Codex instruction checker", "scripts/sync_agent_instructions.py"),
    ("Codex launch adapter", "scripts/codex_backend.py"),
    ("Codex verifier policy", "scripts/codex_verifier.py"),
    ("Codex promotion adapter", "scripts/guard_promotion_codex.py"),
    ("loop knobs", "configs/loop.json"),
    ("verdicts dir", "results/verdicts"),
]

PROJECT_REQUIRED_FILES = ["README.md", "PROJECT.md", "CLAUDE.md"]
PROJECT_REQUIRED_DIRS = ["data", "campaigns", "sessions", "reports"]
# The project background lives ONCE in PROJECT.md and is referenced; a campaign-local copy is a fork.
LOCAL_COPY_DOC = "PHYSICS.md"
# The section the campaign driver delivers into every spawned prompt, in PROJECT.md. Its absence is
# checked here AND by the driver's preflight, so it is caught at scaffold time, not at 3 a.m.
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


def scan_leftovers(paths, base: Path, errors: list[str]) -> None:
    """Flag leftover placeholders / OPTIONAL blocks / PROPOSED and KEEP tags / un-stripped .tmpl in `paths`."""
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


def _local_copy_error(rel: str) -> str:
    return (f"campaign carries a LOCAL copy of the project background (must reference the project "
            f"overview, ../../PROJECT.md - never copy): {rel}")


def check_orientation(proj_root: Path, errors: list[str]) -> None:
    """PROJECT.md carries the section the driver delivers every spawn."""
    if not _md_has_section(proj_root / "PROJECT.md", CONSTRAINTS_HEADING):
        errors.append(
            "PROJECT.md has no '## Standing constraints' section - that section is delivered into every "
            "spawned prompt, so without it the delivery is silently empty. Author it in PROJECT.md (see "
            "the project template)."
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
    # PROJECT.md marks the home.
    return cand if (cand / "PROJECT.md").is_file() else None


# The campaign-property enums. An intentional twin of run_campaign.py.tmpl's NOISE_MODELS: the
# validator must run against a scaffolded tree without importing that campaign's runner, which would pull
# in numpy, metric and frozen_core just to read a few strings. The twin is checked
# rather than trusted: tier0_static.py asserts the two lists
# agree, so a mode added on one side and not the other fails the suite instead of drifting.
NOISE_MODELS = ("stochastic", "deterministic")
VERIFY_PRESETS = ("none", "minimal", "light", "heavy", "intensive")
VERIFY_ROWS = ("invariants", "machinery", "gates", "self_check", "self_verify", "independent", "capstone")
METRIC_REVISION_MODES = ("cautious", "autonomous")
AGENT_BACKENDS = ("auto", "claude", "codex", "custom")
VERIFY_STRATEGIES = ("auto", "legacy-nested", "driver-direct")
CLAUDE_EFFORTS = ("low", "medium", "high", "xhigh", "max")
CODEX_EFFORTS = ("minimal", "low", "medium", "high", "xhigh")


def check_loop_files(root: Path, errors: list[str]) -> None:
    """The driver's config/ledger must PARSE, not merely exist: a loop.json missing a hard-dereferenced
    key passes an existence glob and then crashes supervise() at launch (or worse, mid-night). Mirrors
    the runner's own preflight so the gap is caught at scaffold time too."""
    loop_files = list(root.glob("configs/loop.json"))
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
            noise = str(camp.get("noise_model") or "stochastic").strip().lower()
            if noise not in NOISE_MODELS:
                errors.append(f"loop.json campaign.noise_model is {noise!r}; expected one of "
                              + " | ".join(NOISE_MODELS))
            verify_block = cfg.get("verify") if isinstance(cfg.get("verify"), dict) else {}
            preset = verify_block.get("preset")
            if preset is not None:
                p = str(preset).strip().lower()
                if p not in VERIFY_PRESETS:
                    errors.append(f"loop.json verify.preset is {p!r}; expected one of "
                                  + " | ".join(VERIFY_PRESETS) + " (docs/reference/verification-presets.md)")
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
    metric_text = _read_text(root / "scripts" / "metric.py") or ""
    if re.search(r"^PLAUSIBILITY_BOUNDS\s*=\s*None\b", metric_text, re.M):
        print("note: scripts/metric.py sets PLAUSIBILITY_BOUNDS = None - no plausible range, so the "
              "implementation-error check reports 'unavailable' on every result. Set it with the user "
              "(new-campaign: the perfect score to the trivial-predictor score is a good default).")


def check_routing_table(root: Path, errors: list[str]) -> None:
    """Every row of CLAUDE.md's §Where things live table must resolve in THIS campaign.

    Live skills route through that table instead of naming a campaign path, so a dangling row misdirects
    the whole skills layer — and it misdirects QUIETLY, because a wrong path degrades (the agent guesses
    and moves on) rather than erroring. The template says "Keep it true", which is an exhortation; the
    kit's own rule is enforce, don't exhort. A campaign with no table fails too: the skills have nowhere
    to route.
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
        errors.append("CLAUDE.md has no '## Where things live' routing table (or it has no rows) - the "
                      "skills route through it; restore it from the campaign template.")
        return

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
    """A campaign exposes the shared promotion policy to Codex's canonical apply_patch."""
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
    loop_files = list(root.glob("configs/loop.json"))
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
    for state in root.glob("results/correctness_state.json"):
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
    (the brief trim). A table without the source column fails as a whole."""
    text = _md_section_text(root / "campaign.md", LANDMINE_HEADING)
    rows = [L for L in (text or "").splitlines() if L.startswith("|")]
    if len(rows) < 2:
        return
    header = [c.strip().lower() for c in rows[0].strip().strip("|").split("|")]
    if len(header) < 4 or "source" not in header[-1]:
        errors.append("campaign.md §Known landmines: the table has no source column (the fourth, last "
                      "column) - add it and source every row (the user, a ledger id, a verdict).")
        return
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
    # (../../PROJECT.md) — referenced, never copied. There is no standalone mode to detect.
    proj_root = project_root_of(root)

    # 1. Required files present.
    for label, rel in CAMPAIGN_REQUIRED:
        if not (root / rel).exists():
            errors.append(f"missing {label}: {rel}")

    runner = root / "scripts" / "run_campaign.py"
    runner_text = _read_text(runner) or ""
    # The runner's helpers are required files (CAMPAIGN_REQUIRED); the runner must also be wired to the
    # instruction checker, and the Claude/Codex instruction pair and the Codex promotion hook are checked.
    if runner.is_file() and "import sync_agent_instructions as _agent_instructions" not in runner_text:
        errors.append("managed Claude/Codex instructions require runner checker wiring "
                      "(scripts/run_campaign.py does not import sync_agent_instructions)")
    check_agent_instructions(root, errors, chain=True)
    check_codex_hook_wiring(root, errors)

    # 1b. The project home + its background doc. A campaign with no home is lifted into a project
    #     (new-campaign Step 0.1) rather than given campaign-local physics/conventions.
    if proj_root is None:
        errors.append(
            "no project home: expected <project>/campaigns/<slug>/ with ../../PROJECT.md — "
            "every campaign lives in a project; lift this tree in via new-campaign Step 0.1"
        )
    else:
        check_orientation(proj_root, errors)

    # 1c. No campaign-local copy of the project background (validate_project runs the same check tree-wide).
    if (root / "docs" / LOCAL_COPY_DOC).is_file():
        errors.append(_local_copy_error(f"docs/{LOCAL_COPY_DOC}"))

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

    # 1. Required project files + dirs, and PROJECT.md's delivered-constraints and lineage sections.
    for rel in PROJECT_REQUIRED_FILES:
        if not (root / rel).is_file():
            errors.append(f"missing required project file: {rel}")
    for rel in PROJECT_REQUIRED_DIRS:
        if not (root / rel).is_dir():
            errors.append(f"missing required project dir: {rel}/")
    check_orientation(root, errors)
    if not _md_has_section(root / "PROJECT.md", LINEAGE_HEADING):
        errors.append("PROJECT.md has no '## Lineage' section - the campaign/session index lives there "
                      "(see the project template).")
    check_agent_instructions(root, errors, chain=False)       # the managed CLAUDE.md/AGENTS.md pair

    # 2. No leftover tokens in the project-root docs (campaigns validate separately; skip data/).
    scan_leftovers(sorted(root.glob("*.md")), root, errors)

    # 3. Every campaign (incl. archived) is indexed in PROJECT.md §Lineage; no campaign carries a local
    #    copy of the project background.
    lineage, lineage_name = _md_section_text(root / "PROJECT.md", LINEAGE_HEADING), "PROJECT.md §Lineage"
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
            if (d / "docs" / LOCAL_COPY_DOC).is_file():
                errors.append(_local_copy_error(f"campaigns/{slug}/docs/{LOCAL_COPY_DOC}"))

    # 4. Portability: no absolute path hard-coded in a config JSON (prose docs are exempt — legit examples).
    for cfg in root.glob("campaigns/**/configs/*.json"):
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


def older_kit_stamp(root: Path) -> str | None:
    """The kit version a campaign is stamped with, when that kit is older than the oldest this validator
    supports (or unreadable); else None. A tree scaffolded by an older kit is laid out the way that kit
    expected, so checking it here would report every difference as damage - and an agent told its campaign
    is broken may "repair" a frozen record. Such a tree is validated with the kit version stamped in it."""
    if OLDEST_SOURCE is None:
        return None
    for rel in ("campaign.md", "results/logbook.md"):
        try:
            text = (root / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        upgrades = UPGRADE_STAMP_RE.findall(text)
        m = STAMP_RE.search(text)
        version = upgrades[-1][0] if upgrades else (m.group(1) if m else None)
        if version is None:
            continue
        t = _version_tuple(version)
        return version if t is None or t < OLDEST_SOURCE else None
    return None


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python validate_campaign.py <target_dir>", file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).resolve()
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 2

    # PROJECT.md + campaigns/ marks a project root.
    is_project = (root / "PROJECT.md").is_file() and (root / "campaigns").is_dir()
    kind = "PROJECT" if is_project else "CAMPAIGN"

    if not is_project:
        old = older_kit_stamp(root)
        if old is not None:
            _say(f"REFUSING: this campaign is stamped physkit {old}, older than this validator supports "
                 f"(v{'.'.join(map(str, OLDEST_SOURCE))}+).")
            _say("  Validate it with the kit version stamped in it. Do NOT edit this tree to satisfy this check.")
            return 3

    errors = validate_project(root) if is_project else validate_campaign(root)

    if errors:
        _say(f"{kind} VALIDATION FAILED - {len(errors)} issue(s):\n")
        for e in errors:
            _say(f"  - {e}")
        _say(f"\nResolve every item above; a {kind.lower()} with an unresolved issue is not done. If this tree was")
        _say("scaffolded by an older kit, validate it with that kit instead; never edit a frozen tree to satisfy this check.")
        return 1

    print(f"{kind} VALIDATION PASSED - {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
