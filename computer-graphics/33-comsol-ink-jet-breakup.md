---
id: b15a5174-b22e-490d-94a6-409fa1ff734d
---

# COMSOL: Modelling Ink Jet Breakup

This lesson builds a COMSOL model that predicts how an ink jet breaks into droplets.

## What this model is
<!-- bite: 17c84535-8a7a-493f-b07b-c79e724ca134 -->

COMSOL Multiphysics is software that simulates physics, such as how a fluid flows. This lesson builds the COMSOL model of a continuous ink jet breaking up into droplets, the way an inkjet printer's stream does, step by step as you would write it in the exam.

Next: the kid version, then the words you need.

## The kid version
<!-- bite: 5882963c-ca3d-49d4-ada9-b4c0f24ac4f1 -->

Turn a tap on gently and the thin stream of water breaks into drops a little way down. Surface tension — the "skin" on the water — prefers drops to a long cylinder, so any small wobble grows until the stream pinches off. An inkjet printer does this on purpose, very fast, and shakes the nozzle at a steady rhythm so every drop comes off the same size at the same place. **The computer model predicts where and how the stream breaks**, so engineers can design the nozzle without building dozens of them.

**Where the analogy stops working.** A tap stream breaks at random spots. A printer's stream is *forced* at a fixed frequency, so its breakup is regular — and the model has to be calibrated against experiments, because the shaking membrane itself isn't simulated.

## Terms used in the model
<!-- bite: e5e8f5c4-330d-4833-ab91-8dd8327351b8 -->

1. **CIJ**: The letters stand for **continuous ink jet**. This is the printing technique where a stream of ink is broken into droplets continuously; chosen droplets are charged and deflected onto the print, and the rest go to a gutter.
2. **Rayleigh–Plateau instability**: This is the tendency of a liquid cylinder, driven by surface tension, to break up when disturbed by wavelengths longer than its circumference.
3. **Breakup length**: This is the distance from the nozzle to the point where a droplet has just separated.
4. **Satellite droplet**: This is a small extra droplet that forms from the thin neck between two main droplets. Satellites hurt print quality.
## More terms used in the model
<!-- bite: b4bd1611-2738-4da4-ba67-656b8196f05e -->

5. **Level set function**: This is a smooth field $\phi$ that marks which fluid is where — for example 1 in ink and 0 in air — with the interface at the $\phi = 0.5$ contour.
6. **2D axisymmetric**: This is a model of a body of revolution drawn as one half-plane and spun about its axis, avoiding a full 3D model.
7. **Navier-slip condition**: This is a wall boundary condition with no flow through the wall, but with the shear stress proportional to the fluid's velocity along the wall, through a slip coefficient. Zero is no-slip; infinity is full slip.

## 1. Background to state first
<!-- bite: 44c078d7-ecb4-42c7-968a-90e9b7155b5d -->

- **The process.** In CIJ, ink leaves a nozzle at about **20 m/s** and is broken into droplets at **of the order of 100 kHz**, typically about **100 µm** in diameter. Chosen droplets are charged (about **1 pC**), deflected by an electric field (about **1 kV/mm**) onto the medium; uncharged droplets go to a gutter.
- **Why it breaks up: the Rayleigh–Plateau instability.** Surface tension makes a liquid cylinder unstable to disturbances longer than its circumference. **A periodic perturbation applied at the nozzle by a piezoelectric membrane is amplified along the jet until it pinches off at a regular spacing.**
- *Standard theory, not from the papers:* for an inviscid jet, the fastest-growing wavelength is about **4.5 × the jet diameter**, and the droplet diameter is then about **1.9 × the jet diameter**.
- **What the model is for:** the breakup length, the jet shape at breakup, and whether satellites form. **These drive printhead size and print quality.**

## 2. The step-by-step model build (the answer to write)
<!-- bite: f0c4954e-8acd-47f3-94ea-e25c638f5f87 -->

1. **Component: 2D axisymmetric.** The nozzle and jet are bodies of revolution, so one half-plane suffices and the 3D cost is avoided.
2. **Geometry.** Three connected parts: the **stimulation (droplet generator) chamber**, the **nozzle with its chamfer**, and a **long free-surface region downstream**, long enough to contain several formed droplets. The nozzle shape and operating point are the design variables.
3. **Physics.** Add **Laminar Flow** and the **Level Set** interface through the multiphysics coupling **Two-Phase Flow, Level Set** (*Fluid Flow > Multiphase Flow > Two-Phase Flow, Level Set > Laminar Flow*). Flow is laminar and incompressible; gravity is neglected.
## The model build, step 4: the governing equations
<!-- bite: cfbb85ea-e057-44b5-a902-92f3a9fe5f7f -->

