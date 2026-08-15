# Robot Control

**[Intermediate → Advanced]** — Cascaded joint loops, trajectory following, and the control problems specific to machines with arms.

> **The theory is in [[engineering/02-control-theory/README|engineering/02-control-theory]].** PID, tuning, stability, state estimation, LQR — all of it lives there and applies unchanged. **This note is the robotics-specific part**: how those loops are arranged in a real robot, what a manipulator adds, and what goes wrong on hardware.

## The cascade

Essentially every robot joint is driven by three nested loops:

```
 trajectory
     │
     ▼
 ┌────────────────┐  θ_d      ┌──────────┐
 │ POSITION LOOP  │──────────→│          │   100–1000 Hz
 └────────────────┘  ω_d      │ VELOCITY │
         ▲                    │   LOOP   │   1–5 kHz
         │                    └──────────┘
         │                          │ i_d
         │                          ▼
         │                    ┌──────────┐
         │                    │ CURRENT  │   10–20 kHz
         │                    │   LOOP   │
         │                    └──────────┘
         │                          │ PWM
         │                          ▼
         └──── encoder ─────────  MOTOR
```

**Each loop is faster than the one outside it** — 5–10× is the standard guidance, and the reason is that the inner loop must settle before the outer loop notices it moved. → [[engineering/02-control-theory/04-pid-control|Cascade control]]

**Why this arrangement rather than one big loop:**

**The current loop linearises the actuator.** Motor torque is proportional to current, so a fast current loop turns "a motor" into "a torque source" as far as everything above it is concerned. All the electrical dynamics — inductance, back-EMF, bus voltage sag — get absorbed here.

**The velocity loop absorbs friction and load disturbance** before the position loop sees them.

**The position loop only has to deal with kinematics.** Which is a much easier problem than "kinematics and motor electrical dynamics and friction all at once".

**Tune inner-out, always.** Current loop first with the mechanics locked, then velocity, then position. **Tuning the position loop while the velocity loop is badly tuned is unproductive** — you're fighting a moving target, and the gains you find won't survive fixing the inner loop.

**Typical structure:** the current loop is PI (no D — the signal is noisy and the plant is essentially first-order). The velocity loop is PI. The position loop is often **P only**, because the plant already contains an integrator (velocity integrates to position) so it's type 1 and has no steady-state error. Adding I to a position loop is a common mistake that mostly buys you windup. → [[engineering/02-control-theory/03-time-response|System type]]

## Joint space vs Cartesian space

**Two places to close the loop**, and the choice matters:

**Joint-space control** — convert the goal to joint angles once, then run independent per-joint loops.

*Simple, decoupled, no Jacobian in the loop, and it behaves predictably near singularities.* The tool path between waypoints is **not a straight line** — it's whatever curve the joint interpolation produces, which can be surprising and can collide with things.

**Cartesian control** — close the loop on tool pose, converting to joint commands each cycle via the [[robotics/07-jacobians-and-singularities|Jacobian]] or IK.

*The tool follows the path you specified.* Costs a Jacobian or IK solve every cycle, and **degrades badly near singularities** where the mapping blows up.

> **The practical default: plan in Cartesian space, execute in joint space.** Convert the path to joint waypoints ahead of time, check them, then run fast reliable joint loops. You get the path you wanted and the robustness of joint control. Cartesian *servoing* is reserved for cases where the target moves — visual servoing, force control, teleoperation.

## Trajectory generation

A setpoint step is not a trajectory. **Commanding a joint to jump from 0° to 90° asks for infinite velocity**, the controller saturates, and the resulting motion is uncontrolled — the arm does whatever the saturated actuator does, not what you designed.

**So you generate a smooth time-parameterised path** and feed it as a moving setpoint.

**Trapezoidal velocity profile** — accelerate at a limit, cruise, decelerate. The standard, and it respects velocity and acceleration limits by construction.

