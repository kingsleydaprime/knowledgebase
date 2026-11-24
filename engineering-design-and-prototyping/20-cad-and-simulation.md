---
id: ec48b8cd-11e5-441c-8e86-6e7996aa0184
---

# CAD and Simulation

CAD builds an exact digital model of a design, and simulation tests that model on the computer before any metal is cut.

## Before you start
<!-- bite: ae67fa3b-928f-47ba-8692-8c42c7ec4aca -->

You should know concept refinement ([[engineering-design-and-prototyping/14-concept-refinement|14 — Concept Refinement]]) and the material properties from [[engineering-design-and-prototyping/18-considerations-of-good-design-2|18 — Considerations of Good Design 2]].

After this lesson you will be able to:

1. explain parametric, feature-based modelling and design intent;
2. describe the steps of a finite element analysis and read its result against a factor of safety;
3. say which kind of simulation answers which question, and why simulation never fully replaces testing.

## What CAD and simulation are
<!-- bite: 0f26c76a-ae42-4ee0-a602-b83abba95584 -->

**Computer-aided design (CAD)** is building the design as an exact digital model: every dimension, hole and fillet, and how the parts fit together. **Simulation**, also called **computer-aided engineering (CAE)**, uses that model to predict how the design will behave: where it bends, how hot it gets, how air flows around it.

Together they are a **virtual prototype**. Changing a model costs minutes; changing a steel part costs days and money. So the detailed design phase starts here, and the drawings of lesson 21 are produced from this model. Common tools: SolidWorks, Fusion 360, Onshape, CATIA, Creo and the free FreeCAD for CAD; ANSYS, Abaqus and the simulation tools built into the CAD packages for CAE.

## Parametric, feature-based modelling
<!-- bite: a04257ac-253e-4981-a42b-71dbac2b0604 -->

Most mechanical CAD is **parametric** and **feature-based**:

1. **Sketch:** draw a 2D profile on a plane, such as a rectangle for a bracket.
2. **Constrain:** add dimensions and rules: 80 mm wide, these two lines parallel, this hole centred.
3. **Feature:** turn the sketch into 3D with an operation: **extrude** (push it out), **revolve** (spin it round an axis), **cut**, **fillet** (round an edge), **shell** (hollow it out), **pattern** (repeat a hole).
4. **History tree:** the features are stored in order, so you can go back and change a dimension, and every later feature updates.

That last point is the power of parametric modelling: change the bracket's thickness from 4 mm to 5 mm, and the holes, fillets and the drawing follow.

**Design intent** is building the model so it changes the way the designer means. If the hole should always stay in the centre, constrain it to the centre, not 40 mm from the edge; then when the bracket grows, the hole stays centred.

## Assemblies and outputs
<!-- bite: c63b11df-f80c-4eba-9c77-06b436d1a639 -->

An **assembly** puts parts together with **mates**: this face touches that face, these holes line up. The CAD tool can then check for **interference** (parts overlapping) and move mechanisms to check they don't collide.

From one model you get many outputs:

1. **Engineering drawings** for the factory (lesson 21).
2. **STL files** for 3D printing (lesson 26).
3. **CAM toolpaths** for CNC machining.
4. **Mass, centre of gravity** and a **bill of materials**.
5. **Renders** for marketing and design reviews.

## Simulation: which tool for which question
<!-- bite: 1c180762-061a-47dd-9487-9237bf81f93f -->

| Question | Simulation |
| --- | --- |
| Will the part break or bend too much? | Structural analysis by **finite element analysis (FEA)** |
| Will it overheat? | Thermal analysis |
| How do air or water flow around or through it? | **Computational fluid dynamics (CFD)** |
| Do the moving parts collide or reach? | Motion (kinematic) simulation |
| Will it survive repeated loading? | Fatigue analysis |
| Will it vibrate at a dangerous frequency? | Modal (frequency) analysis |

## How finite element analysis works
<!-- bite: 271ee976-a66e-4395-b88e-a51f772169b9 -->

FEA splits the part into thousands of small pieces called **elements**, joined at **nodes**: the **mesh**. It solves simple equations for each element and combines them to predict the stress and deflection of the whole part.

The steps:

1. **Geometry:** the CAD model, simplified (small cosmetic fillets removed).
2. **Material:** Young's modulus, Poisson's ratio, yield strength.
3. **Mesh:** generate the elements, finer where stress changes quickly, such as round holes and sharp corners.
4. **Boundary conditions:** where the part is held fixed, such as bolt holes.
5. **Loads:** forces, pressures, gravity.
6. **Solve.**
7. **Check the results:** the peak stress, the deflection, and whether they make sense.

## From stress to a factor of safety
<!-- bite: a592425f-5709-4345-9870-78e184e7fdce -->

Then compare the peak stress with the material's strength to get a **factor of safety** (lesson 23). A bracket with a peak stress of 120 MPa, in steel with a yield strength of 250 MPa, has a factor of safety of 250 ÷ 120 ≈ 2.1.

## Trusting a simulation
<!-- bite: 4e673aa6-0157-4fb5-b061-57dcf73f23ee -->

A simulation is only as good as its inputs: garbage in, garbage out.

