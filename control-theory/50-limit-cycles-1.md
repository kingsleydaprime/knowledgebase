---
id: 9f9684a5-b2c3-40c4-9d75-c2e84a2267af
---

# Limit Cycles 1: Stable, Unstable and Semi-Stable

A limit cycle is an isolated closed orbit in the phase plane: a self-sustaining oscillation that nearby trajectories wind towards or away from.

## Before you start
<!-- bite: 9251514e-03ca-444d-a8b8-5de3a985def9 -->

You should have read [[control-theory/49-phase-plane-3|49 — Phase Plane 3: Linearising Around an Equilibrium]], and be comfortable converting $x_1 = r\cos\theta$, $x_2 = r\sin\theta$ ([[mathematics/index|polar coordinates]]).

After this lesson you will be able to:

1. say what a periodic solution and a closed orbit are;
2. explain why a linear oscillator is a poor oscillator, and what a nonlinear one fixes;
3. define a limit cycle and its three types;
4. find limit cycles and their types for systems written in polar form.

## What a limit cycle is
<!-- bite: 5612f13a-990f-4702-8bca-c80458815bc3 -->

A system **oscillates** when it has a nontrivial **periodic solution**:

$$x(t + T) = x(t) \quad \text{for all } t \ge 0, \text{ for some } T > 0$$

"Nontrivial" rules out an equilibrium, which trivially repeats. In the phase plane a periodic solution draws a **closed orbit**: the state goes round and comes back to exactly where it started.

We've met closed orbits already: the frictionless pendulum (lesson 47) and the linear centre (lesson 48) are full of them. This lesson shows why those are fragile, and what a limit cycle does differently.

## The kid version
<!-- bite: 67e7648c-f949-4b85-82da-862f3a40f48f -->

A playground swing pushed once swings at whatever size you started it, and slowly dies. A grandfather clock is different: its mechanism gives the pendulum a tiny kick each swing, so whether you start it gently or roughly, it soon settles to the same swing size and keeps it for years. That fixed, self-correcting swing is a limit cycle.

**Where the analogy stops working.** A clock's limit cycle always attracts. Limit cycles can also repel, so nearby motions run away from them, or attract from one side only.

## The trouble with linear oscillators
<!-- bite: bcde9515-d075-4904-9f48-b5f1daebc29d -->

A linear system with eigenvalues $\pm j\beta$ (a centre) oscillates. In Jordan coordinates:

$$z_1(t) = r_0\cos(\beta t + \theta_0), \qquad z_2(t) = r_0\sin(\beta t + \theta_0)$$

with amplitude $r_0 = \sqrt{z_{10}^2 + z_{20}^2}$. There's a whole continuum of closed orbits, one for every amplitude: a **harmonic oscillator**. In an LC circuit, the energy swaps back and forth between the capacitor's electric field and the inductor's magnetic field.

But it's a bad oscillator, for two reasons:

1. **It's not robust.** Lesson 49 showed that any small change can turn a centre into a focus, destroying the oscillation. The linear oscillator is **not structurally stable**.
2. **Its amplitude depends on how you started it.** There's nothing pulling it to a particular size.

A well-built **nonlinear** oscillator fixes both: it's structurally stable, and its steady amplitude doesn't depend on the starting state. That's what every electronic oscillator and every clock relies on.

## Limit cycles and their three types
<!-- bite: 916c606d-d61b-4021-8814-4d163bef8640 -->

On the phase plane, a **limit cycle** is an **isolated** closed orbit. Two words carry the definition:

1. **Closed**: the motion is periodic.
2. **Isolated**: there are no other closed orbits right next to it; nearby trajectories converge to it or diverge from it. (So a linear centre's orbits, or the mass-spring system's, are *not* limit cycles: they sit in a continuous family.)

How nearby trajectories behave gives three types:

1. **Stable limit cycle**: all nearby trajectories converge to it as $t \to \infty$.
2. **Unstable limit cycle**: all nearby trajectories diverge from it.
3. **Semi-stable limit cycle**: some nearby trajectories converge and some diverge.

## Example 1a: a stable limit cycle
<!-- bite: 024f1828-6851-4df6-89dd-17162f52bc6f -->

$$\dot{x}_1 = x_2 - x_1(x_1^2 + x_2^2 - 1), \qquad \dot{x}_2 = -x_1 - x_2(x_1^2 + x_2^2 - 1)$$

In polar coordinates it splits neatly:

$$\dot{r} = -r(r^2 - 1), \qquad \dot\theta = -1$$

1. **On the unit circle** ($r = 1$): $\dot{r} = 0$, so the state circles the origin with period $2\pi$.
2. **Inside** ($r < 1$): $\dot{r} > 0$, so trajectories grow out to the circle.
3. **Outside** ($r > 1$): $\dot{r} < 0$, so trajectories shrink in to the circle.

From both sides they approach $r = 1$: **the unit circle is a stable limit cycle.** Start anywhere except the origin, and you end on it.

## Examples 1b and 1c: unstable and semi-stable
<!-- bite: fc1f4aa6-770f-4e86-95a1-ce6c545a5fd5 -->

Flip the sign and you get **example 1b**, $\dot{r} = r(r^2 - 1)$, $\dot\theta = -1$. Inside the circle $\dot{r} < 0$, so trajectories fall into the origin; outside $\dot{r} > 0$, so they run away. Both sides leave the circle: **an unstable limit cycle**.

