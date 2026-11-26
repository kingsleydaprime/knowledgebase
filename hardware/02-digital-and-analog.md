---
id: c807d936-1bdc-41b1-bf92-983e5502279b
---

# Digital vs Analog

An analog signal changes smoothly over a range, like the volume knob on an old radio, while a digital signal has only a few fixed values, usually on and off. The real world is analog, but computers only work in digital. This lesson covers the parts that convert between the two, so a device can read a sensor or dim a light.

## Analog: The Real World
<!-- bite: 37faea54-6610-4555-9040-3b6484c9ff52 -->

The real world is analog. Temperature doesn't jump from 25°C to 26°C — it slides through 25.1, 25.2, 25.37... infinitely. Sound is a continuously varying air pressure wave. Light intensity varies smoothly.

An analog signal can take **any value** within a range. A microphone output might swing between 0V and 3.3V with infinite resolution representing the audio waveform.

## Digital: What Computers Speak
<!-- bite: 64e121f4-0f45-42a1-93d7-20e0c38bee3f -->

Digital signals are binary — they're either HIGH (1) or LOW (0). In a 3.3V system, anything above ~2V is read as HIGH, anything below ~0.8V is LOW. The gap in between is undefined (and you should never design a system that idles there).

The advantage: digital signals are **noise-immune**. A tiny bit of interference on an analog signal corrupts your data. On a digital signal, as long as the corruption doesn't push a HIGH below the threshold or a LOW above it, the signal is read perfectly.

## ADC — The Bridge from Analog to Digital
<!-- bite: b2c512f7-2aab-4c1a-b145-cc0e0132657c -->

An **ADC (Analog to Digital Converter)** samples an analog signal and converts it to a number. Two key specs:

- **Resolution** — how many bits? A 10-bit ADC divides its voltage range into $2^{10} = 1024$ steps. A 12-bit ADC gives you 4096 steps. More bits = finer granularity.
- **Sample rate** — how many times per second it takes a reading. Audio needs at least 44,100 samples/sec (44.1 kHz). A temperature sensor might only need 1 sample/sec.

Most microcontrollers have built-in ADCs. When you plug a temperature sensor into an "analog pin," the MCU's ADC is converting that voltage to a number your code reads.

## DAC — The Bridge from Digital to Analog
<!-- bite: e45222ce-a03b-4ae8-96c2-4d39053283a2 -->

A **DAC (Digital to Analog Converter)** does the reverse — turns a number into a voltage. Used in audio output, motor speed control, generating arbitrary waveforms. Not all microcontrollers have true DAC outputs (many fake it with PWM — explained below).

## PWM — Faking Analog with Digital
<!-- bite: e69cde8a-bcef-4cb0-a00c-07ac8ccc7ad0 -->

**Pulse Width Modulation** is a technique where you rapidly switch a digital pin ON and OFF. If you switch fast enough and control *how long* it stays ON vs OFF (the "duty cycle"), the average voltage approximates an analog value.

```text
Duty cycle 0%   → average = 0V    (always LOW)
Duty cycle 50%  → average = 1.65V (half the time HIGH)
Duty cycle 100% → average = 3.3V  (always HIGH)
```

This is how you dim an LED, control a servo motor, or drive a buzzer. The frequency of the switching matters — for LEDs, above ~100Hz and your eyes can't see the flicker.

---

## Related
<!-- bite: d90871e3-b244-4bf7-8dde-b89184fda9c4 -->
- [[hardware/01-electricity|Electricity]] — the signals being converted
- [[hardware/04-microcontrollers|Microcontrollers]] — where the ADC/DAC peripherals actually live
- [[hardware/03-embedded-systems|Embedded Systems]] — reading a converted value in a firmware loop

## About this lesson
<!-- bite: f9f6938c-41ff-4a2d-928f-af1a3d946157 -->

**Level:** Beginner. **Covers:** The bridges between a continuous physical world and a CPU that only understands numbers: ADC, DAC, and PWM.
