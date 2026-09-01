# Digital Signal Processing — Projects

*The rare theory folder whose reps are genuinely fun and mostly free — **NumPy on your laptop, then a ~$30 RTL-SDR dongle** that turns the whole course into a working radio. Every project produces something you can hear, see, or decode.*

Difficulty: 🟢 starter (hours–days) · 🟡 intermediate (a week or two) · 🔴 ambitious / portfolio-grade. ⭐ = highest signal.

## The ladder

- 🟢 ⭐ **See a sound's spectrum** — record a few seconds of audio (a whistle, a chord, your voice), FFT it, and plot the spectrum and a spectrogram. **Done when:** you can point at the peaks and name the notes, and watch a rising whistle sweep up the spectrogram → [[foundations/digital-signal-processing/07-spectral-analysis|spectral analysis]]. **Do this first** — an hour, and the frequency domain stops being abstract.

- 🟢 **Make aliasing happen** — synthesise a tone above half your sample rate, sample it, and watch it appear as a *different, lower* tone. **Done when:** a 900 Hz tone sampled at 1 kHz plays back as 100 Hz, and you understand why → [[foundations/digital-signal-processing/02-sampling-and-aliasing|aliasing]].

- 🟢 **Remove hum with a filter** — take a recording with 50/60 Hz mains hum, design a notch filter (`scipy.signal`), and hear it vanish. **Done when:** the hum spike is gone from the spectrum and the audio is clean → [[foundations/digital-signal-processing/06-digital-filters|filters]].

- 🟡 ⭐ **Implement convolution from scratch, then prove the theorem** — write the slide-multiply-sum by hand, verify it matches `np.convolve`, then compute the same result via FFT → multiply → inverse-FFT. **Done when:** both give the identical answer, and you've *seen* that convolution in time equals multiplication in frequency → [[foundations/digital-signal-processing/05-convolution-and-lti-systems|convolution]]. **The single most clarifying DSP exercise.**

- 🟡 **Build a graphic equaliser** — split audio into frequency bands, apply per-band gain, recombine. **Done when:** you can boost the bass and cut the treble on a real track and hear it → [[foundations/digital-signal-processing/06-digital-filters|filters]].

- 🟡 **FIR vs IIR, measured** — design a low-pass both ways to the same spec, then compare tap count, phase response, and (for the IIR) plot the poles against the unit circle. **Done when:** you can state which you'd ship for audio (FIR, linear phase) vs tight embedded (IIR, efficient) and why → [[foundations/digital-signal-processing/06-digital-filters|FIR vs IIR]].

- 🟡 **A guitar tuner / pitch detector** — capture audio, find the fundamental frequency, display the note. **Done when:** it correctly reads a plucked string, and you've handled the resolution/latency trade (you need a long enough window for low notes) → [[foundations/digital-signal-processing/07-spectral-analysis|resolution]].

- 🔴 ⭐ **Decode a real radio signal with an RTL-SDR** — a ~$30 dongle, GNU Radio (or `pyrtlsdr`), and demodulate FM radio, then decode aircraft **ADS-B** transponders and plot the planes overhead. **Done when:** you're seeing real aircraft on a map, decoded from raw I/Q you captured → [[foundations/digital-signal-processing/08-modulation-and-sdr|SDR]]. **The most satisfying payoff in this folder** — and legal, because you're only *receiving*.

- 🔴 **Build a digital modem** — modulate a bitstream (BPSK or QPSK) onto a carrier, add noise, demodulate, and measure the bit error rate as noise rises. **Done when:** you can plot BER vs signal-to-noise and see it match theory → [[foundations/digital-signal-processing/08-modulation-and-sdr|modulation]].

- 🔴 **Connect it to ML** — take an audio classification task, build the mel-spectrogram front-end yourself (don't use a black-box loader), and feed it to a small CNN. **Done when:** you understand every step from waveform to the tensor the model sees → [[ai-ml/02-ml-engineer/06-computer-vision/README|CNNs]].

## If you only do one

**See a sound's spectrum, then decode ADS-B with an RTL-SDR.** The first is an hour and makes the frequency domain concrete; the second is a weekend and a dongle, and ends with real aircraft on a map decoded from radio you captured — which is about the most tangible thing any foundations folder can offer.

## Related
- [[foundations/digital-signal-processing/README|the DSP course]]
- [[hardware/projects|hardware projects]] — the RF/embedded side
- [[foundations/projects|foundations projects]] · [[project-ideas|Project Ideas]] — the vault-wide index
