#!/usr/bin/env python3
"""archive_transcript.py — snapshot THIS session's Claude Code transcript into ./transcripts/.

Run from a campaign folder (e.g. at each campaign-status checkpoint) to preserve the session
transcript(s) with the campaign before Claude Code's retention pruning removes them — the provenance
record for the work, and primary data for any write-up. Derives the transcript location from the current
working directory, copies the `.jsonl` file(s), and writes a MANIFEST. Idempotent (re-run to refresh as
the session grows). Never raises — a failure here must not block a checkpoint.

Usage (from the campaign dir):  python <this script>
"""
from __future__ import annotations
import glob, json, os, re, shutil, sys
from datetime import datetime, timezone


def main():
    try:
        cwd = os.getcwd()
        enc = re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(cwd))
        tdir = os.path.join(os.path.expanduser("~"), ".claude", "projects", enc)
        files = sorted(glob.glob(os.path.join(tdir, "*.jsonl")))
        if not files:
            print(f"archive_transcript: no transcript found at {tdir} (nothing to archive).")
            return 0
        dest = os.path.join(cwd, "transcripts")
        os.makedirs(dest, exist_ok=True)
        copied = []
        for f in files:
            shutil.copy2(f, os.path.join(dest, os.path.basename(f)))
            copied.append((os.path.basename(f), os.path.getsize(f)))
        first = last = None
        n = 0
        for f in files:
            for line in open(f, encoding="utf-8", errors="replace"):
                line = line.strip()
                if not line:
                    continue
                n += 1
                try:
                    raw = json.loads(line).get("timestamp")
                    ts = datetime.fromisoformat(str(raw).replace("Z", "+00:00")) if raw else None
                except Exception:
                    ts = None
                if ts:
                    first = ts if (first is None or ts < first) else first
                    last = ts if (last is None or ts > last) else last
        man = ["# Archived transcript", "",
               f"- Source: `{tdir}`",
               f"- Archived (UTC): {datetime.now(timezone.utc).isoformat()}",
               f"- Sessions: {len(files)} file(s), {n} records",
               f"- Span: {first.isoformat() if first else '?'} -> {last.isoformat() if last else '?'}",
               "", "Files:"]
        man += [f"- `{nm}` ({sz:,} bytes)" for nm, sz in copied]
        man += ["", "Raw Claude Code session transcript (full conversation + tool I/O) — treat as sensitive."]
        with open(os.path.join(dest, "MANIFEST.md"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(man) + "\n")
        print(f"archive_transcript: {len(copied)} file(s) -> {dest}  ({n} records)")
        return 0
    except Exception as e:  # never block a checkpoint
        print(f"archive_transcript: skipped (non-fatal): {e}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
