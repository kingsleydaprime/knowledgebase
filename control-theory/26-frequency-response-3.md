---
id: 36d16115-f222-49c9-b6be-97ccbe8853f2
---

# Frequency Response 3: Reading Bode Plots and Design by Gain Adjustment

A Bode plot read backwards gives a system's type and error constants, and the gain alone can set its margins.

## Before you start
<!-- bite: 7f9c97fa-d47c-4a2a-b7ea-b54373e0bc82 -->

You should have read [[control-theory/25-frequency-response-2|25 — Frequency Response 2: Loop Shaping, Bandwidth and Margins]], and know the error constants ([[control-theory/15-steady-state-error-1|15 — Steady-State Error 1: Test Inputs and Error Constants]]).

After this lesson you will be able to:

1. read the system type and error constant off a Bode magnitude plot;
2. recover a transfer function from its asymptotic Bode plot;
3. choose the gain that gives a required phase margin, gain margin or crossover frequency;
4. compute the closed-loop peak $M_p$, its frequency and the bandwidth from $\zeta$ and $\omega_n$.

## What this lesson covers
<!-- bite: 9442b8dd-d436-4dd6-b060-1756c63d866f -->

Lessons 24 and 25 went from a transfer function to its Bode plot and margins. The course notes' chapter 12 also goes the other way: given a *measured* Bode plot, what's the system? And it uses the simplest design tool there is, the gain, to set the margins. Finally it looks at the *closed* loop's frequency response, which connects back to overshoot.

## The kid version
<!-- bite: da751023-beb4-438a-ba83-7f6809a6f8b1 -->

A tailor can measure you and cut a suit (the transfer function to the Bode plot). A good tailor can also look at a suit and tell your measurements (the plot back to the transfer function). And sometimes the only alteration needed is lengthening the whole suit evenly: that's adjusting the gain, which slides the magnitude plot up or down without changing its shape.

**Where the analogy stops working.** Lengthening a suit doesn't change how it hangs. Changing the gain does change the margins, because it moves where the magnitude crosses 0 dB, and the phase there is different.

## The type from the low-frequency slope
<!-- bite: 704fccd3-b3a9-449a-b6f3-90fef0254e3e -->

At low frequency only the gain and the integrators matter, so the first slope gives the type and the error constant:

1. **Type 0**: flat at $20\log K_p$ dB.
2. **Type 1**: $-20$ dB per decade. Extended, it passes through $20\log K_v$ dB at $\omega = 1$, and crosses 0 dB at $\omega = K_v$.
3. **Type 2**: $-40$ dB per decade. Extended, it passes through $20\log K_a$ dB at $\omega = 1$, and crosses 0 dB at $\omega = \sqrt{K_a}$.

The course notes' example 2: the plot starts at $-40$ dB per decade (type 2), and its extension crosses 0 dB at 3 rad/s. So $K_a = 3^2 = 9$, matching the 19.1 dB it shows at $\omega = 1$ ($20\log 9 = 19.1$). Their example 3 is flat at 25 dB: type 0, $K_p = 10^{25/20} = 17.8$.

## The transfer function from the slopes
<!-- bite: 2a23df7a-1ff9-4556-a881-5140d22a805e -->

Every asymptotic slope change marks a corner:

1. Slope **falls** by 20 dB per decade at $\omega_1$: a real pole at $\omega_1$, a factor $1/(1 + s/\omega_1)$.
2. Falls by 40: a pair of poles (or a quadratic) there.
3. **Rises** by 20 at $\omega_1$: a real zero, a factor $(1 + s/\omega_1)$. Rises by 40: a quadratic zero.

So a measured plot that starts at $-20$, turns to $-40$ at 1 rad/s and to $-60$ at 2 rad/s, with the initial slope crossing 0 dB at 0.5, is $\dfrac{0.5}{s(1 + s)(1 + s/2)} = \dfrac{1}{s(s+1)(s+2)}$: our running loop. With $K_v = 0.5$.

## Design by gain adjustment
<!-- bite: 4a0ed00d-528e-4881-aaaf-5c315be54f46 -->

Changing the gain $K$ slides the whole magnitude plot up or down by $20\log K$ dB and leaves the phase alone. So:

1. Draw the Bode plot with $K = 1$.
2. For a **phase margin** target: find the frequency where the phase is $-180° + \text{PM}$. That must become the crossover, so choose $K$ to make the magnitude 0 dB there.
3. For a **gain margin** target: find where the phase is $-180°$, and choose $K$ so the magnitude there is $-\text{GM}$ dB.
4. For a **crossover** target: make the magnitude 0 dB at that frequency.

## Gain adjustment worked
<!-- bite: bbd07b78-0411-4b9b-b0db-747437b908a6 -->

Our loop $K/(s(s+1)(s+2))$: what $K$ gives a phase margin of 45°? Predict: more or less than 1?

1. The phase must be $-135°$ at the new crossover: $-90° - \tan^{-1}\omega - \tan^{-1}(\omega/2) = -135°$ at $\omega = 0.562$ rad/s.
2. There $|L|$ with $K = 1$ is $1/(0.562 \times \sqrt{1.316} \times \sqrt{4.316}) = 0.747$, so $K = 1/0.747 = 1.34$.
3. The gain margin is then $6/1.34 = 4.48$, or 13.0 dB.

For 60° the crossover moves down to 0.36 rad/s and $K = 0.78$. More margin, less gain, slower loop: the trade from lesson 25, now with numbers.

