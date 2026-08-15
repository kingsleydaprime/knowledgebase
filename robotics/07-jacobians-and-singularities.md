# Jacobians and Singularities

**[Advanced]** — The derivative of the kinematics. Velocities, forces, and the configurations where a robot loses the ability to move in some direction.

## The Jacobian

Forward kinematics maps joint angles to tool pose. **The Jacobian is its derivative** — it maps joint *velocities* to tool *velocity*:

$$\dot{\mathbf{x}} = J(\boldsymbol\theta)\,\dot{\boldsymbol\theta}$$

where $\dot{\mathbf{x}} = [v_x, v_y, v_z, \omega_x, \omega_y, \omega_z]^T$ is the **twist** — linear and angular velocity stacked.

$$J = \begin{bmatrix} J_v \\ J_\omega \end{bmatrix} \in \mathbb{R}^{6 \times n}$$

**Six rows** (the DOF of a rigid body), **$n$ columns** (one per joint). **Column $i$ is the tool twist produced by moving joint $i$ alone at unit rate** — which is a genuinely useful way to read it, and makes the matrix concrete rather than abstract.

**It depends on configuration.** $J$ is not a constant; it changes as the robot moves, which is why singularities are a property of *where the arm is*, not of the arm.

## Computing it

**Geometrically**, per column, which is the way worth understanding:

**Revolute joint $i$**, with axis $\hat{z}_i$ and origin $\mathbf{p}_i$ (both in the base frame):

$$J_{v,i} = \hat{z}_i \times (\mathbf{p}_{tool} - \mathbf{p}_i) \qquad J_{\omega,i} = \hat{z}_i$$

The cross product is just $v = \omega \times r$ — rotating about an axis moves a distant point perpendicular to both the axis and the lever arm.

**Prismatic joint $i$:**

$$J_{v,i} = \hat{z}_i \qquad J_{\omega,i} = \mathbf{0}$$

Sliding translates and doesn't rotate.

**Everything you need comes from forward kinematics** — the axes and origins are the third column and fourth column of each accumulated transform. **So computing $J$ is nearly free once you've done FK**, which is why Jacobian-based IK is practical.

**Numerically**, by finite difference, is fine for prototyping and a good way to check your analytical version:

$$J_{:,i} \approx \frac{FK(\boldsymbol\theta + \epsilon\,\mathbf{e}_i) - FK(\boldsymbol\theta)}{\epsilon}$$

