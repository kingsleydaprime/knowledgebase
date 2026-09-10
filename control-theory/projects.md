# Control Theory — Projects

_From the vault's bluntest `[reference]` label: **this material validates against an experiment, not a compiler.** These projects are the cheapest available substitute — simulate it, then check the simulation against something physical you can measure._

Difficulty: 🟢 starter (hours–days) · 🟡 intermediate (a week or two) · 🔴 ambitious / portfolio-grade. ⭐ = highest signal.

**Python + NumPy/SciPy + Matplotlib is the whole toolchain.** Nothing here needs licensed software.

## Projects

- 🟢 ⭐ **Tune a PID on a simulated plant** — a first-order-plus-dead-time model, then tune by Ziegler–Nichols and by hand. Plot step responses for each gain change. **Done when:** you can produce overshoot, sluggishness and instability _on demand_ and explain which term caused each. Exercises: [[control-theory/04-pid-control|PID]].

- 🟢 **Draw the plots yourself** — root locus, Bode and Nyquist for the same system, in code. **Done when:** you can predict from the Bode plot what the step response will look like, then confirm it. Exercises: [[control-theory/06-frequency-response|Bode]].

- 🟡 ⭐ **Balance a real thing** — a physical inverted pendulum or a reaction wheel with a cheap microcontroller and an IMU. **Done when:** it balances, and your measured settling time is within sight of your simulation's. **This is the rep that closes the gap this folder names** — theory meeting a real actuator with real noise and real latency. Ties to [[hardware/index|hardware]] and [[robotics/index|robotics]].

- 🟡 **A Kalman filter on noisy real data** — log accelerometer data from a phone, fuse it, and compare against a complementary filter. **Done when:** you can show the filter tracking through a period where the raw signal is useless. Exercises: [[control-theory/10-observers-and-kalman|observers]].

- 🔴 **MPC on a constrained system** — model predictive control with actuator limits, against the same plant you PID-tuned. **Done when:** you can show MPC respecting a constraint that PID violates.

## If you only do one

**Balance a physical inverted pendulum.** It is the only project here that validates against reality rather than against another equation.

## Related

- [[control-theory/index|control theory]] — the course these exercise
- [[continuum-mechanics/projects|continuum mechanics projects]] — the other half of the old engineering folder
- [[mathematics/07-applied-and-computational/01-numerical-methods/index|numerical methods]] — the solvers under all of this
- [[robotics/index|robotics]] · [[hardware/index|hardware]] — where it becomes physical
- [[project-ideas|Project Ideas]] — the vault-wide index
