# Inverse Kinematics

**[Intermediate → Advanced]** — Given where you want the hand, what joint angles get it there? The hard direction, and the one that actually matters.

## Why it's hard

$$\text{desired tool pose } T_{goal} \quad\longrightarrow\quad \boldsymbol\theta = ?$$

Forward kinematics is a chain of matrix multiplies. Inverse kinematics means **solving a system of nonlinear trigonometric equations**, and the difficulties are structural:

**There may be no solution.** The target is outside the workspace, or unreachable in that orientation.

**There may be many.** A 6-DOF industrial arm typically has **up to 8 solutions** for a reachable pose — shoulder left/right, elbow up/down, wrist flipped. All of them put the tool in exactly the same place.

```
   elbow up            elbow down
       ╱●                    ●
     ╱                        ╲
   ●───●  same tool pose   ●───●
```

**There may be infinitely many.** A 7-DOF arm has a continuous **null space** — a whole family of configurations reaching the same pose, which you can slide along while the tool stays put.

**Near singularities it misbehaves.** Small tool motions demand enormous joint motions. → [[robotics/07-jacobians-and-singularities|Jacobians and Singularities]]

> **So IK is not "the inverse function". It's a search with choices**, and picking *which* solution is as much of the problem as finding one.

## Analytical IK

Closed-form, exact, fast — solve the equations by hand for a specific geometry.

**The planar two-link arm** is the one to work through, because it shows the whole character of the problem:

$$\cos\theta_2 = \frac{x^2 + y^2 - l_1^2 - l_2^2}{2l_1l_2}$$

$$\theta_2 = \pm\arccos(\cdots) \qquad \theta_1 = \text{atan2}(y,x) - \text{atan2}\big(l_2\sin\theta_2,\ l_1 + l_2\cos\theta_2\big)$$

**Three things to read off it:**

**The $\pm$ is the elbow-up/elbow-down choice** — two solutions, and the maths hands you both.

**If $|\cos\theta_2| > 1$, the point is unreachable.** The arithmetic tells you directly, which is a nice property of analytical solutions.

**Use `atan2`, never `atan`.** `atan2(y,x)` knows which quadrant you're in; `atan(y/x)` doesn't and will silently put your arm 180° out. This is a real, recurring bug.

**For 6-DOF arms with a spherical wrist**, the [[robotics/05-forward-kinematics-and-dh-parameters|decoupling]] makes it tractable: solve joints 1–3 for the wrist centre position, then extract $R_{wrist}$ and solve joints 4–6 for orientation. **Pieper's criterion** is the general statement — three consecutive axes intersecting (or three parallel) guarantees a closed-form solution exists.

| | |
|---|---|
| **Good** | microseconds, exact, **finds all solutions**, no initial guess, deterministic |
| **Bad** | must be derived per robot, only exists for favourable geometries, painful to derive, brittle to design changes |

**Use it when you have it.** For a standard industrial arm, the closed form exists and the vendor ships it.

## Numerical IK

Iterate towards the answer. **Works for any geometry**, which is why it's the general answer.

### Jacobian-based

The workhorse. Uses the [[robotics/07-jacobians-and-singularities|Jacobian]] $J$, which relates joint velocities to tool velocities:

```
θ ← initial guess
repeat:
    e = pose_error(FK(θ), T_goal)     # 6-vector: position + orientation
    Δθ = J⁺(θ) · e                     # pseudoinverse times error
    θ ← θ + α·Δθ
until |e| < tolerance
```

**It's Newton's method on the kinematics**, and the variants differ in how they compute that step:

**Jacobian transpose** — $\Delta\theta = \alpha J^T e$. No inversion at all, cheap, provably converges (it's gradient descent), but **slowly**.

**Pseudoinverse** — $\Delta\theta = J^+e$. Fast convergence, and **it blows up near singularities** where $J$ loses rank.

**Damped least squares (Levenberg–Marquardt)** — the practical default:

$$\Delta\theta = J^T\left(JJ^T + \lambda^2 I\right)^{-1}e$$

**The $\lambda^2 I$ is what makes it usable.** Near a singularity the inverse stays bounded — you trade a little accuracy for not commanding infinite joint velocity. **This is the single most important practical detail in numerical IK**, and it's why naive pseudoinverse implementations produce arms that thrash.

**Selectively damped least squares** varies $\lambda$ per singular direction, damping only where needed — better accuracy away from the singularity.

### Optimisation-based

Pose it as a constrained optimisation:

$$\min_{\boldsymbol\theta}\ \|FK(\boldsymbol\theta) - T_{goal}\|^2 + w\,C(\boldsymbol\theta) \quad\text{s.t.}\quad \theta_{min} \leq \boldsymbol\theta \leq \theta_{max}$$

**Slower, and far more flexible** — you can add joint limits as hard constraints, penalise proximity to obstacles, prefer staying near a comfortable posture, or minimise joint motion from the current configuration.

**TRAC-IK** is the well-known practical solver: it runs a damped-least-squares solver and a nonlinear optimiser (SQP) **in parallel** and takes whichever returns first. It notably outperforms the older KDL solver mainly by handling joint limits properly and restarting from random seeds on failure — a good illustration that the engineering around the algorithm matters as much as the algorithm.

### Cyclic Coordinate Descent

Adjust one joint at a time, from the tip backwards, each to minimise the error. Repeat.

**Trivially simple, no Jacobian, no matrix maths.** Converges reliably if slowly, and it handles long chains well — which is why it's popular in **games and animation** for character IK. Less common in robotics because the joint motions it produces aren't smooth or natural.

## Choosing among solutions

Often the real work, and the part that determines whether the robot is usable.

**Closest to current configuration** — minimise $\|\theta - \theta_{current}\|$. **The sensible default**: it keeps motion continuous and avoids the arm suddenly reconfiguring mid-task.

**Away from joint limits** — maximise clearance, so you don't paint yourself into a corner.

**Away from singularities** — maximise manipulability. → [[robotics/07-jacobians-and-singularities|Jacobians and Singularities]]

**Collision-free** — check each candidate against the environment.

**Consistent configuration** — stay in "elbow up" for a whole task. **Switching branches mid-trajectory means a large, fast, and usually alarming reconfiguration motion**, even though both endpoints are correct.

> **This is the failure that surprises people:** the robot executes a smooth path, then at one waypoint flips its elbow through a wide arc to reach a pose that's millimetres from the previous one. The IK was right every time; the *sequence* wasn't. **Solve IK for a trajectory as a sequence with continuity constraints**, not as independent points.

## Redundancy

For $n > 6$ joints, the solution set is a continuous manifold, and you can exploit it.

**Null-space projection** — move within the null space without affecting the tool:

$$\dot{\boldsymbol\theta} = J^+\dot{\mathbf{x}} + \left(I - J^+J\right)\dot{\boldsymbol\theta}_0$$

The first term achieves the task. **The second does whatever you like, projected onto the directions that don't disturb the tool.** Use it to avoid joint limits, dodge obstacles with the elbow, keep away from singularities, or minimise energy.

**This is the concrete payoff of a 7-DOF arm**, and it's why collaborative robots have that extra joint: the elbow can move out of a human's way while the gripper holds still.

## Practical notes

**Seed it well.** Numerical IK from the current configuration converges fast and lands on a nearby solution. From a random seed it converges slowly to somewhere arbitrary. **Always seed from the current joint angles** in a control loop.

**Set a tolerance and an iteration cap.** Sub-micron IK tolerance is meaningless on a robot with 0.1 mm repeatability, and it wastes iterations.

**Position and orientation have different units.** A 6-vector error mixing metres and radians needs weighting, or the solver will trade a metre of position for a radian of orientation. **Weight them explicitly.**

**Handle failure explicitly.** IK fails — unreachable, singular, or out of iterations. **Returning garbage joint angles on failure is dangerous**; return a status and let the caller decide.

**Check joint limits after solving**, if the solver doesn't enforce them. An analytical solution will happily return an angle the robot can't reach.

**Verify with forward kinematics.** Run FK on the solution and confirm it produces the pose you asked for. It's cheap, and it catches sign and convention errors immediately.

---

## Related
- [[robotics/05-forward-kinematics-and-dh-parameters|Forward Kinematics]] — the easy direction
- [[robotics/07-jacobians-and-singularities|Jacobians and Singularities]] — the maths this depends on
- [[robotics/10-motion-planning|Motion Planning]] — where IK gets called in a loop
- [[robotics/README|Robotics map]]
