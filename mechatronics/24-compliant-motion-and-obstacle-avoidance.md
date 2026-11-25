---
id: 31fd1258-e328-46ed-9532-3b5a4c9a6439
---

# Compliant Motion and Obstacle Avoidance

**Obstacle avoidance is planning a robot's path so it reaches its target without hitting anything, often with an artificial potential field that pulls it towards the goal and pushes it away from obstacles; constrained and compliant motion is moving while respecting joint limits, workspace limits and contact with surfaces.**

A robot vacuum steering round a chair leg, a warehouse robot keeping clear of people, and an arm wiping a table without crushing it are all doing this: getting to the goal while respecting what is in the way.

## Before you start
<!-- bite: ad2fca46-b7ed-4deb-99e0-5e44fa15d1db -->

You should know forward and inverse kinematics and reachability ([[mechatronics/18-forward-and-inverse-kinematics|Forward and Inverse Kinematics]]), and singularities ([[mechatronics/20-redundancy-and-singularities|Redundancy and Singularities]]). Distance between two points, √((x₂ − x₁)² + (y₂ − y₁)²), and the idea of a gradient (the direction in which a function rises fastest).

After this lesson you will be able to:

1. compute straight-line distances and the repulsive potential around an obstacle;
2. explain potential-field path planning, including its local-minimum trap;
3. handle joint limits and workspace constraints, and explain compliance as a spring–damper behaviour.

## What this last lesson adds
<!-- bite: fb20b8de-1ead-40b4-a38f-d5445f2011ca -->

Everything so far assumed empty space: the target was a point, and the arm went straight there. The T_6 tutorials put things in the way — an obstacle, joint limits, a wall the hand must not pass — and ask the robot to cope. That is **constrained motion**. And when the robot must touch something, like a table or a workpiece, it should give a little rather than fight — that is **compliant motion**.

The running example is **T_6 Q1**: a mobile robot going from (1.0, 2.0) to (5.0, 6.0), with a circular obstacle of radius 1.0 m at (3.0, 4.0), and a top speed of 1.0 m/s.

## The kid version
<!-- bite: b8cf652d-ab8b-4170-810a-59731149d90d -->

Imagine the target is a magnet pulling a marble across a table, and the obstacle is a magnet of the same pole, pushing the marble away. Let go, and the marble rolls towards the target and curves round the obstacle on its own. Nobody plans the curve; it just follows the pushes and pulls. That is a potential field.

**Where the analogy stops working.** If the obstacle sits exactly on the straight line between marble and target, the push and the pull can balance perfectly, and the marble stops dead in front of the obstacle — stuck. Real planners have to watch for that.

## Step 1: the straight-line distance
<!-- bite: 781eeaf4-4761-4fd2-8682-c15e349fd374 -->

Always start with the direct distance — it is the best you could possibly do, and it tells you the minimum time.

$$d = \sqrt{(x_d - x_0)^2 + (y_d - y_0)^2} = \sqrt{(5 - 1)^2 + (6 - 2)^2} = \sqrt{32} = 5.66\ \text{m}$$

At the top speed of 1.0 m/s, no path can take less than 5.66 s. But check the line itself: it runs along y = x + 1, and the obstacle's centre (3, 4) is **on it**. The straight path drives straight through the obstacle, so a detour is unavoidable.

## Step 2: potential fields
<!-- bite: 741fce6c-d890-47c8-a93f-fcc8c569a3f0 -->

A **potential field** gives every point a "height": low at the goal, high near obstacles. The robot simply rolls downhill, moving along the negative gradient — the direction the height falls fastest.

1. The **attractive potential** pulls towards the goal, U_att = ½k_a‖x − x_d‖², a bowl centred on the target.
2. The **repulsive potential**, as the tutorial gives it, pushes away from an obstacle — but only within a threshold distance r₀:

$$U_{rep}(r) = \frac{k_r}{2}\left(\frac{1}{r} - \frac{1}{r_0}\right)^2 \quad\text{for } r \le r_0, \qquad U_{rep} = 0 \text{ for } r > r_0$$

where r is the distance between the robot and the obstacle. As r shrinks, 1/r grows, so the potential climbs steeply — an invisible wall.

