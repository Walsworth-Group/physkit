"""upgrade_campaign.py - bring an existing campaign up to the current kit IN PLACE, without re-scaffolding.

Every kit-owned file in a campaign was rendered from a template at the kit commit stamped in
`campaign.md` ("Scaffolded by physkit vX.Y.Z (<hash>, <date>)"). So the upgrade is a THREE-WAY MERGE per
file - base = the template the campaign was rendered from, ours = the campaign's file (with its own
edits: hooks, checks, decisions), theirs = the current template - which keeps every campaign-side edit
and conflicts only where both sides changed the same lines. A kit-only file the campaign lacks is
created. Placeholders never need re-answering: where a template line still reads `{{X}}` on both sides,
the campaign's rendered value wins by construction.

Supported sources: campaigns scaffolded by (or last upgraded to) physkit v0.12.1 or newer. A campaign
from an older kit keeps running on the kit version stamped in it.

    python <kit>/skills/new-campaign/scripts/upgrade_campaign.py <campaign_dir>
        [--preset none|minimal|light|heavy|intensive]  default: keep the campaign's verify.preset
        [--base-git <kit repo path>[@<ref>]]       base templates from a kit git checkout (ref defaults to the stamped hash)
        [--base-dir <kit>/templates/campaign]      base templates from the stamped plugin version's cache
        [--new-dir <kit>/templates/campaign]       current templates (default: this script's own kit)
        [--dry-run] [--no-validate]

Writes a backup `<file>.pre_upgrade_<UTC>` beside every file it changes, an upgrade log under
results/diagnostics/, and a provenance line in campaign.md and results/logbook.md. Exits 2 when merges
left conflict markers (resolve them, then run the validator and `--preflight`). Requires `git` for the
merge itself. Never touches the FROZEN scorer (scripts/metric.py), data, results, or configs/exp*.json.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
KIT = HERE.parents[3]                                   # <kit>/skills/new-campaign/scripts/ -> <kit>
STAMP_RE = re.compile(r"Scaffolded by physkit (v[\w.\-]+) \(([0-9a-f]{6,40}), ([0-9-]{10})\)")
# The line stamp() writes (the version's leading "v" is optional).
UPGRADE_STAMP_RE = re.compile(r"Upgraded in place to physkit (v?[\w.\-]+) \(([0-9a-f]{6,40}), ([0-9-]{10})\)")

# (campaign-relative path, template-relative path). MERGE: kit files the campaign edits. COPY: kit-only
# files (never campaign-edited), replaced with the current version; created when absent.
MERGE = [
    ("scripts/guard_promotion.py", "scripts/guard_promotion.py.tmpl"),
    ("scripts/frozen_core.py", "scripts/frozen_core.py.tmpl"),
    ("scripts/loop_heartbeat.py", "scripts/loop_heartbeat.py.tmpl"),
    ("tests/correctness_checks.py", "tests/correctness_checks.py.tmpl"),
    ("CLAUDE.md", "CLAUDE.md.tmpl"),
    ("campaign.md", "campaign.md.tmpl"),
    ("roles/worker.md", "roles/worker.md.tmpl"),
    ("README.md", "README.md.tmpl"),
    (".claude/settings.json", ".claude/settings.json.tmpl"),
]
COPY = [
    # The runner is the kit's machinery: replaced wholesale (a campaign edit is merged three-way below,
    # with the backup to port from). The campaign's own code lives in scripts/experiment.py.
    ("scripts/run_campaign.py", "scripts/run_campaign.py.tmpl"),
    ("scripts/codex_backend.py", "scripts/codex_backend.py"),
    ("scripts/codex_verifier.py", "scripts/codex_verifier.py.tmpl"),
    ("scripts/guard_promotion_codex.py", "scripts/guard_promotion_codex.py.tmpl"),
    ("scripts/supervisor_lock.py", "scripts/supervisor_lock.py"),
    ("scripts/sync_agent_instructions.py", "scripts/sync_agent_instructions.py"),
    (".codex/hooks.json", ".codex/hooks.json.tmpl"),
]
# CREATE: the campaign's own code. Created from the template when absent; NEVER touched when present
# (its base is the stub, so a three-way merge would conflict every implementation against
# `raise NotImplementedError`).
CREATE = [
    ("scripts/experiment.py", "scripts/experiment.py.tmpl"),
    # The verifier's and the capstone's roles, and the reference the worker's contract points at.
    # Rendered with the values the upgrade recovers; a placeholder it cannot recover is left literal and
    # named in the log.
    ("roles/verifier.md", "roles/verifier.md.tmpl"),
    ("roles/capstone.md", "roles/capstone.md.tmpl"),
    ("roles/REFERENCE.md", "roles/REFERENCE.md.tmpl"),
]
PRESETS = ("none", "minimal", "light", "heavy", "intensive")
OLDEST_SOURCE = (0, 12, 1)       # the oldest kit version this script upgrades from


def _version_tuple(v: str) -> tuple | None:
    m = re.match(r"v?(\d+)\.(\d+)\.(\d+)", v or "")
    return tuple(int(x) for x in m.groups()) if m else None


def stamp_of(campaign: Path) -> tuple[str, str, str] | None:
    """The kit the campaign's kit-owned files were LAST rendered/merged from: the newest 'Upgraded in
    place' line this script wrote (it says it supersedes the scaffold pin), else the scaffold pin. A
    second upgrade that merged against the scaffold's templates instead treated every change the first
    upgrade brought in as a campaign edit, flagging several times the real number of conflicts."""
    try:
        text = (campaign / "campaign.md").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    upgrades = UPGRADE_STAMP_RE.findall(text)
    if upgrades:
        v, commit, date = upgrades[-1]
        return ("v" + v.lstrip("v"), commit, date)
    m = STAMP_RE.search(text)
    return (m.group(1), m.group(2), m.group(3)) if m else None


def kit_version(kit: Path) -> str:
    try:
        return str(json.loads((kit / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")).get("version") or "?")
    except Exception:
        return "?"


def kit_commit(kit: Path) -> str:
    try:
        r = subprocess.run(["git", "-C", str(kit), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else "unknown"
    except OSError:
        return "unknown"


class Base:
    """Where the campaign's ORIGINAL templates come from: a git ref in a kit checkout, or a directory."""

    def __init__(self, git: str | None, ref: str | None, directory: Path | None):
        self.repo, self.ref, self.dir = None, ref, directory
        if git:
            repo, _, r = git.partition("@")
            self.repo = Path(repo).resolve()
            self.ref = r or ref

    def read(self, tmpl_rel: str) -> str | None:
        if self.dir is not None:
            p = self.dir / tmpl_rel
            return p.read_text(encoding="utf-8") if p.is_file() else None
        r = subprocess.run(["git", "-C", str(self.repo), "show", f"{self.ref}:kit/templates/campaign/{tmpl_rel}"],
                           capture_output=True, text=True, encoding="utf-8")
        return r.stdout if r.returncode == 0 else None

    def describe(self) -> str:
        return f"dir {self.dir}" if self.dir is not None else f"{self.repo}@{self.ref}"