4. **Governing equations.**
   - **Navier–Stokes** — momentum change equals pressure, viscous and surface-tension forces, with incompressibility:
     $$\rho\left(\frac{\partial \mathbf u}{\partial t} + \mathbf u\cdot\nabla\mathbf u\right) = \nabla\cdot\left[-p\mathbf I + \mu(\nabla\mathbf u + \nabla\mathbf u^T)\right] + \mathbf F,\qquad \nabla\cdot\mathbf u = 0$$
     where $\mathbf F$ includes the surface-tension force at the interface, $\sigma\kappa\delta\mathbf n$.
   - **The level set** $\phi$ marks the phases, with the interface at $\phi = 0.5$. (COMSOL's tutorials use $\phi = 1$ in ink and 0 in air; the 2023 paper uses the opposite — **state which you use.**) It is carried by the flow and kept sharp by the reinitialised conservative level-set equation:
     $$\frac{\partial\phi}{\partial t} + \mathbf u\cdot\nabla\phi = \gamma\,\nabla\cdot\left[\varepsilon_{ls}\nabla\phi - \phi(1-\phi)\frac{\nabla\phi}{|\nabla\phi|}\right]$$
   - **Properties are blended across the interface:** $\rho = \rho_{air} + (\rho_{ink} - \rho_{air})\phi$, $\mu = \mu_{air} + (\mu_{ink} - \mu_{air})\phi$.
   - **Level-set parameters:** $\gamma$ sets the amount of reinitialisation (COMSOL suggests the maximum velocity magnitude); $\varepsilon_{ls}$ sets the interface thickness and should match the mesh size. The 2023 paper uses **$\gamma = 20$ m/s** (the jet velocity) and **$\varepsilon_{ls} = 2$ µm**.
## The model build, steps 5–6: materials and boundary conditions
<!-- bite: e50c6ea1-ebfd-45e6-8412-3ae7a2a8dc1f -->

5. **Materials.** Ink density and viscosity, air density and viscosity, and the ink–air surface-tension coefficient.
6. **Boundary conditions.**
   - **Upstream (top of the chamber): a periodic pressure** $P_{in} = P_{out} + P_0 + P_1\sin(\omega t)$. The constant $P_0$ (mean pressure drop) drives the flow; **the oscillating $P_1$ at the stimulation frequency perturbs the jet and sets the breakup length.**
   - **Downstream outer boundaries:** open, at fixed pressure $P_{out}$.
   - **Axis:** axial symmetry.
   - **Walls:** no-slip is the classical choice. **Viry et al. use Navier slip** — the slip coefficient lumps together uncertainties such as machining tolerance, roughness and non-Newtonian ink behaviour, and is fitted once.
## The model build, steps 7–9: initial conditions, mesh and study
<!-- bite: 0e36a7b2-7364-4c8d-bb7b-419446fd77d8 -->

7. **Initial conditions.** Ink fills the chamber and nozzle; air fills the outside. **Compute a smooth initial level-set field first** (COMSOL's inkjet tutorial does this as a separate step), then start the transient flow from it.
8. **Mesh.** Triangular finite elements, **refined where the interface moves most** — in the 2023 paper from 10 µm down to 2 µm near the axis. Choose $\varepsilon_{ls}$ to match.
9. **Study.** Time-dependent. In the 2023 paper the maximum time step is **the pressure period ÷ 300**, with a direct solver, over about **100 jet periods (1 ms)** — solved until the solution becomes periodic.
## The model build, steps 10–12: calibrate, post-process and validate
<!-- bite: b316bb46-b077-4987-bd17-8a1083f2f375 -->

10. **Calibrate.** Fit the mean pressure drop and the slip coefficient together so the simulated mean flow rate and jet velocity match experiment. Then **sweep the perturbation amplitude $P_1$**, and compare simulated and measured breakup lengths to find the relation between piezo signal amplitude and $P_1$ (**linear for small amplitudes**).
11. **Post-process.** Plot the $\phi = 0.5$ contour and the velocity field over time. Extract the breakup length and the jet shape at pinch-off. Check for satellites. Compare with experimental snapshots.
12. **Validate and discuss.** The calibrated model matched breakup-length curves and jet-shape types for a low- and a high-viscosity ink; satellites were mostly predicted correctly, with some difference in their dynamics. **Limitations:** the piezo membrane is not modelled (so calibration is needed); rheology and roughness are lumped into the slip coefficient; and it is expensive — the 2023 model had about **620,000 degrees of freedom and took about 100 hours for 1 ms** of physical time.

## 3. Extension: charging the droplets
<!-- bite: 741817f8-ad87-4963-aad3-8c879ae9d8a6 -->

Add the **Electric Currents** interface (AC/DC module) on a **snapshot** of the breaking droplet from the flow run. Assign conductivity by phase — about **0.1 S/m in ink**, and a tiny non-zero **$10^{-15}$ S/m in air** so the stationary problem is well posed. Set the droplet at 0 V and the charge electrode at a fixed potential (**150 V** in the paper). Solve a stationary study. **The droplet's charge is the integral of the normal displacement field $\mathbf D = \varepsilon_0\varepsilon_r\mathbf E$ over its surface** (about **−1.25 pC** in the paper). The result depends on timing, so the time step must be small near pinch-off.

## 4. A short model answer for 10 marks
<!-- bite: 58416ec0-6ae5-4028-b1f7-6834d0b03ee4 -->

> Build a **2D axisymmetric** model of the nozzle and the ink–air region downstream. Couple **Laminar Flow with the Level Set method (Two-Phase Flow, Level Set)** to follow the interface ($\phi = 0.5$) through pinch-off. Drive the jet with a **periodic inlet pressure $P_0 + P_1\sin(\omega t)$**, with open fixed-pressure outer boundaries and Navier-slip (or no-slip) walls. **Mesh finely near the axis**, matching $\varepsilon_{ls}$ to the mesh and $\gamma$ to the jet velocity. Solve a **transient** study with a small fixed maximum time step for about 100 periods until the jet breaks up periodically. **Calibrate** $P_0$ and the slip coefficient to the measured flow and jet velocity, **sweep $P_1$**, and read off breakup length, jet shape and satellites to compare with experiment. Optionally couple an **Electric Currents** study to find each droplet's charge.

## Check your understanding
<!-- bite: 458224cd-8a82-4a32-bd33-6a95eaa235f4 -->

Try each one before you open the answer.

1. <!-- q: gap id="76ad0728" answers="rayleigh-plateau|rayleigh plateau|rayleigh–plateau" -->
   Fill in the gap. A liquid cylinder breaks up because surface tension makes it unstable to long-wavelength disturbances. This is the ___ instability.

   <details><summary>Answer</summary>

   The Rayleigh–Plateau instability. A periodic perturbation at the nozzle is amplified until the jet pinches off.

   </details>

2. <!-- q: mcq id="309f722f" -->
   Which COMSOL physics coupling follows the ink–air interface through pinch-off?

   - [x] Two-Phase Flow, Level Set (Laminar Flow + Level Set)
   - [ ] Electric Currents
   - [ ] Heat Transfer in Solids

   <details><summary>Answer</summary>

   Two-Phase Flow, Level Set. The interface is the φ = 0.5 contour. Electric Currents is only for the charging extension.

   </details>

3. <!-- q: mcq id="79c4c65f" -->
   What two quantities are calibrated first, and against what?

   - [x] The mean pressure drop P₀ and the slip coefficient, against the measured mean flow rate and jet velocity
   - [ ] The ink colour and the nozzle length, against print quality
   - [ ] The mesh size and the time step, against the solver time

   <details><summary>Answer</summary>

   The mean pressure drop P₀ and the slip coefficient, against the measured mean flow rate and jet velocity; then P₁ against measured breakup lengths.

   </details>

4. <!-- q: open id="132d979f" -->
   Why is a 2D axisymmetric model justified here, and when would it stop being valid?

   <details><summary>Answer</summary>

   The nozzle and jet are bodies of revolution and the flow is assumed symmetric about the axis. It stops being valid if the jet deflects or develops non-axisymmetric modes (for example, the electric deflection stage).

   </details>

5. <!-- q: open id="83888391" -->
   Why must ε_ls be matched to the mesh size?

   <details><summary>Answer</summary>

   ε_ls is the interface thickness; thinner than the elements and the interface cannot be resolved, much thicker and the interface is smeared and pinch-off timing is wrong.

   </details>

## Related
<!-- bite: 094748b3-f4d2-45a4-801d-991c4b42863d -->
- [[continuum-mechanics/13-computational-methods-and-fem|Computational methods and FEM]] — what COMSOL is solving underneath
- [[computer-graphics/29-animation-and-simulation|Animation and Simulation]] — fluids in graphics, where visual plausibility replaces accuracy
- [[computer-graphics/32-ssg-511-question-bank|Question bank]]
- [[computer-graphics/index|Computer graphics map]]

## About this lesson
<!-- bite: a7d5f0d8-64ae-415b-ad13-bcaec43cffeb -->

**Level:** Advanced. **Covers:** How to model continuous-inkjet droplet breakup in COMSOL Multiphysics: the physics (Rayleigh–Plateau instability), the step-by-step model build (two-phase laminar flow with a level set), calibration, post-processing, and the droplet-charging extension. Written as the model answer to SSG 511 exam Q3.

**Why this is in a graphics course.** It isn't really graphics — it is computational fluid dynamics, and the exam took it from a published COMSOL paper rather than the lecture notes. It is here because it is on the paper. **If you are short of time, skip Q3:** the exam asks for Q1 and any three others, and the rest are covered by notes 03–20. The physics underneath is in [[continuum-mechanics/13-computational-methods-and-fem|continuum mechanics: computational methods and FEM]].

**Sources.** The exam's first sentence is the opening line of *Modelling of Ink Jet Breakup using COMSOL Multiphysics®* (Viry, Sturma, Namy and Barbet; Simtec and Markem-Imaje; COMSOL Conference 2024). This note follows that paper, the companion 2023 paper on droplet charging (Sturma et al.), and COMSOL's application-library models *Inkjet Nozzle: Level Set Method* and *Jet Instability: Level Set*. **Standard theory not taken from those sources is marked as such.** `[reference]`
