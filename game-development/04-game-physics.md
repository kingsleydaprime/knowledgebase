# Game Physics

> **[Intermediate]** · Collision detection, integration and constraint solving — approximations that must look right at 60 Hz.

**Game physics is not simulation.** It's a set of approximations tuned so that objects behave plausibly, fast, and stably. Being *visibly* wrong is the bug; being *actually* wrong is the design.

## The two halves

**Collision detection** — what is touching what? *(the expensive part)*
**Collision response** — what should happen about it? *(the subtle part)*

## Broad phase and narrow phase

Testing every pair of *n* objects is **O(n²)** — 1,000 objects is half a million tests per frame. So it's split:

**Broad phase** — cheaply reject pairs that cannot possibly touch. Test **axis-aligned bounding boxes (AABBs)**, which overlap-test in six comparisons, using a spatial structure: a **uniform grid**, a **BVH** (bounding volume hierarchy, usually a dynamic AABB tree), or **sweep and prune** (sort by axis, check overlapping intervals).

**Narrow phase** — exact tests on surviving pairs. Sphere-sphere is trivial; convex-convex uses **GJK** (Gilbert–Johnson–Keerthi) to detect intersection, and **EPA** (expanding polytope algorithm) to find how deep and in which direction. **SAT** (separating axis theorem) is the simpler alternative for boxes and simple polyhedra, and the intuition is worth having: *two convex shapes are disjoint if and only if some axis exists on which their projections don't overlap.*

**Concave shapes are decomposed into convex pieces**, because every efficient algorithm here assumes convexity. That's why engines ask you for a "convex hull" or "compound collider" and why a concave mesh collider is expensive and often static-only.

## Integration

Given force, find motion — numerically, at discrete steps → [[foundations/numerical-methods/08-ordinary-differential-equations|ODEs]].

**Explicit Euler** — the obvious one, and wrong:
```
velocity += acceleration * dt
position += velocity * dt
```
**It adds energy.** A pendulum swings higher each cycle; an orbit spirals outward. Fine for particles that die quickly, unacceptable for anything persistent.

**Semi-implicit (symplectic) Euler** — update velocity *first*, then use the new velocity:
```
velocity += acceleration * dt
position += velocity * dt      # ← the NEW velocity
```
**Nearly identical code, and it conserves energy approximately over time.** This is what most game engines actually use, and the difference between stable and exploding is that one ordering.

**Verlet** — stores previous position instead of velocity. Stable, and natural for cloth and soft bodies, because positional constraints can be applied directly.

**RK4** — accurate, four evaluations per step. Used where accuracy matters more than speed; usually overkill for games.

**And this is why the fixed timestep matters** → [[game-development/02-engines-and-the-game-loop|the game loop]]. Integrators are stability-sensitive to step size: a variable `dt` makes behaviour depend on frame rate, so the same jump is different on a faster machine.

## Tunnelling

A fast object moves further in one step than the thickness of a wall, so it is never intersecting on any tested frame and passes straight through. **A bullet at 500 m/s moves 8 metres per 60 Hz step.**

Fixes, in increasing cost:
- **Smaller timestep** for fast objects
- **Raycast along the movement path** instead of testing the endpoint — the standard answer for projectiles
- **Continuous collision detection (CCD)** — sweep the shape along its path and solve for the time of impact. Expensive; enable it per-object, not globally

## Constraint solving

Real scenes are stacks, joints and contacts that must all hold simultaneously. Solving them exactly is a large system of equations — too slow.

**So engines iterate.** Sequential impulses: walk the constraint list, correct each one a little, repeat 4–10 times per step. It converges toward a plausible answer and **is deliberately allowed not to converge fully**.

That single fact explains the artefacts everyone has seen:

- **Jitter** in tall stacks — corrections fight each other
- **Sinking** — objects settle slightly into the floor before the solver pushes back
- **Rubbery joints** under load — the constraint isn't fully satisfied
- **Explosions** when too many contacts interact — corrections compound

**Increasing solver iterations reduces all of these and costs time.** That's the tuning knob, and it's a direct frame-budget trade.

## Rotation, and why quaternions

Euler angles suffer **gimbal lock** — at certain orientations two axes align and a degree of freedom is lost. They also interpolate badly.

**Quaternions** avoid both: compact (4 floats), no lock, and they interpolate smoothly with **slerp**. You need almost no theory — construct from axis-angle, multiply to compose, slerp to interpolate.

**This vault already covers them properly in [[robotics/04-rigid-body-transforms|rigid body transforms]]**, because robotics needs identical maths. Rotation, transforms and kinematics are the same subject in both fields.

## When not to use a physics engine

**A physics engine is often the wrong tool for gameplay.** Mario's jump is not a ballistic trajectory — it's a hand-tuned curve, with variable gravity depending on whether the button is held, because *that feels better*.

**Realism and good feel are frequently in opposition**, and feel wins. Many great platformers use physics only for collision detection and drive movement entirely with authored curves and state machines.

**Use the physics engine for:** ragdolls, debris, vehicles, stacking, anything incidental.
**Author by hand:** the player character's movement, almost always.

## Related
- [[foundations/numerical-methods/08-ordinary-differential-equations|ODEs]] — integrators, properly
- [[robotics/04-rigid-body-transforms|rigid body transforms]] — quaternions, already written
- [[game-development/02-engines-and-the-game-loop|the game loop]] — the fixed timestep
- [[engineering/01-continuum-mechanics/README|continuum mechanics]] — what real simulation looks like

*Source: [reference] — cross-referenced against [roadmap.sh game-developer](https://roadmap.sh/game-developer).*
