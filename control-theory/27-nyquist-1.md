---
id: a3945129-5c7d-4bd6-98b9-9b6325f9a6bf
---

# Nyquist 1: The Nyquist Criterion

The Nyquist criterion decides stability by counting how many times one curve goes around the point −1.

## Before you start
<!-- bite: 4049ab25-9cfd-4505-9c2a-53d191b1c030 -->

You should have read [[control-theory/25-frequency-response-2|25 — Frequency Response 2: Loop Shaping, Bandwidth and Margins]], and be able to read gain and phase margin off a Bode plot.

After this lesson you will be able to:

1. draw what a Nyquist plot is and say why the point −1 matters;
2. apply $N = Z - P$ to decide closed-loop stability, including for an unstable plant;
3. read gain margin, phase margin and vector margin off a Nyquist plot;
4. explain why good gain and phase margins can still hide a fragile loop, and use $M_s$ instead.

## What the Nyquist plot is
<!-- bite: 871935b4-6701-4aa5-a721-e69beca638c2 -->

A Bode plot shows the loop gain $L(j\omega)$ as two graphs: size and angle. A **Nyquist plot** shows the same numbers as one curve: for each frequency, plot the complex number $L(j\omega)$ as a point, and join the points as $\omega$ runs from $-\infty$ to $+\infty$. (The negative frequencies just mirror the positive ones in the real axis.)

Why bother, when Bode margins are so handy? Because Bode margins quietly assume two things: **the plant is stable on its own, and the phase crosses −180° only once.** For an unstable plant, a plant with several crossings, or a big delay, Bode margins can give a confidently wrong answer. Nyquist handles all of it, because it is a proper theorem, not a rule of thumb.

## The kid version
<!-- bite: 188ee401-64e0-4eca-bcba-2764c4c4a755 -->

Imagine walking a dog on a long lead around a tree. Afterwards, you can tell how many times the lead wrapped around the tree just by counting how many times you circled it, without tracing every step. Nyquist does the same: the point −1 is the tree, the curve is your walk, and the number of wraps tells you how many unstable poles the closed loop has.

**Where the analogy stops working.** With the dog, zero wraps is always good. In Nyquist, if the plant is unstable on its own, you *need* some wraps, in the right direction, for the loop to be stable.

## Why the point −1
<!-- bite: 9c0d3b62-4731-4606-81f5-3805d58953ad -->

Closed-loop poles are the roots of $1 + L(s) = 0$, which means $L(s) = -1$. The point −1 is a loop gain of size 1 and angle 180°: a signal goes around the loop, comes back the same size and exactly upside down, and the minus sign at the comparator turns it right way up again, so it feeds itself. **That's the definition of a steady oscillation.**

So everything about stability and robustness comes down to where the curve is relative to that one point, and how close it gets.

## The criterion
<!-- bite: 15df40cc-f06b-419b-9edb-d5c599a05e53 -->

Count three things:

1. **$P$**: the number of the plant's own (open-loop) poles in the right half plane: how many unstable modes it already has.
2. **$N$**: the number of times the Nyquist curve goes **clockwise** around −1 (anticlockwise counts as negative).
3. **$Z$**: the number of closed-loop poles in the right half plane. This is what you want to know.

They are linked by

$$\boxed{N = Z - P}$$

You need $Z = 0$, so in words: **the closed loop is stable exactly when the curve goes around −1 anticlockwise $P$ times.**

## The two cases in practice
<!-- bite: 89540c83-fe8e-4ed5-8be9-ef39b0b17cf9 -->

**A stable plant ($P = 0$).** Stable exactly when the curve **doesn't go around −1 at all**. This is the case you meet most often, and it's a glance at the picture.

**An unstable plant ($P > 0$).** You *need* anticlockwise wraps. And that means an unstable plant needs **enough** gain: too little and the curve doesn't reach far enough to go around −1. This is the formal version of "you must be quick enough to catch a falling pole", and it's why lesson 25 gave unstable plants a *lower* limit on bandwidth.

## Our loop on a Nyquist plot
<!-- bite: 8d2ec373-da58-4d1f-bba7-690736a09910 -->

Take $L = K/(s(s+1)(s+2))$ once more, at $K = 1$. The plant has no right-half-plane poles (the one at 0 is handled by a small detour around it), so $P = 0$, and we need no wraps.

![The Nyquist plot of 1 over s times s plus 1 times s plus 2 for positive frequencies, with the unit circle and the point minus 1 marked. The curve comes up from far below, crosses the unit circle at an angle of 53 degrees from the negative real axis, and crosses the negative real axis at minus 0.167, a sixth of the way to minus 1. The closest approach to minus 1 is 0.64, marked with a circle.](images/ct-nyquist.svg)

The curve crosses the negative real axis at $-1/6$. Multiply $K$ by 6 and that crossing lands on −1; multiply by more and the curve wraps around it, $N = 2$, so $Z = 2$: two unstable closed-loop poles. Exactly lesson 19's result, from a third direction.

## Reading margins off the plot
<!-- bite: d9ead66d-998d-4622-ba11-e7196ac0e6f9 -->

The distance from the curve to −1 is how close you are to instability. The margins measure it in different ways:

1. **Gain margin**: where the curve crosses the negative real axis, at $-a$, GM $= 1/a$. Here $1/0.167 = 6$.
2. **Phase margin**: where the curve crosses the unit circle, the angle from there to the negative real axis. Here 53.4°.
3. **Vector margin**: the **shortest** distance from the curve to −1, in any direction. Here 0.64.

The vector margin is the honest one, and the next section shows why.

## Margins can lie
<!-- bite: 5b499aeb-f739-468e-9b65-5ad15de22ead -->

A design can have GM = 10 dB and PM = 60°, textbook-good numbers, and still be one small change away from instability. How? The curve swings in *close* to −1 without crossing the unit circle or the negative real axis anywhere near it. Each classical margin measures along its own line, so both miss the near miss completely.

Remember this one: **gain and phase margin measure two particular directions; real model errors come from every direction.**

The fix is the **sensitivity peak**, the largest value of $|S|$ over all frequencies:

$$M_s = \max_\omega \left|\frac{1}{1 + L(j\omega)}\right| = \frac{1}{\text{shortest distance from the curve to } -1}$$

So $M_s$ is one over the vector margin, and one number captures the closest approach from any direction. Our loop has $M_s = 1/0.64 = 1.57$.

## What a good $M_s$ guarantees
<!-- bite: 9eb4205d-72a4-45f3-9a8b-222633872bc9 -->

**Target $M_s < 2$** (6 dB). A good $M_s$ guarantees good classical margins:

$$GM \geq \frac{M_s}{M_s - 1}, \qquad PM \geq 2\sin^{-1}\frac{1}{2M_s}$$

With $M_s = 2$ that's GM of at least 2 (6 dB) and PM of at least 29°. But it doesn't work the other way: **a good $M_s$ guarantees good classical margins; good classical margins don't guarantee a good $M_s$.** If you check only one robustness number, check this one.

## Common pitfalls
<!-- bite: 9bcfccba-4d17-4c5b-b18b-98746235008e -->

1. **Counting wraps in the wrong direction.** $N$ counts clockwise; anticlockwise wraps are negative.
2. **Forgetting $P$.** With an unstable plant, "no wraps" means *unstable*.
3. **Plotting only positive frequencies and counting.** The negative half mirrors it; count the full closed curve.
4. **Trusting GM and PM alone.** Check the closest approach, $M_s$.

## Check your understanding
<!-- bite: 664e76c9-4db7-47da-a7c4-99b2d12c4c2a -->

Try each one before you open the answer.

1. <!-- q: exact id="3e7d1a26" answer="0" -->
   A stable plant's Nyquist curve does not go around −1 at all. How many closed-loop poles are in the right half plane?

   <details><summary>Answer</summary>

   $P = 0$ and $N = 0$, so $Z = N + P = 0$. Stable.

   </details>

2. <!-- q: exact id="b0c4f8e9" answer="2" -->
   A plant has one right-half-plane pole ($P = 1$). Its Nyquist curve goes around −1 once **clockwise**. How many unstable closed-loop poles are there?

   <details><summary>Answer</summary>

   $N = 1$, so $Z = N + P = 2$. Unstable: it needed one anticlockwise wrap instead.

   </details>

3. <!-- q: exact id="1f9a6d53" answer="4" -->
   A Nyquist curve crosses the negative real axis at $-0.25$. What is the gain margin, as a factor?

   <details><summary>Answer</summary>

   GM $= 1/0.25 = 4$, about 12 dB.

   </details>

4. <!-- q: exact id="c72e0b14" answer="2.5" -->
   The closest a Nyquist curve gets to −1 is 0.4. What is $M_s$?

   <details><summary>Answer</summary>

   $M_s = 1/0.4 = 2.5$: above the target of 2, so the loop is fragile even if its GM and PM look fine.

   </details>

5. <!-- q: open id="64a8f0d2" -->
   Why does an unstable plant need a *minimum* amount of loop gain to be stabilised?

   <details><summary>Answer</summary>

   With $P > 0$ the curve must go around −1 anticlockwise $P$ times. If the gain is too small, the curve stays too close to the origin to reach around −1, so the wraps can't happen and the closed loop stays unstable.

   </details>

## Before moving on
<!-- bite: c5589e02-ef0c-409d-b20d-c79148990fa9 -->

You can apply $N = Z - P$, read three margins off a Nyquist plot, and use $M_s$. **Next:** [[control-theory/28-nyquist-2|28 — Nyquist 2: Sketching Polar and Nyquist Plots]], which shows how to draw these plots by hand.

## Related
<!-- bite: 091de540-930e-4fc4-929a-20b0b468f9ca -->

- [[control-theory/19-stability-1|19 — Stability 1: What Stability Means and Routh–Hurwitz]]: the same loop, by Routh.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: 1b45117e-3bee-4632-a075-c8d2ca8473ea -->

**Level:** Advanced. **Covers:** the Nyquist plot, why −1 matters, the criterion $N = Z - P$, reading three margins, and the sensitivity peak $M_s$.

**Where it sits:** lesson 27 of 58, part 1 of 3 on Nyquist analysis.

**Source:** `[reference]`, assembled from standard control texts. The plot and its margins come from `scripts/diagrams/control_theory.py`.
