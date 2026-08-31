# Engineering — Projects

*26 notes, ~41,000 words, and the vault's bluntest `[reference]` label: **this material validates against an experiment, not a compiler.** These projects are the cheapest available substitute — simulate it, then check the simulation against something physical you can measure.*

Difficulty: 🟢 starter (hours–days) · 🟡 intermediate (a week or two) · 🔴 ambitious / portfolio-grade. ⭐ = highest signal.

**Python + NumPy/SciPy + Matplotlib is the whole toolchain.** Nothing here needs licensed software.

## Control theory

- 🟢 ⭐ **Tune a PID on a simulated plant** — a first-order-plus-dead-time model, then tune by Ziegler–Nichols and by hand. Plot step responses for each gain change. **Done when:** you can produce overshoot, sluggishness and instability *on demand* and explain which term caused each. Exercises: [[engineering/02-control-theory/04-pid-control|PID]].

- 🟢 **Draw the plots yourself** — root locus, Bode and Nyquist for the same system, in code. **Done when:** you can predict from the Bode plot what the step response will look like, then confirm it. Exercises: [[engineering/02-control-theory/06-frequency-response|Bode]].

- 🟡 ⭐ **Balance a real thing** — a physical inverted pendulum or a reaction wheel with a cheap microcontroller and an IMU. **Done when:** it balances, and your measured settling time is within sight of your simulation's. **This is the rep that closes the gap this folder names** — theory meeting a real actuator with real noise and real latency. Ties to [[hardware/README|hardware]] and [[robotics/README|robotics]].

- 🟡 **A Kalman filter on noisy real data** — log accelerometer data from a phone, fuse it, and compare against a complementary filter. **Done when:** you can show the filter tracking through a period where the raw signal is useless. Exercises: [[engineering/02-control-theory/10-observers-and-kalman|observers]].

- 🔴 **MPC on a constrained system** — model predictive control with actuator limits, against the same plant you PID-tuned. **Done when:** you can show MPC respecting a constraint that PID violates.

## Continuum mechanics

- 🟢 **Verify a beam by hand and by code** — cantilever deflection analytically, then numerically. **Done when:** they agree to several digits, and you know which assumptions you made. Exercises: [[engineering/01-continuum-mechanics/09-beams-and-structures|beams]].

- 🟡 ⭐ **Write a 1D finite element solver** — bar under axial load: shape functions, assembly, boundary conditions, solve. **Done when:** it matches the analytical solution, and refining the mesh converges. **FEM stops being a black box the moment you assemble the stiffness matrix yourself.** Exercises: [[engineering/01-continuum-mechanics/13-computational-methods-and-fem|FEM]].

- 🟡 **2D heat or stress on a plate** — extend the solver, or use FEniCS/scikit-fem, and validate against a known case. **Done when:** your answer matches a textbook benchmark.

- 🔴 **A CFD toy** — lid-driven cavity flow by finite differences. **Done when:** your streamlines match the published benchmark at the same Reynolds number. Exercises: [[engineering/01-continuum-mechanics/11-viscous-fluids-and-navier-stokes|Navier-Stokes]].

## If you only do one

**Balance a physical inverted pendulum.** It's the only project here that validates against reality rather than against another equation — which is exactly the gap [[engineering/README|the folder's own README]] admits to.

## Related
- [[engineering/README|the engineering courses]]
- [[foundations/numerical-methods/README|numerical methods]] — the solvers under all of this
- [[robotics/README|robotics]] · [[hardware/README|hardware]] — where it becomes physical
- [[project-ideas|Project Ideas]] — the vault-wide index
