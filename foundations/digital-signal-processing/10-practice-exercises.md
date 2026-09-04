# Practice Exercises

> **[Intermediate]** · Twelve short scripts. **DSP's failure mode is nodding along to the maths without ever seeing a signal transform — and reading about the FFT doesn't build the instinct that *watching* a spectrum does.**

Every one is a few dozen lines of Python with `numpy`/`scipy`/`matplotlib`. **Plot everything** — this domain is visual, and half the learning is in the picture. Solutions with expected results in [[foundations/digital-signal-processing/11-practice-exercises-solutions|note 11]].

The last two need a **~$30 RTL-SDR dongle** and are optional — but they're the most fun in the folder.

---

## Part A — Sampling and the frequency domain (notes 02–04)

**1. See a tone become a spike.**
Synthesise a 5-second 440 Hz sine at `fs = 8000`. Plot the first 20 ms (time domain), then its FFT magnitude (frequency domain).
**Done when:** the waveform is a clean sinusoid and the spectrum is a single spike at 440 Hz — and you can explain why the spike has a small width rather than being infinitely thin → [[foundations/digital-signal-processing/03-the-frequency-domain|note 03]].

**2. Make aliasing happen, and hear it.**
Synthesise a 3000 Hz tone sampled at `fs = 4000` (Nyquist = 2000). Predict the aliased frequency *before* running, then FFT to confirm, and play it back.
**Done when:** the tone appears at 1000 Hz, you predicted it from `fs − f`, and you understand why no filter *after* sampling can recover the original → [[foundations/digital-signal-processing/02-sampling-and-aliasing|note 02]].

**3. Reconstruct a square wave from sinusoids.**
Add the first N odd harmonics of a square wave (1st, 3rd, 5th…) with amplitudes 1, 1/3, 1/5… Plot for N = 1, 3, 9, 50.
**Done when:** the sum visibly approaches a square wave as N grows, you can see the **Gibbs overshoot** at the edges refuse to vanish, and Fourier's "any signal is a sum of sinusoids" is now something you've *built* → [[foundations/digital-signal-processing/03-the-frequency-domain|note 03]].

**4. Time the FFT against the naive DFT.**
Implement the O(N²) DFT directly (a double loop). Time it and `np.fft.fft` for N = 256, 1024, 4096, 16384. Plot both on log-log axes.
**Done when:** your DFT and the FFT agree to floating-point precision, and the timing slopes visibly differ (N² vs N log N) — the speed-up that moved the frequency domain into every real-time system → [[foundations/digital-signal-processing/04-the-fft|note 04]].

---

## Part B — Convolution and filtering (notes 05–06)

**5. Prove the convolution theorem yourself.**
Take two short signals. Convolve them (a) with your own slide-multiply-sum loop, (b) with `np.convolve`, and (c) via FFT → element-wise multiply → inverse FFT.
**Done when:** all three give the identical result, and you can state which one is O(N²) and which is O(N log N) → [[foundations/digital-signal-processing/05-convolution-and-lti-systems|note 05]].

**6. Recover a signal buried in noise.**
Add heavy Gaussian noise to a 50 Hz sine. Design a low-pass filter (`scipy.signal.butter` + `filtfilt`) and recover it. Plot noisy vs filtered, and both spectra.
**Done when:** the tone is clearly recovered, the noise above the cutoff is gone from the spectrum, and you can explain what `filtfilt` does that a single-pass filter doesn't (zero phase) → [[foundations/digital-signal-processing/06-digital-filters|note 06]].

**7. FIR vs IIR to the same spec.**
Design a low-pass at the same cutoff both ways: an FIR (`firwin`) and an IIR (`butter`). Compare the number of coefficients (taps), and plot both frequency responses (`freqz`) — magnitude *and* phase.
**Done when:** you can show the IIR needs far fewer coefficients, the FIR has linear phase and the IIR doesn't, and you can state which you'd ship for audio vs a tight embedded loop → [[foundations/digital-signal-processing/06-digital-filters|note 06]].

**8. Plot IIR poles against the unit circle.**
For your IIR filter from #7, get the poles (`scipy.signal.tf2zpk`) and plot them on the complex plane with the unit circle. Then deliberately nudge a coefficient until a pole crosses outside, and observe the output blow up.
**Done when:** the stable filter's poles are all inside the circle, and you've *seen* instability appear the moment one crosses out — the same rule as [[engineering/02-control-theory/05-stability-and-root-locus|control-theory stability]] → [[foundations/digital-signal-processing/06-digital-filters|note 06]].

---

## Part C — Spectral analysis (note 07)

**9. Cause and cure spectral leakage.**
FFT a sinusoid whose frequency is *not* an exact bin (a non-integer number of cycles in the window), with no window. Then apply a Hann window and FFT again.
**Done when:** the un-windowed spectrum smears a single tone across many bins, the Hann-windowed one is far cleaner, and you can state the trade you made (leakage down, main-lobe width up) → [[foundations/digital-signal-processing/07-spectral-analysis|note 07]].

**10. Build a spectrogram of a chirp.**
Synthesise a tone that sweeps from 200 Hz to 2000 Hz over a few seconds. Plot its spectrogram (`scipy.signal.spectrogram`). Then redo it with a short window and a long window.
**Done when:** you see the frequency ramp diagonally, and you can show the time-frequency trade — short window = crisp timing/blurry frequency, long window = the reverse (the uncertainty principle, visible) → [[foundations/digital-signal-processing/07-spectral-analysis|note 07]].

---

## Part D — Radio, optional but the best part (note 08) — needs an RTL-SDR (~$30)

**11. Look at real spectrum.**
With an RTL-SDR and `pyrtlsdr` (or GNU Radio), capture I/Q from the FM broadcast band and plot the spectrum. Identify individual stations as peaks.
**Done when:** you can point at peaks and match them to real station frequencies → [[foundations/digital-signal-processing/08-modulation-and-sdr|note 08]].

**12. Decode aircraft (ADS-B).**
Tune to 1090 MHz and decode ADS-B transponder messages (`dump1090`), then plot the aircraft on a map.
**Done when:** real planes overhead appear on your map, decoded from raw radio *you* captured — the most tangible payoff in this whole folder, and legal because you're only receiving → [[foundations/digital-signal-processing/08-modulation-and-sdr|note 08]].

---

## The meta-point

If you do only three: **#1** (a tone becomes a spike — the frequency domain made concrete), **#5** (prove the convolution theorem — the hinge of the field), and **#2** (make aliasing happen — the sampling theorem you can hear). Then buy the dongle for #11–12.

## Related
- [[foundations/digital-signal-processing/README|the DSP course]] · [[foundations/digital-signal-processing/projects|projects]] — the larger builds
- [[foundations/digital-signal-processing/11-practice-exercises-solutions|solutions]]
