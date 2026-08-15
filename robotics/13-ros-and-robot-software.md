# ROS and Robot Software

**[Intermediate]** — Nodes, topics, services and transforms, and why robotics settled on message passing.

## Why an architecture at all

A robot is several processes on several machines, each talking to different hardware at different rates, needing each other's data.

**The problem this creates:** the camera driver runs at 30 Hz, the lidar at 10 Hz, the controller at 1 kHz, the planner on demand. They're written by different people, in different languages, and some of them crash.

**Writing that as one program is a mistake** — one segfault in the vision code takes down the control loop, and every component has to be in the same language, on the same machine, at the same rate.

> **So robotics settled on message passing**: independent processes exchanging typed messages over named channels. It's the same reasoning that produced microservices, arrived at independently and about a decade earlier. → [[architecture/03-architectural-patterns/README|Architectural Patterns]]

**What you get:** language independence (C++ for control, Python for the planner), process isolation (one crash doesn't take everything), distribution across machines, introspection (record and replay every message), and reusable drivers.

**What it costs:** serialisation and latency, no shared-memory speed without extra work, harder debugging (the bug is *between* processes), and version-mismatch problems.

## Core concepts

**Node** — one process, one job. `camera_driver`, `object_detector`, `arm_controller`.

**Topic** — a named, typed channel. **Publish/subscribe, many-to-many, asynchronous, anonymous.** Publishers don't know who's listening.

*Use for streaming data:* sensor readings, state estimates, commands. **This is the default and most communication is topics.**

**Service** — request/response, synchronous, one-to-one. *Use for quick queries and commands with a result:* "compute IK for this pose". **Never for anything slow** — it blocks.

**Action** — a long-running goal with feedback and the ability to cancel. *Use for anything with duration:* "move to this pose", "navigate to the kitchen". **The right choice whenever the answer takes seconds.** Nav2 and MoveIt are both action-driven.

**Parameter** — per-node configuration, settable at launch and (in ROS 2) changeable at runtime with change callbacks.

**Message** — a typed struct defined in a `.msg` file, generating code for every supported language. **Standard message types matter more than they sound** — because everyone uses `sensor_msgs/LaserScan`, any lidar driver works with any SLAM package.

## The transform system

**`tf2` is arguably the most valuable single piece of ROS**, and it solves a problem every robot has.

Every frame publishes its transform relative to its parent. `tf2` maintains the tree, **buffers it with timestamps**, and answers queries:

```
"where is the camera relative to the gripper,
 at the moment this image was captured?"
```

**That timestamp clause is the point.** A camera frame arrives 80 ms late; the arm moved in between. Using the *current* transform to interpret an *old* image gives a wrong answer, and it's a subtle error that produces plausible-looking results. `tf2` interpolates to the right moment. → [[robotics/04-rigid-body-transforms|Rigid Body Transforms]]

**The conventions:**

- `map` → `odom` → `base_link` → everything else
- **`map` → `odom`** is the SLAM/localisation correction. It jumps when a loop closes
- **`odom` → `base_link`** is odometry. **Continuous and smooth, but drifts**
- **Two frames, deliberately**: controllers use `odom` (smooth, no jumps), planners use `map` (globally correct). **A control loop on a frame that jumps is a bad time**

**Each frame has exactly one parent.** It's a tree, not a graph. Two nodes publishing the same transform is a classic and confusing bug — the values fight and the robot's model flickers.

## ROS 1 vs ROS 2

**ROS 1 is end-of-life** (Noetic's support ended in May 2025). **New work goes on ROS 2.**

| | ROS 1 | ROS 2 |
|---|---|---|
| Discovery | central `roscore` — **single point of failure** | **DDS, distributed**, no master |
| Transport | custom TCPROS | DDS (RTPS) |
| Real-time | no | yes, with care |
| QoS | none | **configurable reliability/durability** |
| Security | none | SROS2 — auth and encryption |
| Windows/embedded | poor | supported; micro-ROS for MCUs |
| Composition | separate processes | **components in one process, zero-copy** |

**The QoS settings are the ROS 2 thing that most often catches people:**

- **Reliability** — `RELIABLE` (retry until delivered) vs `BEST_EFFORT` (drop). **Sensor streams want best-effort**; a stale lidar scan is worthless, so don't spend bandwidth retransmitting it
- **Durability** — `TRANSIENT_LOCAL` lets late subscribers receive the last message. **Essential for latched data** like a map or robot description
- **History depth** — how many messages to queue

**Mismatched QoS means silent non-delivery.** The publisher publishes, the subscriber gets nothing, no error appears. **This is the single commonest ROS 2 debugging frustration**, and `ros2 topic info --verbose` is how you catch it.

## Structuring a robot system

A typical stack, and the layering is deliberate:

```
      [ behaviour tree / task layer ]
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
[ perception ]  [ planning ]   [ control ]
    │               │               │
    └───────────────┼───────────────┘
                    ▼
              [ drivers / hardware ]
```

**Design rules that hold up:**

**One node, one responsibility.** Easier to test, replace and reason about — the same argument as any service boundary.

**Drivers do nothing but talk to hardware.** No processing, no policy. Then the same driver works everywhere.

**Keep the control loop out of ROS** where timing matters. **A 1 kHz loop should not depend on message passing** — run it on a microcontroller or in a real-time thread, and use ROS for setpoints and telemetry. `ros2_control` exists exactly for this boundary. → [[robotics/14-safety-and-real-time|Safety and Real-Time]]

**Use standard message types.** Custom messages fragment the ecosystem and lose you tooling.

**Launch files describe the system**, and in ROS 2 they're Python, so they can be conditional. Keep configuration in YAML, not hardcoded.

## The ecosystem

**What you should not write yourself:**

**MoveIt 2** — arm planning, kinematics, collision checking, execution, and a config wizard. **Enormous, and worth it.** Writing your own arm planning stack is a project measured in years.

**Nav2** — mobile navigation. Global and local planners, costmaps, recovery behaviours, and a behaviour-tree coordinator. Production-grade.

**`ros2_control`** — the hardware abstraction layer for controllers. Real-time-safe, with standard controllers (joint trajectory, differential drive) and a clean hardware-interface plugin boundary. **Write a hardware interface, get the controllers free.**

**`robot_state_publisher`** — reads your URDF and joint states, publishes the whole transform tree. One line of configuration, and your entire kinematic chain is in `tf2`.

**RViz2** — 3D visualisation. **Not optional.** Seeing your transform tree, sensor data and planned path rendered together is how you find frame bugs.

**`rosbag2`** — record every message, replay it later. **The most valuable debugging tool in robotics**, because you cannot reproduce a physical run. Record everything on every run; disk is cheap and the failure you need is always the one you didn't record.

**Gazebo / Ignition** — simulation with physics and simulated sensors. Same ROS interface as the real robot, so code moves across unchanged.

## Description formats

**URDF** — XML describing links, joints, geometry, inertia. **The robot model everything reads**: RViz, MoveIt, Gazebo, `robot_state_publisher`.

**Xacro** — macros for URDF, because raw URDF is extremely verbose and repetitive. **Everyone uses xacro**; nobody writes URDF by hand past a toy.

**SDF** — Gazebo's richer format, with world modelling URDF doesn't do.

**What to get right:** inertial properties (Gazebo behaves absurdly with wrong or missing inertia — a common cause of "my simulated robot exploded"), collision geometry simplified relative to visual geometry, and joint limits matching the real hardware.

## Debugging

**The tooling, and it's genuinely good:**

```
ros2 node list / info        what's running, what it connects to
ros2 topic list / echo / hz  is data flowing, at what rate
ros2 topic info --verbose    QoS mismatches — check this early
ros2 param get / set         runtime configuration
ros2 run tf2_tools view_frames    render the transform tree
rqt_graph                    the node/topic graph, visually
ros2 bag record -a           record everything
```

**The debugging order that works:**

1. **Is the node running?** `ros2 node list`
2. **Is data flowing?** `ros2 topic hz` — a rate of zero localises the problem immediately
3. **QoS mismatch?** The silent one. Check it early, not late
4. **Frames correct?** `view_frames`, then look in RViz
5. **Timestamps sane?** Out-of-order or zero timestamps break `tf2` in confusing ways
6. **Record and replay.** Then iterate offline, deterministically, without the hardware

**Log with context.** `[joint_2] current=1.57 target=1.60 error=0.03` beats "moving". You're reading these after the fact, from a robot that isn't in front of you.

## Beyond ROS

Worth knowing that ROS isn't the only answer:

**LCM, Zenoh, ZeroMQ** — lighter message-passing alternatives. **Zenoh** is increasingly used *under* ROS 2 as a DDS replacement, especially for multi-robot and constrained networks.

**Custom stacks** — most autonomous-vehicle companies run their own middleware, for latency, determinism and safety certification.

**micro-ROS** — ROS 2 on microcontrollers, bridging the MCU/SBC divide directly.

**When not to use ROS:** a single microcontroller with one loop (just write the loop), a hard-real-time safety-certified system (ROS isn't certifiable), or an extremely resource-constrained target. **ROS earns its keep when you have multiple sensors, multiple processes, and want the ecosystem.**

---

## Related
- [[robotics/04-rigid-body-transforms|Rigid Body Transforms]] — what `tf2` manages
- [[robotics/14-safety-and-real-time|Safety and Real-Time]] — where ROS stops being appropriate
- [[architecture/04-distributed-systems/README|Distributed Systems]] — a multi-machine robot is one
- [[robotics/README|Robotics map]]
