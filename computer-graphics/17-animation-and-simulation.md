---
id: ee555b02-8c1c-45e7-91b9-9ec49c5b36c2
---

# Animation and Simulation

Animation is making things move over time; simulation uses physics to work out how.

## What animation and simulation are
<!-- bite: 0ed71b81-b300-4763-869f-f242d03e5eca -->

Animation is making things move over time, and simulation is using the rules of physics to work out how they should move. A game character walking, a car crashing or cloth flapping in the wind all come from these methods.

Next: keyframe animation.

## Keyframe animation
<!-- bite: 675129fb-7994-4273-a921-2450f7e3345d -->

**Store poses at key times; interpolate between them.**

**Interpolating positions is straightforward** — linear, or a spline for smoothness. → [[mathematics/07-applied-and-computational/01-numerical-methods/06-interpolation-and-approximation|Interpolation]]

**Interpolating rotations is not.**

> **Never interpolate Euler angles.** You get gimbal-lock artefacts and a path that wobbles rather than rotating smoothly.
>
> **Never interpolate rotation matrices element-wise.** The result isn't a rotation matrix at all.
>
> **Use quaternion SLERP** — constant angular velocity along the shortest arc:
> $$\text{slerp}(q_0,q_1,t) = \frac{\sin((1-t)\theta)}{\sin\theta}q_0 + \frac{\sin(t\theta)}{\sin\theta}q_1$$
>
> **And check the sign first.** $q$ and $-q$ are the same rotation, so **if $q_0\cdot q_1 < 0$, negate one** — otherwise you interpolate the long way round, and the object spins 350° instead of 10°. **A classic and very visible bug.** → [[robotics/04-rigid-body-transforms|Quaternions]]

**Easing** — `smoothstep` and its relatives shape the timing. **Linear interpolation looks mechanical**; the ease-in/ease-out that animators use is a perceptual necessity, not decoration.

## Skeletal animation
<!-- bite: 2a7776dc-0a06-4fd7-a9bb-7eea91fccf02 -->

**A hierarchy of bones deforms a mesh.**

**Linear blend skinning:** each vertex is influenced by up to four bones with weights summing to 1:

$$\mathbf{v}' = \sum_i w_i\,M_i\,B_i^{-1}\,\mathbf{v}$$

**$B_i^{-1}$ is the inverse bind pose** — it moves the vertex into bone-local space, then $M_i$ places it by the current pose.

**The classic artefact — the candy wrapper:** twist a joint 180° and the mesh collapses at the twist, because **you're averaging *matrices*, and the average of two opposite rotations is a degenerate transform.**

## Dual quaternion skinning
<!-- bite: f26556b7-eaef-4bdc-82aa-c57bd1e6cb89 -->

**Dual quaternion skinning** fixes it by interpolating in a space where the average of two rotations is a rotation. **Slight volume bulging instead**, which is far less objectionable.

**Runs in the vertex shader**, with bone matrices in a uniform buffer — one of the standard uses of the vertex stage.

**Inverse kinematics** — *"put the hand here, work out the joint angles."* **Exactly the [[robotics/06-inverse-kinematics|robotics problem]]**, and graphics uses the same methods: analytic two-bone solutions for limbs, CCD or FABRIK for chains. **Used for foot placement on uneven terrain and for hands reaching objects.**

## Blend trees, state machines and IK
<!-- bite: 2745daf8-1a71-46ad-beab-a7b50cfe371d -->

**Blend trees and state machines** combine animations — walk blended with run by speed, layered upper/lower body. **Motion matching** searches a database for the clip best matching current velocity and desired direction, and has largely replaced hand-built blend trees in AAA games.

## Rigid body physics
<!-- bite: c01565bb-a125-4910-ab53-6f39838ecdfe -->

**Integrate the equations of motion.** → [[mathematics/07-applied-and-computational/01-numerical-methods/08-ordinary-differential-equations|ODEs]]

