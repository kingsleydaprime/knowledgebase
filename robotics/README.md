# Robotics

Machines that sense, decide, and move. Distinct from [[hardware/README|hardware/]], which is the electronics and embedded layer this sits on top of: hardware is "the board works," robotics is "the thing moves where I meant it to."

**~22,000 words across 14 notes.** Built August 2026 against the 9-note curriculum this README originally proposed, with the kinematics half expanded — transforms, forward, inverse, Jacobians and dynamics each earned their own note. `[reference]` throughout, and **the honest note at the bottom is the important part of this page.**

> **The one idea:** every robot is running **sense → plan → act**, forever, fast. That's not a teaching device — it's how the software is actually structured, and it's why ROS is a message-passing architecture with perception, planning and control nodes.

## Reading order

**01–03 — the ground floor.** What robots are, what they sense, what they move with. Little maths.

1. [[robotics/01-what-robotics-actually-is|What Robotics Actually Is]] — **[Beginner]** — the sense/plan/act loop, the three layers by timescale, degrees of freedom, and **why this is genuinely harder than software**
2. [[robotics/02-sensors-and-perception|Sensors and Perception]] — **[Beginner]** — encoders, IMUs, lidar, cameras, force. **Proprioceptive sensors are precise but drift; exteroceptive ones are noisy but absolute** — the whole reason fusion works
3. [[robotics/03-actuators-and-motion|Actuators and Motion]] — **[Beginner]** — DC/BLDC/stepper/servo, gearing and backlash, drivers, and the stall current that browns out your logic supply

**04–08 — kinematics and dynamics.** The part that's genuinely a subject. Builds strictly in order.

4. [[robotics/04-rigid-body-transforms|Rigid Body Transforms]] — **[Intermediate]** — rotations, quaternions, homogeneous transforms, frame trees. **Get the conventions right once and the rest follows**
5. [[robotics/05-forward-kinematics-and-dh-parameters|Forward Kinematics and DH Parameters]] — **[Intermediate]** — the easy direction, the notation the field standardised on, and why URDF replaced it in practice
6. [[robotics/06-inverse-kinematics|Inverse Kinematics]] — **[Intermediate → Advanced]** — the hard direction. No solution, one, eight, or infinitely many — and **choosing between them is half the problem**
7. [[robotics/07-jacobians-and-singularities|Jacobians and Singularities]] — **[Advanced]** — velocities, the $\boldsymbol\tau = J^T\mathbf{F}$ duality, and the configurations where your commands stop meaning what you think
8. [[robotics/08-dynamics|Dynamics]] — **[Advanced]** — forces not just geometry. Gravity compensation, computed torque, impedance control, and identifying the model

**09–10 — making it move.**

9. [[robotics/09-robot-control|Robot Control]] — **[Intermediate → Advanced]** — cascaded position/velocity/current loops, trajectory generation, compliance, and what actually goes wrong on hardware
10. [[robotics/10-motion-planning|Motion Planning]] — **[Advanced]** — configuration space, RRT and friends, nonholonomic constraints, and turning a path into a trajectory

**11–12 — knowing where you are.**

11. [[robotics/11-state-estimation-and-filtering|State Estimation and Filtering]] — **[Advanced]** — **why odometry drifts without bound**, what robots actually fuse, estimating bias as a state, and the delayed-measurement problem
12. [[robotics/12-localisation-and-slam|Localisation and SLAM]] — **[Advanced]** — particle filters, graph-based SLAM, and **why loop closure is the single most important operation**

**13–14 — the engineering around it.**

13. [[robotics/13-ros-and-robot-software|ROS and Robot Software]] — **[Intermediate]** — nodes, topics, actions, `tf2`, ROS 2 QoS, and what not to write yourself
14. [[robotics/14-safety-and-real-time|Safety and Real-Time]] — **[Advanced]** — deadlines as correctness constraints, failing to a *defined* state, and why an E-stop is never a software feature

## The things worth carrying

1. **Odometry is a relative measurement used as an absolute one.** It drifts without bound and no encoder resolution fixes it — **1° of heading error is 17 cm after 10 m** → [[robotics/11-state-estimation-and-filtering|11]]
2. **Never trust one sensor.** Every one lies in its own particular way, and a lying sensor keeps reporting → [[robotics/02-sensors-and-perception|02]]
3. **Coordinate frames cause more bugs than any algorithm.** Write the sub/superscripts; adjacent indices must match → [[robotics/04-rigid-body-transforms|04]]
4. **Inverse kinematics is a search with choices, not an inverse function.** Solve for a *trajectory* with continuity, not for independent points → [[robotics/06-inverse-kinematics|06]]
5. **A singularity isn't where you crash — it's where your commands stop meaning what you think.** Damped least squares, always → [[robotics/07-jacobians-and-singularities|07]]
6. **Gravity compensation is the cheapest big win in manipulator control** → [[robotics/08-dynamics|08]]
7. **Real-time means predictable, not fast.** Jitter is worse than latency → [[robotics/14-safety-and-real-time|14]]
8. **"Remove power" is not automatically safe.** A powered-off arm holding a load collapses; fail to a *defined* state → [[robotics/14-safety-and-real-time|14]]
9. **Angle error must wrap.** 179° to −179° is 2°, not 358° — and the unwrapped version is dramatic → [[robotics/04-rigid-body-transforms|04]]
10. **Most robotics work is calibration, wiring and frames.** The algorithm is usually the part that works → [[robotics/01-what-robotics-actually-is|01]]

