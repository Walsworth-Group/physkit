"""ingest.py - generic collection + the quarantine stamp.

The last third of the hardware loop: block files on disk -> a reduced record -> a quarantine
verdict. Like `instrument.py` this file names no physical quantity; what a result file
CONTAINS is read by a declared reader, and what makes an acquisition scientifically void is
declared in the instrument's `quarantine` block.

The rule this implements (`hardware-in-the-loop.md` §6): an acquisition can complete
mechanically and still be scientifically void. Gate at ingest, stamp ok/caution/quarantined,
exclude quarantined results from everything downstream that steers the campaign, and make the
reason travel with the record - because a quietly-dropped result and a quietly-kept bad result
are the same integrity failure.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

OK, CAUTION, QUARANTINED = "ok", "caution", "quarantined"


# ---------------------------------------------------------------------------------------
# Readers. A reader turns ONE result file into a flat dict of arrays/scalars. Declared per
# instrument as `data.reader`; registered here so a campaign never improvises one inline.
# ---------------------------------------------------------------------------------------

def _read_json_blocks(path: Path) -> dict[str, Any]:
    """The stub instrument's block format, and a reasonable default for any lab program that
    can write JSON. Used by the token-free end-to-end tests."""
    return json.loads(path.read_text(encoding="utf-8"))


def _read_scipy_mat(path: Path) -> dict[str, Any]:
    """MATLAB-style container via scipy.io.loadmat.

    Imported lazily and reported as a MISSING DEPENDENCY rather than an ingest failure: a
    machine without scipy should say so plainly instead of producing an empty record that
    looks like an instrument problem.
    """
    try:
        from scipy.io import loadmat
    except ImportError as exc:
        raise RuntimeError(
            "reader 'scipy_mat_v1' needs scipy (pip install scipy). This is a MISSING "
            "DEPENDENCY on the analysis machine, not an instrument fault - do not record it "
            "as a failed acquisition.") from exc
    m = loadmat(str(path), squeeze_me=True)
    return {k: v for k, v in m.items() if not k.startswith("__")}


READERS: dict[str, Callable[[Path], dict[str, Any]]] = {
    "json_blocks_v1": _read_json_blocks,
    "scipy_mat_v1": _read_scipy_mat,
}


# ---------------------------------------------------------------------------------------
# Collection + quarantine
# ---------------------------------------------------------------------------------------

def _first_present(container: dict[str, Any], names: list[str]) -> tuple[str | None, Any]:
    """Instruments disagree about what they call the same array across versions, so the spec
    lists ALIASES in priority order rather than one name. Returns (name_used, value)."""
    for n in names:
        if n in container and container[n] is not None:
            return n, container[n]
    return None, None


def _length(v: Any) -> int:
    try:
        import numpy as np
        return int(np.asarray(v).ravel().size)
    except Exception:
        try:
            return len(v)
        except TypeError:
            return 1 if v is not None else 0


def collect(instrument, order, *, reader: str | None = None) -> dict[str, Any]:
    """Read every instrument-written result file for this order into one record.

    The NEWEST file is the completed acquisition where a lab program rewrites a working file
    as it averages, so it is read last and its fields win. Earlier files are still counted -
    they are what batch-aware liveness saw.
    """
    reader_name = reader or instrument.spec.get("data", {}).get("reader", "json_blocks_v1")
    if reader_name not in READERS:
        raise ValueError(
            f"instrument.json declares reader {reader_name!r}, which is not registered. "
            f"Known: {sorted(READERS)}. Readers are declared, never improvised.")
    fn = READERS[reader_name]

    files = instrument.result_files(order.results_dir)
    files.sort(key=lambda p: p.stat().st_mtime)
    merged: dict[str, Any] = {}
    read_ok, read_errors = [], []
    for p in files:
        try:
            merged.update(fn(p))
            read_ok.append(str(p))
        except Exception as exc:              # a corrupt file is DATA, not a crash
            read_errors.append(f"{p.name}: {exc!r}")

    ts = instrument.types.get(order.experiment_type, {})
    fields = ts.get("result_fields", {})
    extracted: dict[str, Any] = {}
    for role, names in fields.items():
        if role.startswith("_") or not isinstance(names, list):
            continue
        used, val = _first_present(merged, names)
        if used is not None:
            extracted[role] = {"key": used, "n": _length(val)}
            if _length(val) == 1:
                try:
                    extracted[role]["value"] = float(val)
                except (TypeError, ValueError):
                    pass

    return {
        "unit_id": order.unit_id,
        "experiment_type": order.experiment_type,
        "reader": reader_name,
        "n_result_files": len(files),
        "result_files": [str(p) for p in files],
        "read_errors": read_errors,
        "keys_present": sorted(k for k in merged if isinstance(k, str)),
        "extracted": extracted,
        "_raw": merged,
    }


def quarantine(instrument, order, record: dict[str, Any]) -> dict[str, Any]:
    """Stamp ok / caution / quarantined, with the reason attached to the record.

    Never silent: the verdict and its reason land in the record itself, so a stale-calibration
    or short-sweep result stays identifiable long after ingest.
    """
    q = instrument.spec.get("quarantine", {}) or {}
    reasons: list[str] = []
    verdict = OK

    min_files = int(q.get("min_result_files", 0) or 0)
    if min_files and record["n_result_files"] < min_files:
        verdict = QUARANTINED
        reasons.append(
            f"{record['n_result_files']} instrument-written result file(s), below the "
            f"declared minimum {min_files}. The arm completed mechanically and produced no "
            "science - it is excluded from anything that steers the campaign.")

    if record["read_errors"]:
        verdict = QUARANTINED
        reasons.append("unreadable result file(s): " + "; ".join(record["read_errors"]))

    # Short-acquisition check: the sweep came back with fewer points than were asked for.
    frac = float(q.get("min_points_fraction", 0) or 0)
    ts = instrument.types.get(order.experiment_type, {})
    cm = ts.get("cost_model") or {}
    count_key = cm.get("count_key")
    if frac and count_key and order.settings.get(count_key):
        asked = int(order.settings[count_key])
        # "How much of the acquisition came back" has two shapes and the generic layer must
        # not assume one: an instrument that writes ONE file holding an N-point array, and one
        # that writes N files of a point each. Take whichever is larger - both are the same
        # claim about coverage, and assuming the array shape alone quarantines every
        # block-writing instrument's perfectly good run.
        got = max([v.get("n", 0) for v in record["extracted"].values()]
                  + [record["n_result_files"]], default=0)
        if got and got < frac * asked:
            verdict = QUARANTINED
            reasons.append(
                f"acquisition returned {got} point(s) against {asked} requested "
                f"({got / asked:.0%}, below the declared {frac:.0%} floor) - the arm was cut "
                "short, so its record is not the measurement that was designed.")
        elif got == 0:
            verdict = QUARANTINED
            reasons.append(
                "no sweep/signal array found in the result files. Either the reader is "
                "wrong for this instrument or the acquisition wrote nothing usable; the "
                "keys actually present are recorded alongside this verdict.")

    record["quarantine"] = {
        "verdict": verdict,
        "version": q.get("version", "unversioned"),
        "reasons": reasons,
    }
    return record
