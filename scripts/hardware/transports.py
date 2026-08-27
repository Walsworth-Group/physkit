"""transports.py - how PhysKit reaches an instrument, factored out from what it says to one.

The instrument contract is a STATE MACHINE, not a file format:

    order -> {in flight, complete, refused},  plus abort-re-enters-complete,
             plus provenance-gated acceptance.

A watched directory with sibling markers is one materialization of that machine. It is the
default, and it earned the default: it needed zero edits to a lab program that had never heard
of PhysKit. But it is not the only one, and a lab program that is already a server, or that
cannot be modified at all, wants a different materialization of the SAME machine.

## The seam

Eight methods, in two groups:

  LIFECYCLE  submit · poll · abort · collect
  CHANNEL    pending · liveness_since · record_wedged · preflight

(An earlier sketch called this "four operations". That was the lifecycle half only - the channel
half is what makes crash recovery and wedge detection work, and leaving it out would have pushed
filesystem assumptions back into the generic layer through the side door.)

What is deliberately NOT here: the gate. `Instrument.gate()` touches no transport at all, and
that separation is the safety property - a design is refused before anything is reached, by code
with no I/O in it. Do not let a transport acquire a "submit unchecked" path.

## The durability checklist - what a new transport must re-earn

Files give these away for free. Anything else has to provide them explicitly, and a transport
that skips one looks correct right up until the first crash. A new transport is not done until
its docstring answers all five:

  1. **Enumerate in flight after a restart.** `pending()` must be answerable from durable state,
     never from this process's memory. (Files: glob for orders with no terminal sibling.)
  2. **A durable record of what was asked.** Written locally at emission regardless of transport
     - see `Instrument.emit`, which writes the manifest itself for exactly this reason.
  3. **Human inspect / replay / clear.** An operator must be able to see the channel and empty it
     without the loop running.
  4. **Abort re-enters the NORMAL completion path.** Never a second terminal state. A transport
     that acknowledges an abort differently deadlocks every poller that watches for the ordinary
     terminal pair.
  5. **Liveness that our own writes cannot fake.** Whatever counts as "the instrument is doing
     something" must exclude everything PhysKit writes (contract §7d).

Registered transports are declared per instrument (`orders.transport`), defaulting to `file_v1`
so every existing instrument.json keeps working unchanged.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, NamedTuple


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_write(path: Path, text: str) -> None:
    """Temp on the same filesystem, then os.replace. A watcher - or a poller on the other side -
    must never observe a half-written file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


class Terminal(NamedTuple):
    """A terminal observation: the unit is complete or refused, and why."""
    state: str          # "processed" | "rejected"
    detail: str
    ref: str = ""       # transport-specific locator of the acknowledgment, for the record


@dataclass
class Order:
    """A dispatched unit, transport-neutral.

    `ref` is an opaque, transport-specific locator. The generic layer never interprets it; it
    only hands it back to the transport that produced it.
    """
    unit_id: str
    experiment_type: str
    settings: dict[str, Any]
    expected_duration_s: float
    results_dir: Path
    ref: Any = None
    emitted_at: str = field(default_factory=utc_now)


class Transport:
    """Base class. Subclasses answer the five durability points in their own docstring."""

    name = "abstract"

    # --- lifecycle ---
    def submit(self, envelope: dict[str, Any], payload: str, *, campaign_tag: str,
               day: str | None = None) -> Order:
        raise NotImplementedError

    def poll(self, order: Order) -> Terminal | None:
        """Terminal observation, or None while still in flight. Must not block."""
        raise NotImplementedError

    def abort(self, order: Order, reason: str) -> None:
        """Request a clean stop. The instrument must then acknowledge through the NORMAL
        completion path (durability point 4)."""
        raise NotImplementedError

    def collect(self, order: Order) -> list[Path]:
        """Instrument-written result artifacts for this unit, engine-written names excluded."""
        raise NotImplementedError

    def terminal_order_ref(self, campaign_tag: str, unit_id: str):
        """The ref of a unit's order that has already reached a terminal state, or None.
        Lets a CLI rebuild a handle after completion without knowing the transport's layout."""
        raise NotImplementedError

    def order_states(self, campaign_tag: str) -> list[tuple[str, str]]:
        """(order name, state) for every order this campaign has emitted - state is 'pending'
        or a comma-joined list of the transport's own terminal/abort markers."""
        raise NotImplementedError

    # --- channel ---
    def pending(self, campaign_tag: str) -> list[Order]:
        raise NotImplementedError

    def liveness_since(self, epoch: float) -> bool:
        """Has the INSTRUMENT produced anything since `epoch`, anywhere - not just for the unit
        being waited on (batch-aware liveness, contract §6)."""
        raise NotImplementedError

    def record_wedged(self, order: Order, reason: str) -> None:
        """PhysKit's own durable note that it stopped waiting. Not a request to the instrument."""
        raise NotImplementedError

    def preflight(self, campaign_tag: str) -> list[str]:
        """Problems that would make this channel silently not work. Returns teaching text."""
        raise NotImplementedError


