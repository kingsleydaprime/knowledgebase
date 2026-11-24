---
id: a42eea37-3fdd-40b2-87bc-dfe5cabe098c
---

# Design by Root Locus: Lead and Lag Compensators

When no gain puts the poles where the specification wants them, a compensator reshapes the root locus so it does.

## Before you start
<!-- bite: 435d2d2c-bf73-4997-bbdd-0ee0a4ad3605 -->

You should have read [[control-theory/22-root-locus-2|22 — Root Locus 2: Test Points, Departure Angles and Positive Feedback]], and be able to turn an overshoot and settling time into a target pole ([[control-theory/13-time-response-1|13 — Time Response 1: First- and Second-Order Systems]]).

After this lesson you will be able to:

1. explain what adding a pole or a zero does to the root locus;
2. design a lead compensator by the angle-deficiency method;
3. design a lag compensator to improve steady-state error without disturbing the transient;
4. name the op-amp realisations of PI, PD, PID, lead and lag.

## What design by root locus is
<!-- bite: 8c263dbf-af85-4c8d-93b7-fe3679c10561 -->

Turning the gain moves the closed-loop poles only **along** the locus. If the specification needs a pole at a point B that isn't on the locus, no gain will do: at the right overshoot you can only get the settling time of point A, on the locus. The fix is to **reshape the locus** by adding a **compensator** $G_c(s)$, whose own poles and zeros bend the branches so they pass through B.