$$\dot{\mathbf{x}} = \mathbf{v}, \qquad \dot{\mathbf{v}} = \mathbf{F}/m$$
$$\dot{\mathbf{q}} = \tfrac{1}{2}\boldsymbol\omega\,q, \qquad I\dot{\boldsymbol\omega} + \boldsymbol\omega\times I\boldsymbol\omega = \boldsymbol\tau$$

**Rotation is the awkward half** — the inertia tensor is configuration-dependent and the gyroscopic term is nonlinear. **Same equations as [[robotics/08-dynamics|robot dynamics]]**, different application.

**The integrator matters:**

## Integrators: which to use
<!-- bite: 2dc5f2d4-e0d3-4ec0-89b0-552fada1c2c0 -->

**Explicit Euler** — **gains energy and explodes.** Never use it for physics.

**Semi-implicit (symplectic) Euler** — update velocity *first*, then position using the *new* velocity. **One line different, and it's stable** with bounded energy.

**Velocity Verlet** — second-order, symplectic, time-reversible. **The standard for anything needing long-term energy conservation.**

> **This is the same argument as [[mathematics/07-applied-and-computational/01-numerical-methods/08-ordinary-differential-equations|note 08]]:** for physics you want **long-term qualitative correctness** — the simulation shouldn't gain energy and fly apart — **rather than per-step accuracy.** RK4 is more accurate per step and drifts in energy; symplectic integrators don't.
>
> **A fixed timestep is essential.** Variable timesteps break the symplectic property and make simulations non-deterministic. **Use a fixed physics step with an accumulator**, interpolating for rendering — the standard "fix your timestep" pattern.

## Collision detection
<!-- bite: c816b18f-3b47-495b-a731-62d1d4ee9cfb -->

**Two phases, because $O(n^2)$ pair tests don't scale.**

**Broad phase** — cheap rejection. **Sweep and prune** (sort by axis, check overlapping intervals), **spatial hashing**, or a **dynamic BVH.** Reduces the candidate set enormously.

**Narrow phase** — exact tests on survivors. **GJK** for convex shapes (works in configuration space on the Minkowski difference — elegant, and it handles any convex shape via a support function), **EPA** for penetration depth, **SAT** for boxes and polyhedra.

**Continuous collision detection** — the tunnelling problem: **a fast bullet moves entirely through a thin wall between two frames.** Discrete tests see no overlap at either instant. **Fixed by conservative advancement or swept-volume tests**, and it's why "bullets go through walls" is a classic game bug.

**Convex decomposition** — concave meshes are decomposed into convex pieces (V-HACD), because narrow-phase algorithms need convexity. **Or you use a triangle-mesh collider for static geometry only.**

## Constraint solving
<!-- bite: db6708c7-89c5-40fd-8723-8d69a2062e33 -->

**Contacts and joints are constraints**, and solving them is the heart of a physics engine.

**Impulse-based sequential solving (PGS)** — iterate over constraints, applying corrective impulses, repeatedly.

> **It doesn't fully converge**, which is why stacked boxes jitter and why a heavy object resting on a light one sinks slightly. **More iterations means more stability and more cost** — the `solverIterations` knob every engine exposes.

**Position-based dynamics (PBD)** — work directly on positions, project constraints, derive velocity afterwards. **Unconditionally stable, fast, not physically exact.** **XPBD** adds proper compliance so stiffness is a real material parameter rather than an iteration artefact. **The basis of most modern cloth and soft-body solvers.**

**Featherstone's articulated body algorithm** — $O(n)$ for a kinematic chain, and **used in robotics simulators** because it handles high joint stiffness ratios that impulse solvers struggle with. → [[robotics/08-dynamics|Dynamics]]

## Deformable simulation
<!-- bite: b8a4302c-d791-46ae-b5b9-09b70ebdead9 -->

**Cloth** — a mass-spring system (structural, shear and bend springs) or a proper continuum FEM model. **Position-based dynamics dominates in games**, FEM in film.

**Soft bodies** — FEM with a hyperelastic material model, or shape matching. **This is [[continuum-mechanics/10-finite-deformation|finite deformation]] applied at interactive rates.**

