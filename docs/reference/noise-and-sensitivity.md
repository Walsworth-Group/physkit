---
id: noise-and-sensitivity
kind: reference
layer: operating
load: on-demand
frozen: false
addresses: [5, 4, 2]
status: active
---

# Noise & sensitivity — know the floor before you burn the hours

Before you measure, know your noise. The a-priori question this reference answers: *what is the smallest
signal I can resolve in integration time T, and what limits it?* Characterizing the noise floor and the
sensitivity **before** spending instrument-hours is the a-priori-bound discipline (`dimensional-analysis`,
`frame-problem`) applied to measurement — it tells you whether the target precision is reachable **at all**,
and which noise source to attack first. This is the *a-priori* companion to `signal-extraction-pitfalls.md`
(which catches what goes wrong *after* the data exists).

## 1. Measure the noise floor — with the signal absent

The floor is what you read when there is no signal. Measure it directly (signal off / far-detuned / a
blank region) rather than inferring it, and keep it as a reference: every later "feature" is compared to
*this*. A statistic's behaviour on the floor is also the first of the two-question reflex
(`signal-extraction-pitfalls.md`). A signal you cannot separate from the floor is not a measurement yet.

## 2. Noise is a spectrum, not a number — the PSD

Characterize noise by its **power spectral density** vs frequency, not one RMS number. Real noise has
structure: a **white** plateau, a **1/f (flicker)** rise at low frequency, drift at the lowest frequencies,
and lines (mains harmonics, mechanical resonances). What matters is the PSD **in your measurement band** —
where your signal/encoding sits. Amplitude-spectral-density units (e.g. V/√Hz, T/√Hz) make sensitivity
fall out directly. Push the measurement band away from the 1/f corner and the lines (modulate/chop to a
quiet band) — often the single biggest a-priori win.

## 3. Fundamental vs technical noise — know which you're fighting

- **Fundamental** floors are set by physics and cannot be engineered away: **shot noise** (photon/particle
  counting), **spin-projection noise** (a spin sensor's quantum limit), **thermal / Johnson–Nyquist**
  noise. They set the best achievable.
- **Technical** noise sits above the floor: laser intensity/frequency noise, vibration, pickup/ground
  loops, temperature, drift. It *can* be engineered down.
- **The verdict you need first: which regime are you in?** Technical-limited → the win is engineering
  (shielding, stabilization, better references). Fundamental-limited → only more measurements, a better
  protocol, or a different modality helps. Chasing the wrong one wastes months.

## 4. Sensitivity — the figure of merit

**Sensitivity** = the smallest resolvable signal per unit bandwidth, e.g. a magnetometer's `η` in T/√Hz.
It is the noise floor referred to signal units:
`sensitivity = (noise ASD at the readout) / (responsivity)`, where **responsivity** is the calibrated
signal→readout transduction (§7). For white noise, the precision reached in time T is `sensitivity/√T`
(equivalently `η·√(bandwidth)`). Compute this **a priori** from the measured floor and the responsivity —
it is the ceiling your campaign is bounded by, and the number every proposed run should be checked against.

## 5. The √T law — and where it breaks

`precision ∝ 1/√T` holds **only while the noise is white**. 1/f noise flattens the gain and drift *reverses*
it at the **drift wall** `τ_opt` (diagnosed by the Allan deviation — home: `uncertainty-and-error-budgets.md`
§5). A sensitivity figure implicitly assumes "up to `τ_opt`": a target needing `T ≫ τ_opt` is **unreachable
by averaging alone** — know that before the run, not after the wasted night (`hardware-in-the-loop.md`).

## 6. Dynamic range, linearity, and resolution — three different limits

- The **noise floor** sets the bottom of the measurable range; **saturation / nonlinearity** sets the top;
  their ratio is the **dynamic range**.
- **Resolution** (the smallest representable step — ADC quantization, digitizer LSB) is *not* sensitivity
  (the smallest step distinguishable from noise). Confusing them over-promises: a 24-bit ADC does not give
  24-bit measurements if the noise floor is at bit 12.
- Check **linearity across the operating range** — a responsivity measured at one amplitude that sags at
  another is a systematic (`systematic-errors.md`).

## 7. Sensitivity is meaningless without a calibrated responsivity

To turn readout noise into a *signal-referred* sensitivity you need the transfer function — the calibrated
signal→readout gain. An "uncalibrated sensitivity" is just a noise number in the wrong units. Measure the
responsivity, track its drift, and propagate its uncertainty into the sensitivity (`calibration-and-drift.md`,
`uncertainty-and-error-budgets.md`).

## The a-priori reflex (before a long run)

1. **What is the expected sensitivity, and the time to reach target?** Compute it from the floor + the
   responsivity; if the target needs `T` beyond the drift wall, it is unreachable as-designed.
2. **Am I fundamental- or technical-limited?** — it decides whether to average, engineer, or redesign.

## Checklist

- [ ] Noise floor measured directly (signal absent), kept as the reference?
- [ ] Noise characterized as a PSD in the measurement band (not one RMS number)?
- [ ] Fundamental-vs-technical regime identified?
- [ ] Sensitivity computed a-priori from floor ÷ calibrated responsivity?
- [ ] `τ_opt` / drift wall respected (√T assumed only in the white regime)?
- [ ] Resolution not mistaken for sensitivity; linearity checked across the range?

## Composition

`signal-extraction-pitfalls.md` is the post-hoc twin (this is a-priori) · `uncertainty-and-error-budgets.md`
owns the Allan deviation / √T-and-drift-wall and the error budget this feeds · `dimensional-analysis` /
`frame-problem` for the a-priori bound · `calibration-and-drift.md` supplies the responsivity ·
`systematic-errors.md` for nonlinearity/technical-noise systematics · `hardware-in-the-loop.md` for the
SNR-limited averaging economics.

## Sources *(Allan cite-checked 2026-07-03; confirm phenomenon-origin citations at paper time)*

Standard noise/sensitivity methodology — nothing novel here. The named noise limits (**Johnson–Nyquist**
thermal noise; **shot noise**; **spin-projection noise** for spin sensors) are textbook phenomena — cite
their original sources at paper time (not yet verified here). The **Allan deviation** is Allan (*Proc. IEEE*
**54**, 1966, 221–230). Run `cite-check` on every attribution before the paper cites it.
