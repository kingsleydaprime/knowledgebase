---
id: 60a864b5-4539-4f46-b20c-1ffe964d8758
---

# Nyquist 2: Sketching Polar and Nyquist Plots

A polar plot can be sketched from a few points, its start, its end and its axis crossings, and then tested for stability.

## Before you start
<!-- bite: 1664b466-a99e-461a-8ae5-ac28150c4e9f -->

You should have read [[control-theory/27-nyquist-1|27 — Nyquist 1: The Nyquist Criterion]], and be able to find the magnitude and angle of a complex number.

After this lesson you will be able to:

1. draw the polar plots of the basic factors: integrator, differentiator, first- and second-order terms;
2. sketch a polar plot from its start, end and axis crossings;
3. complete a Nyquist plot, including the large arc that comes from a pole at the origin;
4. apply the Nyquist criterion to a sketched plot.

## What this lesson covers
<!-- bite: 95a7fc89-4cd4-4698-bad9-ca0a6268b298 -->

Lesson Nyquist 1 used computer-drawn plots. In an exam, and often in design, you sketch them. The course notes' chapter 13 gives a short procedure: you only need a handful of exact points, and the rest follows from the shape.

Two words first. A **polar plot** is the curve of $G(j\omega)H(j\omega)$ for $\omega$ from 0 to $\infty$. The **Nyquist plot** is the full curve for $\omega$ from $-\infty$ to $\infty$: the polar plot plus its mirror image in the real axis, plus any closing arcs.

## The kid version
<!-- bite: 68b7e601-6630-4396-b895-096b0b761f91 -->

You don't need to plot every house to sketch a road on a map. Mark where it starts, where it ends, and where it crosses the main streets, and you can draw it freehand well enough to see whether it goes round the town hall (the point −1).

**Where the analogy stops working.** A road between marked points could wander anywhere. A polar plot can't: its angle changes steadily with frequency, so between the marked points it's smooth and predictable.

## The basic shapes
<!-- bite: 38b12b93-ed9c-4d18-a10d-cf23d2ba64d9 -->

1. **Integrator** $1/(j\omega)$: magnitude $1/\omega$, angle $-90°$. The whole plot lies on the **negative imaginary axis**, from $-j\infty$ in to the origin.
2. **Differentiator** $j\omega$: on the **positive imaginary axis**, from the origin outwards.
3. **First order** $1/(1 + j\omega T)$: a **semicircle** in the lower half, centre 0.5, radius 0.5, from 1 (at $\omega = 0$) to 0 (at $\omega = \infty$), passing $0.5 - 0.5j$ at $\omega = 1/T$.
4. **Second order** $\omega_n^2/(s^2 + 2\zeta\omega_ns + \omega_n^2)$: starts at 1, crosses the imaginary axis at $\omega = \omega_n$ (where it equals $1/(2j\zeta)$), and ends at 0 approaching from angle $-180°$. The point farthest from the origin is the resonance, $\omega_r$.

## The sketching procedure
<!-- bite: 39600961-9c19-43df-80c5-cb8070568d7b -->

1. Replace $s$ by $j\omega$, and write the magnitude and angle as functions of $\omega$.
2. **Start**: magnitude and angle at $\omega \to 0$.
3. **End**: magnitude and angle at $\omega \to \infty$.
4. **Real-axis crossings**: where the imaginary part is zero (the angle is $0°$ or $-180°$); find $\omega$ and the value there.
5. **Imaginary-axis crossings**: where the real part is zero (angle $-90°$ or $-270°$).
6. Join them smoothly, with the angle falling steadily as $\omega$ rises.

The start tells you the type: type 0 starts at a finite point on the positive real axis; type 1 starts at infinity along $-90°$; type 2 along $-180°$. The end angle is $-90°$ times the number of poles minus zeros.

## Worked: a type-0 third-order loop
<!-- bite: 327861f8-54a0-4015-b067-2b2ac9398364 -->

$G(s) = \dfrac{10}{(s + 1)^3}$. Predict first: does it cross the negative real axis, and where?

1. **Start**: $G(0) = 10$, angle $0°$.
2. **End**: magnitude 0, angle $-270°$ (three poles).
3. **Imaginary axis**: angle $-3\tan^{-1}\omega = -90°$ at $\omega = \tan 30° = 0.577$; there $|G| = 10/(1 + 1/3)^{3/2} = 6.50$. So it crosses at $-6.50j$.
4. **Real axis**: angle $-180°$ at $\omega = \tan 60° = \sqrt3$; there $(1 + j\sqrt3)^3 = -8$, so $G = -1.25$.

## The type-0 loop's plot and verdict
<!-- bite: 2a88e85b-2c4a-424e-9055-716d8fdae889 -->

Here is the curve through those four points.

![The polar plot of 10 over (s+1) cubed: it starts at 10 on the positive real axis, swings down through minus 6.50j at 0.577 radians per second, crosses the negative real axis at minus 1.25 at 1.73 radians per second, and spirals into the origin from angle minus 270 degrees. The point minus 1 lies inside the curve.](images/ct-nyq-sketch-type0.svg)

The curve crosses the negative real axis at $-1.25$, **beyond** $-1$. With its mirror image, the Nyquist plot goes around $-1$ twice clockwise ($N = 2$), the plant has $P = 0$, so $Z = 2$: **unstable**. The gain margin is $1/1.25 = 0.8$: the gain must drop to $10 \times 0.8 = 8$ for marginal stability.

(The course notes state that type-0 polar plots don't cross the axes. That's true of their first- and second-order examples, but, as this one shows, not of type-0 plots in general.)

## Poles at the origin: closing the contour
<!-- bite: e5e02e0a-7ec5-4e79-9eb6-dcbc182b098a -->