Square the bracket and you get **example 1c**, $\dot{r} = -r(r^2 - 1)^2$, $\dot\theta = -1$. Now $\dot{r} \le 0$ everywhere. Outside, trajectories shrink *onto* the circle; inside, they shrink *away* from it, towards the origin. **A semi-stable limit cycle**: attracting from outside, repelling inside.

![Three phase portraits, each with the unit circle drawn in orange. Stable: trajectories from inside and outside wind onto the circle. Unstable: trajectories leave the circle, inwards to the origin and outwards to infinity. Semi-stable: trajectories from outside wind onto the circle, while those just inside spiral away towards the origin.](images/ct-lc-three-types.svg)

## The recipe for polar systems
<!-- bite: 807b13c0-b442-439c-bde0-f5fe6e8f8c7c -->

Every example worked the same way, and it's a recipe for any system of the form $\dot{r} = g(r)$, $\dot\theta = \text{constant}$:

1. Find the radii where $g(r) = 0$, other than $r = 0$. Each is a circular closed orbit.
2. Check the sign of $g$ just inside and just outside each one.
3. Inside positive and outside negative: **stable**. Inside negative and outside positive: **unstable**. Same sign on both sides: **semi-stable**.

## Common pitfalls
<!-- bite: a9efe6ba-ab88-4a37-aa67-3bfdcd9911a7 -->

1. **Calling a centre's orbits limit cycles.** A limit cycle must be isolated.
2. **Checking only one side.** Semi-stable cycles look stable from one side.
3. **Forgetting $\dot\theta$.** The period is $2\pi/|\dot\theta|$ when $\dot\theta$ is constant.
4. **Expecting limit cycles in linear systems.** Linear oscillations always come in a continuous family.

## Check your understanding
<!-- bite: 6330b72c-f9f2-4553-88f3-7528c16b56d5 -->

Try each one before you open the answer.

1. <!-- q: mcq id="3a6d0f91" -->
   A system in polar form is $\dot{r} = r(r - 1)(r - 2)$, $\dot\theta = 1$. What kind of limit cycle is $r = 1$?

   - [x] Stable
   - [ ] Unstable
   - [ ] Semi-stable
   - [ ] Not a limit cycle

   <details><summary>Answer</summary>

   At $r = 0.5$, $\dot{r} = 0.375 > 0$ (grows towards 1); at $r = 1.5$, $\dot{r} = -0.375 < 0$ (shrinks towards 1). Both sides approach: stable.

   </details>

2. <!-- q: mcq id="c50e8b27" -->
   Same system, $\dot{r} = r(r - 1)(r - 2)$. What kind of limit cycle is $r = 2$?

   - [ ] Stable
   - [x] Unstable
   - [ ] Semi-stable
   - [ ] Not a limit cycle

   <details><summary>Answer</summary>

   At $r = 1.5$, $\dot{r} < 0$ (moves away, down to 1); at $r = 2.5$, $\dot{r} = 1.875 > 0$ (moves away, outwards). Both sides leave: unstable.

   </details>

3. <!-- q: mcq id="9f2c4e60" -->
   $\dot{r} = r(r - 1)^2$, $\dot\theta = 1$. What kind of limit cycle is $r = 1$?

   - [ ] Stable
   - [ ] Unstable
   - [x] Semi-stable
   - [ ] Not a limit cycle

   <details><summary>Answer</summary>

   $\dot{r} \ge 0$ on both sides: inside, trajectories grow up to the circle; outside, they grow away from it. Attracting on one side only: semi-stable.

   </details>

4. <!-- q: exact id="d17e3b85" answer="2.0944" sigfigs="3" -->
   A circular limit cycle has $\dot\theta = 3$ rad/s. What is its period, in seconds?

   <details><summary>Answer</summary>

   $T = 2\pi/3 = 2.09$ s.

   </details>

5. <!-- q: open id="64b8a1f3" -->
   Give two reasons a nonlinear oscillator with a stable limit cycle makes a better clock than a linear harmonic oscillator.

   <details><summary>Answer</summary>

   Its amplitude settles to the same value whatever the starting state, while a harmonic oscillator keeps whatever amplitude it started with. And it's structurally stable: small changes in the system don't destroy the oscillation, while any tiny damping or energy gain turns a linear centre into a decaying or growing spiral.

   </details>

## Before moving on
<!-- bite: 10fc59f0-0bbb-4864-8f49-e37ae0129cbd -->

You can say what a limit cycle is and classify one in polar form. **Next:** [[control-theory/51-limit-cycles-2|51 — Limit Cycles 2: Proving They Exist or Don't]], with tests that work without polar coordinates.

## Related
<!-- bite: f0b54ed8-06f6-448f-9196-244d357781f8 -->

- [[control-theory/56-nonlinear-design-1|56 — Nonlinear Design 1: Describing Functions and Gain Scheduling]]: describing functions, an engineer's way to predict limit cycles in a loop.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: faf190b1-2e0e-433e-8d9e-4a1709886fba -->

**Level:** Advanced. **Covers:** periodic solutions and closed orbits, the harmonic oscillator and its two weaknesses, the definition of a limit cycle, its three types, and the lecture's three polar examples.

**Where it sits:** lesson 50 of 58, part 1 of 2 on limit cycles.

**Source:** the author's nonlinear-control lecture notes, F. Abdollahi, *Nonlinear Control*, lecture 2, slides 35 to 41. Portraits computed in `scripts/diagrams/control_theory.py`.
