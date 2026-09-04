"""upgrade_campaign.py - bring an existing campaign up to the current kit IN PLACE, without re-scaffolding.

Every kit-owned file in a campaign was rendered from a template at the kit commit stamped in
`campaign.md` ("Scaffolded by physkit vX.Y.Z (<hash>, <date>)"). So the upgrade is a THREE-WAY MERGE per
file - base = the template the campaign was rendered from, ours = the campaign's file (with its own
edits: hooks, checks, decisions), theirs = the current template - which keeps every campaign-side edit
and conflicts only where both sides changed the same lines. Files the old kit did not ship are copied.
Placeholders never need re-answering: where a template line still reads `{{X}}` on both sides, the
campaign's rendered value wins by construction.

    python <kit>/skills/new-campaign/scripts/upgrade_campaign.py <campaign_dir> --preset light|moderate|intensive|minimal
        [--base-git <kit repo path>[@<ref>]]       base templates from a kit git checkout (ref defaults to the stamped hash)
        [--base-dir <old kit>/templates/campaign]  base templates from an older plugin version's cache
        [--new-dir <kit>/templates/campaign]       current templates (default: this script's own kit)
        [--reproducible true|false] [--dry-run] [--no-validate]

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

# (campaign-relative path, template-relative path). MERGE: exists in both old and new kits and the
# campaign edits it. COPY: kit-only files an older kit may not have shipped (never campaign-edited).
MERGE = [
    ("scripts/run_campaign.py", "scripts/run_campaign.py.tmpl"),
    ("scripts/guard_promotion.py", "scripts/guard_promotion.py.tmpl"),
    ("scripts/frozen_core.py", "scripts/frozen_core.py.tmpl"),
    ("scripts/loop_heartbeat.py", "scripts/loop_heartbeat.py.tmpl"),
    ("tests/correctness_checks.py", "tests/correctness_checks.py.tmpl"),
    ("CLAUDE.md", "CLAUDE.md.tmpl"),
    ("campaign.md", "campaign.md.tmpl"),
    ("roles/worker.md", "roles/worker.md.tmpl"),
    ("roles/planner.md", "roles/planner.md.tmpl"),
    ("README.md", "README.md.tmpl"),
    (".claude/settings.json", ".claude/settings.json.tmpl"),
]
COPY = [
    ("scripts/codex_backend.py", "scripts/codex_backend.py"),
    ("scripts/codex_verifier.py", "scripts/codex_verifier.py.tmpl"),
    ("scripts/guard_promotion_codex.py", "scripts/guard_promotion_codex.py.tmpl"),
    ("scripts/supervisor_lock.py", "scripts/supervisor_lock.py"),
    ("scripts/sync_agent_instructions.py", "scripts/sync_agent_instructions.py"),
    (".codex/hooks.json", ".codex/hooks.json.tmpl"),
]
PRESETS = ("minimal", "light", "moderate", "intensive")


def stamp_of(campaign: Path) -> tuple[str, str, str] | None:
    try:
        m = STAMP_RE.search((campaign / "campaign.md").read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return None
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
        runner = (campaign / "scripts" / "run_campaign.py").read_text(encoding="utf-8", errors="replace")
        m = re.search(r"run (\S+) in campaign mode", runner)
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
    vals.setdefault("VERIFY_SKILL", "/physkit:verify")
    vals.setdefault("PYTHON_CMD", "python")
    return vals


def render(text: str, vals: dict) -> str:
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


def edit_loop_json(campaign: Path, preset: str, reproducible: bool | None, log: list, dry: bool) -> None:
    p = campaign / "configs" / "loop.json"
    cfg = json.loads(p.read_text(encoding="utf-8-sig"))
    camp = cfg.setdefault("campaign", {})
    verify = cfg.setdefault("verify", {})
    changes = []
    if verify.get("preset") != preset:
        changes.append(f"verify.preset: {verify.get('preset')!r} -> {preset!r}")
        verify["preset"] = preset
    for k in ("verification", "verification_reason"):
        if k in camp:
            changes.append(f"campaign.{k} removed (superseded by verify.preset; was {camp[k]!r})")
            camp.pop(k)
    if reproducible is None:
        reproducible = not (campaign / "configs" / "instrument.json").is_file()
    if not isinstance(camp.get("reproducible"), bool):
        camp["reproducible"] = reproducible
        changes.append(f"campaign.reproducible: {reproducible}")
    drv = cfg.setdefault("driver", {})
    if "verifier_retries" not in drv:
        drv["verifier_retries"] = int(drv.get("planner_retries", 1))
        changes.append(f"driver.verifier_retries: {drv['verifier_retries']}")
    if "full_reproduction_threshold_s" in verify:
        changes.append("verify.full_reproduction_threshold_s kept (honoured as a cap; delete it when the "
                       "computed rule alone is right)")
    if not changes:
        log.append("configs/loop.json: already current")
        return
    log.append("configs/loop.json: " + "; ".join(changes))
    if not dry:
        backup(p)
        p.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")


def edit_recommended(campaign: Path, log: list, dry: bool) -> None:
    p = campaign / "configs" / "RECOMMENDED.json"
    if not p.is_file():
        return
    try:
        rec = json.loads(p.read_text(encoding="utf-8-sig"))
        cfg = json.loads((campaign / "configs" / "loop.json").read_text(encoding="utf-8-sig"))
    except Exception as exc:
        log.append(f"configs/RECOMMENDED.json: not edited ({exc})")
        return
    mv = str((cfg.get("campaign") or {}).get("metric_version") or "")
    if isinstance(rec, dict) and "_metric_version" not in rec and mv:
        rec["_metric_version"] = mv
        log.append(f"configs/RECOMMENDED.json: _metric_version {mv!r} added (the metric epoch the current-best was promoted under)")
        if not dry:
            backup(p)
            p.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")


_UTC = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def backup(p: Path) -> None:
    shutil.copy2(p, p.with_name(p.name + f".pre_upgrade_{_UTC}"))


DUAL_MARKER = "<!-- physkit-dual-instructions:v1 -->"   # sync_agent_instructions.MARKER


def materialize_project_pair(project: Path, log: list, dry: bool) -> None:
    """A project root with exactly one ordinary, unmarked CLAUDE.md and no AGENTS.md (any case) gets the
    marker prepended and the result byte-copied to AGENTS.md. Anything else is left for the operator."""
    claude = project / "CLAUDE.md"
    names = {p.name.lower() for p in project.iterdir()} if project.is_dir() else set()
    if not claude.is_file() or claude.is_symlink() or "agents.md" in names or "agents.override.md" in names:
        return
    raw = claude.read_bytes()
    if DUAL_MARKER.encode() in raw:
        return
    log.append(f"- project {project.name}/CLAUDE.md: unmarked, no AGENTS.md - marker prepended and byte-copied to "
               f"AGENTS.md (the twin the current runner requires)")
    if not dry:
        backup(claude)
        claude.write_bytes(DUAL_MARKER.encode() + b"\n" + raw)
        shutil.copyfile(claude, project / "AGENTS.md")


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
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("campaign", type=Path)
    ap.add_argument("--preset", required=True, choices=PRESETS,
                    help="the verification preset for this campaign (an explicit choice, like the interview's; "
                         "'intensive' keeps the previous per-block spend)")
    ap.add_argument("--base-git", help="<kit repo>[@<ref>]; ref defaults to the hash stamped in campaign.md")
    ap.add_argument("--base-dir", type=Path, help="an older kit's templates/campaign directory (e.g. the previous plugin version's cache)")
    ap.add_argument("--new-dir", type=Path, default=KIT / "templates" / "campaign")
    ap.add_argument("--reproducible", choices=("true", "false"))
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
    if not args.base_git and not args.base_dir:
        sys.exit(f"stamped at physkit {st[0]} ({st[1]}): pass --base-git <kit repo path> (the ref defaults to {st[1]}) "
                 "or --base-dir <that version's templates/campaign>")
    base = Base(args.base_git, st[1] if st else None, args.base_dir.resolve() if args.base_dir else None)
    new_dir = args.new_dir.resolve()
    if not (new_dir / "scripts" / "run_campaign.py.tmpl").is_file():
        sys.exit(f"--new-dir {new_dir} holds no campaign templates")
    version, commit = kit_version(new_dir.parents[1]), kit_commit(new_dir.parents[1])
    vals = recover_values(campaign)
    log = [f"# Upgrade of {campaign.name}", "",
           f"- from: {st[0] if st else '?'} ({st[1] if st else '?'}, {st[2] if st else '?'}) base = {base.describe()}",
           f"- to: physkit {version} ({commit}) templates = {new_dir}",
           f"- preset: {args.preset}; recovered placeholders: {vals}", f"- utc: {_UTC}", ""]
    conflicts = []
    print(f"upgrade: {campaign}\n  base {base.describe()} -> physkit {version} ({commit})" + ("  [dry run]" if args.dry_run else ""))

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
            log.append(f"- {rel}: copied (the scaffold's kit did not ship it)")
            if not args.dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text(render(src.read_text(encoding="utf-8"), vals), encoding="utf-8", newline="\n")
    edit_loop_json(campaign, args.preset, None if args.reproducible is None else args.reproducible == "true", log, args.dry_run)
    edit_recommended(campaign, log, args.dry_run)
    stamp(campaign, version, commit, log, args.dry_run)

    # The instruction twins (CLAUDE.md <-> AGENTS.md) the current runner requires at both roots. A
    # project scaffolded before the twins has one unmarked CLAUDE.md and no AGENTS.md: the documented
    # migration (new-campaign, project membership) is to prepend the inert marker and byte-copy it.
    materialize_project_pair(campaign.parent.parent, log, args.dry_run)
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
            "1. Resolve any file marked CONFLICTS (the markers name the three sides: campaign, scaffold-template, current-template).",
            "2. Declare rows in tests/correctness_checks.py: @check(row='machinery') on analytic-limit / parity / convergence "
            "checks, row='gates' on per-result gates (they then take the experiment as their argument); undeclared checks "
            "stay 'invariants' and run every unit inside the budget. Fill the four contract checks or record tests/CORRECTNESS_NA.md.",
            "3. python <kit>/skills/new-campaign/scripts/validate_campaign.py <campaign>, then, with the campaign's own "
            "interpreter (the one .claude/settings.json names), scripts/run_campaign.py --preflight. Preflight runs the whole "
            "suite once, timed: an every-set over budget is refused by name - declare the named checks machinery or gates.",
            "4. Read the new HARD GATE 1 in CLAUDE.md and the presets doc: promotions now follow the label, not the verdict alone."]
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
