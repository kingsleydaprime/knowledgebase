# What Robotics Actually Is

**[Beginner]** — The sense → plan → act loop, why every robotics problem decomposes into those three, and what makes this genuinely harder than software.

**Source:** `[reference]` — see [[robotics/README|the domain note]], which is blunt about what that means here.

## The loop

Every robot, from a Roomba to a surgical arm to a Mars rover, is running the same loop:

```
      ┌─────────────────────────────────────┐
      │                                     │
      ▼                                     │
  [ SENSE ] ──→ [ PLAN ] ──→ [ ACT ] ───────┘
   what is        what        make it
   the world      should       happen
   like?          I do?
```

That's it. **The decomposition is not a teaching device — it's how robot software is actually structured**, and it's why ROS is a message-passing architecture with perception nodes, planning nodes, and control nodes.

**Sense** — read encoders, IMUs, cameras, lidar. Turn raw, noisy, partial measurements into a usable belief about the world and about yourself. → [[robotics/02-sensors-and-perception|Sensors and Perception]]

**Plan** — decide what to do. At the top, "go to the kitchen". In the middle, "follow this path". At the bottom, "these joint angles, at this velocity". → [[robotics/10-motion-planning|Motion Planning]]

**Act** — drive motors so the physical thing actually does it, against gravity, friction, and a load you didn't model. → [[robotics/03-actuators-and-motion|Actuators and Motion]], [[robotics/09-robot-control|Robot Control]]

**And then repeat, fast.** The loop runs continuously because the world moves, the model is wrong, and the last action didn't do exactly what you asked.

## Why this is harder than software

The honest framing, and it's worth internalising before anything else.

**The world is the source of truth, and it doesn't have an API.**

| Software | Robotics |
|---|---|
| State is what you wrote | State is what you *measure*, noisily |
| `x = 5` means x is 5 | "move 5 cm" means somewhere near 5 cm |
| Deterministic replay | Never the same run twice |
| Bugs produce stack traces | Bugs produce a broken arm and a dent in the wall |
| Undo is free | Undo is not a thing |
| Slow = annoying | Late = wrong. A missed deadline is a correctness failure |

**Four properties cause most of the difficulty:**

**1. Everything is uncertain.** Sensors are noisy and biased. Actuators don't do exactly what you asked. Models are approximations. **There is no ground truth available to the robot** — only estimates. Which is why [[robotics/11-state-estimation-and-filtering|state estimation]] is a first-class subject rather than a detail.

**2. Time is a correctness constraint.** A control loop that misses its deadline doesn't run slower — it produces wrong output, because the maths assumed a fixed sample interval. → [[robotics/14-safety-and-real-time|Safety and Real-Time]]

**3. Physics doesn't accept invalid input.** You can't command infinite torque. You can't move a joint past its limit. You can't stop instantly. **Constraints are physical, not validation you can skip.**

**4. Failure is expensive.** A crashed process restarts. A robot arm that swings through a hard stop bends. One that swings through a person injures them. This is the reason robotics culture is conservative in ways software culture isn't.

## The three layers

Real robot software is layered by **timescale**, and the layers have genuinely different characters:

```
 ┌────────────────────────────────────────────────┐
 │  DELIBERATIVE   "go to the kitchen"            │  seconds–minutes
 │  task planning, mapping, global path planning   │  slow, smart, may fail
 ├────────────────────────────────────────────────┤
 │  EXECUTIVE      "follow this path, avoid that"  │  10–100 ms
 │  local planning, obstacle avoidance, sequencing │
 ├────────────────────────────────────────────────┤
 │  REACTIVE       "hold this joint angle"         │  0.1–10 ms
 │  servo loops, safety interlocks, e-stop         │  fast, dumb, must not fail
 └────────────────────────────────────────────────┘
```

**The rule that makes this work: the lower the layer, the faster, simpler, and more reliable it must be.** The bottom layer runs on a microcontroller or a real-time thread, has no dynamic allocation, and cannot be allowed to fail. The top layer can run in Python, take a second to think, and return "no plan found".

**Safety lives at the bottom, always.** An emergency stop that goes through the planner is not an emergency stop. → [[robotics/14-safety-and-real-time|Safety and Real-Time]]

This layering is also why [[architecture/04-distributed-systems/README|distributed-systems]] thinking shows up: a real robot is several computers (an MCU per joint, an onboard SBC, sometimes an offboard machine) exchanging messages with latency, partial failure, and no shared clock.

## The three questions

Almost every robotics problem is one of these, and naming which one you're on is most of getting unstuck:

**"Where am I?"** — [[robotics/12-localisation-and-slam|localisation]], odometry, [[robotics/11-state-estimation-and-filtering|state estimation]]. Also "where is my hand?", which is [[robotics/05-forward-kinematics-and-dh-parameters|forward kinematics]].

