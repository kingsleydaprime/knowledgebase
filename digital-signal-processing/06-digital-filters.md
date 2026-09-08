# Digital Filters

**[Advanced]** — the most common thing DSP is *used* for: reshaping a signal's frequency content, and the two families that do it.

## The kid version first

A filter passes some frequencies and blocks others. A bass boost, a hum remover, a noise cleaner, the tone controls on a stereo — all filters. **A digital filter does this with arithmetic on the samples**: each output is a weighted combination of recent input (and sometimes output) samples.

The weights *are* the filter. Choosing them so the filter passes what you want and blocks what you don't is **filter design**, and the two ways of structuring the arithmetic give the two great families: FIR and IIR.

## What a filter is

By type of what it passes:

```
   low-pass    ▔▔▔╲___     keep low frequencies, cut high   (smoothing, anti-alias)
   high-pass   ___╱▔▔▔     keep high, cut low               (remove drift/DC)
   band-pass   __╱▔╲__     keep a band                      (isolate a channel)
   band-stop   ▔▔╲_╱▔▔     cut a band (notch)               (kill 50/60Hz hum)
```

The **cutoff frequency** is where it transitions; the **transition band** is how sharply (a real filter can't cut instantly); the **passband** and **stopband** are what it keeps and rejects. A filter is fundamentally a [[foundations/digital-signal-processing/05-convolution-and-lti-systems|frequency response `H(f)`]] — a gain to apply at each frequency — and applying it is [[foundations/digital-signal-processing/05-convolution-and-lti-systems|convolution]] with its impulse response.

## FIR — Finite Impulse Response

The output is a weighted sum of *input* samples only:

```
y[n] = b₀·x[n] + b₁·x[n−1] + ... + bₘ·x[n−M]
```

The impulse response is finite (`M+1` taps, then it stops) — it's literally the list of `b` coefficients. **This is just convolution with a fixed kernel.**

**Properties, and they're the reason FIR is often preferred:**
- **Always stable** — no feedback, so it can't blow up. One less thing to get wrong
- **Linear phase achievable** — with symmetric coefficients, every frequency is delayed by the *same* amount, so the waveform shape is preserved (no phase distortion). **Essential for audio and for anything where the shape matters** (ECG, data)
- **The cost:** to cut sharply you need many taps (long kernel = more computation and more latency)

**Design methods:** the window method (take the ideal response, truncate it with a [[foundations/digital-signal-processing/07-spectral-analysis|window]]), or Parks–McClellan for optimal equiripple designs. In practice, `scipy.signal.firwin`.

## IIR — Infinite Impulse Response

The output feeds back on itself — it depends on past *outputs* as well as inputs:

```
y[n] = b₀·x[n] + ... − a₁·y[n−1] − a₂·y[n−2] − ...
                        ↑ feedback: past OUTPUTS
```

The feedback means the impulse response rings on forever (infinite), and it's the digital cousin of an analog RC/RLC filter.

**Properties, the mirror image of FIR:**
- **Very efficient** — a sharp cut needs far fewer coefficients than the FIR equivalent (feedback does a lot of work cheaply). Low latency, low compute
- **Can be unstable** — feedback can blow up if the coefficients are wrong → see poles, below
- **Nonlinear phase** — different frequencies are delayed differently, distorting the waveform shape. Fine for many jobs (audio EQ), disqualifying for others

**Design methods:** usually by transforming a classic analog prototype — **Butterworth** (maximally flat passband), **Chebyshev** (sharper, at the cost of ripple), **Elliptic** (sharpest, ripple in both bands). In practice, `scipy.signal.butter` / `iirfilter`.

## The choice

| | FIR | IIR |
|---|---|---|
| Stability | **Always stable** | Can be unstable |
| Phase | **Linear achievable** | Nonlinear |
| Efficiency | Needs many taps | **Few coefficients** |
| Latency | Higher | Lower |
| Analog analogue | None (purely digital) | Yes (RC/RLC) |
| Use when | Phase matters, stability is paramount | Compute/latency is tight, phase doesn't matter |

**Rule of thumb:** FIR when you can afford the taps and need linear phase or guaranteed stability (audio, biomedical); IIR when efficiency or low latency dominates and phase distortion is acceptable (real-time control, cheap embedded).

## Poles, zeros and the z-transform

To reason about IIR stability, DSP uses the **z-transform** — the discrete-time analogue of the Laplace transform → [[engineering/02-control-theory/README|control theory]]. It turns the filter's difference equation into a ratio of polynomials, the **transfer function `H(z)`**:

- **Zeros** (roots of the numerator) — frequencies the filter *nulls*
- **Poles** (roots of the denominator) — frequencies the filter *boosts*, and the source of feedback/resonance

**The stability rule is exact and simple:** plot the poles on the complex plane. **A digital filter is stable if and only if all its poles lie inside the unit circle** (`|z| < 1`). A pole on or outside the circle means the feedback grows without bound — the filter rings forever or explodes.

**This is the same pole/stability analysis as [[engineering/02-control-theory/05-stability-and-root-locus|control theory]]**, with the unit circle playing the role that the left-half-plane plays for continuous systems. If you know control theory, IIR filter stability is the same idea in `z` instead of `s`.

## Practical warnings

- **Fixed-point arithmetic** on cheap hardware causes coefficient rounding that can move a pole *outside* the unit circle — a filter that's stable in floating-point maths becomes unstable when quantised. Real embedded concern → [[foundations/digital-signal-processing/09-dsp-in-practice|fixed-point]]
- **Cascade IIR filters as second-order sections (biquads)** rather than one high-order filter — high-order direct forms are numerically fragile, and biquads are the standard robust building block
- **Don't hand-roll the coefficients** — use `scipy.signal`. Getting them right by hand is error-prone, and the design functions encode decades of care

## Key insight

**A filter is a frequency response you apply by convolution, and the FIR-vs-IIR choice is the trade between guaranteed stability with linear phase (FIR, but many taps) and high efficiency with low latency (IIR, but it can go unstable).** IIR stability reduces to one geometric rule — all poles inside the unit circle — which is the same pole analysis as control theory, and the practical craft is choosing the family for your constraints and letting a library compute the coefficients rather than hand-deriving them.

## Related
- [[foundations/digital-signal-processing/05-convolution-and-lti-systems|convolution]] — applying a filter *is* convolution
- [[foundations/digital-signal-processing/07-spectral-analysis|spectral analysis]] — windows, used in FIR design
- [[engineering/02-control-theory/05-stability-and-root-locus|control theory: stability]] — the same pole analysis in `s`
- [[foundations/digital-signal-processing/09-dsp-in-practice|DSP in practice]] — fixed-point pitfalls

*Source: [reference] — Aug 2026.*