*(Careful with the orientation part — you can't subtract rotations, you have to compose the difference and convert to an axis-angle vector.)*

## What it's used for

Four things, and this is why the Jacobian is central rather than a curiosity.

**1. Velocity control (resolved-rate motion).** Given a desired tool velocity, find joint velocities:

$$\dot{\boldsymbol\theta} = J^{-1}\dot{\mathbf{x}} \quad\text{(or } J^+ \text{ for non-square)}$$

**This is how you jog a robot in Cartesian space** — the operator pushes a joystick "move right", and the Jacobian converts it into six joint rates.

**2. Inverse kinematics.** Iterate on the same relation. → [[robotics/06-inverse-kinematics|Inverse Kinematics]]

**3. Force and torque mapping.** The duality that surprises people:

$$\boxed{\boldsymbol\tau = J^T\mathbf{F}}$$

**Joint torques from a tool force, via the *transpose*.** No inverse required.

It falls out of virtual work — power is the same computed either way, $\mathbf{F}^T\dot{\mathbf{x}} = \boldsymbol\tau^T\dot{\boldsymbol\theta}$ — and it's the basis of **force control** and of estimating external forces from measured joint torques. A collaborative arm that detects a collision without a force sensor is using this.

**4. Singularity detection**, which is the rest of this note.

## Singularities

> **A singularity is a configuration where the Jacobian loses rank — the robot cannot move the tool in some direction, no matter what the joints do.**

Mathematically: $\text{rank}(J) < 6$, i.e. $\det(JJ^T) = 0$.

**Physically:** a direction of Cartesian motion becomes instantaneously impossible.

**The intuition** is the fully-extended arm. Reach your own arm straight out and try to move your hand further away. You can't — no combination of shoulder and elbow rotation produces motion along that direction. **You've lost a degree of freedom, at that configuration only.**

### The three kinds

**Boundary singularities** — at the edge of the workspace, arm fully extended or fully folded. **Easy to avoid**: don't plan to the limits of reach.

**Interior singularities** — inside the workspace, where joint axes align. **These are the dangerous ones**, because they're in the middle of otherwise-usable space and you can drive into one without warning.

**Wrist singularity** — on a spherical-wrist arm, when joints 4 and 6 become collinear (typically joint 5 at 0°). Then joints 4 and 6 do the *same thing*, and rotation about the lost axis is impossible.

**This one is notorious in practice.** A path that passes near it makes joints 4 and 6 spin at enormous rates in opposite directions — physically the tool moves slowly and correctly, while the wrist thrashes violently. It's a common cause of "the robot went crazy" on an otherwise valid path.

### Why they're dangerous

**Near** a singularity — not at it — the trouble starts:

$$\dot{\boldsymbol\theta} = J^{-1}\dot{\mathbf{x}}$$

As $J$ approaches rank deficiency, $J^{-1}$ blows up. **A modest tool velocity demands enormous joint velocities.**

```
 joint
 velocity
    │        ╱  ← demanded rate → ∞
    │       ╱
    │     ╱
    │___╱
    └──────────────→ distance from singularity
```

**Consequences:** velocity limits are exceeded and the controller either saturates (path error) or faults out; motion becomes violent; the numerics degrade; and the arm may reconfigure suddenly.

**A singularity is not a place you crash — it's a place your commands stop meaning what you think.**

## Measuring closeness

You need a scalar warning, not a binary test, since the trouble starts *before* you arrive.

**Manipulability** (Yoshikawa):

$$w = \sqrt{\det(JJ^T)} = \sigma_1\sigma_2\cdots\sigma_6$$

Zero at a singularity, larger when the robot moves freely. **A good general-purpose scalar to maximise** in a redundant arm's null space.

**Condition number:**

$$\kappa = \frac{\sigma_{max}}{\sigma_{min}}$$

Ratio of largest to smallest singular value. **1 is isotropic** (equally capable in every direction), $\infty$ at a singularity. Better than manipulability at revealing *near*-singular directions, since a single small $\sigma$ dominates it while barely moving the product.

**Minimum singular value $\sigma_{min}$** — the most directly meaningful. It's the worst-case gain from joint rates to tool velocity, and it has physical units.

### The manipulability ellipsoid

The picture worth having:

```
        ╱‾‾‾‾‾╲          well-conditioned:
       │   ●   │         moves easily in all directions
        ╲_____╱

    ───────●───────      near singular:
                         easy along one axis,
                         nearly impossible across it
```

Map the unit sphere of joint velocities through $J$ and you get an ellipsoid of achievable tool velocities. **Its axes are the singular vectors, its radii the singular values.** A long thin ellipsoid means the robot is fast in one direction and nearly stuck in another. Flat means singular.

**The force ellipsoid is the inverse** — where the robot moves easily it's weak, and where it can barely move it's strong. That's the same trade as gearing, and it explains why a nearly-extended arm can push hard along its length but not steer.

## Dealing with them

**Avoid, at planning time.** Add manipulability to the planner's cost function or IK's null-space objective. **The best fix is not being there.**

**Damped least squares**, when you must pass nearby:

$$\dot{\boldsymbol\theta} = J^T(JJ^T + \lambda^2I)^{-1}\dot{\mathbf{x}}$$

**Bounded joint rates, at the cost of tracking error.** The tool deviates slightly from the commanded direction instead of the arm thrashing — a good trade, and the standard one.

**Adaptive damping:** $\lambda = 0$ when well-conditioned, growing as $\sigma_{min}$ falls. Full accuracy where it's safe, protection where it isn't.

**Task-priority / null-space methods** on a redundant arm — reconfigure the elbow to improve conditioning while the tool holds its path. **This is the real reason 7-DOF arms exist.**

**Truncate small singular values.** Do the SVD, zero the components below a threshold, invert the rest. Explicitly gives up the unachievable direction rather than screaming about it.

**Design around it.** A 7-DOF arm has singularities of measure zero in configuration space — you can almost always reconfigure out. Six-DOF arms cannot.

## Practical notes

**Singularities are configuration-dependent, not workspace-dependent.** The same tool pose reached elbow-up may be fine and elbow-down may be singular. **So the branch you chose in IK determines whether you hit one.**

**Check manipulability along a planned path**, not just at the endpoints. The interesting failures are in the middle.

**Cartesian jogging near a wrist singularity is where operators get surprised.** Joint-space motion is unaffected — it's only the Cartesian command that becomes ill-posed. If the arm is thrashing, jog in joint space to get out.

**$J^T$ is always safe.** No inversion, no blow-up. That's why Jacobian-transpose IK converges slowly but never explodes, and why force control (which only needs $J^T$) is well-behaved at singularities where velocity control isn't.

**Watch your units again.** The top three rows of $J$ are in metres, the bottom three dimensionless per radian. **Singular values of a mixed-unit matrix are unit-dependent and therefore somewhat arbitrary** — scale the rows consistently (by a characteristic length) before drawing conclusions from a condition number.

---

## Related
- [[robotics/06-inverse-kinematics|Inverse Kinematics]] — the main consumer of this
- [[robotics/08-dynamics|Dynamics]] — where $J^T$ appears again
- [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/README|Linear Algebra]] — rank, SVD, singular values
- [[robotics/README|Robotics map]]