class FileTransport(Transport):
    """The watched-directory contract: `docs/reference/instrument-contract.md`.

    Durability checklist:
      1. in flight = glob `*.order<ext>` with no terminal sibling; re-derived from disk, never
         from memory, so either side restarts freely.
      2. the order file itself is the record of what was asked, and stays readable because
         markers are additive siblings rather than renames.
      3. inspect/replay/clear is a file manager.
      4. `.abort` is halted-and-then-`.processed` by the lab side - one unblocking path.
      5. engine-written names are excluded from liveness, so a fresh emission cannot fake its
         own heartbeat.
    """

    name = "file_v1"

    def __init__(self, *, orders_root: Path, prefix: str, ext: str, data_root: Path,
                 result_glob: str, engine_written: tuple[str, ...] = ("manifest.json",)):
        self.orders_root = orders_root
        self.prefix = prefix
        self.ext = ext
        self.data_root = data_root
        self.result_glob = result_glob
        self.engine_written = tuple(engine_written)

    TERMINAL_SUFFIXES = (".processed", ".rejected")

    # --- helpers ---
    def marker(self, order: Order, suffix: str) -> Path:
        return Path(order.ref).with_name(Path(order.ref).name + suffix)

    def order_dir(self, campaign_tag: str, day: str | None = None) -> Path:
        day = day or datetime.now().strftime("%Y_%m_%d")
        return self.orders_root / f"{self.prefix}{campaign_tag}_{day}"

    # --- lifecycle ---
    def submit(self, envelope, payload, *, campaign_tag, day=None) -> Order:
        unit_id = envelope["unit_id"]
        results_dir = Path(envelope["results_dir"])
        d = self.order_dir(campaign_tag, day)
        path = d / f"{unit_id}.order{self.ext}"
        # Redispatch gets a FRESH order identity: if this unit's order already reached a
        # terminal marker, a re-submit to the same path would be answered instantly by the
        # stale sibling (the fast-fail found in the HW-1a acceptance run). The attempt
        # suffix lives on the FILE name only; the unit_id inside the payload - the
        # contract's sole join key - is unchanged.
        attempt = 1
        while any(path.with_name(path.name + s).exists()
                  for s in self.TERMINAL_SUFFIXES + (".abort",)):
            attempt += 1
            path = d / f"{unit_id}~{attempt}.order{self.ext}"
        atomic_write(path, payload)
        return Order(unit_id=unit_id, experiment_type=envelope["experiment_type"],
                     settings=dict(envelope["settings"]),
                     expected_duration_s=float(envelope["expected_duration_s"]),
                     results_dir=results_dir, ref=path)

    def poll(self, order: Order) -> Terminal | None:
        for suffix in self.TERMINAL_SUFFIXES:
            p = self.marker(order, suffix)
            if p.exists():
                return Terminal("rejected" if suffix == ".rejected" else "processed",
                                _read_text(p), str(p))
        return None

    def terminal_order_ref(self, campaign_tag: str, unit_id: str):
        hits = []
        for od in sorted(self.orders_root.glob(f"{self.prefix}{campaign_tag}_*")):
            hits += sorted(od.glob(f"{unit_id}.order{self.ext}"))
            hits += sorted(od.glob(f"{unit_id}~*.order{self.ext}"))
        return hits[-1] if hits else None   # the LATEST attempt is the live record

    def order_states(self, campaign_tag: str) -> list[tuple[str, str]]:
        out = []
        for od in sorted(self.orders_root.glob(f"{self.prefix}{campaign_tag}_*")):
            for o in sorted(od.glob(f"*.order{self.ext}")):
                marks = [s for s in self.TERMINAL_SUFFIXES + (".abort",)
                         if o.with_name(o.name + s).exists()]
                out.append((o.name, ", ".join(sorted(set(marks))) or "pending"))
        return out

    def abort(self, order: Order, reason: str) -> None:
        m = self.marker(order, ".abort")
        if m.exists():                      # one abort request per order, durable across restarts
            return
        atomic_write(m, reason + "\n")

    def collect(self, order: Order) -> list[Path]:
        d = order.results_dir
        if not d.is_dir():
            return []
        return [p for p in sorted(d.rglob(self.result_glob))
                if p.name not in self.engine_written and not p.name.endswith(".tmp")]

    # --- channel ---
    def pending(self, campaign_tag: str) -> list[Order]:
        out: list[Order] = []
        if not self.orders_root.is_dir():
            return out
        for d in sorted(self.orders_root.iterdir()):
            if not d.is_dir() or not d.name.startswith(f"{self.prefix}{campaign_tag}_"):
                continue
            for o in sorted(d.glob(f"*.order{self.ext}")):
                if any(o.with_name(o.name + s).exists() for s in self.TERMINAL_SUFFIXES):
                    continue
                out.append(Order(unit_id=o.name.split(".order")[0].split("~")[0], experiment_type="",
                                 settings={}, expected_duration_s=0.0,
                                 results_dir=self.data_root / o.name.split(".order")[0], ref=o))
        return out

    def liveness_since(self, epoch: float) -> bool:
        if not self.data_root.is_dir():
            return False
        for p in self.data_root.rglob(self.result_glob):
            if p.name in self.engine_written or p.name.endswith(".tmp"):
                continue
            try:
                if p.stat().st_mtime >= epoch:
                    return True
            except OSError:
                continue
        return False

    def record_wedged(self, order: Order, reason: str) -> None:
        atomic_write(self.marker(order, ".wedged"), reason)

    def preflight(self, campaign_tag: str) -> list[str]:
        problems = []
        if not self.orders_root.exists():
            problems.append(
                f"orders root does not exist: {self.orders_root}. The watcher cannot see an "
                "order that has nowhere to land.")
        elif not os.access(self.orders_root, os.W_OK):
            problems.append(f"orders root is not writable: {self.orders_root}")
        d = self.order_dir(campaign_tag)
        if not d.name.startswith(self.prefix):
            problems.append(
                f"order directory {d.name!r} does not start with the declared prefix "
                f"{self.prefix!r} - the watcher would ignore it SILENTLY.")
        if not self.data_root.exists():
            problems.append(f"data root does not exist: {self.data_root}")
        sib = [p.name for p in self.orders_root.iterdir()] if self.orders_root.is_dir() else []
        if sib and not any(n.startswith(self.prefix) for n in sib):
            problems.append(
                f"no directory under {self.orders_root} starts with {self.prefix!r}. If the lab "
                f"side has a different convention, the prefix in instrument.json is wrong and "
                "every order will be ignored without a diagnostic.")
        return problems


def _read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def build_transport(name: str, *, orders: dict, data: dict, resolve) -> Transport:
    """Construct the declared transport. Unknown names FAIL rather than defaulting: silently
    falling back to files would put orders somewhere the instrument never looks, which is the
    silent-wedge failure mode wearing a different hat."""
    if name == "file_v1":
        return FileTransport(orders_root=resolve(orders["root"]), prefix=orders["prefix"],
                             ext=orders["ext"], data_root=resolve(data["root"]),
                             result_glob=data["result_glob"],
                             engine_written=tuple(data.get("engine_written",
                                                           ("manifest.json",))))
    raise ValueError(
        f"instrument.json declares transport {name!r}, which is not registered. Known: "
        f"{sorted(TRANSPORT_NAMES)}. Add it to transports.py, answer the five durability points "
        "in its docstring, and give it a case in check_hardware_layer.py.")


TRANSPORT_NAMES = ("file_v1",)