def recover_values(campaign: Path) -> dict:
    """The few placeholder values the COPIED kit-only files need, read back from rendered files."""
    vals = {}
    try:
        verifier = (campaign / "roles" / "verifier.md").read_text(encoding="utf-8", errors="replace")
        m = re.search(r"run (\S+) in campaign mode", verifier)
        if m:
            vals["VERIFY_SKILL"] = m.group(1)
    except OSError:
        pass
    try:
        hooks = json.loads((campaign / ".claude" / "settings.json").read_text(encoding="utf-8"))
        text = json.dumps(hooks)
        m = re.search(r'"command": "([^"]*?)\s+\S*guard_promotion\.py', text)
        if m:
            vals["PYTHON_CMD"] = m.group(1)
    except Exception:
        pass
    # The metric names and the title: a current-template line the campaign never had (e.g. a new f-string
    # naming {{PRIMARY_METRIC}}) is rendered with the campaign's values or it ships as a literal
    # placeholder (a card printing "{PRIMARY_METRIC} = None"). Read back from
    # the campaign's own rendered runner and campaign.md.
    try:
        runner = (campaign / "scripts" / "run_campaign.py").read_text(encoding="utf-8", errors="replace")
        m = re.search(r'score = float\(d\["([A-Za-z0-9_]+)"\]\)', runner)     # _prior_results: the result key
        if m:
            vals.setdefault("PRIMARY_METRIC", m.group(1))
        m = re.search(r"; ([A-Za-z0-9_]+) = \{diags\}", runner)                   # the logbook's Result line
        if m:
            vals.setdefault("GUARDRAIL_METRIC", m.group(1))
        m = re.search(r'description="Experiment runner for (.+?)"\)', runner)
        if m:
            vals.setdefault("CAMPAIGN_TITLE", m.group(1))
    except OSError:
        pass
    try:
        camp_md = (campaign / "campaign.md").read_text(encoding="utf-8", errors="replace")
        m = re.search(r"PRIMARY = `([A-Za-z0-9_]+)`", camp_md)
        if m:
            vals.setdefault("PRIMARY_METRIC_COL", m.group(1))
            vals.setdefault("PRIMARY_METRIC", m.group(1))
    except OSError:
        pass
    vals.setdefault("VERIFY_SKILL", "/physkit:verify")
    vals.setdefault("PYTHON_CMD", "python")
    return vals


