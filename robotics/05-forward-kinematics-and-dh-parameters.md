# Forward Kinematics and DH Parameters

**[Intermediate]** — Given the joint angles, where is the hand? The easy direction, and the notation the field standardised on.

## The problem

$$\text{joint angles } \boldsymbol{\theta} = [\theta_1, \theta_2, \ldots, \theta_n] \quad\longrightarrow\quad \text{tool pose } ^{0}_{n}T$$

**This direction is always solvable, always unique, and has a closed form.** Multiply the link transforms together and you're done:

$$^{0}_{n}T(\boldsymbol\theta) = {^{0}_{1}T(\theta_1)}\ {^{1}_{2}T(\theta_2)}\cdots{^{n-1}_{n}T(\theta_n)}$$

**That's the whole idea.** Everything else in this note is bookkeeping to make the individual link transforms systematic.

Contrast with [[robotics/06-inverse-kinematics|inverse kinematics]], which may have no solution, one, several, or infinitely many. **Forward is easy; inverse is the subject.**

## A worked two-link arm

Before the general machinery, do it by hand — planar, two revolute joints, link lengths $l_1, l_2$:

```
              ╱● (x, y)
            ╱  l₂
      ●───╱  θ₂
     ╱  l₁
   ╱ θ₁
  ●───────────
```

$$x = l_1\cos\theta_1 + l_2\cos(\theta_1 + \theta_2)$$
$$y = l_1\sin\theta_1 + l_2\sin(\theta_1 + \theta_2)$$

**Note the $(\theta_1 + \theta_2)$.** Joint angles are measured *relative to the previous link*, so they accumulate down the chain. That's the essential structure of every serial manipulator, and it's why the transforms multiply.

**Do this one on paper.** The general method is this, formalised — and the formalism is much easier to trust once you've seen the concrete version.

## Denavit–Hartenberg parameters

The standard way to describe a serial chain. **Four numbers per joint instead of a general six-DOF transform**, achieved by constraining how you're allowed to place the frames.

| Parameter | Meaning | Varies for |
|---|---|---|
| $\theta_i$ | joint **angle** about $z_{i-1}$ | revolute joints |
| $d_i$ | link **offset** along $z_{i-1}$ | prismatic joints |
| $a_i$ | link **length** along $x_i$ | fixed |
| $\alpha_i$ | link **twist** about $x_i$ | fixed |

**The trick that makes four suffice:** the frames are placed so that $x_i$ is the common normal between $z_{i-1}$ and $z_i$. That constraint removes two of the six degrees of freedom, and what's left is exactly four.

**One parameter per joint varies** — $\theta$ for a revolute joint, $d$ for a prismatic one. The other three are fixed by the robot's geometry. So an $n$-joint arm is described by a $4n$ table, and that table *is* the robot as far as kinematics is concerned.

The link transform:

$$^{i-1}_{i}T = \begin{bmatrix}
\cos\theta_i & -\sin\theta_i\cos\alpha_i & \sin\theta_i\sin\alpha_i & a_i\cos\theta_i \\
\sin\theta_i & \cos\theta_i\cos\alpha_i & -\cos\theta_i\sin\alpha_i & a_i\sin\theta_i \\
0 & \sin\alpha_i & \cos\alpha_i & d_i \\
0 & 0 & 0 & 1
\end{bmatrix}$$

**Don't memorise it.** It's $\text{Rot}_z(\theta)\,\text{Trans}_z(d)\,\text{Trans}_x(a)\,\text{Rot}_x(\alpha)$ multiplied out — recognising that decomposition is more useful than recalling the entries.

### The honest assessment

**DH is the standard, it's what textbooks and papers use, and you need to be able to read it.** But:

- **Two incompatible conventions exist** — "standard" (Denavit–Hartenberg 1955) and "modified" (Craig). They differ in whether the frame sits at the near or far end of the link, and **they produce different tables for the same robot.** Mixing them silently gives a wrong model. Always state which you're using
- **Frame assignment is fiddly and error-prone**, especially with parallel or intersecting joint axes
- **It cannot represent branching** — a humanoid or a hand isn't a serial chain
- **It's degenerate when consecutive axes are parallel**, where the common normal isn't unique

**What modern practice actually uses:** URDF (in ROS) and similar formats specify each joint with an explicit parent frame, child frame, origin transform and axis. **More verbose, no conventions to get wrong, handles trees, and generated directly from CAD.** → [[robotics/13-ros-and-robot-software|ROS and Robot Software]]

