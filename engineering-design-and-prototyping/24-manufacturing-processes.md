---
id: 012f7f1b-4816-41aa-bd57-55d52d5f1739
---

# Manufacturing Processes

A manufacturing process is the method a factory uses to turn raw material into a finished part.

## Before you start
<!-- bite: a6190d0c-ec39-4cab-8833-c90f3ffb2108 -->

You should know rapid prototyping ([[engineering-design-and-prototyping/23-rapid-prototyping|lesson 23]]), the DFMA principles ([[engineering-design-and-prototyping/16-engineering-drawings-and-dfma|lesson 16]]) and the bicycle frame example ([[engineering-design-and-prototyping/17-materials-polymers-and-frames|lesson 17]]).

After this lesson you will be able to:

1. explain tooling cost and cost per part, and why production volume decides the process;
2. describe five common processes with products made by each;
3. calculate the break-even quantity between two processes.

## What a manufacturing process is
<!-- bite: 26c51769-d018-44f4-8558-acefce4736b6 -->

Choosing one comes down to the shape, the material, how many you need and the cost. Rapid prototyping makes *a few* parts fast. But the bottle cap on your drink was one of millions, each costing a tiny amount. That needs a different kind of process.

The choice of process is a design decision, not something the factory sorts out later. Remember manufacturing technology from lesson 13: it must be considered at the initial level. A part shaped for 3D printing may be impossible to mould, and a part shaped for moulding may be impossible to forge.

## Tooling cost and cost per part
<!-- bite: 8582e0f7-9709-40ec-8da8-d0866379aa19 -->

Every process has two kinds of cost:

1. **Tooling cost**: the one-time cost of setting up, such as making a mould or a die. You pay it once, whether you make 1 part or 1 million.
2. **Cost per part**: the material, energy and labour for each part.

A process with expensive tooling usually has a very low cost per part. A process with no tooling usually has a high cost per part.

So the total cost is:

total cost = tooling cost + (cost per part × number of parts)

That's why production volume decides the process. Spread a ₦3,000,000 mould over 10 parts, and each one carries ₦300,000 of it. Spread it over a million, and each carries just ₦3.

## Injection moulding and casting
<!-- bite: 68525137-41d4-4610-9630-38cbe9ed8f38 -->

1. **Injection moulding**: melted thermoplastic is forced into a steel mould, cools, and pops out. The mould is very expensive, but each part takes seconds and costs very little. Good for high volume plastic parts. Examples: bottle caps, phone cases, plastic chairs, toy bricks.
2. **Casting**: liquid metal is poured into a mould shaped like the part and left to set. Sand casting uses a cheap sand mould, good for big parts in low numbers; die casting uses a steel mould, good for many small, accurate parts. Examples: engine blocks, manhole covers, tap bodies.

## Forging, extrusion and sheet metal forming
<!-- bite: 7430a23d-44b2-4f1e-8a10-4204aee2f278 -->

3. **Forging**: hot metal is hammered or pressed into shape. It squeezes the metal's grain to follow the shape of the part, so forged parts are very strong and tough. Examples: spanners, crankshafts, hammer heads.
4. **Extrusion**: material is pushed through a shaped hole (a die), like toothpaste from a tube, making a long piece with the same cross-section all the way along. Examples: aluminium window frames, pipes, and the bicycle frame tubes from lesson 17.
5. **Sheet metal forming**: flat metal sheet is cut, bent or pressed (stamped) into shape. Examples: car body panels, drink cans, cabinets.

## Comparing the processes
<!-- bite: e8c45f6a-284a-4704-87d8-d5aca92089ca -->

| Process | Material | Tooling cost | Cost per part | Best volume |
| --- | --- | --- | --- | --- |
| 3D printing (from lesson 23) | Plastics, resins | None | High | 1 to about 100 |
| CNC machining | Almost any | Low | High | 1 to about 1,000 |
| Sand casting | Metals | Low | Medium | Low to medium |
| Die casting | Metals (aluminium, zinc) | High | Low | High |
| Injection moulding | Thermoplastics | Very high | Very low | High (thousands to millions) |
| Forging | Metals | High | Low | Medium to high |
| Extrusion | Metals, plastics | Medium | Low | Medium to high |
| Sheet metal forming | Metal sheet | Medium to high | Low | Medium to high |

These volumes are rough guides, and they shift with the part's size and complexity.

## The break-even quantity
<!-- bite: bf6bacb5-8a36-437b-941c-fc3788922fe9 -->

So when does it become worth paying for a mould? At the **break-even quantity**: the number of parts at which two processes cost the same in total.

Take a plastic part for the study desk stand's stationery holder:

- **3D printing**: no tooling, ₦2,000 per part.
- **Injection moulding**: ₦3,000,000 mould, ₦100 per part.

Set the totals equal and solve for the number of parts, n:

2,000n = 3,000,000 + 100n

1,900n = 3,000,000