```
 v │    ┌────────┐
   │   ╱          ╲
   │  ╱            ╲
   └─────────────────── t
     accel  cruise  decel
```

*Discontinuous acceleration at the corners* — infinite jerk, which excites structural resonances and sounds like a clunk.

**S-curve** — smooth the acceleration too, bounding jerk. **Noticeably gentler on the mechanism and quieter**, at the cost of slightly longer moves. Worth it on anything with compliance.

**Polynomial (quintic)** — a fifth-order polynomial matching position, velocity and acceleration at both ends. Smooth, easy, and it **doesn't respect limits** unless you check afterwards.

**Splines** through waypoints — for multi-point paths, with continuity at the joins.

**Two things that matter in practice:**

**Feedforward the trajectory's own velocity and acceleration**, don't just give the controller a position setpoint:

$$\tau = \underbrace{K_p e + K_d\dot{e}}_{\text{feedback}} + \underbrace{M\ddot{\theta}_d + g(\theta)}_{\text{feedforward}}$$

**Feedback alone must lag** — it needs an error before it acts, so a purely feedback controller tracks a moving target with a persistent error proportional to speed. **Feedforward removes most of that error before it happens**, and feedback handles what the model got wrong. → [[engineering/02-control-theory/01-what-control-theory-is|Feedforward]]

**Time-scale the whole trajectory** rather than clipping individual joints. If one joint would exceed its limit, slow the entire motion — clipping one joint desynchronises it from the others and the tool leaves the intended path.

## What a manipulator adds

The problems you don't have with a single motor:

**Configuration-dependent inertia.** A gain set that's well-tuned with the arm folded is under-damped with it extended, by a large factor. Options: detune for the worst case (safe, slow), gain-schedule on configuration, or cancel it with [[robotics/08-dynamics|computed torque]].

**Gravity.** A joint holding a load against gravity needs continuous torque. With P-only control that means a steady-state error; with I it means windup on the way there. **Gravity feedforward is the right answer** and it's cheap. → [[robotics/08-dynamics|Dynamics]]

**Coupling.** Accelerating joint 2 exerts torque on joints 1 and 3. Each joint's controller sees this as an unexplained disturbance, and it grows with speed.

**Joint flexibility.** Harmonic drives, belts and long links are springy, so motor position ≠ joint position. **This creates a resonance that caps your achievable bandwidth**, and it's usually the real limit on how fast an arm can be tuned. Push the gains past it and the arm rings. → [[engineering/02-control-theory/06-frequency-response|Resonance]]

**Backlash.** Free play in the gearbox. A hard nonlinearity that no tuning removes, and it causes limit cycling around a setpoint. → [[engineering/02-control-theory/13-nonlinear-and-modern-control|Nonlinear Control]]

## Compliance and interaction

**A stiff position controller is dangerous and inflexible.** Command a position inside a table and the controller applies whatever torque it takes to get there.

**Impedance control** makes the arm behave like a virtual spring-damper — specify how it should *react* to contact rather than where it must be. → [[robotics/08-dynamics|Dynamics]]

**Why it matters in practice:**

- **Assembly.** Insertion tasks need compliance; you cannot position accurately enough to fit a peg in a hole by geometry alone. A compliant arm lets the contact forces guide it in
- **Human safety.** A compliant arm that hits a person pushes; a stiff one crushes. This is the basis of collaborative robots → [[robotics/14-safety-and-real-time|Safety]]
- **Surface work.** Polishing, sanding, deburring — force normal to the surface, position along it
- **Teaching.** Gravity-compensated and compliant, the arm can be hand-guided through a trajectory

**It needs backdrivable joints or good torque sensing.** A high-ratio worm-geared joint cannot be compliant no matter what the software wants — the mechanics won't let the load back-drive the motor.

## Mobile robot control

Different problems, same theory.

**Differential drive** — two independently driven wheels:

