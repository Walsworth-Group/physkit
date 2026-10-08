---
id: instrument-contract
kind: reference-doc
layer: operating
load: on-demand
load_trigger: Implementing either side of the PhysKit-instrument coupling — writing a lab-side
  watcher that accepts PhysKit work orders, or writing the campaign hooks that emit them. The
  normative half of `hardware-in-the-loop.md` §2; read that section first for why the channel is
  files, then this for the bytes. §11 covers non-file transports and the durability properties
  each must re-earn.
frozen: false
review: living
---

# The instrument contract — the normative protocol

`hardware-in-the-loop.md` §2 argues that the agent–instrument channel should be
an append-only file protocol in a watched directory. This document is that
protocol, written down precisely enough to implement twice, independently, and
have the two halves interoperate.

**Sections 1–10 describe the file materialization, which is the default and the
only one shipped. §11 states the smaller machine underneath it** — order →
{in flight, complete, refused} — and what any other transport must re-earn before
it may carry the same contract. Read §1–§10 to implement a lab-side watcher; read
§11 before proposing to reach an instrument some other way. It is the **only** interface PhysKit has to a
real instrument: PhysKit never speaks a lab program's protocol, never links its
libraries, and never drives its GUI.

**Division of labour.** §2 of the reference doc owns the *why* — this document
does not restate its rationale. This document owns the *what*: paths, names,
schemas, ordering, atomicity, and the failure modes that have actually wedged a
running loop. Where the two disagree, §2 governs intent and this document
governs bytes.

**Who implements what.** The lab side implements a watcher (§4, §5, §9). PhysKit
implements the emitter and the poller. Everything instrument-specific — the
experiment types, the settings keys, the on-disk encoding, the result file
extension — is *declared* in `configs/instrument.json`, never coded into the
generic layer.

A conforming lab side can be LabVIEW, MATLAB, Python, or a C++ GUI. The whole
obligation is: watch a directory, read a file, write sibling files.

## 1. Two roots

The protocol has two directory roots, and they are deliberately not the same
place.

| Root | Owned by | Direction | Typical location |
|---|---|---|---|
| **orders root** | the **instrument** | PhysKit writes, lab reads | inside the lab-control program's own tree, at a path it already watches |
| **data root** | the **campaign** | lab writes, PhysKit reads | `<campaign>/lab_data/`, redirectable per campaign |

Commands go *out* to a directory the instrument owns; results come *back* into a
directory the campaign owns. The split is what makes a blind campaign and a
clean-room rerun possible: point a second campaign at a fresh data root and it
inherits no history, while both campaigns still dispatch through the one
directory the instrument watches.

Both roots are declared in `configs/instrument.json`. The orders root is fixed
by the instrument. The data root is campaign-local and must be writable by the
lab side.

## 2. Naming

```
<orders_root>/<orders_prefix><campaign_tag>_<YYYY_MM_DD>/<unit_id>.order<ext>
<data_root>/<unit_id>/<block files, instrument-defined>
<data_root>/<unit_id>/manifest.json          <- written by PhysKit at emission
```

- `orders_prefix` is an agreed string (e.g. `physkit_`). **The lab side
  auto-loads only from directories whose name begins with it** — see §7(a).
- `campaign_tag` and `unit_id` are PhysKit's. `unit_id` is the campaign's
  experiment identifier and is the **sole join key** between an order, its
  markers, and its results; it must appear verbatim in the results directory
  name, because nothing else correlates the two roots.
- `ext` is declared in `instrument.json` and defaults to `.json`. The contract
  fixes the directory layout, the marker protocol, and the *envelope* (§3); the
  on-disk **encoding** may be whatever the instrument already parses, produced
  by a serializer declared per instrument. An instrument that natively reads
  YAML gets YAML; the envelope fields and their meanings do not change.
- One order file per unit. Batching is several order files in one dated
  directory, never several units inside one file.

## 3. The work order

The envelope is fixed. `settings` is instrument-defined and is validated against
`instrument.json` before emission, never after.

