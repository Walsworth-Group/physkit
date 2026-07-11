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

Attribution, fitting, and discovery all start downstream of an extraction step — a window, a baseline, an
FFT, a peak-pick. Each pitfall below manufactured a convincing fake signature (or buried a real one) in
real lab data before becoming a rule. The common thread: **the extraction chain is a candidate mechanism
for every feature it reports** (see `attribute-mechanism`, rule "the null candidate is always on the
list").

## 1. Detrend before you FFT — demeaning is not enough

A slow trend across a record (envelope growth, drift, decay) puts spectral weight into the lowest non-DC
bins, where it reads as a clean low-frequency "oscillation." Subtracting the mean does NOT remove it —
fit and subtract (at least) a linear trend, or use a proper detrend, before interpreting any
low-frequency peak. *Origin: a convincing "N-point periodic modulation" in an echo-amplitude series that
was nothing but the noise floor's slow growth leaking through a demean-only pipeline.*

## 2. A fixed-bin peak tracks the noise floor once the signal dies

Extracting "the peak amplitude in a fixed window" silently changes meaning when the signal decays below
the noise: from that point on the statistic reports the maximum of noise, which has its own smooth,
plausible-looking trend (it grows with window width, drifts with the floor). **Cross-check any windowed
statistic at a signal-free location** — same window width, offset to where no signal can be. If the
"signal" and the blank track each other, you are measuring the noise floor. *Origin: late-record
amplitudes in a decaying train that looked like a revival and were the noise maximum.*

## 3. Trust the tuned pipeline over a naive re-extraction

A production analysis chain (phasing, window placement, baseline handling tuned for the instrument's
regime) embodies calibration you will not reproduce in a quick script. When a quick re-extraction
disagrees with the tuned pipeline, the burden of proof is on the quick script — diff the intermediate
steps before believing the discrepancy, and use the tuned chain as ground truth for regime questions
(does the signal grow, decay, oscillate?). The converse discipline once the pipeline IS the question:
change it only versioned (`metric_version`-style), never silently.

## 4. Incoherent averaging destroys what coherent averaging measures

Averaging magnitudes (`mean(|x|)`) rectifies noise into a positive bias and forfeits the √N gain;
averaging complex/signed records first and taking the magnitude last (`|mean(x)|`) is a different
measurement, not a stylistic choice. Low-SNR quantities (per-shot spectra, per-record peaks) computed
incoherently can gate real data out or fake a floor. *Origin: a signal-quality gate computed on an
incoherent sum rejected clean records at exactly the moment averaging would have revealed them — the
gate, not the signal, was broken.*

## 5. Peak-picking at low SNR returns the largest noise excursion

An argmax over a search band at per-record SNR ≲ a few returns noise, scattered across the whole band —
downstream "drift tracks," alignment shifts, or frequency scatter derived from it are artifacts of the
picker. Either raise the SNR before picking (coherent co-add, §4), constrain the search band to a
physically-motivated window, or propagate the pick's confidence and refuse to act on low-confidence
picks. *Origin: an apparent large shot-to-shot frequency scatter that vanished when the peak was picked
on the co-added record instead of per-shot.*

## The two-question reflex

Before promoting any extracted feature to "observed signature," answer both:
1. **What does this statistic report when there is NO signal?** (Run it on a blank region, a scrambled
   record, or pure noise — the null control from `metric.py --selftest` thinking, applied to analysis.)
2. **Does an independent extraction path agree?** (Different window/method/tooling — mechanism-diverse,
   like all verification in this kit.)

If either answer is unknown, the feature is INCONCLUSIVE — an extraction property, not yet a physical
observation.
