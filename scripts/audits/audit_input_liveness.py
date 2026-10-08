"""audit_input_liveness.py - every quantity the prompts tell the loop to reason about must have
a LIVE data path feeding it.

The prompt-surface audit verifies the RULE is present. This one catches a different failure: the
rule is present and the QUANTITY it relies on is wired to nothing, or to the wrong input, or is
silently zero. The rule reads perfectly and steers on a number that never arrives.

For each quantity this audit checks, in order:

  (a) STATIC  - some producer under `scripts/` actually writes the field, and
  (b) LIVE    - at least one stored result carries it NON-NULL and NOT-ALWAYS-ZERO.

On a fresh campaign (0 results) an empty store is CORRECT at t0, so (b) degrades to (a) - but a
missing producer still hard-fails, because "no data yet" must not excuse "no wiring ever".

    python audit_input_liveness.py <campaign_dir> [--quantities docs/liveness.json]

Quantities come from the campaign's `docs/liveness.json` if present; otherwise they are DERIVED
from the campaign itself - the scoreboard header, the primary/guardrail metric names in
`configs/loop.json`, and the keys the result JSONs already carry. Deriving rather than hardcoding
is the point: a hand-maintained list goes stale in exactly the way this audit exists to catch.

The always-zero check is ported deliberately: `n_avg` passed every presence check in the deployed
loop while being silently 0, so "present" was never the right test - "present and not degenerate"
is.

Exit 0 = all live. Exit 1 = at least one relied-upon quantity is dangling.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _surface import discover_roles, find_campaign, flatten, norm, surface  # noqa: E402

ok_n = fail_n = 0


def report(name: str, ok: bool, detail: str) -> None:
    global ok_n, fail_n
    print(("  ok   " if ok else "  FAIL ") + f"{name}: {detail}")
    if ok:
        ok_n += 1
    else:
        fail_n += 1


def results(campaign: Path) -> list[dict]:
    out = []
    for f in sorted((campaign / "results").glob("result_*.json")):
        try:
            out.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception:
            continue
    return out


def flat(d: dict, prefix: str = "") -> dict:
    """One level of nesting flattened, so guardrail sub-keys are visible as quantities."""
    out = {}
    for k, v in d.items():
        if isinstance(v, dict) and not prefix:
            out.update(flat(v, k + "."))
        else:
            out[prefix + k] = v
    return out


def producer_writes(campaign: Path, key: str) -> tuple[bool, str]:
    """STATIC liveness: some script writes this field. The check the fresh-campaign path
    depends on - a missing producer must hard-fail even with zero results on disk."""
    for f in sorted((campaign / "scripts").rglob("*.py")):
        try:
            if f'"{key}"' in f.read_text(encoding="utf-8"):
                return True, f'producer scripts/{f.name} writes "{key}"'
        except OSError:
            continue
    return False, f'NO producer under scripts/ writes "{key}"'


def derive_quantities(campaign: Path, res: list[dict]) -> tuple[list[str], str]:
    """Quantities the campaign itself says it reasons about."""
    qs: list[str] = []
    sb = campaign / "results" / "scoreboard.tsv"
    if sb.is_file():
        # The header is the first NON-COMMENT line. The scoreboard opens with `#` description
        # lines; taking line 1 blindly turned that whole sentence into a "column"
        # and then failed it for having no producer. A comment is not a quantity.
        for line in sb.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            qs += [c.strip() for c in line.split("\t") if c.strip()]
            break
    cfg = campaign / "configs" / "loop.json"
    if cfg.is_file():
        try:
            c = json.loads(cfg.read_text(encoding="utf-8-sig"))
            camp = c.get("campaign") or {}
            qs += [k for k in ("metric_version", "data_version") if k in camp]
        except Exception:
            pass
    for r in res:
        qs += list(flat(r))
    drop = {"exp_id", "exp_name", "utc", "config", "notes", "status"}
    seen, out = set(), []
    for q in qs:
        if q and q not in seen and q not in drop and not q.startswith("config."):
            seen.add(q)
            out.append(q)
    return out, "derived from scoreboard header + loop.json + result JSONs"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("campaign", nargs="?", default=".")
    ap.add_argument("--quantities")
    a = ap.parse_args()

    campaign = find_campaign(Path(a.campaign))
    res = results(campaign)
    fresh = not res

    qp = Path(a.quantities) if a.quantities else (campaign / "docs" / "liveness.json")
    if qp.is_file():
        quantities = json.loads(qp.read_text(encoding="utf-8"))["quantities"]
        src = str(qp)
    else:
        quantities, src = derive_quantities(campaign, res)

    print(f"campaign  : {campaign}")
    print(f"results   : {len(res)} stored"
          + ("   [FRESH CAMPAIGN MODE: store-backed checks degrade to static producer checks]"
             if fresh else ""))
    print(f"quantities: {len(quantities)} {src}\n")

    placeholders = [q for q in quantities if "{{" in q and "}}" in q]
    if placeholders:
        # An unresolved scaffold placeholder is a DIFFERENT diagnosis from a dangling quantity,
        # and reporting it as "no producer writes it" sends the reader hunting for wiring that
        # was never supposed to exist yet. Name it, point at the tool that owns it, move on.
        print("  NOTE unresolved scaffold placeholder(s) in the scoreboard header: "
              + ", ".join(placeholders))
        print("       the campaign is not fully scaffolded; that is validate_campaign.py's "
              "check, not this one. Skipping them here.\n")
        quantities = [q for q in quantities if q not in placeholders]

    for key in quantities:
        if fresh:
            ok, det = producer_writes(campaign, key)
            report(key + " [static]", ok, det)
            continue
        vals = [flat(r).get(key) for r in res]
        present = [v for v in vals if v is not None]
        if not present:
            ok, det = producer_writes(campaign, key)
            report(key, False,
                   f"NULL in all {len(res)} result(s)" + ("; " + det if ok else f"; {det}"))
            continue
        # Present is not enough: a field wired to a constant zero or an empty string passes
        # every presence check while steering nothing. This is the n_avg failure, generalized.
        degenerate = all(
            (isinstance(v, (int, float)) and v == 0) or (isinstance(v, str) and not v.strip())
            or (isinstance(v, (list, dict)) and not v)
            for v in present)
        if degenerate:
            report(key, False,
                   f"present in {len(present)}/{len(res)} result(s) but ALWAYS zero/empty - "
                   "wired to nothing, or wired to a default that never gets set")
        else:
            report(key, True, f"non-null and non-degenerate in {len(present)}/{len(res)}")

    # The other half of the failure class: a quantity the PROMPTS name that no result carries.
    # A rule can only steer on a number the record actually has.
    print()
    have = set(quantities)
    roles, _how = discover_roles(campaign)
    surf = norm(" ".join(txt for role in roles
                         for _, _, txt in flatten(surface(campaign, role))))
    named_but_absent = []
    for q in sorted(have):
        if len(q) > 4 and norm(q) not in surf:
            named_but_absent.append(q)
    if named_but_absent:
        print("  note: recorded but never mentioned in any rendered prompt - these steer "
              "nothing, which is fine for bookkeeping columns and a gap for anything else:")
        print("        " + ", ".join(named_but_absent))

    print(f"\ninput-liveness audit: {ok_n} ok, {fail_n} FAIL")
    return 1 if fail_n else 0


if __name__ == "__main__":
    sys.exit(main())
