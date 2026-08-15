# Safety and Real-Time

**[Advanced]** — Deadlines that are correctness constraints rather than performance goals, and failing safe when a moving machine can hurt someone.

## Real-time means deadlines, not speed

**The commonest misunderstanding in the subject.**

> **Real-time does not mean fast. It means predictable.** A system that responds in a guaranteed 10 ms is real-time. One that usually responds in 1 ms and occasionally takes 100 ms is not — and for a control loop, the second is worse.

**Hard real-time** — a missed deadline is a **system failure**. Motor commutation, safety interlocks, flight control.

**Firm real-time** — a late result is worthless but not catastrophic. A control loop that skips a cycle.

**Soft real-time** — late degrades quality. Video display, logging, UI.

**Why a missed deadline is a correctness failure**, not a performance one: the control maths assumed a fixed sample interval $T$. Your integral and derivative terms are computed with it. **Miss a deadline and your effective gains change** — you're now running a different controller than the one you tuned. → [[engineering/02-control-theory/12-digital-control|Digital Control]]

**And jitter is worse than latency.** A consistent 5 ms delay you can design around — model it, add phase margin. A delay varying between 1 and 10 ms you cannot, because the plant you're controlling changes every cycle.

## Achieving it

**Determinism is destroyed by anything unbounded.** The list of what to avoid in a real-time path:

- **Dynamic memory allocation** — `malloc` has unbounded worst-case time and can fragment. **Pre-allocate everything**
- **Unbounded loops** — every loop needs a provable iteration bound
- **Blocking I/O** — file writes, network calls, printing. Log to a preallocated ring buffer and let a low-priority thread drain it
- **Page faults** — `mlockall()` to pin memory resident
- **Garbage collection** — which rules out most managed runtimes for hard real-time
- **Priority inversion** — a low-priority task holding a lock a high-priority task needs. **Use priority inheritance mutexes**; this is what caused the Mars Pathfinder resets in 1997

**Where to run it:**

| | Determinism | Note |
|---|---|---|
| **Bare metal MCU** | **excellent** | no OS to interfere. Where the fast loop belongs |
| **RTOS** (FreeRTOS, Zephyr) | excellent | real scheduling guarantees, small footprint |
| **Linux + PREEMPT_RT** | good | tens of µs latency. The practical choice for a robot SBC |
| **Stock Linux** | poor | tens of *milliseconds* of jitter. Fine for planning, not control |
| **Python / JVM / Go** | poor | GC pauses. Never in a control loop |

→ [[foundations/os/03-scheduling|Scheduling]], [[foundations/os/README|Operating Systems]]

**The standard architecture, and it's the right default:**

```
 ┌──────────────────────────────────────┐
 │  Linux SBC — planning, perception,   │   soft real-time
 │  SLAM, ROS, logging                  │   Python/C++, GC fine
 └──────────────────┬───────────────────┘
                    │ setpoints (10–100 Hz)
 ┌──────────────────▼───────────────────┐
 │  MCU / RT thread — servo loops,      │   HARD real-time
 │  safety interlocks, watchdog          │   C, no allocation
 └──────────────────────────────────────┘
```

**Put the hard real-time work on hardware that can guarantee it**, and let the smart, slow, occasionally-crashing layer send setpoints. **If the top layer dies, the bottom layer must still behave safely** — which is the whole point of the split.

## Failing safe

**Every robot needs a defined behaviour for every failure**, and "undefined" is a decision you've made by not making it.

**What can fail:** software crashes, a network link drops, a sensor lies, a motor stalls, power sags, the operator walks away.

**Watchdogs.** A hardware timer that resets or disables the system if it isn't petted regularly. **The essential mechanism**, because it catches the failure you didn't anticipate — including a hung process that's still holding the motors at full torque.

**Pet it from the actual control loop**, not from a timer callback. A watchdog fed by a thread that's still alive while the control loop is wedged tells you nothing.

**Heartbeats between nodes.** If the planner stops publishing, the controller must notice and stop — not hold the last command forever. **"Hold last command" is a dangerous default** for a moving robot.

**Define the safe state, per system:**

| Robot | Safe state |
|---|---|
| Arm | stop, brakes on. **Not** power-off — a vertical arm falls |
| Ground robot | stop, brakes |
| Drone | hover, then controlled descent. **Not** motors-off |
| Mobile with a payload | stop before drop |

**"Remove power" is not automatically safe**, and this catches people. A powered-off arm holding a load collapses. A powered-off drone falls out of the sky. **Fail to a *defined* state, not to zero.**

**Limits at every layer**, because each catches what the one above missed:

1. **Software limits** — joint, velocity, torque, workspace
2. **Firmware limits** — current, temperature, independent of the software above
3. **Hardware limits** — mechanical stops, fuses, current-limited supplies

