# Beams and Structures

**[Intermediate]** — Reducing 3D elasticity to 1D and 2D by exploiting geometry. Where continuum mechanics becomes the engineering you'd actually do.

## The idea

A beam is a 3D elastic body. Solving Navier's equations for it is possible and unnecessary — if one dimension dominates, a kinematic assumption collapses the problem.

```
3D elasticity                    →  6 stress components, 3 PDEs
  ↓ one dimension dominates
beam / rod (1D)                  →  one ODE, closed-form answers
  ↓ two dimensions dominate
plate / shell (2D)               →  one PDE in two variables
```

**The assumption is always kinematic** — you assert something about how cross-sections deform, and the mechanics follows. That's why these theories are named after their assumptions.

## Euler–Bernoulli beam theory

**The assumption:** plane sections remain plane **and perpendicular to the neutral axis** after bending. No shear deformation.

Everything follows from that one sentence.

If sections stay plane and perpendicular, axial strain varies linearly through the depth:

$$\varepsilon_{xx} = -\frac{y}{R} = -y\,\frac{d^2w}{dx^2}$$

Apply Hooke, integrate the moment over the section:

$$\boxed{\sigma_{xx} = \frac{My}{I} \qquad\qquad EI\,\frac{d^4w}{dx^4} = q(x)}$$

The **flexure formula** and the **beam equation**. Two results that carry an enormous amount of engineering.

**Reading them:**

- **Stress is linear in $y$**: maximum at the outer fibres, **zero at the neutral axis**. The material at the centre of a beam carries almost no bending stress
- **That's why I-beams exist.** Put the material where $y$ is large. An I-beam and a solid rectangle of equal mass differ in $I$ by a large factor
- **$I$ scales as depth cubed** for a rectangle ($I = bh^3/12$). Doubling the depth gives eight times the bending stiffness for twice the material. **Depth is the single most powerful variable in beam design**
- **Stiffness is $EI$**, so — from [[engineering/01-continuum-mechanics/08-linear-elasticity|note 08]] — if a beam is too flexible, changing steel grade won't help. Change $I$

Standard results worth having memorised:

| Case | Max deflection | Max moment |
|---|---|---|
| Cantilever, end load $P$ | $PL^3/3EI$ | $PL$ |
| Cantilever, UDL $q$ | $qL^4/8EI$ | $qL^2/2$ |
| Simply supported, centre load | $PL^3/48EI$ | $PL/4$ |
| Simply supported, UDL | $5qL^4/384EI$ | $qL^2/8$ |

**Deflection scales as $L^3$ or $L^4$.** Doubling a span makes a cantilever 8–16× more flexible. Span dominates everything.

## Timoshenko beam theory

**Relaxes one assumption:** sections stay plane but **need not remain perpendicular**. Shear deformation is included.

This adds a term and matters when:

- **The beam is short and deep** — span-to-depth below about 10
- **The material has low $G/E$** — composites, sandwich panels, where shear compliance is significant
- **You care about higher vibration modes** — Euler–Bernoulli overestimates natural frequencies badly at high modes

For a slender steel beam the difference is a few percent. For a stubby composite beam it can be a factor of two. **Most FE beam elements are Timoshenko** because it degrades gracefully to Euler–Bernoulli as slenderness increases, while the reverse isn't true.

The catch is **shear locking** — naive Timoshenko elements go artificially stiff as they get thin, for the same reason volumetric locking happens in nearly-incompressible elasticity. Reduced integration fixes it. → [[engineering/01-continuum-mechanics/13-computational-methods-and-fem|FEM]]

## Torsion

**Circular shafts** behave beautifully — cross-sections rotate rigidly and stay plane:

$$\tau = \frac{Tr}{J} \qquad\qquad \theta = \frac{TL}{GJ}$$

with $J = \pi d^4/32$ for a solid circle. Shear stress is maximum at the surface, zero at the centre — which is why hollow shafts are efficient.

**Non-circular sections warp.** Sections do *not* remain plane, and the simple formula fails completely. Saint-Venant torsion theory handles it via a warping function and a Prandtl stress function, and the results are much less pleasant.

**The practical consequence is large:** an **open** thin-walled section (I-beam, channel, angle) is catastrophically weaker in torsion than a **closed** one (tube, box) of the same material. Orders of magnitude, not percentages.

That's why a car chassis is a box, why a bicycle frame is tubes, and why you should never carry torsion through an open section if you can avoid it. A slit cut lengthwise along a tube destroys most of its torsional stiffness — a genuinely dramatic demonstration.

## Buckling

The failure mode that isn't about strength.

**Euler's critical load:**

$$P_{cr} = \frac{\pi^2 EI}{(KL)^2}$$

$K$ is the effective-length factor: 1.0 pinned–pinned, 0.5 fixed–fixed, 2.0 fixed–free (a flagpole).

**Buckling is an instability, not a stress failure.** A slender column can buckle at a stress far below yield, and the material is entirely undamaged at the moment of collapse. The structure simply finds a lower-energy configuration.

**Two things this changes about how you think:**

