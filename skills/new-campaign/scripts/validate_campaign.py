#!/usr/bin/env python3
"""validate_campaign.py — gate a generated autoresearch CAMPAIGN tree, or a PROJECT tree.

The target is auto-detected:
  * a PROJECT root (has PROJECT.md + LINEAGE.md + campaigns/)  -> project-tree validation, or
  * a campaign tree                                            -> campaign validation.

EVERY campaign lives inside a project (<project>/campaigns/<name>/ with ../../PROJECT.md + ../../LINEAGE.md);
there is no standalone/bare-campaign mode. The physics + conventions + instrument docs therefore live in the
project's shared/ and are REFERENCED, never copied.

Campaign validation fails (exit 1) on anything new-campaign left unresolved:
  * a literal {{PLACEHOLDER}} token, a dangling [[OPTIONAL … block, a stray [PROPOSED] tag,
  * an un-stripped .tmpl file,
  * a missing required file (charter, scoreboard, journal, discoveries, config template, the two code stubs),
  * no project home above the campaign, or a missing shared/{PHYSICS,CONVENTIONS,INSTRUMENT}.md in it,
  * a LOCAL copy of any shared doc in the campaign's docs/ (design §4.1).
Legacy trees using the retired multi-stage suffix (charter_<NAME>.md / configs_<NAME>/ / results_<NAME>/) still
validate — the required-file checks glob — but new stages are scaffolded as sibling campaigns, not suffixes.

Project-tree validation fails (exit 1) if the project home is malformed:
  * a missing required file/dir (PROJECT.md, LINEAGE.md, CLAUDE.md, DISCOVERIES.md, ENGINEERING_NOTES.md,
    shared/{PHYSICS,CONVENTIONS,INSTRUMENT}.md, data/, campaigns/, sessions/, reports/),
  * a leftover {{PLACEHOLDER}}/[[OPTIONAL/[PROPOSED] in a project-root or shared/ doc,
  * a campaign in campaigns/ (or campaigns/_archive/) NOT indexed in LINEAGE.md,
  * a campaign carrying a LOCAL copy of a shared doc (docs/PHYSICS.md|CONVENTIONS.md|INSTRUMENT.md) —
    it must reference ../../shared/, never copy (design §4.1),
  * an ABSOLUTE path hard-coded in a config JSON (the portability breaker; prose docs are exempt because
    they legitimately carry example paths — the invariant is that the tree relocates as one unit, the only
    absolute path being the resolved data_path pointer in PROJECT.md / data/DATA_PATH.txt).

Usage:
    python validate_campaign.py <target_dir>
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

TEXT_EXT = {".md", ".py", ".json", ".tsv", ".txt", ".cfg", ".ini", ".yaml", ".yml"}
# Kit placeholders are UPPER_SNAKE (start with a letter/underscore). Matching only those avoids
# false positives on legitimate LaTeX (\frac{{a}}, x_{{ij}}) and Python f-string ({{...}}) braces.
PLACEHOLDER = re.compile(r"\{\{[A-Z_][A-Z0-9_]*\}\}")
LEAK_LITERALS = ("[[OPTIONAL", "[PROPOSED]")
# Windows drive-letter (C:\ or C:/) or UNC (\\server) absolute paths — the realistic portability breaker
# for this Windows/shared-drive project. Applied to CONFIG files only (not prose, which has legit examples).
ABS_PATH = re.compile(r"(?:[A-Za-z]:[\\/])|(?:\\\\[A-Za-z0-9_.$-]+\\)")

CAMPAIGN_REQUIRED_GLOBS = [
    ("program charter", "docs/charter*.md"),
    ("scoreboard ledger", "results*/scoreboard.tsv"),
    ("index", "results*/INDEX.md"),
    ("logbook", "results*/logbook.md"),
    ("journal", "results*/JOURNAL*.md"),
    ("discoveries", "results*/DISCOVERIES*.md"),
    ("config template", "configs*/_template.json"),
    ("metric scorer", "scripts/metric.py"),
    ("runner", "scripts/run_campaign.py"),
    ("frozen-core manifest", "scripts/frozen_core.py"),
    ("correctness suite", "tests/correctness_checks.py"),
    ("always-on doctrine", "CLAUDE.md"),
    ("discoveries guard hook", "scripts/guard_discoveries.py"),
    ("loop heartbeat hook", "scripts/loop_heartbeat.py"),
    ("hook settings", ".claude/settings.json"),
    ("loop knobs", "configs*/loop.json"),
    ("unit queue", "results*/queue.json"),
    ("predictions dir", "predictions"),
    ("verdicts dir", "results*/verdicts"),
]

PROJECT_REQUIRED_FILES = [
    "PROJECT.md", "LINEAGE.md", "CLAUDE.md", "DISCOVERIES.md", "ENGINEERING_NOTES.md",
    "shared/PHYSICS.md", "shared/CONVENTIONS.md", "shared/INSTRUMENT.md",
]
PROJECT_REQUIRED_DIRS = ["data", "shared", "campaigns", "sessions", "reports"]
# Shared docs live once at <project>/shared/ and are referenced; a campaign-local copy is a fork (design §4.1).
SHARED_DOCS = ("PHYSICS.md", "CONVENTIONS.md", "INSTRUMENT.md")


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
    return cand if (cand / "PROJECT.md").is_file() and (cand / "LINEAGE.md").is_file() else None


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
                               ("planner.cadence_units", ("planner", "cadence_units")),
                               ("plateau.wall_clock_hours", ("plateau", "wall_clock_hours"))):
                node = cfg
                try:
                    for k in keys:
                        node = node[k]
                    float(node)
                except Exception:
                    errors.append(f"loop.json is missing the numeric key the driver requires: {name}")
        except Exception as exc:
            errors.append(f"loop.json does not parse as JSON ({exc})")
    queue_files = list(root.glob("results*/queue.json"))
    if queue_files:
        try:
            q = json.loads(_read_text(queue_files[0]) or "")
            assert isinstance(q.get("next"), list) and isinstance(q.get("shelved"), list)
        except Exception as exc:
            errors.append(f"queue.json does not parse as a queue ledger ({exc})")


def validate_campaign(root: Path) -> list[str]:
    errors: list[str] = []

    # Every campaign lives inside a project, so the physics/conventions/instrument docs are SHARED at
    # ../../shared/ — referenced, never copied (design §4.1). There is no standalone mode to detect.
    proj_root = project_root_of(root)

    # 1. Required files present (glob-based; tolerates the retired _<NAME> suffix in legacy trees).
    for label, pattern in CAMPAIGN_REQUIRED_GLOBS:
        if not list(root.glob(pattern)):
            errors.append(f"missing {label}: no file matches '{pattern}'")

    # 1b. The project home + its shared docs. A campaign with no home is a legacy bare tree — lift it into a
    #     project (new-campaign Step 0.1) rather than authoring campaign-local physics/conventions.
    if proj_root is None:
        errors.append(
            "no project home: expected <project>/campaigns/<slug>/ with ../../PROJECT.md + ../../LINEAGE.md — "
            "every campaign lives in a project; lift this tree in via new-campaign Step 0.1"
        )
    else:
        for doc in SHARED_DOCS:
            if not (proj_root / "shared" / doc).is_file():
                errors.append(f"missing shared reference: no '../../shared/{doc}'")

    # 1c. No campaign-local copy of a shared doc (validate_project runs the same check tree-wide).
    for doc in SHARED_DOCS:
        if (root / "docs" / doc).is_file():
            errors.append(
                f"campaign carries a LOCAL copy of a shared doc (must reference ../../shared/): docs/{doc}"
            )

    # 1d. The loop driver's config + queue ledger parse and carry the keys the driver dereferences.
    check_loop_files(root, errors)

    # 2. No leftover tokens / un-stripped templates anywhere in the tree.
    scan_leftovers(sorted(root.rglob("*")), root, errors)
    return errors


def validate_project(root: Path) -> list[str]:
    errors: list[str] = []

    # 1. Required project files + dirs.
    for rel in PROJECT_REQUIRED_FILES:
        if not (root / rel).is_file():
            errors.append(f"missing required project file: {rel}")
    for rel in PROJECT_REQUIRED_DIRS:
        if not (root / rel).is_dir():
            errors.append(f"missing required project dir: {rel}/")

    # 2. No leftover tokens in the project-root docs + shared/ (campaigns validate separately; skip data/).
    root_docs = [p for p in root.glob("*.md")]
    shared_docs = list((root / "shared").glob("*.md")) if (root / "shared").is_dir() else []
    scan_leftovers(sorted(root_docs + shared_docs), root, errors)

    # 3. Every campaign (incl. archived) is indexed in LINEAGE.md; no campaign carries a LOCAL shared-doc copy.
    lineage = _read_text(root / "LINEAGE.md") or ""
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
                errors.append(f"campaign not indexed in LINEAGE.md: campaigns/{('_archive/' if d.parent.name=='_archive' else '')}{slug}")
            for shared_doc in SHARED_DOCS:
                if (d / "docs" / shared_doc).is_file():
                    errors.append(
                        f"campaign carries a LOCAL copy of a shared doc (must reference ../../shared/): "
                        f"campaigns/{slug}/docs/{shared_doc}"
                    )

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


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python validate_campaign.py <target_dir>", file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).resolve()
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 2

    is_project = (root / "PROJECT.md").is_file() and (root / "LINEAGE.md").is_file() and (root / "campaigns").is_dir()
    kind = "PROJECT" if is_project else "CAMPAIGN"
    errors = validate_project(root) if is_project else validate_campaign(root)

    if errors:
        print(f"{kind} VALIDATION FAILED - {len(errors)} issue(s):\n")
        for e in errors:
            print(f"  - {e}")
        print(f"\nResolve every item above; a {kind.lower()} with an unresolved issue is not done.")
        return 1

    print(f"{kind} VALIDATION PASSED - {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