$$v = \frac{r(\omega_R + \omega_L)}{2}, \qquad \omega = \frac{r(\omega_R - \omega_L)}{L}$$

**Nonholonomic:** you can't move sideways. The robot has 3 DOF in the plane and 2 controls, so some motions require a manoeuvre rather than a translation. → [[robotics/10-motion-planning|Motion Planning]]

**Path following** — the standard approaches:

**Pure pursuit** — aim at a point a fixed **lookahead distance** ahead on the path, steer towards it. Simple, robust, widely used. **The lookahead is the tuning knob and it's a real trade**: too short and it oscillates, too long and it cuts corners.

**Stanley controller** — used on the DARPA Grand Challenge winner. Combines cross-track error and heading error, measured at the front axle. Better tracking than pure pursuit, more sensitive to noise.

**MPC** — predicts ahead and respects constraints. Increasingly standard in autonomous driving, and the right answer when you have limits that bind. → [[engineering/02-control-theory/11-optimal-control-and-lqr|MPC]]

**Balancing robots** (Segway, two-wheeled) are **unstable open loop** and need fast attitude feedback just to stay upright — the classic inverted pendulum. → [[engineering/02-control-theory/01-what-control-theory-is|Stabilising unstable plants]]

**Quadcopters** use a cascade too: position → velocity → attitude → rate → motor. **Attitude is the fast inner loop** (typically 500 Hz–1 kHz) because that's what keeps it in the air; position is a slow outer loop. Same structure as a robot joint, different physics.

## Visual servoing

Closing the loop on camera images directly.

**Position-based (PBVS)** — estimate the target's 3D pose from the image, control in Cartesian space. Intuitive, and **sensitive to calibration error**, since a bad camera model gives a confidently wrong 3D position.

**Image-based (IBVS)** — define the error in *image* coordinates (pixels) and control directly on it, using an image Jacobian. **Robust to calibration error** — you're driving a pixel error to zero, and being slightly wrong about the camera model just changes the path, not the destination. The 3D trajectory can be strange, and it can fail if features leave the frame.

**The practical difficulty is latency.** 50–100 ms from photon to control action is normal, and that phase lag limits your gain hard. Predict forward, or run a fast inner loop with slow visual correction — the same structure as everything else in this note. → [[engineering/02-control-theory/03-time-response|Time delay]]

## What actually goes wrong

Roughly in the order you'll meet it:

**Sample rate too low.** Simulates beautifully, oscillates on hardware. The zero-order hold costs $T/2$ of delay. → [[engineering/02-control-theory/12-digital-control|Digital Control]]

**Timing jitter.** A control loop in a `while` loop with a `sleep` has varying $dt$, and therefore varying effective gains. **Use a timer interrupt or a real-time thread.**

**Derivative on a quantised encoder.** Differencing a staircase gives spikes. Filter it, or estimate velocity with an observer. → [[engineering/02-control-theory/10-observers-and-kalman|Observers]]

**Integral windup** on a saturated joint — and joints saturate constantly, whenever they hit something or lift a heavy payload. → [[engineering/02-control-theory/04-pid-control|Anti-windup]]

**Angle wrapping.** Error between 179° and −179° is 2°, not 358°. Without wrapping, the joint takes the long way round at full speed. **This one is dramatic when it happens.** → [[robotics/04-rigid-body-transforms|Transforms]]

**Gains tuned in one configuration.** Works folded, unstable extended.

**No feedforward.** Tracking error that grows with speed and looks like a tuning problem but isn't.

---

## Related
- [[engineering/02-control-theory/README|Control Theory]] — the theory this applies
- [[robotics/08-dynamics|Dynamics]] — the model behind feedforward and computed torque
- [[robotics/10-motion-planning|Motion Planning]] — what generates the trajectories
- [[robotics/14-safety-and-real-time|Safety and Real-Time]] — the timing guarantees this depends on
- [[robotics/README|Robotics map]]
