---
id: 57b35b19-1574-48d1-a572-56c1be2e24e6
---

# Time Response 2: Dominant Poles, Delay and Step Tests

Slow poles dominate the response, delay is the worst thing a loop can hold, and a step test turns a measured response into a model.

## Before you start
<!-- bite: 78a404c3-ac10-4229-ab28-4be176c3291d -->

You should have read [[control-theory/13-time-response-1|13 — Time Response 1: First- and Second-Order Systems]], and be able to work out overshoot and settling time from $\zeta$ and $\omega_n$.

After this lesson you will be able to:

1. decide when a high-order system can be treated as second order;
2. explain why delay is so harmful, estimate its effect with the Padé approximation, and list where delay comes from;
3. read a first-order-plus-dead-time model off a step test, and judge how hard the plant is to control.

## What this lesson covers
<!-- bite: 53e463dc-4034-4c89-9db0-82f09ad75821 -->

Lesson 13's formulas are for perfect first- and second-order systems. Real plants have more poles than that, so the first question is when the formulas still work. The second is the enemy hiding in every real loop: delay. And the third is practical: how to get a model from a measured response when you can't derive one.

## The kid version
<!-- bite: 6bbaf73e-2e7e-47cc-8852-079bb47ec343 -->

You're in a shower with a slow tap. You turn it hotter and nothing happens, so you turn it more. Then both turns arrive at once and you're scalded, so you turn it cold, and the same thing happens the other way. The tap isn't the problem; the delay between turning and feeling is.

**Where the analogy stops working.** In the shower you eventually learn to wait. A controller only waits if it was designed to, and the only cure for delay is a slower loop or a model that predicts what the delayed output will be.

## Dominant poles
<!-- bite: db13cde3-5b89-422a-a374-3112262723bb -->

Here is the approximation that makes classical design work: **poles far to the left die out fast and barely matter; the response is dominated by the poles closest to the imaginary axis.**

Rule of thumb: if the other poles are at least **five times further left** than the dominant pair, treat the system as second order and use lesson 13's formulas.

## Dominant poles: an example
<!-- bite: 98db8c31-9255-47d7-abbc-bd0fba85e9e1 -->

Here is a pair at $-0.5 \pm 0.87j$, alone and with a third pole added at two different places.

![Step responses of a second-order system with poles at minus 0.5 plus or minus 0.87j, alone, with an extra pole at minus 5, and with an extra pole at minus 1. The pole at minus 5 barely changes the curve; the pole at minus 1 slows it noticeably and cuts the overshoot.](images/ct-dominant-poles.svg)

The extra pole at $-5$ is ten times further left than the pair's real part ($-0.5$), and the curve hardly changes. The one at $-1$ is only twice as far, and it slows the response and cuts the overshoot. This is the first thing to check when a system doesn't behave as designed: a neglected pole or an unmodelled delay has crept close enough to matter.

## Time delay
<!-- bite: fc5795aa-a20e-46d3-984a-1a1b253bda9d -->

A pure delay of $T$ seconds has transfer function

$$G_{delay}(s) = e^{-sT}$$

It doesn't change how big a signal is at any frequency, but it shifts it later, and the faster the signal wobbles, the bigger that shift is as a fraction of a wobble. Lesson 25 shows this is exactly what eats a loop's safety margin, while giving nothing back.

For analysis, $e^{-sT}$ is often replaced by a ratio of polynomials, the **Padé approximation**:

$$e^{-sT} \approx \frac{1 - sT/2}{1 + sT/2}$$

Look at the numerator: a zero at $s = +2/T$, in the right half plane. So delay behaves like the wrong-way plants of lesson 03, with the same speed limit.

## Where delay comes from
<!-- bite: e8a2a48b-ce47-42ac-a00d-ff36eb6aaee7 -->

All of these count, and they add up:

1. **Transport**: fluid travelling down a pipe, material on a conveyor.
2. **Sensors**: processing and filtering take time.
3. **Computation**: the controller takes time to calculate.
4. **Sampling**: a digital controller holds each command for one sample period, an average delay of half a sample. → [[control-theory/44-digital-control-1|44 — Digital Control 1: Sampling and the z-Transform]]
5. **Networks**: messages between parts of a distributed system.

Delay is why cloud autoscaling oscillates: new servers take minutes to boot, so the controller keeps adding more while the first batch is still starting. The classic remedy is the **Smith predictor**: use a model to predict what the delayed output *will* be and control against the prediction. It works well when the delay is known and steady, and badly when it isn't.

## Reading a real step test
<!-- bite: 5fdca932-1d60-4a4e-9c37-029cc37483f0 -->

This is the practical skill: getting a model from data. Step the input of an unknown plant and record the output.