```json
{
  "provenance": {
    "source": "physkit/<kit_version>",
    "campaign": "<campaign_tag>",
    "emitted_at": "<ISO-8601 UTC>",
    "order_version": 1
  },
  "unit_id": "<campaign experiment id>",
  "experiment_type": "<one of instrument.json's declared types>",
  "settings": { "<instrument-defined levers>": "..." },
  "expected_duration_s": 0,
  "results_dir": "<path under the data root, for this unit>"
}
```

- **`provenance` is the auto-load precondition.** A file in a watched directory
  *without* a well-formed provenance block must not be executed. This is what
  lets a human leave a hand-written file in the same tree without the loop
  claiming it, and what lets the lab side tell an agent-authored order from an
  operator's.
- `expected_duration_s` is PhysKit's cost-model estimate. The lab side may
  ignore it; PhysKit uses it to scale the in-flight timeout (§6), and later to
  check the estimate against the actual (`T_wall` estimated *and* actual, per §8
  of the reference doc).
- `results_dir` is stated explicitly rather than derived, so a lab side that
  cannot compute the campaign's path convention only has to read a string.
- **Atomic write, always.** Write to a temporary name on the same filesystem and
  `os.replace` (or the platform equivalent) into position. A watcher must never
  observe a half-written order. The same rule applies to every marker and every
  result file.

## 4. Markers

A marker is a **sibling file whose name is the order's full name plus a
suffix** — never a rename or a move of the order itself. "Pending" is then
computable by glob (`*.order<ext>` minus those carrying a terminal sibling), and
the order stays readable as the durable record of what was asked.

| Marker | Written by | Meaning |
|---|---|---|
| `<order>.processed` | lab | terminal: the unit is finished. **Also written after an abort** |
| `<order>.rejected` | lab | terminal: the watcher refused the order; the reason is inside |
| `<order>.abort` | PhysKit | non-terminal request: stop this unit cleanly, now |
| `<order>.wedged` | PhysKit | record only: PhysKit gave up waiting. The lab side never reads it |

Contents:

- `.processed` — at minimum a completion timestamp; optionally a small JSON
  status object. PhysKit must treat an **empty** `.processed` as valid.
- `.rejected` — **must** carry a human-readable reason. That reason is teaching
  text: it is fed back into the next proposal's context verbatim, so it should
  name the mechanism, the number, and the fix, not merely say "invalid".
- `.abort` — may carry the deterministic verdict that triggered it. One abort
  request per order, ever.
- `.wedged` — PhysKit's own note of when and why it stopped waiting.

Rules:

1. `.processed` and `.rejected` are **mutually exclusive and terminal**. Once
   either exists the unit's lifecycle is over, and neither side writes further
   markers for it.
2. **The abort path re-enters the normal completion path.** On seeing `.abort`
   the lab side halts the acquisition and then writes `.processed`, exactly as
   if the unit had completed. PhysKit therefore has one unblocking path rather
   than two, and whatever partial data exists ingests through the ordinary
   quarantine gate (reference doc §6). A lab side that acknowledged an abort
   with some *other* marker would deadlock every poller that watches only for
   the terminal pair.
3. Neither side deletes a marker during a campaign. Clearing them is an operator
   action.

## 5. Lifecycle

```
PhysKit                                   lab side
-------                                   --------
gate the design (reject-don't-fill)
write manifest.json into results_dir
atomically write <unit>.order<ext>   -->  watcher sees a new file
                                           |
                                           +- absent/bad provenance -> IGNORE (not rejected)
                                           +- unacceptable settings -> write .rejected(reason)
                                           +- accepted -> acquire, streaming result
                                                          files into results_dir
poll for a terminal marker
  (calm fixed cadence; idle cheaply)
optional: deterministic fatal verdict
  -> write <unit>.abort              -->  halt cleanly
                                     <--  write .processed
see .processed -> collect + ingest
                  -> quarantine stamp -> score
```

Between emission and ingest the PhysKit side has exactly three states: **in
flight** (emitted, no terminal marker, inside the timeout), **complete**
(`.processed`), and **refused** (`.rejected`). There is no "lost" state; see §6.

## 6. Waiting, liveness, and the wedge

- **An emitted but unacknowledged order is *in flight*, not lost.** The timeout
  scales with `expected_duration_s` rather than being a fixed constant, and a
  restart of either side re-derives the pending set from the filesystem, never
  from memory.
