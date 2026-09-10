# Digital Signal Processing

**Turning real-world signals into numbers, and doing useful things to them.** A 9-note course built Aug 2026, filling the gap between [[hardware/06-radio-frequency|hardware/RF]] (the analog/antenna side) and [[information-theory/index|information theory]] (the limits) — and, unexpectedly, the maths under a [[ai-ml/02-ml-engineer/06-computer-vision/index|CNN's convolution layer]].

> **The one idea:** almost everything interesting is *one system acting on one signal*, and the two moves that make it tractable are **the frequency domain** (any signal is a sum of sinusoids, so filtering becomes selection) and **convolution** (which *is* multiplication in that domain). Learn those two and the field opens up.

## Why this exists

The vault's gap audit named it: `hardware/` has RF and embedded, `information-theory/` has entropy and channels, `numerical-methods/` has interpolation and integration — but **the discipline that connects sampling, Fourier, filtering and modulation** had no home. It's the natural application of a lot of maths the vault already teaches, and it turns out to be the bridge to [[ai-ml/index|computer vision]] and audio ML as well as to radio.

## Reading order

**01–05 are the core and build on each other; read them in order.** 06–09 apply the core — filters, spectra, radio, and practice.

1. [[digital-signal-processing/01-signals-and-systems|signals-and-systems]] — **[Beginner]** — signals, systems, and **LTI: the class of system fully described by its response to one impulse**, which makes everything else work
2. [[digital-signal-processing/02-sampling-and-aliasing|sampling-and-aliasing]] — **[Beginner → Intermediate]** — the continuous-to-digital bridge, **Nyquist (sample at >2× the top frequency)**, and why aliasing is irreversible
3. [[digital-signal-processing/03-the-frequency-domain|the-frequency-domain]] — **[Intermediate]** — the central idea: **any signal is a sum of sinusoids**, the DFT, and why the frequency view makes hard problems easy
4. [[digital-signal-processing/04-the-fft|the-fft]] — **[Intermediate]** — the O(N log N) algorithm that **moved the frequency domain from theory into every real-time system on earth**
5. [[digital-signal-processing/05-convolution-and-lti-systems|convolution-and-lti-systems]] — **[Intermediate → Advanced]** — the core operation, the convolution theorem (**time-convolution = frequency-multiplication**), and why it's also the heart of CNNs
6. [[digital-signal-processing/06-digital-filters|digital-filters]] — **[Advanced]** — reshaping frequency content: **FIR vs IIR**, and the pole/unit-circle stability rule (the same analysis as control theory)
7. [[digital-signal-processing/07-spectral-analysis|spectral-analysis]] — **[Advanced]** — the FFT on real data: **leakage, windowing, and the time-frequency uncertainty trade**, plus the spectrogram
8. [[digital-signal-processing/08-modulation-and-sdr|modulation-and-sdr]] — **[Advanced]** — how data rides radio waves, **I/Q signals**, and software-defined radio — the bridge to [[hardware/06-radio-frequency|RF]]
9. [[digital-signal-processing/09-dsp-in-practice|dsp-in-practice]] — **[Intermediate]** — the tooling, **fixed-point (the textbook-vs-shipped gap)**, and how much of what you use daily is quietly DSP

**Practice:** [[digital-signal-processing/10-practice-exercises|practice-exercises]] — **[Intermediate]** — twelve short scripts (a tone becoming a spike, making aliasing audible, proving the convolution theorem, poles crossing the unit circle), plus two RTL-SDR radio drills. Solutions in [[digital-signal-processing/11-practice-exercises-solutions|note 11]]

## If you only take three things

1. **Any signal is a sum of sinusoids** — the frequency domain is the same signal seen differently, and filtering is just selecting frequencies ([[digital-signal-processing/03-the-frequency-domain|03]]).
2. **Convolution in time = multiplication in frequency** — the theorem that ties the field together and makes the FFT so useful ([[digital-signal-processing/05-convolution-and-lti-systems|05]]).
3. **A CNN's convolution is DSP convolution** with learned kernels — this folder is upstream of computer vision, not just radio ([[digital-signal-processing/05-convolution-and-lti-systems|05]]).

## The status note

Like the rest of the [[HOME|theory spine]], this is **`[reference]`** — read and assembled, not validated by building. The fastest way to make it real is cheap and genuinely fun: **NumPy/SciPy on your laptop, then a ~$30 RTL-SDR dongle** turns the whole folder into a working radio receiver → [[digital-signal-processing/10-practice-exercises|the exercises]] and [[digital-signal-processing/projects|projects]].

## Related
- [[information-theory/index|information theory]] — the limits on what a channel can carry
- [[hardware/06-radio-frequency|radio frequency]] — the analog side of modulation
- [[mathematics/07-applied-and-computational/01-numerical-methods/index|numerical methods]] — the numerical maths next door
- [[ai-ml/02-ml-engineer/06-computer-vision/index|computer vision]] — convolution, learned
- [[control-theory/index|control theory]] — LTI systems and pole stability, in continuous time
- [[projects|foundations projects]] · [[HOME|the home page]]

*Source: [reference] — Aug 2026.*
