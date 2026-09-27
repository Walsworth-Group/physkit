"""instrument.py - the generic hardware layer: PhysKit's side of the instrument contract.

This module is LAYER 2 of the hardware-mode design (`docs/reference/instrument-contract.md`):
the machinery that gates, emits, waits, and collects. Everything instrument-specific is a
DESCRIPTION read from `configs/instrument.json` - experiment types, required keys, ranges,
cost coefficients, the payload encoding, the result reader.

Nothing in this file may name a physical unit, an observable, or a result-file extension. That
is a grep-able acceptance criterion, not a style preference: the genericity test for hardware
mode is that a second instrument needs a new instrument.json and a lab-side watcher, and ZERO
edits here. `check_hardware_layer.py` greps this file to enforce it - including for the words
this paragraph would otherwise have used as examples, which is why it does not use them.

Doctrine implemented here, with the reference each rule comes from:
  * REJECT, DON'T FILL, NEVER CLAMP - an out-of-envelope design is hard-rejected and the
    reason is teaching text (mechanism, number, fix), because the refusal is fed back into
    the next proposal (`hardware-in-the-loop.md` §7; contract §7e).
  * The gate runs TWICE - on the proposed settings, and again on the built payload, so a
    serializer bug cannot silently drop a required key (Co-scientist `lab_safety` doctrine).
  * APPARATUS GIVENS may be default-filled; CALIBRATIONS may not. The distinction is declared
    per experiment type (`defaults` vs `required_keys`), never inferred.
  * Liveness is batch-aware and never counts engine-written files (contract §6, §7d).
  * The abort path re-enters the completion path (contract §4 rule 2).
"""
from __future__ import annotations

import fnmatch
import json
import os
import time
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from serializers import SERIALIZERS
from transports import Order, Terminal, atomic_write, build_transport, utc_now  # noqa: F401

CONTRACT_VERSION = 1


class GateRejection(Exception):
    """Raised when a design is refused before it can spend instrument time.

    `.reasons` is a list of teaching-text strings. They are the product, not a side effect:
    the cheapest abort is the one that costs no instrument time, and its value to the loop is
    entirely in whether the refusal explains itself well enough to be fixed.
    """

    def __init__(self, reasons: list[str]):
        self.reasons = reasons
        super().__init__("; ".join(reasons))


