# Convolution and LTI Systems

**[Intermediate → Advanced]** — the single most important operation in DSP, the theorem that connects it to the frequency domain, and why it's also the heart of modern computer vision.

## The kid version first

You know an [[foundations/digital-signal-processing/01-signals-and-systems|LTI system]] completely once you know its response to one impulse (a single spike). **Convolution is the operation that uses that impulse response to compute the system's output for *any* input** — you slide the impulse response along the input, multiplying and summing as you go.

That's the whole mechanism behind echoes, filters, blur, edge detection, and — the same maths — the convolutional layer in a neural network.

## The impulse response

Recall the LTI magic: poke the system with an impulse `δ[n]` (1 at zero, else 0) and record the output. That output is the **impulse response `h[n]`**, and it *is* the system — a complete description.

- An echo's impulse response is a spike, then a smaller delayed spike (the echo)
- A blur's impulse response is a little smeared bump
- A moving-average filter's impulse response is a small flat block

**Why one impulse suffices:** any input signal is just a sum of scaled, shifted impulses (sample `x[3]` is `x[3]·δ[n−3]`). Because the system is *linear* (scaled inputs → scaled outputs) and *time-invariant* (shifted inputs → shifted outputs), the response to the whole input is the sum of scaled, shifted copies of `h[n]`. **Summing those copies is exactly convolution.**

## Convolution, mechanically

```
y[n] = Σ  x[k] · h[n − k]
       k
```

In words: **flip the impulse response, slide it across the input, and at each position multiply-and-sum the overlap.** The output at each point is a weighted blend of nearby input samples, with the weights given by `h`.

```
   input:   [1, 2, 3, 4]
   kernel:  [1, 1, 1]  (a moving-average-ish sum)
   slide, multiply overlap, sum at each shift → the output sequence
```

**Intuition per application:**
- **Smoothing/blur** — `h` is a bump, so each output is a local average → noise falls
- **Edge detection** — `h` is `[−1, 1]` (a difference), so output is large where the input *changes* → edges pop
- **Echo** — `h` has spikes at delays → the output is the signal plus delayed copies

**One subtlety worth flagging:** the flip (`h[n−k]`) distinguishes true convolution from **cross-correlation** (no flip). They're identical for symmetric kernels, and — a point that trips up newcomers — **"convolution" in a CNN is actually cross-correlation** (no flip). The distinction rarely matters in ML because the weights are learned either way, but it's why the maths looks slightly different between a DSP textbook and a deep-learning one.

## The convolution theorem — the payoff

This is the result that ties the whole field together:

> **Convolution in the time domain equals multiplication in the frequency domain.**
> `x * h  ⟷  X · H`

Slide-and-sum in time is the *same operation* as element-wise multiply of the two spectra. This is profound and practical:

**1. It explains why the frequency domain matters.** An [[foundations/digital-signal-processing/03-the-frequency-domain|LTI system]] convolves the input with `h[n]` — equivalently, it multiplies the input's spectrum by `H(f)`, the system's **frequency response**. So a filter is just "a gain to apply at each frequency," which is why filter design is done in the frequency domain → [[foundations/digital-signal-processing/06-digital-filters|filters]].

**2. It makes big convolutions fast.** Direct convolution is O(N²). But *multiplication* is O(N), so for large signals you go **FFT → multiply → inverse-FFT**, which is O(N log N) → [[foundations/digital-signal-processing/04-the-fft|the FFT]]. Large filters, long correlations, and template matching all use this.

**The mental model to keep:** convolution (hard, in time) and multiplication (easy, in frequency) are two faces of the same thing, and the FFT lets you switch to the easy face whenever it's worth it.

## The frequency response

Because an LTI system multiplies each frequency by a complex number, that set of numbers — the **frequency response `H(f)`** — tells you everything the system does:

- **Magnitude `|H(f)|`** — the gain at each frequency. `>1` boosts, `<1` attenuates, `0` removes. **This is what a filter's "shape" is** (low-pass = high near 0, zero at high frequencies)
- **Phase `∠H(f)`** — the delay at each frequency. Matters for waveform shape and for [[foundations/digital-signal-processing/06-digital-filters|linear-phase filters]]

`H(f)` is just the [[foundations/digital-signal-processing/03-the-frequency-domain|Fourier transform]] of the impulse response `h[n]`. So the two complete descriptions of an LTI system — impulse response (time) and frequency response (frequency) — are a Fourier pair. Same system, two views, again.

## Convolution beyond audio

The identical operation, in more dimensions and more fields:

- **Images (2-D convolution)** — a small kernel slides over the image: blur, sharpen, edge-detect, emboss are all `h` choices → [[foundations/computer-graphics/README|graphics]]
- **Convolutional neural networks** — a CNN's core layer convolves learned kernels over images. **The network *learns the impulse responses*** — early layers learn edge and texture detectors, later ones learn object parts. Understanding DSP convolution is understanding what a conv layer *does* → [[ai-ml/02-ml-engineer/06-computer-vision/README|computer vision]]
- **Probability** — the distribution of a sum of two independent random variables is the convolution of their distributions → [[ai-ml/00-foundations/03-mathematics/README|the maths]]

**That a CNN and an audio filter run the same operation is not a coincidence** — both are LTI-style local weighted blends, and it's why "convolution" is one of the highest-leverage concepts to actually understand.

## Key insight

**Convolution is how an LTI system's single impulse response is used to process any input — slide, multiply, sum — and the convolution theorem makes it the hinge of the entire field: convolution in time *is* multiplication in frequency.** That equivalence explains why filters are designed as frequency shapes, lets the FFT make big convolutions fast, and connects audio filtering, image processing and CNNs as literally the same operation with different kernels. Master convolution and the frequency response, and most of DSP is downstream.

## Related
- [[foundations/digital-signal-processing/06-digital-filters|digital filters]] — designing the `h[n]` that does what you want
- [[foundations/digital-signal-processing/03-the-frequency-domain|the frequency domain]] · [[foundations/digital-signal-processing/04-the-fft|the FFT]]
- [[ai-ml/02-ml-engineer/06-computer-vision/README|computer vision]] — convolution as the CNN's core
- [[foundations/digital-signal-processing/01-signals-and-systems|signals and systems]] — the LTI foundation

*Source: [reference] — Aug 2026.*
