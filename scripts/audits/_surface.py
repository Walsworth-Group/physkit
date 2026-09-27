"""_surface.py - assemble a campaign role's RENDERED context, once, for every audit.

`docs/reference/prompt-surface-audit.md` step 3: "The template is not the render. Run the
renderer and capture what the agent actually receives." All three audits in this directory
share this module so they cannot disagree about what the surface IS - the same reason the
driver funnels both spawn sites and `--show-prompt` through one `build_prompt()`.

A PhysKit role's context has three TIERS, and the distinction is the whole point:

  spawn  - the literal string the driver spawns the agent with, obtained by running the
           campaign's own driver (`run_campaign.py --show-prompt ROLE`). Strongest guarantee:
           the agent cannot not-receive it.
  auto   - the campaign `CLAUDE.md`, auto-loaded by the harness on top of the spawn string.
           Nearly as strong, but only for sessions the harness starts in that folder.
  named  - files the spawn string TELLS the agent to read (campaign.md, roles/<role>.md, ...).
           Weakest: the design intends them to be read, and a rule living only here is in
           force only if the agent complies. Discovered by parsing the spawn string rather
           than hardcoded, so the tier tracks prompt edits automatically.

A rule found only in `named` is reported as such rather than as a pass. That is not pedantry:
the surfaces table in the reference doc exists because "subagent prompts REPLACE the doctrine
stack", and a rule one indirection away from the render is exactly the kind of thing that
looks present in a grep of the repo and is absent from the agent.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# Roles are DISCOVERED from the campaign's own driver, never hardcoded.
#
# v0.10.0 added a third role (`verifier`) to a driver that had two. A hardcoded pair would have
# kept passing while auditing none of it - and the verifier is the honesty check, so it is the
# worst role to silently skip. This is the failure class the audits exist to catch, so the
# audits do not get to commit it. `KNOWN_ROLES` is only a probe fallback; the source scan is
# what generalizes to a role nobody here has heard of.
KNOWN_ROLES = ("worker", "verifier", "capstone", "critic", "refuter", "analyst")
_SHOW_PROMPT_CHOICES = re.compile(r"--show-prompt.*?choices=\(([^)]*)\)", re.S)

# Files the prompts name. Matched literally in the spawn text, so a renamed file drops out of
# the surface automatically instead of being audited as though it were still wired in.
_FILE_RE = re.compile(r"\b((?:docs/|roles/|results/|configs/)?[A-Za-z_][\w.\-]*\.(?:md|json|tsv))\b")


def norm(text: str) -> str:
    """Lowercase and collapse ALL whitespace.

    Line wraps break substring matches, and every prompt file here is hard-wrapped - without
    this an audit reports a rule missing because the renderer put a newline in the middle of
    it. Ported verbatim from the Co-scientist's `_norm`, which learned this the same way.
    """
    return " ".join(text.lower().split())


def find_campaign(start: Path) -> Path:
    """Nearest ancestor that looks like a scaffolded campaign."""
    p = start.resolve()
    for cand in (p, *p.parents):
        if (cand / "scripts" / "run_campaign.py").is_file() and (cand / "results").is_dir():
            return cand
    raise SystemExit(
        f"no campaign tree at or above {start} (needs scripts/run_campaign.py + results/). "
        "Point the audit at a scaffolded campaign, not at the kit source.")


def discover_roles(campaign: Path) -> tuple[list[str], str]:
    """Which roles this driver can actually spawn, read from the driver itself.

    Primary: the `choices=(...)` on the driver's own `--show-prompt` argument. That is the one
    list the driver cannot disagree with, and it picks up a role added by a version nobody here
    anticipated.

    Fallback: probe `KNOWN_ROLES` and keep those the driver accepts. This is REPORTED as a
    fallback, because it can only find roles already named above - exactly the blind spot that
    motivated discovery in the first place.
    """
    src = (campaign / "scripts" / "run_campaign.py").read_text(encoding="utf-8")
    m = _SHOW_PROMPT_CHOICES.search(src)
    if m:
        roles = [r.strip().strip("\"'") for r in m.group(1).split(",") if r.strip().strip("\"'")]
        if roles:
            return roles, "driver --show-prompt choices"
    found = []
    for r in KNOWN_ROLES:
        probe = subprocess.run([sys.executable, str(campaign / "scripts" / "run_campaign.py"),
                                "--show-prompt", r], cwd=str(campaign),
                               capture_output=True, text=True, timeout=120)
        if probe.returncode == 0 and probe.stdout.strip():
            found.append(r)
    if not found:
        raise SystemExit(
            "could not discover any spawnable role from "
            f"{campaign / 'scripts' / 'run_campaign.py'}. Auditing zero roles would report a "
            "clean surface while checking nothing, so this is a hard failure.")
    return found, "PROBED (driver choices not parseable - a role outside KNOWN_ROLES would be MISSED)"


def render_spawn(campaign: Path, role: str) -> str:
    """The literal spawn string, from the campaign's OWN driver.

    Running the driver rather than re-implementing the assembly is the point: an audit that
    rebuilt the prompt itself would be auditing its own copy, and would keep passing after the
    real prompt changed.
    """
    r = subprocess.run([sys.executable, str(campaign / "scripts" / "run_campaign.py"),
                        "--show-prompt", role],
                       cwd=str(campaign), capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise SystemExit(f"--show-prompt {role} failed (exit {r.returncode}):\n{r.stderr[-800:]}")
    return r.stdout


def named_files(campaign: Path, spawn_text: str, role: str) -> list[Path]:
    """Files the spawn string names, resolved inside the campaign, in mention order."""
    out: list[Path] = []
    for m in _FILE_RE.finditer(spawn_text):
        rel = m.group(1)
        cand = campaign / rel
        if not cand.is_file() and "/" not in rel:
            hits = [p for p in campaign.rglob(rel) if p.is_file()]
            cand = hits[0] if hits else cand
        if cand.is_file() and cand not in out:
            out.append(cand)
    # Fallback for a role whose file the prose names in a form the regex misses. NOT every role
    # has one - v0.10's verifier is spawn-only by design - so absence is legitimate here and is
    # reported as a thinner surface rather than treated as an error.
    rf = campaign / "roles" / f"{role}.md"
    if rf.is_file() and rf not in out:
        out.append(rf)
    return out


def surface(campaign: Path, role: str) -> dict[str, list[tuple[str, str]]]:
    """{tier: [(source_name, text), ...]} for one role."""
    spawn = render_spawn(campaign, role)
    tiers: dict[str, list[tuple[str, str]]] = {"spawn": [(f"{role} spawn string", spawn)],
                                               "auto": [], "named": []}
    cm = campaign / "CLAUDE.md"
    if cm.is_file():
        tiers["auto"].append(("CLAUDE.md", cm.read_text(encoding="utf-8")))
    for p in named_files(campaign, spawn, role):
        # CLAUDE.md is already the `auto` tier - counting it again as `named` would let a rule
        # that lives only there be reported at the WEAKER tier, which is backwards.
        if p.name == "CLAUDE.md":
            continue
        tiers["named"].append((str(p.relative_to(campaign)).replace("\\", "/"),
                               p.read_text(encoding="utf-8")))
    return tiers


def all_surfaces(campaign: Path) -> dict[str, dict[str, list[tuple[str, str]]]]:
    roles, _ = discover_roles(campaign)
    return {role: surface(campaign, role) for role in roles}


def flatten(tiers: dict[str, list[tuple[str, str]]]) -> list[tuple[str, str, str]]:
    """[(tier, source, text)] in strength order."""
    return [(tier, src, txt) for tier in ("spawn", "auto", "named")
            for src, txt in tiers.get(tier, [])]
