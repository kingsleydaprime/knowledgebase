# Robotics

## What robotics is

**Robotics is building machines that sense the world, decide what to do, and move to do it, on their own.**

A robot vacuum feels for walls, works out where it hasn't cleaned yet, and drives there. A factory arm sees a part on a belt, works out how to bend its joints to reach it, and picks it up. Every robot runs the same loop, many times a second: **sense** (read its sensors), **plan** (decide what to do), **act** (drive its motors).

It's harder than ordinary software because the real world is messy. Sensors give slightly wrong readings, motors don't move exactly as told, wheels slip, and an error that would be a bug report in software can be a broken robot or an injury. Much of robotics is maths for describing position and movement, plus methods for coping with uncertainty.

## What you'll be able to do

By the end you will be able to:
- explain the sense-plan-act loop and the parts of a robot;
- choose sensors and motors, and avoid common wiring mistakes;
- describe where things are and how they're turned, in 3D, without mixing up coordinate frames;
- work out where a robot arm's hand is from its joint angles, and the reverse: which joint angles reach a given point;
- control motors smoothly and plan paths around obstacles;
- combine sensor readings to estimate where a robot is, and build a map while exploring;
- use ROS, the standard robot software framework, and design for safety.

## Where to start

**Before you start:** programming, and some [[mathematics/04-linear-algebra/index|linear algebra]] (vectors and matrices) and trigonometry. [[control-theory/index|Control Theory]] covers the theory behind making things move smoothly; this course points to it where needed.

Read in order. Notes 01–03 need little maths. Notes 04–08 are the mathematical core and build strictly on each other.

### The basics

1. [[robotics/01-what-robotics-actually-is|What Robotics Actually Is]]: the sense-plan-act loop, how many ways a robot can move, and why this is harder than software.
2. [[robotics/02-sensors-and-perception|Sensors and Perception]]: wheel counters, motion sensors, laser scanners, cameras and force sensors, and why combining sensors works better than trusting one.
3. [[robotics/03-actuators-and-motion|Actuators and Motion]]: the main kinds of motor, gears, motor drivers, and the power surge that can reset your electronics.

### Position and movement (the mathematical core)

4. [[robotics/04-rigid-body-transforms|Rigid Body Transforms]]: describing where something is and which way it faces in 3D, and keeping track of many coordinate frames. Get this right and the rest follows.
5. [[robotics/05-forward-kinematics-and-dh-parameters|Forward Kinematics]]: working out where an arm's hand is from its joint angles, the easy direction.
6. [[robotics/06-inverse-kinematics|Inverse Kinematics]]: the hard direction: which joint angles put the hand at a given point. There may be no answer, one, or many.
7. [[robotics/07-jacobians-and-singularities|Jacobians and Singularities]]: linking joint speeds to hand speed, and the positions where an arm loses the ability to move in some direction.
8. [[robotics/08-dynamics|Dynamics]]: the forces involved, not just the shapes: holding an arm up against gravity, and moving it accurately.

### Making it move

9. [[robotics/09-robot-control|Robot Control]]: controlling motors in layers, planning smooth movements, and what goes wrong on real hardware.
10. [[robotics/10-motion-planning|Motion Planning]]: finding a path around obstacles, and turning it into a movement the robot can actually follow.

### Knowing where you are

11. [[robotics/11-state-estimation-and-filtering|State Estimation and Filtering]]: combining sensor readings to estimate position, and why counting wheel turns alone always drifts.
12. [[robotics/12-localisation-and-slam|Localisation and SLAM]]: working out where you are on a map, and building the map at the same time.

### Building it properly

13. [[robotics/13-ros-and-robot-software|ROS and Robot Software]]: ROS, the standard framework that connects a robot's programs, and what not to write yourself.
14. [[robotics/14-safety-and-real-time|Safety and Real-Time]]: meeting deadlines every time, stopping safely when something fails, and why an emergency stop must never depend on software.

## Practice

These notes should only be trusted once something has actually been made to move. The cheapest ways to start, roughly from easiest:

1. **A servo motor and a knob:** make the motor follow the knob, then turn up the gain and watch it wobble.
2. **A two-wheeled balancing robot:** it falls over without good feedback, so it forces you to get sensing and control right.
3. **A small arm from hobby servos:** work out positions both ways, and check them with a tape measure.
4. **A wheeled robot in ROS 2** that maps a room. You'll watch the wheel-counting drift happen.
5. **Simulate first** in MuJoCo, PyBullet or Gazebo. It's free and catches mistakes before they break hardware.

- [[robotics/projects|Projects]]: hands-on tasks with a clear "done when".

## Key ideas to remember

1. **Counting wheel turns to track position always drifts.** A 1° error in heading puts you 17 cm off after 10 metres. → [[robotics/11-state-estimation-and-filtering|11]]
2. **Never trust one sensor.** Each is wrong in its own way, and a faulty one keeps reporting confidently. → [[robotics/02-sensors-and-perception|02]]
3. **Mixed-up coordinate frames cause more bugs than any algorithm.** → [[robotics/04-rigid-body-transforms|04]]
4. **Angles wrap around.** From 179° to −179° is 2°, not 358°. → [[robotics/04-rigid-body-transforms|04]]
5. **In robot software, predictable timing matters more than speed.** → [[robotics/14-safety-and-real-time|14]]
6. **Switching the power off isn't automatically safe.** An arm holding something drops it. Design what "safe" means. → [[robotics/14-safety-and-real-time|14]]
7. **Most robotics work is calibration, wiring and coordinate frames.** The algorithm is usually the part that works. → [[robotics/01-what-robotics-actually-is|01]]

## Related

- [[control-theory/index|Control Theory]]: the theory of feedback loops; the [[control-theory/36-observers|Kalman filter]] used in note 11 is taught there.
- [[hardware/index|Hardware & Embedded]]: microcontrollers, motor drivers, power and sensors.
- [[machine-learning/06-computer-vision/index|Computer Vision]]: making sense of camera images.
- [[machine-learning/08-other-architectures/03-reinforcement-learning|Reinforcement Learning]]: robots that learn by trial and error.

---

## About this course

- **Size:** 14 notes, about 22,000 words, written in August 2026.
- **Where it came from:** standard reference sources, not from building a robot. Every note has a "what actually goes wrong" section, but those come from other people's experience. Read them as things to watch for.
- **Not covered yet:** full worked examples with code, grasping objects, walking robots, many robots working together, and flying or underwater robots.
