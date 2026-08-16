# Engineering

The physical half of the vault. Mechanics of continuous media, control of dynamic systems, and eventually the rest of what a systems engineering degree covers.

Everything else here — software, infrastructure, security — assumes a working machine and reasons about information. **This domain reasons about matter, force and time**, where the constraints aren't chosen by a language designer and the feedback loop involves a multimeter or a load cell rather than a stack trace.

**Structure:** numbered tracks under one umbrella, so it can grow without proliferating top-level folders.

## Tracks

1. [[engineering/01-continuum-mechanics/README|01-continuum-mechanics/]] — **[Advanced]** — how solids and fluids deform and flow, treated as continuous media. Tensors, strain, stress, the conservation laws, constitutive models, elasticity, Navier–Stokes, failure, and an entry into FEM
2. [[engineering/02-control-theory/README|02-control-theory/]] — **[Intermediate → Advanced]** — making a system behave despite a wrong model and real disturbances. Transfer functions, PID and how to actually tune one, stability, root locus, Bode and Nyquist, state space, observers and Kalman, LQR and MPC, digital implementation, and an entry into nonlinear control

**Later, if they earn their place:** thermodynamics and heat transfer, statics and dynamics, materials science, fluid mechanics as its own track, signals and systems.

## Where this connects

| | |
|---|---|
| [[hardware/README\|hardware/]] | the electronics layer — this is the mechanical one |
| [[robotics/README\|robotics/]] | draws on `02-control-theory` for the whole control half; its notes 07–08 carry the Jacobians and manipulator dynamics |
| [[ai-ml/00-foundations/03-mathematics/README\|the maths notes]] | linear algebra and calculus, at the level ML needs. This domain needs more — tensor calculus and PDEs |
| [[foundations/numerical-methods/README\|numerical methods]] | **now written** — quadrature, sparse solvers, ODE/PDE discretisation, stability. FEM and CFD both sit on it |

## The honest note

`[reference]` throughout, and more sharply than elsewhere in this vault.

Software knowledge you can validate by running the code. **Mechanics you validate against an experiment, and there isn't one here.** A model that predicts a beam deflection is a claim about the world, and nothing in these notes has been checked against a strain gauge.

That gap matters more than the equivalent gap in a software domain, because the failure mode is different: a wrong mental model in software produces a bug you eventually find, while a wrong constitutive assumption produces a number that looks entirely reasonable and is wrong by a factor of three.

Treat these as a map of the vocabulary and the structure of the arguments — enough to read a paper, follow a derivation, or know which assumption a textbook is quietly making — not as a substitute for a course with problem sets. → [[PRIMETECHIE|Reading is not a rank.]]

## Related
- [[hardware/README|Hardware & Embedded]] — the layer this sits beside
- [[robotics/README|Robotics]] — where mechanics and control meet
- [[research/README|Research]] — how to read the papers this field is written in
- [[BUILD-PLAN|Build Plan]]
