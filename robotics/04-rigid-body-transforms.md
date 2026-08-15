# Rigid Body Transforms

**[Intermediate]** — Rotations, homogeneous transforms, and the frame bookkeeping that causes more robotics bugs than any algorithm.

## Why this comes first

Everything downstream is transforms. Forward kinematics is a chain of them. Inverse kinematics inverts one. SLAM estimates them. The camera sees in its frame and the gripper acts in another.

> **Get the frame conventions right once and most of the maths follows. Get them wrong and the robot moves smoothly, confidently, in the wrong direction** — which is the hardest kind of bug, because nothing crashes.

## Frames

A **frame** is a coordinate system attached to something: the world, the robot base, each link, the tool, the camera, the map.

The notation that saves you, and it's worth adopting rigidly:

$$^{A}\mathbf{p} \quad\text{— a point expressed in frame } A$$
$$^{A}_{B}T \quad\text{— the transform that takes a point in frame } B \text{ and expresses it in frame } A$$

**And then the subscripts cancel like units:**

$$^{A}\mathbf{p} = {^{A}_{B}T}\ {^{B}\mathbf{p}}$$

$$^{A}_{C}T = {^{A}_{B}T}\ {^{B}_{C}T}$$

**Adjacent indices must match.** If they don't, you've composed backwards. This one convention catches most transform errors before you run anything, and it's the reason to write the sub/superscripts even when it feels fussy.

**Read $^{A}_{B}T$ two ways** — both are correct and the ambiguity is a real source of confusion:
- It **converts** coordinates from $B$ into $A$
- It **describes the pose of frame $B$** as seen from $A$

## Rotations

### Rotation matrices

A 3×3 matrix $R$ whose columns are the axes of the rotated frame expressed in the original:

$$R = \begin{bmatrix} | & | & | \\ \hat{x}' & \hat{y}' & \hat{z}' \\ | & | & | \end{bmatrix}$$

It's a member of $SO(3)$ — orthonormal with determinant $+1$:

$$R^TR = I \qquad \det R = 1 \qquad \boxed{R^{-1} = R^T}$$

**That last identity is the useful one.** Inverting a rotation is a transpose — free, and numerically exact. No matrix inversion anywhere in your kinematics.

The elementary rotations:

$$R_z(\theta) = \begin{bmatrix} \cos\theta & -\sin\theta & 0 \\ \sin\theta & \cos\theta & 0 \\ 0 & 0 & 1\end{bmatrix}$$

with $R_x$ and $R_y$ analogous.

**Nine numbers for three degrees of freedom** — heavily redundant, which is both a weakness (storage, and numerical drift off the manifold) and a strength (no singularities, and composition is a plain matrix multiply).

> **Renormalise periodically.** Multiply enough rotation matrices in floating point and $R^TR$ drifts away from $I$. Re-orthogonalise (Gram–Schmidt or SVD) in anything long-running.

### Euler angles

Three sequential rotations — roll, pitch, yaw. **Intuitive, compact, and the source of a genuine trap.**

**The order matters, and there are 12 valid conventions.** ZYX (yaw-pitch-roll) is standard in aerospace and robotics, but "roll pitch yaw" alone doesn't specify it. **Rotations do not commute** — rotate 90° about $x$ then $y$ and you get somewhere different than $y$ then $x$. Try it with a book.

**And then gimbal lock:**

> At pitch = ±90°, the first and third axes align. **You lose a degree of freedom** — two of your three parameters now do the same thing, and the representation is singular. Nearby, the angles change violently for small motions.

That's not a bug in a particular convention. **Every three-parameter representation of 3D rotation has a singularity somewhere** — it's a topological fact, and it's the reason Apollo 11's IMU had a physical gimbal-lock warning.

**Use Euler angles for display and human input. Do not use them in your state representation.**

### Quaternions

Four numbers, $q = w + xi + yj + zk$, unit norm.

$$q = \left(\cos\frac{\theta}{2},\ \hat{n}\sin\frac{\theta}{2}\right)$$

for a rotation of $\theta$ about axis $\hat{n}$.

**Why they win:**

- **No singularities.** No gimbal lock, anywhere
- **Compact** — 4 numbers, and renormalising is one division
- **Composition is cheap** — quaternion multiplication, fewer operations than a matrix multiply
- **Interpolation works** — SLERP gives constant-rate rotation along the shortest path. Interpolating Euler angles gives visible wobble, and interpolating rotation matrices element-wise gives something that isn't a rotation at all

**What bites:**

- **Not intuitive.** You cannot read a quaternion and picture the orientation
- **Double cover:** $q$ and $-q$ are the *same rotation*. Handle it explicitly, especially when comparing orientations or computing an error — the shortest path may require flipping the sign
- **Convention split:** $(w,x,y,z)$ vs $(x,y,z,w)$. Eigen uses one, ROS uses the other. **Check, every time** — this is a real and common bug
- **Renormalise** after accumulating