# A template's [[KEEP — ...]] tag lines tell a setup agent what code reads; they are deleted at scaffold time,
# so a campaign never carries them and an upgrade must not merge them in (the validator refuses a leftover).
KEEP_LINE = re.compile(r"(?m)^(?:# )?\[\[KEEP[^\n]*\]\]\r?\n")


def render(text: str, vals: dict) -> str:
    text = KEEP_LINE.sub("", text)
    return re.sub(r"\{\{([A-Z0-9_]+)\}\}", lambda m: vals.get(m.group(1), m.group(0)), text)


def merge3(ours: str, base: str, theirs: str, label: str) -> tuple[str, bool]:
    """git merge-file: returns (merged text, had_conflicts)."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        po, pb, pt = d / "ours", d / "base", d / "theirs"
        for p, s in ((po, ours), (pb, base), (pt, theirs)):
            p.write_text(s, encoding="utf-8", newline="\n")
        r = subprocess.run(["git", "merge-file", "-p", "--diff3", "-L", f"campaign:{label}", "-L", "scaffold-template",
                            "-L", "current-template", str(po), str(pb), str(pt)],
                           capture_output=True, text=True, encoding="utf-8")
        # exit code = number of conflicts (0 clean), <0 on error
        if r.returncode < 0 or (r.returncode > 0 and "<<<<<<<" not in r.stdout):
            raise RuntimeError(f"git merge-file failed for {label}: {r.stderr.strip()}")
        return r.stdout, r.returncode > 0


_PH = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def _line_pattern(base_line: str):
    """A regex that matches the RENDERED form of one template line, capturing each placeholder's value.
    Returns (pattern, placeholder names) or None when the line has no placeholder."""
    if not _PH.search(base_line):
        return None
    parts, pos, names = [], 0, []
    for m in _PH.finditer(base_line):
        parts.append(re.escape(base_line[pos:m.start()]))
        parts.append("(.*?)")
        names.append(m.group(1))
        pos = m.end()
    parts.append(re.escape(base_line[pos:]))
    return re.compile("^" + "".join(parts) + "$", re.S), names


def auto_resolve(merged: str, vals: dict) -> tuple[str, int, dict]:
    """Resolve the conflicts that are only placeholders: the campaign's side of a hunk is the scaffold
    template's side with `{{X}}` rendered, and the current template changed that line. Recover each value
    from the campaign side, render the current template's side with it, and take that. A hunk where the
    campaign genuinely edited the text (its side is not a rendering of the base side) is left for a
    person, markers intact. Returns (text, conflicts_left, values_learned)."""
    lines = merged.split("\n")
    out, i, left, learned = [], 0, 0, dict(vals)
    while i < len(lines):
        if not lines[i].startswith("<<<<<<<"):
            out.append(lines[i])
            i += 1
            continue
        j = i + 1
        while j < len(lines) and not lines[j].startswith("|||||||"):
            j += 1
        k = j + 1
        while k < len(lines) and not lines[k].startswith("======="):
            k += 1
        m = k + 1
        while m < len(lines) and not lines[m].startswith(">>>>>>>"):
            m += 1
        if m >= len(lines):                       # malformed: keep as is
            out.extend(lines[i:])
            break
        ours, base, theirs = lines[i + 1:j], lines[j + 1:k], lines[k + 1:m]
        resolved = None
        if len(ours) == len(base) and base:
            hv = dict(learned)
            ok = True
            for b, o in zip(base, ours):
                lp = _line_pattern(b)
                if lp is None:
                    if b != o:
                        ok = False
                        break
                    continue
                pat, names = lp
                mm = pat.match(o)
                if not mm:
                    ok = False
                    break
                for name, val in zip(names, mm.groups()):
                    if name in hv and hv[name] != val:
                        ok = False
                        break
                    hv[name] = val
                if not ok:
                    break
            if ok:
                rendered = [render(t, hv) for t in theirs]
                if not any(_PH.search(t) for t in rendered):
                    resolved = rendered
                    learned = hv
        if resolved is not None:
            out.extend(resolved)
        else:
            out.extend(lines[i:m + 1])
            left += 1
        i = m + 1
    return "\n".join(out), left, learned


def edit_loop_json(campaign: Path, preset: str | None, log: list, dry: bool) -> None:
    """Set verify.preset when --preset names one; without it (None) the campaign's preset is kept. Every
    other key in configs/loop.json is the campaign's."""
    p = campaign / "configs" / "loop.json"
    cfg = json.loads(p.read_text(encoding="utf-8-sig"))
    verify = cfg.setdefault("verify", {})
    if preset is None or verify.get("preset") == preset:
        log.append(f"configs/loop.json: verify.preset {verify.get('preset')!r} kept")
        return
    log.append(f"configs/loop.json: verify.preset {verify.get('preset')!r} -> {preset!r}")
    verify["preset"] = preset
    if not dry:
        backup(p)
        p.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")


