# Robotics

**New domain, scaffold only — nothing written yet.** Machines that sense, decide, and move. Distinct from [[hardware/README|hardware/]], which is the electronics and embedded layer this sits on top of: hardware is "the board works," robotics is "the thing moves where I meant it to."

Scaffolded August 2026 as a stated direction rather than existing knowledge. Labelled the same way as [[ai-automation/README|ai-automation/]] and [[foundations/os/README|foundations/os]] — an honest placeholder, so it's on the map without pretending to be a course.

## Planned reading order

1. `what-robotics-actually-is` — **[Beginner]** — the sense → plan → act loop, and why every robotics problem decomposes into those three regardless of the robot
2. `sensors-and-perception` — **[Beginner]** — encoders, IMUs, range finders, cameras; noise, drift, and why a single sensor is never trusted alone
3. `actuators-and-motion` — **[Beginner]** — DC/stepper/servo motors, drivers, gearing, and the current draw that makes [[hardware/01-electricity|power design]] suddenly matter
4. **Control theory** — **already written, elsewhere.** → [[engineering/02-control-theory/README|engineering/02-control-theory/]] covers open vs closed loop, PID and how to actually tune one, steady-state error, why derivative gain amplifies noise, and a great deal past that. When this track is built, note 4 becomes a *robotics-specific* note — cascaded position/velocity/current loops, joint servo design, computed-torque control — pointing at that track for the theory rather than restating it
5. `kinematics` — **[Intermediate]** — forward and inverse kinematics, degrees of freedom, workspace; the maths that turns "put the gripper there" into joint angles
6. `state-estimation-and-filtering` — **[Advanced]** — sensor fusion, complementary and Kalman filters: combining unreliable sensors into one usable belief. The theory is in [[engineering/02-control-theory/10-observers-and-kalman|Observers and Kalman Filters]]; this note is the robot-specific application
7. `ros-and-robot-software` — **[Intermediate]** — ROS 2 nodes, topics, services, transforms; why robotics settled on a message-passing architecture
8. `localisation-and-slam` — **[Advanced]** — knowing where you are in a map, and building the map while you do
9. `safety-and-real-time` — **[Advanced]** — deadlines that are correctness constraints rather than performance goals, emergency stops, and failing safe when a moving machine can hurt someone

## Where it connects

Robotics is unusual in this vault because it's genuinely a **join** of domains that already exist here rather than a new silo:

| Draws on | For |
|---|---|
| [[hardware/README\|hardware/]] | Microcontrollers, motor drivers, power, I2C/SPI to sensors |
| [[engineering/02-control-theory/README\|control theory]] | The whole control half — PID, cascade loops, state estimation, LQR |
| [[engineering/01-continuum-mechanics/README\|continuum mechanics]] | Structural compliance, resonances, and soft robotics |
| [[ai-ml/02-ml-engineer/08-other-architectures/03-reinforcement-learning\|reinforcement learning]] | Learned control policies |
| [[ai-ml/02-ml-engineer/06-computer-vision/README\|computer vision]] | Perception from cameras |
| [[foundations/os/README\|operating systems]] | Real-time scheduling, RTOS |
| [[architecture/04-distributed-systems/03-time-and-ordering\|time & ordering]] | Multi-node robots are distributed systems with a physical body |
| [[foundations/networking/README\|networking]] | Robot ↔ base station links, and their latency budgets |

That's the argument for building it eventually: most of the prerequisites are already written.

## The honest note

Nothing here is knowledge yet. **The control theory now exists as a track** — [[engineering/02-control-theory/README|engineering/02-control-theory/]] — but it carries the same caveat, stated in its own honest note: a PID loop that looks fine on paper oscillates on hardware for reasons the paper didn't mention. **These robotics notes should still only be written *after* something has actually been made to move**, not before. The vault's own rule: [[PRIMETECHIE|reading is not a rank]].

## Related
- [[hardware/README|Hardware & Embedded]] — the layer below, and the one that's actually built
- [[PRIMETECHIE|The Primetechie Path]] — where this direction sits
- [[project-ideas|Project Ideas]] — no robotics builds listed yet; the first one belongs there before these notes do
