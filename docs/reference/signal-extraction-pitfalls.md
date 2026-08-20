---
id: signal-extraction-pitfalls
kind: reference
layer: operating
load: on-demand
frozen: false
addresses: [2, 4, 5]
status: active
---

# Signal-extraction pitfalls — before you trust a feature, distrust the extraction

Attribution, fitting, and discovery all start downstream of an extraction step: a window, a baseline, an
FFT, a peak-pick. Each pitfall below manufactures a false signature, or buries a real one, while the
underlying physics is unchanged. The extraction chain is a candidate mechanism for every feature it
reports (see `attribute-mechanism`, rule "the null candidate is always on the list").

## 1. Detrend before you FFT — demeaning is not enough

A slow trend across a record (envelope growth, drift, decay) puts spectral weight into the lowest non-DC
bins, where it reads as a clean low-frequency oscillation. Subtracting the mean does not remove it. Fit
and subtract at least a linear trend, or use a proper detrend, before interpreting any low-frequency
peak. A demean-only pipeline reports slow growth of the noise floor as a periodic modulation of the
extracted amplitude series.

## 2. A fixed-bin peak tracks the noise floor once the signal dies

Extracting "the peak amplitude in a fixed window" silently changes meaning when the signal decays below
the noise: from that point on the statistic reports the maximum of noise, which has its own smooth,
plausible-looking trend (it grows with window width, drifts with the floor). Cross-check any windowed
statistic at a signal-free location, at the same window width, offset to where no signal can be. If the
candidate feature and the blank track each other, the statistic is measuring the noise floor. Late-record
amplitudes in a decaying train read as a revival under this failure.

## 3. Trust the tuned pipeline over a naive re-extraction

A production analysis chain (phasing, window placement, baseline handling tuned for the instrument's
regime) embodies calibration a quick script does not reproduce. When a quick re-extraction disagrees with
the tuned pipeline, the burden of proof is on the quick script: diff the intermediate steps before
believing the discrepancy, and use the tuned chain as ground truth for regime questions (does the signal
grow, decay, oscillate?). The converse discipline applies once the pipeline is the question: change it
only versioned (`metric_version`-style), never silently.

## 4. Incoherent averaging destroys what coherent averaging measures

Averaging magnitudes (`mean(|x|)`) rectifies noise into a positive bias and forfeits the √N gain.
Averaging complex/signed records first and taking the magnitude last (`|mean(x)|`) is a different
measurement, not a stylistic choice. Low-SNR quantities (per-shot spectra, per-record peaks) computed
incoherently can gate real data out or fake a floor. A signal-quality gate computed on an incoherent sum
rejects clean records that coherent averaging would have recovered: the gate fails, not the signal.

## 5. Peak-picking at low SNR returns the largest noise excursion

An argmax over a search band at per-record SNR ≲ a few returns noise, scattered across the whole band.
Downstream drift tracks, alignment shifts, or frequency scatter derived from it are artifacts of the
picker. Either raise the SNR before picking (coherent co-add, §4), constrain the search band to a
physically-motivated window, or propagate the pick's confidence and refuse to act on low-confidence
picks. Shot-to-shot frequency scatter produced this way disappears when the peak is picked on the
co-added record instead of per-shot.

## The two-question reflex

Before promoting any extracted feature to "observed signature," answer both:
1. What does this statistic report when there is no signal? Run it on a blank region, a scrambled record,
   or pure noise: the null control of `metric.py --selftest`, applied to analysis.
2. Does an independent extraction path agree? Use a different window, method, or tooling; the check must
   be mechanism-diverse.

If either answer is unknown, the feature is INCONCLUSIVE: an extraction property, not yet a physical
observation.
