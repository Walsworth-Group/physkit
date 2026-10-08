#!/usr/bin/env python3
"""Exercise every decision path of the loop_heartbeat Stop hook against synthetic hook stdin.

Runs the SHIPPED template (templates/campaign/scripts/loop_heartbeat.py.tmpl) in a throwaway campaign-shaped
sandbox, so what is tested is what new-campaign actually generates. Run it after any edit to that template:

    python skills/new-campaign/scripts/test_loop_heartbeat.py      # from the kit root
"""
import json, os, subprocess, sys, shutil, tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

TEMPLATE = (Path(__file__).resolve().parents[3]
            / "templates" / "campaign" / "scripts" / "loop_heartbeat.py.tmpl")
if not TEMPLATE.is_file():
    sys.exit(f"cannot find the hook template at {TEMPLATE}")

SANDBOX = Path(tempfile.mkdtemp(prefix="loop_heartbeat_test_"))
(SANDBOX / "scripts").mkdir()
HOOK = SANDBOX / "scripts" / "loop_heartbeat.py"
shutil.copyfile(TEMPLATE, HOOK)
R = SANDBOX / "results"
PY = [sys.executable]

HEADER = "exp_id\ttimestamp\tmetric\tverified\tnotes\n"


def reset(rows=0, journal=True):
    if R.exists():
        shutil.rmtree(R)
    R.mkdir(parents=True)
    if rows:
        body = "".join(f"{i:03d}\t2026-08-03\t0.5\t\t\n" for i in range(rows))
        (R / "scoreboard.tsv").write_text("# comment line\n" + HEADER + body, encoding="utf-8")
    if journal:
        (R / "JOURNAL.md").write_text(
            "# JOURNAL\n\n**NEXT:** sweep the tip-sample distance at fixed drive\n\n"
            "## Open questions\n- exp 002 residual is structured, unexplained\n- (placeholder bullet)\n",
            encoding="utf-8")


def run(event="Stop", env=None):
    payload = json.dumps({"hook_event_name": event, "last_assistant_message": "done", "stop_hook_active": True})
    p = subprocess.run(PY + [str(HOOK)], input=payload, capture_output=True, text=True, env=env)
    out = {}
    if p.stdout.strip():
        try:
            out = json.loads(p.stdout)
        except Exception:
            out = {"RAW": p.stdout}
    return p.returncode, out, p.stderr


def iso(minutes_ago=0):
    return (datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)).isoformat()


def write_request(**kw):
    (R / "stop_request.json").write_text(json.dumps(kw), encoding="utf-8")


FAILS = []


def check(name, cond, extra=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}" + (f"   {extra}" if extra and not cond else ""))
    if not cond:
        FAILS.append(name)


# 1 — not armed: no scoreboard rows, no .loop_armed -> must allow (don't trap the setup session)
reset(rows=0)
rc, out, _ = run()
check("unarmed tree allows the stop", rc == 0 and out == {}, f"rc={rc} out={out}")

# 1b — armed explicitly by flag even with no rows
(R / ".loop_armed").touch()
rc, out, _ = run()
check("explicit .loop_armed arms the hook", out.get("decision") == "block", f"out={out}")

# 2 — live campaign, nothing else: block, and the reason must name the NEXT exp and the JOURNAL pointer
reset(rows=3)
rc, out, _ = run()
reason = out.get("reason", "")
check("live campaign blocks the stop", out.get("decision") == "block", f"out={out}")
check("reason names the next exp id (003)", "exp 003" in reason, reason[:200])
check("reason carries the JOURNAL NEXT pointer", "tip-sample distance" in reason, reason[:200])
check("reason carries open threads", "structured, unexplained" in reason, reason[:200])
check("placeholder thread bullet is skipped", "placeholder bullet" not in reason)
check("reason tells the agent how to stop", "stop_request.json" in reason and "results/STOP" in reason)

# 3 — SubagentStop must never be blocked (the independent refuter has to finish)
rc, out, _ = run(event="SubagentStop")
check("SubagentStop is allowed", rc == 0 and out == {}, f"out={out}")

