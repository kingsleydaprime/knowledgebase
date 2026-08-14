# Digital vs Analog

**[Beginner]** — The bridges between a continuous physical world and a CPU that only understands numbers: ADC, DAC, and PWM.

## Analog: The Real World

The real world is analog. Temperature doesn't jump from 25°C to 26°C — it slides through 25.1, 25.2, 25.37... infinitely. Sound is a continuously varying air pressure wave. Light intensity varies smoothly.

An analog signal can take **any value** within a range. A microphone output might swing between 0V and 3.3V with infinite resolution representing the audio waveform.

## Digital: What Computers Speak

Digital signals are binary — they're either HIGH (1) or LOW (0). In a 3.3V system, anything above ~2V is read as HIGH, anything below ~0.8V is LOW. The gap in between is undefined (and you should never design a system that idles there).

The advantage: digital signals are **noise-immune**. A tiny bit of interference on an analog signal corrupts your data. On a digital signal, as long as the corruption doesn't push a HIGH below the threshold or a LOW above it, the signal is read perfectly.

## ADC — The Bridge from Analog to Digital

An **ADC (Analog to Digital Converter)** samples an analog signal and converts it to a number. Two key specs:

- **Resolution** — how many bits? A 10-bit ADC divides its voltage range into 2^10 = 1024 steps. A 12-bit ADC gives you 4096 steps. More bits = finer granularity.
- **Sample rate** — how many times per second it takes a reading. Audio needs at least 44,100 samples/sec (44.1 kHz). A temperature sensor might only need 1 sample/sec.

Most microcontrollers have built-in ADCs. When you plug a temperature sensor into an "analog pin," the MCU's ADC is converting that voltage to a number your code reads.

## DAC — The Bridge from Digital to Analog

A **DAC (Digital to Analog Converter)** does the reverse — turns a number into a voltage. Used in audio output, motor speed control, generating arbitrary waveforms. Not all microcontrollers have true DAC outputs (many fake it with PWM — explained below).

## PWM — Faking Analog with Digital

**Pulse Width Modulation** is a technique where you rapidly switch a digital pin ON and OFF. If you switch fast enough and control *how long* it stays ON vs OFF (the "duty cycle"), the average voltage approximates an analog value.

```
Duty cycle 0%   → average = 0V    (always LOW)
Duty cycle 50%  → average = 1.65V (half the time HIGH)
Duty cycle 100% → average = 3.3V  (always HIGH)
```

This is how you dim an LED, control a servo motor, or drive a buzzer. The frequency of the switching matters — for LEDs, above ~100Hz and your eyes can't see the flicker.

---

## Related
- [[hardware/01-electricity|Electricity]] — the signals being converted
- [[hardware/04-microcontrollers|Microcontrollers]] — where the ADC/DAC peripherals actually live
- [[hardware/03-embedded-systems|Embedded Systems]] — reading a converted value in a firmware loop
