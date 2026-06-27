#!/usr/bin/env python3
"""validate_campaign.py — gate a generated autoresearch campaign tree.

Fails (exit 1) if the new-campaign generation left anything unresolved:
  * a literal {{PLACEHOLDER}} token,
  * a dangling [[OPTIONAL … block,
  * a stray [PROPOSED] tag,
  * an un-stripped .tmpl file,
  * a missing required file (program charter, scoreboard, journal, discoveries, config template,
    and the two code stubs).

Multi-campaign trees (program_<NAME>.md / configs_<NAME>/ / results_<NAME>/) are handled by globbing.

Usage:
    python validate_campaign.py <target_dir>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

TEXT_EXT = {".md", ".py", ".json", ".tsv", ".txt", ".cfg", ".ini", ".yaml", ".yml"}
# Kit placeholders are UPPER_SNAKE (start with a letter/underscore). Matching only those avoids
# false positives on legitimate LaTeX (\frac{{a}}, x_{{ij}}) and Python f-string ({{...}}) braces.
PLACEHOLDER = re.compile(r"\{\{[A-Z_][A-Z0-9_]*\}\}")
LEAK_LITERALS = ("[[OPTIONAL", "[PROPOSED]")

REQUIRED_GLOBS = [
    ("program charter", "docs/program*.md"),
    ("conventions reference", "docs/CONVENTIONS.md"),
    ("physics reference", "docs/PHYSICS.md"),
    ("scoreboard ledger", "results*/scoreboard.tsv"),
    ("index", "results*/INDEX.md"),
    ("logbook", "results*/logbook.md"),
    ("journal", "results*/JOURNAL*.md"),
    ("discoveries", "results*/DISCOVERIES*.md"),
    ("config template", "configs*/_template.json"),
    ("metric scorer", "scripts/metric.py"),
    ("runner", "scripts/run_campaign.py"),
]


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python validate_campaign.py <target_dir>", file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).resolve()
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 2

    errors: list[str] = []

    # 1. Required files present (glob-based for multi-campaign suffixes).
    for label, pattern in REQUIRED_GLOBS:
        if not list(root.glob(pattern)):
            errors.append(f"missing {label}: no file matches '{pattern}'")

    # 2. No leftover tokens / un-stripped templates.
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix == ".tmpl":
            errors.append(f"un-stripped template (.tmpl not removed): {path.relative_to(root)}")
            continue
        if path.suffix.lower() not in TEXT_EXT:
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")   # strips a UTF-8 BOM if present
        except UnicodeDecodeError:
            try:
                text = path.read_text(encoding="utf-16")   # PowerShell/Out-File default on Windows
            except (UnicodeError, OSError):
                # Don't silently skip a text file we can't read — it could hide a leftover token.
                errors.append(
                    f"could not decode (not UTF-8/UTF-16), cannot scan for leftovers: {path.relative_to(root)}"
                )
                continue
        except OSError:
            continue
        rel = path.relative_to(root)
        for i, line in enumerate(text.splitlines(), 1):
            if PLACEHOLDER.search(line):
                errors.append(f"unresolved placeholder {rel}:{i}: {line.strip()[:100]}")
            for lit in LEAK_LITERALS:
                if lit in line:
                    errors.append(f"unresolved {lit} {rel}:{i}: {line.strip()[:100]}")

    if errors:
        print(f"CAMPAIGN VALIDATION FAILED - {len(errors)} issue(s):\n")
        for e in errors:
            print(f"  - {e}")
        print("\nResolve every item above; a campaign with an unresolved token is not done.")
        return 1

    print(f"CAMPAIGN VALIDATION PASSED - {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