**The practical rule for the whole section:**

| Use | For |
|---|---|
| **Quaternions** | storing and propagating orientation |
| **Rotation matrices** | transforming vectors, composing chains |
| **Euler angles** | display, config files, human input |
| **Axis-angle** | rotation *errors* and control (it's a natural "how far off am I") |

## Homogeneous transforms

Rotation and translation in one 4×4 matrix:

$$T = \begin{bmatrix} R & \mathbf{t} \\ \mathbf{0}^T & 1 \end{bmatrix} = \begin{bmatrix} r_{11} & r_{12} & r_{13} & t_x \\ r_{21} & r_{22} & r_{23} & t_y \\ r_{31} & r_{32} & r_{33} & t_z \\ 0 & 0 & 0 & 1 \end{bmatrix}$$

Points get a 1 appended: $\tilde{\mathbf{p}} = [x, y, z, 1]^T$.

**The point of the fourth row** is that it makes rotation-then-translation a single matrix multiply, so **composing a chain of joints is just multiplying matrices**. Without it you'd carry $R$ and $t$ separately and write out $R_2(R_1p + t_1) + t_2$ by hand at every link.

**The inverse has a closed form** — never call a general 4×4 inverse:

$$T^{-1} = \begin{bmatrix} R^T & -R^T\mathbf{t} \\ \mathbf{0}^T & 1\end{bmatrix}$$

**Note the $-R^T\mathbf{t}$.** Negating the translation alone is wrong, and it's a classic error. The intuition: to undo "rotate then translate", you undo the translation *in the rotated frame*.

**Vectors vs points.** A point has $w=1$ and is affected by translation. A **direction** has $w=0$ and is not — which is correct, because rotating a velocity or a surface normal should not move it. The homogeneous form handles this automatically, which is a large part of why it's used.

## Transform trees

A real robot has many frames, and they form a tree:

```
        world
          │
         map
          │
         odom
          │
      base_link
       ╱   │   ╲
  link1  laser  camera
    │
  link2
    │
   tool0
```

**Every edge is a transform.** Some are fixed (camera bolted to the base), some change every cycle (joint angles), some are estimated (map → odom, from SLAM).

**The transform between any two frames is the product along the path**, inverting where you travel against an edge. Finding `camera → tool0` means going up to `base_link` and back down.

**This is exactly what ROS's `tf2` does**, and it does one more important thing: **it buffers transforms with timestamps**, so you can ask "where was the camera relative to the gripper *at the moment that image was captured*". Because sensors have latency and the robot moved in the meantime, using the current transform for an old measurement is wrong — and this is a subtle, real, and very common source of error. → [[robotics/13-ros-and-robot-software|ROS and Robot Software]]

## Conventions to pin down

**Agree these on day one and write them in the README.** Every one of them has bitten someone.

**Axis convention.** ROS uses **x forward, y left, z up** (right-handed) for robot bodies, and **z forward, x right, y down** for optical camera frames. **Those are different, deliberately, and mixing them is a rite of passage.**

**Handedness.** Right-handed nearly everywhere in robotics; some graphics and CAD tools are left-handed.

**Units.** **Metres and radians**, always, internally. Convert at the boundary — display, config, user input. Degrees creeping into the maths is a recurring bug, and it's silent because the numbers look plausible.

**Angle wrapping.** Is your angle in $[0, 2\pi)$ or $(-\pi, \pi]$? **Angular error must wrap** — the error between 179° and −179° is 2°, not 358°. A controller that doesn't wrap will command a full rotation the wrong way around, dramatically. Use `atan2(sin(e), cos(e))` and stop thinking about it.

**Quaternion ordering.** $(w,x,y,z)$ or $(x,y,z,w)$. Stated above; stated again because it keeps happening.

## Debugging transforms

The practical checklist, since this is where the time goes:

**Visualise.** RViz, or draw the axes. **A frame in the wrong place is obvious visually and invisible numerically.** This alone is worth setting up early.

**Check the identity cases.** Zero joint angles should put the tool somewhere you can predict by looking at the robot.

**Check determinants and norms.** $\det R = 1$ and $\|q\| = 1$. A determinant of $-1$ means you've mirrored something — usually a flipped axis convention.

**Move one joint at a time** and confirm the tool frame moves the way it physically does. This finds sign errors immediately.

**Read the subscripts.** $^{A}_{B}T\ ^{C}\mathbf{p}$ is meaningless — $B \neq C$. Most composition bugs are visible in the notation before they're visible in the robot.

---

## Related
- [[robotics/05-forward-kinematics-and-dh-parameters|Forward Kinematics]] — chaining these into a robot
- [[robotics/07-jacobians-and-singularities|Jacobians]] — the derivative of this chain
- [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/README|Linear Algebra]] — matrices and orthogonality
- [[robotics/README|Robotics map]]