Compensators come in three families (the course notes' list):

1. **Lead compensator**, a practical PD: improves the transient.
2. **Lag compensator**, a practical PI: improves the steady-state error.
3. **Lag-lead compensator**, a practical PID: both.

## The kid version
<!-- bite: 89bb6a40-35a1-48eb-b7ce-e84bc16a08f7 -->

The root locus is a set of railway tracks the poles must ride. If the station you want isn't on the tracks, turning the throttle (the gain) won't get you there. A compensator is a track-laying crew: it bends the line so it runs through your station.

**Where the analogy stops working.** Laying track somewhere never affects the rest of the railway. Adding a pole or zero reshapes *every* branch a little, so after designing you must check the other poles too.

## What adding poles and zeros does
<!-- bite: 19810acd-8d95-49e8-ac6d-3439099917f1 -->

1. **Adding a pole** pulls the locus to the **right**: less stable, slower settling. The closer to the origin, the stronger the effect. An integrator (a pole at the origin) is the extreme: it raises the system type and kills steady-state error, at a cost in stability.
2. **Adding a zero** pulls the locus to the **left**: more stable, faster. A system that goes unstable at high gain can become stable for every gain once a zero is added. Physically, a zero is derivative action.

Remember this one: **a lead compensator uses its zero to pull the locus left; a lag compensator uses a pole-zero pair near the origin to raise the low-frequency gain while hardly moving the locus.**

## The lead compensator
<!-- bite: b4828af7-bf5a-4374-b352-c0bcd17a2479 -->

$$G_c(s) = K_c\frac{s + z_c}{s + p_c}, \qquad |z_c| < |p_c|$$

The zero is nearer the origin than the pole: the zero "leads". Its net angle at a point above the real axis is positive, which is what the design uses. Built with an op-amp and two RC pairs, $G_c = \dfrac{C_1}{C_2}\cdot\dfrac{s + 1/(R_1C_1)}{s + 1/(R_2C_2)}$ with $R_1C_1 > R_2C_2$.

**The procedure:**

1. From the specification, find the desired dominant pole $s_d$.
2. Compute the angle of the uncompensated $G$ at $s_d$. If it isn't $-180°$, the shortfall is the **angle deficiency** $\theta_c$ the compensator must add.
3. Choose the zero, and place the pole so that (zero's angle) $-$ (pole's angle) $= \theta_c$ at $s_d$.
4. Find the gain from the magnitude condition, and check the other closed-loop poles.

## Lead design worked: the setup
<!-- bite: 9d1d06cb-0d19-4f2d-bc63-7b3ddfb09c16 -->

The course notes' example 1: $G(s) = \dfrac{K}{s(s + 4)(s + 6)}$, unity feedback. Halve the settling time while keeping 30% overshoot.

1. 30% overshoot needs $\zeta = 0.358$. Along that line, the locus is crossed at $s = -1.006 + 2.627j$ ($\omega_n = 2.81$), with $K = 63.2$ (Root Locus 2). Settling time: $4/(0.358 \times 2.81) = 3.97$ s.
2. Halving it needs $\zeta\omega_n$ doubled at the same $\zeta$: $\omega_n = 5.63$, so the target is $s_d = -2.014 + 5.255j$.

Before reading on: is $s_d$ on the uncompensated locus?

## Lead design worked: the angles
<!-- bite: c961d31b-1d42-4122-8456-9713c94c0b15 -->

At $s_d$, the angles from the poles at $0$, $-4$ and $-6$ sum (with minus signs) to $-233.08°$. The locus needs $-180°$, so the compensator must add

$$\theta_c = -180° - (-233.08°) = 53.08°$$

No: $s_d$ isn't on the locus; a 53° lead is needed.

1. **Choose the zero** at $-5$. From $-5$ to $s_d$, the angle is 60.4°.
2. **Place the pole** so its angle is $60.4° - 53.08° = 7.3°$: the pole sits at $-42.97$.
3. **Gain**: the magnitude condition at $s_d$ gives $K = 1425$ for $\dfrac{K(s + 5)}{s(s + 4)(s + 6)(s + 42.97)}$.

Step 4's check matters here. The closed loop now has four poles: the designed pair at $-2.01 \pm 5.26j$, one at $-43.8$ (far to the left, so negligible), and one at $-5.13$, which sits almost on the compensator's zero at $-5$, so the two nearly cancel. The dominant pair stays in charge, and the settling time halves at about the same overshoot; a simulation confirms the small differences.

## The bisector method
<!-- bite: f9133ede-4627-443b-b066-568dcafe17f5 -->

The zero at $-5$ above was a free choice, and any zero with a matching pole meets the angle condition. The course notes' example 2 uses the **bisector method** to choose: at the design point $P$, draw the line to the origin and the horizontal line through $P$; bisect the angle between them; then mark lines at $\pm\theta_c/2$ either side of the bisector. Where they hit the real axis are the zero and the pole. It gives the largest $z_c/p_c$ ratio (the gentlest compensator). In their example ($\zeta = 0.5$, $\omega_n = 3$), it put the zero at $-1.94$ and the pole at $-4.65$.

## The lag compensator
<!-- bite: 599b646c-effe-446c-ba77-e5e0619321d7 -->

$$G_c(s) = K_c\frac{s + 1/T}{s + 1/(\beta T)}, \qquad \beta > 1$$

Use it when the **transient is already fine but the steady-state error isn't**. Put the pole and zero close together and near the origin: their angle contribution at the dominant poles is tiny (aim for under about 5°), so the locus there barely moves, but at $s = 0$ the compensator multiplies the gain by $\beta$. So $K_v$ (or $K_p$) goes up by $\beta$.

## Lag design worked
<!-- bite: 66ae4d05-e8b5-412c-b668-e8967a0495b0 -->

The course notes' second example 2: $G(s) = \dfrac{K}{s(s + 1)(s + 2)}$. At $\zeta = 0.491$ the dominant poles sit at $-0.331 \pm 0.586j$, with $K = 1.06$, so $K_v = 1.06/2 = 0.53$. The specification wants $K_v = 5$.

1. **Ratio**: $\beta = 5/0.53 = 9.43$.
2. **Place the pair near the origin**: with $T = 18.9$, the zero is at $1/T = 0.053$ and the pole at $1/(\beta T) = 0.0056$.
3. **Check the angle**: at the dominant pole, the pair adds only $-3.7°$, so the locus hardly moves.
4. **Retune the gain**: at the same $\zeta$, the gain comes out $K_c \approx 0.97$ of the original.

The transient is almost unchanged, and the ramp error is nearly ten times smaller.

## Common pitfalls
<!-- bite: e28c226a-83a5-4c57-9507-58a43f5831b8 -->

1. **Forgetting to check the third pole.** A compensator adds a closed-loop pole; make sure it doesn't dominate.
2. **Putting a lag pair far from the origin.** It then changes the transient too.
3. **Expecting a lead to fix steady-state error.** That's the lag's job.
4. **Choosing the lead's zero on top of a plant pole.** That's pole-zero cancellation; it's fine only for a well-known stable pole.

## Check your understanding
<!-- bite: 2610c6ca-21f6-4bb0-99e5-82fa147ddad8 -->

Try each one before you open the answer.

1. <!-- q: exact id="4e0a9d53" answer="30" accept="30°" -->
   At a desired pole, the uncompensated $G$ has angle $-210°$. How many degrees of lead must a compensator add?

   <details><summary>Answer</summary>

   $\theta_c = -180 - (-210) = 30°$.

   </details>

2. <!-- q: exact id="b7f15c28" answer="10" -->
   A system's transient is fine but its $K_v = 2$; the specification needs $K_v = 20$. What ratio $\beta$ must a lag compensator give?

   <details><summary>Answer</summary>

   $\beta = 20/2 = 10$.

   </details>

3. <!-- q: mcq id="2c8e6f71" -->
   Which compensator is a lead compensator?

   - [x] $(s + 2)/(s + 10)$
   - [ ] $(s + 0.1)/(s + 0.01)$
   - [ ] $(s + 10)/(s + 2)$
   - [ ] $1/(s + 5)$

   <details><summary>Answer</summary>

   A lead has its zero nearer the origin than its pole: $(s + 2)/(s + 10)$. $(s + 0.1)/(s + 0.01)$ is a lag; $(s + 10)/(s + 2)$ has the pole nearer, so it's a lag too, but not placed near the origin.

   </details>

4. <!-- q: mcq id="9d4b0e36" -->
   Why are a lag compensator's pole and zero placed close together near the origin?

   - [x] So they add almost no angle at the dominant poles, but still multiply the low-frequency gain by $\beta$
   - [ ] So they cancel each other completely
   - [ ] So they speed up the transient
   - [ ] So they add a lot of phase lead

   <details><summary>Answer</summary>

   Close together, their angles nearly cancel at the dominant poles, so the transient barely changes; at $s = 0$ their ratio is still $\beta$, boosting $K_v$ or $K_p$.

   </details>

5. <!-- q: open id="51e7c0a9" -->
   A designer wants 20% overshoot and a settling time half the current one. Why can't a gain change alone achieve it on a typical plant?

   <details><summary>Answer</summary>

   The overshoot fixes $\zeta$, so the poles must lie on one line through the origin; the gain only moves them along the root locus, which crosses that line at one point with one settling time. A faster settling time at the same $\zeta$ needs a point further out on the line, which isn't on the locus, so the locus itself must be reshaped with a compensator.

   </details>

## Before moving on
<!-- bite: 976c1bd0-3cad-4b9e-9dc6-ce8e591d59b7 -->

You can design lead and lag compensators on the root locus. **Next:** [[control-theory/24-frequency-response-1|24 — Frequency Response 1: Bode Plots]], a second way of looking at the same loops.

## Related
<!-- bite: 29a038c4-11ce-47a5-9a82-eb63b9db6eb1 -->

- [[control-theory/17-pid-control-1|17 — PID Control 1: The Three Terms]]: lead as filtered PD, lag as approximate PI.
- [[control-theory/04-modelling-2|04 — Modelling 2: Transfer Functions of Electrical Circuits]]: op-amp compensators.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: 3c449967-316b-41ee-8b37-b3e2de547627 -->

**Level:** Intermediate. **Covers:** the effects of added poles and zeros, lead and lag compensators, the angle-deficiency design procedure, a full lead design, the bisector method, and a full lag design.

**Where it sits:** lesson 23 of 58, the design lesson after the two root locus lessons.

**Source:** the author's course notes, A. M. Hussein, *Control Engineering*, Benha University, chapter 11 (sections 1 to 4, examples 1 and 2), with the lead example after N. S. Nise and the lag example after K. Ogata. Every angle, pole and gain is checked in `scripts/diagrams/control_theory.py`.
