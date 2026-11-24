---
id: 008ab218-7fbf-4ba3-9194-d4a3acc41add
---

# Root Locus 2: Test Points, Departure Angles and Positive Feedback

The angle and magnitude conditions test points and give gains, departure angles start branches, and positive feedback flips the rules.

## Before you start
<!-- bite: 6de525a1-a43f-4a81-bb36-7095452eb142 -->

You should have read [[control-theory/21-root-locus-1|21 — Root Locus 1: Sketching the Locus]], and be able to sketch a locus with the basic rules.

After this lesson you will be able to:

1. test whether a point is on the root locus with the angle condition, measuring each vector's angle;
2. find the gain that puts a closed-loop pole at a given point;
3. compute the angle of departure from a complex pole, or arrival at a complex zero;
4. sketch the complementary root locus of a positive-feedback system.

## What this lesson adds
<!-- bite: e630b634-7776-409d-87f7-76fabf38fd86 -->

The root locus lesson gave six rules. The course notes use nine steps; the extra ones are below: testing points by measuring vectors, the angle at which a branch leaves a complex pole, and finding the gain at a chosen point. Then a twist: the locus for positive feedback.

The nine steps, for reference: (1) poles, (2) zeros, (3) number of asymptotes $|n - m|$, (4) their angles, (5) their centroid, (6) real-axis segments, (7) departure and arrival angles, (8) breakaway and break-in points, (9) imaginary-axis crossings.

## The kid version
<!-- bite: 710f39e4-a517-47d4-9848-6f3d156b8aee -->

Imagine standing at a spot in a field with several flagpoles (poles) and markers (zeros). Point your arm at each one and note its compass direction. The spot is "on the locus" only if the directions to the markers minus the directions to the flagpoles add up to exactly 180°. And how far you are from each one says how much gain it takes to put a pole on that spot.

**Where the analogy stops working.** You measure directions *from* the flagpoles *to* you, not from you to them, which is easy to get backwards.

## Testing a point
<!-- bite: dc84dfe0-779e-4f5a-8d26-6fe955bd6358 -->

For $G(s)H(s) = K\dfrac{\prod(s + z_i)}{\prod(s + p_j)}$, each factor $(s + z_i)$ is a **vector from the zero at $-z_i$ to the point $s$**. The angle condition says $s$ is on the locus when

$$\sum \angle(s + z_i) - \sum \angle(s + p_j) = \pm180°(2k + 1)$$

with every angle measured from the positive real axis.

The course notes' example: is $s = -3 + 4j$ on the locus of $\dfrac{K(s + 1)}{s(s + 2)}$?

1. Zero at $-1$: vector $-2 + 4j$, angle 116.57°.
2. Pole at 0: vector $-3 + 4j$, angle 126.87°.
3. Pole at $-2$: vector $-1 + 4j$, angle 104.04°.

Sum: $116.57 - 126.87 - 104.04 = -114.34°$. Not $\pm180°$, so the point is **not** on the locus, and no gain will put a closed-loop pole there.

## Finding the gain at a point
<!-- bite: 1fd24508-1afe-4c7a-a392-4530d1c9a6c4 -->

For a point that *is* on the locus, the magnitude condition gives the gain that puts a closed-loop pole there:

$$K = \frac{\prod|s + p_j|}{\prod|s + z_i|} = \frac{\text{product of distances to the poles}}{\text{product of distances to the zeros}}$$

Worked: for $\dfrac{K}{s(s + 4)(s + 6)}$, the line of $\zeta = 0.358$ (30% overshoot) crosses the locus at $s = -1.006 + 2.627j$. The distances to the poles at $0$, $-4$ and $-6$ multiply to 63.2, so $K = 63.2$, with no zeros to divide by. This is the starting point of the lead design example in the next lesson.

## Departure and arrival angles
<!-- bite: f1bccfa0-75ff-4946-88bc-91e8b854548c -->

When a pole is complex, the locus doesn't leave it along the real axis. Its **angle of departure** comes from the angle condition applied to a point just next to the pole: everything else sees that point as if it were the pole itself. So

$$\theta_D = 180° + \sum\angle(\text{from zeros}) - \sum\angle(\text{from the other poles})$$

with the angles measured to the complex pole. The **angle of arrival** at a complex zero works the same way, with the roles of poles and zeros swapped and the sign flipped.

## Worked: a departure angle
<!-- bite: 787f7080-fe8c-40da-ab98-8c8d576c0341 -->

$G(s)H(s) = \dfrac{K(s + 2)}{s^2 + 2s + 3}$, with poles at $-1 \pm j\sqrt2$ and a zero at $-2$. Find the departure angle from the upper pole. Predict before reading on: will the branch leave going left or right?

1. From the zero at $-2$ to the pole: vector $1 + j\sqrt2$, angle 54.74°.
2. From the other pole, $-1 - j\sqrt2$, to this one: vector $2j\sqrt2$, straight up, angle 90°.
3. $\theta_D = 180° + 54.74° - 90° = 144.74°$.

