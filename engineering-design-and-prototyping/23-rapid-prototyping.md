---
id: f41220c6-b3b2-4665-bf1d-09aea70a2ef0
---

# Rapid Prototyping

Rapid prototyping is making a physical model of a part straight from its CAD file, in hours or days instead of weeks.

## Before you start
<!-- bite: 52cf60c7-e106-46b3-901b-191068a9a5d5 -->

You should know low- and high-fidelity prototypes ([[engineering-design-and-prototyping/18-prototyping-and-testing-protocols|lesson 18]]) and the difference between thermoplastics and thermosets ([[engineering-design-and-prototyping/17-materials-polymers-and-frames|lesson 17]]).

After this lesson you will be able to:

1. explain the difference between additive and subtractive manufacturing;
2. describe three 3D printing methods, CNC machining and laser cutting;
3. choose a rapid prototyping method for a given part and justify it.

## What rapid prototyping is
<!-- bite: 1a6adca1-1deb-451d-b784-764eb4561435 -->

The study desk went from cardboard to "3D printed or CNC cut". But what do those actually mean, and how do you choose?

Before rapid prototyping, making one test part meant a skilled machinist working from a drawing for days, or making a mould that cost a fortune. Now you draw the part in CAD, send the file to a machine, and the machine makes it. That's the "rapid": no tooling, no waiting, and you can change the design and print again the same day.

That speed is what makes the design loop from lesson 2 cheap to go round.

## Additive and subtractive manufacturing
<!-- bite: 4e4d2d04-4824-4088-b1ce-9e08cbac2aee -->

There are two families of rapid prototyping, and they work in opposite directions:

1. **Additive manufacturing** builds the part up, one thin layer at a time, adding material only where the part is. 3D printing is additive. Like building a wall brick by brick.
2. **Subtractive manufacturing** starts with a solid block or sheet and cuts away everything that isn't the part. CNC machining and laser cutting are subtractive. Like carving a statue out of a block of wood.

## Additive versus subtractive
<!-- bite: 782d4666-0c02-453b-9a85-3b01dc35cf34 -->

| | Additive (3D printing) | Subtractive (CNC, laser cutting) |
| --- | --- | --- |
| How | Adds material layer by layer | Cuts material away from a block or sheet |
| Waste | Very little | The cut-away material (chips, offcuts) |
| Shapes | Almost any shape, even hollow insides and internal channels | Limited to what the cutting tool can reach |
| Materials | Mostly plastics and resins (metal printers exist but are expensive) | Almost any: metal, wood, plastic |
| Strength | Often weaker between layers | Full strength of the solid material |
| Surface | Visible layer lines | Smooth, accurate finish |

## Three 3D printing methods
<!-- bite: 19f519a2-ae54-473f-8d71-8c5720956566 -->

1. **Fused deposition modelling**: a nozzle melts thermoplastic filament (like PLA plastic) and draws each layer, like a hot glue gun controlled by a computer. The cheapest and most common kind; this is what most school and hobby printers are. Good for size and shape checks, but you can see the layer lines and the part is weaker between layers.
2. **Stereolithography**: a light (a laser or a screen) hardens a liquid resin one layer at a time. The resin sets once and can't be remelted, so it behaves like a thermoset. Very fine detail and a smooth surface, so it's used for small, detailed parts like jewellery models and dental moulds. The resin is messy and can be brittle.
3. **Selective laser sintering**: a laser fuses fine nylon powder, layer by layer. The loose powder holds the part up while it prints, so no support structures are needed and complex shapes come out well. Strong parts, close to real use, but the machines are expensive.

You'll often see these written as initials: `FDM`, `SLA` and `SLS`.

## CNC machining and laser cutting
<!-- bite: 764388d3-7f92-4977-88eb-732e16161ddd -->

1. **CNC machining**: CNC stands for computer numerical control. A computer moves a spinning cutter (a mill) or turns the part against a fixed tool (a lathe), cutting away metal, wood or plastic exactly as the CAD file says. The part has the full strength of the real material, with an accurate, smooth finish. Good for high-fidelity prototypes and for testing real loads.
2. **Laser cutting**: a laser cuts flat shapes out of a sheet of plywood, acrylic, card or thin metal. Very fast and cheap, but only for flat parts, which can then be slotted or glued together into 3D shapes.

## Choosing a method
<!-- bite: 69b01728-1535-4f80-b1f6-7b135d56940c -->

Match the method to what the prototype must test:

| The prototype must check… | Good method |
| --- | --- |
| Size, shape, how it fits the hand | Cardboard or foam, then fused deposition modelling |
| Fine detail and a smooth finish | Stereolithography |
| A complex shape that must also be strong | Selective laser sintering |
| Real strength in the real material (metal, hardwood) | CNC machining |
| A product made of flat panels | Laser cutting |