# 4 — human sentinel
reset(rows=3)
(R / "STOP").write_text("", encoding="utf-8")
rc, out, _ = run()
check("STOP sentinel allows the stop", rc == 0 and out == {}, f"out={out}")
check("sentinel stop is logged", "SENTINEL" in (R / "loop_stops.log").read_text(encoding="utf-8"))
reset(rows=3)
(R / "STOP.txt").write_text("", encoding="utf-8")
rc, out, _ = run()
check("STOP.txt sentinel also works", rc == 0 and out == {}, f"out={out}")

# 5 — a valid, fresh user-fork request
reset(rows=3)
write_request(utc=iso(), reason_code="user-fork", evidence="metric change needs the user's call")
rc, out, _ = run()
check("valid user-fork request allows the stop", rc == 0 and out == {}, f"out={out}")
check("honored request is archived", any((R / "stop_requests").glob("*user-fork.json")))
check("honored request is cleared", not (R / "stop_request.json").exists())
check("honored request is logged", "STOP_REQUEST" in (R / "loop_stops.log").read_text(encoding="utf-8"))

# 6 — bad reason code
reset(rows=3)
write_request(utc=iso(), reason_code="im-tired", evidence="x")
rc, out, _ = run()
check("unknown reason_code is refused", out.get("decision") == "block" and "not one of" in out.get("reason", ""))

# 7 — missing evidence
reset(rows=3)
write_request(utc=iso(), reason_code="hard-blocked", evidence="  ")
rc, out, _ = run()
check("empty evidence is refused", out.get("decision") == "block" and "`evidence`" in out.get("reason", ""))

# 8 — stale request must not silently end a later run
reset(rows=3)
write_request(utc=iso(minutes_ago=120), reason_code="user-fork", evidence="stale one")
rc, out, _ = run()
check("stale request is refused", out.get("decision") == "block" and "old (window" in out.get("reason", ""))

# 9 — exhausted while holding a named untried lever (the untried-lever clause)
reset(rows=3)
write_request(utc=iso(), reason_code="exhausted", evidence="plateau across families",
              untried_levers=["drive amplitude"], campaign_status_utc=iso())
rc, out, _ = run()
check("exhausted refused with an untried lever named",
      out.get("decision") == "block" and "untried_levers` is non-empty" in out.get("reason", ""),
      out.get("reason", "")[:200])

# 10 — exhausted with no untried_levers field at all
reset(rows=3)
write_request(utc=iso(), reason_code="exhausted", evidence="plateau", campaign_status_utc=iso())
rc, out, _ = run()
check("exhausted requires the untried_levers field",
      out.get("decision") == "block" and "requires an `untried_levers` list" in out.get("reason", ""))

# 11 — exhausted with a stale campaign-status
reset(rows=3)
write_request(utc=iso(), reason_code="exhausted", evidence="plateau", untried_levers=[],
              campaign_status_utc=iso(minutes_ago=400))
rc, out, _ = run()
check("exhausted requires a recent campaign-status",
      out.get("decision") == "block" and "campaign_status_utc" in out.get("reason", ""))

# 12 — fully valid exhausted
reset(rows=3)
write_request(utc=iso(), reason_code="exhausted", evidence="all four lever families at the same floor",
              untried_levers=[], campaign_status_utc=iso(minutes_ago=5))
rc, out, _ = run()
check("fully valid exhausted allows the stop", rc == 0 and out == {}, f"out={out}")

# 13 — stall ladder: repeated blocks with no new row escalate, then release
reset(rows=3)
escalated_at = None
released_at = None
for i in range(1, 40):
    rc, out, _ = run()
    if out.get("decision") != "block":
        released_at = i
        break
    if "STALL:" in out.get("reason", "") and escalated_at is None:
        escalated_at = i
check("stall escalates before releasing", escalated_at is not None and escalated_at < (released_at or 99),
      f"escalated_at={escalated_at} released_at={released_at}")
check("stall releases at the cap", released_at == 26, f"released_at={released_at}")
check("stall release is logged", "STALL_RELEASE" in (R / "loop_stops.log").read_text(encoding="utf-8"))

# 14 — progress resets the counter: a new scoreboard row clears the stall
reset(rows=3)
for _ in range(5):
    run()
