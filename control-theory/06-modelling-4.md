---
id: 2eb5b75c-8a2a-4576-9fc5-98efe345b5b7
---

# Modelling 4: Rotational Systems, Gears and the DC Motor

Rotating systems follow the same laws as straight-line ones, with torque, angle and inertia, and gears and a DC motor complete the plant.

## Before you start
<!-- bite: fa8d9adb-2b7e-45fb-86a3-4d68bcd8d650 -->

You should have read [[control-theory/05-modelling-3|05 — Modelling 3: Translational Mechanical Systems]].

After this lesson you will be able to:

1. write the torque laws for inertia, torsional springs and rotational dampers;
2. find the transfer function of a two-inertia system;
3. use the gear relations and reflect inertia and damping through a gear train;
4. model a DC motor, find its constants from its torque-speed curve, and get its transfer function.

## What this lesson covers
<!-- bite: 2f4ec753-dc6c-40f7-8151-36e385b345fc -->

The classic control plant is a motor turning a load through gears: an antenna, a robot joint, a printer head. The textbook's opening picture is an antenna azimuth position control system. Everything in this lesson builds up to that plant's transfer function: rotational elements, then gears, then the motor itself.

## The kid version
<!-- bite: def4a847-4461-4d45-b7b6-901586d715b5 -->

A spinning playground roundabout is hard to start and hard to stop: that's inertia. Fix it to the ground with a twisted rubber band and it springs back: a torsional spring. Drag your foot on the ground and it slows: a damper. A bicycle's gears let your legs turn slowly with big force while the wheel spins fast with small force.

**Where the analogy stops working.** On a bike you feel the gears change the effort. In a model, the gears also change how heavy the load *looks* from the motor: a big load behind a big gear reduction feels light, by the square of the ratio.

## The rotational elements
<!-- bite: 8bcfeac0-8843-471a-877e-63c67b24b9b2 -->

| Element | Torque law | In $s$ |
| --- | --- | --- |
| Inertia $J$ | $T = J\ddot\theta$ | $Js^2$ |
| Torsional spring $K$ | $T = K(\theta_1 - \theta_2)$ | $K$ |
| Rotational damper $B$ | $T = B(\dot\theta_1 - \dot\theta_2)$ | $Bs$ |

Newton's law for rotation: the sum of torques equals $J$ times the angular acceleration. $K$ is in N·m/rad and $B$ in N·m·s/rad. The method is the same as in Modelling 3: one equation per angle, each spring and damper using the difference of its ends.

## A two-inertia system
<!-- bite: 913d59cb-7409-426f-aae1-7abcaea36ab6 -->

The textbook's example 6: torque $T$ drives inertia $J_1$ (damper $B_1$ to ground), joined by a shaft of stiffness $K$ to inertia $J_2$ (damper $B_2$ to ground).

At $\theta_1$: $T = (J_1s^2 + B_1s + K)\theta_1 - K\theta_2$

At $\theta_2$: $0 = -K\theta_1 + (J_2s^2 + B_2s + K)\theta_2$

Cramer's rule, or substitution, gives

$$\frac{\theta_2(s)}{T(s)} = \frac{K}{(J_1s^2 + B_1s + K)(J_2s^2 + B_2s + K) - K^2}$$

The same shape as the two-mass system: diagonal terms collect everything at a node, the shared shaft appears off the diagonal.

## Gears
<!-- bite: e57f0855-89c6-47fb-bb56-00c9bb79b154 -->

A gear with $N_1$ teeth drives one with $N_2$ teeth. The teeth that pass each other are equal in number, so $N_1\theta_1 = N_2\theta_2$. And an ideal gear stores no energy, so the work in equals the work out, $T_1\theta_1 = T_2\theta_2$. Together:

$$\frac{\theta_2}{\theta_1} = \frac{N_1}{N_2} = \frac{T_1}{T_2}$$

A small gear driving a big one ($N_1 < N_2$) **slows the output and multiplies its torque**. Each meshing pair reverses the direction of rotation, so an even number of gears in a line reverses the output and an odd number doesn't.

