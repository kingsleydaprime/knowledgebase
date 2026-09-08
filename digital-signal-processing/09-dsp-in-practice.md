# DSP in Practice

**[Intermediate]** — the tooling, the applications that show DSP is everywhere, and the one hardware reality that separates textbook DSP from shipped DSP.

## The kid version first

Everything in this folder is maths until you run it on real signals. **In practice DSP is: load samples, transform, filter, measure, reconstruct** — usually in a few lines of NumPy/SciPy for analysis, or in C on a tiny chip for real-time work. This note is where the concepts meet the keyboard, and where you see how many things you use every day are quietly DSP.

## The tooling

**For learning and analysis — Python:**

```python
import numpy as np
from scipy import signal, fft
import matplotlib.pyplot as plt

# the whole workflow in five lines
x = np.loadtxt("signal.csv")                    # samples
X = fft.rfft(x * signal.windows.hann(len(x)))   # windowed spectrum
b, a = signal.butter(4, 0.2)                     # a 4th-order low-pass
y = signal.filtfilt(b, a, x)                     # zero-phase filtering
plt.specgram(x, Fs=fs)                           # a spectrogram, one call
```

**`scipy.signal` is the workhorse** — filter design, convolution, spectrograms, resampling, all of it → [[ai-ml/00-foundations/04-python-and-data-tools/README|the Python data stack]]. **`librosa`** for audio specifically (loading, mel-spectrograms, feature extraction). **`numpy.fft`** or `scipy.fft` for transforms. **This is where you should learn DSP** — instant feedback, plots, no hardware.

**For real-time and embedded — C/C++:**
- **CMSIS-DSP** — ARM's optimised library for microcontrollers → [[hardware/03-embedded-systems|embedded]]
- Vendor libraries for DSP chips (TI, Analog Devices)
- The maths is identical; the constraints (fixed-point, latency, memory) are the whole difficulty

**For radio — GNU Radio** + an RTL-SDR dongle → [[foundations/digital-signal-processing/08-modulation-and-sdr|SDR]]. **MATLAB/Octave** remains common in academia and legacy signal-processing shops.

## Fixed-point vs floating-point — the hardware reality

**This is the single biggest gap between DSP-on-a-laptop and DSP-on-a-chip.**

Your NumPy code uses floating-point — huge dynamic range, you never think about it. **Cheap embedded DSP chips often have no floating-point unit**, so they use **fixed-point** integer arithmetic, and that changes everything:

- **You manage the decimal point yourself** (Q-format: how many bits are the fractional part). Get the scaling wrong and values overflow or lose all precision
- **Overflow wraps or saturates** — a large intermediate result silently becomes garbage or clamps
- **Coefficient quantisation destabilises filters** — an [[foundations/digital-signal-processing/06-digital-filters|IIR filter]] that's perfectly stable in floating-point can have a pole pushed *outside* the unit circle when its coefficients are rounded to fixed-point, and then it oscillates or explodes. **This is a real, shipped-product failure mode**

**Why bother with fixed-point:** it's faster, cheaper, and lower-power — critical for battery devices and high-volume chips. **The craft of embedded DSP is largely making floating-point algorithms survive fixed-point**, and it's why "it worked in my simulation" is not the end of the job → [[foundations/computer-architecture/02-data-representation|data representation]].

## DSP is genuinely everywhere

The point of this note is to make the ubiquity concrete — you interact with DSP constantly:

**Audio:**
- Every noise-cancelling headphone runs adaptive filters in real time
- MP3/AAC compression transforms to a frequency domain and discards the inaudible → [[foundations/information-theory/03-source-coding-and-compression|compression]]
- Voice assistants convert speech to [[foundations/digital-signal-processing/07-spectral-analysis|mel-spectrograms]] before the ML model sees it
- EQ, autotune, reverb, and every audio effect is filtering and convolution

**Images and video:**
- JPEG *is* DSP — the DCT (a Fourier relative), quantise, discard imperceptible detail
- Blur, sharpen, edge-detect are 2-D [[foundations/digital-signal-processing/05-convolution-and-lti-systems|convolution]] → [[foundations/computer-graphics/README|graphics]]

**Communications** — every phone, Wi-Fi router, GPS receiver and satellite link is DSP modulating and demodulating → [[foundations/digital-signal-processing/08-modulation-and-sdr|modulation]].

**Sensors and control** — filtering noisy accelerometer/gyro data (a Kalman filter has DSP in it), extracting a heartbeat from a noisy ECG → [[engineering/02-control-theory/10-observers-and-kalman|state estimation]], [[robotics/README|robotics]].

**Machine learning — the connection worth internalising:**
- **A CNN's convolution layer is DSP convolution** with learned kernels → [[ai-ml/02-ml-engineer/06-computer-vision/README|computer vision]]
- **Audio and speech models run on spectrograms**, not raw waveforms — the DSP front-end is half the pipeline
- **Data augmentation** (pitch shift, time stretch, adding noise) is DSP

**That so many fields reduce to "sample, transform, convolve, filter" is the reason DSP is a foundation**, not a niche.

## The practical workflow

How real signal work actually goes:

1. **Look at it — in both domains.** Plot the time signal *and* its spectrum before doing anything. Half of all "bugs" are visible immediately (a DC offset, a mains hum spike, clipping, obvious aliasing)
2. **Check the sample rate and units.** Most confusion is a mislabelled frequency axis or a wrong `fs` → [[foundations/digital-signal-processing/02-sampling-and-aliasing|sampling]]
3. **Filter conservatively.** It's easy to filter out signal along with noise; compare before/after spectra
4. **Prototype in Python, then port.** Get it right in floating-point NumPy where it's easy to inspect, *then* deal with fixed-point and real-time constraints
5. **Validate against reality**, like all of [[engineering/README|engineering]] — a filter that looks right in simulation must be checked on real recorded data with real noise

## Key insight

**DSP in practice is "sample, transform, filter, reconstruct" — a few lines of SciPy for analysis — and the one thing that separates it from textbook DSP is fixed-point arithmetic, where a filter that's stable in floating-point can destabilise once its coefficients are quantised for a cheap chip.** The reason to learn it despite the maths is ubiquity: audio, images, comms, sensors and even CNNs all reduce to the same handful of operations, so understanding convolution and the frequency domain pays off across an unusually wide span of the vault.

## Related
- [[foundations/digital-signal-processing/README|the DSP course]]
- [[ai-ml/02-ml-engineer/06-computer-vision/README|computer vision]] — convolution, learned
- [[hardware/03-embedded-systems|embedded systems]] — where fixed-point bites
- [[ai-ml/00-foundations/04-python-and-data-tools/README|the Python data stack]] — NumPy/SciPy

*Source: [reference] — Aug 2026.*
