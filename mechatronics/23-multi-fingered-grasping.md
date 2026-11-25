---
id: 18299341-1ce0-4c3a-9428-6eb4b31d9995
---

# Multi-Fingered Grasping

**Grasping is holding an object with several fingers so that the contact forces keep it still against gravity and any push, and a good grasp is one where the fingers can resist every disturbance without the object slipping.**

You do it a thousand times a day without thinking: lifting a cup by its handle, pinching a coin, carrying a bag. A robot hand has to work out where to put its fingers and how hard to press — too soft and the object slips, too hard and it breaks.

## Before you start
<!-- bite: c12f4d71-8bfe-4fc3-ae44-5ad0b11dc096 -->

You should know what torque is (force times its perpendicular distance from a point), vector addition, and the manipulability index ([[mechatronics/20-redundancy-and-singularities|Redundancy and Singularities]]).

After this lesson you will be able to:

1. use friction to find the squeeze force a grasp needs;
2. explain equilibrium, force closure and form closure;
3. compute the course's finger torques, total grasp force and grasp-quality index, and judge a grasp against a threshold.

## What a grasp has to do
<!-- bite: 220d2e15-27cb-478a-a882-f1b739c11776 -->

So far in this section the robot's hand has been a point we placed. Now we open it up. A multi-fingered hand touches the object at a few **contact points**, and at each one the finger pushes with a **contact force**. Those few forces must do all the work:

1. **Hold the object up** against gravity.
2. **Keep it from turning** — the forces' torques must balance.
3. **Keep it from slipping** at each contact, which friction must allow.
4. **Resist disturbances** — a bump, a tug, a sudden acceleration of the arm.

The running example is the T_5 tutorial's **three-fingered hand** holding a triangular object, with finger forces 10, 12 and 8 N.

## The kid version
<!-- bite: fcaa290c-4ee4-4a0b-bc9c-7642ffce5470 -->

Try picking up a ball with two pencils. Push gently and it slips out; squeeze from opposite sides and it holds. Now try it with three pencils spread around the ball — it is much harder to knock loose, because whichever way you push the ball, some pencil is already pushing back. That "some finger is always pushing back" is what engineers call **force closure**.

**Where the analogy stops working.** Pencils can only push. Real fingertips can also grip sideways through friction, which is why two padded fingers can hold what two pencil points cannot.

## Friction: why squeezing holds things up
<!-- bite: 7e5b1ec4-3753-4e21-b93b-a20159781935 -->

A fingertip pressing on a surface with normal force N can also resist sliding, up to a friction force of μN, where μ is the coefficient of friction. In 3-D, the allowed contact forces form a **friction cone** around the surface normal; push outside it and the finger slips.

**Worked example.** A 0.5 kg object is held between two fingers pressing from opposite sides, with μ = 0.4. Its weight is 0.5 × 9.81 = 4.905 N, and it is held up only by friction at the two contacts:

$$2\mu N \ge W \quad\Longrightarrow\quad N \ge \frac{4.905}{2 \times 0.4} = 6.13\ \text{N}$$

Each finger must press with at least 6.13 N. Any less and it slides down; in practice the hand presses harder, for a safety margin against bumps.

## Equilibrium of the grasped object
<!-- bite: 38a5139d-6509-4fe5-a9fe-64560e4d4e5e -->

For the object to stay still, the contact forces plus gravity must balance in two ways:

1. **Net force zero:** the force vectors add to zero (or exactly cancel the weight).
2. **Net torque zero:** their turning effects about any point cancel.

If the net force is not zero, the object accelerates out of the hand; if the net torque is not zero, it spins.

## Force closure and form closure
<!-- bite: 5c97297d-baf3-4458-9598-27ca6755a6e5 -->

These are the two ideas the exam calls a "stable" grasp:

1. **Force closure**: the fingers can resist **any** external force and torque on the object by adjusting their contact forces, while staying inside their friction cones. Two fingers pressing exactly opposite each other with friction (an antipodal grasp) can achieve it in a plane.
2. **Form closure**: the fingers' **positions alone** trap the object, with no reliance on friction — like a peg boxed in on all sides. In a plane it needs at least four frictionless contacts.