_UTC = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def backup(p: Path) -> None:
    shutil.copy2(p, p.with_name(p.name + f".pre_upgrade_{_UTC}"))


def stamp(campaign: Path, version: str, commit: str, log: list, dry: bool) -> None:
    line = (f"> **Upgraded in place to physkit {version} ({commit}, {_dt.date.today().isoformat()})** - kit-owned files "
            f"merged three-way against the scaffold's own templates; campaign edits kept; the upgrade log is "
            f"`results/diagnostics/upgrade_{_UTC}.md`. This line supersedes the scaffold pin above for tooling and doctrine.")
    for rel in ("campaign.md", "results/logbook.md"):
        p = campaign / rel
        if not p.is_file():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        if "Upgraded in place to physkit" in text and version in text:
            continue
        m = STAMP_RE.search(text)
        if m:
            end = text.index("\n", m.end()) + 1 if "\n" in text[m.end():] else len(text)
            # append after the stamp's own blockquote paragraph
            while end < len(text) and text[end:end + 1] == ">":
                end = text.index("\n", end) + 1 if "\n" in text[end:] else len(text)
            new = text[:end] + line + "\n" + text[end:]
        else:
            new = line + "\n\n" + text
        log.append(f"{rel}: upgrade provenance line added")
        if not dry:
            p.write_text(new, encoding="utf-8")