## Reflecting through gears
<!-- bite: 4b81e5c8-e066-4223-a2df-df4e362108f8 -->

A motor sees the load through the gears. Moving an inertia or damper from the load side to the motor side, it gets multiplied by the **square** of the gear ratio:

$$J_{at\ motor} = J_{load}\left(\frac{N_1}{N_2}\right)^2, \qquad B_{at\ motor} = B_{load}\left(\frac{N_1}{N_2}\right)^2$$

(The square appears because the gears scale both the angle and the torque.) Worked: a motor with $J_m = 0.5$ kg·m² drives an 8 kg·m² load with 4 N·m·s/rad of damping through gears with $N_1 = 25$, $N_2 = 100$. Then

$$J_{eq} = 0.5 + 8 \times (1/4)^2 = 1, \qquad B_{eq} = 4 \times (1/4)^2 = 0.25$$

The heavy load looks like half a unit of inertia to the motor. That's why motors drive loads through big gear reductions.

## The DC motor's equations
<!-- bite: 43f8bcfb-0509-4445-b705-efa2f9654fee -->

A DC motor turns current into torque and, while spinning, generates a voltage that opposes the supply (the **back emf**). With armature resistance $R_a$, inductance $L_a$, constant field:

1. **Torque**: $T_m = K_ti_a$, where $K_t$ is the **torque constant**.
2. **Back emf**: $e_b = K_b\omega_m$, where $K_b$ is the **back-emf constant**.
3. **Electrical**: $e_a = R_ai_a + L_a\,di_a/dt + e_b$.
4. **Mechanical**: $T_m = J\ddot\theta_m + B\dot\theta_m$ (plus any load torque).

In SI units, an ideal motor has $K_t = K_b$. Usually $L_a$ is small, and neglecting it, the transfer function from armature voltage to shaft angle is

$$\frac{\theta_m(s)}{E_a(s)} = \frac{K_t/(R_aJ)}{s\left(s + \dfrac{1}{J}\left(B + \dfrac{K_tK_b}{R_a}\right)\right)}$$

Notice $K_tK_b/R_a$ adds to $B$: **the back emf acts like extra damping.**

## The motor's constants from its curve
<!-- bite: ba6e9947-7b1f-415b-ba33-f85f2de02285 -->

At steady state, the motor's torque-speed curve is a straight line, and its two ends give both constants (the textbook's method):

1. **Stall** (speed 0, torque $T_{st}$): $e_a = R_aT_{st}/K_t$, so $K_t = R_aT_{st}/e_a$.
2. **No load** (torque 0, speed $\omega_{nL}$): $e_a = K_b\omega_{nL}$, so $K_b = e_a/\omega_{nL}$.

Worked: at $e_a = 100$ V a motor has no-load speed 50 rad/s and stall torque 100 N·m, with $R_a = 2$ Ω. Then $K_b = 100/50 = 2$ and $K_t = 2 \times 100/100 = 2$, equal, as they should be.

## Putting it together
<!-- bite: 21bb2b60-58c0-44f2-b916-c746c7d5bc22 -->

That motor drives the geared load from before, so $J = 1$ and $B = 0.25$ at the motor. Predict before reading on: what's $\theta_L/E_a$?

$$\frac{1}{J}\left(B + \frac{K_tK_b}{R_a}\right) = 0.25 + 2 = 2.25, \qquad \frac{K_t}{R_aJ} = 1$$

$$\frac{\theta_m}{E_a} = \frac{1}{s(s + 2.25)}, \qquad \frac{\theta_L}{E_a} = \frac{1}{4} \cdot \frac{1}{s(s + 2.25)} = \frac{0.25}{s(s + 2.25)}$$

A pole at the origin (angle is the integral of speed: type 1, lesson 15) and one at $-2.25$. That's the standard position-control plant you'll meet in almost every later example.

## The geared motor as a block diagram
<!-- bite: bf250300-2991-42c8-a60f-e666924547e9 -->

Here is the same plant drawn block by block, so you can see where each constant sits.

