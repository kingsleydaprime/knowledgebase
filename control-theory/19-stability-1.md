---
id: 8844a418-f95f-4fe1-ae7e-5029138a5078
---

# Stability 1: What Stability Means and Routh–Hurwitz

A stable system settles down after a change instead of running away or shaking harder and harder, and Routh–Hurwitz tests for it without solving for the poles.

## Before you start
<!-- bite: 131bb161-eecb-433f-860d-f2e5a3f71908 -->

You should have read [[control-theory/08-block-diagrams-1|08 — Block Diagrams 1: Connections and the Feedback Rule]], and know that the closed-loop poles are the roots of $1 + L(s) = 0$.

After this lesson you will be able to:

1. define BIBO stability and give the pole test for it;
2. say why marginal stability should be treated as unstable;
3. build a Routh array and count the right-half-plane roots;
4. find the range of gain that keeps a loop stable, and the gain and frequency where it starts to oscillate.

## What stability means
<!-- bite: a15f1623-3328-4a5d-8370-65955a83b94c -->

Hold a microphone too close to its speaker and it squeals, louder and louder. The sound from the speaker goes into the microphone, gets amplified, comes out louder, goes back in... That's an unstable loop: a small disturbance grows by itself.

The formal idea is **BIBO stability**, which stands for bounded input, bounded output: no input that stays within limits can ever make the output grow without limit. For a linear system that's the same as the pole rule from lesson 03:

$$\boxed{\text{Stable} \iff \text{every closed-loop pole has a negative real part}}$$

And remember **closed-loop**: the poles that matter are the roots of $1 + L(s) = 0$, not the plant's own poles. Feedback can steady an unstable plant (that's the point of it) and it can also shake a stable plant apart.

## The kid version
<!-- bite: 14d10c91-a0c7-423c-ad4c-c068ecd4c06b -->

Put a marble in a bowl and nudge it: it rolls back and settles at the bottom. That's stable. Balance it on an upside-down bowl and nudge it: it rolls off and never comes back. Unstable. Put it on a flat table: nudged, it rolls a little way and stays. That's marginal.

**Where the analogy stops working.** A bowl's shape is fixed. In a feedback loop, turning up the controller's gain can quietly reshape the bowl into a hill, so the same plant goes from stable to unstable as you turn one knob. That's what this lesson and the next measure.

## The three cases
<!-- bite: f9bcdf65-363f-4208-b4ed-9695ac9159ec -->

1. **All poles in the left half plane**: stable. Every term in the response decays.
2. **Any pole in the right half plane**: unstable. Some term grows without bound.
3. **Single poles on the imaginary axis, none on the right**: marginally stable. A wobble that neither grows nor dies.

Remember this one: **marginal stability is not "just barely stable"; treat it as unstable.** Two poles at the same point on the axis actually grow, and any real plant has enough model error that a pole "on" the axis is really somewhere unknown near it, possibly on the wrong side.

## Routh–Hurwitz: the free check first
<!-- bite: d57fac8d-37dd-414c-9d6c-b377c16fa657 -->

You can test stability **without finding the roots**, which matters because a polynomial of degree 5 or more has no formula for its roots. Write the characteristic polynomial as

$$a_n s^n + a_{n-1}s^{n-1} + \cdots + a_1 s + a_0 = 0$$

**The free check:** every coefficient must be present and have the same sign. A missing term or a sign change means unstable, and you can stop. It isn't enough on its own, though: from degree 3 up, all-positive coefficients can still hide a right-half-plane root.

## The Routh array
<!-- bite: 544aac77-2c9a-433e-b362-29c3c7b9ca29 -->

For the full test, build the **Routh array**. The first two rows are the coefficients, taken alternately. Each later row is built from the two rows above it by a cross-multiplication. For a cubic $s^3 + a_2 s^2 + a_1 s + a_0$:

| | first column | second column |
| --- | --- | --- |
| $s^3$ | 1 | $a_1$ |
| $s^2$ | $a_2$ | $a_0$ |
| $s^1$ | $b_1 = (a_2a_1 - a_0)/a_2$ | 0 |
| $s^0$ | $a_0$ | |

Then the rule, in words: **the number of sign changes down the first column equals the number of roots in the right half plane.** No sign changes, stable.

For a cubic that boils down to: stable when all coefficients are positive **and** $a_2a_1 > a_0$.

## Routh with the gain left in
<!-- bite: aea6bdf4-f9e2-418e-b428-25f45707564d -->

What makes Routh genuinely useful is leaving the gain $K$ as a letter. Take a motor position loop with a two-stage drive, $L(s) = K/(s(s+1)(s+2))$. Its characteristic equation is $s(s+1)(s+2) + K = 0$:

$$s^3 + 3s^2 + 2s + K = 0$$

| | first column | second column |
| --- | --- | --- |
| $s^3$ | 1 | 2 |
| $s^2$ | 3 | $K$ |
| $s^1$ | $(6 - K)/3$ | 0 |
| $s^0$ | $K$ | |

Before reading on, predict: for which $K$ are there no sign changes?

## The stable range and the ultimate gain
<!-- bite: ba1b7d65-9fd8-431d-913e-d9b94e9ae9ad -->

The first column is $1,\ 3,\ (6-K)/3,\ K$. All positive needs $K > 0$ and $6 - K > 0$:

$$0 < K < 6$$

At $K = 6$ the $s^1$ row is all zero: the poles sit on the imaginary axis and the loop oscillates steadily. That gain is the **ultimate gain** $K_u$ from Ziegler–Nichols (lesson 18). The row above gives the **auxiliary equation** $3s^2 + K = 0$, so $3s^2 + 6 = 0$ and $s = \pm j\sqrt{2}$. The loop oscillates at $\omega = 1.414$ rad/s, a period $T_u = 2\pi/1.414 = 4.44$ s.

So Routh gives the Ziegler–Nichols test numbers on paper, without having to drive a real plant into oscillation.

## Stability isn't yes or no
<!-- bite: 29f90074-cf10-4207-a329-12dfe9963f45 -->

Knowing a loop is stable tells you surprisingly little. A pole at $-0.001$ is stable and takes over an hour to settle. A design that goes unstable if the plant gain rises 5% is stable *and useless*.

What you need is a **margin**: how much can the plant change before stability is lost? With the loop above, running at $K = 2$ leaves a factor of 3 before $K_u = 6$. That factor is called the **gain margin**.

Lesson 21 shows the poles moving as $K$ grows, which lets you see how close the loop is to the edge. The systematic answer, gain and phase margin read off a frequency plot, comes in lessons 25 and 27, and that's what working engineers design against.

## Common pitfalls
<!-- bite: 113f9774-960d-404b-b73a-710565c3f4b2 -->

1. **Testing the plant's poles instead of the closed loop's.** Stability is about the roots of $1 + L = 0$.
2. **Stopping at "all coefficients positive".** That's necessary, not sufficient, from degree 3 up.
3. **Calling marginal stability safe.** It isn't.
4. **Forgetting that an all-zero row means poles on the axis.** Use the row above it to find where.

## Check your understanding
<!-- bite: 3d111e68-3486-45a4-914a-b38cbb148827 -->

Try each one before you open the answer.

1. <!-- q: mcq id="1a8e5f37" -->
   Which characteristic polynomial is certainly unstable, without building a Routh array?

   - [ ] $s^3 + 4s^2 + 5s + 2$
   - [x] $s^3 + 2s^2 - s + 6$
   - [ ] $s^2 + 3s + 7$
   - [ ] $s^4 + s^3 + 4s^2 + 2s + 1$

   <details><summary>Answer</summary>

   $s^3 + 2s^2 - s + 6$ has a coefficient with a different sign, which is enough to show a right-half-plane root.

   </details>

2. <!-- q: exact id="b3d06c42" answer="2" -->
   A Routh array's first column is $1,\ 4,\ -2,\ 5$. How many poles are in the right half plane?

   <details><summary>Answer</summary>

   Two sign changes: $4 \to -2$ and $-2 \to 5$. So two right-half-plane poles.

   </details>

3. <!-- q: exact id="7f2c91e0" answer="20" -->
   A loop has characteristic equation $s^3 + 4s^2 + 5s + K = 0$. What is the largest $K$ for which it is stable (the ultimate gain)?

   <details><summary>Answer</summary>

   For a cubic, stable needs $a_2a_1 > a_0$: $4 \times 5 > K$, so $K < 20$. The ultimate gain is 20.

   </details>

4. <!-- q: exact id="c5a8e2d1" answer="2.236" sigfigs="3" -->
   Same loop, $s^3 + 4s^2 + 5s + K = 0$, at $K = 20$. At what frequency $\omega$ (rad/s) does it oscillate?

   <details><summary>Answer</summary>

   Auxiliary equation from the $s^2$ row: $4s^2 + 20 = 0$, so $s = \pm j\sqrt{5}$ and $\omega = 2.24$ rad/s.

   </details>

5. <!-- q: open id="e96b0f24" -->
   A system has a single pair of poles exactly at $\pm 3j$ in the model. Why should an engineer treat it as unstable?

   <details><summary>Answer</summary>

   The model is never exact, so the real poles are somewhere near $\pm 3j$, possibly just inside the right half plane, where the oscillation grows. Even at best it never dies away, so any disturbance leaves a permanent wobble.

   </details>

## Before moving on
<!-- bite: 52b585bc-cda7-4550-bed5-9e9466f0c46d -->

You can test stability with Routh and find the stable gain range and the ultimate gain. **Next:** [[control-theory/20-stability-2|20 — Stability 2: Routh's Special Cases and Stability Design]], which handles the two ways the Routh table can break, and uses it to design.

## Related
<!-- bite: fee6d490-963c-4a98-9f3a-1e30d6cabe08 -->

- [[control-theory/18-pid-control-2|18 — PID Control 2: Tuning and Implementation]]: the ultimate gain in Ziegler–Nichols.
- [[control-theory/52-lyapunov-stability-1|52 — Lyapunov Stability 1: What Stable Means]]: what stability means for nonlinear systems.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: 45978057-05e9-4a73-a753-e41bd38eb103 -->

**Level:** Intermediate. **Covers:** BIBO stability, the three pole cases, the Routh–Hurwitz test, the stable gain range and ultimate gain, and why stability needs a margin.

**Where it sits:** lesson 19 of 58, part 1 of 2 on stability.

**Source:** `[reference]`, assembled from standard control texts. The numbers are checked in `scripts/diagrams/control_theory.py`.
