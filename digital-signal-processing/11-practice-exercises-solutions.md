# Practice Exercises — Solutions

> **[Intermediate]** · Worked answers and expected results for [[foundations/digital-signal-processing/10-practice-exercises|note 10]]. **Attempt each yourself first** — a spectrum you plotted teaches more than one you read about. These give the expected outcome and the *why*, not full code you can paste.

---

## Part A — Sampling and the frequency domain

**1. Tone → spike.** The waveform is a clean 440 Hz sinusoid (≈8.8 cycles in 20 ms). The spectrum has one peak at 440 Hz. **Why it has width:** a finite-length capture is implicitly multiplied by a rectangular window, whose transform is a sinc — so a true single frequency smears into a narrow main lobe plus side lobes. Longer capture → narrower peak (finer bin resolution `fs/N`). This previews leakage (#9).

**2. Aliasing.** A 3000 Hz tone at `fs = 4000` aliases to `|fs − f| = 1000` Hz — the FFT shows the peak at 1000 Hz, and it *sounds* like a 1000 Hz tone, indistinguishable from a real one. **The key point:** the information is corrupted at sampling; no post-filter recovers it, because the alias and a genuine 1000 Hz tone are now byte-identical. This is why the anti-aliasing filter must be *analog, before* the ADC.

**3. Square from sinusoids.** N=1 is a pure sine; by N=9 it's visibly square-ish; N=50 has sharp edges. The **Gibbs overshoot** (~9% spikes at the discontinuities) never disappears no matter how large N — it narrows but doesn't shrink. Takeaway: sharp edges need infinite frequencies, and any band-limited (real) system rounds them.

**4. FFT vs DFT timing.** Both agree to ~1e-10 (floating-point noise). On log-log axes the naive DFT's line has slope ≈2 (N²) and the FFT's is nearly linear-ish (N log N) — by N=16384 the FFT is thousands of times faster. This *is* the reason real-time DSP exists.

## Part B — Convolution and filtering

**5. Convolution theorem.** All three methods match to floating-point precision. The hand loop and `np.convolve` are O(N²); the FFT route is O(N log N) and wins for large signals. Seeing the FFT route give the *identical* answer is the convolution theorem made concrete: convolution in time = multiplication in frequency.
*(One gotcha: FFT convolution is circular — zero-pad both signals to `len(a)+len(b)-1` to match linear `np.convolve`.)*

**6. Denoising.** The filtered signal recovers the 50 Hz tone cleanly; its spectrum shows the peak at 50 Hz with the broadband noise above the cutoff removed. `filtfilt` runs the filter forward *and* backward, cancelling phase distortion (zero-phase) — a single-pass `lfilter` would shift the waveform in time. For an offline signal, `filtfilt` is almost always what you want.

**7. FIR vs IIR.** The IIR (e.g. 4th-order Butterworth) needs ~5 coefficients per side; an FIR matching the same transition sharpness needs tens to hundreds of taps. The FIR's phase response is a straight line (linear phase, constant delay); the IIR's phase is curved (frequency-dependent delay). Ship FIR when phase/shape matters (audio, biomedical) or stability is paramount; IIR when compute/latency is tight and phase distortion is acceptable.

**8. Poles and the unit circle.** The Butterworth poles sit inside the unit circle, clustered near the cutoff angle. Nudge a denominator coefficient until a pole's magnitude exceeds 1 and the impulse response grows without bound — the output explodes. **Exactly** the control-theory rule, with the unit circle (discrete, z-plane) playing the role of the left-half-plane (continuous, s-plane).

## Part C — Spectral analysis

**9. Leakage.** Un-windowed, the off-bin tone smears across many bins with prominent side lobes — a single frequency looks like a messy hump. Hann windowing tapers the edges, dropping the side lobes dramatically; the peak is cleaner but slightly *wider* (the main lobe broadened). That width-vs-leakage trade is unavoidable — you choose where to spend it (Hann is the sensible default).

**10. Chirp spectrogram.** The energy traces a diagonal line from 200 Hz up to 2000 Hz over time. Short window (e.g. 128 samples): sharp *time* localisation, blurry frequency (the diagonal is thin horizontally, fuzzy vertically). Long window (e.g. 2048): sharp *frequency*, blurry time. You cannot get both — the time-frequency uncertainty principle, visible in one plot.

## Part D — Radio (RTL-SDR)

**11. FM spectrum.** You'll see distinct peaks across ~88–108 MHz, each a station; strong local ones dominate. Matching a peak's centre frequency to a known station confirms your frequency axis is correct. (Watch for the DC spike at the tuner's centre — a known SDR artefact, not a station.)

**12. ADS-B.** `dump1090` decodes 1090 MHz Mode-S messages into aircraft positions; feed them to a map (dump1090 ships a web view). Real planes appear, updating live. This is amplitude-modulated pulse position at heart, decoded entirely in software from I/Q — the whole folder, working, for $30. **Receive only** — transmitting on these bands needs a licence.

## The through-line

If a result surprised you — the alias sounding real (#2), the Gibbs overshoot refusing to vanish (#3), leakage from an off-bin tone (#9), or a pole crossing the circle and the output exploding (#8) — that surprise *is* the learning. Each is a place where the maths in the notes becomes something you've now seen with your own eyes.

## Related
- [[foundations/digital-signal-processing/10-practice-exercises|the exercises]]
- [[foundations/digital-signal-processing/README|the DSP course]]