def main() -> int:
    for stream in (sys.stdout, sys.stderr):      # a cp1252 console must not crash the log on a superscript
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("campaign", type=Path)
    ap.add_argument("--preset", choices=PRESETS,
                    help="set the campaign's verification preset (docs/reference/verification-presets.md); "
                         "default: keep the one configs/loop.json names")
    ap.add_argument("--base-git", help="<kit repo>[@<ref>]; ref defaults to the hash stamped in campaign.md")
    ap.add_argument("--base-dir", type=Path, help="the stamped kit version's templates/campaign directory (e.g. that plugin version's cache)")
    ap.add_argument("--new-dir", type=Path, default=KIT / "templates" / "campaign")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-validate", action="store_true")
    args = ap.parse_args()

    campaign = args.campaign.resolve()
    if not (campaign / "campaign.md").is_file() or not (campaign / "scripts" / "run_campaign.py").is_file():
        sys.exit(f"{campaign} is not a campaign root (no campaign.md / scripts/run_campaign.py)")
    st = stamp_of(campaign)
    if st is None and not (args.base_git or args.base_dir):
        sys.exit("campaign.md carries no 'Scaffolded by physkit vX (hash, date)' stamp - pass --base-git <repo>@<ref> "
                 "or --base-dir explicitly")
    if st is not None and (_version_tuple(st[0]) is None or _version_tuple(st[0]) < OLDEST_SOURCE):
        sys.exit(f"stamped at physkit {st[0]}: this script upgrades campaigns from v0.12.1 or newer. Keep running "
                 f"this campaign on the kit version stamped in it ({st[0]}), or scaffold a new campaign.")
    if not args.base_git and not args.base_dir:
        sys.exit(f"stamped at physkit {st[0]} ({st[1]}): pass --base-git <kit repo path> (the ref defaults to {st[1]}) "
                 "or --base-dir <that version's templates/campaign>")
    base = Base(args.base_git, st[1] if st else None, args.base_dir.resolve() if args.base_dir else None)
    new_dir = args.new_dir.resolve()
    if not (new_dir / "scripts" / "run_campaign.py.tmpl").is_file():
        sys.exit(f"--new-dir {new_dir} holds no campaign templates")
    version, commit = kit_version(new_dir.parents[1]), kit_commit(new_dir.parents[1])
    vals = recover_values(campaign)
    # The copied runner stamps its own kit version into every snapshot manifest (kit_version:), the
    # machinery's provenance (the runner is outside the frozen-core hash). Same form as campaign.md's pin.
    vals["PHYSKIT_VERSION"] = f"v{version.lstrip('v')} ({commit}, {_UTC[:4]}-{_UTC[4:6]}-{_UTC[6:8]})"
    log = [f"# Upgrade of {campaign.name}", "",
           f"- from: {st[0] if st else '?'} ({st[1] if st else '?'}, {st[2] if st else '?'}) base = {base.describe()}",
           f"- to: physkit {version} ({commit}) templates = {new_dir}",
           f"- preset: {args.preset or '(kept)'}; recovered placeholders: {vals}", f"- utc: {_UTC}", ""]
    conflicts = []
    print(f"upgrade: {campaign}\n  base {base.describe()} -> physkit {version} ({commit})" + ("  [dry run]" if args.dry_run else ""))

    for rel, tmpl in CREATE:
        dst, srcp = campaign / rel, new_dir / tmpl
        if dst.is_file() or not srcp.is_file():
            continue
        rendered = render(srcp.read_text(encoding="utf-8"), vals)
        left = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", rendered)))
        log.append(f"- {rel}: created from the template (it was absent)"
                   + (f"; fill by hand: {', '.join(left)}" if left else ""))
        if not args.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(rendered, encoding="utf-8", newline="\n")

    for rel, tmpl in MERGE:
        ours_p = campaign / rel
        theirs = (new_dir / tmpl).read_text(encoding="utf-8") if (new_dir / tmpl).is_file() else None
        if theirs is None:
            continue
        if not ours_p.is_file():
            log.append(f"- {rel}: absent in the campaign; NOT created (merge-class file - scaffold it by hand if needed)")
            continue
        base_t = base.read(tmpl)
        if base_t is None:
            log.append(f"- {rel}: no base template at {base.describe()}; skipped (pass --base-dir/--base-git for the "
                       f"version this campaign was scaffolded from)")
            continue
        ours = ours_p.read_text(encoding="utf-8", errors="replace")
        if ours == render(base_t, vals) or ours == base_t:
            merged, conflict = render(theirs, vals), False   # never edited by the campaign: take the new one
        else:
            merged, conflict = merge3(ours, base_t, theirs, rel)
            auto = 0
            if conflict:
                before = merged.count("<<<<<<<")
                merged, n_left, vals = auto_resolve(merged, vals)
                auto, conflict = before - n_left, n_left > 0
            merged = render(merged, vals)                    # placeholders the current template added
            if auto:
                log.append(f"  ({rel}: {auto} placeholder-only conflict(s) resolved by re-rendering the current "
                           f"template line with the campaign's own values)")
        if merged == ours:
            log.append(f"- {rel}: unchanged")
            continue
        n = merged.count("<<<<<<<")
        log.append(f"- {rel}: {'CONFLICTS ' + str(n) if conflict else 'merged clean'}")
        if conflict:
            conflicts.append((rel, n))
        if not args.dry_run:
            backup(ours_p)
            ours_p.write_text(merged, encoding="utf-8", newline="\n")
    for rel, tmpl in COPY:
        dst, src = campaign / rel, new_dir / tmpl
        if not src.is_file():
            continue
        if dst.is_file():
            cur, new = dst.read_text(encoding="utf-8", errors="replace"), render(src.read_text(encoding="utf-8"), vals)
            if cur == new:
                log.append(f"- {rel}: current")
                continue
            base_t = base.read(tmpl)
            if base_t is not None and cur != render(base_t, vals):
                merged, conflict = merge3(cur, base_t, src.read_text(encoding="utf-8"), rel)
                merged = render(merged, vals)
                log.append(f"- {rel}: {'CONFLICTS' if conflict else 'merged clean'} (kit-only file the campaign edited)")
                if conflict:
                    conflicts.append((rel, merged.count("<<<<<<<")))
            else:
                merged = new
                log.append(f"- {rel}: replaced with the current kit file")
            if not args.dry_run:
                backup(dst)
                dst.write_text(merged, encoding="utf-8", newline="\n")
        else:
            log.append(f"- {rel}: created (it was absent)")
            if not args.dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text(render(src.read_text(encoding="utf-8"), vals), encoding="utf-8", newline="\n")
    edit_loop_json(campaign, args.preset, log, args.dry_run)
    stamp(campaign, version, commit, log, args.dry_run)

    # The instruction twins (CLAUDE.md <-> AGENTS.md) at both roots: re-derive AGENTS.md from the merged
    # CLAUDE.md.
    sync = campaign / "scripts" / "sync_agent_instructions.py"
    if sync.is_file() and not args.dry_run and not conflicts:
        for scope in ("campaign", "project"):
            r = subprocess.run([sys.executable, str(sync), "--scope", scope, "--from", "claude", "--write"],
                               cwd=str(campaign), capture_output=True, text=True)
            log.append(f"- sync_agent_instructions --scope {scope}: exit {r.returncode} {(r.stdout or r.stderr).strip()[:160]}")
    elif conflicts:
        log.append("- sync_agent_instructions: skipped until the conflicts above are resolved (run it yourself: "
                   "python scripts/sync_agent_instructions.py --scope campaign --from claude --write, then --scope project)")

    log += ["", "## Next",
            "1. Resolve any file marked CONFLICTS (the markers name the three sides: campaign, scaffold-template, "
            "current-template), then run the instruction sync named above if it was skipped.",
            "2. Read the CHANGELOG entries between the two kit versions for anything that asks a campaign-side "
            "change (a new contract check, a new seam in scripts/experiment.py).",
            "3. python <kit>/skills/new-campaign/scripts/validate_campaign.py <campaign>, then, with the campaign's own "
            "interpreter (the one .claude/settings.json names), scripts/run_campaign.py --preflight."]
    text = "\n".join(log) + "\n"
    if not args.dry_run:
        (campaign / "results" / "diagnostics").mkdir(parents=True, exist_ok=True)
        (campaign / "results" / "diagnostics" / f"upgrade_{_UTC}.md").write_text(text, encoding="utf-8")
    print(text)
    if conflicts:
        print(f"upgrade: {len(conflicts)} file(s) with conflicts - resolve, then validate and preflight.")
        return 2
    if not args.dry_run and not args.no_validate:
        r = subprocess.run([sys.executable, str(HERE.parent / "validate_campaign.py"), str(campaign)],
                           capture_output=True, text=True)
        print(r.stdout[-2000:] + r.stderr[-800:])
        print(f"upgrade: validator exit {r.returncode} - next: python scripts/run_campaign.py --preflight")
        return 0 if r.returncode == 0 else 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