A type-1 loop like our $L = \dfrac{1}{s(s+1)(s+2)}$ goes to infinity as $\omega \to 0$, because of the integrator. The Nyquist contour must avoid the pole at the origin, so it detours around it on a tiny semicircle, $s = \epsilon e^{j\phi}$ with $\phi$ from $-90°$ to $+90°$.

On that detour $L \approx \dfrac{1}{2\epsilon e^{j\phi}}$: a huge magnitude, with angle going from $+90°$ to $-90°$. So **in the $L$ plane the tiny detour becomes an infinitely large semicircle, swinging clockwise** from the end of the $\omega = 0^-$ branch to the start of the $\omega = 0^+$ branch. Each pole at the origin adds one such half-turn arc.

## Worked: our type-1 loop sketched
<!-- bite: d810ecb6-f02e-4e68-9366-0e8054233a6b -->

1. **Start**: as $\omega \to 0^+$, angle $\to -90°$ and magnitude $\to \infty$. The real part tends to $-3/4 = -0.75$, so the plot comes down from $-j\infty$ along a vertical asymptote at $-0.75$.
2. **End**: 0, approached from $-270°$.
3. **Real axis**: angle $-180°$ at $\omega = \sqrt2$, value $-1/6$.

![The Nyquist plot of 1 over s(s+1)(s+2): the positive-frequency branch comes down from minus j infinity along the asymptote x = minus 0.75, crosses the negative real axis at minus 1/6, and curls into the origin; its mirror image is dashed; a large clockwise arc, drawn schematically, joins the two branches through the right half plane. The point minus 1 is outside the closed curve.](images/ct-nyq-sketch-type1.svg)

With the large arc swinging through the right half plane, the curve doesn't enclose $-1$: $N = 0$, $P = 0$, so the loop is stable, and stays so until the gain reaches 6 (when $-1/6$ becomes $-1$). Lesson 19's Routh result, from a sketch.

## Common pitfalls
<!-- bite: 77b0080b-453e-49a0-88bc-d50bccf04c84 -->

1. **Forgetting the mirror image.** The Nyquist plot includes $\omega < 0$.
2. **Leaving a type-1 plot open.** Close it with the infinite clockwise arc.
3. **Assuming type-0 plots never cross the axes.** Third-order and higher ones do.
4. **Getting the end angle wrong.** It's $-90°$ times (poles minus zeros).

## Check your understanding
<!-- bite: 1f66a2e4-149b-4c90-b136-c488c9d39e6a -->

Try each one before you open the answer.

1. <!-- q: exact id="3e1c8b76" answer="-180" accept="−180|180" -->
   A loop has two poles and no zeros. At what angle, in degrees, does its polar plot end as $\omega \to \infty$?

   <details><summary>Answer</summary>

   $-90° \times 2 = -180°$.

   </details>

2. <!-- q: mcq id="c9a24f05" -->
   Where does the polar plot of $1/(1 + j\omega T)$ lie?

   - [x] On a semicircle of radius 0.5 centred at 0.5, in the lower half plane
   - [ ] On the negative imaginary axis
   - [ ] On a full circle around the origin
   - [ ] On the positive real axis

   <details><summary>Answer</summary>

   It goes from 1 to 0 along a lower semicircle centred at 0.5.

   </details>

3. <!-- q: exact id="6d07e2b9" answer="-0.625" accept="−0.625" -->
   Using the same steps as the worked example, $G(s) = 5/(s + 1)^3$ crosses the negative real axis at $\omega = \sqrt3$. Where?

   <details><summary>Answer</summary>

   $(1 + j\sqrt3)^3 = -8$, so $G = 5/(-8) = -0.625$. Inside $-1$: stable, with a gain margin of 1.6.

   </details>

4. <!-- q: mcq id="5a8f3e12" -->
   A loop has one pole at the origin. What does the tiny detour around that pole become on the Nyquist plot?

   - [ ] A small circle around −1
   - [x] An infinitely large clockwise semicircle
   - [ ] A point at the origin
   - [ ] A straight line along the real axis

   <details><summary>Answer</summary>

   Near the pole, $L$ is huge, and its angle swings through 180° as the detour goes round: an infinite clockwise half-circle.

   </details>

5. <!-- q: open id="0b6e9d24" -->
   Why is it enough to compute only the start, the end and the axis crossings when sketching a polar plot?

   <details><summary>Answer</summary>

   The magnitude and angle change smoothly with frequency, and for typical loops the angle decreases steadily. So once the endpoints and the places where it crosses the axes (the quadrant boundaries) are fixed, the curve between them is determined closely enough to see whether it encircles −1, which is what the criterion needs.

   </details>

## Before moving on
<!-- bite: 44f5932f-b71f-42fa-9d75-d86cd289359e -->

You can sketch polar and Nyquist plots by hand and apply the criterion to them. **Next:** [[control-theory/29-nyquist-3|29 — Nyquist 3: Uncertainty and Fundamental Limits]].

## Related
<!-- bite: 2986d4c6-ffae-4627-945e-834ebfc68038 -->

- [[control-theory/24-frequency-response-1|24 — Frequency Response 1: Bode Plots]]: the same information as Bode plots.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: e7443812-fce0-491d-b290-c58bb2013699 -->

**Level:** Intermediate. **Covers:** polar plots of basic factors, the sketching procedure, a type-0 third-order example, poles at the origin and the infinite arc, and the criterion on a sketched plot.

**Where it sits:** lesson 28 of 58, part 2 of the Nyquist lessons.

**Source:** the author's course notes, A. M. Hussein, *Control Engineering*, Benha University, chapter 13 (sections 1 and 2, examples 1 to 7). Plots computed in `scripts/diagrams/control_theory.py`.
