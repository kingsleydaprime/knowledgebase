# Dynamics

**[Advanced]** — Forces and torques, not just geometry. What it actually takes to make a heavy arm move fast and accurately.

## Kinematics vs dynamics

**Kinematics is geometry** — where things are, ignoring why. Notes 04–07.

**Dynamics is physics** — what torques produce what motion, given mass, inertia and gravity.

**You can go a long way on kinematics alone.** Move slowly, let a stiff PID hold each joint, and the dynamics show up only as disturbances the controller rejects.

**Dynamics starts to matter when:**

- The robot moves **fast** — inertial forces scale with acceleration
- Links are **heavy** relative to the actuators
- You need **accuracy during motion**, not just at the endpoint
- You want **compliance** or force control
- The arm is **unstable** without it (legged robots, anything balancing)

> **The rough dividing line:** below roughly a third of the arm's maximum speed, a well-tuned joint controller handles the dynamics as disturbance. Above that, you need to model them, and the tracking error of a purely kinematic controller grows with the square of the speed.

## The equation of motion

Every serial manipulator obeys the same structure:

$$\boxed{M(\boldsymbol\theta)\ddot{\boldsymbol\theta} + C(\boldsymbol\theta, \dot{\boldsymbol\theta})\dot{\boldsymbol\theta} + \mathbf{g}(\boldsymbol\theta) + \mathbf{f}(\dot{\boldsymbol\theta}) = \boldsymbol\tau}$$

| Term | Name | What it is |
|---|---|---|
| $M(\boldsymbol\theta)\ddot{\boldsymbol\theta}$ | **inertia** | $F = ma$, generalised. **$M$ depends on configuration** |
| $C(\boldsymbol\theta,\dot{\boldsymbol\theta})\dot{\boldsymbol\theta}$ | **Coriolis and centrifugal** | velocity-dependent coupling between joints |
| $\mathbf{g}(\boldsymbol\theta)$ | **gravity** | usually the biggest term at low speed |
| $\mathbf{f}(\dot{\boldsymbol\theta})$ | **friction** | viscous + Coulomb; hard to model, always present |
| $\boldsymbol\tau$ | **joint torques** | what the motors provide |

**Three properties worth carrying:**

**$M$ is configuration-dependent.** An extended arm has far more inertia about the shoulder than a folded one — by a large factor. **So a fixed-gain joint controller is well-tuned in one configuration and badly tuned in another**, which is the practical reason gain scheduling appears in robotics. → [[engineering/02-control-theory/13-nonlinear-and-modern-control|Gain scheduling]]

**$M$ is symmetric and positive definite.** Always invertible, which is what makes forward dynamics well-posed.

**The system is coupled.** Moving joint 2 exerts torque on joints 1 and 3. **Joints are not independent**, and treating them as independent SISO loops is an approximation that degrades as speed rises. → [[engineering/02-control-theory/08-state-space|MIMO]]

**Coriolis and centrifugal terms scale with velocity squared**, which is why they're negligible when jogging and dominant when moving fast.

## Two directions

**Inverse dynamics** — given desired motion, what torques?

$$\boldsymbol\tau = f(\boldsymbol\theta, \dot{\boldsymbol\theta}, \ddot{\boldsymbol\theta})$$

**This is what control uses.** The **recursive Newton–Euler algorithm** computes it in $O(n)$ — a forward pass propagating velocities and accelerations outward, then a backward pass propagating forces inward. Fast enough to run at 1 kHz on a microcontroller, which is why model-based control is practical at all.

**Forward dynamics** — given torques, what motion?

$$\ddot{\boldsymbol\theta} = M^{-1}\left(\boldsymbol\tau - C\dot{\boldsymbol\theta} - \mathbf{g} - \mathbf{f}\right)$$

**This is what simulation uses.** The **articulated body algorithm** does it in $O(n)$ without forming $M$ explicitly. Every physics engine (MuJoCo, Bullet, Drake, Isaac) is doing this in its inner loop.

## Two formulations

Both give the same equation; they differ in what's convenient.

**Newton–Euler** — apply $F = ma$ and $\tau = I\alpha$ link by link, propagating outward then inward.

*Recursive, $O(n)$, efficient, and it gives you the internal joint forces* (which you need for structural design and for joint force sensing). **This is what implementations use.**

**Lagrangian** — write kinetic minus potential energy and apply

$$\frac{d}{dt}\frac{\partial L}{\partial \dot{q}_i} - \frac{\partial L}{\partial q_i} = \tau_i, \qquad L = T - V$$

*Systematic, coordinate-free, and it makes the structure visible* — you can see where $M$ and $C$ come from. **Better for analysis and for deriving properties**; worse for computation.

**Learn the Lagrangian formulation to understand the equation. Use a Newton–Euler implementation to compute it.**

## Model-based control

The payoff.

### Gravity compensation

**The cheapest big win, and the first thing to implement.**

$$\boldsymbol\tau = \mathbf{g}(\boldsymbol\theta) + \text{PID}(\mathbf{e})$$

Feed forward the gravity torque; let the feedback handle the rest.

**Why it matters:** without it, a PID holding a horizontal arm needs a large steady-state error to generate the holding torque (or a large integral term that winds up and overshoots). **With it, the error goes to zero and the feedback only has to correct the model's mistakes.**

**And it enables hand-guiding.** With gravity compensated and low feedback gains, the arm floats — you can push it around by hand, which is how you teach a collaborative robot a trajectory.

**Gravity is usually the dominant dynamic term at low speed**, so this one term captures most of the available benefit for a fraction of the modelling effort.

