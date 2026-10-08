"""audit_prompt_surface.py - verify every relied-upon rule is physically present in each
role's RENDERED context.

It checks PhysKit's surfaces: `--show-prompt <role>` + `CLAUDE.md` + the files the prompt names. The
doctrine is `docs/reference/prompt-surface-audit.md`: doctrine only governs an agent whose rendered
context contains it, and a rule missing from a role's render is a hole the loop walks straight through.

    python audit_prompt_surface.py <campaign_dir> [--rules docs/prompt_rules.json] [--strict]

Rules come from the campaign's own `docs/prompt_rules.json` when it has one - the campaign's
own rules ARE the checklist - and otherwise from the kit-doctrine defaults below, which are
the disciplines the shipped driver assumes each role obeys. Rule file shape:

    {"rules": [{"name": "...", "tokens": ["..."], "roles": ["worker"], "tier": "spawn"}]}

`tier` is the WEAKEST tier that counts as present: "spawn" (must be in the literal spawn
string), "auto" (spawn or CLAUDE.md), "named" (anywhere in the render, including a file the
prompt merely tells the agent to read). A rule satisfied only below its declared tier is
reported as WEAK, not as a pass - see `_surface.py` for why that distinction is the point.

Exit 0 = clean. Exit 1 = at least one rule missing (and, with --strict, any WEAK rule too).
Run at launch and after ANY prompt change; the audit is cheap and mechanical, so gate on it
rather than trusting that it happened.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _surface import discover_roles, find_campaign, flatten, norm, surface  # noqa: E402

TIER_ORDER = {"spawn": 0, "auto": 1, "named": 2}

# Kit-doctrine defaults: the rules the SHIPPED driver relies on each role obeying. Every token
# below is grepped against the real render, so this list is falsifiable - if the kit's prompts
# change wording, this audit fails and one of the two has to move.
DEFAULT_RULES = [
    # --- worker ---
    {"name": "a result outside the plausible range is settled first", "tokens": ["plausible range"], "roles": ["worker"],
     "tier": "spawn"},
    {"name": "the worker CHOOSES its unit (no queue)",
     "tokens": ["there is no queue"], "roles": ["worker"], "tier": "spawn"},
    {"name": "one unit per spawn", "tokens": ["you never start a second unit"],
     "roles": ["worker"], "tier": "spawn"},
    {"name": "a stopping judgement is the worker's, written as NEXT: STOP",
     "tokens": ["stop -"], "roles": ["worker"], "tier": "spawn"},
    {"name": "the ledger is the loop's only memory",
     "tokens": ["work you do not record did not happen"], "roles": ["worker"], "tier": "spawn"},
    {"name": "solve in YOUR shell, never a background subagent",
     "tokens": ["never inside a background subagent"], "roles": ["worker"], "tier": "spawn"},
    {"name": "heartbeat is the dead-worker signal", "tokens": ["heartbeat"],
     "roles": ["worker"], "tier": "spawn"},
    {"name": "a mid-unit anomaly is recorded and probed as a unit, not chased ad hoc",
     "tokens": ["anomaly is information"], "roles": ["worker"], "tier": "spawn"},
    {"name": "escalate a user-only fork", "tokens": ["escalate.md"], "roles": ["worker"],
     "tier": "spawn"},
    {"name": "the FROZEN metric is named to the worker", "tokens": ["frozen metric"],
     "roles": ["worker"], "tier": "spawn"},
    {"name": "a metric fault is a declared epoch, never an in-place edit",
     "tokens": ["metric epoch"], "roles": ["worker"], "tier": "spawn"},
    {"name": "a metric epoch owes a re-baseline before any cross-epoch ranking",
     "tokens": ["re-baseline"], "roles": ["worker"], "tier": "spawn"},
    # --- every role ---
    {"name": "user notes are acknowledged, not silently absorbed",
     "tokens": ["user notes"], "roles": ["worker"], "tier": "spawn"},
    {"name": "campaign definition is re-read (it does not auto-load)",
     "tokens": ["campaign.md"], "roles": ["worker"], "tier": "spawn"},
    {"name": "comparability tags travel with the number",
     "tokens": ["metric_version"], "roles": ["worker"], "tier": "named"},
    {"name": "a-priori bound / plausibility is a gate",
     "tokens": ["plausib"], "roles": ["worker"], "tier": "named"},
    # --- verifier (the role is discovered from the driver, not assumed) ---
    {"name": "verification is INDEPENDENT of the generating reasoning",
     "tokens": ["never saw the generating reasoning"], "roles": ["verifier"], "tier": "spawn"},
    {"name": "a verdict ARTIFACT is required, with the refuter named",
     "tokens": ["results/verdicts/"], "roles": ["verifier"], "tier": "spawn"},
    {"name": "every verdict field filled", "tokens": ["every field filled"],
     "roles": ["verifier"], "tier": "spawn"},
    {"name": "judge the claim AS RECORDED, not as re-derived",
     "tokens": ["as recorded"], "roles": ["verifier"], "tier": "spawn"},
    {"name": "negatives and kill-claims get the SAME rigor as wins",
     "tokens": ["same rigor"], "roles": ["verifier"], "tier": "spawn"},
    {"name": "the verifier never edits what it judges",
     "tokens": ["do not edit the scoreboard"], "roles": ["verifier"], "tier": "spawn"},
    {"name": "promotion is not the verifier's call",
     "tokens": ["never yours"], "roles": ["verifier"], "tier": "spawn"},
    {"name": "a REFUTED/INCONCLUSIVE verdict produces a named next unit",
     "tokens": ["refuted or inconclusive"], "roles": ["verifier"], "tier": "spawn"},
    {"name": "a verified kill of the metric is what a metric epoch cites",
     "tokens": ["metric epoch"], "roles": ["verifier"], "tier": "spawn"},
    # --- all roles: the project's standing constraints ride IN the spawn string ---
    {"name": "standing constraints delivered by value, not by reference",
     "tokens": ["standing constraints"], "roles": ["worker", "verifier"],
     "tier": "spawn"},
]


def load_rules(campaign: Path, explicit: str | None) -> tuple[list[dict], str]:
    p = Path(explicit) if explicit else (campaign / "docs" / "prompt_rules.json")
    if p.is_file():
        data = json.loads(p.read_text(encoding="utf-8"))
        return data["rules"], str(p)
    return DEFAULT_RULES, "(kit-doctrine defaults - no docs/prompt_rules.json in this campaign)"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("campaign", nargs="?", default=".")
    ap.add_argument("--rules")
    ap.add_argument("--strict", action="store_true",
                    help="treat a rule present only BELOW its declared tier as a failure")
    a = ap.parse_args()

    campaign = find_campaign(Path(a.campaign))
    rules, src = load_rules(campaign, a.rules)
    print(f"campaign: {campaign}")
    roles, how = discover_roles(campaign)
    print(f"rules   : {len(rules)} from {src}")
    print(f"roles   : {', '.join(roles)}  [{how}]\n")

    surfaces = {r: surface(campaign, r) for r in roles}
    for role in roles:
        tiers = surfaces[role]
        sizes = ", ".join(f"{t}={sum(len(x[1]) for x in tiers.get(t, [])):,}c"
                          for t in ("spawn", "auto", "named"))
        print(f"  [{role}] {sizes}  named: "
              + ", ".join(s for s, _ in tiers.get("named", [])))
    print()

    n_missing = n_weak = 0
    for rule in rules:
        toks = [norm(t) for t in rule["tokens"]]
        want = TIER_ORDER[rule.get("tier", "named")]
        for role in rule.get("roles", list(roles)):
            if role not in surfaces:
                continue
            found_at, found_src = None, None
            for tier, sname, text in flatten(surfaces[role]):
                nt = norm(text)
                if all(t in nt for t in toks):
                    found_at, found_src = tier, sname
                    break
            if found_at is None:
                print(f"  MISS [{role:7s}] {rule['name']}  tokens={rule['tokens']}")
                n_missing += 1
            elif TIER_ORDER[found_at] > want:
                print(f"  WEAK [{role:7s}] {rule['name']}  -> only in {found_at} "
                      f"({found_src}); declared tier is {rule.get('tier')}")
                n_weak += 1
            else:
                print(f"  ok   [{role:7s}] {rule['name']}  <- {found_src}")

    print(f"\nprompt-surface audit: {n_missing} MISSING, {n_weak} weak"
          + ("" if not n_weak else "  (weak = present, but one indirection further from the "
                                   "agent than the rule was declared to need)"))
    return 1 if (n_missing or (a.strict and n_weak)) else 0


if __name__ == "__main__":
    sys.exit(main())
