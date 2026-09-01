# Modulation and Software-Defined Radio

**[Advanced]** — how information rides on radio waves, and the shift that turned radio from circuits into code. The bridge from DSP to [[hardware/06-radio-frequency|RF]].

## The kid version first

A radio wave is a fast sinusoid — say 100 million cycles a second. On its own it carries nothing. **Modulation is nudging that wave — its height, its speed, or its timing — in step with your data**, so the wobbles encode your voice, your Wi-Fi packet, your GPS signal. The receiver watches the wobbles and reconstructs the data.

**Software-defined radio** is the realisation that all of this nudging and un-nudging is just arithmetic on samples — so a general-purpose computer with a simple antenna front-end can *become* any radio, in software.

## Why modulate at all

Two reasons you can't just broadcast your signal directly:

1. **Antenna size.** An efficient antenna is roughly the size of the wavelength. Your voice (~3 kHz) has a wavelength of ~100 km — an impossible antenna. Ride it on a 100 MHz carrier (~3 m wavelength) and the antenna is practical. **Modulation shifts your low-frequency information up to a high carrier frequency where it can radiate**
2. **Sharing the spectrum.** Everyone transmitting at once would collide. Assigning each service a different carrier frequency (radio stations, Wi-Fi channels, phone bands) lets many signals coexist — you tune to the carrier you want → [[foundations/information-theory/05-channel-capacity-and-noise|channel capacity]]

## The analog modulations

A carrier `A·cos(2πf_c·t + φ)` has three things you can vary in step with your message:

- **AM (Amplitude Modulation)** — vary the *height* `A`. Simple, cheap receivers, but noise adds to amplitude so it's noisy. AM radio, and the video part of old TV
- **FM (Frequency Modulation)** — vary the *frequency* `f_c`. More robust to noise (noise hits amplitude, which FM ignores), better fidelity. FM radio
- **PM (Phase Modulation)** — vary the *phase* `φ`. Closely related to FM, and the basis of the digital schemes below

**The noise trade is the point:** AM is simple but noise-prone; FM/PM trade bandwidth for noise immunity. That trade — bandwidth for robustness — recurs throughout communications.

## Digital modulation

Digital data (bits) is carried by switching the carrier between discrete states:

- **ASK** — amplitude shift keying: on/off or between levels (a digital AM)
- **FSK** — frequency shift keying: bit 0 = one frequency, bit 1 = another. Old modems' sound
- **PSK** — phase shift keying: bits map to carrier phases. **BPSK** (2 phases = 1 bit), **QPSK** (4 phases = 2 bits)
- **QAM** — quadrature amplitude modulation: vary amplitude *and* phase together, so each symbol carries many bits. **16-QAM = 4 bits/symbol, 256-QAM = 8.** This is how Wi-Fi, cable and LTE pack high data rates into limited spectrum

**The trade-off you can feel in your daily life:** higher-order QAM sends more bits per symbol but the constellation points sit closer together, so noise flips them more easily. **This is why your Wi-Fi drops to a lower rate when the signal is weak** — it falls back to a lower-order modulation with more noise margin. Same channel, fewer bits per symbol, more reliable → [[foundations/information-theory/05-channel-capacity-and-noise|Shannon's limit]].

## I/Q — the representation that makes it all computable

Modern radio represents a signal as two components: **In-phase (I)** and **Quadrature (Q)** — the signal multiplied by a cosine and by a sine. Together they're the real and imaginary parts of a **complex signal**, and they capture both amplitude and phase at once → [[foundations/digital-signal-processing/03-the-frequency-domain|why complex numbers]].

**Why I/Q is the whole game:** every modulation scheme becomes simple arithmetic on I/Q samples. QAM is literally a grid of (I, Q) points (the **constellation diagram** you see in RF tools). Demodulation is measuring which grid point each received sample is nearest. **Once a signal is I/Q samples, modulation and demodulation are just DSP** — filtering, FFTs, and geometry on complex numbers.

## Software-Defined Radio

**Traditionally, radio was fixed-function circuits** — a specific chip for FM, another for your car key, another for Wi-Fi, each mixing and filtering in hardware. **SDR replaces the circuits with an ADC/DAC and a computer:** the antenna front-end digitises a chunk of spectrum into I/Q samples, and *all* the demodulation happens in software.

```
   antenna ──► [ RF front-end + ADC ] ──► I/Q samples ──► [ SOFTWARE: any radio ]
                digitise a band              (numbers)      FM, ADS-B, GPS, Wi-Fi, ...
```

**Why this is transformative:**
- **One device becomes any radio.** Reprogram it to decode aircraft transponders, then weather satellites, then your car's key fob — no hardware change
- **New protocols ship as software updates**, not new chips
- **It democratised RF.** An **RTL-SDR dongle costs ~$30** and turns DSP knowledge into a working radio receiver on your laptop → [[foundations/digital-signal-processing/09-dsp-in-practice|tooling]]

**GNU Radio** is the standard framework — you build a radio as a flowgraph of DSP blocks (filters, FFTs, demodulators). Learning SDR is applied DSP: every block is a concept from this folder.

**The honest caveats:** SDR trades hardware efficiency for flexibility — a purpose-built chip is far more power-efficient, so phones still use dedicated silicon for the heavy lifting. And **transmitting** is legally restricted (you need a licence and the right band); *receiving* on an RTL-SDR is the safe, legal playground → [[hardware/06-radio-frequency|RF]].

## Key insight

**Modulation shifts low-frequency information onto a high-frequency carrier by varying its amplitude, frequency or phase — and once you represent the signal as I/Q (complex) samples, every modulation scheme becomes simple DSP arithmetic.** That realisation is what makes software-defined radio possible: digitise a band into I/Q, and a computer can *be* any radio in software. A $30 dongle plus GNU Radio turns this whole folder into a working receiver, which is the most tangible payoff DSP offers.

## Related
- [[hardware/06-radio-frequency|radio frequency]] — the analog/antenna side
- [[foundations/information-theory/05-channel-capacity-and-noise|channel capacity]] — the limit on how many bits a channel carries
- [[foundations/digital-signal-processing/03-the-frequency-domain|the frequency domain]] — I/Q as complex signals
- [[foundations/digital-signal-processing/09-dsp-in-practice|DSP in practice]] — RTL-SDR, GNU Radio

*Source: [reference] — Aug 2026. Transmitting is licence-restricted; receiving on an RTL-SDR is the legal playground.*