### Computed torque control

The full version — **feedback linearisation** applied to a manipulator:

$$\boldsymbol\tau = M(\boldsymbol\theta)\left[\ddot{\boldsymbol\theta}_d + K_v\dot{\mathbf{e}} + K_p\mathbf{e}\right] + C\dot{\boldsymbol\theta} + \mathbf{g} + \mathbf{f}$$

**Cancel the nonlinear dynamics exactly, leaving a linear, decoupled system** that a simple PD controller handles:

$$\ddot{\mathbf{e}} + K_v\dot{\mathbf{e}} + K_p\mathbf{e} = 0$$

**Each joint now behaves like an independent second-order system with whatever poles you choose** — and crucially, **the same gains work in every configuration**, because the configuration-dependence has been cancelled. → [[engineering/02-control-theory/13-nonlinear-and-modern-control|Feedback linearisation]]

**What it needs, and where it fails:**

- **An accurate model.** Cancellation error goes straight into the response — you're subtracting two large numbers, so a 10% model error is a 10% disturbance
- **Torque-controlled actuators.** A position-controlled servo can't accept a torque command, which rules this out for hobby servos and most stepper systems
- **Full state at high rate**, including joint velocity, which means good velocity estimation
- **Friction is the weak point.** Coulomb friction is discontinuous at zero velocity and never modelled well; it's what limits achievable accuracy in practice

**In practice, partial compensation is the sweet spot.** Gravity plus inertia, skip Coriolis and friction, let feedback mop up. Most of the benefit, much less of the modelling.

## Force and impedance control

What dynamics enables beyond faster tracking, and it changes what tasks are possible.

**Position control alone requires knowing exactly where the world is.** Command the gripper to a surface 1 mm off and you either miss it or push with enormous force — because a stiff position controller will apply whatever torque it takes to reach a position inside the table.

**Impedance control** commands a *relationship* between motion and force instead:

$$\mathbf{F} = M_d\ddot{\tilde{\mathbf{x}}} + B_d\dot{\tilde{\mathbf{x}}} + K_d\tilde{\mathbf{x}}$$

**You're specifying a virtual mass–spring–damper between the tool and its target.** Set $K_d$ high and it's stiff; set it low and the robot yields when pushed.

**Admittance control** is the dual — measure force, command motion. Used when the robot is position-controlled and you have a force sensor; it works on stiff industrial arms, where true impedance control needs backdrivable joints.

**Hybrid force/position control** splits directions: position-control along the surface, force-control into it. That's how you polish, deburr, or write on a whiteboard.

> **This is why torque-controlled arms (Franka, Kuka iiwa, UR to a degree) are a different class of machine.** "Push until you feel 5 N" is a fundamentally different instruction from "move to $z = 0.412$", and only one of them survives a table that's 2 mm from where you thought.

## Identification

The model needs parameters: link masses, centres of mass, inertia tensors, friction coefficients.

**From CAD** — a good starting point, and wrong. It misses cabling, connectors, the actual motor mass distribution, and gearbox inertia.

**By experiment** — the standard approach, and it works well because **the dynamics are linear in the inertial parameters**:

$$\boldsymbol\tau = Y(\boldsymbol\theta, \dot{\boldsymbol\theta}, \ddot{\boldsymbol\theta})\,\boldsymbol\pi$$

$Y$ is the **regressor** and $\boldsymbol\pi$ the parameter vector. **So it's a linear least-squares problem** — run an exciting trajectory, record torques and motion, solve. That's a surprisingly friendly result for a nonlinear system.

**Two practical points:**

**Trajectory design matters.** You must excite all the parameters — the standard approach optimises a periodic trajectory to minimise the condition number of the regressor. A lazy trajectory gives a badly conditioned fit and nonsense parameters.

**Only *base parameters* are identifiable.** Some combinations of mass and inertia never affect the torque and cannot be recovered from any experiment. Trying to identify them gives numerical garbage — you fit the identifiable combinations and accept the rest are unobservable. → [[engineering/02-control-theory/09-controllability-observability-and-pole-placement|Observability]]

## Practical notes

**Start with gravity compensation.** Best effort-to-benefit ratio by a wide margin.

**A payload changes everything.** Picking up a 5 kg object changes $M$ and $\mathbf{g}$ substantially. **Update the model when the payload changes** — most industrial controllers have a payload parameter for exactly this, and running with it wrong is a common cause of degraded accuracy and nuisance faults.

**Joint flexibility is the unmodelled thing that bites.** Harmonic drives and belts are compliant, so motor position ≠ joint position. That introduces a resonance, and it's the practical limit on bandwidth for most arms. → [[engineering/02-control-theory/06-frequency-response|Resonance]]

**Friction is worse than the models say.** Stiction, Stribeck effects, and position-dependence. It's what causes hunting around a setpoint at very low velocity, and it doesn't yield to better PID tuning.

**Simulate before you run it.** MuJoCo, Drake, PyBullet, Isaac Sim. **A dynamics bug at speed damages hardware**, and unlike a kinematic error it doesn't announce itself gently.

**Check your units and your inertia tensor convention** — about the centre of mass or about the joint? Parallel-axis theorem exists precisely because people conflate them.

---

## Related
- [[robotics/09-robot-control|Robot Control]] — putting this into a loop
- [[robotics/07-jacobians-and-singularities|Jacobians]] — where $J^T$ maps forces
- [[engineering/01-continuum-mechanics/README|Continuum Mechanics]] — the deformation this assumes away
- [[robotics/README|Robotics map]]
