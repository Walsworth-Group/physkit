"""Check or explicitly reconcile PhysKit's Claude/Codex instruction twins."""
from __future__ import annotations

import argparse
import difflib
import hashlib
import os
import stat
import tempfile
from pathlib import Path


MARKER = "<!-- physkit-dual-instructions:v1 -->"
NAMES = {"claude": "CLAUDE.md", "agents": "AGENTS.md"}
OVERRIDE = "AGENTS.override.md"


class InstructionError(RuntimeError):
    """The managed instruction pair is unsafe or inconsistent."""


def _matches(root: Path, name: str) -> list[Path]:
    try:
        return [entry for entry in root.iterdir() if entry.name.casefold() == name.casefold()]
    except OSError as exc:
        raise InstructionError(f"cannot inspect instruction root {root}: {exc}") from exc


def _is_regular(path: Path) -> bool:
    try:
        return not path.is_symlink() and stat.S_ISREG(path.lstat().st_mode)
    except OSError:
        return False


def _normalized(path: Path) -> str:
    try:
        text = path.read_bytes().decode("utf-8-sig")
    except (OSError, UnicodeError) as exc:
        raise InstructionError(f"cannot read {path} as UTF-8: {exc}") from exc
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _has_marker(text: str) -> bool:
    lines = text.splitlines()
    return (bool(lines) and lines[0] == MARKER and text.count(MARKER) == 1
            and any(line.strip() for line in lines[1:]))


def _marked_candidates(root: Path) -> bool:
    for name in NAMES.values():
        for path in _matches(root, name):
            if _is_regular(path):
                try:
                    if MARKER in _normalized(path):
                        return True
                except InstructionError:
                    pass
    return False


def _managed_runner(root: Path) -> bool:
    runner = root / "scripts" / "run_campaign.py"
    return (_is_regular(runner)
            and "import sync_agent_instructions as _agent_instructions" in _normalized(runner))


def _repair_hint(root: Path) -> str:
    scope = "campaign" if root.parent.name == "campaigns" else "project"
    return ("stop the supervisor, choose the authoritative file, then run "
            f"`python scripts/sync_agent_instructions.py --scope {scope} "
            "--from claude --write` (or `--from agents --write`)")


def _first_difference(left: str, right: str) -> int:
    a, b = left.splitlines(keepends=True), right.splitlines(keepends=True)
    for index in range(max(len(a), len(b))):
        if index >= len(a) or index >= len(b) or a[index] != b[index]:
            return index + 1
    return 0


def check_pair(root: Path, *, required: bool = False) -> str | None:
    """Return the normalized pair hash, or None for an unmarked legacy root."""
    root = Path(root)
    managed = required or _marked_candidates(root)
    if not managed:
        return None

    problems: list[str] = []
    override = _matches(root, OVERRIDE)
    if override:
        problems.append(f"{OVERRIDE} would override AGENTS.md")

    paths: dict[str, Path] = {}
    for name in NAMES.values():
        matches = _matches(root, name)
        if len(matches) != 1:
            problems.append(f"expected one exact-case {name}, found {len(matches)}")
        elif matches[0].name != name:
            problems.append(f"wrong-case instruction file {matches[0].name!r}; expected {name!r}")
        elif not _is_regular(matches[0]):
            problems.append(f"{name} must be a regular file, not a link or directory")
        else:
            paths[name] = matches[0]
    if problems:
        raise InstructionError(f"instruction pair at {root} is unsafe: {'; '.join(problems)}; "
                               + _repair_hint(root))

    claude = _normalized(paths["CLAUDE.md"])
    agents = _normalized(paths["AGENTS.md"])
    if not _has_marker(claude) or not _has_marker(agents):
        raise InstructionError(f"managed marker must appear exactly once on line 1 with content at {root}; "
                               + _repair_hint(root))
    if claude != agents:
        left = hashlib.sha256(claude.encode()).hexdigest()[:12]
        right = hashlib.sha256(agents.encode()).hexdigest()[:12]
        line = _first_difference(claude, agents)
        raise InstructionError(
            f"instruction drift at {root}: CLAUDE.md sha256={left}, AGENTS.md sha256={right}, "
            f"first differing line={line}; {_repair_hint(root)}"
        )
    return hashlib.sha256(claude.encode()).hexdigest()