Formally, the **grasp matrix** G maps the finger forces f to the net force and torque on the object, w = Gf. Force closure needs G to be able to produce any w, and a common **grasp-quality** measure is how small a finger force is needed to resist the worst disturbance (for example, the smallest singular value of G).

## The tutorial's simple measures
<!-- bite: 01515daf-e04b-40b7-abe2-9f973ece1bc6 -->

The T_5 tutorials use simpler indices that you can compute by hand. They are teaching simplifications, not full force-closure tests, so state them as such in an answer:

1. **Finger torque** about the hand centre: τᵢ = rᵢFᵢ, taking each force at right angles to its radius rᵢ (the largest turning effect it can have).
2. **Total torque** of the hand: Στᵢ, compared with a stability threshold.
3. **Total grasp force**: ΣFᵢ, the sum of the finger force magnitudes — how hard the hand squeezes.
4. **Grasp quality**: Q = Σ rᵢFᵢ, with rᵢ = |Pᵢ| the distance from the object's centre to contact point Pᵢ — compared with a threshold Q_threshold.

## Tutorial Q1: three fingers, torque test
<!-- bite: 0aba0c56-71c7-4591-900c-65f5351520f2 -->

Three fingers press with F = (10, 12, 8) N at contact points 0.05, 0.06 and 0.04 m from the hand centre, at 30°, 120° and 240°:

![Three fingers acting on an object around the hand centre O: contact points at 30, 120 and 240 degrees and 5, 6 and 4 centimetres from O, each finger pushing at right angles to its radius with 10, 12 and 8 newtons, so each turns the object the same way about O](images/robot-grasp-three-fingers.svg)

1. **Finger torques:** τ₁ = 10 × 0.05 = 0.50 N·m, τ₂ = 12 × 0.06 = 0.72 N·m, τ₃ = 8 × 0.04 = 0.32 N·m.
2. **Total torque:** 0.50 + 0.72 + 0.32 = **1.54 N·m**.
3. **Stability test:** 1.54 < τ_threshold = 2.0 N·m, so by the tutorial's criterion this grasp is **not** strong enough. The fix is to press harder or place the fingers further from the centre.

## Tutorials Q2 and Q3: total grasp force
<!-- bite: d1b753c9-416b-4e51-bddf-2ff6357b5d93 -->

**Q2:** four fingers press on a cube with 5, 6, 7 and 4 N. Total grasp force = 5 + 6 + 7 + 4 = **22 N**.

**Q3:** three fingers press on a cylinder with 15, 14 and 13 N at 45°, 135° and 225°. Total force = **42 N**.

Q2(b) also asks for force closure "where d is the distance from the centre of the object to the centre of mass of the hand". The point of d: if the hand's grip is centred d away from the object's centre of mass, the weight acting at that offset produces a torque W·d that the fingers must also resist — so a larger offset makes force closure harder to achieve. (The tutorial does not give its formula, so state the idea and the torque W·d.)

## Tutorials Q4 and Q5: grasp quality
<!-- bite: fecbb12e-81c8-4ac0-b280-3fd3001e9674 -->

**Q4:** forces 12, 10 and 15 N at P₁ = (0.1, 0.2), P₂ = (−0.1, 0.3), P₃ = (0.2, −0.1) m. The distances are r = 0.224, 0.316 and 0.224 m, so

$$Q = 12(0.224) + 10(0.316) + 15(0.224) = 9.20\ \text{N·m}$$

**Q5:** a 4-fingered hand on a 0.2 m × 0.5 m box, forces 10, 12, 9, 11 N at P₁ = (0.1, 0.2), P₂ = (−0.1, 0.3), P₃ = (0.3, −0.2), P₄ = (−0.2, 0.4). With r = 0.224, 0.316, 0.361 and 0.447 m:

$$Q = 2.24 + 3.79 + 3.25 + 4.92 = 14.20\ \text{N·m}$$

Against Q_threshold = 50 N·m, Q = 14.2 is **far from sufficient** to prevent slipping by that test — the fingers would need to press roughly 3.5 times harder, or sit further out.

## Dexterity: finger placement and force distribution
<!-- bite: fc43fb81-dc34-455b-8d49-2c513841275c -->

Q3(b–c) and Q5(b) ask about **dexterity** — how well the hand can move the object in its grasp — measured, as for arms, by a **manipulability index** of the hand's Jacobian, w = √det(JJᵀ) (or the norm ‖J‖): larger means the fingers can move and push the object more freely in every direction. Two practical effects:

1. **Finger placement.** Fingers spread around the object, far from its centre, have long moment arms: they resist turning better and give a better-conditioned grasp. Fingers bunched together, or nearly in a line, approach a singular, low-manipulability configuration.
2. **Force distribution.** Evenly shared forces keep every contact well inside its friction cone. One finger doing most of the work is the first to slip.

## Terms used in grasping
<!-- bite: 1f3f0e69-6599-4d8f-bc42-df5705e4ab96 -->

1. **Contact point**: this is where a finger touches the object.
2. **Contact force**: this is the force a finger applies at its contact point — a normal part pressing in, and a tangential part from friction.
3. **Friction cone**: this is the set of contact-force directions that will not slip, all within angle tan⁻¹μ of the surface normal.
4. **Force closure**: this is a grasp that can resist any external force and torque by adjusting the finger forces within their friction cones.
5. **Form closure**: this is a grasp that traps the object by the fingers' positions alone, without needing friction.
6. **Grasp matrix, G**: this is the matrix that maps the finger contact forces to the net force and torque on the object.
7. **Grasp quality**: this is a number measuring how well a grasp resists disturbances. The tutorials use Q = Σ rᵢFᵢ.
8. **Dexterity**: this is how well a hand can move and reorient an object in its grasp.

## Common pitfalls and traps
<!-- bite: 02f31245-4dac-4bee-bd41-b27cc1d79f37 -->

- **Forgetting friction is limited.** Friction can only supply up to μN; past that, the finger slips.
- **Using τ = rF when the force is not perpendicular.** In general τ = rF sin(angle between them); the tutorials assume perpendicular.
- **Treating "total grasp force" as the net force.** The squeeze (sum of magnitudes) is large in a good grasp; the net force on a still object must be zero.
- **Claiming force closure from a single number.** Q = Σ rᵢFᵢ is the course's simplified index. Say so, and say what a full check would need (friction cones and the grasp matrix).
- **Bunching the fingers.** Close or collinear fingers give poor resistance to turning and low manipulability.

## Check your understanding
<!-- bite: 46cc9e69-9ee4-4b5f-8ed4-38f795eff30f -->

Try each one before you open the answer.

1. <!-- q: exact id="7c81f498" answer="0.6" tolerance="0.001" -->
   A finger presses with 15 N at right angles to its radius, at a contact point 0.04 m from the hand centre. What torque does it produce about the centre, in N·m?

   <details><summary>Answer</summary>

   τ = rF = 0.04 × 15 = 0.6 N·m.

   </details>

2. <!-- q: exact id="04f85186" answer="9.81" tolerance="0.01" -->
   A 1.0 kg object is held between two fingers pressing from opposite sides, held up by friction alone, with μ = 0.5. Taking g = 9.81 m/s², what is the smallest normal force, in newtons, each finger must apply?

   <details><summary>Answer</summary>

   2μN ≥ mg, so N ≥ 9.81 / (2 × 0.5) = 9.81 N.

   </details>

3. <!-- q: exact id="419b9c5d" answer="9" tolerance="0.01" -->
   Two fingers grasp an object. Finger 1 presses with 10 N at P₁ = (0.3, 0.4) m and finger 2 with 20 N at P₂ = (0, 0.2) m, measured from the object's centre. Using the course's grasp-quality index Q = Σ rᵢFᵢ with rᵢ = |Pᵢ|, what is Q, in N·m?

   <details><summary>Answer</summary>

   r₁ = √(0.09 + 0.16) = 0.5 m and r₂ = 0.2 m, so Q = 10(0.5) + 20(0.2) = 5 + 4 = 9 N·m.

   </details>