**Defence in depth.** The software limit will be wrong someday.

## Emergency stops

**The E-stop is not a software feature.**

A real E-stop is a **hardwired, normally-closed circuit** that cuts motor power directly through a safety relay. **It works when the software has crashed, the OS has hung, and the main board is dead** — which is exactly when you need it.

**Requirements:**

- **Hardwired**, not a software message. A button that publishes a ROS topic is a *stop button*, not an E-stop
- **Normally closed** — a cut wire triggers the stop. **Fail-safe by construction**
- **Latching** — stays stopped until deliberately reset
- **Reachable** from wherever a person can be hurt
- **Category 0** (immediate power removal) or **Category 1** (controlled stop, then power removal). Cat 1 is safer for arms that would fall

**Never route an E-stop through software you wrote.** The entire point is that it works when your software doesn't.

## Human-robot safety

The standards exist because people have been killed by robots, and they encode real lessons.

**ISO 10218** (industrial robots) and **ISO/TS 15066** (collaborative operation) define four modes:

**Safety-rated monitored stop** — robot stops when a human enters; resumes when they leave.

**Hand guiding** — the operator moves the robot directly, with an enabling device held.

**Speed and separation monitoring** — the robot slows as a human approaches and stops if they get too close. Needs reliable sensing of where people are.

**Power and force limiting** — the robot is *inherently* safe, limited so contact can't injure. **This is what "collaborative robot" actually means**, and TS 15066 tabulates force and pressure limits per body region.

**The concept underneath:** a fence keeps people out; a collaborative robot is safe to be near. **Those require completely different designs**, and "we'll limit the speed in software" doesn't make a robot collaborative — the limiting has to be safety-rated.

**And the honest caveat:** a cobot is only collaborative *for a given task*. Give it a knife or a hot tool and the force limits are irrelevant. **The risk assessment covers the whole application, not the arm.**

## Redundancy and diversity

**For anything where failure is unacceptable:**

**Redundancy** — two of the same thing. Handles random failure.

**Diversity** — two *different* things solving the same problem. **Handles design failure**, which redundancy does not: two copies of the same buggy code fail identically.

Dual encoders that disagree indicate a fault. **Comparison is itself a detection mechanism** — the disagreement is the signal.

**Safety Integrity Levels (SIL/PL)** quantify the required reliability of a safety function. **You cannot claim a safety level for software you haven't developed to the corresponding process** — this is why certified safety controllers are separate, simple, and expensive.

## Testing what can hurt people

**You cannot test safety into a system**, but you can catch a great deal.

**Simulate first.** Every trajectory, every planner change. Free, and it catches the gross errors.

**Then run at reduced speed** with everyone at a distance and a hand on the E-stop. Industrial practice caps teach-mode speed at 250 mm/s for exactly this reason.

**Test the failure paths deliberately.** Kill the planner process. Unplug the network. Yank a sensor. **The failure handling you never tested does not work** — and unlike a feature, nobody notices it's broken until it matters.

**Fault injection** in simulation: dropped messages, delayed sensors, stuck values, wrong data. → [[architecture/04-distributed-systems/15-testing-distributed-systems|Testing Distributed Systems]]

**Record everything.** When something goes wrong you get one chance to understand it, and the log is all you'll have. → [[robotics/13-ros-and-robot-software|rosbag]]

## Practical notes

**Measure your loop timing.** Log actual $dt$, not the nominal one, and look at the *distribution* — the tail is what matters. A p99 of 3× your period means you're not meeting your deadline.

**Budget the whole chain**, not just computation: sensor → transport → compute → actuate. The compute is often the smallest term.

**Separate power domains.** Motor power and logic power on different rails. **A stalling motor should never reset your controller** — and when it does, the fault presents as a mystifying software bug.

**Brakes are not stops.** Many joint brakes are holding brakes, rated to hold a stationary load, not to decelerate a moving one.

**Know what happens on power loss** — mid-motion, mid-grasp, mid-flight. Decide it deliberately.

**Assume the human does the wrong thing.** They will reach in, lean over, and press reset while standing in the workspace. Design for it.

> **The cultural point.** In software, moving fast and fixing forward is often correct. **A robot that fails injures someone or destroys hardware, and there's no rollback.** The conservatism in robotics engineering isn't timidity — it's calibrated to a failure mode that software people don't usually face. → [[PRIMETECHIE|Reading is not a rank.]]

---

## Related
- [[robotics/09-robot-control|Robot Control]] — the loops with the deadlines
- [[foundations/os/03-scheduling|Scheduling]] — how an OS meets or misses them
- [[robotics/13-ros-and-robot-software|ROS and Robot Software]] — and where it isn't appropriate
- [[robotics/README|Robotics map]]