The branch leaves the upper pole heading up and to the **left**, and curves round towards the zero, the classic circular arc for one zero and a complex pole pair.

## Positive feedback: the complementary locus
<!-- bite: 9fa1d6b0-f09c-48ac-ae06-6355e2e7dbd7 -->

With **positive** feedback the characteristic equation is $1 - KGH = 0$, so $KGH = +1$: the angle condition becomes **0°** instead of 180°. The rules change accordingly:

1. **Real axis**: a point is on the locus if the number of poles and zeros to its right is **even** (including zero).
2. **Asymptote angles**: $\dfrac{360°k}{n - m}$ instead of $\dfrac{180°(2k + 1)}{n - m}$. One asymptote always lies along the positive real axis.
3. **Departure angles**: use 0° in place of 180°.

Everything else (start at poles, end at zeros, centroid, symmetry) stays. Positive feedback appears in inner loops and some electronic circuits, and its locus usually heads into the right half plane: a positive-feedback loop with enough gain is unstable.

## Common pitfalls
<!-- bite: 34ddc3b1-629a-42d4-82f1-64be22304cdf -->

1. **Measuring angles from the point to the poles.** Measure from each pole or zero *to* the point.
2. **Forgetting to subtract pole angles.** Zeros add, poles subtract.
3. **Including the pole itself in its departure-angle sum.** Use only the *other* poles.
4. **Using 180° for positive feedback.** The complementary locus uses 0°.

## Check your understanding
<!-- bite: f0b3cc56-cc65-4ce5-b1ad-e110b48367ef -->

Try each one before you open the answer.

1. <!-- q: mcq id="5c2e0b87" -->
   At a test point, the zero angles sum to 60° and the pole angles sum to 240°. Is the point on the root locus of a negative-feedback system?

   - [x] Yes: $60 - 240 = -180°$
   - [ ] No: the angles must sum to 0°
   - [ ] No: the pole angles must be smaller
   - [ ] It depends on the gain

   <details><summary>Answer</summary>

   $\sum$zero angles $-$ $\sum$pole angles $= -180°$, which satisfies the angle condition. The gain then comes from the magnitude condition.

   </details>

2. <!-- q: exact id="e8d41a96" answer="40" -->
   A point on the locus of $K/((s + 2)(s + 4))$ is at distance 5 from the pole at $-2$ and 8 from the pole at $-4$. What gain $K$ puts a closed-loop pole there?

   <details><summary>Answer</summary>

   $K = 5 \times 8 = 40$ (no zeros).

   </details>

3. <!-- q: exact id="0f6b9c34" answer="90" accept="90°" -->
   $G(s) = K/(s^2 + 2s + 2)$ has poles at $-1 \pm j$ and no zeros. What is the departure angle from the upper pole, in degrees?

   <details><summary>Answer</summary>

   The vector from the lower pole to the upper one points straight up, at 90°, and there are no zeros. So $\theta_D = 180° - 90° = 90°$: the branch leaves straight up, along the line $\text{Re}(s) = -1$.

   </details>

4. <!-- q: mcq id="a37e5d10" -->
   For positive feedback with poles at $0$ and $-3$ and no zeros, which real-axis points are on the complementary locus?

   - [ ] Between 0 and $-3$ only
   - [x] Right of 0, and left of $-3$
   - [ ] The whole real axis
   - [ ] None

   <details><summary>Answer</summary>

   An even number of poles must lie to the right: none right of 0 (zero is even), two left of $-3$.

   </details>

5. <!-- q: open id="6b9f2c45" -->
   Why does the departure angle from a complex pole exclude that pole's own contribution?

   <details><summary>Answer</summary>

   The angle from the pole to a point right next to it is exactly the departure direction we're solving for; it's the unknown, not a known term. Every other pole and zero is far away, so it sees the nearby point at the same angle as the pole itself.

   </details>

## Before moving on
<!-- bite: 5f6dec41-42c4-4b99-82c2-12ff96c9a12b -->

You can test points, find gains, compute departure angles and sketch a complementary locus. **Next:** [[control-theory/23-root-locus-design|23 — Design by Root Locus: Lead and Lag Compensators]].

## Related
<!-- bite: 88a30cd1-4d5e-46f4-b5a8-df86d00f3e25 -->

- [[control-theory/21-root-locus-1|21 — Root Locus 1: Sketching the Locus]]: the first six rules.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: 45b297ee-ecff-4c9a-9421-4e472a1ef84b -->

**Level:** Intermediate. **Covers:** the nine sketching steps, testing a point with vectors, the magnitude condition for gain, departure and arrival angles, and the complementary root locus for positive feedback.

**Where it sits:** lesson 22 of 58, part 2 of 2 on the root locus, before design.

**Source:** the author's course notes, A. M. Hussein, *Control Engineering*, Benha University, chapter 10 (sections 2.1 to 3). Angles and gains checked in `scripts/diagrams/control_theory.py`.
