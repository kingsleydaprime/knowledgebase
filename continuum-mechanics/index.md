# Continuum Mechanics

## What continuum mechanics is

**Continuum mechanics is the maths of how materials stretch, bend, break and flow: solids like steel and bone, and fluids like water and air.**

Everything is made of atoms, but a spoonful of water has around 10²³ of them, far too many to track one by one. So engineers pretend the material is smooth and continuous, like jelly with no gaps, and use calculus to describe how it moves when pushed or pulled. That one simplification works astonishingly well, and it's the theory behind designing bridges and aircraft, predicting how blood flows, shaping metal in factories, and every physics simulation in films and games.

A surprising fact makes the subject tidy: **solids and fluids follow the same laws.** The only difference is how they respond. A solid resists *how far* you've deformed it (bend a ruler and it springs back), while a fluid resists *how fast* you're deforming it (stir honey slowly and it's easy; quickly and it fights you).

## What you'll be able to do

By the end you will be able to:
- describe how a material deforms, and measure stretching and twisting properly;
- describe the forces inside a material (stress), and why you can never measure stress directly;
- write the basic laws every material obeys: conservation of mass, momentum and energy;
- calculate how beams bend and twist, and when columns buckle;
- explain how fluids flow, and where turbulence comes from;
- predict when a material will fail, including from repeated loading (fatigue);
- explain how simulation software solves these problems, and how its answers can mislead.

## Where to start

**Before you start:** [[mathematics/06-calculus/04-calculus-3/01-partial-derivatives|multivariable calculus]] and [[mathematics/04-linear-algebra/index|linear algebra]], especially matrices and eigenvalues. This is a university engineering subject, and it's maths-heavy.

**Want a gentler start?** [[continuum-mechanics/01-intro|Fundamentals of Continuum Mechanics]] introduces the core idea with less notation. Then begin the numbered course.

Notes 01–07 are the foundation and build strictly on each other. Notes 08–13 are applications you can read as needed.

### The foundation

1. [[continuum-mechanics/01-what-continuum-mechanics-is|What Continuum Mechanics Is]]: treating materials as smooth, when that breaks down, and why solids and fluids are one theory.
2. [[continuum-mechanics/02-index-notation-and-tensors|Index Notation and Tensors]]: the shorthand the subject is written in, and what a tensor is (a way of describing quantities that change with direction, like stress).
3. [[continuum-mechanics/03-kinematics-of-deformation|Kinematics of Deformation]]: describing how every point of a material moves, by following the material or by watching fixed points in space.
4. [[continuum-mechanics/04-strain-measures|Strain Measures]]: measuring how much a material is stretched or twisted, and why the simple measure fails when things rotate.
5. [[continuum-mechanics/05-stress|Stress]]: the forces inside a material, and the directions where they are largest.
6. [[continuum-mechanics/06-conservation-laws|Conservation Laws]]: the laws every material obeys, and why they're deliberately not enough on their own.
7. [[continuum-mechanics/07-constitutive-models|Constitutive Models]]: the missing piece: how a particular material responds. This is where most of the uncertainty lives.

### Applications

8. [[continuum-mechanics/08-linear-elasticity|Linear Elasticity]]: materials that spring back, like steel under normal loads, and why stress gathers around holes and corners.
9. [[continuum-mechanics/09-beams-and-structures|Beams and Structures]]: bending, twisting and buckling. The engineering you'd actually do.
10. [[continuum-mechanics/10-finite-deformation|Finite Deformation]]: large stretches, like rubber, where the simple methods stop working.
11. [[continuum-mechanics/11-viscous-fluids-and-navier-stokes|Viscous Fluids and Navier–Stokes]]: the equations of fluid flow, the thin layer next to surfaces, and where turbulence comes from.
12. [[continuum-mechanics/12-failure-and-yield|Failure and Yield]]: predicting when a material gives way, and why most real failures come from repeated loading.
13. [[continuum-mechanics/13-computational-methods-and-fem|Computational Methods and FEM]]: how simulation software solves these problems, and how a believable result can still be wrong.

## Practice

- [[continuum-mechanics/projects|Projects]]: hands-on tasks with a clear "done when".

## Key ideas to remember

1. **The laws every material obeys are certain; the model of a particular material is a guess.** That's where large errors come from. → [[continuum-mechanics/07-constitutive-models|07]]
2. **The simple stretching formulas break when things rotate a lot,** even if they barely stretch. → [[continuum-mechanics/04-strain-measures|04]]
3. **All steel is about equally stiff, whatever the grade.** If a part bends too much, change its shape, not its alloy. → [[continuum-mechanics/08-linear-elasticity|08]]
4. **Make a beam twice as deep and it gets eight times stiffer.** Depth is the most powerful choice in structural design. → [[continuum-mechanics/09-beams-and-structures|09]]
5. **You can't measure stress directly.** You measure stretch or force and work stress out through a model. → [[continuum-mechanics/05-stress|05]]
6. **Most real failures come from repeated loading (fatigue),** which a one-off strength check doesn't catch. → [[continuum-mechanics/12-failure-and-yield|12]]

## Related

- [[mathematics/07-applied-and-computational/01-numerical-methods/index|Numerical Methods]]: how the equations are solved on a computer.
- [[robotics/index|Robotics]]: flexible structures and soft robots.
- [[computer-graphics/index|Computer Graphics]]: simulating cloth, jelly and water.

---

## About this course

- **Size:** 13 notes, about 22,000 words, written in August 2026.
- **Where it came from:** reference sources, not engineering practice. In a physical field that matters more than in software: a believable-looking result can still be wrong.
- **Not covered yet:** tensor calculus in curved coordinates (needed for shells).