> **Learn DH to read the literature. Use URDF to build the robot.**

## Common arm geometries

Recognising these tells you a lot before you compute anything:

**Articulated / anthropomorphic (6R)** — the classic industrial arm. Three joints position the wrist, three orient it. Large dexterous workspace. UR, KUKA, ABB, Fanuc.

**SCARA** — two parallel revolute joints, one prismatic, one rotation. **4 DOF, planar motion plus vertical.** Fast, stiff vertically, cheap. Dominant in electronics assembly, and the reason is that pick-and-place doesn't need 6 DOF.

**Cartesian / gantry** — three prismatic axes. **Kinematics is trivial** ($x, y, z$ *are* the joint values). 3D printers, CNC, large gantries. Stiff, accurate, big footprint for the workspace you get.

**Delta** — a parallel robot, three arms to a common platform. **Extremely fast** because the motors are all on the fixed base and the moving mass is tiny. Small workspace. Used for high-speed picking.

**Parallel arms invert the difficulty.** For a delta or a Stewart platform, **inverse kinematics is easy and forward kinematics is hard** — the opposite of a serial arm, and worth knowing so it doesn't surprise you.

## The spherical wrist

The design decision that makes 6-DOF arms tractable.

**If the last three joint axes intersect at a point**, then position and orientation **decouple**:

- The first three joints determine the **wrist centre position**
- The last three determine the **orientation** about it

$$\mathbf{p}_{wrist} = \mathbf{p}_{tool} - d_6\,R\,\hat{z}$$

**That's why 6-DOF industrial arms have closed-form inverse kinematics** and arbitrary 6-joint arms generally don't. You solve a 3-DOF position problem, then a 3-DOF orientation problem, instead of one coupled 6-DOF problem. → [[robotics/06-inverse-kinematics|Inverse Kinematics]]

**It's a mechanical design choice made specifically to make the maths solvable**, which is a nice example of hardware and software being co-designed. Some modern arms (notably some collaborative designs) give it up for other benefits, and pay in IK complexity.

## The tool frame

Forward kinematics gives you the **flange** — the mounting face at the end of the last link. **That's not what you care about.** You care about the gripper tip, the welding point, the camera.

$$^{0}_{tool}T = {^{0}_{flange}T}\ {^{flange}_{tool}T}$$

The **tool centre point (TCP)** offset is a fixed transform you supply.

> **Getting the TCP wrong is one of the commonest practical errors**, and it's insidious: the robot is perfectly accurate and consistently wrong by a fixed offset. Worse, a TCP error in *orientation* produces a position error that changes as the wrist rotates, which looks like a much more complicated fault than it is.

**Calibrate the TCP** rather than measuring it from CAD — the standard method is touching a single fixed point from four different orientations and solving for the offset that makes them agree.

## Where forward kinematics is used

More places than "where's the hand":

**Visualisation** — drawing the robot in RViz is forward kinematics at every joint.

**Collision checking** — a planner needs every link's pose, for every candidate configuration, thousands of times per second. **This is why FK performance matters** even though a single evaluation is cheap. → [[robotics/10-motion-planning|Motion Planning]]

**Inside inverse kinematics** — numerical IK solvers evaluate FK repeatedly to measure error and iterate.

**Sensor placement** — a lidar on link 3 is somewhere in the world determined by joints 1–3.

**Calibration** — comparing measured tool poses against FK-predicted ones is how you identify the true link lengths and joint offsets.

## Practical notes

**Get link lengths from CAD, then verify physically.** Manufacturing tolerance and assembly are real. **A 1 mm link error and a 0.1° joint offset both matter** at the end of a metre-long arm.

**Joint zero is a convention you must pin down.** Where is "zero" and which direction is positive? Nothing about the hardware tells you, and getting it wrong gives a mirrored robot.

**Watch joint limits.** FK will happily compute a pose that requires a joint at 400°. The maths doesn't know about hard stops.

**Cache along the chain.** Computing frames 1..n incrementally is much cheaper than recomputing each from the base — worth it inside a planner's inner loop.

**Test against the physical robot.** Command a known configuration, measure where the tool actually is. **A tape measure has settled more kinematics arguments than any simulation.**

---

## Related
- [[robotics/04-rigid-body-transforms|Rigid Body Transforms]] — the transforms being chained
- [[robotics/06-inverse-kinematics|Inverse Kinematics]] — the hard direction
- [[robotics/07-jacobians-and-singularities|Jacobians]] — differentiating this
- [[robotics/README|Robotics map]]
