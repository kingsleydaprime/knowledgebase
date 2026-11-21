---
id: be36b7cd-264e-4266-8df4-7bbae6be0986
---

# Signals and Systems

A signal is a measurement that changes over time, like the sound reaching a microphone or your heart rate, and a system is anything that takes a signal in and gives a changed signal out. Digital signal processing is doing that changing with numbers on a computer. The noise cancelling in your earphones and the voice clean-up on a WhatsApp call are both systems working on signals.

## The kid version first
<!-- bite: 7131e580-e6e9-456c-b601-7442ff8d379b -->

A **signal** is just a measurement that changes over time: the air pressure hitting a microphone, the voltage on a wire, the brightness along a row of pixels, your heart rate. **A system** is anything that takes a signal in and puts a (changed) signal out — a volume knob, an equaliser, a noise filter, an echo.

**Digital signal processing is doing this with numbers, on a computer, instead of with analog circuits** — and it turns out that almost everything interesting (removing noise, finding a heartbeat, decoding Wi-Fi, recognising speech) is one system acting on one signal.

## What a signal is, precisely
<!-- bite: 81289a4c-f79f-4b14-953f-de50ad557715 -->

A signal is a function mapping an independent variable (usually time) to a value:

- **Continuous-time** — defined at every instant. Real-world, analog: sound, voltage, temperature. Written `x(t)`
- **Discrete-time** — defined only at sample points. What a computer holds: a sequence of numbers. Written `x[n]`, where `n` is an integer index

**The whole discipline lives at the boundary** between these two — the real world is continuous, computers are discrete, and [[digital-signal-processing/02-sampling-and-aliasing|sampling]] is the bridge.

Signals can be 1-D (audio, `x[n]`), 2-D (an image, `x[m,n]`), or higher (video). **The maths is the same in every dimension**, which is why the ideas here transfer straight to image processing and to [[machine-learning/06-computer-vision/index|convolutional networks]].

## The building-block signals
<!-- bite: b8b7445e-eba4-44c1-afd9-851eba560592 -->

A few idealised signals recur everywhere, because complex signals are built from them:

- **The sinusoid** `A·cos(2πft + φ)` — a pure tone at frequency `f`. **The single most important signal in DSP**, because [[digital-signal-processing/03-the-frequency-domain|every signal is a sum of these]]
- **The impulse** `δ[n]` — 1 at n=0, zero everywhere else. A single spike. **It's how you *probe* a system** → [[digital-signal-processing/05-convolution-and-lti-systems|the impulse response]]
- **The step** — 0 then 1. A switch turning on
- **The exponential** — decay or growth, and the complex exponential `e^{jωn}`, which is a rotating sinusoid and the mathematical heart of the frequency domain

## What a system does
<!-- bite: 3936ff73-3c26-4bcc-9e61-e154a4b64dcb -->

A system transforms an input signal into an output signal. We classify systems by their properties, because the properties determine what maths applies:

- **Linear** — scaling the input scales the output, and inputs add: $system(a·x + b·y) = a·system(x) + b·system(y)$.
- **Superposition.** This is the property that lets you decompose a hard signal into simple parts, process each, and add the results
- **Time-invariant** — the system behaves the same today as tomorrow; delaying the input just delays the output. The rules don't change over time
- **Causal** — the output depends only on present and past inputs, not the future. Required for real-time processing (you can't use samples you haven't received yet)
- **Stable** — a bounded input produces a bounded output; it doesn't blow up → [[digital-signal-processing/06-digital-filters|filter stability]]

## LTI — the abstraction that makes DSP tractable
<!-- bite: 9aa29464-d3a5-4bbb-8423-00c070ebe05b -->

**Linear Time-Invariant** systems are the ones that are both linear and time-invariant, and **almost all of classical DSP is the study of LTI systems** — because they have an almost magical property:

> **An LTI system is *completely* described by its response to a single impulse.**

Poke an LTI system with one spike, record what comes out (the **impulse response**), and you now know exactly what it will do to *any* input — via [[digital-signal-processing/05-convolution-and-lti-systems|convolution]]. You never have to test it with anything else.

**And there's a second gift:** feed an LTI system a pure sinusoid and you get back the *same-frequency* sinusoid, only scaled and phase-shifted — never a new frequency. This is why the [[digital-signal-processing/03-the-frequency-domain|frequency domain]] is so powerful: an LTI system just applies a "gain and delay per frequency," which turns hard time-domain problems into simple frequency-domain multiplication.

**Why this matters:** most useful systems either *are* LTI (filters, echoes, most audio and comms processing) or are usefully approximated as LTI over a working range. The moment a system is LTI, the entire toolkit — impulse response, convolution, Fourier, transfer functions — applies.

## Why DSP is everywhere
<!-- bite: 11e1c6b0-915b-4770-9182-a4803f2d7c49 -->

Once signals are numbers, you can do anything computation can do, precisely and reproducibly:

- **Audio** — noise removal, EQ, compression, effects, speech recognition
- **Communications** — every phone, Wi-Fi and satellite link modulates and demodulates digitally → [[digital-signal-processing/08-modulation-and-sdr|modulation]]
- **Images and video** — filtering, compression (JPEG *is* DSP), enhancement → [[computer-graphics/index|graphics]]
- **Sensors and control** — filtering noisy readings, extracting signals → [[control-theory/index|control theory]], [[robotics/index|robotics]]
- **Biomedical** — ECG, EEG, ultrasound, MRI reconstruction
- **Machine learning** — a CNN's core operation is [[digital-signal-processing/05-convolution-and-lti-systems|convolution]]; audio and speech models run on spectrograms → [[machine-learning/index|Machine Learning]]

**Analog vs digital, briefly:** analog processing (op-amps, RC circuits) is instantaneous and continuous but drifts, is hard to change, and can't do anything complex. Digital is a sampled approximation but is exact, reproducible, reprogrammable, and can run arbitrarily sophisticated algorithms. **The world went digital because "reprogrammable and exact" beats "instant and continuous" for almost everything** → [[hardware/02-digital-and-analog|digital and analog]].

## Key insight
<!-- bite: f3ce5139-4870-4308-8f7b-d5b3aa66bf91 -->

**A signal is a measurement over time, a system transforms it, and the entire classical toolkit exists because *Linear Time-Invariant* systems are fully described by their response to a single impulse.** That one fact — poke it once and you know everything it does — is what makes convolution, the frequency domain, and filter design all work. Learn to recognise when a system is LTI, and the rest of DSP is the machinery for exploiting it.

## Related
<!-- bite: 008dc389-04a3-4e11-a52e-1f7be99e942e -->
- [[digital-signal-processing/02-sampling-and-aliasing|sampling and aliasing]] — the continuous-to-discrete bridge
- [[digital-signal-processing/03-the-frequency-domain|the frequency domain]] — why sinusoids are special
- [[digital-signal-processing/05-convolution-and-lti-systems|convolution and LTI systems]] — the impulse-response payoff
- [[control-theory/index|control theory]] — LTI systems from the control side

## About this lesson
<!-- bite: d7f67741-a9bb-405c-8f5f-1007e0467a4c -->

**Level:** Beginner. **Covers:** what a signal is, what a system does to it, and the one class of system that makes the whole field tractable.

*Source: [reference] — Aug 2026.*