## Step 3: the potential at a point
<!-- bite: 18724c50-0e58-4bfe-ac92-ed3ad3e28f13 -->

**T_6 Q1(c):** k_r = 10 and r₀ = 1.5 m. Find the potential at (4.0, 5.0).

The distance to the obstacle's centre is r = √((4 − 3)² + (5 − 4)²) = √2 = 1.414 m. That is less than r₀ = 1.5, so the field is active:

$$U_{rep} = \frac{10}{2}\left(\frac{1}{1.414} - \frac{1}{1.5}\right)^2 = 5\,(0.7071 - 0.6667)^2 = 0.0082$$

The tutorial gives no attractive constant, so the "total" here is just the repulsive part; with an attractive field you would add ½k_a × (distance to goal)².

Notice the assumption: r was measured to the obstacle's **centre**. If you measure to its **surface** instead (r = 1.414 − 1.0 = 0.414 m), the same formula gives 15.27 — a very different number. The tutorial measures between robot and obstacle positions, so use the centre, and state it.

## Seeing the field at work
<!-- bite: 4df2351f-2dd0-4783-8bed-ead58be1529e -->

Here are two robots rolling down the field from Q1 (the paths use distance from the obstacle's surface, so the barrier is infinite at the surface):

![Potential-field path planning from (1, 2) to (5, 6) around a circular obstacle of radius 1 m at (3, 4). The straight line passes through the obstacle centre; gradient descent started exactly on that line stalls in front of the obstacle, while a start just off the line slides round it and reaches the target](images/robot-potential-field.svg)

The blue robot starts 0.15 m off the line: the push from the obstacle has a sideways part, which slides it round, and it reaches the goal. The red robot starts **exactly** on the line: the push and the pull point exactly opposite, balance at about (2.02, 3.02), and it stops — a **local minimum**.

## The local-minimum trap
<!-- bite: 0af83ee8-5852-45cc-a396-901e46d9ab6e -->

That stall is the famous weakness of potential fields. Wherever the attractive and repulsive forces cancel, the gradient is zero and the robot thinks it has arrived. Fixes include:

1. **Add a small random or sideways nudge** when the robot stops short of the goal.
2. **Add a rotational (vortex) field** around obstacles, so the push always has a sideways part.
3. **Plan globally first** (a road map or grid search) and use the field only for the local motion.

## T_6 Q3: a robot inside the obstacle zone
<!-- bite: eb6cf1c7-e3df-4f25-b41b-8984fc3af1a9 -->

Q3 moves a 3-joint arm's hand from (0, 0) to (5.0, 5.0) past a circular obstacle of radius 1.5 m at (2.5, 3.0), with k_r = 100 and r₀ = 2.0 m.

1. **Straight-line distance:** √(25 + 25) = 7.07 m.
2. **Potential at the robot's position (2.0, 2.5):** r = √(0.25 + 0.25) = 0.707 m, so U = 50(1/0.707 − 1/2.0)² = 50(1.414 − 0.5)² = **41.8**.
3. **Potential at the obstacle's centre (2.5, 3.0):** r = 0, and 1/r → ∞, so **U → ∞**.

How does this affect the motion? The robot's position is only 0.707 m from the centre of a 1.5 m obstacle — it is **inside** the obstacle's outline, so the plan has already failed to keep clear. The huge potential pushes it hard away from the centre, down and to the left, which is directly **away** from the target at (5, 5). It must back off and go round before it can make progress, and the infinite potential at the centre guarantees the field never drives it through.

## Constrained motion: check the reach first
<!-- bite: bb246880-653d-4be3-a6dd-a1950dfad122 -->

**T_6 Q2:** a 3-link arm with l = (1.0, 1.5, 1.0) m and joint limits θ₁ ∈ [0°, 90°], θ₂ ∈ [0°, 180°], θ₃ ∈ [0°, 120°] must put its hand at (3.0, 2.0).

Before any IK, check reachability (lesson 18):

$$R_{max} = 1.0 + 1.5 + 1.0 = 3.5\ \text{m} \qquad d = \sqrt{3^2 + 2^2} = 3.61\ \text{m}$$

d > R_max: **the target is out of reach**, whatever the joint limits. So no joint angles solve part (a). The best the arm can do is stretch straight towards it: θ₁ = atan2(2, 3) = 33.7°, θ₂ = θ₃ = 0 — which is within all three limits, but is also an arm singularity, so it can do nothing in that direction once there.

## Constrained optimisation for joint and workspace limits
<!-- bite: 9e0d781a-e2e0-485a-bc18-33a08026a06b -->

When the target *is* reachable but a solution breaks a limit, turn IK into a **constrained optimisation**:

$$\min_{q}\;\lVert x(q) - x_d\rVert^2 \quad\text{subject to}\quad q_{i,min} \le q_i \le q_{i,max}, \quad x(q) \le x_{max}$$

Practical ways to solve it:

1. **Clamp** each joint into its range after every iteration (projected gradient).
2. **Use the redundancy**: with spare joints, the null-space term from lesson 20 can push joints away from their limits while the hand still tracks the target.
3. **Add a barrier** to the cost, like the repulsive potential, that grows steeply as a joint nears its limit or the hand nears x_max = 4.0 m (Q2(c)) — so the path bends away before it violates the constraint.

## Compliance: a robot that gives
<!-- bite: c4b23cdf-1e5a-4243-b3ec-50766f9c5de5 -->

When a robot touches something, a pure position controller is dangerous: if the table is 1 mm higher than the model says, the controller pushes harder and harder to reach a position it cannot. **Compliant** control makes the hand behave like a **spring and damper** instead:

$$F = K\,(x_d - x) + B\,(\dot{x}_d - \dot{x})$$

Remember the mass–spring–damper of lesson 9? This is the same element laws, now programmed into the controller. Small K makes the hand soft (good for contact); large K makes it stiff (good for accuracy in free space). **Hybrid position/force control** goes further: control force in the direction you touch (pressing on the table) and position in the directions you move (sliding across it).

## Terms used in constrained motion
<!-- bite: ab5108fe-3e6e-49d9-a94c-5b6a89808f87 -->

1. **Potential field**: this is a function giving each point a "height", low at the goal and high near obstacles, which the robot descends.
2. **Attractive potential**: this is the part of the field that pulls towards the goal, usually U_att = ½k_a‖x − x_d‖².
3. **Repulsive potential**: this is the part that pushes away from obstacles within a distance r₀, here U_rep = (k_r/2)(1/r − 1/r₀)².
4. **Local minimum**: this is a point where the forces cancel short of the goal, so a gradient-following robot stops there.
5. **Constrained optimisation**: this is minimising a cost (such as distance to the target) while obeying limits (joint ranges, workspace bounds).
6. **Compliance**: this is a robot's ability to give under contact force, instead of rigidly holding position.
7. **Impedance control**: this is making the robot behave like a chosen spring–damper, F = K(x_d − x) + B(ẋ_d − ẋ).

## Common pitfalls and traps
<!-- bite: 709e7797-4625-4522-af02-bfe55580405b -->

- **Skipping the straight-line check.** It gives the minimum time and shows whether the direct path hits the obstacle.
- **Forgetting the r₀ cut-off.** Beyond r₀ the repulsive potential is zero, not small.
- **Measuring r inconsistently.** State whether r is to the obstacle's centre or its surface; the numbers differ enormously.
- **Trusting a potential field blindly.** It can stall in a local minimum, especially when the obstacle sits on the straight line.
- **Solving IK before checking reach.** In T_6 Q2 no joint limits matter, because the target is out of reach.
- **Using stiff position control for contact tasks.** Use compliance so small model errors do not become large forces.

## Check your understanding
<!-- bite: 1874816d-230a-4f4d-b102-0b1bb46eff12 -->

Try each one before you open the answer.

1. <!-- q: exact id="32d5dbe3" answer="10" tolerance="0.001" -->
   A robot moves from (0, 0) to (6, 8) in metres. What is the straight-line distance?

   <details><summary>Answer</summary>

   √(6² + 8²) = √100 = 10 m.

   </details>

2. <!-- q: exact id="2bc35787" answer="1.25" tolerance="0.001" -->
   The repulsive potential is U_rep = (k_r/2)(1/r − 1/r₀)² for r ≤ r₀. With k_r = 10 and r₀ = 2.0 m, what is U_rep when the robot is r = 1.0 m from the obstacle?

   <details><summary>Answer</summary>

   U = 5 × (1/1 − 1/2)² = 5 × 0.25 = 1.25.

   </details>

3. <!-- q: mcq id="46dbf4fa" -->
   With k_r = 10 and r₀ = 2.0 m, what is the repulsive potential when the robot is 2.5 m from the obstacle?

   - [x] 0, because 2.5 m is beyond r₀.
   - [ ] 0.05
   - [ ] 1.25
   - [ ] It is infinite.

   <details><summary>Answer</summary>

   Zero. The repulsive field only acts within r₀; beyond it the obstacle has no effect.

   </details>

4. <!-- q: exact id="43a95ed4" answer="3.60555" sigfigs="3" -->
   A 3-link arm with links 1.0, 1.5 and 1.0 m must reach (3.0, 2.0). How far is the target from the base, in metres? (Compare it with the arm's total length.)

   <details><summary>Answer</summary>

   √(9 + 4) = 3.61 m — more than the 3.5 m total length, so the target is unreachable.

   </details>

5. <!-- q: mcq id="f3767082" -->
   A robot following a potential field stops 1 m short of its goal, directly in front of an obstacle that lies on the straight line to the goal. What has happened?

   - [x] It is in a local minimum, where the attractive and repulsive forces cancel.
   - [ ] It has reached the goal.
   - [ ] The repulsive potential has become zero.
   - [ ] Its top speed is too low.

   <details><summary>Answer</summary>

   A local minimum: the pull towards the goal and the push from the obstacle point exactly opposite and balance, so the gradient is zero. A sideways nudge or a vortex field gets it moving again.

   </details>

6. <!-- q: open id="98b05381" -->
   Explain what compliant (impedance) control is, how it relates to the mass–spring–damper model, and why it is used when a robot touches a surface.

   <details><summary>Answer</summary>

   Impedance control makes the robot's hand behave like a programmed spring and damper: F = K(x_d − x) + B(ẋ_d − ẋ), so the force it applies grows with how far and how fast it is from where it wants to be — the same element laws as the spring K and damper f in the mass–spring–damper. When touching a surface, a rigid position controller would push harder and harder if the surface is even slightly out of place, damaging the part or the robot; with compliance, a small position error produces only a small, controlled force, so the robot presses gently and safely. K sets how soft or stiff it feels, B how much it resists fast motion.

   </details>

## Before moving on
<!-- bite: 010439cf-1b53-444e-b961-f9bff7b183a0 -->

You are done when you can compute distances and repulsive potentials (stating where r is measured), explain how a potential field steers a robot and how it gets stuck, check reach before solving constrained IK, and describe compliance as a programmed spring–damper.

Recap: d = √(Δx² + Δy²) gives the minimum path and time; U_rep = (k_r/2)(1/r − 1/r₀)² inside r₀, zero outside; follow −∇U, watch for local minima; handle limits by clamping, null-space motion or barriers; compliance F = K(x_d − x) + B(ẋ_d − ẋ).

That is the end of the course. Go back to the [[mechatronics/index|Mechatronics]] index for the full map, or revisit the exam topics through the end-of-lesson quizzes.

## Related
<!-- bite: 94b592d0-c396-4e60-b871-4e8cc863231e -->

- [[robotics/10-motion-planning|Robotics: Motion Planning]]: road maps and sampling-based planners beyond potential fields.
- [[mechatronics/09-translational-systems|Translational Systems]]: the spring–damper behind compliance.

## About this lesson
<!-- bite: 2033b1d5-596f-47e8-b93e-7fb61e7ac8ef -->

**Level:** coordinate geometry and gradients. It covers straight-line distance, attractive and repulsive potentials, the potential at a point, local minima, a robot inside an obstacle zone, reachability under joint limits, constrained optimisation, and compliant (impedance) control, worked through the T_6 tutorial questions. The tutorial's r is taken as distance to the obstacle's centre; the path picture measures it from the surface so the barrier is solid, and says so. It is lesson 24, the last of section F. Every number and both simulated paths are checked in `scripts/diagrams/mechatronics_robotics.py`.

**Source:** T_6, "Robot-Compliant and Constrained Motion & Obstacle Avoidance" tutorial questions by Dr John Ogbemhe (University of Lagos SSG 515/519), Questions 1–3.