**"How do I get there?"** — [[robotics/10-motion-planning|motion planning]], trajectory generation, and [[robotics/06-inverse-kinematics|inverse kinematics]] for "what joint angles put the gripper *there*".

**"How do I make the hardware do it?"** — [[robotics/09-robot-control|control]], [[robotics/08-dynamics|dynamics]], and the [[engineering/02-control-theory/README|control theory]] underneath.

## Kinds of robot

The vocabulary differs by type, and the maths splits along the same line:

**Manipulators** — arms bolted to something. Industrial robots, surgical arms, the arm on a rover.

*The problem is configuration:* given the joint angles, where is the hand? (forward kinematics) Given a desired hand pose, what joint angles? (inverse kinematics) The base doesn't move, so localisation is trivial and kinematics is everything.

**Mobile robots** — things that drive, walk, swim, or fly.

*The problem is localisation:* you don't know where you are, because wheels slip and integration drifts. Kinematics is comparatively simple (a differential-drive robot has two wheels); SLAM is the hard part.

**Mobile manipulators** — both, and the errors compound. A 2 cm base localisation error is a 2 cm gripper error before the arm has done anything wrong.

**Drones and legged robots** — the additional problem is that **they're unstable open-loop**. A quadcopter with the controller off falls out of the sky; a bipedal robot falls over. Control isn't improving performance, it's the only thing keeping the machine intact — which is the case [[engineering/02-control-theory/01-what-control-theory-is|control theory]] exists for.

## Degrees of freedom

The counting argument that underlies most of the kinematics notes.

**A rigid body in 3D space has 6 DOF** — three translations ($x, y, z$), three rotations (roll, pitch, yaw). To place an object anywhere in any orientation, you need to control 6 numbers.

**So a general-purpose arm needs at least 6 joints.** That's why industrial arms are 6-axis, and it isn't a coincidence — it's the minimum to reach an arbitrary pose in the workspace.

**7+ joints is redundant** — infinitely many joint configurations reach the same hand pose. That sounds like a problem and is actually a feature: the extra freedom lets you avoid obstacles, dodge [[robotics/07-jacobians-and-singularities|singularities]], or keep joints away from their limits while the hand stays put. It's why collaborative arms (UR, Franka, Kuka iiwa) are 7-axis and why the human arm is too.

**Fewer than 6 means a restricted workspace.** A SCARA arm has 4 DOF and can only do "move in a plane and rotate about vertical" — which is exactly what pick-and-place needs, at much lower cost.

**Mobile robots are often *underactuated*:** a car has 3 DOF in the plane ($x, y, \theta$) but only 2 controls (drive and steer). You cannot move sideways. **That's why parallel parking takes a manoeuvre** rather than a translation, and it's a genuine mathematical constraint called nonholonomy, not a limitation of the car. → [[robotics/10-motion-planning|Motion Planning]]

## What you actually build

The gap between the subject and the practice.

**Most robotics work is not algorithms.** It's wiring, power, mounting, calibration, coordinate frames that don't line up, a sensor that reports in the wrong units, and a motor that stalls at the current you specced. The algorithm is usually the part that works.

**Calibration is a bigger deal than it sounds.** Camera intrinsics, camera-to-robot extrinsics, joint zero offsets, wheel radius and track width. **A 1° error in a joint zero is a centimetre of error at the end of a metre-long arm**, and no amount of clever control fixes a wrong model.

**Coordinate frames cause more bugs than anything else.** World, base, joint, tool, camera, map, odom — every one is a frame, and getting the transform between two of them backwards produces a robot that confidently moves in exactly the wrong direction. ROS has a whole subsystem (`tf2`) for nothing but bookkeeping frames, which tells you how common the problem is. → [[robotics/04-rigid-body-transforms|Rigid Body Transforms]]

## Reading this track

**01–03 are the ground floor** — what robots are, what they sense, what they move with. Little maths.

**04–08 are the kinematics and dynamics core**, and they build strictly in order. Transforms before forward kinematics before inverse kinematics before Jacobians. This is the part that's genuinely a subject.

**09–10 are making it move** — control and planning.

**11–12 are knowing where you are** — estimation and SLAM.

**13–14 are the engineering around it** — the software architecture and the safety obligations.

**Prerequisites:** linear algebra (matrices, rotations, eigenvalues), calculus, and [[engineering/02-control-theory/README|control theory]] for notes 08–09. The control track carries the feedback theory this domain applies.

---

## Related
- [[robotics/02-sensors-and-perception|Sensors and Perception]] — the sense half
- [[robotics/09-robot-control|Robot Control]] — the act half
- [[engineering/02-control-theory/README|Control Theory]] — the theory underneath all of it
- [[robotics/README|Robotics map]]