def check_chain(campaign_root: Path) -> str | None:
    """Check campaign and project pairs; return a fingerprint only when both are managed."""
    campaign = Path(campaign_root).resolve()
    if campaign.parent.name != "campaigns":
        raise InstructionError(f"expected <project>/campaigns/<campaign>, got {campaign}")
    project = campaign.parent.parent
    managed = _managed_runner(campaign)
    project_hash = check_pair(project, required=managed)
    campaign_hash = check_pair(campaign, required=managed)
    if project_hash is None or campaign_hash is None:
        return None
    joined = f"{project_hash}\0{campaign_hash}".encode()
    return hashlib.sha256(joined).hexdigest()


def _exact_regular(root: Path, name: str, *, may_be_missing: bool = False) -> Path | None:
    matches = _matches(root, name)
    if not matches and may_be_missing:
        return None
    if len(matches) != 1 or matches[0].name != name or not _is_regular(matches[0]):
        raise InstructionError(f"{root / name} must be one exact-case regular file")
    return matches[0]


def reconcile(root: Path, source: str, *, write: bool = False) -> None:
    """Copy one explicitly selected marked twin over the other, atomically when requested."""
    root = Path(root).resolve()
    if _matches(root, OVERRIDE):
        raise InstructionError(f"remove {root / OVERRIDE} before reconciling")
    source_name = NAMES[source]
    target_name = NAMES["agents" if source == "claude" else "claude"]
    source_path = _exact_regular(root, source_name)
    target_path = _exact_regular(root, target_name, may_be_missing=True)
    raw = source_path.read_bytes()
    if not _has_marker(_normalized(source_path)):
        raise InstructionError("unmarked legacy instructions require an explicit migration, not reconciliation")
    action = f"{source_name} -> {target_name} at {root}"
    if not write:
        print(f"DRY RUN: would copy {action}")
        target_text = _normalized(target_path) if target_path is not None else ""
        diff = difflib.unified_diff(target_text.splitlines(True), _normalized(source_path).splitlines(True),
                                    fromfile=target_name, tofile=source_name)
        print("".join(diff), end="")
        return
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=root, prefix=f".{target_name}.", suffix=".tmp",
                                         delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, stat.S_IMODE(source_path.stat().st_mode))
        os.replace(temporary, root / target_name)
        temporary = None
    except OSError as exc:
        raise InstructionError(f"could not atomically write {root / target_name}: {exc}") from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    check_pair(root, required=True)
    print(f"WROTE: {action}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--check", action="store_true", help="check project + campaign pairs")
    parser.add_argument("--scope", choices=("project", "campaign"))
    action.add_argument("--from", dest="source", choices=tuple(NAMES))
    parser.add_argument("--write", action="store_true", help="perform the selected reconciliation")
    args = parser.parse_args(argv)
    campaign = Path(__file__).resolve().parent.parent
    if args.source:
        if not args.scope:
            parser.error("--from requires --scope project|campaign")
        root = campaign if args.scope == "campaign" else campaign.parent.parent
        reconcile(root, args.source, write=args.write)
    else:
        if args.write or args.scope:
            parser.error("--write/--scope require --from agents|claude")
        fingerprint = check_chain(campaign)
        print((f"OK: managed instruction chain sha256={fingerprint[:12]}"
               if fingerprint else "LEGACY: incomplete/unmarked chain; Claude behavior is unchanged, "
                                   "but Codex requires migration"))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except InstructionError as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(2)
