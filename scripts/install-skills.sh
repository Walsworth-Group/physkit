#!/usr/bin/env bash
#
# Install PhysKit skills into a vendor-neutral location shared by Codex, OpenCode, and Gemini CLI.
#
# PhysKit's skills are written to the open Agent Skills standard (SKILL.md). This script projects
# every skill from this kit's canonical ../skills/ directory into ~/.agents/skills/ (the user-scope
# location Codex, OpenCode, and Gemini CLI all scan), so those harnesses auto-discover them the same
# way Claude Code does through its plugin.
#
# This script does NOT touch Claude Code. Install PhysKit on Claude Code the usual way:
#     claude plugin marketplace add <path-to-kit>
#     claude plugin install physkit@physkit
#
# The kit's ../skills/ directory stays the single source of truth; this only copies (or links) it
# outward. Re-run after updating the kit to refresh the installed copy.
#
# Usage:
#   ./install-skills.sh                       # copy skills into ~/.agents/skills
#   ./install-skills.sh --target DIR          # install into a different skills directory
#   ./install-skills.sh --link                # symlink instead of copy (live-linked, never drifts)
#   ./install-skills.sh --uninstall           # remove PhysKit skills from the target

set -euo pipefail

TARGET="${HOME}/.agents/skills"
MODE="copy"
ACTION="install"

usage() {
    echo "Usage: install-skills.sh [--target DIR] [--link] [--uninstall]"
    exit "${1:-1}"
}

while [ $# -gt 0 ]; do
    case "$1" in
        --target) TARGET="$2"; shift 2 ;;
        --link)   MODE="link"; shift ;;
        --uninstall) ACTION="uninstall"; shift ;;
        -h|--help) usage 0 ;;
        *) echo "unknown argument: $1"; usage 1 ;;
    esac
done

SRC="$(cd "$(dirname "$0")/../skills" && pwd)"
count=0

[ "$ACTION" = "install" ] && mkdir -p "$TARGET"

for dir in "$SRC"/*/; do
    [ -f "${dir}SKILL.md" ] || continue
    name="$(basename "$dir")"
    dest="$TARGET/$name"

    if [ "$ACTION" = "uninstall" ]; then
        if [ -e "$dest" ] || [ -L "$dest" ]; then
            rm -rf "$dest"
            echo "removed  $name"
            count=$((count + 1))
        fi
        continue
    fi

    rm -rf "$dest"
    if [ "$MODE" = "link" ]; then
        ln -s "${dir%/}" "$dest"
        echo "linked   $name"
    else
        cp -R "${dir%/}" "$dest"
        echo "copied   $name"
    fi
    count=$((count + 1))
done

echo ""
if [ "$ACTION" = "uninstall" ]; then
    echo "Uninstalled $count PhysKit skills from $TARGET"
else
    echo "Installed $count PhysKit skills at $TARGET"
    echo "Codex, OpenCode, and Gemini CLI will discover them on next launch."
fi