n = 3,000,000 ÷ 1,900 ≈ 1,579 parts

## Reading the break-even answer
<!-- bite: 99d5e894-bf96-4fc5-bb6d-18b7a7f1a90d -->

Below about 1,579 parts, 3D printing is cheaper, because you never pay for the mould. Above it, injection moulding is cheaper, because the low cost per part soon covers the mould.

In words: the break-even quantity is the difference in tooling cost divided by the difference in cost per part.

$$n = \frac{\text{tooling}_B - \text{tooling}_A}{\text{per part}_A - \text{per part}_B}$$

So if the stand is a term-paper prototype or a small run for one hostel, print it. If it's going to every student in the country, mould it.

## Common pitfalls
<!-- bite: d5beae31-8588-47b3-be32-3c26e4d33ab0 -->

1. **Comparing only the cost per part.** Injection moulding looks cheapest per part, but not if you only need 50.
2. **Choosing the process after the design is finished.** Each process limits the shapes you can make, so it must be chosen early (DFMA).
3. **Forgetting that forging gives strength.** When a part takes heavy, repeated loads (a spanner, a crankshaft), forging's grain flow is the reason to pick it.

## Check your understanding
<!-- bite: 713bdda2-536d-4d7c-b65d-707ed1cbf7f0 -->

Try each one before you open the answer.

1. <!-- q: exact id="6a1d8e43" answer="1000" accept="1,000" -->
   Process A has no tooling cost and costs ₦1,250 per part. Process B needs ₦1,200,000 of tooling and costs ₦50 per part. At how many parts do they cost the same?

   <details><summary>Answer</summary>

   1,250n = 1,200,000 + 50n, so 1,200n = 1,200,000, and n = 1,000 parts.

   </details>

2. <!-- q: mcq id="d9f40b27" -->
   A company needs 2 million identical plastic bottle caps. Which process fits best?

   - [ ] 3D printing
   - [ ] CNC machining
   - [x] Injection moulding

   <details><summary>Answer</summary>

   Injection moulding. The mould is expensive, but over 2 million caps the tooling cost per cap is tiny, and each cap takes seconds.

   </details>

3. <!-- q: mcq id="1b5e7c80" -->
   Which process makes long pieces with the same cross-section all the way along, like aluminium window frames?

   - [ ] Forging
   - [x] Extrusion
   - [ ] Casting

   <details><summary>Answer</summary>

   Extrusion: material is pushed through a shaped die, like toothpaste from a tube.

   </details>

4. <!-- q: mcq id="7c2a9f15" -->
   Why are spanners usually forged rather than cast?

   - [ ] Forging has no tooling cost
   - [x] Forging makes the metal's grain follow the part's shape, so it is stronger and tougher
   - [ ] Casting can't be used for steel

   <details><summary>Answer</summary>

   Forging squeezes the grain to follow the shape, giving a strong, tough part that survives heavy, repeated loads.

   </details>

5. <!-- q: exact id="e4b6c031" answer="2900000" accept="2,900,000|₦2,900,000" -->
   A mould costs ₦2,500,000 and each moulded part costs ₦80. What is the total cost of making 5,000 parts, in naira?

   <details><summary>Answer</summary>

   2,500,000 + 80 × 5,000 = 2,500,000 + 400,000 = ₦2,900,000.

   </details>

6. <!-- q: open id="3f8d2a6b" -->
   Explain why production volume decides which manufacturing process to use.

   <details><summary>Answer</summary>

   Processes differ in tooling cost (paid once) and cost per part (paid every time). Total cost is tooling plus cost per part times the number of parts. At low volume, a process with no tooling is cheaper even though each part costs more. At high volume, an expensive mould is spread over so many parts that its low cost per part wins. The break-even quantity is where the two totals are equal.

   </details>

## Before moving on
<!-- bite: 8cf9feae-2be0-449e-8b8b-19bc7d83bc63 -->

You can explain tooling cost and cost per part, describe five manufacturing processes with examples, and calculate a break-even quantity. **Next:** [[engineering-design-and-prototyping/25-factor-of-safety|Factor of Safety]]: making parts stronger than they need to be, on purpose.

## Related
<!-- bite: 2309164d-3e08-44dd-9f45-d491dc3a265a -->

- [[engineering-design-and-prototyping/index|Engineering design and prototyping map]]

## About this lesson
<!-- bite: c13a5862-2f97-48f6-9580-889d080aeecf -->

**Level:** Intermediate. **Covers:** tooling cost and cost per part, injection moulding, casting, forging, extrusion, sheet metal forming, a comparison table, and the break-even quantity.

**Where it sits:** lesson 24, an extension of detailed design (lessons 16 and 17). It helps with exam question 6(c).

**Source:** written from general engineering knowledge; it is not in the SSG 532 lecture notes. The volumes in the table are rough guides. The break-even numbers are checked by `scripts/diagrams/engineering_design.py`.
