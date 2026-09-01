# Spectral Analysis

**[Advanced]** — using the FFT on real, finite, noisy data, and the two problems that separate a clean spectrum from a misleading one.

## The kid version first

In theory the [[foundations/digital-signal-processing/04-the-fft|FFT]] hands you a signal's exact frequency content. In practice you only ever have a *finite chunk* of a signal, and that chunk lies to you in two specific ways: it smears sharp frequencies (**leakage**), and it forces a trade between knowing *what* frequencies are present and *when* (**the resolution trade**).

Spectral analysis is the craft of getting a trustworthy picture of a real signal's frequencies despite both.

## Leakage — the first problem

The FFT assumes your `N` samples are exactly one period of a signal that repeats forever. **They almost never are** — you grabbed an arbitrary window, so its start and end don't line up. That discontinuity, when the FFT imagines the chunk repeating, injects fake frequencies:

```
   a clean tone, windowed at a non-integer number of cycles:
   the ends don't match → the FFT sees a "jump" → energy SMEARS
   across neighbouring bins instead of one clean spike
```

**Spectral leakage** is that smearing: a single true frequency spreads into a hump across many bins, burying weak nearby frequencies and making the spectrum look noisier than it is. **It's an artefact of the finite window, not the signal.**

## Windowing — the fix

**A window function tapers the chunk smoothly to zero at both ends** before the FFT, so there's no discontinuity when it "repeats." Multiply your samples by a window, then transform:

```
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

Frequency resolution is `fs / N`: to distinguish two close frequencies you need a large `N`, which means a *long* time window. But a long window blurs *when* things happened. **You cannot have fine frequency resolution and fine time resolution at once.**

```
   long window   → sharp frequencies, but "somewhere in this long span"
   short window  → precise timing, but blurry frequencies
```

**This is the time-frequency uncertainty principle** — the DSP sibling of Heisenberg's, and the same mathematics. It's not an engineering limitation you can design around; it's fundamental. Every spectral tool is a choice of where to sit on this trade.

## The spectrogram — seeing frequency change over time

A single FFT gives *one* spectrum for the whole chunk — useless for a signal whose content changes (speech, music, a bird call). The **Short-Time Fourier Transform (STFT)** fixes this: slide a window along the signal, FFT each position, and stack the results into a **spectrogram** — time on one axis, frequency on the other, colour for magnitude:

```
   freq ▲  ████░░  ← a rising tone sweeps up over time
        │  ░░████
        └──────────► time
```

**The spectrogram is the workhorse visualisation of DSP** — it's how you *see* speech formants, music notes, a modem's tones, a machine's changing vibration. And the window length is exactly the resolution/latency trade made visible: a short window gives crisp timing and blurry pitch, a long window the reverse. **Speech analysis uses short windows (timing matters); tuning a note uses long ones (pitch matters).**

**Mel-spectrograms** — a spectrogram warped to the perceptual mel frequency scale — are the standard input to speech and audio ML models, which is a direct bridge from DSP to [[ai-ml/02-ml-engineer/07-sequence-models-and-nlp/README|audio ML]].

## Practical spectral analysis

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

**A finite chunk of signal lies about its spectrum in two fixed ways — leakage (smearing from the window's edges) and the resolution/latency trade (you can't pin down frequency *and* time at once) — and spectral analysis is the craft of managing both.** Windowing (Hann by default) buys leakage suppression at a resolution cost you can't escape, and the spectrogram makes the time-frequency trade visible by sliding short FFTs along the signal. The uncertainty principle here isn't a limitation to engineer around; it's the terrain.

## Related
- [[foundations/digital-signal-processing/04-the-fft|the FFT]] — what spectral analysis runs on
- [[foundations/digital-signal-processing/02-sampling-and-aliasing|sampling]] — the other way a spectrum can mislead
- [[ai-ml/02-ml-engineer/07-sequence-models-and-nlp/README|sequence models]] — spectrograms as ML input
- [[foundations/information-theory/README|information theory]] — the uncertainty/entropy connections

*Source: [reference] — Aug 2026.*