**Fluids** — **SPH** (particles, Lagrangian) or **grid-based** (Eulerian, solving Navier–Stokes). **FLIP/PIC hybrids** are the film standard. → [[continuum-mechanics/11-viscous-fluids-and-navier-stokes|Navier–Stokes]]

**Hair and fur** — strands as constrained particle chains, with the difficulty being self-collision at enormous count.

> **The distinction worth naming: film simulation optimises for accuracy and can take hours per frame; game simulation optimises for stability at 60 Hz and will happily be wrong.** **A game physics engine that is slightly wrong but never explodes is strictly better than an accurate one that occasionally does** — which is why PBD, an unphysical method, dominates real-time.

## Particles
<!-- bite: ef28ed7e-19d6-4dc0-8419-e6aac222ee70 -->

**Many simple entities, updated independently.**

**Perfect for GPU compute** — the canonical data-parallel workload. Update positions in a compute shader, render with instancing, **never touching the CPU.** → [[gpu-and-parallel-computing/04-parallel-patterns|Parallel Patterns]]

**Sorting for correct alpha blending** is the usual bottleneck — a GPU radix sort per frame, or accept the artefacts.

**Uses:** smoke, fire, sparks, rain, debris, magic effects, crowds.

## Simulation for robotics and ML
<!-- bite: 24172a1b-7105-454a-9a9f-bee9759b43a2 -->

**The connection that makes this note relevant beyond games.**

**Physics simulators for robotics** — MuJoCo, Isaac Sim, Gazebo, PyBullet, Drake. **They use the same collision detection and constraint solving**, tuned for accuracy and for contact-rich manipulation rather than for spectacle.

**Differentiable simulation** — make the whole simulation differentiable so you can optimise through it. **Gradient-based control and system identification** rather than sampling.

**The sim-to-real gap** is the practical difficulty: **contact, friction and actuator dynamics are the parts simulators model worst**, and they're exactly what matters for manipulation. **Domain randomisation** — randomise masses, friction, delays and textures during training so the policy learns to be robust — is the standard mitigation. → [[robotics/index|Robotics]]

**Rendering for training data** — synthetic datasets with perfect ground-truth labels (depth, segmentation, pose), which is far cheaper than annotating real images.

## Practical notes
<!-- bite: 2df2d1ad-88f7-4535-abdc-8854983ae8c5 -->

**Fix your timestep.** Accumulate real time, step physics at a fixed rate, interpolate the rendered pose. **Variable-step physics is non-deterministic and unstable**, and this is the single most important practical rule here.

**Use semi-implicit Euler or Verlet.** Never explicit Euler.

**Use a physics engine.** Bullet, PhysX, Jolt, Box2D, Rapier. **Constraint solving and robust collision detection are years of work**, and the failure modes are subtle.

**Tune solver iterations** against stability, and reduce the mass ratios in your scene — **a 1000:1 mass ratio will jitter in any impulse-based solver.**

## More practical notes on animation
<!-- bite: 9c2f563c-7c29-4898-80c2-253accc4986a -->

**Enable CCD only for fast small objects.** It's expensive and unnecessary for most bodies.

**Normalise quaternions every step.** Numerical drift accumulates. → [[mathematics/07-applied-and-computational/01-numerical-methods/02-floating-point-and-error|Error accumulation]]

**Check the sign before SLERP.**

**Sleep resting bodies.** Objects that haven't moved get deactivated — **a large performance win in any scene with settled debris.**

---

## Related
<!-- bite: 2a072d74-df88-4f06-852d-bef1f552c8cc -->
- [[robotics/08-dynamics|Robot Dynamics]] — the same equations, more rigour
- [[mathematics/07-applied-and-computational/01-numerical-methods/08-ordinary-differential-equations|ODEs]] — integrators and why symplectic matters
- [[computer-graphics/16-geometry-and-meshes|Geometry and Meshes]] — what gets deformed
- [[computer-graphics/index|Computer graphics map]]

## About this lesson
<!-- bite: 0f29dd82-a1ca-401d-8bda-05e243b4f223 -->

**Level:** Intermediate → Advanced. **Covers:** Making things move. Skinning, physics engines, and why game physics and robotics simulation are the same subject.
