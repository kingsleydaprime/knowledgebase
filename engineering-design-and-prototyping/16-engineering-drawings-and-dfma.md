---
id: daaae8c7-5649-4d62-a425-2e39b00c8403
---

# Engineering Drawings and DFMA

Detailed design pins down every dimension, material and part, and drawings and DFMA are its main tools.

## Before you start
<!-- bite: 30dacbf1-a932-4d37-a530-1547d9e0c9fd -->

You should know concept refinement ([[engineering-design-and-prototyping/12-concept-refinement|lesson 12]]) and the manufacturing technology requirement ([[engineering-design-and-prototyping/13-considerations-of-good-design-1|lesson 13]]).

After this lesson you will be able to:

1. explain why detailed engineering drawings still matter in the age of 3D CAD and rapid prototyping;
2. list the information a drawing conveys that a 3D model file alone may not;
3. explain the four key principles of DFMA and how each one changes a product.

## What detailed design is
<!-- bite: 26e98240-e3e1-4a71-98c3-85a20946c6ea -->

After refinement, we know what the design does and which parts it has. Detailed design pins everything down: every dimension, every material, every screw. It's the last step before anything gets made.

Two questions come up here:

1. **How do we tell the factory exactly what to make?** With engineering drawings.
2. **How do we make sure the factory can make it cheaply and reliably?** With design for manufacturing and assembly (DFMA).

## Why drawings still matter in the age of 3D CAD
<!-- bite: ba2d35a5-b7fe-4ceb-b8e1-b983229a9a52 -->

Today you can model a part on the computer and 3D print it the same day. So why still draw?

Because a 3D model shows the *shape*, but a manufacturer needs to know exactly what to make, how accurately, and how to check it.

- Drawings are standardised documents that everyone reads the same way.
- A drawing is often a legal and contractual record between designer and manufacturer. If the part is wrong, the drawing says whose fault it is.
- Rapid prototyping can work from a model, but production usually needs a drawing.

## What a drawing conveys that a 3D file may not
<!-- bite: 8cad869e-1c1b-4646-97dd-d67d10fa0baa -->

Information a drawing conveys that a 3D file alone may not state explicitly:

1. Dimensions with **tolerances** and geometric tolerances, which say how much variation is allowed.
2. **Material** and its grade or specification, and heat treatment.
3. **Surface finish** and coatings.
4. **Fits** between mating parts (how tight a shaft sits in a hole).
5. Which dimensions are **critical to inspect**, and inspection or quality requirements.
6. **Assembly notes**, the bill of materials and the standards used.
7. **Revision and approval** information, scale and units.

Take a shaft that goes into a bearing. The 3D model says it's 20 mm across. The drawing says 20 mm, *plus or minus 0.01 mm*, ground smooth, hardened steel, check this diameter on every part. Without that, the factory might make it 20.2 mm, and it won't fit.

## DFMA: design for manufacturing and assembly
<!-- bite: 53a6dcfa-6afa-4085-9c74-b8201cc87d9a -->

DFMA is designing a product so it is easy and cheap to make and to put together. Remember from lesson 13: manufacturing must be considered at the initial level, not after the design is finished.

Sources word the principles differently, so check which four your lecturer used. A common set:

1. Minimise the number of parts.
2. Standardise parts and materials.
3. Design for ease of fabrication.
4. Design for ease of assembly.

## DFMA principles 1 and 2
<!-- bite: da936a4e-3a4d-40ff-95a4-86ddb361e3fc -->

**1. Minimise the number of parts.** Fewer parts means fewer things to make, store, assemble and fail.

*Influence on the design:* combine parts into one moulded part, or use snap fits instead of screws. A plastic pen body with a moulded-in clip replaces a body, a metal clip and a rivet.

**2. Standardise parts and materials.** Use off-the-shelf components, fasteners and standard sizes.

*Influence on the design:* lower cost and easier supply and repair. If every screw in a product is the same M4 size, the factory buys one kind, the worker uses one screwdriver, and a repairer finds spares anywhere.

## DFMA principles 3 and 4
<!-- bite: 31d6e628-c859-4630-a461-41dfbcea60e6 -->

**3. Design for ease of fabrication.** Use simple shapes, processes and generous tolerances the factory can achieve.

*Influence on the design:* avoids deep holes, undercuts and tight tolerances that raise cost. Only the dimensions that really matter get tight tolerances (like the shaft in the bearing); the rest stay loose and cheap.