## The closed-loop frequency response
<!-- bite: 5246b94e-ce03-46ee-ac3f-c73a538f425e -->

The closed loop $T(j\omega)$ has its own magnitude plot. For a second-order closed loop it has a peak (for $\zeta < 0.707$):

$$M_p = \frac{1}{2\zeta\sqrt{1 - \zeta^2}} \quad\text{at}\quad \omega_p = \omega_n\sqrt{1 - 2\zeta^2}$$

and its **bandwidth**, where it has fallen 3 dB below its zero-frequency value, is

$$\omega_{BW} = \omega_n\sqrt{(1 - 2\zeta^2) + \sqrt{4\zeta^4 - 4\zeta^2 + 2}}$$

These link straight back to the step response: $\zeta$ sets both overshoot and $M_p$, and $\omega_n$ scales both speed and bandwidth.

## Worked: bandwidth from a step specification
<!-- bite: 3a30a173-4794-46da-8531-1b33c95b563f -->

The course notes' example 6: what closed-loop bandwidth gives 20% overshoot and a 2 s settling time?

1. 20% overshoot: $\zeta = 0.456$.
2. Settling: $4/(\zeta\omega_n) = 2$, so $\omega_n = 4.39$ rad/s.
3. Bandwidth: $\omega_{BW} = 4.39\sqrt{(1 - 0.416) + \sqrt{0.173 - 0.832 + 2}} = 5.79$ rad/s.

The same system peaks at $M_p = 1.23$ (1.8 dB) at $\omega_p = 3.35$ rad/s.

## Common pitfalls
<!-- bite: 52d35917-daad-49fa-88ec-f598e0b5b9f4 -->

1. **Reading $K_v$ at the wrong place.** Use the *extension* of the initial $-20$ slope at $\omega = 1$, or where it crosses 0 dB.
2. **Changing the phase plot when adjusting gain.** Gain shifts magnitude only.
3. **Mixing open- and closed-loop peaks.** $M_p$ here is the closed loop's.
4. **Taking the bandwidth from the open-loop plot.** It's the closed loop's −3 dB point (roughly the open-loop crossover).

## Check your understanding
<!-- bite: f3f7d14e-e3a8-4717-ba82-d40840e0d71e -->

Try each one before you open the answer.

1. <!-- q: exact id="4f9c2e17" answer="25" -->
   A Bode plot starts at $-40$ dB per decade, and its extension crosses 0 dB at 5 rad/s. What is $K_a$?

   <details><summary>Answer</summary>

   Type 2, so $K_a = 5^2 = 25$.

   </details>

2. <!-- q: exact id="a2d61b08" answer="0.25" accept="1/4" -->
   A type-1 Bode plot's initial $-20$ dB per decade line, extended, crosses 0 dB at 4 rad/s. What is the steady-state error to a unit ramp?

   <details><summary>Answer</summary>

   The crossing frequency equals $K_v$, so $K_v = 4$ and $e_{ss} = 1/K_v = 0.25$.

   </details>

3. <!-- q: mcq id="7c5e0d93" -->
   An asymptotic magnitude plot changes from $-20$ to $-60$ dB per decade at 10 rad/s. What does that mean?

   - [ ] A zero at 10 rad/s
   - [ ] One pole at 10 rad/s
   - [x] Two poles (or a quadratic pole pair) at 10 rad/s
   - [ ] An integrator

   <details><summary>Answer</summary>

   A fall of 40 dB per decade means two poles at that corner.

   </details>

4. <!-- q: exact id="e6b3f520" answer="-20" accept="−20" -->
   At the frequency where a loop's phase is $-180° + 45°$, its magnitude with $K = 1$ is $+20$ dB. By how many dB must the gain change to give a 45° phase margin?

   <details><summary>Answer</summary>

   That point must become the 0 dB crossover, so lower the magnitude by 20 dB: $20\log K = -20$, $K = 0.1$.

   </details>

5. <!-- q: exact id="19a8c7d4" answer="1.1547" sigfigs="3" -->
   A closed loop has $\zeta = 0.5$. What is its peak magnitude $M_p$ (not dB)?

   <details><summary>Answer</summary>

   $1/(2 \times 0.5 \times \sqrt{0.75}) = 1.155$.

   </details>

## Before moving on
<!-- bite: e47384d9-cd65-4002-a565-1eec4ad3c7ba -->

You can read a Bode plot backwards, design by gain adjustment, and link closed-loop peak and bandwidth to the step response. **Next:** [[control-theory/27-nyquist-1|27 — Nyquist 1: The Nyquist Criterion]].

## Related
<!-- bite: ca34c01c-7fb9-4b22-833a-096fd7ef0994 -->

- [[control-theory/24-frequency-response-1|24 — Frequency Response 1: Bode Plots]]: drawing Bode plots.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: 72cd7a1d-1e02-4243-b5f3-66d93fbc7d9c -->

**Level:** Intermediate. **Covers:** type and error constants from the low-frequency slope, transfer functions from asymptotic plots, design by gain adjustment, and the closed-loop peak and bandwidth.

**Where it sits:** lesson 26 of 58, part 3 of 3 on frequency response.

**Source:** the author's course notes, A. M. Hussein, *Control Engineering*, Benha University, chapter 12 (sections 6 and 7, examples 2 to 7). Numbers checked in `scripts/diagrams/control_theory.py`.
