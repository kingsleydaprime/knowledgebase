# Sensors and Perception

**[Beginner]** — What a robot can actually measure, why every sensor lies in its own particular way, and why one sensor is never trusted alone.

## The two questions

Sensors answer one of two things, and the split matters because they fail differently:

**Proprioceptive** — *what is my own body doing?* Encoders, IMUs, current sensors, joint torque. Internal, high rate, and usually the most reliable thing you have.

**Exteroceptive** — *what is the world like?* Cameras, lidar, ultrasonic, force sensors, GPS. External, lower rate, and much noisier.

> **The pattern that recurs everywhere: proprioceptive sensors are precise but drift; exteroceptive sensors are noisy but absolute.** An IMU tells you exactly how you rotated over the last millisecond and is hopeless about where you're pointing after a minute. A camera looking at a landmark has no idea what happened in the last millisecond and knows exactly where you are.
>
> **Fusing those two characteristics is what [[robotics/11-state-estimation-and-filtering|state estimation]] is for.** It's not a coincidence that the maths works out — the two error profiles are complementary by nature.

## Encoders

The most important sensor on most robots, and the one you'll use first.

**Incremental (quadrature)** — two channels 90° out of phase. Counting edges gives position; the phase relationship gives direction.

```
A  ──┐  ┌──┐  ┌──┐  ┌──
     └──┘  └──┘  └──┘
B  ─┐  ┌──┐  ┌──┐  ┌───
    └──┘  └──┘  └──┘
     ↑ A leads B = forward
```

**Cheap, high resolution, and it has no absolute reference.** Power cycle and you're at zero wherever you happen to be, so you need a **homing routine** — drive to a limit switch or an index pulse at startup. Every incremental-encoder robot does this, and it's why industrial arms do a slow dance when powered on.

**Absolute** — reports the actual angle, immediately, at power-on. Magnetic (AS5600-class) or optical. **More expensive, no homing.** Single-turn absolute still needs multi-turn tracking if the joint can rotate more than once.

**What bites:**

- **Resolution vs quantisation noise.** Differentiating position to get velocity amplifies quantisation directly. At low speed you get very few counts per sample and the velocity estimate is garbage. **Estimate velocity with a filter or an observer, don't just difference.** → [[engineering/02-control-theory/12-digital-control|Digital Control]]
- **Counting on the wrong edges.** Use hardware quadrature decoding (most MCUs have it) rather than interrupts. At speed, software counting drops edges and the position silently drifts.
- **Encoder on the motor vs on the joint.** With a gearbox, motor-side gives resolution and joint-side gives truth. **Backlash lives between them** and the difference is real.

## IMUs

Accelerometer + gyroscope, usually + magnetometer. On every drone, every balancing robot, every phone.

**Gyroscope** — angular *rate*, in °/s. Integrate to get angle. **Very good over short intervals, and it drifts without bound** because you're integrating a biased signal. A bias of 0.1 °/s is 6° after a minute.

**Accelerometer** — specific force, in m/s². At rest it measures **gravity**, which gives you absolute roll and pitch. In motion it measures gravity *plus* acceleration and you can't separate them from one reading.

**Magnetometer** — the earth's field, giving absolute heading. And it is **wrecked by anything ferrous or current-carrying** — the robot's own motors, a steel table, a nearby power cable.

**The classic fusion**, and the reason it works:

| | Short term | Long term |
|---|---|---|
| Gyro | excellent | drifts |
| Accel (tilt) | noisy under motion | absolute, no drift |
| Mag (heading) | noisy, disturbed | absolute, no drift |

**A complementary filter** is the cheap version — high-pass the gyro, low-pass the accelerometer, add:

$$\theta_k = \alpha\left(\theta_{k-1} + \omega\,\Delta t\right) + (1-\alpha)\,\theta_{accel}$$

with $\alpha \approx 0.98$. **Five lines of code, and on a balancing robot it works.** The Kalman filter is the principled version of exactly this, with the blend chosen by the noise statistics instead of by hand. → [[robotics/11-state-estimation-and-filtering|State Estimation]]

**Estimate gyro bias as a state.** It drifts slowly with temperature, and a filter that tracks and subtracts it is the difference between an attitude estimate that holds and one that doesn't. → [[engineering/02-control-theory/10-observers-and-kalman|Observers and Kalman Filters]]

**Yaw is the hard one.** Roll and pitch have gravity as an absolute reference. **Yaw has nothing** except the magnetometer or an external fix, so indoors, where the magnetometer is unreliable, yaw drifts and there's no clean fix. This is a real, common, and frequently underestimated problem.

## Range and depth

**Ultrasonic** — cheap, a few metres, wide beam. Fails on soft or angled surfaces (the pulse reflects away rather than back). Fine for "is there a wall", useless for mapping.

**Infrared time-of-flight** (VL53L0X class) — cheap, fast, centimetre accuracy, short range. Confused by sunlight and by dark or shiny surfaces.

**Lidar** — the workhorse of mobile robotics. A spinning laser returning a plane (2D) or a cloud (3D) of ranges.