1. **Wrong boundary conditions** are the most common error. Fixing a face that really moves makes the part look far stronger than it is.
2. **Mesh convergence:** refine the mesh and solve again. If the peak stress keeps changing, the answer isn't trustworthy yet; when it settles, it is converged.
3. **Sanity check by hand:** a simple beam formula should give the same order of answer.
4. **Validate with a test.** Simulation guides design and cuts the number of physical prototypes, but critical parts are still tested for real (lesson 30).

## Common pitfalls
<!-- bite: 6c8144ec-33ff-4a55-af44-567bdaf38513 -->

1. **Dimensioning from the wrong reference.** The model then changes in ways you didn't intend; build in design intent.
2. **Believing colourful results.** A red spot in FEA may be a mesh artefact at a sharp corner, or a real problem. Check convergence.
3. **Fixing everything.** Boundary conditions must match how the part is really held.
4. **Skipping the physical test** for safety-critical parts.

The CAD model is the master. Next lesson turns it into the engineering drawings a factory works from, and designs it so it is easy to make and assemble.

## Check your understanding
<!-- bite: 01e1982d-734c-468a-87b6-9053b5513617 -->

Try each one before you open the answer.

1. <!-- q: exact id="02b53470" answer="2.083333" sigfigs="2" -->
   An FEA of a steel bracket shows a peak stress of 120 MPa. The steel's yield strength is 250 MPa. What is the factor of safety?

   <details><summary>Answer</summary>

   About 2.1: yield strength ÷ peak stress = 250 ÷ 120.

   </details>

2. <!-- q: exact id="f436a955" answer="2.5" -->
   A simulation gives an aluminium arm a peak stress of 110 MPa. The aluminium's yield strength is 275 MPa. What is the factor of safety?

   <details><summary>Answer</summary>

   2.5: 275 ÷ 110.

   </details>

3. <!-- q: mcq id="48e44f4a" -->
   A team wants to know how air flows through a laptop's cooling fan and vents. Which simulation should they use?

   - [ ] Finite element structural analysis
   - [x] Computational fluid dynamics (CFD)
   - [ ] Motion simulation
   - [ ] Modal analysis

   <details><summary>Answer</summary>

   CFD, which predicts how fluids such as air flow. A thermal analysis would often be run alongside it.

   </details>

4. <!-- q: mcq id="92ac4d48" -->
   An engineer refines an FEA mesh four times. The peak stress comes out as 96, 108, 117 and 118 MPa. What does this show?

   - [ ] The model is wrong, because the answers differ
   - [x] The result is converging, at about 118 MPa
   - [ ] The coarsest mesh is the most accurate
   - [ ] Mesh size doesn't affect the answer

   <details><summary>Answer</summary>

   It is converging: the change gets smaller each time (12, 9, then 1 MPa), so about 118 MPa can be trusted. A coarse mesh tends to underestimate peak stress.

   </details>

5. <!-- q: open id="503c62fc" -->
   A designer models a plate with a hole placed 40 mm from the left edge, though the hole is meant to stay in the middle. The plate is later widened from 80 mm to 120 mm. What goes wrong, and what is the principle?

   <details><summary>Answer</summary>

   The hole stays 40 mm from the left edge, so it is no longer centred. The principle is design intent: constrain the hole to the centre of the plate, so the model changes the way the designer means when dimensions change.

   </details>

6. <!-- q: open id="13ee8611" -->
   An FEA says a bike pedal crank is safe, but it cracked in the first road test. Give two likely reasons.

   <details><summary>Answer</summary>

   Any two: the boundary conditions were wrong (it was fixed in a way that made it look stiffer); the load was wrong or missed the real peak (a rider standing on the pedal); the mesh hadn't converged at the stress concentration; repeated loading caused fatigue, which a static analysis doesn't check; the material wasn't as strong as assumed. It shows why simulation is validated by testing.

   </details>

## Before moving on
<!-- bite: 93258640-459f-4ad8-8407-d9380d1d6a5d -->

You can describe parametric modelling and design intent, list CAD's outputs, choose a simulation, run through the FEA steps and judge whether to trust a result. **Next:** [[engineering-design-and-prototyping/21-engineering-drawings-and-dfma|21 — Engineering Drawings and DFMA]]: telling a factory exactly what to make, and making it easy to make.

## Related
<!-- bite: f96834de-9c51-414f-8f6c-8f079debf715 -->

- [[engineering-design-and-prototyping/index|Engineering design and prototyping map]]
- [[systems-simulation/index|Systems Simulation]]: simulating whole systems over time, rather than one part.
- [[continuum-mechanics/index|Continuum Mechanics]]: the stress theory FEA rests on.

## About this lesson
<!-- bite: 52c50613-caaf-4ba2-a596-66fa2ca5422c -->

**Level:** Intermediate. **Covers:** parametric, feature-based CAD, design intent, assemblies and outputs, the kinds of simulation, the steps of FEA, and how to trust a simulation.

**Where it sits:** lesson 20 of 36, in part 6 (detailed design).

**Source:** written from general engineering knowledge, because the SSG 532 lecture notes only name CAD and simulation as prototyping tools; they are on the official course outline. The worked numbers are checked by `scripts/diagrams/engineering_design.py`.
