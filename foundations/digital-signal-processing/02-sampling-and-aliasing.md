# Sampling and Aliasing

**[Beginner → Intermediate]** — the bridge from the continuous world to the discrete one, and the theorem that says exactly how fast you must measure.

## The kid version first

To get a real-world signal into a computer, you measure it repeatedly — a snapshot every so often. **Sampling is taking those snapshots**; each one becomes a number.

The critical question: how *often* must you snapshot to capture the signal faithfully? Too slow, and you don't just lose detail — you get **a completely wrong signal** that looks real. That failure has a name (aliasing), a cause, and a precise rule that prevents it.

## Sampling

An **analog-to-digital converter (ADC)** measures the continuous signal `x(t)` at regular intervals, producing the sequence `x[n] = x(nT)`, where:

- `T` = the sampling period (seconds between samples)
- `fs = 1/T` = the **sampling rate** (samples per second, Hz)

A **digital-to-analog converter (DAC)** does the reverse: turns the number sequence back into a continuous signal for a speaker or antenna.

```
   x(t)  ──►  [ ADC ]  ──►  x[n]  ──►  [ DSP ]  ──►  y[n]  ──►  [ DAC ]  ──►  y(t)
  analog      sample        digital    process       digital    reconstruct   analog
```

**Everything between the two converters is DSP.**

## The Nyquist–Shannon sampling theorem

The foundational result of the whole field, and it's exact, not a rule of thumb:

> **To capture a signal perfectly, you must sample at more than *twice* its highest frequency.** `fs > 2·f_max`.

The value `f_max` (half the sampling rate, `fs/2`) is the **Nyquist frequency** — the highest frequency you can represent at a given sample rate.

**Why "twice"?** A sinusoid needs at least two samples per cycle to have its frequency unambiguously determined — one for a peak-ish and one for a trough-ish. Fewer than two, and the samples fit *multiple* different sinusoids, so the frequency is ambiguous, and the reconstruction picks the wrong one.

**The remarkable part:** if you obey it, reconstruction is **perfect** — the discrete samples contain *all* the information in the original continuous signal. Nothing is lost. This is deeply counterintuitive (a finite set of snapshots fully determines a continuous wave) and it's why digital audio can be indistinguishable from analog → [[foundations/information-theory/01-what-information-is|information]].

## Aliasing — what goes wrong

If a signal contains frequencies above `fs/2`, sampling doesn't just miss them — **it folds them back down and disguises them as lower frequencies that were never there.**

```
   true signal: 900 Hz, sampled at 1000 Hz (Nyquist = 500 Hz)
   → appears as a 100 Hz signal.  A frequency you cannot distinguish
     from a real 100 Hz tone. The information is not lost — it's CORRUPTED.
```

**The classic visual is the wagon-wheel effect** — a spinning wheel filmed at 24 fps appears to slow, stop, or rotate *backward* when its spokes move more than half a frame's worth per frame. The camera is undersampling the rotation; the aliased frequency looks real. Same maths, exactly.

**Why aliasing is worse than simple loss:** a low-pass loss just makes things dull. Aliasing *adds phantom content indistinguishable from genuine signal* — and once folded in, **it cannot be removed**, because there's no way to tell the alias from a real tone at that frequency.

## The anti-aliasing filter — mandatory, and it comes first

Since aliasing is irreversible, **you must remove frequencies above `fs/2` *before* sampling**, with an analog **anti-aliasing filter** — a low-pass filter in front of the ADC:

```
   x(t) ──► [ analog low-pass, cutoff < fs/2 ] ──► [ ADC ] ──► x[n]
              removes what would alias, while it still can
```

**This is a hardware step that cannot be skipped or done later**, because once the ADC has sampled, the aliased frequencies are already indistinguishable from real ones. It's why real ADC front-ends always include one → [[foundations/digital-signal-processing/06-digital-filters|filters]].

## Why the standard rates are what they are

- **44.1 kHz** (CD audio) — human hearing tops out around 20 kHz, so `2 × 20 = 40 kHz` is the minimum; the extra ~4 kHz is guard band for a realisable anti-aliasing filter (real filters can't cut infinitely sharply at exactly 20 kHz)
- **48 kHz** — professional/video audio, same logic
- **8 kHz** — telephone; speech intelligibility lives below 4 kHz, so 8 kHz suffices and saves bandwidth

**Every standard sample rate is "just over twice the highest frequency we care about, plus room for the filter."**

## Quantisation — the other approximation

Sampling discretises *time*; **quantisation discretises *amplitude*.** The ADC can only output one of a finite set of values (16 bits = 65,536 levels for CD audio), so each sample is rounded to the nearest level.

- **The rounding error is quantisation noise.** More bits = finer levels = less noise. Each bit adds ~6 dB of dynamic range, so 16-bit gives ~96 dB — beyond most listening environments
- **Unlike aliasing, quantisation noise is benign** — it's just a small random error floor, not phantom frequencies. You reduce it with more bits, and **dithering** (adding tiny deliberate noise before quantising) trades a slightly higher noise floor for removing audible distortion patterns

**Two independent approximations:** sampling (time) governed by Nyquist, quantisation (amplitude) governed by bit depth. A digital signal is discrete in both.

## Key insight

**Sampling perfectly captures a continuous signal *if and only if* you sample at more than twice its highest frequency — and if you don't, the excess frequencies don't vanish, they fold down and masquerade as lower ones you can never remove.** That irreversibility is why the anti-aliasing filter is a mandatory analog step *before* the ADC, and why every sample rate you've ever seen is "just over twice the top frequency of interest." Nyquist for time, bit depth for amplitude — those two numbers define a digital signal.

## Related
- [[foundations/digital-signal-processing/03-the-frequency-domain|the frequency domain]] — "highest frequency" only means something in the frequency domain
- [[foundations/digital-signal-processing/07-spectral-analysis|spectral analysis]] — seeing aliasing in a spectrum
- [[foundations/information-theory/01-what-information-is|information theory]] — sampling as an information bound
- [[hardware/02-digital-and-analog|digital and analog]] — the ADC/DAC hardware

*Source: [reference] — Aug 2026.*