class Instrument:
    """The declared instrument. Construct from `configs/instrument.json`."""

    def __init__(self, spec: dict[str, Any], *, base_dir: Path | None = None):
        self.spec = spec
        self.base_dir = base_dir or Path.cwd()
        if int(spec.get("contract_version", 0)) != CONTRACT_VERSION:
            raise ValueError(
                f"instrument.json declares contract_version="
                f"{spec.get('contract_version')!r}; this layer implements {CONTRACT_VERSION}. "
                "Refusing to run rather than guessing at protocol differences.")
        self.instrument_id = spec["instrument_id"]
        o = spec["orders"]
        self.orders_root = self._resolve(o["root"])
        self.orders_prefix = o["prefix"]
        self.orders_ext = o["ext"]
        self.provenance_source = o["provenance_source"]
        # Some lab programs are told where to write via a key inside the payload rather than
        # by the contract's results_dir field. The KEY NAME is declared here so the generic
        # layer never has to know it; the serializer emits it when the spec supplies one.
        self.results_dir_key = o.get("results_dir_key")
        self.serializer_name = o["serializer"]
        if self.serializer_name not in SERIALIZERS:
            raise ValueError(
                f"instrument.json names serializer {self.serializer_name!r}, which is not "
                f"registered. Known: {sorted(SERIALIZERS)}. A serializer is declared, never "
                "improvised - add it to serializers.py with its own round-trip test.")
        self.serializer = SERIALIZERS[self.serializer_name]
        d = spec["data"]
        self.data_root = self._resolve(d["root"])
        # WHERE THE DRIVER READS vs WHERE THE INSTRUMENT WRITES. Normally the same path,
        # so this is absent and nothing changes. But the driver need not run on the machine
        # that owns the storage (a remote loop reaching it over a mount), and then the two
        # sides name the same directory differently. `root` is always the DRIVER's view -
        # every filesystem operation goes through it. `instrument_root`, when declared, is
        # the INSTRUMENT's view, and is used for exactly one thing: the results directory
        # written into the order. Kept as a RAW string, never resolved through Path: the
        # other machine's convention must survive this one's (a foreign absolute path would
        # otherwise be mangled into a relative component, or have its separators rewritten).
        self.instrument_data_root = d.get("instrument_root") or None
        self.result_glob = d["result_glob"]
        self.engine_written = tuple(d.get("engine_written", ("manifest.json",)))
        self.types = spec["experiment_types"]
        self.caps = spec.get("caps", {})
        # HOW we reach the instrument, separated from WHAT we say to it. Absent = file_v1, so
        # every instrument.json written before the seam existed keeps working unchanged.
        self.transport_name = o.get("transport", "file_v1")
        self.transport = build_transport(self.transport_name, orders=o, data=d,
                                         resolve=self._resolve)

    # ---------- construction ----------

    @classmethod
    def load(cls, path: str | Path) -> "Instrument":
        p = Path(path).resolve()
        return cls(json.loads(p.read_text(encoding="utf-8")), base_dir=p.parent)

    def _resolve(self, raw: str) -> Path:
        """Roots may be absolute, or relative to the instrument.json that declared them.

        Relative-to-the-spec (not to the cwd) so a campaign relocates as one unit: the
        absolute-path-in-a-config rule that `validate_campaign.py` already enforces on the
        rest of the tree. An instrument's own root is the one legitimate absolute path,
        because the instrument does not move when the campaign does."""
        p = Path(os.path.expandvars(raw)).expanduser()
        return p if p.is_absolute() else (self.base_dir / p).resolve()

    # ---------- the gate ----------

    def type_spec(self, experiment_type: str) -> dict[str, Any]:
        if experiment_type not in self.types:
            raise GateRejection([
                f"experiment_type {experiment_type!r} is not declared by instrument "
                f"{self.instrument_id!r}. Declared: {', '.join(sorted(self.types))}. "
                "An undeclared type has no required-key contract and no range table, so it "
                "cannot be gated - and an ungated order is exactly what the gate exists to "
                "prevent. Fix: use a declared type, or declare this one in instrument.json."])
        return self.types[experiment_type]

    def gate(self, experiment_type: str, settings: dict[str, Any],
             *, deadline_epoch: float | None = None) -> dict[str, Any]:
        """Validate a design. Returns the settings WITH apparatus givens filled; raises
        GateRejection with teaching text otherwise. Never clamps a value into range."""
        ts = self.type_spec(experiment_type)
        reasons: list[str] = []
        merged = dict(ts.get("defaults") or {})
        merged.update(settings)

        # (1) required keys - reject, don't fill. A calibration may not be defaulted: a
        # duration is only meaningful at the drive it was calibrated at, so the pair must
        # travel together. Anything safe to default is declared in `defaults` instead.
        missing = [k for k in ts.get("required_keys", []) if merged.get(k) is None]
        if missing:
            reasons.append(
                f"missing required key(s) for {experiment_type!r}: {', '.join(missing)}. "
                "These are calibrations, not apparatus givens - the gate will not fill them, "
                "because a filled-in calibration is a silent assumption that looks like a "
                "measurement. Fix: state each one explicitly in the proposal.")

        # (2) unknown keys - an undispatched key is not a lever. Same failure as the
        # `validate_method` hook's own motivating incident: an unwired lever burned a full
        # evaluation because the run looked like a real test of something it never changed.
        known = set(ts.get("required_keys", [])) | set(ts.get("defaults") or {}) \
            | set(ts.get("optional_keys") or [])
        unknown = sorted(set(merged) - known)
        if unknown:
            reasons.append(
                f"unrecognized settings key(s): {', '.join(unknown)}. Instrument "
                f"{self.instrument_id!r} dispatches {experiment_type!r} only on "
                f"{', '.join(sorted(known))}. A key the instrument does not dispatch on "
                "changes nothing while the arm still costs full instrument time. "
                "Fix: drop it, or declare it in instrument.json first.")

        # (3) declared numeric ranges. Units are carried as opaque LABELS from the spec and
        # only ever echoed into the reason string - this layer never interprets them.
        for key, lo, hi, unit in ts.get("float_ranges", []):
            if key in merged and merged[key] is not None:
                try:
                    v = float(merged[key])
                except (TypeError, ValueError):
                    reasons.append(f"{key}={merged[key]!r} is not numeric")
                    continue
                if not (lo <= v <= hi):
                    reasons.append(
                        f"{key}={v:g} {unit} is outside the declared envelope "
                        f"[{lo:g}, {hi:g}] {unit}. This is a hard limit, not a lever: it is "
                        "rejected, never clamped, because a clamped design silently becomes "
                        "a different experiment than the one that was reasoned about. "
                        f"Fix: re-propose with {key} inside the envelope.")
        for key, lo, hi in ts.get("int_ranges", []):
            if key in merged and merged[key] is not None:
                try:
                    v = int(merged[key])
                except (TypeError, ValueError):
                    reasons.append(f"{key}={merged[key]!r} is not an integer")
                    continue
                if not (lo <= v <= hi):
                    reasons.append(
                        f"{key}={v} is outside the declared range [{lo}, {hi}]. "
                        f"Fix: re-propose with {key} inside it, tiling across arms if the "
                        "span you want exceeds one arm's ceiling.")

        # (4) declared window guards: a centre +/- half-width must fit inside a band. Purely
        # structural - three key NAMES and two numbers, all from the spec.
        for g in ts.get("window_guards", []):
            c_key, w_key, (blo, bhi) = g["center"], g["half_width"], g["band"]
            if merged.get(c_key) is None or merged.get(w_key) is None:
                continue
            try:
                c, w = float(merged[c_key]), float(merged[w_key])
            except (TypeError, ValueError):
                reasons.append(f"{c_key}={merged[c_key]!r} / {w_key}={merged[w_key]!r} is not "
                               "numeric; the window guard needs numbers. Fix: state both as numbers.")
                continue
            if w <= 0:
                reasons.append(f"{w_key}={w:g} must be > 0")
            elif not (blo <= c - w and c + w <= bhi):
                reasons.append(
                    f"{g.get('name', 'window')} [{c - w:g}, {c + w:g}] exceeds the declared "
                    f"band [{blo:g}, {bhi:g}]. Fix: reduce {w_key}, move {c_key}, or tile "
                    "the span across several arms.")

        # (5) declared pairwise ordering constraints (a floor below its ceiling).
        for lo_key, hi_key in ts.get("ordered_pairs", []):
            if merged.get(lo_key) is not None and merged.get(hi_key) is not None:
                try:
                    lo_v, hi_v = float(merged[lo_key]), float(merged[hi_key])
                except (TypeError, ValueError):
                    reasons.append(f"{lo_key}={merged[lo_key]!r} / {hi_key}={merged[hi_key]!r} is "
                                   "not numeric; the ordering constraint needs numbers.")
                    continue
                if lo_v >= hi_v:
                    reasons.append(f"{lo_key}={lo_v:g} must be < {hi_key}={hi_v:g}")

        # (5b) declared product caps: prod(key^power) <= max. The declarable form of a
        # shared-resource budget (e.g. an actuator's amp^2 * seconds thermal limit) that no
        # single-key range can express.
        for pc in ts.get("product_caps", []):
            terms = pc.get("terms", [])
            if any(merged.get(k) is None for k, _ in terms):
                continue
            try:
                vals = [(k, float(merged[k]), p) for k, p in terms]
            except (TypeError, ValueError):
                reasons.append(
                    f"{pc.get('name', 'product cap')}: a term is not numeric "
                    f"({ {k: merged[k] for k, _ in terms} }); state numbers.")
                continue
            prod = 1.0
            for _, v, pw in vals:
                prod *= v ** pw
            cap_v = float(pc.get("max", 0) or 0)
            if cap_v and prod > cap_v:
                expr = " * ".join(f"{k}^{pw}({v:g})" for k, v, pw in vals)
                reasons.append(
                    f"{pc.get('name', 'product cap')} = {prod:g} {pc.get('unit', '')} exceeds "
                    f"the cap {cap_v:g}: {expr}. Reduce one factor; the cap is a shared-resource "
                    "budget, never a lever.")

        # (6) wall-clock cap, from the declared cost model.
        est = self.estimate_seconds(experiment_type, merged)
        cap = float(self.caps.get("max_arm_seconds", 0) or 0)
        if cap and est > cap:
            reasons.append(
                f"estimated arm wall-clock {est / 3600:.2f} h exceeds the cap "
                f"{cap / 3600:.2f} h. Instrument time is the binding budget. "
                "Fix: reduce the averaging or the point count, or split across arms.")

        # (7) budget fit against an ABSOLUTE deadline epoch, never a remaining-seconds
        # snapshot - a snapshot taken at planning time goes stale by exactly one round
        # length, which is how an arm that "fit" ran past the end of the session (contract §7f).
        if deadline_epoch is not None and est > 0:
            remaining = deadline_epoch - time.time()
            if est > remaining:
                reasons.append(
                    f"estimated arm wall-clock {est / 3600:.2f} h does not fit the "
                    f"{max(0.0, remaining) / 3600:.2f} h remaining before the session "
                    "deadline. Fix: emit a design that fits, or shorten the arm.")

        if reasons:
            raise GateRejection(reasons)
        return merged

    def estimate_seconds(self, experiment_type: str, settings: dict[str, Any]) -> float:
        """Declared cost model: base + n*(per_unit + per_unit_per_rep*reps).

        Deliberately one shape rather than an expression evaluator. A cost model that can run
        arbitrary code is a second place for instrument physics to hide, and the estimate has
        to be checkable against the actual (`hardware-in-the-loop.md` §8) - which means it has
        to be legible in the spec, not compiled into it."""
        cm = (self.types.get(experiment_type) or {}).get("cost_model")
        if not cm:
            return 0.0
        n = float(settings.get(cm.get("count_key", ""), cm.get("count_default", 1)) or 1)
        reps = float(settings.get(cm.get("rep_key", ""), cm.get("rep_default", 1)) or 1)
        return float(cm.get("base_s", 0.0)
                     + n * (cm.get("per_count_s", 0.0)
                            + cm.get("per_count_per_rep_s", 0.0) * reps))

    # ---------- emission ----------

    def order_dir(self, campaign_tag: str, *, day: str | None = None) -> Path:
        """Contract §2. Built from the SPEC's prefix, never typed twice - a prefix typo is
        the silent wedge of §7a: the watcher ignores the directory with no error anywhere."""
        day = day or datetime.now().strftime("%Y_%m_%d")
        return self.orders_root / f"{self.orders_prefix}{campaign_tag}_{day}"

    @staticmethod
    def _foreign_sep(root: str) -> str:
        """The separator the OTHER side uses, inferred from how it names its own root."""
        if "\\" in root or (len(root) > 1 and root[1] == ":" and root[0].isalpha()):
            return "\\"
        return "/"

    def _instrument_view(self, results_dir: Path) -> str:
        """The results directory AS THE INSTRUMENT NAMES IT.

        Returns the driver's own path unchanged unless `data.instrument_root` is declared.
        Composed by string join rather than Path: pathlib normalises separators to whichever
        OS is running, which would make the emitted order depend on where the loop happened
        to run - the coupling this exists to remove.
        """
        root = self.instrument_data_root
        if not root:
            return str(results_dir)
        sep = self._foreign_sep(root)
        return root.rstrip("/\\") + sep + Path(results_dir).name

    def build_envelope(self, unit_id: str, experiment_type: str, settings: dict[str, Any],
                       *, campaign_tag: str, results_dir: Path,
                       expected_duration_s: float) -> dict[str, Any]:
        env: dict[str, Any] = {
            "provenance": {
                "source": self.provenance_source,
                "campaign": campaign_tag,
                "emitted_at": utc_now(),
                "order_version": CONTRACT_VERSION,
            },
            "unit_id": unit_id,
            "experiment_type": experiment_type,
            "settings": dict(settings),
            "expected_duration_s": float(expected_duration_s),
            # The instrument's view (identical to ours unless instrument_root is declared).
            "results_dir": self._instrument_view(results_dir),
        }
        if self.results_dir_key:
            env["_results_dir_key"] = self.results_dir_key
        return env

    def emit(self, unit_id: str, experiment_type: str, settings: dict[str, Any], *,
             campaign_tag: str, deadline_epoch: float | None = None,
             orders_root_override: Path | None = None,
             day: str | None = None) -> Order:
        """Gate, then write the order atomically. Returns the Order handle."""
        gated = self.gate(experiment_type, settings, deadline_epoch=deadline_epoch)
        est = self.estimate_seconds(experiment_type, gated)
        results_dir = self.data_root / unit_id
        envelope = self.build_envelope(unit_id, experiment_type, gated,
                                       campaign_tag=campaign_tag, results_dir=results_dir,
                                       expected_duration_s=est)

        # SECOND ENFORCEMENT (contract §7e / Co-scientist lab_safety): re-gate the settings as
        # they come back OUT of the serialized payload, not as they were proposed. Gating the
        # in-memory envelope would miss the more dangerous half: a builder can drop a key, but
        # so can an encoder, and the bytes are what the instrument acts on. Round-tripping
        # here means every emission also proves its own serializer, and the check covers the
        # incident it exists for - 567 arms that carried a field the builder had discarded.
        payload = self.serializer.dumps(envelope)
        round_tripped = dict((self.serializer.loads(payload).get("settings") or {}))
        if self.results_dir_key:
            # The results-dir alias rides inside the payload for instruments that are told
            # where to write by a settings key; it is contract plumbing, not a lever, so it
            # is removed before the gate sees it.
            round_tripped.pop(self.results_dir_key, None)
        self.gate(experiment_type, round_tripped, deadline_epoch=deadline_epoch)

        transport = self.transport
        if orders_root_override is not None:
            # Dry run: same gate, same envelope, same serializer, same protocol - a scratch
            # destination. Rebuilding the transport rather than special-casing emit() means the
            # dry run exercises the real path instead of a lookalike of it.
            transport = build_transport(
                self.transport_name,
                orders={**self.spec["orders"], "root": str(orders_root_override)},
                data=self.spec["data"], resolve=self._resolve)

        # Durability point 2: the record of what was asked is written LOCALLY, by us, at
        # emission - whatever the transport is. A remote transport must not be the only place
        # this exists. It is engine-written by definition and never counts as liveness.
        # A DRY RUN leaves the campaign data tree untouched: its manifest lands beside the
        # scratch orders instead ("the instrument sees nothing" must also mean the campaign
        # records nothing as real).
        if orders_root_override is None:
            results_dir.mkdir(parents=True, exist_ok=True)
            atomic_write(results_dir / "manifest.json", json.dumps(envelope, indent=2))
        else:
            Path(orders_root_override).mkdir(parents=True, exist_ok=True)
            atomic_write(Path(orders_root_override) / (envelope["unit_id"] + ".manifest.json"),
                         json.dumps(envelope, indent=2))
        order = transport.submit(envelope, payload, campaign_tag=campaign_tag, day=day)
        if self.instrument_data_root:
            # The transport reconstructs the Order from the envelope, which now carries the
            # INSTRUMENT's view of the results directory. The Order is OURS: ingest reads
            # results through `order.results_dir`, so it must name the path THIS process can
            # open. Restoring it here keeps the two views from leaking into one another -
            # and the branch is skipped entirely when no translation is declared.
            order = replace(order, results_dir=results_dir)
        return order

    # ---------- waiting ----------

    def result_files(self, results_dir: Path | None = None, order: Order | None = None
                     ) -> list[Path]:
        """Instrument-written result artifacts. Engine-written names are excluded by the
        transport, at the one place that defines what "the instrument produced something" means.

        Accepts either an Order or a bare results_dir; the second form keeps the older call
        sites working and is why this is not simply `transport.collect`.
        """
        if order is None:
            order = Order(unit_id="", experiment_type="", settings={},
                          expected_duration_s=0.0, results_dir=Path(results_dir))
        return self.transport.collect(order)

    def any_liveness_since(self, since_epoch: float) -> bool:
        """Batch-aware liveness (contract §6): has the instrument produced anything ANYWHERE
        since `since_epoch`, not just for the unit being waited on. When a round emits several
        orders and the lab works them FIFO, the newest order's own directory legitimately stays
        empty for hours - scoping liveness to it declares a wedge on a rig that is working."""
        return self.transport.liveness_since(since_epoch)

    def wait(self, order: Order, *, poll_s: float = 30.0, timeout_s: float | None = None,
             pause_sentinel: Path | None = None, stop_sentinel: Path | None = None,
             abort_check: Callable[[Order], str | None] | None = None,
             on_tick: Callable[[dict[str, Any]], None] | None = None) -> dict[str, Any]:
        """Poll for a terminal marker at a calm fixed cadence and no more.

        Do not fill the wait with manufactured work (`hardware-in-the-loop.md` §3): it
        substitutes an expensive kind of spin for a cheap one and burns the autonomy budget
        the guard exists to protect.

        Returns {"state": processed|rejected|wedged|stopped, ...}.
        """
        timeout_s = timeout_s if timeout_s is not None else max(
            float(self.caps.get("min_timeout_s", 3600.0)),
            order.expected_duration_s * float(self.caps.get("timeout_slack", 3.0)))
        started = time.time()
        liveness_since = started
        aborted_reason: str | None = None

        while True:
            term = self.transport.poll(order)
            if term is not None:
                return {"state": term.state, "marker": term.ref,
                        "detail": term.detail, "waited_s": time.time() - started,
                        "aborted": aborted_reason is not None,
                        "abort_reason": aborted_reason,
                        "results": [str(p) for p in self.transport.collect(order)]}

            if stop_sentinel is not None and stop_sentinel.exists():
                return {"state": "stopped", "waited_s": time.time() - started,
                        "detail": "stop sentinel present; the in-flight order is left alone"}

            paused = pause_sentinel is not None and pause_sentinel.exists()
            if paused:
                # PAUSE suppresses, never trips a halt (contract §8): restamp the wedge clock
                # so a long human session at the rig cannot accumulate into a false wedge.
                started = time.time()
                liveness_since = started

            if not paused and aborted_reason is None and abort_check is not None:
                reason = abort_check(order)
                if reason:
                    # One abort request per order, ever. Deterministic verdicts only - an
                    # abort is an intervention and must be reproducible, so it is never a
                    # model's judgment call (`hardware-in-the-loop.md` §7).
                    self.transport.abort(order, reason)
                    aborted_reason = reason

            waited = time.time() - started
            if not paused and waited > timeout_s:
                if self.any_liveness_since(liveness_since):
                    # The rig is demonstrably working - it is just working on something else.
                    # Extend rather than wedge, and restamp so the next window is fresh.
                    liveness_since = time.time()
                    started = time.time()
                else:
                    self.transport.record_wedged(
                        order,
                        f"physkit: no terminal acknowledgment after {waited:.0f} s and no "
                        f"instrument-written result anywhere in that window (contract §6).\n"
                        f"utc: {utc_now()}\n")
                    return {"state": "wedged", "waited_s": waited,
                            "detail": "no terminal acknowledgment and no liveness"}

            if on_tick is not None:
                on_tick({"waited_s": waited, "paused": paused,
                         "aborted": aborted_reason is not None,
                         "results": len(self.transport.collect(order))})
            time.sleep(poll_s)

    # ---------- pending-set recovery ----------

    def pending(self, campaign_tag: str) -> list[Path]:
        """Every emitted order with no terminal acknowledgment, recovered from DURABLE state.

        Durability point 1: never from memory. A restart of either side must re-derive the
        in-flight set, which is the whole reason this channel is not a live connection.
        Returns the transport's refs so existing callers keep printing something meaningful.
        """
        return [o.ref for o in self.transport.pending(campaign_tag)]

    def pending_orders(self, campaign_tag: str) -> list[Order]:
        """The same set as `pending`, as Order handles you can wait on or abort."""
        return self.transport.pending(campaign_tag)

    def audit_prefix_reachable(self, campaign_tag: str) -> list[str]:
        """Report anything that would make this channel silently not work.

        For the file transport that is contract §7a - a wrong prefix produces no execution, no
        rejection, and no error on either side, so it has to be checked FOR rather than waited
        on. Every transport owes an equivalent: the failure that is silent on BOTH sides.
        """
        return self.transport.preflight(campaign_tag)


def _read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def matches_any(name: str, patterns: tuple[str, ...]) -> bool:
    return any(fnmatch.fnmatch(name, pat) for pat in patterns)