*Accurate, fast, and works in the dark.* Expensive, and it fails on glass, mirrors, and heavy dust or rain. **2D lidar plus a flat floor is the classic indoor SLAM setup** and it's why so many robot vacuums have a turret.

**Depth cameras** — structured light (older Kinect), active IR stereo (RealSense), or time-of-flight. A dense depth image, cheap relative to lidar.

*Short range, noisy at edges, and sunlight destroys the IR-based ones.* Good indoors, poor outdoors.

**Radar** — works through fog, rain and dust where lidar doesn't, and measures velocity directly via Doppler. Low angular resolution. Automotive and outdoor.

## Cameras

The richest sensor and the hardest to use.

**A camera gives you enormous information in a form that needs interpretation.** Everything else on this list returns a number; a camera returns two million numbers that mean nothing until something processes them. → [[ai-ml/02-ml-engineer/06-computer-vision/README|Computer Vision]]

**What cameras are used for in robotics:**

- **Fiducial markers** (AprilTag, ArUco) — a printed square giving full 6-DOF pose, robustly, with a library. **Wildly effective and underused.** If you need to know where an object is and you're allowed to put a sticker on it, do that before you train anything
- **Visual odometry** — track features between frames to estimate motion
- **Object detection and pose** — where is the mug, and which way up
- **Line following** — the classic beginner project, and still how a lot of AGVs navigate
- **Visual servoing** — control directly on image error, without ever computing a 3D position

**What bites:**

- **Calibration is mandatory.** Intrinsics (focal length, principal point, distortion) *and* the extrinsic transform from camera to robot. **An uncalibrated camera gives confidently wrong 3D positions**, and the OpenCV checkerboard routine takes twenty minutes
- **Lighting changes everything.** A pipeline tuned at your desk fails in the afternoon sun. This is the single commonest reason a vision demo doesn't reproduce
- **Latency.** Capture, transfer, process — 50–100 ms is normal, and that's a very long time in a control loop. → [[engineering/02-control-theory/03-time-response|Time delay]]
- **One camera gives no scale.** Monocular vision recovers structure only up to an unknown scale factor. Stereo, depth, or a known-size object resolves it

## Force and torque

Underrated, and what separates a robot that can only follow a trajectory from one that can interact.

**Joint torque sensing** — strain gauges in the joint, or estimated from motor current. Enables compliance: the robot yields when pushed rather than fighting.

**Motor current *is* a torque estimate**, free, since $\tau \approx K_t i$. Crude — it misses friction and gearbox losses — but it's enough for basic collision detection, and it's how most collaborative arms notice they hit something.

**Six-axis F/T sensors** at the wrist — full force and torque vector. Expensive, and the enabler for assembly, polishing, and anything involving contact.

**Tactile sensors** — arrays on a gripper. Grasp quality, slip detection. Still a research area more than a solved product.

> **Force sensing changes what's possible.** Position control alone requires knowing exactly where the world is. **Force control lets you say "push until you feel 5 N" and stop caring**, which is how a human inserts a plug without measuring anything. → [[robotics/09-robot-control|Robot Control]]

## GPS and absolute positioning

**GPS/GNSS** — a few metres, outdoors only. **RTK-GNSS** with a base station gets centimetres, and it's what agricultural and survey robots use.

*Fails indoors, under trees, in urban canyons, and it drops out without warning.* **Never build a system that breaks when GPS drops** — it will.

**Indoor alternatives:** UWB beacons (10 cm, needs infrastructure), motion capture (sub-millimetre, needs a room full of cameras — the standard for drone research), and visual/lidar localisation against a map, which needs no infrastructure and is what most real robots use.

## The rules

What experience teaches, compressed:

**1. Every sensor lies.** Noise, bias, drift, quantisation, latency, dropouts. Design assuming each one, individually, will give you a bad reading.

**2. Never trust one sensor.** Redundancy and fusion, always. A single point of sensing is a single point of failure — and unlike a crashed process, a lying sensor keeps reporting.

**3. Know your latency.** A measurement is a statement about the past. If it took 80 ms to arrive, you're controlling on 80 ms old information, and **timestamping at capture rather than at arrival is the fix.**

**4. Calibrate, then calibrate again.** Most "algorithm" problems are calibration problems.

**5. Reject outliers explicitly.** One bad reading through an unguarded filter corrupts the estimate. Gate on the innovation. → [[engineering/02-control-theory/10-observers-and-kalman|Observers and Kalman]]

**6. Check units and signs first.** Degrees vs radians, and a flipped axis, account for an embarrassing share of robotics bugs. The robot moving smoothly in exactly the wrong direction is the signature.

**7. Log everything, timestamped.** You cannot reproduce a physical run. The log is the only debugger you have. → [[robotics/13-ros-and-robot-software|ROS and Robot Software]]

---

## Related
- [[robotics/11-state-estimation-and-filtering|State Estimation and Filtering]] — turning these into a usable belief
- [[robotics/03-actuators-and-motion|Actuators and Motion]] — the other half of the hardware
- [[hardware/05-communication-protocols|Communication Protocols]] — I2C/SPI/UART, how sensors physically talk
- [[robotics/README|Robotics map]]
