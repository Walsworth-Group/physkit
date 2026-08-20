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

Declaring frames up front prevents the cheapest class of coordinate bug. Numbers computed correctly in an
undeclared frame are unverifiable: nobody, including the agent that produced them, can check a quantity
whose frame was never stated. A declared frame makes the check a mechanical comparison; an undeclared
frame turns it into an argument. This doc is the depth behind `frame-problem`'s physics inventory and
`verify`'s frame-consistency check.

## The discipline
- **Declare every frame explicitly before using it**: origin, axes, handedness and orientation. Give each
  frame a name. "The lab frame" and "the cylinder frame" are names; "the frame" is not.
- **One symbol per axis per frame. Never overload a symbol across frames.** An overloaded symbol is
  undetectable in the expression it corrupts. If `z` names both a field-of-view normal and a cylinder axis,
  `dB_z/dz` is ambiguous by construction: neither the numerator nor the denominator can be resolved, and
  the expression cannot be checked until the symbols are disambiguated.
- **State the frame of every derived quantity**, in particular gradients, derivatives, and projected vector
  components. `dB_NV/dx` is a lab-frame statement: the NV-projected field, differentiated along the lab
  x-axis. `dB_z/dz` is a cylinder-frame statement: the axial field, differentiated along the cylinder axis.
  They are not interchangeable, not equal in general, and not substitutable in a formula. State which one
  is meant at every occurrence, not once at the top of a derivation.
- **Resolve orientation, handedness, and chirality from an independent geometric reference**: a known
  feature orientation, a fiducial mark, or the apparatus geometry. Never resolve them from the fit. A fit
  selects whichever frame or sign minimizes its error, so using the fit's own preference to fix the frame
  it was fit in is circular.
- **Fix and state active vs. passive** (rotating the object or rotating the axes) **and degrees vs.
  radians.** Both are silent-failure modes: the math goes through under either convention and only the
  number changes, so nothing downstream reports an error. The check has to be explicit because the code
  will not raise one.

## The ambiguity/degeneracy catalog
Some symmetries leave the observable exactly invariant. Fitting and code review cannot resolve them
internally; only an external reference or an explicit convention does. Name which one applies and state how
it was broken:

- **Transpose/handedness degeneracy.** A forward model symmetric under swapping data axes (x↔y, a
  transpose), combined with an angle map such as φ → 90°−φ, reproduces the same observable from a
  mirror-image geometry. Break it with an independent orientation reference, never the fit, and add a
  dedicated equivalence self-test that checks the two candidate frames give the same prediction before
  either is relied on.
- **Sign unobservables.** A quantity that enters the model only through its square (e.g. a canting term
  ∝ n_z²) fixes only |n_z|; the data does not determine the sign. Report the invariant (`|n_z|`) and do
  not claim a sign the observable cannot see.
- **Global sign / gauge freedom.** Fixed by a chosen reference state, such as a zero point or a reference
  orientation. State which reference it was fixed to. Until a reference is named, the correct sign is a
  convention, not a physical fact.
- **Index/storage-order convention.** `(row, col) = (y, x)`, or which stored axis is called x, is a
  data-layout convention, not a physical-frame choice, and the two must not be conflated: getting the
  physics frame right while silently transposing the storage array reproduces the transpose/handedness bug
  above through the back door.

## Frame-consistency checklist (verify-time)
Run this whenever a result crosses frames. It is what `verify`'s frame-consistency check executes:
1. Is every quantity's frame declared (name, origin, axes, handedness)?
2. Is no symbol overloaded across two different frames?
3. Is every gradient and every projected component labelled with its frame, rather than stated once at the
   top and assumed to carry?
4. Was orientation and handedness resolved from an independent reference, not from what the fit prefers?
5. Does an independent, from-scratch recompute of the geometry agree with the shipped code? This is the
   check that discriminates a real frame bug from a presentational one: a rebuild matching the shipped
   kernel to round-off localizes the problem to how the frames were named and reported, while
   disagreement is a numerical frame bug.
6. Is there a symmetry or degeneracy self-test for each ambiguity in the catalog above that plausibly
   applies to this problem (transpose/handedness equivalence, sign-invariant reporting, gauge reference
   stated, storage-order documented)?

If any box is unchecked, the result is not yet verifiable, independent of whether the number looks right.

## Worked cautionary example
A magnetometry analysis computes a bias-magnet gradient correction across a sensor field of view. The
correct framing treats the gradient as a lab/field-of-view-frame quantity: evaluate the full 3-D magnet
field at each lab pixel, project it onto the sensor's NV axis n̂, and report `dB_NV/dx` and `dB_NV/dy`,
both lab-frame derivatives of a lab-frame projected quantity. Describing the same computation as a
cylinder-axial `dB_z/dz` states something else, and the substitution passes unnoticed whenever `z` does
double duty for both axes.

The numerics can be correct throughout this failure. An independent from-scratch rebuild agrees with the
shipped code to round-off, and the claim remains uncheckable by inspection: a reader cannot tell which
derivative was reported. No numerical check catches this, because every number is right; only a reader
noticing the ambiguity does. Right code with unverifiable presentation is the failure mode this doc exists
to prevent.

## Pointers
`frame-problem` declares frames in the physics inventory, up front. `verify` runs the checklist above
before a cross-frame result is trusted. `dimensional-analysis` is the first cheap check on units and
frames, and shares the requirement that an unstated quantity is not checkable. A campaign's
`CONVENTIONS.md` pins the project's frame names, handedness, and active/passive plus degrees/radians
choices for the duration.