![A step test of a process with gain 2, dead time 3 seconds and time constant 10 seconds: the output stays flat for 3 seconds, then rises; the steepest tangent crosses the starting level at 3 seconds and the final value at 13 seconds, and the output settles at 2.](images/ct-step-test.svg)

## Reading the step test: the numbers
<!-- bite: 552d9895-8a99-4318-bd6f-392a4ebd92e6 -->

From that picture, read off three numbers:

1. **Dead time $\theta$**: the flat bit before anything happens. Here 3 s.
2. **Time constant $\tau$**: draw the steepest tangent; from where it leaves the start level to where it meets the final value is $\tau$. Here $13 - 3 = 10$ s.
3. **Gain $K$**: final change divided by step size. Here 2.
4. For an oscillating response, overshoot gives $\zeta$ (lesson 13's table) and the wobble period gives $\omega_d$.

That gives $G(s) = 2e^{-3s}/(10s + 1)$, enough to design a controller. This is what Ziegler–Nichols tuning does (lesson 18).

**The ratio $\theta/\tau$ is the most useful number** from the test: below about 0.2 the loop is easy; above about 1 it's genuinely hard, and no PID tuning will make it fast. Here it is 0.3.

## Common pitfalls
<!-- bite: 7d27d4a4-cfc0-4e5a-990c-d93b9ee367c2 -->

1. **Applying second-order formulas when a third pole is close.** Check the five-times rule first.
2. **Ignoring small delays.** Sensor filtering plus computing plus sampling adds up, and it all costs margin.
3. **Measuring $\tau$ from $t = 0$.** Measure it from the end of the dead time.

## Check your understanding
<!-- bite: 063b914e-de7f-4dcc-aaee-1e77ed5274d3 -->

Try each one before you open the answer.

1. <!-- q: mcq id="f3a9c021" -->
   A system has poles at $-1 \pm 2j$ and $-12$. Can you use second-order formulas from the pair?

   - [x] Yes: $-12$ is more than five times further left than $-1$
   - [ ] No: any third pole breaks the formulas
   - [ ] No: the third pole is real
   - [ ] Only if the third pole is on the imaginary axis

   <details><summary>Answer</summary>

   Yes. The pair's real part is $-1$, and $-12$ is twelve times further left, so it dies away quickly and the pair dominates.

   </details>

2. <!-- q: gap id="7e0b2d94" answers="5;12;3" -->
   A step test: the output stays flat for 5 s, the steepest tangent meets the final value at 17 s, and a step of 2 units moves the output by 6 units. The dead time is ___ s, the time constant is ___ s and the gain is ___.

   <details><summary>Answer</summary>

   Dead time 5 s; time constant $17 - 5 = 12$ s; gain $6/2 = 3$.

   </details>

3. <!-- q: exact id="b6f2e8a1" answer="20" -->
   A loop has a pure delay of 0.1 s. Using the Padé approximation $e^{-sT} \approx (1 - sT/2)/(1 + sT/2)$, where is the right-half-plane zero?

   <details><summary>Answer</summary>

   At $s = 2/T = 20$. That zero caps the loop's speed, like any right-half-plane zero.

   </details>

4. <!-- q: mcq id="5d0a7c39" -->
   A step test gives dead time 8 s and time constant 6 s. How hard is this plant to control?

   - [ ] Easy: $\theta/\tau$ is below 0.2
   - [ ] Moderate: $\theta/\tau$ is about 0.5
   - [x] Hard: $\theta/\tau$ is above 1, and no PID tuning will make it fast
   - [ ] It can't be judged from a step test

   <details><summary>Answer</summary>

   $\theta/\tau = 8/6 = 1.33$, above 1: delay-dominated and genuinely hard.

   </details>

## Before moving on
<!-- bite: aafad689-04a2-4e02-86ea-1fe9206c37e9 -->

You can check the dominant-pole rule, cost a delay and fit a model to a step test. **Next:** [[control-theory/15-steady-state-error-1|15 — Steady-State Error 1: Test Inputs and Error Constants]], which answers the question we've carried since lesson 01: why did the cruise control settle at 18.18 m/s instead of 20?

## Related
<!-- bite: c0956efa-ed97-4488-b589-3365178a3f40 -->

- [[control-theory/25-frequency-response-2|25 — Frequency Response 2: Loop Shaping, Bandwidth and Margins]]: delay and phase margin.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: a256fd5f-fc54-4505-90e6-6a37f183183a -->

**Level:** Intermediate. **Covers:** dominant poles, time delay and the Padé approximation, and reading a first-order-plus-dead-time model from a step test.

**Where it sits:** lesson 14 of 58, part 2 of 2 on time response.

**Source:** `[reference]`, assembled from standard control texts. Diagrams and numbers from `scripts/diagrams/control_theory.py`.
