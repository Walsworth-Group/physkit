"""check_prompt_leaks.py - sealed-value scan of the loop-visible prompt surface.

Ported from the Co-scientist's G-1 leak check (2026-07-05) and retargeted at PhysKit's rendered
surfaces. The provenance claim a blind campaign can actually make is NOT "the prompt author
never saw the truth" - it is **"no withheld value appears in any loop-visible artifact, verified
by these greps"**. This script is that verification.

    python check_prompt_leaks.py <campaign_dir> --withheld <FILE OUTSIDE THE CAMPAIGN>
    PHYSKIT_WITHHELD_FILE=... python check_prompt_leaks.py <campaign_dir>

## The withheld list must live outside the campaign tree

The token list IS the sealed information. The Co-scientist could keep it in a source file
because that repo was not the blinded surface; here the campaign tree is exactly what the loop
reads, so a `configs/blinding.json` would leak the very values it exists to protect - the
checker would become the leak. **This script refuses to run if the withheld file is inside the
campaign tree**, and it never echoes a token: hits are reported by source, line, and a masked
token, with the matched line shown only under --show-lines.

Withheld file shape (JSON), operator-side, never committed to the campaign:

    {"tokens": ["892", "2.283", "209"], "note": "free text, not scanned"}

## Matching semantics (ported verbatim, and deliberate)

A token must START a number - not preceded by a digit or a decimal point - so "892" catches
"892", "892200" and "892.2" but not "1892" or "0.892". Prefix rather than whole-word, because a
sealed value shows up in many unit scalings and a whole-word match misses every one of them.

Opt-in by construction: an empty or absent withheld list means the campaign is not blinded, and
the check reports "not a blind campaign" and exits 0 rather than pretending to have verified
something.

Exit 0 = clean (or not blinded). Exit 1 = at least one hit. Run after ANY prompt edit.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _surface import discover_roles, find_campaign, flatten, surface  # noqa: E402


def token_re(token: str) -> re.Pattern[str]:
    return re.compile(r"(?<![0-9.])" + re.escape(token))


def mask(token: str) -> str:
    """Report WHICH token fired without reprinting it - the report is an artifact too, and a
    leak report that quotes the sealed value has moved the leak rather than closed it."""
    return token[0] + "*" * (len(token) - 1) if len(token) > 1 else "*"


def load_withheld(path: Path | None, campaign: Path) -> tuple[list[str], str]:
    if path is None:
        return [], "(no withheld file given)"
    p = path.resolve()
    try:
        p.relative_to(campaign.resolve())
    except ValueError:
        pass
    else:
        raise SystemExit(
            f"REFUSING TO RUN: the withheld file {p} is INSIDE the campaign tree {campaign}.\n"
            "The token list is the sealed information. Kept in the tree, it is loop-visible, so "
            "the checker itself becomes the leak it exists to prevent. Move it outside the "
            "campaign (operator-side) and pass its path.")
    if not p.is_file():
        raise SystemExit(f"withheld file not found: {p}")
    data = json.loads(p.read_text(encoding="utf-8"))
    toks = [str(t) for t in (data.get("tokens") or []) if str(t).strip()]
    return toks, str(p)


def scan(text: str, tokens: list[str]) -> list[tuple[int, str, str]]:
    pats = [(t, token_re(t)) for t in tokens]
    hits = []
    for n, line in enumerate(text.splitlines(), start=1):
        for tok, pat in pats:
            if pat.search(line):
                hits.append((n, tok, line.strip()))
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("campaign", nargs="?", default=".")
    ap.add_argument("--withheld", default=os.environ.get("PHYSKIT_WITHHELD_FILE"))
    ap.add_argument("--show-lines", action="store_true",
                    help="print the matched line (it contains the sealed value - avoid in logs)")
    a = ap.parse_args()

    campaign = find_campaign(Path(a.campaign))
    tokens, src = load_withheld(Path(a.withheld) if a.withheld else None, campaign)
    if not tokens:
        print(f"campaign: {campaign}")
        print(f"withheld list: {src} -> EMPTY")
        print("leak-check: not a blind campaign; nothing to verify. (Blinding is opt-in: an "
              "empty list means no claim is being made, not that a claim was checked.)")
        return 0

    print(f"campaign: {campaign}")
    print(f"withheld list: {src} ({len(tokens)} token(s), values not echoed)\n")

    roles, how = discover_roles(campaign)
    print(f"roles: {', '.join(roles)}  [{how}]\n")
    surfaces = {r: surface(campaign, r) for r in roles}
    seen: set[tuple[str, str]] = set()
    all_hits = 0
    n_sources = 0
    for role in roles:
        for tier, sname, text in flatten(surfaces[role]):
            if (tier, sname) in seen:      # CLAUDE.md/campaign.md are shared between roles
                continue
            seen.add((tier, sname))
            n_sources += 1
            for line_no, tok, line in scan(text, tokens):
                all_hits += 1
                shown = f": {line}" if a.show_lines else ""
                print(f"  LEAK [{tier}] {sname}:{line_no} token={mask(tok)}{shown}")

    print(f"\nleak-check: {n_sources} rendered source(s), {len(tokens)} token(s) - "
          + ("CLEAN" if not all_hits else f"{all_hits} HIT(S)"))
    if all_hits and not a.show_lines:
        print("re-run with --show-lines to see the offending text (it contains the value).")
    return 1 if all_hits else 0


if __name__ == "__main__":
    sys.exit(main())