## Where it connects

Robotics is unusual in this vault because it's genuinely a **join** of domains that already exist here rather than a new silo:

| Draws on | For |
|---|---|
| [[engineering/02-control-theory/README\|control theory]] | **The whole theory half** — PID, cascade loops, observers/Kalman, LQR, digital implementation |
| [[engineering/01-continuum-mechanics/README\|continuum mechanics]] | Structural compliance, resonances, soft robotics |
| [[hardware/README\|hardware/]] | Microcontrollers, motor drivers, power, I2C/SPI to sensors |
| [[ai-ml/02-ml-engineer/08-other-architectures/03-reinforcement-learning\|reinforcement learning]] | Learned control policies |
| [[ai-ml/02-ml-engineer/06-computer-vision/README\|computer vision]] | Perception from cameras |
| [[foundations/os/README\|operating systems]] | Real-time scheduling, RTOS, priority inversion |
| [[architecture/04-distributed-systems/03-time-and-ordering\|time & ordering]] | Multi-node robots are distributed systems with a physical body |
| [[foundations/networking/README\|networking]] | Robot ↔ base station links, and their latency budgets |

**That's the argument for the domain existing:** most of the prerequisites were already written, and this track mostly connects them to physical hardware.

## Deliberate divisions of labour

Two things live elsewhere on purpose, so you don't go looking:

**Control theory** — [[engineering/02-control-theory/README|engineering/02-control-theory/]]. This README originally planned it as note 4 here. It became its own 13-note track instead, because it's a real subject that applies far beyond robots (a TCP congestion controller and an autoscaler are feedback loops with the same pathologies). **Note 09 here is the robotics-specific part** — cascaded joint loops, trajectory following, compliance — and points there for the theory.

**Kalman filtering** — the algorithm is in [[engineering/02-control-theory/10-observers-and-kalman|Observers and Kalman Filters]]. **Note 11 here is the application** — what robots fuse, why odometry drifts, delayed measurements.

## The honest note

**None of this is knowledge yet.** It's `[reference]` — assembled from the standard sources, not from a robot that moved.

**And this domain punishes that gap harder than most.** A PID loop that looks fine on paper oscillates on hardware for reasons the paper didn't mention: the encoder quantises, the gearbox has backlash, the loop jitters, the sensor is 80 ms late. **Every note here has a "what actually goes wrong" section, and those are the parts written from other people's experience rather than mine.** Read them as a list of things to watch for, not as things I've watched for.

The original rule on this page still stands, and it's the right one:

> **These notes should only be trusted after something has actually been made to move.**

The vault's own principle: [[PRIMETECHIE|reading is not a rank]].

**The cheapest way to close the gap**, roughly in order of effort:

1. **A servo and a potentiometer.** Close a position loop by hand. Watch it oscillate when you raise the gain. Everything in [[engineering/02-control-theory/04-pid-control|PID]] becomes concrete in an afternoon
2. **A two-wheeled balancing robot.** MPU-6050, two motors, an MCU. It's an unstable plant, so it *cannot* work without feedback — you'll implement a complementary filter and a real cascade, and it'll fall over until both are right
3. **A 3-DOF arm** from hobby servos. Forward kinematics, then inverse. **A tape measure will settle more arguments than any simulation**
4. **A differential-drive robot in ROS 2**, with `slam_toolbox` and Nav2. Odometry drift stops being a paragraph and becomes a thing you watch happen
5. **Simulate first, always.** MuJoCo, PyBullet, or Gazebo. Free, and it catches the errors that damage hardware

**Nothing in [[project-ideas|project-ideas]] is a robotics build yet.** That's the real gap on this page — the first one belongs there before these notes deserve much trust.

## Known gaps

Within the track: no worked examples end to end, no code beyond pseudocode, nothing on grasping and manipulation planning specifically, nothing on legged locomotion (a subject in itself), nothing on multi-robot coordination, and only a mention of learned control. Aerial and underwater vehicles get passing references rather than treatment.

## Related
- [[robotics/projects|Projects]] — **the reps for this domain**, graded 🟢🟡🔴 with a *done when* for each
- [[engineering/02-control-theory/README|Control Theory]] — the theory half, deliberately housed elsewhere
- [[hardware/README|Hardware & Embedded]] — the layer below, and the one that's actually built
- [[PRIMETECHIE|The Primetechie Path]] — where this direction sits
- [[project-ideas|Project Ideas]] — no robotics builds listed yet; the first one belongs there