4. <!-- q: mcq id="aa961ea8" -->
   Three fingers produce torques of 0.45, 0.60 and 0.70 N·m about the hand centre. The grasp is judged stable if the total torque exceeds 2.0 N·m. Is it stable by this test?

   - [ ] Yes, the total is 2.05 N·m.
   - [x] No, the total is 1.75 N·m.
   - [ ] Yes, each finger exceeds 0.4 N·m.
   - [ ] No, the total is 0.70 N·m.

   <details><summary>Answer</summary>

   0.45 + 0.60 + 0.70 = 1.75 N·m, below 2.0 N·m, so not stable by the test.

   </details>

5. <!-- q: mcq id="a82591a4" -->
   What is the difference between force closure and form closure?

   - [x] Force closure resists any disturbance using contact forces including friction; form closure traps the object by finger positions alone.
   - [ ] Force closure needs more fingers than form closure.
   - [ ] Form closure uses friction; force closure does not.
   - [ ] They are two names for the same thing.

   <details><summary>Answer</summary>

   Force closure relies on the contact forces (with friction) being adjustable to resist anything; form closure relies only on geometry, with no friction needed — so form closure usually needs more contacts.

   </details>

6. <!-- q: open id="be80c089" -->
   Explain how finger placement and force distribution affect the dexterity and stability of a grasp.

   <details><summary>Answer</summary>

   Spreading the fingers around the object and away from its centre gives longer moment arms, so the same forces resist more torque, and keeps the hand's Jacobian well-conditioned (higher manipulability, better dexterity); bunched or nearly collinear fingers approach a singular, weak configuration. Sharing the force evenly keeps every contact well inside its friction cone, so no single finger is close to slipping; an uneven distribution makes the most-loaded finger slip first and can leave the net force or torque unbalanced.

   </details>

## Before moving on
<!-- bite: e3930f60-b020-4348-9053-98e50aca6c9c -->

You are done when you can find the squeeze force from friction, explain equilibrium, force closure and form closure, and compute and judge the tutorial's finger torques, total force and grasp quality.

Recap: friction holds if 2μN ≥ W; a still object needs zero net force and torque; force closure resists any disturbance using friction, form closure by geometry alone; tutorials: τᵢ = rᵢFᵢ, ΣFᵢ, Q = Σ|Pᵢ|Fᵢ against thresholds.

Next, [[mechatronics/24-compliant-motion-and-obstacle-avoidance|Compliant Motion and Obstacle Avoidance]] — the last lesson — moves the robot through the world: around obstacles, within joint limits, and gently against surfaces.

## Related
<!-- bite: bb964255-e0b1-47bd-aa9a-97582cc2907b -->

- [[robotics/02-sensors-and-perception|Sensors and Perception]]: force and touch sensors in robot hands.
- [[mechatronics/20-redundancy-and-singularities|Redundancy and Singularities]]: the manipulability index used for dexterity.

## About this lesson
<!-- bite: 8f1beb59-d286-4b1d-a632-a69fe692b2c2 -->

**Level:** forces, torques and vectors. It covers contact and friction, equilibrium, force and form closure, the grasp matrix, the T_5 tutorial measures (finger torque, total grasp force, grasp quality) worked for Q1–Q5, and dexterity. The tutorial sheet gives questions without the theory or every formula, so the theory here is the standard treatment, and the tutorial's indices are labelled as the course's simplified measures. It is lesson 23, in section F. Every number is checked in `scripts/diagrams/mechatronics_robotics.py`.

**Source:** T_5, "Multi-Fingered Hand Grasping and Manipulation" tutorial questions by Dr John Ogbemhe (University of Lagos SSG 515/519), Questions 1–5.
