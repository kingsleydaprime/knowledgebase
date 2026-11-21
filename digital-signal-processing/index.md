# Digital Signal Processing

## What signal processing is

**Digital signal processing (DSP) is turning real-world signals, like sound, radio waves and sensor readings, into numbers, and then using maths to clean them up, analyse them or change them.**

When you speak into your phone, the microphone produces a wavy electrical signal. The phone measures it thousands of times a second and turns it into a list of numbers. DSP is what happens next: removing background noise, compressing it to send, and decoding what arrives on the other side. The same ideas run in music apps, noise-cancelling headphones, Wi-Fi, medical scanners, and the image-recognition layers of AI models.

Two ideas unlock the whole subject. First, **any signal can be described as a mix of simple waves** at different frequencies, like a chord made of notes, so removing noise often means removing certain frequencies. Second, **convolution**, a way of sliding one signal across another, is how filters work, and it's the same operation at the heart of image-recognition AI.

## What you'll be able to do

By the end you will be able to:
- explain how a smooth signal becomes a list of numbers, and how often you must measure to avoid distorting it;
- break any signal into its frequencies, quickly, with the FFT;
- explain convolution, and why it connects filters, signal processing and image AI;
- design simple filters that remove unwanted frequencies;
- analyse real recordings and read a spectrogram (a picture of frequencies over time);
- explain how data is carried on radio waves, and receive real radio with a cheap USB receiver.

## Where to start

**Before you start:** some [[mathematics/03-geometry-trigonometry/index|trigonometry]] (sine waves) and basic programming in Python. Complex numbers help for later notes.

Read notes 01–05 in order; they're the core. Notes 06–09 apply it.

1. [[digital-signal-processing/01-signals-and-systems|Signals and Systems]]: what a signal and a system are, and the special kind of system you can describe completely by how it responds to one short click.
2. [[digital-signal-processing/02-sampling-and-aliasing|Sampling and Aliasing]]: turning a smooth signal into numbers, why you must measure more than twice as fast as the highest frequency, and the distortion you can never undo if you don't.
3. [[digital-signal-processing/03-the-frequency-domain|The Frequency Domain]]: the central idea: any signal is a sum of simple waves, and seeing it that way makes hard problems easy.
4. [[digital-signal-processing/04-the-fft|The FFT]]: the fast method for breaking a signal into frequencies, which made real-time signal processing possible everywhere.
5. [[digital-signal-processing/05-convolution-and-lti-systems|Convolution and LTI Systems]]: sliding one signal across another, why it equals multiplying their frequencies, and why it's the heart of image-recognition AI.
6. [[digital-signal-processing/06-digital-filters|Digital Filters]]: keeping some frequencies and removing others, the two main kinds of filter, and keeping them stable.
7. [[digital-signal-processing/07-spectral-analysis|Spectral Analysis]]: measuring the frequencies in real, messy recordings, and the trade-off between precision in time and in frequency.
8. [[digital-signal-processing/08-modulation-and-sdr|Modulation and SDR]]: how data rides on radio waves, and software-defined radio, where a computer does the work of a radio's circuits.
9. [[digital-signal-processing/09-dsp-in-practice|DSP in Practice]]: the tools, doing the maths with whole numbers on small chips, and how much everyday technology quietly relies on DSP.

## Practice

- [[digital-signal-processing/10-practice-exercises|Practice Exercises]]: twelve short Python scripts, such as watching a tone become a single spike, hearing aliasing, and proving the convolution rule, plus two exercises with a real radio receiver.
- [[digital-signal-processing/11-practice-exercises-solutions|Solutions]]: worked answers. Try first.
- [[digital-signal-processing/projects|Projects]]: hands-on tasks with a clear "done when". A USB radio receiver (RTL-SDR, around $30) turns the whole course into a working radio.

## Key ideas to remember

1. **Any signal is a mix of simple waves.** Filtering is choosing which ones to keep. → [[digital-signal-processing/03-the-frequency-domain|03]]
2. **Measure more than twice as fast as the highest frequency,** or high frequencies disguise themselves as low ones, permanently. → [[digital-signal-processing/02-sampling-and-aliasing|02]]
3. **Convolution in time equals multiplication in frequency.** This one rule ties the subject together. → [[digital-signal-processing/05-convolution-and-lti-systems|05]]
4. **An image-recognition network's convolution layer is DSP convolution** with patterns it learned itself. → [[digital-signal-processing/05-convolution-and-lti-systems|05]]

## Related

- [[information-theory/index|Information Theory]]: the limits on how much a signal can carry.
- [[hardware/06-radio-frequency|Radio Frequency]]: the physical side of radio.
- [[control-theory/index|Control Theory]]: the same maths of systems and stability.
- [[machine-learning/06-computer-vision/index|Computer Vision]]: convolution, learned.
- [[mathematics/07-applied-and-computational/01-numerical-methods/index|Numerical Methods]]: the computational maths next door.

---

## About this course

- **Size:** 9 notes plus practice, written in August 2026 to connect the hardware, radio and information theory courses.
- **Where it came from:** reference sources, not yet tested by building.
