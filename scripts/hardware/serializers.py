"""serializers.py - declared payload encodings for the instrument contract.

The contract fixes the directory layout, the marker protocol, and the ENVELOPE (`provenance`,
`unit_id`, `experiment_type`, `settings`, `expected_duration_s`, `results_dir`). It does not
fix the bytes: an instrument that already parses some other format gets that format, produced
by a serializer NAMED in its instrument.json.

Each serializer is a pair (dumps, loads) over the same envelope dict, plus a round-trip test in
`check_hardware_layer.py`. A serializer is declared, never improvised - an encoder invented at
the call site is how the two sides of a file protocol drift apart while both look correct.

Adding one: write the pair, register it below, add its round-trip case to the checker.
"""
from __future__ import annotations

import json
from typing import Any, Callable, NamedTuple


class Serializer(NamedTuple):
    name: str
    dumps: Callable[[dict[str, Any]], str]
    loads: Callable[[str], dict[str, Any]]


# --------------------------------------------------------------------------------------
# json_v1 - the contract's default encoding.
# --------------------------------------------------------------------------------------

def _json_dumps(envelope: dict[str, Any]) -> str:
    return json.dumps(envelope, indent=2, sort_keys=False) + "\n"


def _json_loads(text: str) -> dict[str, Any]:
    return json.loads(text)


# --------------------------------------------------------------------------------------
# coscientist_yaml_v1 - a YAML order dialect an existing instrument queue parses; the name is part
# of the wire contract, so it stays as is.
#
# This is the payload half of the "PhysKit joins an existing lab program with zero lab-side
# edits" claim, and it is worth being precise about what the lab side requires, because each
# requirement is load-bearing:
#
#   * a top-level `provenance` mapping whose `source` starts with the string the watcher
#     checks; without it the file is REJECTED (a marker is written - this failure is loud),
#   * an `items` list, each with `experiment`, `label`, and an `overrides` mapping - the
#     watcher hands these to the same code path as a human clicking Load Queue,
#   * one queue file per unit, matching the contract's one-order-per-unit rule.
#
# The envelope's `settings` become `overrides`; `unit_id` becomes both the filename stem and
# the `label`, keeping the contract's join key intact through the translation.
#
# Hand-rolled emitter rather than PyYAML: the lab side parses with yaml.safe_load, but PhysKit
# must not acquire a YAML dependency to talk to one instrument, and the value space here is
# closed (numbers, strings, bools) because the gate ran first. `_scalar` is the whole risk
# surface, and the round-trip test covers it.
# --------------------------------------------------------------------------------------

_COSCI_HEADER = ("# AUTO-EMITTED by PhysKit hardware mode. Auto-load requires the\n"
                 "# 'provenance' block below; do not delete it.\n")


def _scalar(v: Any) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if v is None:
        return "null"
    if isinstance(v, (int,)):
        return str(v)
    if isinstance(v, float):
        # repr() keeps full precision, but a dot-less exponent form ("1e-09") is a STRING to a
        # YAML 1.1 reader while our own reader parses it as a float - the one place the two
        # halves could quietly diverge - so the mantissa is forced to carry a dot. An integral
        # float is emitted without the trailing .0 so downstream int() casts on the lab side
        # see what they expect.
        if v.is_integer() and abs(v) < 1e15:
            return str(int(v))
        s = repr(v)
        if "e" in s and "." not in s:
            s = s.replace("e", ".0e")
        return s
    s = str(v)
    if s == "" or any(c in s for c in ":#{}[],&*?|<>=!%@`\"'\n") or s.strip() != s:
        return json.dumps(s)          # JSON strings are valid YAML strings
    return s


def _cosci_dumps(envelope: dict[str, Any]) -> str:
    prov = envelope["provenance"]
    lines = [_COSCI_HEADER.rstrip("\n"),
             "provenance:",
             f"  source: {_scalar(prov['source'])}",
             f"  emitted_at: {_scalar(prov['emitted_at'])}"]
    for k in ("campaign", "order_version"):
        if k in prov:
            lines.append(f"  {k}: {_scalar(prov[k])}")
    # Contract fields the lab side ignores but a human reading the queue file needs, and which
    # make the file self-describing if it is ever found on its own.
    lines.append(f"physkit_unit_id: {_scalar(envelope['unit_id'])}")
    lines.append(f"physkit_expected_duration_s: {_scalar(envelope['expected_duration_s'])}")
    lines.append(f"physkit_results_dir: {_scalar(str(envelope['results_dir']))}")
    lines.append("items:")
    lines.append(f"- experiment: {_scalar(envelope['experiment_type'])}")
    lines.append(f"  label: {_scalar(envelope['unit_id'])}")
    lines.append("  overrides:")
    for k, v in envelope["settings"].items():
        lines.append(f"    {k}: {_scalar(v)}")
    # The lab program is told where to put its output through its own results-dir key; the
    # contract carries the same thing as results_dir. Emitting both keeps the instrument
    # working without the generic layer having to know the key name - it is declared as
    # results_dir_key in the spec and rides in here as an alias.
    alias = envelope.get("_results_dir_key")
    if alias:
        lines.append(f"    {alias}: {_scalar(envelope['results_dir'])}")
    return "\n".join(lines) + "\n"


def _cosci_loads(text: str) -> dict[str, Any]:
    """Minimal reader for round-tripping and for inspecting an emitted order.

    Deliberately NOT a general YAML parser: it reads exactly what `_cosci_dumps` writes. The
    lab side uses yaml.safe_load, and the checker verifies that PyYAML - when available -
    agrees with this reader on real output, so the two halves cannot quietly diverge.
    """
    prov: dict[str, Any] = {}
    settings: dict[str, Any] = {}
    top: dict[str, Any] = {}
    item: dict[str, Any] = {}
    section = None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith("provenance:"):
            section = "prov"
            continue
        if raw.startswith("items:"):
            section = "items"
            continue
        if raw.startswith("- experiment:"):
            item["experiment"] = _unscalar(raw.split(":", 1)[1].strip())
            continue
        if raw.startswith("  label:"):
            item["label"] = _unscalar(raw.split(":", 1)[1].strip())
            continue
        if raw.strip() == "overrides:":
            section = "overrides"
            continue
        if raw.startswith("    ") and section == "overrides":
            k, v = raw.strip().split(":", 1)
            settings[k] = _unscalar(v.strip())
            continue
        if raw.startswith("  ") and section == "prov":
            k, v = raw.strip().split(":", 1)
            prov[k] = _unscalar(v.strip())
            continue
        if not raw.startswith(" ") and ":" in raw:
            k, v = raw.split(":", 1)
            top[k] = _unscalar(v.strip())
    return {"provenance": prov, "unit_id": top.get("physkit_unit_id", item.get("label")),
            "experiment_type": item.get("experiment"), "settings": settings,
            "expected_duration_s": top.get("physkit_expected_duration_s", 0.0),
            "results_dir": top.get("physkit_results_dir", "")}


def _unscalar(s: str) -> Any:
    if s.startswith('"'):
        return json.loads(s)
    if s == "true":
        return True
    if s == "false":
        return False
    if s == "null":
        return None
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        return s


SERIALIZERS: dict[str, Serializer] = {
    s.name: s for s in (
        Serializer("json_v1", _json_dumps, _json_loads),
        Serializer("coscientist_yaml_v1", _cosci_dumps, _cosci_loads),
    )
}
