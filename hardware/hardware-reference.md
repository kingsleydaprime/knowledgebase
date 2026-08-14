# Hardware Reference

**[reference]** — units, prefixes, and the formulas. Lookup, not reading; split out of the old `fundamentals.md` monolith so it can be found without scrolling a course note.

## Units and Conversions

| Prefix | Symbol | Multiplier | Example |
|---|---|---|---|
| Mega | M | 10^6 | 2.4 MHz |
| Kilo | k | 10^3 | 4.7 kΩ |
| milli | m | 10^-3 | 100 mA |
| micro | µ | 10^-6 | 10 µA |
| nano | n | 10^-9 | 100 nF |
| pico | p | 10^-12 | 10 pF |

## Key Formulas

```
Ohm's Law:      V = I × R
Power:          P = V × I
Frequency:      f = 1 / T          (T = period in seconds)
Wavelength:     λ = c / f          (c = 3×10^8 m/s)
ADC resolution: steps = 2^n        (n = bit depth)
dBm to mW:      P(mW) = 10^(dBm/10)
Battery life:   hours = mAh / mA_avg
```

## Related
- [[hardware/README|Hardware course index]]
- [[hardware/01-electricity|Electricity]] — where most of these formulas come from
