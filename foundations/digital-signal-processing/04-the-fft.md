# The FFT

**[Intermediate]** — the algorithm that made the frequency domain practical, and one of the most important algorithms ever written.

## The kid version first

Computing a signal's frequency content ([[foundations/digital-signal-processing/03-the-frequency-domain|the DFT]]) the direct way is *slow* — for a big signal, impossibly slow. The **Fast Fourier Transform** is a clever shortcut that gets the identical answer in a tiny fraction of the work.

It's not an approximation and it's not a different transform — **it's the exact same DFT, computed cleverly instead of naively.** And the speed-up is so enormous that it's the difference between the frequency domain being a textbook idea and being in every phone, radio and audio app on earth.

## The problem it solves

The DFT computes `N` frequency bins from `N` samples. Done directly, each bin is a sum over all `N` samples, so it's **N × N = O(N²)** operations:

```
   N = 1,000      → ~1,000,000 operations        (fine)
   N = 1,000,000  → ~1,000,000,000,000 ops       (a trillion — hopeless in real time)
```

**O(N²) makes the DFT unusable for anything large.** A one-second audio clip at 44.1 kHz is 44,100 samples; processing audio in real time with an O(N²) DFT is a non-starter → [[foundations/dsa/README|complexity]].

## What the FFT does

The FFT computes the same DFT in **O(N log N)**:

```
   N = 1,000,000  →  ~20,000,000 operations   (vs a trillion)
                     roughly a 50,000× speed-up
```

**The core trick (Cooley–Tukey, 1965) is divide-and-conquer:** a DFT of size `N` can be built from two DFTs of size `N/2` — split the samples into even-indexed and odd-indexed halves, transform each half, then combine. Recurse, and the work collapses from N² to N·log N.

```
   DFT(N)  =  combine( DFT(N/2 of evens),  DFT(N/2 of odds) )
                          ↓ recurse                ↓ recurse
```

The combine step (the "butterfly") reuses shared computations that the naive DFT redundantly repeats — **that reuse is where the saving comes from** → [[foundations/dsa/05-algorithms/01-algorithms|divide and conquer]].

**It works best when `N` is a power of 2** (the halving is clean). Libraries handle other sizes, but they may pad to a power of 2, which is why you'll see FFT lengths of 1024, 2048, 4096.

## Why it's one of the most important algorithms ever

The FFT is regularly listed among the most influential algorithms of the 20th century, and the claim is fair:

- **It made real-time DSP possible.** Every digital radio, phone, Wi-Fi chip, and audio effect relies on being able to move to the frequency domain *fast*. Without O(N log N), none of it works in real time
- **It made convolution fast.** The [[foundations/digital-signal-processing/05-convolution-and-lti-systems|convolution theorem]] says convolution = multiply-in-frequency, so **FFT → multiply → inverse-FFT** turns an O(N²) convolution into O(N log N). Large filters and correlations depend on this
- **It underpins compression.** JPEG and MP3 transform to a frequency-like domain (DCT, a Fourier relative) and discard imperceptible components — that transform is FFT-family maths
- **It's everywhere in science** — spectroscopy, radio astronomy, MRI reconstruction, seismology all live on the FFT

**A nice historical note:** Cooley and Tukey published it in 1965 partly to detect Soviet nuclear tests from seismic data — but Gauss had worked out the same idea around 1805, unpublished. It was independently reinvented and only became world-changing once computers existed to run it at scale.

## Using it

You essentially never implement an FFT — you call a highly-optimised library. But you must understand its output and its parameters:

```python
import numpy as np
X = np.fft.rfft(signal)              # real-input FFT → complex spectrum
freqs = np.fft.rfftfreq(len(signal), d=1/fs)   # the frequency of each bin
magnitude = np.abs(X)                # amplitude per frequency
phase = np.angle(X)                  # timing per frequency
```

- **`rfft`** for real signals (audio, sensors) — it exploits the symmetry to compute only the meaningful half, twice as fast as the full complex FFT
- **FFTW** ("Fastest Fourier Transform in the West") is the gold-standard C library; NumPy/SciPy, MATLAB and hardware DSP chips all use FFT implementations under the hood
- **Bin `k` corresponds to frequency `k · fs / N`** — you need the sample rate and length to label the axis, which `rfftfreq` does for you

## The practical gotchas

Two things bite everyone, and both get their own treatment in [[foundations/digital-signal-processing/07-spectral-analysis|spectral analysis]]:

- **Spectral leakage** — the FFT assumes your `N` samples are one period of a signal that repeats forever. If they aren't (they usually aren't), energy "leaks" across bins, smearing sharp peaks. **Windowing** mitigates it
- **The resolution/latency trade** — a longer FFT gives finer frequency bins but needs more samples, so it captures a longer time window and adds latency. You can't have fine frequency resolution *and* fine time resolution at once — the FFT's version of an uncertainty principle

## Key insight

**The FFT computes the exact same DFT as the naive method but in O(N log N) instead of O(N²), via divide-and-conquer, and that single speed-up is what moved the frequency domain from theory into every real-time system on the planet.** You'll never write one, but you must read its output (complex bins = magnitude and phase, bin `k` = frequency `k·fs/N`) and respect its two gotchas — leakage and the resolution/latency trade — because those are where practical spectral analysis lives.

## Related
- [[foundations/digital-signal-processing/03-the-frequency-domain|the frequency domain]] — the DFT the FFT computes
- [[foundations/digital-signal-processing/05-convolution-and-lti-systems|convolution]] — made fast by the FFT
- [[foundations/digital-signal-processing/07-spectral-analysis|spectral analysis]] — leakage, windowing, the resolution trade
- [[foundations/dsa/05-algorithms/01-algorithms|algorithms]] — divide and conquer, and O(N log N)

*Source: [reference] — Aug 2026.*