**4. Design for ease of assembly.** Parts should be easy to handle, self-locating and assembled from one direction, and impossible to assemble wrongly.

*Influence on the design:* faster, cheaper and more reliable assembly. A phone charger plug that only fits one way round can't be assembled upside down.

Drawings say what to make, DFMA makes sure it can be made. The other big detailed-design choice is the material itself, and that's the next lesson.

## Common pitfalls
<!-- bite: 23a2a4a3-7886-4ac5-a310-0a91a2dd525c -->

1. **"A 3D model has everything."** It shows the shape, but often not tolerances, fits, finish, inspection points or approval.
2. **Tight tolerances everywhere.** They raise cost. Use them only where the function needs them.
3. **Treating DFMA as a last step.** It must shape the design from the start; changing a part's shape after tooling is made is expensive.

## Check your understanding
<!-- bite: c6db4fdb-9b18-46c6-939a-00945e6b7b29 -->

Try each one before you open the answer.

1. <!-- q: mcq id="5a8e0c3d" -->
   Which of these does an engineering drawing convey that a 3D model file alone may not state explicitly? Choose all that apply.

   - [x] Tolerances on dimensions
   - [x] Surface finish
   - [x] Which dimensions are critical to inspect
   - [ ] The overall shape of the part

   <details><summary>Answer</summary>

   Tolerances, surface finish and inspection points. The 3D model already shows the overall shape.

   </details>

2. <!-- q: mcq id="c2f6d917" -->
   A toy maker replaces six screws holding two halves of a toy together with snap fits moulded into the plastic. Which DFMA principle is this?

   - [x] Minimise the number of parts
   - [ ] Standardise parts and materials
   - [ ] Design for ease of fabrication

   <details><summary>Answer</summary>

   Minimise the number of parts: the six screws disappear. It also helps ease of assembly, since snapping is faster than screwing.

   </details>

3. <!-- q: mcq id="9e1b47a6" -->
   A furniture company redesigns all its products to use one size of bolt. Which DFMA principle is this?

   - [ ] Minimise the number of parts
   - [x] Standardise parts and materials
   - [ ] Design for ease of assembly

   <details><summary>Answer</summary>

   Standardise parts and materials: lower cost, easier supply and repair.

   </details>

4. <!-- q: mcq id="47d3a0e8" -->
   A battery holder is shaped so a battery can only go in the right way round. Which DFMA principle is this?

   - [ ] Design for ease of fabrication
   - [x] Design for ease of assembly
   - [ ] Standardise parts and materials

   <details><summary>Answer</summary>

   Design for ease of assembly: parts should be impossible to assemble wrongly.

   </details>

5. <!-- q: open id="b06c8f25" -->
   Give two reasons why engineering drawings are still vital in the age of 3D CAD and rapid prototyping.

   <details><summary>Answer</summary>

   Any two: a manufacturer needs to know exactly what to make, how accurately and how to check it, which the model's shape alone doesn't say; drawings are standardised documents everyone reads the same way; they are often a legal and contractual record between designer and manufacturer; production usually needs a drawing even when prototyping works from a model.

   </details>

## Before moving on
<!-- bite: f63b36e4-8d75-47c0-8cce-cc6d3ce6de3c -->

You can explain why drawings still matter, list what they convey beyond a 3D model, and explain the four DFMA principles with their effect on a design. **Next:** [[engineering-design-and-prototyping/17-materials-polymers-and-frames|Materials: Polymers and Frames]]: choosing what the product is made of.

## Related
<!-- bite: b4bf42d9-6324-4cf0-b55a-eb056a2f24ab -->

- [[engineering-design-and-prototyping/index|Engineering design and prototyping map]]
- [[computer-graphics/index|Computer Graphics]]: CAD is one of its applications.

## About this lesson
<!-- bite: 5f66306a-f760-4a56-9377-03d9307b7ac7 -->

**Level:** Intermediate. **Covers:** detailed design, why engineering drawings still matter, what a drawing conveys beyond a 3D model, and the four key principles of DFMA.

**Where it sits:** lesson 16 of 21, phase 5 of the design process. Exam questions 5(c) and 6(b) come from here.

**Source:** written for the SSG 532 exam from general engineering knowledge. It is not in the lecture notes, so check it (especially which four DFMA principles your lecturer used) against any slides the lecturer gave.
