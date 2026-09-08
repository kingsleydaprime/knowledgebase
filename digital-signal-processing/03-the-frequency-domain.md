# The Frequency Domain

**[Intermediate]** — the central idea of DSP: any signal is a sum of sinusoids, and switching to that view makes hard problems easy.

## The kid version first

A musical chord looks like a single messy wiggle on an oscilloscope. But your ear hears **three distinct notes** — it takes that one wiggle apart into its constituent pure tones.

**The frequency domain is doing exactly that, mathematically:** taking any signal and finding *which pure sinusoids, at which strengths, add up to make it.* The wiggle over time (the **time domain**) and the list of frequencies it contains (the **frequency domain**) are two views of the *same* signal — and some problems are trivial in one view and impossible in the other.

## The big idea

> **Any signal can be written as a sum of sinusoids of different frequencies, amplitudes and phases.**

This is **Fourier's theorem**, and it's one of the most consequential ideas in all of applied mathematics. A square wave, a spoken word, an image, a stock chart — each is a combination of pure sine waves, and Fourier analysis finds the recipe.

```
   TIME DOMAIN                    FREQUENCY DOMAIN
   "how the signal            "which frequencies it
    changes over time"         is made of, and how much"

   a messy wiggle      ◄──►     a few spikes: 100Hz strong,
                                 250Hz medium, 3kHz faint
```

**Neither view is more "real."** They contain identical information — the transform is reversible, losing nothing. You switch to whichever makes your problem easier, which is the whole trick.

## Why the frequency view is so powerful

Three things become obvious in the frequency domain that are hard in the time domain:

**1. Filtering becomes selection.** "Remove the hum" is hopeless to express as time-domain arithmetic, but in the frequency domain it's "delete the spike at 50 Hz." Noise, hum, and unwanted bands are *visible and separable* → [[foundations/digital-signal-processing/06-digital-filters|filters]].

**2. LTI systems become multiplication.** An [[foundations/digital-signal-processing/01-signals-and-systems|LTI system]] applies a gain and phase shift *per frequency* — so its effect is just multiplying the input's spectrum by the system's frequency response. The messy time-domain operation ([[foundations/digital-signal-processing/05-convolution-and-lti-systems|convolution]]) becomes simple multiplication. **This is the single biggest reason the frequency domain matters.**

**3. Structure appears.** A heartbeat's rhythm, a rotating machine's vibration signature, the pitch of a voice — periodic structure that's buried in the time wiggle shows up as clear peaks in the spectrum.

## The Fourier family

There are four Fourier transforms, and the differences are just "is the signal periodic/aperiodic, continuous/discrete." You mostly use the last one, but the family clarifies which is which:

| | Time signal | Result |
|---|---|---|
| **Fourier Series** | Continuous, **periodic** | Discrete frequencies (harmonics) |
| **Fourier Transform (FT)** | Continuous, aperiodic | Continuous spectrum |
| **Discrete-Time FT (DTFT)** | Discrete, aperiodic | Continuous, periodic spectrum |
| **Discrete Fourier Transform (DFT)** | **Discrete, finite** | **Discrete, finite** — the one computers use |

**The DFT is the practical one** — it takes `N` samples in and gives `N` frequency values out, all discrete and finite, so a computer can actually compute it. Everything a program does is a DFT (usually via its fast algorithm, the [[foundations/digital-signal-processing/04-the-fft|FFT]]).

## Reading a DFT output

The DFT of `N` samples gives `N` complex numbers, one per **frequency bin**. Each complex number encodes two things:

- **Magnitude** — how much of that frequency is present (the amplitude). This is what a spectrum plot shows
- **Phase** — the timing/alignment of that frequency component. Often ignored in visualisation, but **essential** — throw away phase and you can't reconstruct the signal, and it's why two signals with identical spectra can sound or look different

The bins span from 0 (DC, the average) up to the [[foundations/digital-signal-processing/02-sampling-and-aliasing|Nyquist frequency]] `fs/2`. For real signals the upper half mirrors the lower (conjugate symmetry), so you usually plot only the first `N/2` bins.

**Frequency resolution** = `fs / N`: more samples → finer bins → you can distinguish closer frequencies. This is a fundamental trade — capturing more time gives better frequency resolution, which is the seed of the [[foundations/digital-signal-processing/07-spectral-analysis|time-frequency uncertainty]].

## Why complex numbers?

DSP is full of `e^{jω}` and complex spectra, which can feel like unnecessary abstraction. The reason is clean: **a complex exponential `e^{jωt}` is a rotating point** — it encodes both a cosine (real part) and a sine (imaginary part) at once, and rotation is the natural language of oscillation → [[foundations/discrete-math/README|the maths]].

Practically, the two numbers per frequency (real/imaginary, or magnitude/phase) *are* amplitude-and-timing. Complex numbers aren't a complication bolted on; they're the compact, correct way to carry "how much *and* when" for each frequency. Euler's formula `e^{jθ} = cos θ + j·sin θ` is the bridge.

## Key insight

**The frequency domain is the same signal seen as "which sinusoids it's made of," and switching to that view is powerful because filtering becomes selection and LTI processing becomes multiplication.** Fourier's theorem — any signal is a sum of sinusoids — is what lets you move between the two views losslessly, and the DFT is the finite, discrete version a computer can actually run. Once you're comfortable that a signal *is* its spectrum, half of DSP becomes "do the easy thing in whichever domain it's easy in."

## Related
- [[foundations/digital-signal-processing/04-the-fft|the FFT]] — the algorithm that computes the DFT fast enough to matter
- [[foundations/digital-signal-processing/05-convolution-and-lti-systems|convolution]] — why "convolution in time = multiplication in frequency"
- [[foundations/digital-signal-processing/07-spectral-analysis|spectral analysis]] — the DFT applied to real, noisy, finite data
- [[foundations/numerical-methods/06-interpolation-and-approximation|approximation]] — Fourier as a basis expansion

*Source: [reference] — Aug 2026.*
