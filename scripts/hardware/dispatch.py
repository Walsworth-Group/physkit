"""dispatch.py - the hardware-mode CLI: preflight, emit, wait, ingest.

One command per verb so an operator can stop between any two of them. That is deliberate:
the first live arm on any instrument should be driven by a human who can watch the rig, and a
single do-everything command removes the place to stand.

    python dispatch.py preflight --instrument <spec.json> --campaign <tag>
    python dispatch.py gate      --instrument <spec.json> --type <t> --set k=v ...
    python dispatch.py emit      --instrument <spec.json> --campaign <tag> --unit <id> \
                                 --type <t> --set k=v ...  [--dry-run-root DIR]
    python dispatch.py wait      --instrument <spec.json> --campaign <tag> --unit <id>
    python dispatch.py ingest    --instrument <spec.json> --campaign <tag> --unit <id>
    python dispatch.py status    --instrument <spec.json> --campaign <tag>

`--dry-run-root` redirects the ORDERS root to a scratch directory: the full gate, envelope,
serializer, and file-protocol path run, and the real instrument never sees anything. Run it
before every first-of-its-kind arm. `preflight` never writes an order at all.

`gate` is the cheapest thing in the system: it answers "would this arm be allowed" for zero
instrument time, and prints the refusal as the teaching text the loop would receive.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ingest import collect, quarantine                      # noqa: E402
from instrument import GateRejection, Instrument, Order      # noqa: E402


def parse_settings(pairs: list[str]) -> dict:
    """--set k=v, typed by literal: int, then float, then bool/null, else string.

    No unit suffixes and no expressions. A settings value that needs arithmetic to be written
    down should be computed by whatever proposed it, so that the number the gate checks is
    the number the instrument receives.
    """
    out = {}
    for p in pairs or []:
        if "=" not in p:
            sys.exit(f"--set expects k=v, got {p!r}")
        k, v = p.split("=", 1)
        v = v.strip()
        low = v.lower()
        if low in ("true", "false"):
            out[k] = (low == "true")
        elif low in ("null", "none"):
            out[k] = None
        else:
            try:
                out[k] = int(v)
            except ValueError:
                try:
                    out[k] = float(v)
                except ValueError:
                    out[k] = v
    return out


def find_order(inst: Instrument, campaign: str, unit: str) -> Order | None:
    """Rebuild the Order handle from DURABLE state, so wait/ingest work in a fresh process
    after a restart - the in-flight set is never carried in memory (durability point 1).

    Reads back through the transport and the declared serializer, which means this also
    re-proves that what was written can be read: a payload the emitter can produce and the
    reader cannot parse would otherwise only surface at the rig.
    """
    for handle in inst.transport.pending(campaign):
        if handle.unit_id != unit:
            continue
        try:
            env = inst.serializer.loads(Path(handle.ref).read_text(encoding="utf-8"))
        except Exception:
            return handle
        handle.experiment_type = env.get("experiment_type") or ""
        handle.settings = dict(env.get("settings") or {})
        if inst.results_dir_key:
            handle.settings.pop(inst.results_dir_key, None)
        handle.expected_duration_s = float(env.get("expected_duration_s") or 0.0)
        if env.get("results_dir"):
            handle.results_dir = Path(env["results_dir"])
        return handle
    # Already terminal: not pending any more, but wait/ingest still need the handle. The
    # transport owns its layout; the CLI only asks for the ref.
    try:
        pth = inst.transport.terminal_order_ref(campaign, unit)
    except NotImplementedError:
        pth = None
    if pth is not None:
        env = inst.serializer.loads(Path(pth).read_text(encoding="utf-8"))
        settings = dict(env.get("settings") or {})
        if inst.results_dir_key:
            settings.pop(inst.results_dir_key, None)
        return Order(unit_id=unit, experiment_type=env.get("experiment_type") or "",
                     settings=settings,
                     expected_duration_s=float(env.get("expected_duration_s") or 0.0),
                     results_dir=Path(env.get("results_dir") or (inst.data_root / unit)),
                     ref=pth)
    return None


def cmd_preflight(a, inst: Instrument) -> int:
    print(f"instrument : {inst.instrument_id}  (contract v{inst.spec['contract_version']})")
    print(f"orders root: {inst.orders_root}")
    print(f"order dir  : {inst.order_dir(a.campaign).name}")
    print(f"data root  : {inst.data_root}")
    print(f"serializer : {inst.serializer_name}   provenance: {inst.provenance_source}")
    print(f"types      : {', '.join(sorted(inst.types))}")
    problems = inst.audit_prefix_reachable(a.campaign)
    pend = inst.pending(a.campaign)
    if pend:
        print(f"\nIN FLIGHT ({len(pend)}): " + ", ".join(p.name for p in pend))
    if problems:
        print("\nPREFLIGHT PROBLEMS:")
        for p in problems:
            print("  - " + p)
        return 1
    print("\npreflight: OK - the channel is reachable and correctly named.")
    return 0


def cmd_gate(a, inst: Instrument) -> int:
    settings = parse_settings(a.set)
    try:
        gated = inst.gate(a.type, settings)
    except GateRejection as exc:
        print(f"REJECTED ({len(exc.reasons)} reason(s)) - no instrument time spent:\n")
        for r in exc.reasons:
            print("  * " + r + "\n")
        return 1
    est = inst.estimate_seconds(a.type, gated)
    print("ACCEPTED. Settings as they would be emitted (apparatus givens filled, "
          "calibrations as stated):")
    print(json.dumps(gated, indent=2))
    print(f"\nestimated wall-clock: {est:.0f} s ({est / 60:.1f} min)")
    return 0


def cmd_emit(a, inst: Instrument) -> int:
    settings = parse_settings(a.set)
    override = Path(a.dry_run_root).resolve() if a.dry_run_root else None
    if override:
        print(f"DRY RUN - orders go to {override}, the instrument sees nothing.\n")
    try:
        order = inst.emit(a.unit, a.type, settings, campaign_tag=a.campaign,
                          orders_root_override=override)
    except GateRejection as exc:
        print(f"REJECTED ({len(exc.reasons)} reason(s)) - no order written:\n")
        for r in exc.reasons:
            print("  * " + r + "\n")
        return 1
    print(f"order      : {order.ref}")
    print(f"results dir: {order.results_dir}")
    print(f"estimate   : {order.expected_duration_s:.0f} s "
          f"({order.expected_duration_s / 60:.1f} min)")
    print("\n--- payload as written ---")
    print(Path(order.ref).read_text(encoding="utf-8"))
    if override:
        print("DRY RUN complete. Nothing was dispatched.")
    else:
        print("Order is live. The lab program must have auto-load ENABLED to pick it up.")
    return 0


def cmd_wait(a, inst: Instrument) -> int:
    order = find_order(inst, a.campaign, a.unit)
    if order is None:
        print(f"no order found for unit {a.unit!r} under campaign {a.campaign!r}")
        return 1
    pause = Path(a.pause) if a.pause else None
    stop = Path(a.stop) if a.stop else None
    t0 = time.time()

    def tick(s):
        mark = " [PAUSED]" if s["paused"] else ""
        print(f"  waiting {s['waited_s']:6.0f}s  results={s['results']}{mark}", flush=True)

    print(f"waiting on {Path(order.ref).name} (estimate "
          f"{order.expected_duration_s / 60:.1f} min, poll {a.poll}s). Ctrl-C is safe: the "
          "order stays in flight and this command can be re-run.")
    try:
        res = inst.wait(order, poll_s=a.poll, pause_sentinel=pause, stop_sentinel=stop,
                        on_tick=tick)
    except KeyboardInterrupt:
        print("\ninterrupted - order left IN FLIGHT (contract §6: not lost). Re-run `wait`.")
        return 130
    print(f"\nstate: {res['state']}  after {res.get('waited_s', time.time() - t0):.0f}s")
    if res.get("detail"):
        print("detail: " + res["detail"])
    for f in res.get("results", []):
        print("  result: " + f)
    return 0 if res["state"] == "processed" else 1


def cmd_ingest(a, inst: Instrument) -> int:
    order = find_order(inst, a.campaign, a.unit)
    if order is None:
        print(f"no order found for unit {a.unit!r}")
        return 1
    rec = quarantine(inst, order, collect(inst, order))
    rec.pop("_raw", None)
    print(json.dumps(rec, indent=2, default=str))
    v = rec["quarantine"]["verdict"]
    print(f"\nquarantine: {v.upper()} ({rec['quarantine']['version']})")
    for r in rec["quarantine"]["reasons"]:
        print("  - " + r)
    return 0 if v != "quarantined" else 2


def cmd_status(a, inst: Instrument) -> int:
    pend = inst.pending(a.campaign)
    print(f"in flight: {len(pend)}")
    for p in pend:
        print("  " + str(p))
    try:
        for name, state in inst.transport.order_states(a.campaign):
            print(f"  {name}: {state}")
    except NotImplementedError:
        print("  (this transport does not enumerate order states)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command",
                    choices=("preflight", "gate", "emit", "wait", "ingest", "status"))
    ap.add_argument("--instrument", required=True, help="path to instrument.json")
    ap.add_argument("--campaign", default="physkit", help="campaign tag in the order dir name")
    ap.add_argument("--unit", help="unit id (the contract's sole join key)")
    ap.add_argument("--type", help="experiment type, as declared in instrument.json")
    ap.add_argument("--set", action="append", metavar="K=V", help="a settings key")
    ap.add_argument("--dry-run-root", help="emit into this scratch orders root instead")
    ap.add_argument("--poll", type=float, default=30.0, help="wait poll cadence, seconds")
    ap.add_argument("--pause", help="path to the PAUSE sentinel")
    ap.add_argument("--stop", help="path to the STOP sentinel")
    a = ap.parse_args()

    inst = Instrument.load(a.instrument)
    if a.command in ("gate", "emit") and not a.type:
        sys.exit("--type is required for gate/emit")
    if a.command in ("emit", "wait", "ingest") and not a.unit:
        sys.exit("--unit is required for emit/wait/ingest")
    return {"preflight": cmd_preflight, "gate": cmd_gate, "emit": cmd_emit,
            "wait": cmd_wait, "ingest": cmd_ingest, "status": cmd_status}[a.command](a, inst)


if __name__ == "__main__":
    sys.exit(main())
