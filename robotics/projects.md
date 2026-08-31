# Robotics — Projects

*14 notes, ~23,000 words, and the README is blunt that **nothing here has been validated on hardware.** These projects exist to change that — and simulation counts, because Gazebo has real dynamics even if it has no real friction.*

Difficulty: 🟢 starter (hours–days) · 🟡 intermediate (a week or two) · 🔴 ambitious / portfolio-grade. ⭐ = highest signal.

## The ladder

- 🟢 **Make one motor go exactly where you tell it** — a servo or a stepper with an encoder, commanded to a position and holding it. Then disturb it by hand and watch it correct. That's a closed loop, and it's the entire subject in miniature.
- 🟡 ⭐ **Tune a PID by hand, and write down what each term did** — a line follower or a self-balancing two-wheeler. Start with P only and watch it oscillate; add D and watch it stop; add I and watch the steady-state error close. **Tuning one loop badly on real hardware teaches more than any amount of control theory reading** — and it's the honest prerequisite for trusting a word of [[engineering/02-control-theory/04-pid-control|the PID note]].
- 🟡 **Sensor fusion on something that moves** — combine an accelerometer and a gyro into one angle estimate with a complementary filter, and demonstrate why neither alone is usable (one drifts, one is noisy). The intuition Kalman filters formalise.
- 🔴 **Teleoperation with a latency budget** — drive something remotely and measure the end-to-end delay, then make it degrade safely when the link drops rather than continuing at the last command. Joins [[foundations/networking/15-network-performance|latency]] to a machine that can hurt someone.
- 🔴 **A robot that maps a room** — odometry plus a range sensor into a 2D occupancy map, and an honest account of how far it drifts. The entry point to [[robotics/12-localisation-and-slam|SLAM]], and the project that turns "odometry drifts without bound" from a sentence you read into a number you measured.

**If you do one:** the PID tuning project. It's cheap, it fits on a desk, and it's the difference between having read [[engineering/02-control-theory/04-pid-control|the PID note]] and having earned it.


## If you only do one

**Get something moving in ROS 2 + Gazebo.** Simulation removes the hardware cost while keeping the coordinate frames, the timing and the tuning — which is where the actual learning is.


## Related

- [[robotics/README|the robotics course]]
- [[engineering/projects|engineering projects]] — the control theory under this
- [[project-ideas|Project Ideas]] — the vault-wide index
