# Build Your Own Physics Engine

> **[Intermediate → Advanced]** · 2D rigid bodies, collision detection and a constraint solver. **The one where being visibly wrong is the test.**

## What you're building

**A 2D rigid-body physics engine** — boxes and circles that fall, collide, bounce, stack and come to rest — with a renderer simple enough to watch it work.

**And what you're deliberately not:** 3D, soft bodies, fluids, or competing with Box2D. **2D is the right scope** — every concept transfers, and the maths stays legible.

**Why this one:** it's the rare project where **the bug reports itself.** A wrong integrator makes a pendulum gain energy; a wrong solver makes a stack jitter; a wrong restitution makes a ball climb. **You can see all of it.**

## What you need first

- **Vectors** — add, scale, dot, cross (in 2D, a scalar) → [[game-development/01-what-game-development-actually-is|the maths you need]]
- **Newton's laws**, and $F = ma$
- **The fixed timestep**, and why → [[game-development/02-engines-and-the-game-loop|the game loop]]
- **The theory this implements** → [[game-development/04-game-physics|game physics]]
- Helpful: [[foundations/numerical-methods/08-ordinary-differential-equations|ODEs]]

**Any language with a simple drawing surface.** Python + pygame, JS + canvas, C++ + SDL, Rust + macroquad. **Rendering must be trivial or it becomes the project.**

## The build order

**1. A fixed-timestep loop with a circle falling.**
Position, velocity, gravity. Integrate at a **fixed** `dt` and render.
*Works when:* it falls smoothly and identically every run → [[game-development/02-engines-and-the-game-loop|note 02]].

**2. Semi-implicit Euler, and see why.**
Implement explicit Euler first: `pos += vel*dt; vel += acc*dt`. Then swap the order. Simulate a spring or pendulum with each for a minute.
*Works when:* **explicit Euler visibly gains energy and the semi-implicit version doesn't.** Two lines swapped. **Do not skip this** — it's the clearest demonstration of numerical stability you'll get.

**3. Circle–circle collision.**
Overlapping if distance < sum of radii. Compute penetration depth and the collision normal.
*Works when:* two circles report contact exactly when they visually touch.

**4. Impulse resolution.**
On contact, apply an impulse along the normal to separate them. Restitution controls bounciness.
*Works when:* a ball bounces, and with restitution 1 it returns to roughly its drop height. **Not higher** — higher means you're injecting energy.

**5. Positional correction.**
Impulses alone leave objects slightly overlapping, and they sink. Push them apart a fraction (~20–80%) of the penetration each step.
*Works when:* a resting ball stops sinking into the floor. **Correct 100% and it jitters; correct 0% and it sinks.**

**6. AABB collision, then oriented boxes.**
Axis-aligned first. Then rotation, using the **separating axis theorem** — two convex shapes are disjoint iff some axis exists on which their projections don't overlap.
*Works when:* rotated boxes collide correctly at any angle.

**7. Rotation and angular dynamics.**
Moment of inertia, torque, angular velocity. An impulse away from the centre of mass now produces spin.
*Works when:* a box dropped on a corner tips over rather than landing flat.

**8. Friction.**
A tangential impulse, bounded by the normal impulse times the friction coefficient (Coulomb).
*Works when:* a box slides down a slope and stops on a shallow enough one.

**9. The iterative solver.**
Multiple contacts must be resolved together. Collect all contacts, then loop over them applying corrections **4–10 times per step**.
*Works when:* **a stack of five boxes stands still.** This is the hardest milestone and the most satisfying — and if it jitters, more iterations is the knob → [[game-development/04-game-physics|note 04]].

**10. Broad phase.**
Pair testing is O(n²). Add a spatial grid or sweep-and-prune.
*Works when:* 500 bodies run at 60 fps, and you can show the pair-test count dropped by orders of magnitude.

**11. Sleeping.**
Bodies below a velocity threshold for N frames stop being simulated until touched.
*Works when:* a settled stack costs nearly no CPU.

## The parts that will bite you

**Explicit Euler.** Covered above, and worth the detour.

**Tunnelling.** A fast object passes through a thin wall because it was on one side at step *n* and the other at *n+1*, never intersecting. Smaller `dt`, or raycast along the motion path.

**Jitter in stacks.** Solver iterations fighting each other. More iterations, a smaller correction factor, and a small **slop** (allow ~1cm penetration before correcting).

**Objects sinking.** Positional correction missing or too weak.

**Energy gain.** Restitution > 1 somewhere, wrong integrator, or correction adding velocity. **A ball that climbs higher each bounce is the classic symptom.**

**The 2D cross product.** In 2D, `cross(a,b)` is the scalar `a.x*b.y - a.y*b.x`, and `cross(scalar, vec)` is a different operation. Mixing them silently produces wrong torque.

**Floating-point drift** in long-running stacks — small errors accumulate → [[foundations/numerical-methods/02-floating-point-and-error|floating point]].

## How to know it works

1. **A pendulum conserves energy** for a minute
2. **A ball with restitution 1 returns to its drop height** — not higher
3. **Five boxes stack and stay still**
4. **A box tips on a corner** rather than landing flat
5. **A box stops on a shallow slope and slides on a steep one**
6. **500 bodies at 60 fps** after broad phase
7. **Determinism** — same seed, same result, every run

## Where to stop

**Stop at a stable stack with friction and a broad phase.** 3D, continuous collision detection, joints and soft bodies are each substantial projects with sharply diminishing returns on understanding.

**You will have learned:** why game physics is *approximation under a deadline* rather than simulation, why solvers are allowed not to converge, what "restitution" and "slop" actually mean in an engine's inspector, and why every engine separates `Update` from `FixedUpdate` → [[game-development/README|game development]].

**Reference implementation:** Box2D's source is readable and well-commented, and Erin Catto's GDC talks are the canonical explanation of the sequential-impulse solver.

## Related
- [[game-development/04-game-physics|game physics]] — the theory this implements
- [[game-development/engines/from-scratch|from scratch]] — where this fits in an engine
- [[foundations/numerical-methods/08-ordinary-differential-equations|ODEs]] — integrators properly
- [[engineering/01-continuum-mechanics/README|continuum mechanics]] — what real simulation looks like

*Source: [reference] — build guide, Aug 2026.*