![Block diagram of the geared DC motor: armature voltage minus back emf, divided by the armature resistance, gives current; times Kt gives torque; through 1 over (J s + B) gives speed; integrating gives the motor angle, which the gear ratio N1 over N2 turns into the load angle; speed times Kb feeds back as the back emf.](images/ct-dc-motor.svg)

## Common pitfalls
<!-- bite: 66ba7a85-b127-4502-8ab2-bcb795298781 -->

1. **Reflecting by the ratio, not its square.** Inertia and damping scale by $(N_1/N_2)^2$.
2. **Inverting the gear ratio.** $\theta_2/\theta_1 = N_1/N_2$: the output turns less when it has more teeth.
3. **Forgetting the back emf.** It's the motor's built-in feedback and adds damping $K_tK_b/R_a$.
4. **Treating $K_t$ and $K_b$ as unrelated.** In SI units they're equal for an ideal motor.

## Check your understanding
<!-- bite: 4b8d5b35-23ad-4a15-984b-1c083f15959a -->

Try each one before you open the answer.

1. <!-- q: exact id="6b1d9e20" answer="0.33333" accept="1/3" sigfigs="3" -->
   A 20-tooth gear drives a 60-tooth gear. What is $\theta_2/\theta_1$?

   <details><summary>Answer</summary>

   $N_1/N_2 = 20/60 = 1/3$. The output turns a third as far, with three times the torque.

   </details>

2. <!-- q: exact id="c4a8f371" answer="1" -->
   A 9 kg·m² load sits behind that same 20:60 gear pair. What inertia does the motor see, in kg·m²?

   <details><summary>Answer</summary>

   $9 \times (20/60)^2 = 9/9 = 1$.

   </details>

3. <!-- q: exact id="2f9e5b06" answer="3" -->
   At 120 V, a DC motor's no-load speed is 40 rad/s. What is $K_b$, in V·s/rad?

   <details><summary>Answer</summary>

   $K_b = e_a/\omega_{nL} = 120/40 = 3$.

   </details>

4. <!-- q: mcq id="8d3c1a47" -->
   In $\theta_m/E_a = \dfrac{K_t/(R_aJ)}{s(s + (B + K_tK_b/R_a)/J)}$, what does the term $K_tK_b/R_a$ represent?

   - [ ] The motor's inertia
   - [x] Extra damping from the back emf
   - [ ] The gear ratio
   - [ ] The armature inductance

   <details><summary>Answer</summary>

   The back emf opposes the supply in proportion to speed, so the current, and therefore the torque, fall as speed rises: exactly what a damper does.

   </details>

5. <!-- q: open id="e0b6a83d" -->
   Why do motors usually drive heavy loads through a large gear reduction, judging by how inertia is reflected?

   <details><summary>Answer</summary>

   A load's inertia appears at the motor multiplied by $(N_1/N_2)^2$. With a 1:10 reduction, the load looks 100 times lighter, so a small, fast motor can accelerate it, while the gears also multiply the motor's torque at the load.

   </details>

## Before moving on
<!-- bite: 47abc184-19c7-4205-98a7-53037d87a551 -->

You can model rotational systems, gears and a DC motor. **Next:** [[control-theory/07-modelling-5|07 — Modelling 5: Linearisation and System Identification]], which deals with plants that aren't linear, and plants whose models you have to measure.

## Related
<!-- bite: 0cfcafd8-7f11-47b6-a3f2-c3f7b95b2e7c -->

- [[robotics/03-actuators-and-motion|Robotics: Actuators and Motion]]
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: a90c2e8b-6203-4007-abca-fd46a2db5f76 -->

**Level:** Intermediate. **Covers:** rotational elements, a two-inertia system, gear relations and reflected impedances, DC motor equations, motor constants from the torque-speed curve, and the geared motor's transfer function.

**Where it sits:** lesson 6 of 58, part 4 of the modelling lessons.

**Source:** the author's course notes, A. M. Hussein, *Control Engineering*, Benha University, chapter 6 (sections 5 and 7, examples 6, 10 and 13). Numbers and the diagram from `scripts/diagrams/control_theory.py`.