**Strength doesn't help.** $P_{cr}$ contains $E$ and $I$ — not yield stress. High-strength steel buckles at exactly the same load as mild steel of the same geometry. **Geometry and stiffness are the only levers.**

**It's the first genuinely nonlinear phenomenon here.** Below $P_{cr}$ the straight configuration is stable; above it, it isn't. That's a **bifurcation**, and it's where linear elasticity stops being sufficient. → [[engineering/01-continuum-mechanics/10-finite-deformation|Finite Deformation]]

Real columns have imperfections, so they don't reach the Euler load — they deflect progressively from the start. Design codes use empirical curves (Perry–Robertson, AISC) that blend Euler buckling with yielding, and the transition between the two failure modes is governed by **slenderness ratio** $KL/r$.

Buckling appears in many forms beyond columns: plate buckling (a thin panel in compression), lateral–torsional buckling (a deep beam tipping sideways), and shell buckling (a can crushing) — the last being notoriously imperfection-sensitive, with real strengths sometimes a fraction of the theoretical value.

## Plates and shells

Two-dimensional reductions of the same idea.

**Kirchhoff–Love plate theory** — the plate analogue of Euler–Bernoulli. Normals to the mid-surface stay straight and perpendicular. Thin plates:

$$D\,\nabla^4 w = q \qquad\qquad D = \frac{Eh^3}{12(1-\nu^2)}$$

$D$ is the **flexural rigidity**, and note $h^3$ again — thickness dominates. The $(1-\nu^2)$ is the plane-stress correction from [[engineering/01-continuum-mechanics/08-linear-elasticity|note 08]].

**Mindlin–Reissner plate theory** includes transverse shear — the plate analogue of Timoshenko. Needed for thick plates and sandwich panels.

**Shells** are curved, and curvature changes the mechanics qualitatively:

> A flat plate carries transverse load by **bending**. A curved shell carries it primarily by **membrane action** — in-plane tension and compression.

Membrane action is vastly more efficient, because the whole thickness is stressed uniformly rather than linearly with a useless neutral axis. That's why an eggshell is strong, why domes and arches work, and why a pressure vessel is a cylinder with hemispherical ends.

The **hoop stress** result for a thin pressure vessel is worth having:

$$\sigma_{hoop} = \frac{pr}{t} \qquad \sigma_{axial} = \frac{pr}{2t}$$

**Hoop stress is twice axial**, which is why a cylindrical pressure vessel splits along its length rather than around its circumference — and why sausages split lengthwise when you cook them.

## Structural analysis

Beams assemble into structures, and two ideas dominate:

**Statically determinate** — reactions and internal forces follow from equilibrium alone. A simply supported beam, a three-hinged arch, most trusses.

**Statically indeterminate** — more unknowns than equilibrium equations. You need compatibility (deflections must match) to close the system. A fixed–fixed beam, a continuous beam over several supports, most real frames.

**Indeterminate structures are stiffer, redundant, and safer** — losing one member doesn't necessarily cause collapse. They also develop stress from thermal expansion and support settlement, which determinate structures don't, because there's nothing to resist the free movement.

That trade — redundancy versus self-stress — is a genuine design decision, and it's why bridge expansion joints exist.

**Methods:** the force (flexibility) method and the displacement (stiffness) method. **The stiffness method generalises directly into the finite element method**, which is why it won: assemble element stiffness matrices into a global system, apply boundary conditions, solve $\mathbf{K}\mathbf{u} = \mathbf{f}$. → [[engineering/01-continuum-mechanics/13-computational-methods-and-fem|FEM]]

## When these theories fail

Worth knowing the boundaries, because the formulas will happily give you a number regardless:

- **Short, deep beams** — shear matters; use Timoshenko or 3D
- **Near supports and point loads** — Saint-Venant's principle doesn't apply; the local stress field is genuinely different
- **Holes, notches, sudden section changes** — stress concentration is invisible to beam theory → [[engineering/01-continuum-mechanics/08-linear-elasticity|note 08]]
- **Large deflection** — beam theory linearises the curvature. A fishing rod bent through 90° needs the elastica solution
- **Open thin-walled sections in torsion** — warping is significant and simple torsion is wrong
- **Composite and sandwich construction** — layered stiffness needs classical laminate theory

> **These theories are how engineering was done before computers, and they remain how you sanity-check a computer.** A finite element result that disagrees with $PL^3/3EI$ by a factor of ten means one of you is wrong, and it's usually the model — a missed constraint, wrong units, or a load applied in the wrong direction. **Keep the hand calculation.**

---

## Related
- [[engineering/01-continuum-mechanics/08-linear-elasticity|Linear Elasticity]] — what these reduce from
- [[engineering/01-continuum-mechanics/13-computational-methods-and-fem|FEM]] — the general method these preceded
- [[engineering/01-continuum-mechanics/12-failure-and-yield|Failure and Yield]] — whether the stress is acceptable
- [[hardware/README|Hardware & Embedded]] — where these get built
- [[engineering/01-continuum-mechanics/README|Continuum mechanics map]]