For the study desk stand: it's made of flat bamboo panels, so laser cutting plywood is quick and cheap for the shape. To test stability and load with 4 textbooks, CNC cut the real 12 mm bamboo, because a 3D printed version wouldn't have bamboo's strength.

## Prototypes versus production
<!-- bite: d016959e-f114-4869-9cab-95e53ef22fb4 -->

A rapid prototype is usually not how the real product will be made. One 3D printed bottle cap is cheap; a million of them would take forever. For a million, you'd use injection moulding. Rapid prototyping is for making *a few* parts fast; production processes are for making *many* parts cheaply. That trade-off is the next lesson.

## Common pitfalls
<!-- bite: d54b3e19-8d79-4596-9e62-7089ca6a92dc -->

1. **Mixing up additive and subtractive.** Additive builds up (3D printing). Subtractive cuts away (CNC, laser cutting).
2. **Trusting a printed part's strength.** Fused deposition parts are weaker between layers, so a load test on one can fail where the real part wouldn't. Test strength in the real material.
3. **Thinking 3D printing is how the product will be made.** It's for prototypes and small numbers; mass production uses other processes.

## Check your understanding
<!-- bite: bca2ab93-1a09-4c38-afe3-efcb6eefe333 -->

Try each one before you open the answer.

1. <!-- q: mcq id="c3a07e52" -->
   A machine cuts a gear out of a solid block of aluminium. Is this additive or subtractive manufacturing?

   - [ ] Additive
   - [x] Subtractive

   <details><summary>Answer</summary>

   Subtractive: it starts with a solid block and cuts away everything that isn't the gear. This is CNC machining.

   </details>

2. <!-- q: mcq id="5e9d1b74" -->
   Which 3D printing method melts plastic filament through a nozzle, layer by layer?

   - [x] Fused deposition modelling
   - [ ] Stereolithography
   - [ ] Selective laser sintering

   <details><summary>Answer</summary>

   Fused deposition modelling, the cheapest and most common kind of printer.

   </details>

3. <!-- q: mcq id="0b6f2c98" -->
   A dentist needs a very detailed, smooth model of a patient's teeth. Which method fits best?

   - [ ] Fused deposition modelling
   - [x] Stereolithography
   - [ ] Laser cutting

   <details><summary>Answer</summary>

   Stereolithography: light hardens liquid resin, giving very fine detail and a smooth surface.

   </details>

4. <!-- q: mcq id="a71e4d36" -->
   A team designing a steel bracket needs to load-test the prototype to see if it bends. Which method should they use?

   - [ ] Fused deposition modelling in plastic
   - [x] CNC machining from steel
   - [ ] Laser cutting cardboard

   <details><summary>Answer</summary>

   CNC machining from steel. A load test only means something in the real material; a plastic print would bend far sooner than steel.

   </details>

5. <!-- q: mcq id="8d4c0f17" -->
   Which of these are advantages of additive manufacturing? Choose all that apply.

   - [x] Very little waste material
   - [x] Can make hollow insides and internal channels
   - [ ] Parts are always stronger than machined ones
   - [x] No tooling needed

   <details><summary>Answer</summary>

   Little waste, complex internal shapes and no tooling. Printed parts are usually weaker, not stronger, especially between layers.

   </details>

6. <!-- q: open id="f2b85e09" -->
   You're designing a new bookshelf made of flat wooden panels that slot together. Which rapid prototyping method would you use first, and why?

   <details><summary>Answer</summary>

   Laser cutting, for example from thin plywood or card. The bookshelf is made of flat panels, and laser cutting makes flat shapes quickly and cheaply, so you can check that the slots fit and the proportions look right. Later, CNC cutting the real wood would test strength.

   </details>

## Before moving on
<!-- bite: cae531cb-469d-43ee-bd33-fb3e4c7e7ce2 -->

You can explain additive versus subtractive manufacturing, describe three 3D printing methods plus CNC machining and laser cutting, and pick the right method for a prototype. **Next:** [[engineering-design-and-prototyping/24-manufacturing-processes|Manufacturing Processes]]: how products are made when you need thousands, not one.

## Related
<!-- bite: 384c57f2-612d-4992-a347-b0dbb0b5b3d3 -->

- [[engineering-design-and-prototyping/index|Engineering design and prototyping map]]

## About this lesson
<!-- bite: 30e7deee-65e8-4473-a730-f6af6e3bd290 -->

**Level:** Intermediate. **Covers:** additive and subtractive manufacturing, fused deposition modelling, stereolithography, selective laser sintering, CNC machining, laser cutting, and choosing a method.

**Where it sits:** lesson 23, an extension of prototyping (lesson 18).

**Source:** written from general engineering knowledge; it is not in the SSG 532 lecture notes.
