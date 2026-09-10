# Continuum Mechanics — Projects

_From the vault's bluntest `[reference]` label: **this material validates against an experiment, not a compiler.** These projects are the cheapest available substitute — simulate it, then check the simulation against something physical you can measure._

Difficulty: 🟢 starter (hours–days) · 🟡 intermediate (a week or two) · 🔴 ambitious / portfolio-grade. ⭐ = highest signal.

**Python + NumPy/SciPy + Matplotlib is the whole toolchain.** Nothing here needs licensed software.

## Projects

- 🟢 **Verify a beam by hand and by code** — cantilever deflection analytically, then numerically. **Done when:** they agree to several digits, and you know which assumptions you made. Exercises: [[continuum-mechanics/09-beams-and-structures|beams]].

- 🟡 ⭐ **Write a 1D finite element solver** — bar under axial load: shape functions, assembly, boundary conditions, solve. **Done when:** it matches the analytical solution, and refining the mesh converges. **FEM stops being a black box the moment you assemble the stiffness matrix yourself.** Exercises: [[continuum-mechanics/13-computational-methods-and-fem|FEM]].

- 🟡 **2D heat or stress on a plate** — extend the solver, or use FEniCS/scikit-fem, and validate against a known case. **Done when:** your answer matches a textbook benchmark.

- 🔴 **A CFD toy** — lid-driven cavity flow by finite differences. **Done when:** your streamlines match the published benchmark at the same Reynolds number. Exercises: [[continuum-mechanics/11-viscous-fluids-and-navier-stokes|Navier-Stokes]].

## If you only do one

**Write the 1D finite element solver.** FEM stops being a black box the moment you assemble the stiffness matrix yourself.

## Related

- [[continuum-mechanics/index|continuum mechanics]] — the course these exercise
- [[control-theory/projects|control theory projects]] — the other half of the old engineering folder
- [[mathematics/07-applied-and-computational/01-numerical-methods/index|numerical methods]] — the solvers under all of this
- [[robotics/index|robotics]] · [[hardware/index|hardware]] — where it becomes physical
- [[project-ideas|Project Ideas]] — the vault-wide index