- **Poll at a calm fixed cadence and no more.** Do not fill the wait with
  manufactured work (reference doc §3).
- **Liveness is batch-aware.** When a round emits several orders and the lab
  works them FIFO, the newest order's own results directory legitimately stays
  empty for hours. Declare a wedge only when *both* hold: the wait has exceeded
  the timeout, **and** no new result file has appeared anywhere under the data
  root within that window.
- **Engine-written files must not count as liveness.** `manifest.json` is
  written by PhysKit at emission; if it counts, every fresh emission fakes its
  own liveness and the wedge detector never fires. Partially-written and
  periodically-rewritten result files *do* count — they are the instrument's
  genuine heartbeat.
- On a wedge: write `.wedged`, stop waiting on that unit, and record it as an
  **operational** failure. A wedge is an operations bug to fix and re-gate,
  never a data point against the physics under test (reference doc §1). N
  consecutive wedges is systemic and halts the loop.
- **Count completed units path-independently.** Persist the set of order
  filenames already counted and reconcile by scanning for terminal markers whose
  mtime is after the session start. A unit that finished while PhysKit was
  restarting is then still counted, exactly once.

## 7. Named failure modes

Each of these has cost real instrument time. A lab-side implementer should read
this section as the acceptance test for their watcher.

**(a) The silent prefix wedge.** A watcher that auto-loads only from directories
matching `orders_prefix` will *silently ignore* everything else — no execution,
no `.rejected`, no error, on either side. A typo in the prefix, or a campaign tag
that changes the directory name's shape, therefore wedges the loop with no
diagnostic anywhere. **Mitigations, both required:** the emitted directory name
is derived from `instrument.json` and never typed twice; and the readiness gate
dispatches one throwaway order and requires a terminal marker back before the
campaign is allowed to start (with the shipped CLI that is an `emit` of a
designated probe unit followed by `wait` - `preflight` alone never writes an
order, so it cannot stand in for this).

**(a2) Redispatch.** A unit whose order reached a terminal marker and must run again gets a
**fresh order identity**: the engine re-submits under an attempt-suffixed file name
(`<unit>~2.order.<ext>`), never the original path — a re-submit to a path that already has a
terminal sibling would be answered instantly by the stale marker and the instrument would never
see it. The `unit_id` inside the payload (the sole join key) is unchanged; the latest attempt is
the unit's live record.

**(b) The marker-as-rename.** Acknowledging by renaming or moving the order
destroys the pending-set glob and the record of what was asked. Markers are
additive siblings, always.

**(c) The abort that invented its own marker.** See §4 rule 2.

**(d) Engine-written liveness.** See §6.

**(e) The clamp.** A watcher that silently corrects an out-of-range setting
instead of rejecting it converts a design error into a result that looks valid
and is not. The gate rejects; it never clamps and never fills. That obligation is
PhysKit's at emission and the lab side's at acceptance.

**(f) The stale deadline.** Budget fit is checked against an absolute deadline
epoch carried in the order's context, not against a remaining-seconds snapshot
taken at planning time — such a snapshot goes stale by exactly one round length.

## 8. The pause sentinel

`<campaign>/results/PAUSE` — its existence idles the hardware loop completely: no
new orders are emitted, polling continues at its calm cadence for anything
already in flight, and nothing is abandoned. `touch` hands the rig to a human;
`rm` hands it back.

- **PAUSE suppresses; it never trips a halt.** While PAUSE exists the wedge clock
  is restamped on every poll, so a long human session cannot accumulate into a
  false instrument-wedge.
- **PAUSE is not STOP.** `results/STOP` is PhysKit's existing graceful
  end-of-unit stop and ends the campaign loop. PAUSE is resumable and specific to
  hardware mode. If both exist, STOP wins.
- The sentinel lives under the campaign's `results/`, not the orders root — it is
  a message to PhysKit, not to the instrument.

## 9. Conformance checklist (lab side)

A watcher conforms when all nine hold:

1. Auto-loads only from directories under the orders root matching the agreed
   prefix, and ignores everything else.
