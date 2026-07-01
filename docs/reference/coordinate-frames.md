---
id: coordinate-frames
kind: reference-doc
layer: shared
load: on-demand
load_trigger: A problem with multiple coordinate frames, non-trivial sign/handedness/orientation conventions, or projected/rotated vectors and gradients — invoked by frame-problem, verify (frame-consistency check), and dimensional-analysis. Not a cover-to-cover preload.
frozen: false
addresses: [5]
status: new
review: living
---

# Coordinate frames — the depth behind frame hygiene

The cheapest coordinate bug is the one you prevent by **declaring frames up front**. Numbers computed
correctly in an undeclared frame are unverifiable — nobody, including the agent that produced them, can
check a quantity whose frame was never stated. The bookkeeping *is* the check: a well-declared frame turns
"is this right?" into a mechanical comparison; an undeclared one turns it into an argument. This doc is the
depth behind `frame-problem`'s physics inventory and `verify`'s frame-consistency check.

## The discipline
- **Declare every frame explicitly before using it** — origin, axes, handedness/orientation — and **give
  each a name.** "The lab frame" and "the cylinder frame" are names; "the frame" is not.
- **One symbol per axis per frame — never overload a symbol across frames.** The motivating failure: a
  session used **`z` for two different axes** — the lab/field-of-view normal at θ=0, *and* the
  cylinder/NV axis — and then wrote `dB_z/dz`. That expression is ambiguous by construction: which `z` is
  in the numerator, which in the denominator? It cannot be checked until the symbols are disambiguated.
- **State the frame of every derived quantity**, especially gradients/derivatives and projected vector
  components. `dB_NV/dx` is a lab-frame statement (the NV-projected field, differentiated along the lab
  x-axis); `dB_z/dz` is a cylinder-frame statement (the axial field, differentiated along the cylinder
  axis). They are not interchangeable, not equal in general, and not substitutable in a formula — say which
  one you mean every time, not once at the top of a derivation.
- **Resolve orientation, handedness, and chirality from an independent geometric reference** — a known
  feature orientation, a fiducial mark, the apparatus geometry — **never from the fit.** A fit will happily
  pick whichever frame or sign minimizes its error; using the fit's own preference to fix the frame it was
  fit in is circular and proves nothing.
- **Fix and state active vs. passive** (rotating the object vs. rotating the axes) and **degrees vs.
  radians.** Both are silent-failure modes: the math goes through in either convention, only the number
  changes, so nothing downstream complains — the check has to be explicit because the code won't be.

## The ambiguity/degeneracy catalog
Some symmetries leave the observable **exactly invariant**, so no amount of fitting or code review resolves
them internally — only an external reference or an explicit convention can. Name which one applies and how
you broke it:

- **Transpose/handedness degeneracy.** A forward model symmetric under swapping data axes (x↔y, a
  transpose) combined with an angle map like φ → 90°−φ can reproduce the same observable from a
  mirror-image geometry. Break it with an independent orientation reference (never the fit) *and* a
  dedicated equivalence self-test that checks the two candidate frames give the same prediction before you
  rely on either.
- **Sign unobservables.** A quantity that enters the model only through its square (e.g. a canting term
  ∝ n_z²) fixes only |n_z| — the sign is not determined by the data at all. Report the invariant
  (`|n_z|`) and do not claim a sign the observable can't see.
- **Global sign / gauge freedom.** Fixed by a chosen reference state (a zero point, a reference
  orientation) — state which reference you fixed it to, since the "correct" sign is a convention, not a
  physical fact, until a reference is named.
- **Index/storage-order convention.** `(row, col) = (y, x)`, or "which stored axis is called x" — this is a
  **data-layout** convention, not a physical-frame choice, and the two must not be conflated: getting the
  physics frame right while silently transposing the storage array reproduces the transpose/handedness bug
  above through the back door.

## Frame-consistency checklist (verify-time)
Run this whenever a result crosses frames — it is what `verify`'s frame-consistency check executes:
1. Is **every quantity's frame declared** (name, origin, axes, handedness)?
2. Is **no symbol overloaded** across two different frames?
3. Is **every gradient and every projected component labelled with its frame** (not just stated once at the
   top and assumed to carry)?
4. Was **orientation/handedness resolved from an independent reference**, not from what the fit prefers?
5. Does an **independent, from-scratch recompute of the geometry agree** with the shipped code? This is the
   check that actually discriminates a real frame bug from a presentational one — in the motivating case, a
   from-scratch vector-then-project rebuild matched the shipped kernel to ~1e-12–1e-13, which is what let the
   team conclude the numerics were right and the problem was purely in how the frames were named and
   reported.
6. Is there a **symmetry/degeneracy self-test for each ambiguity in the catalog above** that plausibly
   applies to this problem (transpose/handedness equivalence, sign-invariant reporting, gauge reference
   stated, storage-order documented)?

If any box is unchecked, the result is not yet verifiable, independent of whether the number looks right.

## Worked cautionary example
`@transcript_asifit_2026-07-01`: an ASI–NV magnetometry session computed a bias-magnet gradient correction.
The **correct** framing treats the gradient as a **lab/field-of-view-frame quantity**: evaluate the full 3-D
magnet field at each lab pixel, project it onto the sensor's NV axis n̂, and report `dB_NV/dx`, `dB_NV/dy` —
both explicitly lab-frame derivatives of a lab-frame projected quantity. The session instead described the
same computation as a cylinder-axial `dB_z/dz`, because `z` was doing double duty for the FoV normal and the
cylinder axis. The **underlying numerics were correct** — an independent from-scratch rebuild matched the
shipped code to ~1e-12 — but the two-meanings-for-`z` bookkeeping made the claim uncheckable by inspection,
and it took a user catching the ambiguity (not any automated check) to force the reframing into
`dB_NV/dx`/`dB_NV/dy`. Right code, unverifiable presentation: the exact failure mode this doc exists to
prevent.

## Pointers
`frame-problem` (declare frames in the physics inventory, up front); `verify` (the frame-consistency check
above, run before a cross-frame result is trusted); `dimensional-analysis` (units/frame is the first cheap
check, and shares the "state it or it's not checkable" ethic); a campaign's `CONVENTIONS.md` (where a
project pins its frame names, handedness, and active/passive + degrees/radians choices for the duration).
