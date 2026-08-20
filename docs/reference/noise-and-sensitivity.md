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

This reference answers one a-priori question: what is the smallest signal resolvable in integration time
T, and what limits it? Characterize the noise floor and the sensitivity before spending instrument-hours.
This is the a-priori-bound discipline (`dimensional-analysis`, `frame-problem`) applied to measurement: it
establishes whether the target precision is reachable at all, and which noise source to attack first.
`signal-extraction-pitfalls.md` is the post-hoc companion, for what goes wrong once the data exists.

## 1. Measure the noise floor — with the signal absent

The floor is the reading when no signal is present. Measure it directly, with the signal off, far-detuned,
or in a blank region; do not infer it. Keep it as the reference against which every later feature is
compared. How a statistic behaves on the floor is the first of the two-question reflex
(`signal-extraction-pitfalls.md`). A signal that cannot be separated from the floor is not a measurement.

## 2. Noise is a spectrum, not a number — the PSD

Characterize noise by its **power spectral density** against frequency, not by one RMS number. Real noise
has structure: a **white** plateau, a **1/f (flicker)** rise at low frequency, drift at the lowest
frequencies, and lines (mains harmonics, mechanical resonances). What matters is the PSD in the
measurement band, where the signal sits. Amplitude-spectral-density units (V/√Hz, T/√Hz) give the
sensitivity directly. Push the measurement band away from the 1/f corner and the lines by modulating or
chopping into a quiet band; this is often the largest a-priori gain available.

## 3. Fundamental vs technical noise — know which you're fighting

- **Fundamental** floors are set by physics and cannot be engineered away: **shot noise** (photon/particle
  counting), **spin-projection noise** (a spin sensor's quantum limit), **thermal / Johnson–Nyquist**
  noise. They set the best achievable.
- **Technical** noise sits above the floor: laser intensity/frequency noise, vibration, pickup/ground
  loops, temperature, drift. It can be engineered down.
- Identify the regime first. Technical-limited: the gain is engineering (shielding, stabilization, better
  references). Fundamental-limited: only more measurements, a better protocol, or a different modality
  helps. Effort spent on the wrong regime does not lower the floor.

## 4. Sensitivity — the figure of merit

**Sensitivity** is the smallest resolvable signal per unit bandwidth: a magnetometer's `η` in T/√Hz. It is
the noise floor referred to signal units:
`sensitivity = (noise ASD at the readout) / (responsivity)`, where **responsivity** is the calibrated
signal→readout transduction (§7). For white noise, the precision reached in time T is `sensitivity/√T`,
equivalently `η·√(bandwidth)`. Compute the sensitivity a priori from the measured floor and the
responsivity. It bounds what the campaign can reach; check every proposed run against it.

## 5. The √T law — and where it breaks

`precision ∝ 1/√T` holds only while the noise is white. 1/f noise flattens the gain, and drift reverses it
at the **drift wall** `τ_opt`. The Allan deviation diagnoses the wall; `uncertainty-and-error-budgets.md`
§5 owns that method. A sensitivity figure implicitly assumes averaging only up to `τ_opt`. A target
requiring `T ≫ τ_opt` is unreachable by averaging alone. Establish `τ_opt` before committing instrument
time, not after (`hardware-in-the-loop.md`).

## 6. Dynamic range, linearity, and resolution — three different limits

- The **noise floor** sets the bottom of the measurable range; **saturation / nonlinearity** sets the top;
  their ratio is the **dynamic range**.
- **Resolution** is the smallest representable step (ADC quantization, digitizer LSB). It is not
  sensitivity, the smallest step distinguishable from noise. Conflating them over-promises: a 24-bit ADC
  does not give 24-bit measurements when the noise floor sits at bit 12.
- Check linearity across the operating range. A responsivity measured at one amplitude that sags at
  another is a systematic (`systematic-errors.md`).

## 7. Sensitivity is meaningless without a calibrated responsivity

A signal-referred sensitivity requires the transfer function: the calibrated signal→readout gain. An
uncalibrated sensitivity is a noise number in the wrong units. Measure the responsivity, track its drift,
and propagate its uncertainty into the sensitivity (`calibration-and-drift.md`,
`uncertainty-and-error-budgets.md`).

## The a-priori reflex (before a long run)

1. **Expected sensitivity, and time to reach target.** Compute both from the floor and the responsivity.
   If the target needs `T` beyond the drift wall, it is unreachable as designed.
2. **Fundamental- or technical-limited.** The answer decides whether to average, engineer, or redesign.

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

## Sources

Standard noise and sensitivity methodology; nothing here is novel. The named noise limits (Johnson–Nyquist
thermal noise, shot noise, spin-projection noise for spin sensors) are textbook phenomena; their original
sources are not verified here. Cite them at paper time. The Allan deviation is Allan (*Proc. IEEE* **54**,
1966, 221–230). Run `cite-check` on every attribution before the paper cites it.