2. Refuses to execute any order lacking a well-formed `provenance` block.
3. Parses the envelope; treats unknown *envelope* keys as forward-compatible and
   ignorable, and unknown `settings` keys as a rejection.
4. Rejects out-of-envelope settings with a reason; never clamps, never fills.
5. Writes results under `results_dir`, one file per block, atomically, with
   `unit_id` recoverable from the path.
6. Writes `.rejected` (with a reason) or `.processed` for every order it loads —
   exactly one, exactly once.
7. Polls for `.abort` during acquisition, halts cleanly on it, and then writes
   `.processed`.
8. Never renames, moves, or deletes an order or a marker.
9. Survives its own restart without re-executing an order that already carries a
   terminal marker.

`tests/structured_loop/tests/stub_instrument.py` is a conforming reference
implementation, and its `reject | slow | wedge | abort_midway | partial` modes
are the counter-examples. Run the PhysKit side against it before running it
against the rig.

## 10. What this contract deliberately does not specify

The acquisition itself; the settings vocabulary; the result file format; how the
instrument schedules its own queue; calibration; and any physical quantity, unit,
or tolerance. All of those are instrument-side, or live in
`configs/instrument.json`. Nothing in the generic PhysKit layer may name a
physical unit, a frequency, or a result file extension — that constraint is a
grep-able acceptance criterion, and this document is written to be conformant
with it.

## 11. Transports — the contract is a state machine, not a file format

Everything above describes a **watched directory** with sibling markers. That is the default
materialization and it earned the default: it needed zero edits to a lab program that had never
heard of PhysKit. But the contract it materializes is smaller and more portable than the files:

    order -> { in flight, complete, refused },  plus abort-re-enters-complete,
              plus provenance-gated acceptance.

A lab program that is already a server, or that cannot be modified at all, wants a different
materialization of the same machine. PhysKit therefore reaches an instrument through a declared
**transport** (`orders.transport` in `instrument.json`; absent means `file_v1`), implementing
eight methods in two groups:

| Group | Methods |
|---|---|
| lifecycle | `submit` · `poll` · `abort` · `collect` |
| channel | `pending` · `liveness_since` · `record_wedged` · `preflight` |

The gate is deliberately **not** among them. `Instrument.gate()` performs no I/O and reaches no
transport; a design is refused by pure code before anything is contacted. No transport may offer
a submit-without-gate path, and none may be exposed as a tool an agent can call directly — the
emission gate is only a gate while dispatch is deterministic code that cannot be bypassed.

### The durability checklist

Files provide five properties for free. Any other transport must re-earn each one explicitly,
and a transport that skips one looks correct until the first crash. **A new transport is not
finished until its docstring answers all five:**

1. **Enumerate in flight after a restart.** `pending()` answered from durable state, never from
   this process's memory.
2. **A durable record of what was asked.** PhysKit writes the manifest locally at emission
   regardless of transport, so a remote channel is never the only copy.
3. **Human inspect / replay / clear.** An operator can see the channel and empty it with the
   loop stopped.
4. **Abort re-enters the NORMAL completion path** (§4 rule 2) — never a second terminal state.
5. **Liveness our own writes cannot fake** (§6, §7d).

### Candidate transports, and which problem each solves

- **`file_v1` (shipped).** The protocol in §1–§9. Default; use it whenever the lab side can watch
  a directory.
- **A process transport.** Run a command per order, wait for exit, read a directory. This is the
  right answer for the hardest case — a vendor GUI or closed instrument that **cannot** be
  modified — because there nobody can add a watcher either, and someone has to write an adapter
  regardless. Likely the highest-value second transport.
- **An HTTP/RPC transport.** For lab software that is already a server, or a facility instrument
  with no shared filesystem. Must supply an endpoint enumerating in-flight orders, or point 1
  fails.

Unknown transport names are a hard error, never a silent fall back to files: falling back would
put orders somewhere the instrument never looks, which is failure mode §7(a) wearing a different
hat.

---

*See also:* `hardware-in-the-loop.md` (§2 the channel, §3 pausing and the pause
sentinel, §6 ingest quarantine, §7 the emission gate and mid-flight abort) ·
`ARCHETYPE_CHEATSHEET.md` §E.