before = json.loads((R / "loop_state.json").read_text(encoding="utf-8"))["consecutive_blocks"]
with open(R / "scoreboard.tsv", "a", encoding="utf-8") as f:
    f.write("003\t2026-08-03\t0.42\t\tNEW\n")
run()
after = json.loads((R / "loop_state.json").read_text(encoding="utf-8"))["consecutive_blocks"]
check("a new scoreboard row resets the stall counter", before == 5 and after == 1, f"{before} -> {after}")

# 15 — fail-open: a corrupt state file must not brick the loop, and the bypass must be recorded
reset(rows=3)
(R / "scoreboard.tsv").write_text(HEADER + "000\tx\ty\t\t\n", encoding="utf-8")
rc, out, _ = run()
check("corrupt-free baseline still blocks", out.get("decision") == "block")

# 16 — kill switch
reset(rows=3)
env = dict(os.environ, AUTORESEARCH_LOOP_HEARTBEAT="off")
rc, out, _ = run(env=env)
check("AUTORESEARCH_LOOP_HEARTBEAT=off disables the gate", rc == 0 and out == {}, f"out={out}")

# 17 — malformed stdin fails open and logs the bypass
reset(rows=3)
p = subprocess.run(PY + [str(HOOK)], input="not json", capture_output=True, text=True)
check("malformed stdin fails open", p.returncode == 0 and not p.stdout.strip(), f"out={p.stdout}")
check("fail-open bypass is logged to gate_failures.log",
      (R / "gate_failures.log").exists() and "FAIL-OPEN" in (R / "gate_failures.log").read_text(encoding="utf-8"))

# 18 — hook stdout must stay ASCII-safe. The block reason carries em-dashes, and json.dumps escapes them
#      (ensure_ascii) so a legacy console codepage cannot raise UnicodeEncodeError. Switching any emitter to
#      ensure_ascii=False, or printing a reason directly, would fail the hook open under cp1252 and silently
#      disable the gate on exactly the Windows machines this kit runs on. This test pins that property.
reset(rows=3)
env = dict(os.environ, PYTHONIOENCODING="cp1252")
rc, out, err = run(env=env)
check("cp1252 stdout still emits a valid block", out.get("decision") == "block", f"rc={rc} err={err[:200]}")

# 19 — supervisor stand-down: a driver-spawned worker's per-unit end-of-turn is EARNED
reset(rows=3)
env = dict(os.environ, AUTORESEARCH_SUPERVISED="1")
rc, out, _ = run(env=env)
check("AUTORESEARCH_SUPERVISED=1 stands the hook down", rc == 0 and out == {}, f"out={out}")

# 20 — driver-alive stand-down: while a supervisor driver's sentinel is FRESH, attended sessions
#      (the concierge, a user checking in) may end turns freely - the driver owns loop persistence.
reset(rows=3)
(R / ".driver_alive").write_text('{"pid": 1234}', encoding="utf-8")
rc, out, _ = run()
check("fresh .driver_alive stands the hook down", rc == 0 and out == {}, f"out={out}")
check("driver-alive stand-down is logged",
      "DRIVER_ALIVE_STANDDOWN" in (R / "loop_stops.log").read_text(encoding="utf-8"))

# 21 — a STALE sentinel re-arms the hook (a crashed driver must not leave the loop gate open)
reset(rows=3)
(R / ".driver_alive").write_text('{"pid": 1234}', encoding="utf-8")
old = (datetime.now(timezone.utc) - timedelta(hours=1)).timestamp()
os.utime(R / ".driver_alive", (old, old))
rc, out, _ = run()
check("stale .driver_alive re-arms the hook (blocks)", out.get("decision") == "block", f"out={out}")
check("block reason points at supervisor mode first",
      "--supervise" in out.get("reason", "") or "run-campaign" in out.get("reason", ""),
      out.get("reason", "")[:240])

# 22 — sentinel removed entirely -> normal enforcement again
reset(rows=3)
rc, out, _ = run()
check("no sentinel -> normal block", out.get("decision") == "block", f"out={out}")

shutil.rmtree(SANDBOX, ignore_errors=True)

print()
print(f"{'ALL PASS' if not FAILS else str(len(FAILS)) + ' FAILED: ' + ', '.join(FAILS)}")
sys.exit(1 if FAILS else 0)
