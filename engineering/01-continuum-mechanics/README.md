# Continuum Mechanics

How solids and fluids deform and flow, treated as continuous media rather than as atoms. The theory underneath structural analysis, fluid dynamics, manufacturing, biomechanics, and every physics simulation you've seen.

**~22,000 words across 13 notes.** Built August 2026. `[reference]` — see [[engineering/README|the domain note]] on what that means here, because it means something sharper in a physical field than in a software one.

> **The structural insight worth having early:** solids and fluids are the **same theory**. Identical balance laws, identical stress tensor, identical kinematics. What differs is one closure — a solid responds to *how much* you deform it, a fluid to *how fast*. That's the entire distinction, and it's why one course covers both beam bending and Navier–Stokes.

## Reading order

Notes 01–07 are the foundation and build strictly on each other. After that, 08–13 are applications you can take as needed.

**The foundation**

1. [[engineering/01-continuum-mechanics/01-what-continuum-mechanics-is|What Continuum Mechanics Is]] — **[Intermediate]** — the continuum hypothesis and where it breaks, why solids and fluids are one theory, and the three ingredients every problem is assembled from
2. [[engineering/01-continuum-mechanics/02-index-notation-and-tensors|Index Notation and Tensors]] — **[Intermediate → Advanced]** — the language. Summation convention, what a tensor actually is, invariants, and the decompositions that recur everywhere
3. [[engineering/01-continuum-mechanics/03-kinematics-of-deformation|Kinematics of Deformation]] — **[Intermediate → Advanced]** — Lagrangian vs Eulerian, the material derivative, the deformation gradient, and polar decomposition
4. [[engineering/01-continuum-mechanics/04-strain-measures|Strain Measures]] — **[Intermediate → Advanced]** — why there are several, the engineering-shear factor of two, and **why small-strain theory fails on rotation rather than strain**
5. [[engineering/01-continuum-mechanics/05-stress|Stress]] — **[Intermediate → Advanced]** — Cauchy's theorem, why symmetry is forced, principal stresses, and the three stress tensors finite deformation requires
6. [[engineering/01-continuum-mechanics/06-conservation-laws|Conservation Laws]] — **[Advanced]** — one derivation pattern used four times, and **why the system is deliberately six equations short**
7. [[engineering/01-continuum-mechanics/07-constitutive-models|Constitutive Models]] — **[Advanced]** — the missing six. Objectivity, thermodynamic admissibility, and **where all the modelling error lives**

**Applications**

8. [[engineering/01-continuum-mechanics/08-linear-elasticity|Linear Elasticity]] — **[Intermediate → Advanced]** — two constants, Navier's equations, plane stress vs plane strain, Saint-Venant, stress concentration
9. [[engineering/01-continuum-mechanics/09-beams-and-structures|Beams and Structures]] — **[Intermediate]** — Euler–Bernoulli and Timoshenko, torsion, buckling, plates and shells. The engineering you'd actually do
10. [[engineering/01-continuum-mechanics/10-finite-deformation|Finite Deformation]] — **[Advanced]** — hyperelasticity, objective rates, and what you lose when linearity goes
11. [[engineering/01-continuum-mechanics/11-viscous-fluids-and-navier-stokes|Viscous Fluids and Navier–Stokes]] — **[Advanced]** — the Reynolds number, boundary layers, and the one nonlinear term that causes turbulence
12. [[engineering/01-continuum-mechanics/12-failure-and-yield|Failure and Yield]] — **[Intermediate → Advanced]** — von Mises vs Tresca vs Rankine, and **why most real failures are fatigue**
13. [[engineering/01-continuum-mechanics/13-computational-methods-and-fem|Computational Methods and FEM]] — **[Advanced]** — how it's solved, and the failure modes that make a plausible result wrong

## The things worth carrying

If the derivations fade, these keep paying:

1. **Balance laws are physics; constitutive models are hypotheses.** The first are as certain as engineering gets; the second are chosen, empirical, and where a factor-of-three error comes from → [[engineering/01-continuum-mechanics/07-constitutive-models|07]]
2. **Small-strain theory fails on large *rotations*, not just large strains.** A cantilever deflecting 20% of its length has strains under 1% and gets visibly wrong answers → [[engineering/01-continuum-mechanics/04-strain-measures|04]]
3. **$E$ for steel is ~200 GPa regardless of grade.** If a part is too flexible, changing alloy won't help — change the geometry → [[engineering/01-continuum-mechanics/08-linear-elasticity|08]]
4. **Metals yield on the deviator only.** Hydrostatic pressure causes no plastic flow, which is why a solid steel ball survives the deep ocean → [[engineering/01-continuum-mechanics/12-failure-and-yield|12]]
5. **Depth cubed.** Beam stiffness goes as $h^3$ — the single most powerful variable in structural design → [[engineering/01-continuum-mechanics/09-beams-and-structures|09]]
6. **You cannot measure stress.** You measure strain or force and *infer* stress through a model → [[engineering/01-continuum-mechanics/05-stress|05]]
7. **Most real failures are fatigue.** Static criteria say nothing about them → [[engineering/01-continuum-mechanics/12-failure-and-yield|12]]

## Prerequisites and gaps

**You need** multivariable calculus (partial derivatives, divergence, gradient) and linear algebra (matrices, eigenvalues, orthogonality). [[ai-ml/00-foundations/03-mathematics/README|The vault's maths notes]] cover these at the level ML needs, which is a floor rather than sufficient.

**Genuine gaps in this vault** that this track needs and doesn't have:
- **Tensor calculus** beyond Cartesian coordinates — curvilinear systems, Christoffel symbols. Needed for shells
- ~~**PDE theory**~~ — **now covered** in [[foundations/numerical-methods/09-partial-differential-equations|numerical-methods/09]] (classification, finite difference/volume/element, CFL)
- ~~**Numerical methods**~~ — **now written**: [[foundations/numerical-methods/README|foundations/numerical-methods/]] (quadrature, sparse solvers, conditioning, stability)
- **Thermodynamics** — the energy equation and the second law are used here without a proper foundation

**Within the track:** no worked problems, no plasticity in depth (flow rules and return mapping get a paragraph), no composites or laminate theory, no experimental methods beyond a mention, and nothing on multiphysics coupling.

## The honest note

Software knowledge validates by running the code. **Mechanics validates against an experiment, and there isn't one here.**

That gap matters more than the equivalent gap in a software domain, because the failure mode differs: a wrong mental model in software produces a bug you eventually find, while a wrong constitutive assumption produces a number that looks entirely reasonable and is wrong by a factor of three.

Treat this as a map of the vocabulary and the structure of the arguments — enough to read a paper, follow a derivation, or notice which assumption a textbook is quietly making. Not a substitute for a course with problem sets. → [[PRIMETECHIE|Reading is not a rank.]]

**A build project would help**: writing a small 2D linear-elastic FE solver — element stiffness, assembly, boundary conditions, solve — is a few hundred lines and would remove the black box permanently. That's a genuine gap in [[build-your-own-x/README|build-your-own-x]].

## Related
- [[engineering/README|Engineering]] — the umbrella
- [[engineering/02-control-theory/README|Control Theory]] — the other track: controlling the systems this one describes
- [[hardware/README|Hardware & Embedded]] — the electronics layer beside this one
- [[robotics/README|Robotics]] — where mechanics and control meet
- [[build-your-own-x/README|build-your-own-x]] — where an FE solver would go
