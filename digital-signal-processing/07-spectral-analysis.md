---
id: 4cda8f0e-811d-438b-830a-cf4451d8bf4e
---

# Spectral Analysis

Spectral analysis is the careful work of finding out which frequencies are in a real signal, when you only have a short piece of it to look at. A short piece can blur or hide frequencies, so this lesson covers the fixes. Apps that name a song from a few seconds of audio, like Shazam, rely on this kind of analysis.

## The kid version first
<!-- bite: b695356d-d013-495f-8da3-0c770a9b74d9 -->

In theory the [[digital-signal-processing/04-the-fft|FFT]] hands you a signal's exact frequency content. In practice you only ever have a *finite chunk* of a signal, and that chunk lies to you in two specific ways: it smears sharp frequencies (**leakage**), and it forces a trade between knowing *what* frequencies are present and *when* (**the resolution trade**).

Spectral analysis is the craft of getting a trustworthy picture of a real signal's frequencies despite both.

## Leakage — the first problem
<!-- bite: 6fcc2a04-de4c-4b6d-80ec-c768b29249b1 -->

The FFT assumes your `N` samples are exactly one period of a signal that repeats forever. **They almost never are** — you grabbed an arbitrary window, so its start and end don't line up. That discontinuity, when the FFT imagines the chunk repeating, injects fake frequencies:

```text
   a clean tone, windowed at a non-integer number of cycles:
   the ends don't match → the FFT sees a "jump" → energy SMEARS
   across neighbouring bins instead of one clean spike
```

**Spectral leakage** is that smearing: a single true frequency spreads into a hump across many bins, burying weak nearby frequencies and making the spectrum look noisier than it is. **It's an artefact of the finite window, not the signal.**

## Windowing — the fix
<!-- bite: 5b27d427-7341-4223-ae12-779ffb56e91d -->

**A window function tapers the chunk smoothly to zero at both ends** before the FFT, so there's no discontinuity when it "repeats." Multiply your samples by a window, then transform:

```text
   samples × window  →  FFT
   (rectangular = no window = worst leakage)
```

| Window | Character |
|---|---|
| **Rectangular** (none) | Best frequency resolution, **worst leakage** |
| **Hann / Hamming** | The everyday default — good leakage suppression, mild resolution cost |
| **Blackman / Blackman–Harris** | Very low leakage, wider main lobe (worse resolution) |
| **Flat-top** | Poor resolution, but **accurate amplitude** — used for calibration |

**The universal trade:** every window suppresses leakage (lower side-lobes) at the cost of resolution (wider main lobe). **A better main-lobe/side-lobe trade is impossible to escape** — you're choosing *how* to spend it. **Use Hann by default**; reach for others only with a specific reason (Blackman for weak signals near strong ones, flat-top when you need the amplitude to be exact).

## The resolution/latency trade — the second problem
<!-- bite: 80754001-9b4c-48ea-815c-1533e89d86dc -->

Frequency resolution is `fs / N`: to distinguish two close frequencies you need a large `N`, which means a *long* time window. But a long window blurs *when* things happened. **You cannot have fine frequency resolution and fine time resolution at once.**

```text
   long window   → sharp frequencies, but "somewhere in this long span"
   short window  → precise timing, but blurry frequencies
```

**This is the time-frequency uncertainty principle** — the DSP sibling of Heisenberg's, and the same mathematics. It's not an engineering limitation you can design around; it's fundamental. Every spectral tool is a choice of where to sit on this trade.

## The spectrogram — seeing frequency change over time
<!-- bite: c6006810-0d5d-473d-bcc0-fc47fca05622 -->

A single FFT gives *one* spectrum for the whole chunk — useless for a signal whose content changes (speech, music, a bird call). The **Short-Time Fourier Transform (STFT)** fixes this: slide a window along the signal, FFT each position, and stack the results into a **spectrogram** — time on one axis, frequency on the other, colour for magnitude:

```text
   freq ▲  ████░░  ← a rising tone sweeps up over time
        │  ░░████
        └──────────► time
```

**The spectrogram is the workhorse visualisation of DSP** — it's how you *see* speech formants, music notes, a modem's tones, a machine's changing vibration. And the window length is exactly the resolution/latency trade made visible: a short window gives crisp timing and blurry pitch, a long window the reverse. **Speech analysis uses short windows (timing matters); tuning a note uses long ones (pitch matters).**

**Mel-spectrograms** — a spectrogram warped to the perceptual mel frequency scale — are the standard input to speech and audio ML models, which is a direct bridge from DSP to [[ai-ml/02-ml-engineer/07-sequence-models-and-nlp/index|audio ML]].

## Practical spectral analysis
<!-- bite: 7da95397-8cc9-4b25-97f4-c79157858973 -->

Turning an FFT into an honest spectrum:

1. **Window** (Hann, usually) before the FFT
2. **Zero-pad** if you want a smoother-looking spectrum — but understand it **interpolates**, it does not add real resolution (that needs more *actual* samples). A common misconception
3. **Average multiple windows** (Welch's method) to reduce noise variance in the estimate — trading some resolution for a cleaner, more reliable spectrum. The standard for estimating a noisy signal's power spectrum
4. **Convert to dB** (log scale) to see weak and strong components together — the ear and eye are logarithmic
5. **Label the axis correctly** — bin `k` = `k·fs/N` Hz

```python
from scipy import signal
f, t, Sxx = signal.spectrogram(x, fs, window='hann', nperseg=1024)
# f: frequencies, t: times, Sxx: power at each — plot as an image
```

## Key insight
<!-- bite: 142524a9-6082-4fda-867d-8300de64f860 -->

**A finite chunk of signal lies about its spectrum in two fixed ways — leakage (smearing from the window's edges) and the resolution/latency trade (you can't pin down frequency *and* time at once) — and spectral analysis is the craft of managing both.** Windowing (Hann by default) buys leakage suppression at a resolution cost you can't escape, and the spectrogram makes the time-frequency trade visible by sliding short FFTs along the signal. The uncertainty principle here isn't a limitation to engineer around; it's the terrain.

## Related
<!-- bite: df816757-1dc3-4285-b614-29f20c51098a -->
- [[digital-signal-processing/04-the-fft|the FFT]] — what spectral analysis runs on
- [[digital-signal-processing/02-sampling-and-aliasing|sampling]] — the other way a spectrum can mislead
- [[ai-ml/02-ml-engineer/07-sequence-models-and-nlp/index|sequence models]] — spectrograms as ML input
- [[information-theory/index|information theory]] — the uncertainty/entropy connections

## About this lesson
<!-- bite: 358cfd96-f7f5-4bf5-8d49-0429c67701e4 -->

**Level:** Advanced. **Covers:** using the FFT on real, finite, noisy data, and the two problems that separate a clean spectrum from a misleading one.

*Source: [reference] — Aug 2026.*
